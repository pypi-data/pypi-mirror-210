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
from functools import partial
import html
import logging
import random
from typing import Any, cast, Dict, Optional, TYPE_CHECKING, Union

import datarobotx.client.projects as proj_client
from datarobotx.common.config import context
from datarobotx.viz import charts
from datarobotx.viz.viz import drx_viz_theme, jinja_env

if TYPE_CHECKING:
    from datarobotx.models.model import Model

logger = logging.getLogger("drx")


@dataclass
class ModelCardKeyParams:
    project_id: str
    model_id: str
    model_name: str
    project_name: str
    project_metric: str
    metrics: Dict[str, Any]
    model_url: str
    target_type: str
    target_col_name: str


class ModelCardFormatter(logging.Formatter):
    """
    Logging formatter for rendering a model card

    The async coroutine `add_format_context()` should be called before `format()`
    to extend the LogRecord with additional contextual data required
    to render the model card.

    Parameters
    ----------
    attr : str
        The name of the logging record attribute that contains the Model
        object associated with the leaderboard to be rendered.
    as_html : bool
        If true, model card will be formatted as html. Otherwise, will be formatted
        as a Markdown string
    """

    def __init__(self, attr: str, as_html: bool):
        super().__init__()
        self._as_html = as_html
        self._attr = attr

    async def add_format_context(self, record: logging.LogRecord) -> logging.LogRecord:
        """Add the context required for formatting a model card to a logging record"""
        model: Model = getattr(record, self._attr)
        if model._project_id is not None and model._model_id is not None:
            proj_json = await proj_client.get_project(model._project_id)
            external_ds_id = cast(str, getattr(record, "external_ds_id", None))
            coros = [
                proj_client.get_model(model._project_id, model._model_id),
            ]
            if self._as_html:
                coros.append(
                    self.get_dr_chart_data(
                        model._project_id, model._model_id, proj_json, external_ds_id
                    )
                )
            if external_ds_id is not None:
                coros.append(
                    proj_client.get_external_scores(
                        model._project_id, model._model_id, external_ds_id
                    )
                )
            results = await asyncio.gather(*coros)

            record.proj_json = proj_json

            i = 0
            record.model_json = results[i]
            if self._as_html:
                i += 1
                record.chart_jsons = results[i]
            if external_ds_id is not None:
                i += 1
                record.external_ds_id = external_ds_id
                record.external_scores_json = results[i]
        return record

    @staticmethod
    async def get_dr_chart_data(
        project_id: str, model_id: str, proj_json: Dict[str, Any], ds_id: Optional[str] = None
    ) -> dict[str, Dict[str, Any]]:
        """Concurrently retrieve project-appropriate DR chart data"""
        target_type = proj_json["targetType"]
        chart_getters = {
            "Feature Impact": proj_client.get_feature_impact(
                project_id,
                model_id,
                log_calc_with=partial(
                    logger.info,
                    "Calculating feature impact...",
                    extra={"is_header": True},
                ),
            ),
            "ROC Curve": (
                proj_client.get_roc_data(project_id, model_id, ds_id)
                if ds_id is not None and target_type == "Binary"
                else None
            ),
            "Lift Chart": (
                proj_client.get_liftchart_data(project_id, model_id, ds_id)
                if ds_id is not None
                else None
            ),
            "Residuals Chart": (
                proj_client.get_residuals_data(project_id, model_id, ds_id)
                if ds_id is not None and target_type == "Regression"
                else None
            ),
        }
        chart_getters = {k: v for k, v in chart_getters.items() if v is not None}
        results = await asyncio.gather(*list(chart_getters.values()))  # type: ignore[arg-type]
        return dict(zip(chart_getters.keys(), results))

    def format(self, record: logging.LogRecord) -> str:
        """Format model card for display"""
        if self._as_html:
            s = self.format_html(record)
        else:
            s = self.format_terminal(record)
        return s

    def format_html(self, record: logging.LogRecord) -> str:
        """Format logging record as html to render the model"""
        if not hasattr(record, "proj_json") or not hasattr(record, "model_json"):
            return ""

        params = self.get_model_card_params(
            getattr(record, "proj_json"), getattr(record, "model_json")
        )

        external_ds_id = getattr(record, "external_ds_id", None)
        if external_ds_id is not None:
            metrics = {
                score["label"]: score["value"]
                for score_group in getattr(record, "external_scores_json")
                for score in score_group["scores"]
                if (
                    score_group["datasetId"] == getattr(record, "external_ds_id")
                    and score_group["modelId"] == params.model_id
                )
            }
        else:
            metrics = dict(params.metrics.items())

        template = jinja_env.get_template("model_card.html")
        rendered_template = template.render(
            params=params,
            metrics=metrics,
            charts=self.render_charts(getattr(record, "chart_jsons", {})),
            external_ds_id=external_ds_id,
            card_key=get_random_model_key(),
            theme=context.theme,
        )
        iframe = f"""
<iframe  sandbox="allow-scripts" srcdoc="{html.escape(rendered_template)}" width="100%" height="600px"></iframe>
"""
        return iframe

    def format_terminal(self, record: logging.LogRecord) -> str:
        """Format logging record as html to render the model"""
        if not hasattr(record, "proj_json") or not hasattr(record, "model_json"):
            return ""
        params = self.get_model_card_params(
            getattr(record, "proj_json"), getattr(record, "model_json")
        )
        template = jinja_env.get_template("model_card.md")
        return template.render(
            params=params,
        )

    @staticmethod
    def render_charts(chart_jsons: Dict[str, Any]) -> Dict[str, str]:
        """Render charts as chart-name -> altair json pairs"""
        with drx_viz_theme():
            chart_renderers = {
                "Feature Impact": charts.render_feature_impact_chart,
                "ROC Curve": charts.render_roc_curve_chart,
                "Lift Chart": charts.render_lift_chart,
                "Residuals Chart": charts.render_residuals_chart,
            }
            return {
                chart_name: chart_renderers[chart_name](chart_json).to_json()
                for chart_name, chart_json in chart_jsons.items()
            }

    @staticmethod
    def get_model_card_params(
        proj_json: Dict[str, Any], model_json: Dict[str, Any]
    ) -> ModelCardKeyParams:
        project_id = proj_json["id"]
        model_id = model_json["id"]
        target_type = proj_json["targetType"]
        target_col_name = proj_json["target"]
        project_name = proj_json["projectName"]
        model_name = model_json["modelType"].rstrip()
        project_metric = proj_json["metric"]
        metrics = ModelCardFormatter._metric_parser(model_json["metrics"])
        model_url = context._webui_base_url + f"/projects/{project_id}/models/{model_id}/blueprint"
        return ModelCardKeyParams(
            project_id,
            model_id,
            model_name,
            project_name,
            project_metric,
            metrics,
            model_url,
            target_type,
            target_col_name,
        )

    @staticmethod
    def _metric_parser(metric_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metric scores using preferential order"""
        metric_order = [
            "holdout",
            "backtesting",
            "crossValidation",
            "validation",
        ]

        def parse(score_dict: Dict[str, Any]) -> Union[int, str]:
            for data_subset in metric_order:
                if score_dict.get(data_subset, None) is None:
                    continue
                else:
                    return cast(int, round(score_dict.get(data_subset), 2))  # type: ignore[arg-type]
            return "N/A"

        return {key: parse(item) for key, item in metric_dict.items()}


def get_random_model_key() -> str:
    """Generate a random key to identify each model card"""
    rand_range = []
    for _ in range(10):
        rand_range.append(str(random.randint(0, 9)))
    return "".join(rand_range)
