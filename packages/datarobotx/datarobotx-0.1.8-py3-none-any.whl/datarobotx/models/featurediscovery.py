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
from dataclasses import dataclass, field
import datetime
from functools import partial
import logging
from typing import Any, cast, Dict, List, Optional, Tuple, Union

import pandas as pd

import datarobotx.client.datasets as datasets_client
import datarobotx.client.projects as proj_client
from datarobotx.common import utils
from datarobotx.common.utils import FutureDataFrame
from datarobotx.models.autopilot import AutopilotModel
from datarobotx.models.intraproject import IntraProjectModel
from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


# Settings for features to generate. Default values are set so that
# the generated SparkSQL does not generate UDFs
_SSQL_SETTINGS = [
    {"name": "enable_days_from_prediction_point", "value": True},
    {"name": "enable_hour", "value": True},
    {"name": "enable_categorical_num_unique", "value": True},
    {"name": "enable_categorical_statistics", "value": False},
    {"name": "enable_numeric_minimum", "value": True},
    {"name": "enable_token_counts", "value": False},
    {"name": "enable_latest_value", "value": True},
    {"name": "enable_numeric_standard_deviation", "value": True},
    {"name": "enable_numeric_skewness", "value": False},
    {"name": "enable_day_of_week", "value": True},
    {"name": "enable_entropy", "value": False},
    {"name": "enable_numeric_median", "value": True},
    {"name": "enable_word_count", "value": False},
    {"name": "enable_pairwise_time_difference", "value": True},
    {"name": "enable_days_since_previous_event", "value": True},
    {"name": "enable_numeric_maximum", "value": True},
    {"name": "enable_numeric_kurtosis", "value": False},
    {"name": "enable_most_frequent", "value": False},
    {"name": "enable_day", "value": True},
    {"name": "enable_numeric_average", "value": True},
    {"name": "enable_summarized_counts", "value": False},
    {"name": "enable_missing_count", "value": True},
    {"name": "enable_record_count", "value": True},
    {"name": "enable_numeric_sum", "value": True},
]


class FeatureDiscoveryModel(IntraProjectModel):
    """
    Feature discovery orchestrator

    Autopilot orchestration is delegated to the provided base model.

    Builds features on secondary datasets before running an autopilot model.
    Primary and secondary datasets can be provided as pandas dataframes or AI
    catalog entries. Users can also provide a relationship configuration id built
    using the Python SDK.

    Parameters
    ----------
    base_model : AutopilotModel or IntraProjectModel
        Base model for orchestrating Autopilot after feature discovery. Clustering
        and AutoTS are not supported.
    remove_udfs : bool
        Whether feature discovery should forego deriving features using UDFs


    Examples
    --------

    >>> import datarobotx as drx
    >>> df_target = pd.read_csv(
    "https://s3.amazonaws.com/datarobot_public_datasets/drx/Lending+Club+Target.csv"
    )
    >>> df_transactions = pd.read_csv(
    "https://s3.amazonaws.com/datarobot_public_datasets/drx/Lending+Club+Transactions.csv"
    )
    >>> base_model = drx.AutoMLModel()
    >>> model = drx.FeatureDiscoveryModel(base_model)
    >>> transaction_relationship = drx.Relationship(
        df_transactions,
        keys="CustomerID",
        temporal_key="Date"
        feature_windows=[(-14, -7, "DAY"), (-7, 0, "DAY")],
        dataset_name="transactions"
    )
    >>> model.fit(
        df_target,
        target="BadLoan",
        feature_engineering_prediction_point="Date",
        relationships_configuration=[transaction_relationship]
        )
    """

    def __init__(
        self,
        base_model: Union[AutopilotModel, IntraProjectModel],
        remove_udfs: bool = False,
    ):
        super().__init__(base_model, remove_udfs=remove_udfs)

    def _update_root_model(self, **kwargs: Any) -> None:
        """
        Hook for updating parameters on innermost model
        Ensures SAFER is activated
        """
        params = {"autopilot_with_feature_discovery": True}
        self._set_params_root(**params)

    def fit(
        self,
        X: Union[pd.DataFrame, str],
        relationships_configuration: Union[str, Relationship, List[Relationship]],
        *args: Any,
        target: Optional[str] = None,
        feature_engineering_prediction_point: Optional[str] = None,
        **kwargs: Any,
    ) -> FeatureDiscoveryModel:
        """
        Fit a feature discovery model

        Applies automatic feature engineering and feature selection to the
        dataset before running the base model. Note that AutoTS and Clustering
        base models are not supported for feature discovery.

        Parameters
        ----------
        X : pandas.DataFrame or str
            Training dataset for challenger models
        relationships_configuration: Union[str, Relationship, List[Relationship]]
            Secondary dataset(s) relationship configuration. For more complex relationships,
            users can instead pass the relationship configuration id of a relationship
            configured using the official DR python client
        *args
            Positional arguments to be passed to the base model fit()
        target : str, optional
            Column name from the dataset to be used as the target variable
        feature_engineering_prediction_point: str, optional
            Column name of feature in target dataset to join based on time
            Must be set in order to derive time based features
        **kwargs :
            Keyword arguments to be passed to the base model fit()
        """
        utils.create_task_new_thread(
            self._fit(
                X,
                *args,
                target=target,
                feature_engineering_prediction_point=feature_engineering_prediction_point,
                relationships_configuration=relationships_configuration,
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
        """
        Orchestrate creation of SAFER configuration before running autopilot
        """
        self._validate_discovery_params(kwargs)

        if not isinstance(kwargs["relationships_configuration"], str):
            logger.info(
                "Posting feature discovery relationships configuration...",
                extra={"is_header": True},
            )
            kwargs["relationships_configuration"] = (
                await datasets_client.post_relationships_configurations(
                    *(
                        await self._prepare_relationships_configurations(
                            kwargs["relationships_configuration"]
                        )
                    ),
                    feature_discovery_settings=self._get_feature_discovery_settings(),
                )
            )["id"]
        kwargs["relationships_configuration_id"] = kwargs.pop("relationships_configuration")

        logger.info("Running autopilot with feature discovery...", extra={"is_header": True})
        await self.base_model._fit(
            X,
            *args,
            champion_handler=partial(
                self._refresh_leaderboard, callback=kwargs.pop("champion_handler", None)
            ),
            **kwargs,
        )

    @staticmethod
    async def _prepare_relationships_configurations(
        relationships_config: Union[Relationship, List[Relationship]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Prepare relationships configurations for DR, uploading secondary datasets
        """
        if isinstance(relationships_config, Relationship):
            relationships_config = [relationships_config]

        dr_dataset_definitions = list(
            await asyncio.gather(
                *[
                    relationship._get_dr_dataset_definition()
                    for relationship in relationships_config
                ]
            )
        )
        dr_relationships = [
            relationship._get_dr_relationship() for relationship in relationships_config
        ]
        return dr_dataset_definitions, dr_relationships

    def _get_feature_discovery_settings(self) -> List[Dict[str, Any]]:
        """Optionally prevent DR from generating UDFs"""
        if not self._intra_config["remove_udfs"]:
            return [{"name": i["name"], "value": True} for i in _SSQL_SETTINGS]
        else:
            return _SSQL_SETTINGS

    def _validate_discovery_params(self, kwargs: Dict[str, Any]) -> None:
        """
        Validate feature discovery parameters at fit time

        Makes sure the project is not time series or clustering
        """
        root_model_params = self._get_params_root()
        if root_model_params._get("use_time_series", False):
            raise TypeError("Feature discovery cannot be used with DataRobot Time Series")
        if root_model_params._get("unsupervised_type") == "clustering":
            raise TypeError("Feature discovery cannot be used with DataRobot clustering")

        # Make sure relationships configuration is valid if passed in
        relationships_config = kwargs.get("relationships_configuration")
        if relationships_config is not None:
            try:
                if isinstance(relationships_config, list):
                    assert all(isinstance(i, Relationship) for i in relationships_config)
                else:
                    assert isinstance(relationships_config, (Relationship, str))
            except AssertionError:
                raise TypeError(
                    "Relationships configuration must be a Relationship "
                    + "object, list of Relationships, or a string corresponding to a "
                    + "previously configured relationship."
                )
        else:
            raise ValueError(
                "Relationship configuration is required to fit a feature discovery model."
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
        logger.info("Retrieving derived features...", extra={"is_header": True})
        future = utils.create_task_new_thread(
            proj_client.get_derived_features(self._project_id)  # type: ignore[arg-type]
        )
        df = utils.FutureDataFrame(future=future)
        return df

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
        logger.info("Retrieving derived SQL...", extra={"is_header": True})
        return cast(
            str,
            utils.create_task_new_thread(
                proj_client.await_sql_recipes(self._project_id), wait=True  # type: ignore[arg-type]
            ).result(),
        )


@dataclass
class Relationship:
    """
    Secondary dataset relationship definition

    Can be used to configure FeatureDiscoveryModel

    Note that Relationship can only be used for relationships between the primary
    and secondary datasets. The DataRobot SDK should be used to define
    more complex relationships.

    Parameters
    ----------
    X: pd.DataFrame or str
        The primary dataset to use in feature discovery
    keys : str or tuple[str] or list[tuple[str]]
        Column name(s) of the feature(s) to be used for a join
        If a scalar string, key is assumed to be the same in both primary
        and secondary dataset. If a tuple, tuple maps the single join key in
        the primary dataset to the corresponding key in the secondary dataset.
        If a list of tuples, each tuple maps a key in the primary dataset to
        its corresponding key in the secondary dataset.
    temporal_key: str, optional
        The column name to use in a lookback window
    feature_windows : tuple or list[tuple], optional
        A tuple with the following three elements
        to govern feature discovery: (start, end, unit)
        start: int how far back to look to aggregate features
        end: int stopping point for aggregation.
        unit: str unit of time to use for aggregation e.g.
        ('MILLISECOND', 'SECOND', 'MINUTE', 'HOUR', 'DAY', 'WEEK','MONTH','QUARTER', 'YEAR')

        Example: (-14, -7, 'DAY') will created aggregated features from 14 days ago
        until 7 days ago

        Can also be provided as a list of multiple feature discovery window tuples.
    dataset_name : str, optional
        The name of the dataset in feature discovery relationship graph, will be
        automatically generated if omitted.

    """

    X: Union[pd.DataFrame, str]
    keys: Union[str, Tuple[str], List[Tuple[str]]]
    temporal_key: Optional[str] = None
    feature_windows: Optional[Union[Tuple[int, int, str], list[Tuple[int, int, str]]]] = None
    dataset_name: Optional[str] = field(
        default_factory=partial(utils.generate_name, max_len=20, style="underscore")
    )

    def _get_dr_relationship(self) -> Dict[str, Any]:
        """Format relationship as a DR REST API relationship"""
        keys_1, keys_2 = self._resolve_keys()
        dr_relationship = {
            "dataset2Identifier": self.dataset_name,
            "dataset1Keys": keys_1,
            "dataset2Keys": keys_2,
            "featureDerivationWindows": self._resolve_feature_windows(),
        }
        return {k: v for k, v in dr_relationship.items() if v is not None}

    async def _get_dr_dataset_definition(self) -> Dict[str, Any]:
        """Format relationship as a DR REST API dataset definition"""
        ds_json = await self._resolve_secondary_dataset()
        dr_dataset_definition = {
            "catalogId": ds_json["datasetId"],
            "catalogVersionId": ds_json["versionId"],
            "identifier": self.dataset_name,
            "snapshotPolicy": "latest",
            "primaryTemporalKey": self.temporal_key,
        }
        return {k: v for k, v in dr_dataset_definition.items() if v is not None}

    async def _resolve_secondary_dataset(self) -> Dict[str, Any]:
        """Lookup and/or upload a secondary dataset"""
        if isinstance(self.X, str):
            dataset_id = await datasets_client.resolve_dataset_id(self.X)
            return await datasets_client.get_dataset(dataset_id)
        else:
            logger.info("Uploading secondary dataset '%s' to AI Catalog...", self.dataset_name)
            status_url = await datasets_client.post_dataset_from_file(
                utils.prepare_df_upload(
                    self.X,
                ),
                catalog_name=(
                    f"{self.dataset_name} - "
                    + "feature discovery data (Generated {:%Y-%m-%d %H:%M:%S})".format(
                        datetime.datetime.now()
                    )
                ),
            )
            return await datasets_client.await_dataset(status_url, name=self.dataset_name)

    def _resolve_keys(self) -> Tuple[List[str], List[str]]:
        """
        Resolve keys passed in different formats
        to a tuple of two lists of strings
        """
        keys = self.keys
        if isinstance(keys, str):
            return [keys], [keys]
        elif isinstance(keys, tuple):
            keys = [keys]
        assert isinstance(keys, list), "Keys must be a string, tuple or list of tuples"
        key1 = [k[0] for k in keys]
        key2 = [k[1] for k in keys]  # type: ignore[misc]
        return key1, key2

    def _resolve_feature_windows(self) -> List[Dict[str, Any]]:
        """Ensure feature windows are formatted for DR"""
        feature_windows = self.feature_windows
        if feature_windows is not None:
            assert (
                self.temporal_key is not None
            ), "A datetime column must be set if using feature windows"
            if isinstance(feature_windows, tuple):
                feature_windows = [feature_windows]
            feature_windows_out = [
                {"start": window[0], "end": window[1], "unit": window[2]}
                for window in feature_windows
            ]
            return feature_windows_out
        else:
            return [{}]
