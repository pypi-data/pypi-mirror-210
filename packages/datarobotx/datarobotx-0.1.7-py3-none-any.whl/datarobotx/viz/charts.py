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
from typing import Any, Dict

import altair as alt
import pandas as pd

import datarobotx.client.projects as proj_client
from datarobotx.common import utils


def render_feature_impact_chart(fi_json: Dict[str, Any]) -> alt.Chart:
    """Render altair feature impact chart"""
    feature_impact = pd.DataFrame(fi_json["featureImpacts"])
    if feature_impact.shape[0] > 10:
        feature_impact = feature_impact.head(10)
    if "impact_normalized" in feature_impact.columns:
        normal_col = "impact_normalized"
        feature_col = "feature_name"
    else:
        normal_col = "impactNormalized"
        feature_col = "featureName"
    chart: alt.Chart = (
        alt.Chart(feature_impact, width=400, title="Feature Impact Chart")
        .mark_bar()
        .encode(x=alt.X(f"{normal_col}:Q"), y=alt.Y(f"{feature_col}:N", sort="-x"))
    )
    return chart


def feature_impact_chart(project_id: str, model_id: str) -> alt.Chart:
    """Retrieve feature impact data and render altair chart"""
    fi_json = utils.create_task_new_thread(
        proj_client.get_feature_impact(model_id=model_id, pid=project_id), wait=True
    ).result()
    return render_feature_impact_chart(fi_json)


def render_roc_curve_chart(roc_json: Dict[str, Any]) -> alt.Chart:
    """Render altair roc curve"""
    roc_chart_data = pd.DataFrame(roc_json["data"][0]["rocPoints"])
    base_chart = (
        alt.Chart(roc_chart_data, title="ROC Curve", width=400)
        .mark_line()
        .encode(
            x=alt.X("falsePositiveScore:Q", title="False Positive Rate"),
            y=alt.Y("truePositiveScore:Q", title="True Positive Rate"),
        )
    )
    line_data = pd.DataFrame(
        [roc_chart_data.min(), roc_chart_data.max()],
        columns=["falsePositiveScore", "truePositiveScore"],
    )
    line_chart = (
        alt.Chart(line_data)
        .mark_line(color="grey", strokeDash=[6, 4])
        .encode(x="falsePositiveScore:Q", y="truePositiveScore:Q")
    )
    return base_chart + line_chart


def roc_curve_chart(project_id: str, model_id: str, ds_id: str) -> alt.Chart:
    """Retrieve roc data for external prediction data and render altair chart"""
    roc_json = utils.create_task_new_thread(
        proj_client.get_roc_data(project_id, model_id, ds_id), wait=True
    ).result()
    return render_roc_curve_chart(roc_json)


def render_lift_chart(lift_json: Dict[str, Any]) -> alt.Chart:
    """Render altair lift chart"""
    lift_chart_data = pd.DataFrame(lift_json["data"][0]["bins"])
    lift_chart_data = (
        lift_chart_data.reset_index()
        .assign(Bin=lambda df: df["index"] + 1)
        .drop(columns="index")
        .melt(id_vars=["Bin", "binWeight"])
        .sort_values(by="Bin")
    )
    chart = (
        alt.Chart(lift_chart_data.reset_index(), title="Lift Chart", width=400)
        .mark_line()
        .encode(
            x=alt.X("Bin:Q"),
            y=alt.Y("value:Q", title="Average Target Value"),
            color=alt.Color("variable:N", title="Predictions"),
            tooltip=["binWeight"],
        )
    )
    return chart


def lift_chart(project_id: str, model_id: str, ds_id: str) -> alt.Chart:
    """Retrieve lift chart data for external prediction data and render altair chart"""
    lift_json = utils.create_task_new_thread(
        proj_client.get_liftchart_data(project_id, model_id, ds_id), wait=True
    ).result()
    return render_lift_chart(lift_json)


def render_residuals_chart(residuals_json: Dict[str, Any]) -> alt.Chart:
    """Render residuals altair chart"""
    residuals_data = pd.DataFrame(
        residuals_json["data"][0]["data"],
        columns=["Actual", "Predicted", "Residual", "Row Number"],
    )
    chart = (
        alt.Chart(residuals_data, title="Residuals Chart", width=500, height=500)
        .mark_point()
        .encode(x=alt.X("Predicted:Q"), y=alt.Y("Actual:Q"), tooltip=["Residual"])
    )
    line_data = pd.DataFrame(
        [[0, 0, 0, 0], residuals_data.max().values.tolist()],
        columns=["Actual", "Predicted", "Residual", "Row Number"],
    )
    line_chart = (
        alt.Chart(line_data, width=400)
        .mark_line(color="grey", strokeDash=[6, 4], strokeOpacity=0.6)
        .encode(x=alt.X("Predicted:Q"), y=alt.Y("Actual:Q"))
    )
    return chart + line_chart


def residuals_chart(project_id: str, model_id: str, ds_id: str) -> alt.Chart:
    """Retrieve residuals data for external prediction data and render altair chart"""
    residuals_json = utils.create_task_new_thread(
        proj_client.get_residuals_data(project_id, model_id, ds_id), wait=True
    ).result()
    return render_residuals_chart(residuals_json)
