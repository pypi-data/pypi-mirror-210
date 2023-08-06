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
# pylint: disable=cyclic-import
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
import logging
import re
import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

import numpy as np
import pandas as pd

from datarobot.utils import to_api
import datarobotx.client.datasets as dataset_client
import datarobotx.client.deployments as deploy_client
import datarobotx.client.projects as proj_client
from datarobotx.common import ts_helpers, utils
from datarobotx.common.config import context
from datarobotx.common.utils import FutureDataFrame
from datarobotx.models import share
from datarobotx.models.deployment import Deployment
from datarobotx.viz.leaderboard import LeaderboardFormatter
from datarobotx.viz.modelcard import ModelCardFormatter
from datarobotx.viz.viz import designated_widget_handler

if TYPE_CHECKING:
    import datarobot
    from datarobotx import DRConfig

logger = logging.getLogger("drx")


@utils.hidden_instance_classmethods
class Model:
    """
    DataRobot training model

    Represents a model on a project leaderboard. Implements prediction and deployment
    asynchronously.

    Parameters
    ----------
    model_id : str, optional
        DataRobot id for the model from which to initialize the object
    project_id : str, optional
        DataRobot id for the project containing the model from which to initialize
        the object

    """

    def __init__(self, project_id: Optional[str] = None, model_id: Optional[str] = None) -> None:
        self._project_id = project_id
        self._model_id = model_id

    @classmethod
    def from_url(cls, url: str) -> Model:
        """
        Class method to initialize from a URL string

        Useful for copy and pasting between GUI and notebook environments

        Parameters
        ----------
        url : str
            URL of a DataRobot GUI page related to the model of interest

        Returns
        -------
        model : Model
            The constructed Model object

        """
        try:
            project_id, model_id = re.match(  # type: ignore[union-attr]
                "^.*/projects/([0-9a-fA-F]+)/models/([0-9a-fA-F]+)/?.*$", url
            ).group(1, 2)
        except AttributeError:
            raise ValueError("Could not extract a model and project id from the provided url.")
        return Model(model_id=model_id, project_id=project_id)

    @property
    def dr_model(self) -> "datarobot.Model":
        """DataRobot python client datarobot.Model object

        Returns
        -------
        datarobot.Model
            datarobot.Model object associated with this drx.Model
        """
        if self._project_id is None or self._model_id is None:
            raise RuntimeError(
                "Cannot retrieve a datarobot.Model object from an uninitialized model."
            )
        import datarobot

        return datarobot.Model.get(self._project_id, self._model_id)

    @property
    def dr_project(self) -> "datarobot.Project":
        """DataRobot python client datarobot.Project object

        Returns
        -------
        datarobot.Project
            datarobot.Project object associated with this drx.Model
        """
        if self._project_id is None:
            raise RuntimeError(
                "Cannot to retrieve a datarobot.Project from an uninitialized model."
            )
        import datarobot

        return datarobot.Project.get(self._project_id)

    def predict(self, X: Union[pd.DataFrame, str], **kwargs: Any) -> FutureDataFrame:
        """
        Make batch predictions using the model

        Predictions are calculated asynchronously - returns immediately but
        reinitializes the returned DataFrame with data once predictions are
        completed.

        Predictions are made within the project containing the model using modeling
        workers. For real-time predictions, first deploy the model.

        Parameters
        ----------
        X : pandas.DataFrame or str
            Dataset to be scored - target column can be included or omitted.
            If str, can be AI catalog dataset id or name (if unambiguous)
        **kwargs : Any
            Other key word arguments to pass to the _predict function

        Returns
        -------
        FutureDataFrame
            Resulting predictions (contained in the column 'predictions')
            Returned immediately, updated automatically when results are
            completed. If attribute access is attempted, will block until results
            are completed.

        """
        future = utils.create_task_new_thread(self._predict(X, **kwargs))
        return utils.FutureDataFrame(future=future)

    def predict_proba(self, X: Union[pd.DataFrame, str], **kwargs: Any) -> FutureDataFrame:
        """
        Calculate class probabilities using the model

        Only available for classifier models.

        Parameters
        ----------
        X : pandas.DataFrame or str
            Dataset to compute class probabilities on; target column can be included
            or omitted. If str, can be AI catalog dataset id or name (if unambiguous)
        **kwargs : Any
            Other key word arguments to pass to the _predict function

        Returns
        -------
        FutureDataFrame
            Resulting predictions; probabilities for each label are contained in the
            column 'class_{label}'; returned immediately, updated automatically
            when results are completed. If attribute access is attempted, will block
            until results are completed.

        See Also
        --------
        predict
        """
        future = utils.create_task_new_thread(self._predict(X, class_probabilities=True, **kwargs))
        return utils.FutureDataFrame(future=future)

    async def _predict(
        self, X: Union[pd.DataFrame, str], class_probabilities: bool = False, **kwargs: Any
    ) -> None:
        """Orchestrate training model batch predictions."""
        await self._validate_predict_args(class_probabilities)
        project_id = str(self._project_id)
        project_data = await proj_client.get_project(project_id)
        uses_ts_helpers = (
            project_data["partition"]["useTimeSeries"]
            and project_data["unsupervisedType"] != "clustering"
            and ts_helpers._has_ts_helper_args(**kwargs)
        )

        json: Dict[str, Any] = {"modelId": self._model_id}

        if uses_ts_helpers:
            (
                X,
                time_series_parameters,
                ts_project_settings,
            ) = await ts_helpers.prepare_prediction_data(project_id, X, **kwargs)
        else:
            ts_api_arguments = [
                "predictions_start_date",
                "predictions_end_date",
                "forecast_point",
            ]
            time_series_parameters = to_api(
                {key: kwargs[key] for key in ts_api_arguments if key in kwargs}
            )
        json.update(time_series_parameters)

        prediction_ds = await self._create_pred_dataset(
            project_id,
            X,
            relax_kia_check=uses_ts_helpers
            or kwargs.get("relax_known_in_advance_features_check", False),
        )

        json["datasetId"] = prediction_ds["id"]
        predictions_id = await proj_client.post_predictions(pid=project_id, json=json)

        assert self._project_id is not None
        df = await proj_client.get_predictions(
            pid=project_id,
            predictions_id=predictions_id,
        )

        df = await self._format_predictions(df, class_probabilities)

        if uses_ts_helpers:
            df = ts_helpers.post_process_predictions(
                df, ts_project_settings, for_dates=kwargs.get("for_dates")
            )
        logger.info("Predictions complete", extra={"is_header": True})
        return df

    @staticmethod
    async def _create_pred_dataset(
        pid: str, X: Union[pd.DataFrame, str], relax_kia_check: bool = False
    ) -> Dict[str, Any]:
        """Create a prediction dataset server-side for DR to make predictions"""
        if isinstance(X, pd.DataFrame):
            prediction_ds = await proj_client.post_prediction_datasets_file_uploads(
                pid=pid,  # type: ignore[arg-type]
                payload=utils.prepare_df_upload(X),
                relax_kia_check=relax_kia_check,
            )
        elif isinstance(X, str):
            dataset_id = await dataset_client.resolve_dataset_id(X)
            prediction_ds = await proj_client.post_prediction_datasets_dataset_uploads(
                pid=pid, dataset_id=dataset_id, relax_kia_check=relax_kia_check
            )
        else:
            raise TypeError(
                "Provided data to be scored must be a pandas.DataFrame "
                + "or the DataRobot dataset id or name."
            )

        return prediction_ds

    async def _format_predictions(
        self, df: pd.DataFrame, class_probabilities: bool
    ) -> pd.DataFrame:
        """Format dataframe returned by DataRobot pre-deployment predictions route"""
        project_json = await proj_client.get_project(pid=self._project_id)  # type: ignore[arg-type]

        if project_json["partition"]["useTimeSeries"]:
            if (
                project_json["target"] is None and project_json.get("unsupervisedType") == "anomaly"
            ):  # TS Anomaly
                df = df.drop(["actualValue"], axis=1, errors="ignore")
                if class_probabilities:
                    df = df.rename(columns={"prediction": "class_Anomalous"}).assign(
                        class_Normal=lambda x: 1 - x["class_Anomalous"]
                    )
                else:
                    df["prediction"] = np.where(df["prediction"] > 0.5, "Anomalous", "Normal")
            ignore_columns_with = "prediction" if class_probabilities else "class"

            df = df.loc[:, ~df.columns.str.startswith(ignore_columns_with)].set_index("row_id")
            df = df.drop(["target"], axis=1, errors="ignore")
            df["forecastPoint"] = pd.to_datetime(df["forecastPoint"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values(by=["forecastPoint", "forecastDistance"])

        elif project_json["targetType"] is not None:  # non-ts, supervised project
            keep_columns_with = "class" if class_probabilities else "prediction"
            df = df.set_index("row_id").filter(regex=keep_columns_with)
        elif project_json["targetType"] is None and project_json["unsupervisedType"] in (
            "anomaly",
            "clustering",
            None,
        ):
            if not class_probabilities:
                keep_columns_with = "prediction"
                if project_json["unsupervisedType"] == "anomaly":
                    df["prediction"] = df["prediction"] > 0.5
                    df["prediction"] = df["prediction"].replace(
                        {True: "Anomalous", False: "Normal"}
                    )
            else:
                keep_columns_with = "class"
                if project_json["unsupervisedType"] == "anomaly":
                    df["class_Anomalous"] = df["prediction"]
                    df["class_Normal"] = 1 - df["prediction"]
            df = df.set_index("row_id").filter(regex=keep_columns_with)

        return df.reset_index(drop=True)

    async def _validate_predict_args(self, class_probabilities: bool) -> None:
        """Validate that predictions can be made."""
        if self._project_id is None or self._model_id is None:
            raise RuntimeError("Cannot make predictions with an uninitialized model.")
        project_json, model_json = await asyncio.gather(
            proj_client.get_project(pid=self._project_id),
            proj_client.get_model(pid=self._project_id, model_id=self._model_id),
        )
        if class_probabilities and project_json["targetType"] not in [
            "Binary",
            "Multiclass",
            "Multilabel",
            None,
        ]:
            raise ValueError(
                f"Model {self._model_id} from Project {self._project_id} does not "
                + "support calculating class probabilities."
            )
        self._log_starting_predictions(
            project_id=project_json["id"],
            model_id=model_json["id"],
            project_name=project_json["projectName"],
            model_name=model_json["modelType"].rstrip(),
        )

    def deploy(self, name: Optional[str] = None) -> Deployment:
        """
        Deploy the model into ML Ops

        Parameters
        ----------
        name : str, optional, default=None
            Name for the deployment. If None, a name will be generated

        Returns
        -------
        Deployment
            Resulting ML Ops deployment
        """

        if self._project_id is None or self._model_id is None:
            raise RuntimeError("Cannot deploy an uninitialized model. ")

        deployment = Deployment()
        utils.create_task_new_thread(self._deploy(deployment, name=name))
        return deployment

    async def _deploy(self, deployment: Deployment, name: Optional[str] = None) -> None:
        logger.info("Creating deployment", extra={"is_header": True})
        await self._prepare_for_deploy()
        if name is None:
            name = utils.generate_name()
        deploy_id = await deploy_client.deploy_learning_model(
            name=name,
            pid=self._project_id,  # type: ignore[arg-type]
            model_id=self._model_id,  # type: ignore[arg-type]
        )
        deployment._deployment_id = deploy_id

        project_json, model_json, deployment_json = await asyncio.gather(
            proj_client.get_project(pid=self._project_id),  # type: ignore[arg-type]
            proj_client.get_model(pid=self._project_id, model_id=self._model_id),  # type: ignore[arg-type]
            deploy_client.get_deployment(did=deploy_id),
        )
        self._log_created_deployment(
            project_id=project_json["id"],
            model_id=model_json["id"],
            deployment_id=deploy_id,
            project_name=project_json["projectName"],
            model_name=model_json["modelType"].rstrip(),
            deployment_name=deployment_json["label"],
        )
        logger.info("Deployment complete", extra={"is_header": True})

    async def _prepare_for_deploy(self) -> None:
        """Prepare a model for deployment including explanations capabilities"""
        logger.info("Calculating feature impact...")
        project_json, _ = await asyncio.gather(
            proj_client.get_project(pid=self._project_id),  # type: ignore[arg-type]
            proj_client.get_feature_impact(pid=self._project_id, model_id=self._model_id),  # type: ignore[arg-type]
        )

        if not (
            project_json["targetType"] is None and project_json["unsupervisedType"] == "clustering"
        ) and not (project_json["targetType"] == "Multilabel"):
            logger.info("Initializing model for prediction explanations...")
            await proj_client.initialize_prediction_explanations(
                pid=self._project_id, model_id=self._model_id  # type: ignore[arg-type]
            )

    @staticmethod
    def _log_starting_predictions(
        project_id: str, model_id: str, project_name: str, model_name: str
    ) -> None:
        """Log that predictions are about to be made"""
        eda_url = context._webui_base_url + f"/projects/{project_id}/eda"
        model_url = context._webui_base_url + f"/projects/{project_id}/models/{model_id}"
        msg = (
            "Making predictions with model "
            + f"[{model_name}]({model_url}) "
            + "from project "
            + f"[{project_name}]({eda_url})"
        )
        logger.info("Making predictions", extra={"is_header": True})
        logger.info(msg)

    @staticmethod
    def _log_created_deployment(
        project_id: str,
        model_id: str,
        deployment_id: str,
        project_name: str,
        model_name: str,
        deployment_name: str,
    ) -> None:
        """Log that a deployment has been created"""

        eda_url = context._webui_base_url + f"/projects/{project_id}/eda"
        model_url = context._webui_base_url + f"/projects/{project_id}/models/{model_id}/blueprint"
        deploy_url = context._webui_base_url + f"/deployments/{deployment_id}/overview"
        msg = (
            f"Created deployment [{deployment_name}]({deploy_url}) "
            + f"from model [{model_name}]({model_url}) "
            + f"in project [{project_name}]({eda_url})"
        )
        logger.info(msg)

    def _ipython_display_(self) -> None:
        """
        Render a model card for widget-enabled ipython environments

        Called by ipython when last expression in a cell is not an assignment operation
        and the expression evaluates to an instanceof this object.

        Dynamically setup and teardown a logging handler for rendering the model card.
        """
        with designated_widget_handler(
            formatter=ModelCardFormatter(attr="model", as_html=True),
            filter_on=lambda x: int(getattr(x, "model", 0) is self),
        ):
            logger.info(
                "Handling _ipython_display_() call for Model",
                extra={"model": self, "opt_in": True},
            )

    def __str__(self) -> str:
        """
        Render model name + link to model
        """
        formatter = ModelCardFormatter(attr="model", as_html=False)
        record = logging.makeLogRecord({"model": self, "opt_in": True})
        record = utils.create_task_new_thread(
            formatter.add_format_context(record), wait=True
        ).result()
        return formatter.format(record)


class ModelOperator:
    """Abstract base class for models that wrap and orchestrate DataRobot

    Implements shared behaviors (e.g. pedict, deploy, share, etc.) but
    not fit() which has public interfaces that vary depending on problem
    type
    """

    def __init__(self) -> None:
        self._project_id: Optional[str] = None
        self._leaderboard: Optional[list[str]] = None
        self._fitting_underway: Optional[bool] = None
        self._dr_config: Optional[DRConfig] = None

    @property
    def _best_model(self) -> Optional[Model]:
        """Present champion model"""
        if self._leaderboard is None or len(self._leaderboard) == 0:
            return None
        if isinstance(self._leaderboard, list):
            return Model(
                project_id=self._project_id,
                model_id=self._leaderboard[0],  # pylint: disable=E1136
            )

    @property
    def dr_model(self) -> "datarobot.Model":
        """DataRobot python client datarobot.Model object for the present champion

        Returns
        -------
        datarobot.Model
            datarobot.Model object associated with this drx model
        """
        if self._best_model is None:
            raise RuntimeError(
                "Cannot retrieve a datarobot.Model object from an uninitialized drx model."
            )

        return self._best_model.dr_model

    @property
    def dr_project(self) -> "datarobot.Project":
        """DataRobot python client datarobot.Project object

        Returns
        -------
        datarobot.Project
            datarobot.Project object associated with this drx.Model
        """
        if self._project_id is None:
            raise RuntimeError("Cannot retrieve a datarobot.Project from an uninitialized model.")
        import datarobot

        return datarobot.Project.get(self._project_id)

    def predict(
        self, X: pd.DataFrame, wait_for_autopilot: bool = False, **kwargs: Any
    ) -> FutureDataFrame:
        """
        Make batch predictions using the present champion

        Predictions are calculated asynchronously - returns immediately but
        reinitializes the returned DataFrame with data once predictions are
        completed.

        Predictions are made within the project containing the model using modeling
        workers. For real-time predictions, first deploy the model.

        Parameters
        ----------
        X : pandas.DataFrame
            Dataset to be scored - target column can be included or omitted
        wait_for_autopilot : bool, optional, default=False
            If True, wait for autopilot to complete before making predictions
            In non-notebook environments, fit() will always block until complete
        **kwargs : Any
            Other key word arguments to pass to the _predict function

        Returns
        -------
        FutureDataFrame
            Resulting predictions (contained in the column 'predictions')
            Returned immediately, updated automatically when results are
            completed.

        """
        return self._predict(X, wait_for_autopilot=wait_for_autopilot, **kwargs)

    def predict_proba(
        self, X: pd.DataFrame, wait_for_autopilot: bool = False, **kwargs: Any
    ) -> FutureDataFrame:
        """
        Calculate class probabilities using the present champion

        Only available for classifier and clustering models.

        Parameters
        ----------
        X : pandas.DataFrame
            Dataset to compute class probabilities on; target column can be included
            or omitted
        wait_for_autopilot : bool, optional, default=False
            If True, wait for autopilot to complete before making predictions
            In non-notebook environments, fit() will always block until complete
        **kwargs : Any
            Other key word arguments to pass to the _predict function

        Returns
        -------
        FutureDataFrame
            Resulting predictions; probabilities for each label are contained in the
            column 'class_{label}'; returned immediately, updated automatically
            when results are completed.

        See Also
        --------
        predict

        """

        return self._predict(
            X, class_probabilities=True, wait_for_autopilot=wait_for_autopilot, **kwargs
        )

    def _predict(
        self,
        X: Union[pd.DataFrame, str],
        class_probabilities: bool = False,
        wait_for_autopilot: bool = False,
        **kwargs: Any,
    ) -> FutureDataFrame:
        """Private method for making predictions with predict() or predict_proba()"""
        if self._best_model is None and not self._fitting_underway:
            raise RuntimeError("fit() must be called before making predictions")

        if wait_for_autopilot:
            logger.info("Waiting for autopilot to complete...", extra={"is_header": True})
            self._wait()

        elif self._best_model is None:
            logger.info("Waiting for a trained model...", extra={"is_header": True})
            while self._best_model is None:
                time.sleep(context._concurrency_poll_interval)

        future = utils.create_task_new_thread(
            self._best_model._predict(X, class_probabilities=class_probabilities, **kwargs)  # type: ignore[union-attr]
        )

        return utils.FutureDataFrame(future=future)

    def deploy(
        self, wait_for_autopilot: Optional[bool] = False, name: Optional[str] = None
    ) -> Deployment:
        """
        Deploy the model into ML Ops

        Returns
        -------
        Deployment
            Resulting ML Ops deployment
        wait_for_autopilot : bool, optional, default=False
            If True, wait for autopilot to complete before deploying the model
            In non-notebook environments, fit() will always block until complete
        name : str, optional, default=None
            Name for the deployment. If None, a name will be generated
        """

        if wait_for_autopilot:
            logger.info("Waiting for autopilot to complete...", extra={"is_header": True})
            self._wait()
            assert self._best_model is not None
        elif self._best_model is None:
            raise RuntimeError("No model presently available to deploy.")

        return self._best_model.deploy(name=name)

    def share(self, emails: Union[str, List[str]]) -> None:
        """
        Share a project with other users.
        Sets the user role as an owner of the project.

        Parameters
        ----------
        emails : Union[str, list]
            A list of email addresses of users to share with
        """
        if self._project_id is None:
            raise RuntimeError("Cannot share project from an uninitialized model.")

        share.share(self._project_id, emails)

    async def _fit(self, X: Any, *args: Any, **kwargs: Any) -> None:
        """Abstract fitting method stub"""

    def _wait(self) -> ModelOperator:
        """Wait for fitting to finish"""
        while self._fitting_underway:
            time.sleep(context._concurrency_poll_interval)
        return self

    @staticmethod
    async def _log_champion(best_model: Optional[Model] = None, ascii_art: bool = True) -> None:
        """Log the champion model"""
        if best_model is None:
            return
        model_json = await proj_client.get_model(best_model._project_id, best_model._model_id)  # type: ignore[arg-type]
        url = (
            context._webui_base_url
            + f"/projects/{best_model._project_id}/models/{model_json['id']}/blueprint"
        )
        champion = f"Champion model: [{model_json['modelType'].rstrip()}]({url})"
        extra = {}
        if ascii_art:
            extra["is_champion_msg"] = True
        logger.info(champion, extra=extra)

    def _ipython_display_(self) -> None:
        """
        Render a leaderboard for widget-enabled ipython environments

        Called by ipython when last expression in a cell is not an assignment operation
        and the expression evaluates to an instanceof this object.

        Dynamically setup and teardown a logging handler for rendering the leaderboard.
        """

        with designated_widget_handler(
            formatter=LeaderboardFormatter(attr="model_operator", as_html=True),
            filter_on=lambda x: int(getattr(x, "model_operator", 0) is self),
            remove_when=(lambda: not self._fitting_underway) if self._fitting_underway else None,
        ):
            logger.info(
                "Handling _ipython_display_() call for ModelOperator",
                extra={"model_operator": self, "opt_in": True},
            )

    def __str__(self) -> str:
        """
        Render a text leaderboard
        """
        formatter = LeaderboardFormatter(attr="model_operator", as_html=False)
        record = logging.makeLogRecord({"model_operator": self, "opt_in": True})
        record = utils.create_task_new_thread(
            formatter.add_format_context(record), wait=True
        ).result()
        return formatter.format(record)

    @staticmethod
    def _with_fitting_underway(f: Callable) -> Callable:  # type: ignore[type-arg]
        """Decorator for managing the fitting underway flag

        Used to decorate fit orchestration logic e.g. _fit(); ensures flag is properly
        updated, even if exceptions are encountered
        """

        @wraps(f)
        def fitting_underway_outer_wrapper(*args: Any, **kwargs: Any) -> Awaitable:  # type: ignore[type-arg]
            """Manage the fitting underway flag while orchestrating fit"""
            model: ModelOperator = args[0]
            # set flag immediately, synchronously before async work is initiated
            model._fitting_underway = True

            async def fitting_underway_inner_wrapper(*args: Any, **kwargs: Any) -> Awaitable:  # type: ignore[type-arg]
                try:
                    return await f(*args, **kwargs)  # type: ignore[no-any-return]
                finally:
                    model._fitting_underway = False

            return fitting_underway_inner_wrapper(*args, **kwargs)

        return fitting_underway_outer_wrapper
