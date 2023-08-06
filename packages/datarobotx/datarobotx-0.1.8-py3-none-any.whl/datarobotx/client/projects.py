#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from collections.abc import Callable
import io
import json
import logging
from typing import Any, cast, Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode

import aiohttp
import pandas as pd

from datarobotx.client.status import await_status, poll
from datarobotx.common.client import raise_value_error, read_resp_data, session
from datarobotx.common.logging import refresh_bar, tqdm
from datarobotx.common.utils import create_task, FilesSender

logger = logging.getLogger("drx")


async def post_projects(
    payload: Optional[Tuple[str, pd.DataFrame]] = None, json: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a DR project from a pandas DataFrame asynchronously with progress
    tracking.
    Returns the url where project creation status can be polled.
    """
    kwargs = {}
    if payload is not None:
        logger.info("Uploading project dataset...")
        file_name, _ = payload
        sender = FilesSender(payload)
        form_data = aiohttp.FormData()
        form_data.add_field("file", sender.reader(file_name), filename=file_name)
        for key, value in json.items():  # type: ignore[union-attr]
            form_data.add_field(key, value)
        kwargs["data"] = form_data
    else:
        kwargs["json"] = json  # type: ignore[assignment]

    url = "/projects/"
    async with session.post(url, timeout=None, **kwargs) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        return resp.headers["Location"]


async def await_proj(status_url: str) -> str:
    """Poll project creation status and update progress.
    Returns project id upon successful creation.
    """
    coro_args = [status_url]
    coro_kwargs: Dict[str, Any] = {}
    pid = await poll(await_status, coro_args=coro_args, coro_kwargs=coro_kwargs)
    return cast(str, pid)


async def get_recommended_model(pid: str) -> Optional[Dict[str, Any]]:
    """Returns the recommended model for a given project_id
    Returns None if no recommendation available
    Returns model details associated with the recommended model otherwise
    """
    url = f"/projects/{pid}/recommendedModels/recommendedModel/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status == 200:
            json = await resp.json()
            model_id = json["modelId"]
            model_json = await get_model(pid, model_id)
            return model_json
        else:
            return None


async def await_stage_is_modeling(pid: str) -> None:
    """Await project entering stage=modeling (model training)"""

    async def _is_modeling(pid: str) -> Optional[bool]:  # type: ignore[return]
        url = f"/projects/{pid}/status/"
        async with session.get(url, allow_redirects=False) as resp:
            json = await resp.json()
            if json["stage"] == "modeling":
                return True  # end polling

    coro_args = [pid]
    coro_kwargs: Dict[str, Any] = {}
    await poll(_is_modeling, coro_args=coro_args, coro_kwargs=coro_kwargs)


async def get_projects_status(pid: str) -> bool:
    """Retrieve project status."""
    url = f"/projects/{pid}/status/"
    async with session.get(url, allow_redirects=False) as resp:
        json = await resp.json()
        return cast(bool, json["autopilotDone"])


async def await_autopilot(
    pid: str,
    featurelist_id: Optional[str] = None,
    champion_handler: Optional[Callable] = None,  # type: ignore[type-arg]
) -> Optional[bool]:
    """Await and progress track autopilot completion.
    Calls champion_handler() to process champion models in customizable ways
    If featurelist_id is specified the complete_models count will be filtered by this id
    """
    complete = 0
    pbar = tqdm(
        postfix={"Fitting": 0, "Queued": 0},
        bar_format="|{bar}|{n_fmt} completed [{elapsed}{postfix}]",
    )
    create_task(refresh_bar(pbar))

    async def _await_autopilot(pid: str) -> Optional[bool]:  # type: ignore[return]
        nonlocal complete
        url = f"/projects/{pid}/status/"
        async with session.get(url, allow_redirects=False) as resp:
            json = await resp.json()
            autopilot_done = json["autopilotDone"]

        url = f"/projects/{pid}/modelJobs/"
        async with session.get(url, allow_redirects=False) as resp:
            json = await resp.json()
            in_progress = [job for job in json if job["status"] == "inprogress"]
            in_progress_length = len(in_progress)
            queue_jobs = [job for job in json if job["status"] == "queue"]
            queue_length = len(queue_jobs)

        url = f"/projects/{pid}/models/"
        async with session.get(url, allow_redirects=False) as resp:
            json = await resp.json()
            if featurelist_id is not None:
                json = [model for model in json if model["featurelistId"] == featurelist_id]
            now_complete = len(json)

        pbar.update(max(now_complete - complete, 0))
        pbar.total = in_progress_length + queue_length + now_complete
        pbar.set_postfix({"Fitting": in_progress_length, "Queued": queue_length})
        pbar.refresh()
        if autopilot_done and queue_length == 0 and in_progress_length == 0:
            pbar.close()
            if champion_handler is not None:  # wait for champion handler before returning
                await champion_handler()
            return True  # non-None return value ends polling
        elif (
            champion_handler is not None and now_complete > complete
        ):  # schedule champion handler concurrently
            complete = now_complete
            create_task(champion_handler())

    coro_args = [pid]
    coro_kwargs: Dict[str, Any] = {}
    return cast(bool, await poll(_await_autopilot, coro_args=coro_args, coro_kwargs=coro_kwargs))


async def patch_aim(pid: str, json: Dict[str, Any]) -> None:
    """Patch the project /aim/ endpoint, commencing autopilot"""
    aim_url = f"/projects/{pid}/aim/"
    async with session.patch(aim_url, json=json, allow_redirects=False) as resp:
        if resp.status != 202:
            await raise_value_error(resp)


async def patch_projects(pid: str, json: Dict[str, Any]) -> None:
    """Patch the /projects/ endpoint"""
    proj_url = f"/projects/{pid}/"
    async with session.patch(proj_url, json=json, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)


async def get_project(pid: str) -> Dict[str, Any]:
    """Retrieve project details for a given project id."""
    url = f"/projects/{pid}/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def post_models(pid: str, bp_id: str) -> str:
    """Train a new model from a blueprint"""
    url = f"/projects/{pid}/models/"
    json = {"blueprintId": bp_id}
    async with session.post(url, json=json, timeout=None) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        return resp.headers["Location"]


async def await_model(status_url: str) -> str:
    """Wait for model to finish training"""
    coro_args = [status_url]

    model_id = await poll(await_status, coro_args=coro_args)
    return cast(str, model_id)


async def get_model(pid: str, model_id: str) -> Dict[str, Any]:
    """Retrieve model details for a given project id and model id."""
    url = f"/projects/{pid}/models/{model_id}/"
    async with session.get(url, allow_redirects=False) as resp:
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_models(pid: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Retrieve list of models and associate properties for a given project id."""
    if params:
        params_encoded = urlencode(params)
        url = f"/projects/{pid}/models/?{params_encoded}"
    else:
        url = f"/projects/{pid}/models/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_prediction_dataset(pid: str, ds_id: str) -> Dict[str, Any]:
    """Prediction dataset attributes"""
    url = f"/projects/{pid}/predictionDatasets/{ds_id}/"
    async with session.get(url, allow_redirects=False) as resp:
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def post_prediction_datasets_file_uploads(
    pid: str, payload: Tuple[str, pd.DataFrame], relax_kia_check: bool = False
) -> Dict[str, Any]:
    """Upload a new prediction dataset to DR."""
    logger.info("Uploading prediction dataset...")
    file_name, _ = payload
    sender = FilesSender(payload)

    url = f"/projects/{pid}/predictionDatasets/fileUploads/"
    form_data = aiohttp.FormData()
    form_data.add_field("file", sender.reader(file_name), filename=file_name)

    # For time series projects
    if relax_kia_check:
        form_data.add_field("relaxKnownInAdvanceFeaturesCheck", "true")

    async with session.post(url, data=form_data, timeout=None) as resp:
        status_url = resp.headers["Location"]
    logger.info("Awaiting prediction dataset initialization...")

    ds_id = await poll(await_status, coro_args=[status_url])
    ds_json = await get_prediction_dataset(pid=pid, ds_id=ds_id)
    return ds_json


async def post_prediction_datasets_dataset_uploads(
    pid: str, dataset_id: str, relax_kia_check: bool = False
) -> Dict[str, Any]:
    """Upload a new prediction dataset to DR."""
    url = f"/projects/{pid}/predictionDatasets/datasetUploads/"
    json = {"datasetId": dataset_id}

    if relax_kia_check:
        json["relaxKnownInAdvanceFeaturesCheck"] = "true"

    async with session.post(url, json=json, timeout=None) as resp:
        status_url = resp.headers["Location"]
    logger.info("Awaiting prediction dataset initialization...")

    ds_id = await poll(await_status, coro_args=[status_url])
    ds_json = await get_prediction_dataset(pid=pid, ds_id=ds_id)
    return ds_json


async def post_predictions(pid: str, json: Dict[str, Any]) -> str:
    """
    Request and await DataRobot predictions
    """
    start_predictions_url = "/projects/" + pid + "/predictions/"

    async with session.post(start_predictions_url, json=json) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        pred_status_url = resp.headers["Location"]
    logger.info("Scoring...")

    preds_id = await poll(await_status, coro_args=[pred_status_url])
    return cast(str, preds_id)


async def post_external_scores(pid: str, model_id: str, prediction_dataset_id: str) -> str:
    """Request Computation of External Scores"""
    url = f"/projects/{pid}/externalScores/"
    body = {"modelId": model_id, "datasetId": prediction_dataset_id}
    async with session.post(url, json=body) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        test_status_url = resp.headers["Location"]
    logger.info("Calculating External Test Insights...")
    external_score_id = await poll(await_status, coro_args=[test_status_url])
    return cast(str, external_score_id)


async def get_external_scores(
    pid: str, model_id: str, prediction_dataset_id: str
) -> Dict[str, Any]:
    """Request Computation of External Scores"""
    url = f"/projects/{pid}/externalScores/"
    body = {"modelId": model_id, "datasetId": prediction_dataset_id}
    async with session.get(url, json=body) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        score_results = await resp.json()
    return cast(Dict[str, Any], score_results["data"])


async def get_roc_data(pid: str, model_id: str, prediction_dataset_id: str) -> Dict[str, Any]:
    """Get Values external ROC Score"""
    query_params = {"datasetId": prediction_dataset_id, "limit": 1000}
    query_params_encoded = urlencode(query_params)
    url = f"/projects/{pid}/models/{model_id}/datasetRocCurves/?{query_params_encoded}"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        roc_curve_data = await resp.json()
    return cast(Dict[str, Any], roc_curve_data)


async def get_liftchart_data(pid: str, model_id: str, prediction_dataset_id: str) -> Dict[str, Any]:
    """Request Values External Lift Chart"""
    query_params = {"datasetId": prediction_dataset_id, "limit": 1000}
    query_params_encoded = urlencode(query_params)
    url = f"/projects/{pid}/models/{model_id}/datasetLiftCharts/?{query_params_encoded}"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        lift_chart_data = await resp.json()
    return cast(Dict[str, Any], lift_chart_data)


async def get_residuals_data(pid: str, model_id: str, prediction_dataset_id: str) -> Dict[str, Any]:
    """Request Values External Residuals Chart"""
    query_params = {"datasetId": prediction_dataset_id, "limit": 1000}
    query_params_encoded = urlencode(query_params)
    url = f"/projects/{pid}/models/{model_id}/datasetResidualsCharts/?{query_params_encoded}"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        residuals_chart_data = await resp.json()
    return cast(Dict[str, Any], residuals_chart_data)


async def get_predictions(pid: str, predictions_id: str) -> pd.DataFrame:
    """Retrieve prediction results as a stream while updating progress."""
    url = f"/projects/{pid}/predictions/{predictions_id}/"
    headers = {"Accept": "text/csv"}
    logger.info("Downloading predictions...")

    async with session.get(url, headers=headers, timeout=None) as resp:
        f = io.BytesIO()
        pbar = tqdm(
            bar_format="{n_fmt}{unit} [{elapsed}, {rate_fmt}]",
            unit="B",
            unit_scale=True,
            unit_divisor=1000,
        )
        await read_resp_data(resp, f, pbar)
        pbar.close()
        f.seek(0)
        return pd.read_csv(f)


async def get_feature_impact(
    pid: str, model_id: str, log_calc_with: Optional[Callable] = None  # type: ignore[type-arg]
) -> Dict[str, Any]:
    """Retrieve the feature impact scores for a model.
    Parameters
    ----------
    pid : str
        DR project id
    model_id : str
        DR model id
    log_calc_with : Callable
        Function to call if feature impact results not immediately available
    """
    url = f"/projects/{pid}/models/{model_id}/featureImpact/"

    async def _post_feature_impact() -> Optional[str]:  # type: ignore[return]
        async with session.post(url) as resp:
            if resp.status in (422, 200):
                return None  # Feature impact already ran
            elif resp.status == 202:
                if log_calc_with is not None:
                    log_calc_with()
                status_url = resp.headers["Location"]
                return status_url
            else:
                await raise_value_error(resp)

    async def _get_feature_impact() -> Dict[str, Any]:
        async with session.get(url) as resp:
            json = await resp.json()
            return cast(Dict[str, Any], json)

    status_url = await _post_feature_impact()
    if status_url is not None:
        coro_args = [status_url]
        await poll(await_status, coro_args=coro_args)
    json = await _get_feature_impact()
    return json


async def get_features(pid: str) -> Dict[str, Any]:
    """Retrieve list of features for a given project id."""
    url = f"/projects/{pid}/features/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_feature_histogram(pid: str, feature: str) -> Dict[str, Any]:
    """Retrieve feature histogram for a feature from a project."""
    url = f"/projects/{pid}/featureHistograms/{quote(feature)}"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_featurelist(pid: str, featurelist_id: str) -> Dict[str, Any]:
    """Retrieve featurelist details for a given project_id, featurelist_id."""
    url = f"/projects/{pid}/featurelists/{featurelist_id}/"
    async with session.get(url) as resp:
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_model_featurelist(pid: str, model_id: str) -> Dict[str, Any]:
    """
    Retrieve featurelist and background data for a given, project_id, model_id
    Used in generating web applications from deployments.
    """

    feature_json = await get_features(pid)

    feature_dict = {}
    for i in feature_json:
        feature_dict[i["name"]] = {  # type: ignore[index]
            "feature_type": i["featureType"],  # type: ignore[index]
            "mean": i["mean"],  # type: ignore[index]
            "median": i["median"],  # type: ignore[index]
            "std": i["stdDev"],  # type: ignore[index]
            "unique_count": i["uniqueCount"],  # type: ignore[index]
            "na_count": i["naCount"],  # type: ignore[index]
            "parent_features": i["parentFeatureNames"],  # type: ignore[index]
            "has_parent_features": len(i["parentFeatureNames"]) > 0,  # type: ignore[index]
            "date_format": i["dateFormat"],  # type: ignore[index]
        }
    model = await get_model(pid, model_id)
    featurelist_id = model["featurelistId"]

    featurelist = await get_featurelist(pid, featurelist_id)

    # Only add features that aren't child features
    features_and_types: Dict[str, Any] = {}
    for i in featurelist["features"]:
        if feature_dict[i]["has_parent_features"]:
            parent_features: List[str] = cast(List[str], feature_dict[i]["parent_features"])
            for j in parent_features:
                features_and_types[j] = feature_dict[j]
        else:
            features_and_types[i] = feature_dict[i]

    return features_and_types


async def post_featurelist(pid: str, featurelist_json: Dict[str, Any]) -> str:
    """Create a new featurelist. Returns the created featurelist id."""
    url = f"/projects/{pid}/modelingFeaturelists/"
    async with session.post(url, json=featurelist_json) as resp:
        json = await resp.json()
        return cast(str, json["id"])


async def post_autopilots(pid: str, ap_json: Dict[str, Any]) -> None:
    """Start autopilot on a custom featurelist."""
    url = f"/projects/{pid}/autopilots/"
    await session.post(url, json=ap_json, allow_redirects=False)


async def initialize_prediction_explanations(
    pid: str, model_id: str, max_explanations: Optional[int] = 10
) -> bool:
    """Initialize a model for prediction explanations
    Initialization may fail (422) if insufficient data in validation partition
    or no features with impact
    Returns
    -------
    True if successfully initialized, otherwise False
    """
    url = f"/projects/{pid}/models/{model_id}/predictionExplanationsInitialization/"

    async with session.get(url) as resp:
        if resp.status != 200:
            async with session.post(url, json={"maxExplanations": max_explanations}) as resp:
                if resp.status == 422:
                    json = await resp.json()
                    dr_message = json["message"]
                    logger.warning(
                        "Could not initialize prediction explanations for model '%s' in project '%s'. Message: '%s'",
                        model_id,
                        pid,
                        dr_message,
                    )
                    return False
                elif resp.status == 202:
                    status_url = resp.headers["Location"]
                else:
                    await raise_value_error(resp)

            coro_args = [status_url]
            await poll(await_status, coro_args=coro_args)
        return True


async def post_multiseries_properties(pid: str, json: Dict[str, Any]) -> None:
    """Analyze multiseries relationships"""
    url = f"/projects/{pid}/multiseriesProperties/"
    async with session.post(url, json=json, allow_redirects=False) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        status_url = resp.headers["Location"]

    await poll(await_status, coro_args=[status_url])
    return


async def post_segmented_properties(
    pid: str, json: Dict[str, Any], user_defined_segment_id_columns: Optional[List[str]] = None
) -> str:
    """Analyze segmented modeling relationships"""

    url = f"/projects/{pid}/segmentationTasks/"
    segmentation_json = {
        "useTimeSeries": json["useTimeSeries"],
        "target": json["target"],
        "datetimePartitionColumn": json["datetimePartitionColumn"],
        "multiseriesIdColumns": json["multiseriesIdColumns"],
        "userDefinedSegmentIdColumns": user_defined_segment_id_columns,
    }
    async with session.post(url, json=segmentation_json, allow_redirects=False) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        status_url = resp.headers["Location"]

    segmentation_task_id = await poll(await_status, coro_args=[status_url])
    return cast(str, segmentation_task_id)


async def patch_access_control(pid: str, json: Dict[str, Any]) -> int:
    """Share project with other users"""
    url = f"/projects/{pid}/accessControl/"
    async with session.patch(url, json=json, allow_redirects=False) as resp:
        if resp.status != 204:
            await raise_value_error(resp)
    return resp.status


async def get_feature_discovery_recipe_sqls(pid: str) -> str:
    """Get SQL to generate features from feature discovery"""
    url = f"/projects/{pid}/featureDiscoveryRecipeSQLs/download/"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        return await resp.text()


async def post_feature_discovery_recipe_sql_exports(pid: str) -> str:
    """Generate sql export file for feature discovery"""
    url = f"/projects/{pid}/featureDiscoveryRecipeSqlExports/"
    async with session.post(url, allow_redirects=False) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        return resp.headers["Location"]


async def await_sql_recipes(pid: str) -> str:
    """Request and await sql recipes export."""
    status_url = await post_feature_discovery_recipe_sql_exports(pid)
    coro_args = [status_url]
    await poll(await_status, coro_args=coro_args)

    recipe_sqls = await get_feature_discovery_recipe_sqls(pid)
    return recipe_sqls


async def get_derived_features(pid: str) -> pd.DataFrame:
    """Get derived features post feature discovery"""
    url = f"/projects/{pid}/featureDiscoveryDatasetDownload/"
    async with session.get(url) as resp:
        if resp.status != 200:
            raise ValueError(
                f"Received error code {resp.status} from GET '{url}'."
                + "Note that download of the feature discovery dataset is not available until Autopilot has fully "
                "initialized and started."
            )
        response = await resp.text()
        return pd.read_csv(io.StringIO(response), sep=",")


async def get_datetime_partitioning(pid: str) -> Dict[str, Any]:
    """Get time unit and time step of each series"""
    url = f"/projects/{pid}/datetimePartitioning"
    async with session.get(url) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        return await resp.json()


async def get_blueprints(pid: str) -> Dict[str, Any]:
    """Get a list of blueprints from a modeling project"""
    url = f"/projects/{pid}/blueprints/"
    async with session.get(url) as resp:
        if resp.status != 200:
            raise ValueError(
                f"Received error code {resp.status} from GET '{url}'."
                + "Make sure the project has begun fitting models"
            )
        return cast(Dict[str, Any], await resp.json())


async def get_advanced_tuning_parameters(pid: str, mid: str) -> Dict[str, Any]:
    """Get advanced tuning settings from a model"""
    url = f"/projects/{pid}/models/{mid}/advancedTuning/parameters/"
    async with session.get(url) as resp:
        if resp.status != 200:
            raise ValueError(f"Received error code {resp.status} from GET '{url}'.")
        return cast(Dict[str, Any], await resp.json())


async def post_advanced_tuning_parameters(pid: str, mid: str, payload: Dict[str, Any]) -> str:
    """Post advanced tuning options"""
    url = f"/projects/{pid}/models/{mid}/advancedTuning/"
    async with session.post(url, json=payload) as resp:
        if resp.status == 202:
            return resp.headers["Location"]
        else:
            message = await resp.text()
            if (
                "This job duplicates a job or jobs that are in the queue or have completed"
                in message
            ):
                return cast(str, json.loads(message)["previousJob"]["url"])
            else:
                raise ValueError(f"Received error code {resp.status} from GET '{url}'.")
