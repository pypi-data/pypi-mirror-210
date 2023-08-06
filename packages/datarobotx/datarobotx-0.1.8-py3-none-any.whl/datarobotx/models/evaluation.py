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
import logging
import re
from typing import cast, Union

import pandas as pd

import datarobotx.client.projects as proj_client
from datarobotx.common import utils
from datarobotx.models.automl import AutoMLModel
from datarobotx.models.model import Model, ModelOperator
from datarobotx.viz.modelcard import ModelCardFormatter
from datarobotx.viz.viz import designated_widget_handler

logger = logging.getLogger("drx")


def evaluate(
    model: Union[Model, ModelOperator], evaluation_data: Union[pd.DataFrame, str] = None
) -> None:
    """
    Show evaluation metrics and plots for a model

    DataRobot automatically calculates several model evaluation metrics and plots
    to help assess model performance.

    This helper retrieves these metrics and plots and renders them in-notebook;
    if an external dataset is provided, it will automatically be uploaded and
    calculations requested.

    *For Binary Models with external evaluation data:*
    `evaluate` will score the dataset against all DataRobot metrics for binary
    classification and display the lift chart, roc curve, and feature impact chart.

    *For Regression Models with external evaluation data:*
    `evaluate` will score the dataset against all DataRobot metrics for regression
    and display the lift chart, residuals chart, and feature impact chart.

    Parameters
    ----------
    model : Union[Model, ModelOperator]
        The drx model that should be used in the evaluation.
    evaluation_data : Union[pd.DataFrame, str], optional
        The evaluation data to be used. If Pandas Dataframe, the data will be uploaded
        to DR and scored. If a string, should correspond to a previously uploaded
        external test set or an ai catalog id.

    Notes
    -----
    Only Binary and Regression models are presently supported; if no evaluation_data
    is provided only the metrics and feature impact plot will be included.

    """
    if isinstance(model, ModelOperator):
        model_to_evaluate = model._best_model
        assert model_to_evaluate is not None
    else:
        model_to_evaluate = model

    if evaluation_data is not None:
        ds_id = utils.create_task_new_thread(
            _compute_external_scores(model_to_evaluate, evaluation_data),
            wait=True,
        ).result()
    else:
        ds_id = None

    with designated_widget_handler(
        formatter=ModelCardFormatter(attr="model", as_html=True),
        filter_on=lambda x: int(getattr(x, "model", 0) is model_to_evaluate),
    ):
        logger.info(
            "Handling evaluate() call for a model",
            extra={
                "model": model_to_evaluate,
                "external_ds_id": ds_id,
                "opt_in": True,
            },
        )


async def _compute_external_scores(model: Model, evaluation_data: Union[pd.DataFrame, str]) -> str:
    ds_id = await _resolve_prediction_dataset_id(model, evaluation_data)
    assert model._project_id is not None
    assert model._model_id is not None
    await proj_client.post_external_scores(model._project_id, model._model_id, ds_id)
    return ds_id


async def _resolve_prediction_dataset_id(
    model: Model, evaluation_data: Union[pd.DataFrame, str]
) -> str:
    """Resolve user-provided evaluation data into DR pred dataset id

    Upload external dataset if needed
    """
    if isinstance(evaluation_data, str):
        ds_json = await proj_client.get_prediction_dataset(model._project_id, evaluation_data)  # type: ignore[arg-type]
        if "id" in ds_json:
            return cast(str, ds_json["id"])
    # Runs if evaluation data is a dataframe or an ai catalog id
    ds_json = await model._create_pred_dataset(model._project_id, evaluation_data)  # type: ignore[arg-type]
    return cast(str, ds_json["id"])


def import_parametric_model(model: AutoMLModel, model_formula: str) -> Model:
    """Import a linear model onto the DataRobot leaderboard

    bp_base = find_smallest_non_additive_eureqa_blueprint()
    eureqa_model = model.train(bp_base)
    return = tune_eureqa(eureqa_model)

    Parameters
    ----------
    model : AutoMLModel
        A drx AutoMLModel instance
    model_formula : str
        A formula for a simple parametric model.

        See: https://docs.datarobot.com/en/docs/modeling/reference/eureqa-ref/custom-expressions.html
    """

    # Credit to Credit to Lukas Innig for his notebook here:
    # https://github.com/datarobot/data-science-scripts/blob/master/lukas/Eureqa%20for%20simple%20external%20models.ipynb

    logger.info("Fitting initial linear model...")
    base_model_id = utils.create_task_new_thread(
        _make_base_eureqa_bp(model._project_id), wait=True  # type: ignore[arg-type]
    ).result()
    logger.info("Tuning model...")
    tuned_model_id = utils.create_task_new_thread(
        _convert_base_model_using_formula(model._project_id, base_model_id, model_formula),  # type: ignore[arg-type]
        wait=True,
    ).result()

    return Model(model._project_id, tuned_model_id)


async def _make_base_eureqa_bp(project_id: str) -> str:
    """Trains a simple Eureqa Blueprint to be replaced later

    Returns
    -------
    str
        The id of the trained Eureqa blueprint
    """
    blueprints = await proj_client.get_blueprints(project_id)

    # Find eureqa models that's are not GAM variants
    eureqa_bps = [
        bp
        for bp in blueprints
        if "Eureqa" in bp["modelType"]  # type: ignore[index]
        and "Additive" not in bp["modelType"]  # type: ignore[index]
    ]
    # Search for fewest generations
    fast_eureqa_model_bp = sorted(
        eureqa_bps, key=lambda bp: int(re.findall(r"\d+", bp["modelType"])[0])  # type: ignore[index]
    )[0]

    # Fit initial model to get on leaderboard
    status_url = await proj_client.post_models(project_id, fast_eureqa_model_bp["id"])  # type: ignore[index]
    return await proj_client.await_model(status_url)


async def _convert_base_model_using_formula(
    project_id: str, model_id: str, model_formula: str
) -> str:
    """
    Runs advanced tuning on blueprint with the formula as the default option.

    Constrains variable changes so the passed in formula doesn't move

    Returns
    -------
    str
        The id of a tuned eureqa blueprint that is actually the model
    """

    params = {
        "FeatureSelection: max_features": "no_limit",
        "FeatureSelection: method": "no_selection",
        "max_generations": 32,
        "target_expression_string": model_formula,
    }
    advanced_tuning = await proj_client.get_advanced_tuning_parameters(project_id, model_id)
    advanced_tuning_session_parameters = advanced_tuning["tuningParameters"]

    post_tuning_params = {
        "tuningParameters": [],
        "tuningDescription": "Import user defined parameteric model",
    }
    for i in advanced_tuning_session_parameters:
        if "building_block_" in i["parameterName"]:
            post_tuning_params["tuningParameters"].append(  # type: ignore[attr-defined]
                {"parameterId": i["parameterId"], "value": 0}
            )
        elif i["parameterName"] in [
            "FeatureSelection: max_features",
            "FeatureSelection: method",
            "max_generations",
            "target_expression_string",
        ]:
            post_tuning_params["tuningParameters"].append(  # type: ignore[attr-defined]
                {"parameterId": i["parameterId"], "value": params[i["parameterName"]]}
            )
    status_url = await proj_client.post_advanced_tuning_parameters(
        project_id, model_id, post_tuning_params
    )
    return await proj_client.await_model(status_url)
