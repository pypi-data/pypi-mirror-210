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
from functools import partial
from itertools import chain
import logging
from math import ceil, floor, sqrt
from typing import Any, cast, Dict, Optional, Tuple, Union

import pandas as pd
import pyspark.sql
from pyspark.sql.functions import create_map, lit, when

from datarobotx.client.datasets import post_dataset_from_spark_df
from datarobotx.common import utils
from datarobotx.common.config import context
from datarobotx.models.autopilot import AutopilotModel
from datarobotx.models.intraproject import IntraProjectModel
from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


class SparkIngestModel(IntraProjectModel):
    """
    Train on a Spark dataframe

    Ingests a Spark dataframe into DataRobot for model training, downsampling if needed.

    An AI catalog entry will automatically be created for the ingested data and Autopilot
    will subsequently be orchestrated as normal.

    Parameters
    ----------
    base_model: AutopilotModel or IntraProjectModel
        Base model for orchestrating Autopilot after feature discovery. Clustering
        and AutoTS are not supported.
    dataset_name : str
        Name for the automatically-created AI Catalog entry containing the ingested
        data from Spark
    sampling_strategy : {'uniform', 'most_recent', 'smart', 'smart_zero_inflated'}, default='uniform'
        Downsampling strategy to be used if sampling is needed to meet ingest limit.
        When using smart sampling, training weights will be calculated and stored
        in the column 'dr_sample_weights' and automatically used at fit-time.

        'smart' sampling requires a target variable to be passed at fit-time and
        'most_recent' sampling requires a datetime_partition_column at fit-time.

    Notes
    -----
    'uniform' samples uniformly at random from the provided dataframe

    'most_recent' samples after ordering the data by the 'datetime_partition_column'

    'smart' samples attempting to preserve as many minority target examples as possible

    'smart_zero_inflated' performs smart sampling, but treats all non-zero values
    as the same class
    """

    def __init__(
        self,
        base_model: Union[AutopilotModel, IntraProjectModel],
        dataset_name: Optional[str] = None,
        sampling_strategy: str = "uniform",
    ):
        super().__init__(base_model, dataset_name=dataset_name, sampling_strategy=sampling_strategy)
        if dataset_name is None:
            dataset_name = self._get_params_root()["project_name"]
            self.set_params(dataset_name=dataset_name)

    def fit(self, X: pyspark.sql.DataFrame, *args: Any, **kwargs: Any) -> None:
        """
        Fit model from a Spark dataframe

        Parameters
        ----------
        X : pyspark.sql.DataFrame
            Training dataset to be ingested
        *args
            Positional arguments to be passed to the base model fit()
        **kwargs :
            Keyword arguments to be passed to the base model fit()
        """
        utils.create_task_new_thread(self._fit(X, *args, **kwargs))

    @ModelOperator._with_fitting_underway
    async def _fit(
        self,
        X: Union[pyspark.sql.DataFrame, pd.DataFrame, str],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if not isinstance(X, pyspark.sql.DataFrame):
            raise TypeError(
                "SparkIngestModel requires training data to be of type pyspark.sql.DataFrame"
            )
        logger.info("Ingesting Spark data and running autopilot", extra={"is_header": True})
        sampled_df, max_rows = downsample_spark(
            X,
            sampling_strategy=self._intra_config["sampling_strategy"],
            target=kwargs.get("target"),
            datetime_partition_column=kwargs.get("datetime_partition_column"),
        )
        logger.info("Fitting base model", extra={"is_header": True})
        logger.info("Uploading dataset to AI Catalog...")
        ds_json = await post_dataset_from_spark_df(
            sampled_df,
            self._intra_config["dataset_name"],
            max_rows,
        )
        if "dr_sample_weights" in sampled_df.columns:
            kwargs["weights"] = "dr_sample_weights"
        await self.base_model._fit(
            ds_json["datasetId"],
            *args,
            champion_handler=partial(
                self._refresh_leaderboard, callback=kwargs.pop("champion_handler", None)
            ),
            **kwargs,
        )
        logger.info("Spark run complete", extra={"is_header": True})


def spark_to_ai_catalog(
    spark_df: pyspark.sql.DataFrame, name: str, max_rows: Optional[int] = None
) -> str:
    """Upload Spark dataframe to AI Catalog

    Does not attempt to downsample. Will attempt to use the DataRobot 'uploading of
    data files in stages' feature flag if available to do a multipart upload. HTTP
    uploads of large files can intermittently fail without this feature flag.

    Parameters
    ----------
    spark_df : pyspark.sql.DataFrame
        Spark dataframe to be uploaded to AI catalog
    name : str
        Name for the resulting AI Catalog entry
    max_rows : int, optional
        Maximum number of rows from the dataframe to upload to AI catalog

    Returns
    -------
    dataset_id
        DataRobot dataset id of the resulting catalog entry

    See Also
    --------
    downsample_spark
        Downsample spark dataframes if too large for DataRobot
    """
    future = utils.create_task_new_thread(
        post_dataset_from_spark_df(spark_df, name, max_rows=max_rows), wait=True  # type: ignore[arg-type]
    )
    return cast(str, future.result()["datasetId"])


def downsample_spark(
    spark_df: pyspark.sql.DataFrame,
    sampling_strategy: str = "uniform",
    target: Optional[str] = None,
    datetime_partition_column: Optional[str] = None,
) -> Tuple[pyspark.sql.DataFrame, int]:
    """
    Downsample Spark dataframe for DataRobot

    Row limits are estimated statistically for performance and are not guaranteed to
    precisely match the ingest limit. The private drx.Context() property `_max_dr_ingest`
    specifies the DR ingest limit in bytes that will be used for row limit estimation.

    When using this function standalone, training weights produced by smart sampling
    must be manually passed by the user into downstream model fitting operations.

    Parameters
    ----------
    spark_df : pyspark.sql.DataFrame
        Data to be ingested into DataRobot AI Catalog
    sampling_strategy : {'uniform', 'most_recent', 'smart', 'smart_zero_inflated'}
        Downsampling strategy to be used if sampling is needed to meet ingest limit.
        When using smart sampling, training weights will be calculated and stored
        in the column 'dr_sample_weights'
    target : str, optional
        Target column name; required with smart sampling
    datetime_partition_column : str, optional
        Primary date feature column name; required with most recent sampling

    Returns
    -------
    df : pyspark.sql.DataFrame
        Downsampled dataframe
    max_rows : int
        Max number of rows that should be retained from the dataframe; to avoid
        OOM on the driver, this limit should be enforced by whatever mechanism
        streams the data out of the spark cluster

    Notes
    -----
    'uniform' samples uniformly at random from the provided dataframe

    'most_recent' samples after ordering the data by the 'datetime_partition_column'

    'smart' samples attempting to preserve as many minority target examples as possible

    'smart_zero_inflated' performs smart sampling, but treats all non-zero values
    as the same class

    The resulting dataframe is not directly row limited by Spark because Spark limit()
    collapses to a single partition and can OOM the driver. Instead the limit is
    enforced by the uploading function while iterating over Spark partitions at upload
    time.

    In most cases 'most_recent' is the only form of sampling for which this limit
    needs to be enforced at upload time, however 'uniform' may occasionally
    require row limit enforcement because Spark sample() does not provide row count
    guarantees.
    """
    logger.info("Preparing for DataRobot ingest", extra={"is_header": True})
    logger.info("Estimating row limit for ingest...")
    total_rows = spark_df.count()
    max_rows = estimate_max_sample_rows(
        spark_df, context._max_dr_ingest, with_weights="smart" in sampling_strategy
    )

    upload_df = spark_df
    if max_rows < total_rows:
        if sampling_strategy == "uniform":
            logger.info("Downsampling uniform at random...")
            upload_df = create_uniform_sample(
                spark_df, "total_rows", max_rows, 1.0, total_rows=total_rows
            )
        elif sampling_strategy == "most_recent":
            if datetime_partition_column is None:
                raise ValueError("Most recent sampling requires a datetime_partition_column")
            logger.info("Downsampling preserving most recent records...")
            upload_df = create_most_recent_sample(
                spark_df,
                "total_rows",
                datetime_partition_column,
                max_rows,
                1.0,
                total_rows=total_rows,
            )
        elif "smart" in sampling_strategy:  # 'smart sampling'
            if target is None:
                raise ValueError("Smart sampling requires a target")
            if sampling_strategy == "smart_zero_inflated":
                logger.info(
                    "'Smart' downsampling preserving positive, non-zero records where possible..."
                )
                problem_type = "zero_inflated"
            else:
                logger.info("'Smart' downsampling preserving minority records where possible...")
                problem_type = "classification"

            upload_df = create_smart_sample(
                spark_df,
                "total_rows",
                target,
                # safety factor to ensure row limit will be met (Spark sampleBy() is not precise)
                0.95 * max_rows,
                1.0,
                None,
                problem_type,
            )
        else:
            raise ValueError(
                "Sampling strategy must be one of 'uniform', 'most_recent', "
                + "'smart', 'smart_zero_inflated'"
            )
    else:
        logger.info("Downsampling not required")

    logger.info("Ingest preparation complete", extra={"is_header": True})
    return upload_df, min(max_rows, total_rows)


def create_uniform_sample(
    df: pyspark.sql.DataFrame,
    extent_type: str,
    sample_rows: int,
    sample_pct: float,
    total_rows: Optional[int] = None,
) -> pyspark.sql.DataFrame:
    """
    Creates a uniform random sample of a Spark DataFrame

    :param df: The Spark DataFrame to create a sample of
    :param extent_type: How the sample size is determined (total_rows, percentage, auto)
    :param sample_rows: The number of rows in the sample when using the total_rows extent_type
    :param sample_pct: The percentage of the original dataset size when using the percentage extent_type
    :param total_rows: Optional. If the total number of rows in the dataframe is already known this can be set to
        optimize the sample creation
    """
    if extent_type == "total_rows":
        if total_rows is None:
            total_rows = df.count()
        sample_pct = min(total_rows, sample_rows) / total_rows

    if sample_pct > 1.0:
        raise ValueError("Sample size is larger than the original dataset")

    sample_df = df.sample(withReplacement=False, fraction=sample_pct, seed=1234)

    return sample_df


def create_most_recent_sample(
    df: pyspark.sql.DataFrame,
    extent_type: str,
    column_name: str,
    sample_rows: int,
    sample_pct: float,
    total_rows: Optional[int] = None,
) -> pyspark.sql.DataFrame:
    """
    Creates a sample from the most recent rows in a Spark DataFrame

    :param df: The Spark DataFrame to create a sample of
    :param extent_type: How the sample size is determined (total_rows, percentage, auto)
    :param column_name: Name of the column in the DataFrame to use to determine the most recent rows (sorts by
        descending order)
    :param sample_rows: The number of rows in the sample when using the total_rows extent_type
    :param sample_pct: The percentage of the original dataset size when using the percentage extent_type
    :param total_rows: Optional. If the total number of rows in the DataFrame is already known this can be set to
        optimize the sample creation
    """

    if extent_type == "percentage":
        if total_rows is None:
            total_rows = df.count()
        sample_rows = ceil(total_rows * sample_pct)

    if total_rows is not None and sample_rows > total_rows:
        raise ValueError("Sample size is larger than the original dataset")

    return df.orderBy(column_name, ascending=False)


def estimate_max_sample_rows(
    df: pyspark.sql.DataFrame, max_file_size: int, with_weights: Optional[bool] = False
) -> int:
    """Estimates the max number of rows to sample and stay under max_file_size

    This calculation uses the central limit theorem for sample sums which defines the mean and
    the standard deviation of the sample distribution for a given sample size (n)

    The mean of the sample distribution is: original_mean * n
    The standard deviation of the sample distribution is: original_stddev * sqrt(n)

    Using these definitions, we solve the following equation for n:
        max_file_size = (original_mean * n) + (3 * (original_stddev * sqrt(n)))

    This gives us a sample size such that the max_file_size is 3 standard deviations away from
    the mean in the sample distribution.

    This means that there's a roughly 99.7% chance that the size of the sample that is taken
    is less than max_file_size.

    Reference:
    https://openstax.org/books/introductory-statistics/pages/7-2-the-central-limit-theorem-for-sums
    """

    # Add an extra two bytes for the new line + line feed (excel csv dialect)
    if with_weights:
        row_sizes = (
            df.fillna("")
            .withColumn("dr_sample_weights", lit(1.1234567890123456))
            .selectExpr("octet_length(concat_ws(',', *)) + 2 as bytes")
        )
    else:
        row_sizes = df.fillna("").selectExpr("octet_length(concat_ws(',', *)) + 2 as bytes")
    row_stats = row_sizes.selectExpr("mean(bytes) as mean", "stddev(bytes) as stddev").collect()[0]

    mean = row_stats.mean
    stddev = row_stats.stddev

    max_sample_rows = (
        2 * max_file_size * mean
        + 9 * stddev**2
        - 3 * stddev * sqrt(4 * max_file_size * mean + 9 * stddev**2)
    ) / (2 * mean**2)

    return cast(int, floor(max_sample_rows))


def create_smart_sample(
    df: pyspark.sql.DataFrame,
    extent_type: str,
    column_name: str,
    sample_rows: float,
    sample_pct: float,
    weights_col_name: Optional[str],
    problem_type: str,
) -> pyspark.sql.DataFrame:
    """
    Creates a sample of a Spark DataFrame by using our smart downsampling approach

    Smart downsampling is a form of stratified sampling that can be used for classification or zero inflated regression
        problems.

    For classification problems we preserve as much of the minority class(es) as possible. For zero inflated regression
    problems we downsample rows that equal zero in the target column. A weights column is added in the final dataset
    that indicates how much the target column for each row was downsampled from the original dataset. This must be used
    when modeling with the sampled dataset.

    :param df: The Spark DataFrame to create a sample of
    :param extent_type: How the sample size is determined (total_rows, percentage, auto)
    :param column_name: Name of the target column in the DataFrame to use for smart downsampling
    :param sample_rows: The number of rows in the sample when using the total_rows extent_type
    :param sample_pct: The percentage of the original dataset size when using the percentage extent_type
    :param weights_col_name: The name of an optional weights column in the dataset to use when calculating the final
        weights in the sampled dataset
    :param problem_type: The type of data science problem this sample is being prepared for (classification or
        zero_inflated)
    """

    if problem_type == "zero_inflated":
        df = df.withColumn(
            "_tmp_class_name",
            when(df[column_name] == 0, 0).when(df[column_name] > 0, 1).otherwise(-1),
        )
        sample_column_name = "_tmp_class_name"
    elif problem_type == "classification":
        sample_column_name = column_name

    class_count_df = (
        df.groupBy(sample_column_name)
        .count()
        .orderBy("count", ascending=True)
        .withColumnRenamed(sample_column_name, "class_name")
        .toPandas()
    )
    class_count_df = class_count_df.set_index("class_name")

    if problem_type == "zero_inflated":
        if -1 in class_count_df.index.values:
            raise ValueError(
                "Sample column cannot contain negative values for zero inflated regression"
            )

        if 0 not in class_count_df.index.values:
            raise ValueError("Target column must contain zeros for zero inflated regression")

        pct_zero = float(class_count_df.loc[0] / class_count_df["count"].sum())
        if pct_zero < 0.5:
            raise ValueError(
                "Zero inflated regression requires at least 50 percent of the sample column to be 0"
            )

    total_rows = class_count_df["count"].sum()
    if extent_type == "percentage":
        sample_rows = ceil(total_rows * sample_pct)

    target_sample_counts = _calculate_smart_sample_counts(class_count_df, sample_rows)

    class_count_df["target_sample_counts"] = pd.Series(target_sample_counts)
    sample_fractions = (class_count_df["target_sample_counts"] / class_count_df["count"]).to_dict()

    sample_df = df.sampleBy(sample_column_name, fractions=sample_fractions, seed=1234)

    # df.sampleBy is not guaranteed to provide exactly the fraction specified
    # so we calculate the weights by getting the exact count of each class in the final sample
    actual_sample_counts_df = (
        sample_df.groupBy(sample_column_name)
        .count()
        .orderBy("count", ascending=True)
        .withColumnRenamed(sample_column_name, "class_name")
        .toPandas()
    )
    actual_sample_counts_df = actual_sample_counts_df.set_index("class_name")
    actual_total_rows = actual_sample_counts_df["count"].sum()
    if actual_total_rows > total_rows:
        raise RuntimeError(
            "Smart sampling algorithm was unable to produce a "
            + "dataset meeting the provided row limits"
        )
    actual_sample_counts = actual_sample_counts_df["count"].to_dict()

    weights = _calculate_smart_sample_weights(class_count_df, actual_sample_counts)

    weights_map = create_map([lit(x) for x in chain(*weights.items())])
    if weights_col_name and weights_col_name in sample_df.columns:
        sample_df = sample_df.withColumn(
            "dr_sample_weights",
            sample_df[weights_col_name] * weights_map[sample_df[sample_column_name]],
        )
    else:
        sample_df = sample_df.withColumn(
            "dr_sample_weights", weights_map[sample_df[sample_column_name]]
        )

    if problem_type == "zero_inflated":
        sample_df = sample_df.drop("_tmp_class_name")

    return sample_df


def _calculate_smart_sample_counts(df: pd.DataFrame, sample_rows: float) -> Dict[str, Any]:
    classes = df.index.to_list()
    sample_counts = {}

    df = df.sort_values(by="count")
    for row in df.itertuples():
        if sample_rows > row.count * len(classes):
            sample_counts[row.Index] = row.count
            sample_rows -= row.count
            classes.remove(row.Index)
        else:
            break

    remaining_budget = floor(sample_rows / len(classes))
    for class_name in classes:
        sample_counts[class_name] = remaining_budget

    return sample_counts


def _calculate_smart_sample_weights(
    class_count_df: pd.DataFrame, sample_counts: Dict[str, Any]
) -> Dict[str, Any]:
    class_count_df = class_count_df.sort_values(by="count")

    return cast(Dict[str, Any], (class_count_df["count"] / pd.Series(sample_counts)).to_dict())
