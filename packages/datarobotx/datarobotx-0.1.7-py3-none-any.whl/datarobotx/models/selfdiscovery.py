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

from functools import partial
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from datarobotx import Deployment
import datarobotx.client.datasets as datasets_client
from datarobotx.common import utils
from datarobotx.common.utils import FutureDataFrame
from datarobotx.models.autopilot import AutopilotModel
from datarobotx.models.featurediscovery import FeatureDiscoveryModel, Relationship
from datarobotx.models.intraproject import IntraProjectModel
from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


class SelfDiscoveryModel(IntraProjectModel):
    """
    Self-join feature discovery orchestrator

    Partitions a single training dataset into two datasets that will be joined by DR
    feature discovery using the provided join keys. This allows feature discovery
    to synthetically create and explore feature aggregations and transformations on a
    single training dataset.

    For OTV problems, the primary dataset includes the target variable, the
    user provided join keys and the date feature. For non-OTV problems, all original
    features are also included in the primary dataset.

    The secondary dataset includes the join keys, the date feature (if applicable)
    and all non-target features. The secondary dataset will be automatically created
    as a new AI catalog entry.

    Autopilot orchestration is delegated to the provided base model.

    Parameters
    ----------
    base_model: AutopilotModel or IntraProjectModel
        Base model for orchestrating Autopilot after feature discovery. Clustering
        and AutoTS are not supported.
    feature_windows: tuple or list of tuple, optional
        Only applicable for OTV problems. A tuple with the following three elements
        to govern feature discovery: (start, end, unit)
        start: int how far back to look to aggregate features
        end: int stopping point for aggregation.
        unit: str unit of time to use for aggregation e.g.
        ('MILLISECOND', 'SECOND', 'MINUTE', 'HOUR', 'DAY', 'WEEK','MONTH','QUARTER', 'YEAR')

        Example: (-14, -7, 'DAY') will created aggregated features from 14 days ago
        until 7 days ago

        Can also be provided as a list of multiple feature discovery window tuples.
    """

    def __init__(
        self,
        base_model: Union[AutopilotModel, IntraProjectModel],
        feature_windows: Union[Tuple[int, int, str], List[Tuple[int, int, str]], None] = None,
    ):
        super().__init__(base_model, feature_windows=feature_windows)

    def _update_root_model(self, **kwargs: Any) -> None:
        """Hook for updating parameters on innermost model

        Process feature_windows settings, ensure SAFER is activated
        """
        params = {}
        if "feature_windows" in kwargs and kwargs.get("feature_windows") is not None:
            params["cv_method"] = "datetime"
        self._set_params_root(**params)

    def fit(
        self,
        X: Union[pd.DataFrame, str],
        *args: Any,
        keys: Union[str, List[str]],
        kia_features: Optional[List[str]] = None,
        datetime_partition_column: Optional[str] = None,
        **kwargs: Any,
    ) -> SelfDiscoveryModel:
        """
        Fit self-join feature discovery model

        AutoTS and Clustering base models are not supported for feature
        discovery.

        Parameters
        ----------
        X : pandas.DataFrame
            Training dataset for challenger models
        *args
            Positional arguments to be passed to the base model fit()
        keys : str or list[str]
            Column name(s) of the feature(s) to be used for the self-join.
            Can be a scalar string or a list of strings.
        kia_features : list, optional
            A list of features that will be included in the primary dataset of
            the feature discovery model. These will be treated as primary
            features and excluded feature discovery engineering.
        datetime_partition_column: str, optional
            Column name of the feature to be used as the temporal key for
            creating a lookback window for feature discovery.
        **kwargs :
            Keyword arguments to be passed to the base model fit()
        """
        utils.create_task_new_thread(
            self._fit(
                X,
                *args,
                keys=keys,
                kia_features=kia_features,
                datetime_partition_column=datetime_partition_column,
                **kwargs,
            )
        )
        return self

    @ModelOperator._with_fitting_underway
    async def _fit(
        self,
        X: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Orchestrate creation of self-join datasets + SAFER configuration"""
        self._validate_self_discovery_params(kwargs)
        logger.info("Preparing datasets for self-join", extra={"is_header": True})

        if isinstance(X, str):
            dataset_id = await datasets_client.resolve_dataset_id(X)
            ds_json = await datasets_client.get_dataset(dataset_id)
            X = pd.read_csv(ds_json["uri"])

        keys = kwargs.pop("keys")
        primary_cols = keys.copy() if isinstance(keys, list) else [keys]
        if isinstance(keys, str):
            keys = (keys, keys)
        else:
            keys = [(key, key) for key in keys]

        kia_features = kwargs.pop("kia_features")
        kia_features = kia_features if kia_features is not None else []

        primary_cols += [
            col
            for col in [
                kwargs.get("datetime_partition_column"),
                kwargs.get("target"),
            ]
            if col is not None
        ] + kia_features

        drop_cols = [
            col
            for col in [
                kwargs.get("target"),
            ]
            if col is not None
        ] + kia_features

        await FeatureDiscoveryModel(self.base_model)._fit(  # type: ignore[arg-type]
            X[primary_cols],
            *args,
            champion_handler=partial(
                self._refresh_leaderboard, callback=kwargs.pop("champion_handler", None)
            ),
            relationships_configuration=Relationship(
                X.drop(columns=drop_cols),
                keys=keys,
                temporal_key=kwargs["datetime_partition_column"],
                feature_windows=self._intra_config["feature_windows"],
                dataset_name="DiscoveryFeatures",
            ),
            feature_engineering_prediction_point=kwargs["datetime_partition_column"],
            **kwargs,
        )

        logger.info("Self-join feature discovery complete", extra={"is_header": True})

    def _validate_self_discovery_params(self, kwargs: Dict[str, Any]) -> None:
        """Ensure required parameters are provided for self-join feature discovery"""
        if not kwargs.get("keys", False):
            raise ValueError("Self joining requires a column to be used as a join key")

        root_model_params = self._get_params_root()

        if root_model_params._get("use_time_series", False):
            raise TypeError("Feature discovery cannot be used with DataRobot Time Series")
        if root_model_params._get("unsupervised_type") == "clustering":
            raise TypeError("Feature discovery cannot be used with DataRobot clustering")
        if not kwargs.get("datetime_partition_column", False):
            logger.warning(
                "No datetime partition column provided. Consider partitioning "
                "and evaluating models externally to avoid target leakage across the self-join."
            )
        else:
            self._set_params_root(datetime_partition_column=kwargs["datetime_partition_column"])

    def predict(self, X: Any, *args: Any, **kwargs: Any) -> FutureDataFrame:
        """Predict using the base model"""
        logger.warning("SelfDiscoveryModel only derives features from training dataset")
        return super().predict(X, *args, **kwargs)

    def predict_proba(self, X: Any, *args: Any, **kwargs: Any) -> FutureDataFrame:
        """Predict using the base model"""
        logger.warning("SelfDiscoveryModel only derives features from training dataset")
        return super().predict_proba(X, *args, **kwargs)

    def deploy(
        self, wait_for_autopilot: Optional[bool] = False, name: Optional[str] = None
    ) -> Deployment:
        raise NotImplementedError(
            "Deployments on Self Discovery models not yet "
            + "supported. Consider using a feature discovery model instead."
        )

    def get_derived_features(self) -> FutureDataFrame:
        """
        Feature discovery derived features

        Returns
        -------
        df : FutureDataFrame
            DataFrame containing the derived features from the feature
            discovery process.
        """
        return FeatureDiscoveryModel(self).get_derived_features()

    def get_derived_sql(self) -> str:
        """
        SQL recipes for producing derived features

        Returns
        -------
        str
            String with the SQL code for generating the derived features from
            the feature discovery process. Use with print() for a more readable
            output
        """
        return FeatureDiscoveryModel(self).get_derived_sql()
