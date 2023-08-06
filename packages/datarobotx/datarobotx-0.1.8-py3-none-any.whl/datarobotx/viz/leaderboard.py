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
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

import datarobotx.client.projects as proj_client
from datarobotx.common.config import context
from datarobotx.viz.viz import jinja_env

if TYPE_CHECKING:
    from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


class LeaderboardFormatter(logging.Formatter):
    """
    Logging formatter for rendering a leaderboard

    The async coroutine `add_format_context()` should be called before `format()`
    to extend the LogRecord with additional contextual data required
    to render the leaderboard.

    Parameters
    ----------
    attr : str
        The name of the logging record attribute that contains the ModelOperator
        object associated with the leaderboard to be rendered.
    as_html : bool
        If true, leaderboard will be formatted as html. Otherwise, will be formatted
        as a Markdown string
    """

    def __init__(self, attr: str, as_html: bool):
        super().__init__()
        self._as_html = as_html
        self._attr = attr

    async def add_format_context(self, record: logging.LogRecord) -> logging.LogRecord:
        """Add context required for formatting to logging record"""
        model: ModelOperator = getattr(record, self._attr)
        record.fitting_underway = model._fitting_underway
        if model._project_id is not None and model._leaderboard is not None:
            proj_json: Dict[str, Any]
            models_json: List[Any]
            rec_model_json: Dict[str, Any]
            proj_json, models_json, rec_model_json = await asyncio.gather(
                proj_client.get_project(model._project_id),
                proj_client.get_models(model._project_id, params={"orderBy": "-metric"}),
                proj_client.get_recommended_model(model._project_id),
            )
            record.proj_json = proj_json
            models_list = []
            for i in model._leaderboard[:5]:
                for j in models_json:
                    if j["id"] == i:
                        models_list.append(j)
                        break
            record.models_list = models_list

            record.fine_print = self.get_fine_print(model)
            if rec_model_json is not None:
                record.recommended_model_id = rec_model_json["id"]
        return record

    def format(self, record: logging.LogRecord) -> str:
        """Format leaderboard for display"""
        if self._as_html:
            s = self.format_html(record)
        else:
            s = self.format_terminal(record)
        return s

    @staticmethod
    def format_terminal(record: logging.LogRecord) -> str:
        """Format logging record for terminal output"""
        if hasattr(record, "proj_json") and hasattr(record, "models_list"):
            jinja_env.filters["metric_parser"] = LeaderboardFormatter._metric_parser
            template = jinja_env.get_template("leaderboard.md")
            if len(record.models_list) > 0:
                return template.render(
                    models=record.models_list,
                    metrics=record.models_list[0]["metrics"].keys(),
                    key_metric=record.proj_json["metric"],
                    projectId=record.proj_json["id"],
                    project_name=record.proj_json["projectName"],
                )
            else:
                return "Project does not have a leaderboard yet"
        else:
            return "Project does not have a leaderboard yet"

    @staticmethod
    def format_html(record: logging.LogRecord) -> str:
        """Format logging record for html output"""
        if (
            hasattr(record, "models_list")
            and hasattr(record, "proj_json")
            and len(getattr(record, "models_list", [])) > 0
        ):
            jinja_env.filters["metric_parser"] = LeaderboardFormatter._metric_parser
            template = jinja_env.get_template("leaderboard.html")
            metrics = record.models_list[0]["metrics"].keys()
            return template.render(
                models=record.models_list,
                recommended_model_id=getattr(record, "recommended_model_id", None),
                metrics=metrics,
                key_metric=record.proj_json["metric"],
                projectId=record.proj_json["id"],
                project_name=record.proj_json["projectName"],
                webui_base_url=context._webui_base_url,
                fine_print=getattr(record, "fine_print", None),
            )
        elif hasattr(record, "fitting_underway") and not record.fitting_underway:
            return "<h3>Project does not have a leaderboard yet</h3>"
        else:
            return ""

    @staticmethod
    def _metric_parser(metric_dict: Dict[str, Optional[float]]) -> Union[float, str]:
        """Searches through scores and returns first one found"""
        search_order = [
            "holdout",
            "backtesting",
            "crossValidation",
            "validation",
        ]
        for data_subset in search_order:
            if metric_dict.get(data_subset, None) is None:
                continue
            else:
                return round(metric_dict.get(data_subset), 2)  # type: ignore[arg-type]
        return "N/A"

    @staticmethod
    def get_fine_print(model: ModelOperator) -> List[str]:
        """Get additional caveats that should be displayed below the leaderboard

        Notes
        -----
        Imports occur optionally at runtime as some abstractions may require additional
        dependencies
        """
        fine_print = ["Best available out of sample scores presented for each model"]
        try:
            from datarobotx import ColumnReduceModel

            if isinstance(model, ColumnReduceModel):
                fine_print.insert(
                    0,
                    "ColumnReduceModel may rank models differently than DataRobot",
                )
        except ImportError:
            pass
        return fine_print
