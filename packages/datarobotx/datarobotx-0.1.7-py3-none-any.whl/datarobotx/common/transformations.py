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
from typing import List, Optional

import pandas as pd

logger = logging.getLogger("drx")


def melt_explanations(df: pd.DataFrame, id_vars: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Melts Dataframe of explanations into long form columns

    Parameters
    ----------
    df : pd.DataFrame
        A dataframe with prediction explanations. Assumes
        explanations in wide form, with at least one of:
        [feature_name, actual_value, strength, qualitative_strength]
        for each prediction
    id_vars: list, default=[]
        List of columns to keep in long form dataframe
    """
    if id_vars is None:
        id_vars = []

    def create_melted_data_frame(df: pd.DataFrame, melt_string: str) -> pd.DataFrame:
        value_name = melt_string[16:]
        df_melted = (
            pd.melt(
                df,
                id_vars=(["row_id"] + id_vars) if id_vars else ["row_id"],
                value_vars=df.filter(regex=melt_string).columns,
                var_name="explanation",
                value_name=value_name,
            )
            .assign(
                explanation_number=lambda x: x.explanation.str.extract(r"(\d+)").astype("int64")
            )
            .drop(columns="explanation")
        )
        assert len(df_melted) > 0
        return df_melted

    df = df.copy().assign(row_id=df.index)
    regex_strings = [
        r"explanation_\d+_feature_name",
        r"explanation_\d+_actual_value",
        r"explanation_\d+_strength",
        r"explanation_\d+_qualitative_strength",
    ]

    init = False
    for string in regex_strings:
        if not init:
            try:
                df_melt = create_melted_data_frame(df, string)
                init = True
            except AssertionError:
                logger.warning("Columns for explanation %s not found", string[16:])
        else:
            try:
                df_temp = create_melted_data_frame(df, string).drop(columns=id_vars)
                df_melt = df_melt.merge(df_temp, on=["row_id", "explanation_number"], how="left")
            except AssertionError:
                logger.warning("Columns for explanation %s not found", string[16:])
    return (
        # Pylint false positive due to: https://github.com/PyCQA/astroid/issues/1818
        df_melt.loc[
            lambda x: (~pd.isna(x.feature_name))  # pylint: disable=E1130
            | (x.explanation_number == 1)
        ]
        .sort_values(by=["row_id", "explanation_number"])
        .reset_index(drop=True)[
            ["row_id", "explanation_number"]
            + id_vars
            + [i for i in df_melt.columns if i not in ["row_id", "explanation_number"] + id_vars]
        ]
    )


def featurize_explanations(X: pd.DataFrame) -> pd.DataFrame:
    """
    Featurizes a dataframe of explanations into strength values by feature.

    Utility to melt and pivot prediction explanations so that each column
    corresponds to a feature and each value to an explanation strength.

    Parameters
    ----------
    df : pd.DataFrame
        A dataframe with prediction explanations. Assumes dataframe
        has its explanations in wide form, with at least one of:
        [feature_name, actual_value, strength, qualitative_strength]
        for each prediction

    Returns
    -------
    pd.DataFrame
        A dataframe of explanation strengths for each feature
    """
    melted_df = melt_explanations(X)
    pivot_df = pd.pivot(
        melted_df, index="row_id", columns="feature_name", values="strength"
    ).fillna(0)
    pivot_df = pivot_df[[i for i in pivot_df.columns if not pd.isna(i)]]
    pivot_df.columns = pivot_df.columns.to_list()
    return pivot_df.reset_index(drop=True)
