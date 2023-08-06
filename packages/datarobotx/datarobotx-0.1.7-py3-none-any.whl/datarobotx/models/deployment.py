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
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import datetime as dt
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

import datarobot
from datarobot.utils import to_api
import datarobotx.client.deployments as deploy_client
from datarobotx.common import ts_helpers, utils
from datarobotx.common.config import context
from datarobotx.models import share

logger = logging.getLogger("drx")


@utils.hidden_instance_classmethods
class Deployment:
    """
    DataRobot ML Ops deployment

    Implements real-time predictions on ML Ops deployments

    Parameters
    ----------
    deployment_id : str, optional
        DataRobot id for the deployment from which to initialize the object

    """

    def __init__(self, deployment_id: Optional[str] = None) -> None:
        self._deployment_id = deployment_id

    @property
    def dr_deployment(self) -> datarobot.Deployment:
        """DataRobot python client datarobot.Deployment object

        Returns
        -------
        datarobot.Deployment
            datarobot.Deployment object associated with this drx.Deployment
        """
        if self._deployment_id is None:
            raise Exception(
                "Cannot to retrieve a datarobot.Deployment from an uninitialized deployment."
            )

        return datarobot.Deployment.get(self._deployment_id)

    @classmethod
    def from_url(cls, url: str) -> Deployment:
        """
        Class method to initialize from a URL string

        Useful for copy and pasting between GUI and notebook environments

        Parameters
        ----------
        url : str
            URL of a DataRobot GUI page related to the deployment of interest

        Returns
        -------
        model : Deployment
            The deployed model object

        """

        try:
            deployment_id = re.match("^.*/deployments/([0-9a-fA-F]+)/?.*$", url).group(1)  # type: ignore[union-attr]
        except AttributeError:
            raise ValueError("Could not extract a deployment id from the provided url.")

        return Deployment(deployment_id=deployment_id)

    def predict(
        self,
        X: pd.DataFrame,
        batch_mode: bool = False,
        max_explanations: Union[int, str, None] = None,
        as_of: Optional[Union[str, dt.datetime]] = None,
        for_dates: Optional[
            Union[str, dt.datetime, Tuple[str, str], Tuple[dt.datetime, dt.datetime]]
        ] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Make predictions on X asynchronously using the deployment

        Returns empty DataFrame which will be updated with results when complete

        Parameters
        ----------
        X: pd.DataFrame
            Data to make predictions on
        batch_mode: bool (default=False)
            If True, use batch mode for predictions
        max_explanations: int or 'all' (default=None)
            Number of explanations to return for each prediction.
            Note that 'all' is supported for deployments using SHAP models
            only.
        as_of: str (default=None)
            Applies to time series only. Forecast point to use for predictions.
            If not provided on a forecast, the latest forecast point will be used.
            Note that dates passed in are parsed using pd.to_datetime.
        for_dates: str or tuple of str (default=None)
            Applies to time series only. Date(s) to return predictions for.
            If a single date is specified, a single prediction will be returned
            for that date. If a tuple of dates is specified,
            a prediction will be returned for each date in the range.
            Note that dates passed in are parsed using pd.to_datetime.
        **kwargs :
            Additional optional predict-time parameters to pass to DataRobot
            Examples: 'forecast_point', 'predictions_start_date', 'predictions_end_date',
            'relax_known_in_advance_features_check'

        """
        out = self._dispatch_predict(
            X,
            batch_mode,
            max_explanations=max_explanations,
            as_of=as_of,
            for_dates=for_dates,
            **kwargs,
        )
        assert isinstance(out, pd.DataFrame)
        return out

    def predict_proba(
        self,
        X: pd.DataFrame,
        batch_mode: bool = False,
        max_explanations: Union[int, str, None] = None,
        as_of: Optional[Union[str, dt.datetime]] = None,
        for_dates: Optional[
            Union[str, dt.datetime, Tuple[str, str], Tuple[dt.datetime, dt.datetime]]
        ] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Calculate class probabilities on X asynchronously using the deployment

        Returns empty DataFrame which will be updated with results when complete

        Parameters
        ----------
        X: pd.DataFrame
            Data to make predictions on
        batch_mode: bool (default=False)
            If True, use batch mode for predictions
        max_explanations: int or 'all' (default=None)
            Number of explanations to return for each prediction.
            Note that 'all' is supported for deployments using SHAP models
            only.
        as_of: str (default=None)
            Applies to time series only. Forecast point to use for predictions.
            If not provided on a forecast, the latest forecast point will be used.
            Note that dates passed in are parsed using pd.to_datetime.
        for_dates: str or tuple of str (default=None)
            Applies to time series only. Date(s) to return predictions for.
            If a single date is specified, a single prediction will be returned
            for that date. If a tuple of dates is specified,
            a prediction will be returned for each date in the range.
            Note that dates passed in are parsed using pd.to_datetime.
        **kwargs :
            Additional optional predict-time parameters to pass to DataRobot
            Examples: 'forecast_point', 'predictions_start_date', 'predictions_end_date',
            'relax_known_in_advance_features_check'
        """
        out = self._dispatch_predict(
            X,
            batch_mode=batch_mode,
            max_explanations=max_explanations,
            class_probabilities=True,
            as_of=as_of,
            for_dates=for_dates,
            **kwargs,
        )
        assert isinstance(out, pd.DataFrame)
        return out

    def predict_unstructured(self, X: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions with data asynchronously using the deployment

        Returns empty dict which will be updated with results when complete

        Parameters
        ----------
        X: Dict[str, Any]
            Data to make predictions on

        """
        out = self._dispatch_predict(X, batch_mode=False, unstructured=True)
        assert not isinstance(out, pd.DataFrame)
        return out

    def _dispatch_predict(
        self,
        X: Union[pd.DataFrame, Dict[str, Any]],
        batch_mode: bool,
        class_probabilities: bool = False,
        max_explanations: Union[int, str, None] = None,
        unstructured: bool = False,
        as_of: Optional[Union[str, dt.datetime]] = None,
        for_dates: Optional[
            Union[str, dt.datetime, Tuple[str, str], Tuple[dt.datetime, dt.datetime]]
        ] = None,
        **kwargs: Any,
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """Private method for dispatching predictions work

        Behavior depends on requested predictions type (structured vs. unstructured)
        and whether this deployment object has been initialized
        """

        if isinstance(X, str):
            raise NotImplementedError(
                "Local dataset is required for prediction. AI Catalog IDs are not supported yet."
            )

        if self._deployment_id is None:
            logger.info("Waiting for deployment to be initialized...", extra={"is_header": True})
            while self._deployment_id is None:
                time.sleep(context._concurrency_poll_interval)

        future = utils.create_task_new_thread(
            self._predict(
                X,
                batch_mode=batch_mode,
                class_probabilities=class_probabilities,
                max_explanations=max_explanations,
                unstructured=unstructured,
                as_of=as_of,
                for_dates=for_dates,
                **kwargs,
            )
        )

        if not unstructured:
            result: Union[pd.DataFrame, Dict[str, Any]] = utils.FutureDataFrame(future=future)
        else:
            result = utils.FutureDict(future=future)
        return result

    async def _predict(
        self,
        X: Union[pd.DataFrame, Dict[str, Any]],
        batch_mode: bool,
        class_probabilities: bool = False,
        max_explanations: Union[int, str, None] = None,
        unstructured: bool = False,
        **kwargs: Any,
    ) -> Union[pd.DataFrame, Dict[str, Any]]:

        deploy_info = await self._validate_predict_args(
            class_probabilities,
            max_explanations=max_explanations,
        )
        uses_ts_helpers = (
            deploy_info.model_kind.isTimeSeries
            and not deploy_info.model_kind.isClustering
            and ts_helpers._has_ts_helper_args(**kwargs)
        )

        if uses_ts_helpers:
            (
                X,
                time_series_parameters,
                ts_project_settings,
            ) = await ts_helpers.prepare_prediction_data(
                str(deploy_info.model_kind.projectId),
                X,
                as_of=kwargs.get("as_of"),
                for_dates=kwargs.get("for_dates"),
            )
            if batch_mode:
                time_series_parameters["relaxKnownInAdvanceFeaturesCheck"] = True

        else:
            ts_api_arguments = [
                "predictions_start_date",
                "predictions_end_date",
                "forecast_point",
                "relax_known_in_advance_features_check",
            ]

            time_series_parameters = to_api(
                {key: kwargs[key] for key in ts_api_arguments if key in kwargs}
            )

        if not unstructured:
            if not batch_mode:
                preds_df = await deploy_client.post_predictions(
                    did=self._deployment_id,  # type: ignore[arg-type]
                    dr_key=deploy_info.dr_key,
                    pred_server_endpoint=deploy_info.endpoint,
                    payload=utils.prepare_df_upload(X),
                    max_explanations=max_explanations,  # type: ignore[arg-type]
                    ts_params=time_series_parameters,
                )
            else:
                pred_url = await deploy_client.post_batch_predictions(
                    did=self._deployment_id,  # type: ignore[arg-type]
                    payload=utils.prepare_df_upload(X),
                    max_explanations=max_explanations,  # type: ignore[arg-type]
                    ts_params=time_series_parameters,
                )
                preds_df = await deploy_client.await_batch_job_completion(pred_url)

            result = PredictionFormatter(
                preds=preds_df,
                model_kind=deploy_info.model_kind,
                class_probabilities=class_probabilities,
                max_explanations=max_explanations,  # type: ignore[arg-type]
            ).format()
        else:
            result = await deploy_client.post_predictions_unstructured(
                did=self._deployment_id,  # type: ignore[arg-type]
                dr_key=deploy_info.dr_key,
                pred_server_endpoint=deploy_info.endpoint,
                data=X,
            )
        if uses_ts_helpers:
            result = ts_helpers.post_process_predictions(
                result, ts_project_settings, for_dates=kwargs.get("for_dates")
            )

        logger.info("Predictions complete", extra={"is_header": True})
        return result

    async def _validate_predict_args(
        self, class_probabilities: bool, max_explanations: Union[int, str, None]
    ) -> DeploymentInfo:
        """Raise errors if predictions request is invalid

        Returns
        -------
        DeploymentInfo
            Data structure containing elements needed to request and format predictions
        """
        if self._deployment_id is None:
            raise RuntimeError(
                "Deployment not available to make predictions. "
                + "To make predictions deployment_id must be defined."
            )

        deploy_json, settings_json = await asyncio.gather(
            deploy_client.get_deployment(did=self._deployment_id),
            deploy_client.get_deployment_settings(did=self._deployment_id),
        )
        model_kind = ModelKind.infer_model_kind(
            settings_json=settings_json, deployment_json=deploy_json
        )

        if class_probabilities and model_kind.isRegression and model_kind.targetName is not None:
            raise RuntimeError(
                f"Deployment {self._deployment_id} does not "
                + "support calculating class probabilities."
            )
        if max_explanations is not None and (model_kind.isClustering or model_kind.isMultilabel):
            raise RuntimeError(
                f"Deployment {self._deployment_id} does not " + "support prediction explanations."
            )  # raise error client side to avoid ambiguous server message on uninitialized expls
        self._log_starting_predictions(
            deployment_id=self._deployment_id, deployment_name=deploy_json["label"]
        )
        return DeploymentInfo(
            model_kind=model_kind,
            dr_key=deploy_json["defaultPredictionServer"]["datarobot-key"],
            endpoint=deploy_json["defaultPredictionServer"]["url"] + "/predApi/v1.0",
        )

    def share(self, emails: Union[str, list[str]]) -> None:
        """
        Share a deployment with other users.
        Sets the user role as an owner of the deployment.

        Parameters
        ----------
        emails : Union[str, list]
            A list of email addresses of users to share with
        """
        if self._deployment_id is None:
            logger.info("Waiting for deployment to be initialized...", extra={"is_header": True})
            while self._deployment_id is None:
                time.sleep(context._concurrency_poll_interval)

        share.share(self._deployment_id, emails)

    @staticmethod
    def _log_starting_predictions(deployment_id: str, deployment_name: str) -> None:
        """Log that predictions are about to be made"""
        deploy_url = context._webui_base_url + f"/deployments/{deployment_id}/overview"
        msg = f"Making predictions with deployment [{deployment_name}]({deploy_url})"
        logger.info("Making predictions", extra={"is_header": True})
        logger.info(msg)


class PredictionFormatter:
    """
    Format DataRobot deployment predictions

    Reshape predictions from DataRobot RT and Batch deployment prediction API
    into sklearn-style format

    Parameters
    ----------
    preds : pd.DataFrame
        Predictions from DataRobot, requested as text/csv and read into pandas
    model_kind : ModelKind
        Capabilities and model type of the deployment
    class_probabilities : bool
        Whether class probabilities have been requested
    max_explanations : int, optional
        Number of prediction explanations requested
    """

    def __init__(
        self,
        preds: pd.DataFrame,
        model_kind: ModelKind,
        class_probabilities: bool,
        max_explanations: Optional[int] = None,
    ) -> None:
        self.preds_df = preds
        self.class_probabilities = class_probabilities
        self.model_kind = model_kind.confirm_model_kind_from_results(self.preds_df)
        self.max_explanations = max_explanations
        self.target_name = model_kind.targetName
        self.all_prediction_columns = list(
            filter(lambda col: re.search(re.escape("_PREDICTION"), col), preds.columns)
        )

    def format(self) -> pd.DataFrame:
        if self.target_name is not None:
            df = self.preds_df.rename(columns={self.target_name + "_PREDICTION": "prediction"})
        else:
            df = self.preds_df.rename(columns={"PREDICTION": "prediction"})

        if self.model_kind.isAnomalyDetectionModel:
            df = self._process_anomaly_detection_results(df)
        if self.model_kind.isClustering:
            df = self._process_clustering_results(df)
        if self.model_kind.isTimeSeries:
            df = self._process_timeseries_results(df)
        if self.model_kind.isMultilabel:
            df = self._process_multilabel_results(df)
        if self.model_kind.isBinary:
            df = self._process_binary_predictions(df)
        if self.max_explanations is not None:
            df = self._process_batch_explanations(df)
        df = self._process_supervised_model_class_probs(df)

        # Universal changes for all models
        df.drop(
            ["DEPLOYMENT_APPROVAL_STATUS", self.target_name, "CLASS_1"],
            axis=1,
            errors="ignore",
            inplace=True,
        )

        return df

    def _process_supervised_model_class_probs(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.class_probabilities and (self.target_name is not None):
            renamer = {
                old_col: PredictionFormatter._standardize_prediction_label(
                    self.target_name, old_col
                )
                for old_col in self.all_prediction_columns
            }
            df = df.rename(columns=renamer).drop("prediction", axis=1, errors="ignore")
        elif self.target_name is not None:
            df = df.drop(
                filter(lambda col: re.search(re.escape("_PREDICTION"), col), df.columns),
                axis=1,
                errors="ignore",
            )
        return df

    def _process_binary_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.class_probabilities:
            df = df.drop(
                ["THRESHOLD", "POSITIVE_CLASS", "prediction"],
                axis=1,
                errors="ignore",
            )
        else:
            df = df.drop(["THRESHOLD", "POSITIVE_CLASS"], axis=1, errors="ignore")
        return df

    def _process_multilabel_results(self, df: pd.DataFrame) -> pd.DataFrame:
        def swap_target(in_str: str, class_probabilities: bool) -> str:
            if "target_" in in_str and class_probabilities:
                return in_str.replace("target_", "class_").replace("_PROBABILITY", "")
            elif "target_" in in_str and not class_probabilities:
                return in_str.replace("target_", "prediction_").replace("_DECISION", "")
            else:
                return in_str

        def col_finder(cols: List[str], finder: str) -> List[str]:
            """Multi label batch predictions always return DECISION, THRESHOLD, and PROBABILITY
            if we ask for class_probabilities we want the PROBABILITY column if we don't we want the DECISION
            column. We want to keep all the other columns
            """
            return [
                col
                for col in cols
                if (finder.lower() in col.lower())
                and (
                    ("THRESHOLD" not in col.lower())
                    or ("DECISION" not in col.lower())
                    or ("PROBABILITY" not in col.lower())
                )
            ]

        if self.class_probabilities:
            cols_to_keep = col_finder(df.columns, "PROBABILITY")
            renamer = {
                col: swap_target(col, class_probabilities=self.class_probabilities)
                for col in cols_to_keep
            }
            new_cols = [
                swap_target(col, class_probabilities=self.class_probabilities)
                for col in cols_to_keep
            ]
            df = df.rename(columns=renamer)[new_cols]
        else:
            cols_to_keep = col_finder(df.columns, "DECISION")
            renamer = {
                col: swap_target(col, class_probabilities=self.class_probabilities)
                for col in cols_to_keep
            }
            new_cols = [
                swap_target(col, class_probabilities=self.class_probabilities)
                for col in cols_to_keep
            ]
            df = df.rename(columns=renamer)[new_cols]
        return df

    def _process_timeseries_results(self, df: pd.DataFrame) -> pd.DataFrame:
        first_column = df.columns.values.tolist()[0]
        if first_column == "FORECAST_POINT":
            renamer = {
                "FORECAST_POINT": "forecastPoint",
                "FORECAST_DISTANCE": "forecastDistance",
                self.model_kind.timestampCol: "timestamp",
            }
            df = df.rename(columns=renamer).assign(seriesId=None)
        else:
            renamer = {
                "FORECAST_POINT": "forecastPoint",
                "FORECAST_DISTANCE": "forecastDistance",
                self.model_kind.timestampCol: "timestamp",
                first_column: "seriesId"  # ok I know this seems really hacky but from what
                # I can tell this is always true and there is no route that provides the series id
            }
            df = df.rename(columns=renamer)
        return df

    def _process_clustering_results(self, df: pd.DataFrame) -> pd.DataFrame:
        renamer = {
            old_col: PredictionFormatter._standardize_clustering_label(old_col)
            for old_col in self.all_prediction_columns
        }
        df = df.rename(columns=renamer)
        self.all_prediction_columns = [value for _, value in renamer.items()]
        if self.class_probabilities:
            df = df.drop("prediction", axis=1)
        else:
            df = df.drop(self.all_prediction_columns, axis=1)
        return df

    def _process_anomaly_detection_results(self, df: pd.DataFrame) -> pd.DataFrame:
        df["prediction"] = (df["ANOMALY_SCORE"] > 0.5).replace({True: "Anomalous", False: "Normal"})
        df = df.rename(columns={"ANOMALY_SCORE": "anomaly_score"})
        df = df.drop("Anomaly", axis=1, errors="ignore")
        if not self.class_probabilities:
            df.drop("anomaly_score", axis=1, errors="ignore", inplace=True)
        else:
            df = df.assign(
                class_Anomalous=lambda df: df["anomaly_score"],
                class_Normal=lambda df: 1 - df["anomaly_score"],
            ).drop("anomaly_score", axis=1)
        if self.class_probabilities:
            df = df.drop("prediction", axis=1)
        return df

    def _process_batch_explanations(self, df: pd.DataFrame) -> pd.DataFrame:
        expl_columns = [col for col in df.columns if "EXPLANATION" in col]

        renamer = {
            old_col: PredictionFormatter._standardize_explanation_label(old_col)
            for old_col in expl_columns
        }
        df = df.rename(columns=renamer)
        return df

    @staticmethod
    def _standardize_clustering_label(column_label: str) -> str:
        """Batch Predictions returns "Cluster 2_PREDICTION" but we want "class_Cluster 2" for consistency.


        Args:
            column_label (str): _description_

        Returns:
            str: New coumn name
        """
        return f"class_{column_label.replace('_PREDICTION', '')}"

    @staticmethod
    def _standardize_prediction_label(incol: str, column_label: str) -> str:
        """Standardize class prediction column names

        Batch predictions have a funny way of naming columns in Multiclass models.
        Say you are predicting the weather, the column names will be:

        - Weather_Rain_PREDICTION
        - Weather_Snow_PREDICTION
        - Weather_SUN_PREDICTION

        This function converts that format to be:

        - Weather_Rain_PREDICTION -> class_Rain_prediction
        - Weather_Snow_PREDICTION -> class_Snow_prediction
        - Weather_SUN_PREDICTION -> class_SUN_prediction

        This function illustrates why this is needed so badly. To infer the class names from the results
        of batch prediction, you need to REGEX with the target name to extract the middle value.
        a data scientist using DRX would only need to do:

        ```
        >>> prediction = 'class_Rain_prediction'
        >>> class_name = prediction[6:len(prediction)- 11
        >>> print(class_name)
        Rain
        ```

        Parameters
        ----------
        incol : str
            The target column this will be used to shape the new column name
        column_label : str)
            The column name being converted

        Returns
        -------
        str
            The new column name
        """
        m = re.match(re.escape(incol + "_"), column_label)
        s = re.search(re.escape("_PREDICTION"), column_label)
        if s:
            return f"class_{column_label[m.end(): s.start()]}"  # type: ignore[union-attr]
        else:
            return column_label

    @staticmethod
    def _standardize_explanation_label(column_label: str) -> str:
        """Standardize explanation column names

        Batch predictions have a funny way of returning columns with the prediction
        explanation value and information. Consider a model that is predicting the weather (sunny, rainy, or snowy):

        - Weather_EXPLANATION_1_STRENGTH
        - Weather_EXPLANATION_1_ACTUAL_VALUE
        - Weather_EXPLANATION_1_QUALITATIVE_STRENGTH

        Note that binary proejcts don't prepend the target name to the front:

        This function converts that format to be:

        - Weather_EXPLANATION_1_STRENGTH -> explanation_1_strength

        Parameters
        ----------
        column_label : str
            The column name being converted

        Returns
        -------
        str
            The new column name
        """

        s = re.search(re.escape("EXPLANATION"), column_label)
        if s:
            if s.start() == 0:
                return column_label.lower()
            else:
                return f"{column_label[s.start():len(column_label)]}".lower()
        else:
            return column_label


@dataclass
class ModelKind:
    """Capabilities of a deployed DataRobot model

    See https://app.datarobot.com/docs/api/reference/public-api/models.html#properties_103
    """

    isAnomalyDetectionModel: bool = False
    isCombinedModel: bool = False
    isDecisionFlow: bool = False
    isFeatureDiscovery: bool = False
    isMultiseries: bool = False
    isTimeSeries: bool = False
    isUnsupervisedLearning: bool = False
    isClustering: bool = False
    isMultilabel: bool = False
    isMultiClass: bool = False
    isRegression: bool = False
    isBinary: bool = False
    seriesId: Optional[str] = None
    timestampCol: Optional[str] = None
    targetName: Optional[str] = None
    projectId: Optional[str] = None

    @staticmethod
    def infer_model_kind(
        settings_json: Dict[str, Any], deployment_json: Dict[str, Any]
    ) -> ModelKind:
        """
        Infer DataRobot deployed model capabilities

        Uses response from
          - GET /deployments/{did}/
          - GET /deployments/{did}/settings/

        Parameters
        ----------
        settings_json : dict
            HTTP response from GET /deployments/{did}/settings/
        deploymnet_json : dict
            HTTP response from GET /deployments/{did}/

        Returns
        -------
        ModelKind
            Data structure with deployment capabilities

        Notes
        -----
        Due to limitations of the API, returned predictions may also need to be
        inspected to correctly infer all capabilities. See
        `confirm_model_kind_from_results`

        """
        projectId = deployment_json["model"]["projectId"]
        isAnomalyDetectionModel = False
        isCombinedModel = False
        isDecisionFlow = False
        isFeatureDiscovery = False
        isMultiseries = False
        isTimeSeries = False
        isUnsupervisedLearning = deployment_json["model"]["unsupervisedMode"]
        isMultilabel = False
        isClustering = False
        isMultiClass = False
        isBinary = False
        timestampCol = None
        isRegression = False
        if deployment_json["model"]["targetType"] == "Multilabel":
            isMultilabel = True
        if deployment_json["model"]["targetType"] == "Regression":
            isRegression = True
        targetName = deployment_json["model"].get("targetName", None)
        # Are we anomalous? Due to Datarobot API error the unsupervisedType can't be relied on
        # we are leaving this code here so that you know we tried it and hope that one day
        # VIZAI-4050 can be properly fixed see slack https://datarobot.slack.com/archives/C019E6X2WMU/p1671724949085819
        # if isUnsupervisedLearning:
        #     if deployment_json['model']['unsupervisedType'] == 'anomaly': Unsupervised type not available
        #         isAnomalyDetectionModel = True
        #     else:
        #         isClustering = True

        # are we using decision flow?
        isDecisionFlow = deployment_json["model"].get("hasDecisionFlow", False)
        # are we using feature discovery?
        isFeatureDiscovery = deployment_json["capabilities"]["supportsSecondaryDatasets"]
        # are we a time series model
        if settings_json["predictionsByForecastDate"]["columnName"]:
            isTimeSeries = True
            timestampCol = settings_json["predictionsByForecastDate"]["columnName"]
            # there is no current way to find the seriesID
        # are we multilable?
        if deployment_json["model"]["targetType"] == "Multiclass":
            if deployment_json["model"]["targetName"] is not None:
                isMultiClass = True
            else:
                isClustering = True
        else:
            isMultiClass = False
        # are we binary?
        if deployment_json["model"]["targetType"] == "Binary":
            isBinary = True

        return ModelKind(
            projectId=projectId,
            isAnomalyDetectionModel=isAnomalyDetectionModel,
            isCombinedModel=isCombinedModel,
            isDecisionFlow=isDecisionFlow,
            isFeatureDiscovery=isFeatureDiscovery,
            isMultiseries=isMultiseries,
            isMultilabel=isMultilabel,
            isTimeSeries=isTimeSeries,
            isClustering=isClustering,
            isUnsupervisedLearning=isUnsupervisedLearning,
            isMultiClass=isMultiClass,
            isBinary=isBinary,
            timestampCol=timestampCol,
            targetName=targetName,
            isRegression=isRegression,
        )

    def confirm_model_kind_from_results(
        self,
        df_results: pd.DataFrame = None,
        json_results: Optional[Dict[str, Any]] = None,
    ) -> ModelKind:
        """
        Update ModelKind based on returned predictions

        ModelKind objects are generated from data received from the `deployment` and
        `deploymentSettings` routes. Unfortunately, the information in these responses
        is not sufficient to infer all capabilities. This function takes returned
        batch or real time predictions and updates a few capabilities, specifically:

            - Whether a deployment is anomaly detection
            - `seriesId` of time series models

        Parameters
        ----------
        df_results : pd.DataFrame, optional
            Predictions returned from a completed batch prediction job
            (as a DataFrame).
        json_results : dict, optional
            Predictions returned from requesting RT predictions
            (JSON response body).

        Returns
        -------
        self : ModelKind
            Updated model capabilities (mutated in place)
        """
        if df_results is not None:
            if "ANOMALY_SCORE" in df_results.columns:
                self.isAnomalyDetectionModel = True
        if json_results is not None:
            if (
                len(json_results["data"][0]["predictionValues"]) == 1
                and json_results["data"][0]["predictionValues"][0]["label"] == "Anomaly Score"
            ):
                self.isAnomalyDetectionModel = True
        if self.isTimeSeries:
            if df_results is not None:
                if self.timestampCol is not None:
                    if "(actual)" in self.timestampCol:
                        # DataRobot transforms the datetime column and creates a new
                        # column with the "(actual)" suffix. Therefore, to identify
                        # the timestamp used in time series predictions we will find
                        # the column based on position. DataRobot returns in the
                        # following format:
                        #
                        # SERIES_ID | FORECAST_POINT | TIMESTAMP_COL
                        # or for single series
                        # FORECAST_POINT | TIMESTAMP_COL
                        if df_results.columns[0] == "FORECAST_POINT":
                            self.timestampCol = str(df_results.columns[1])
                        else:
                            self.timestampCol = str(df_results.columns[2])
        return self


@dataclass
class DeploymentInfo:
    model_kind: ModelKind
    dr_key: str
    endpoint: str
