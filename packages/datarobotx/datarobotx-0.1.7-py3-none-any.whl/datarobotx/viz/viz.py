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
"""
Helpers related to displaying models

e.g. implementing __repr__()/__str__()/_ipython_display_()
"""
import asyncio
from contextlib import contextmanager
import logging
import typing as t
from typing import TYPE_CHECKING

import altair as alt
from altair.utils.plugin_registry import PluginEnabler
from ipywidgets import widgets
from jinja2 import Environment, PackageLoader, select_autoescape

from datarobotx.common import utils
from datarobotx.common.config import context
from datarobotx.common.logging import (
    get_widget_for_output,
    is_widgets_nb_env,
    logging_output_widget,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger("drx")

SEQUENTIAL_BLUE = [
    "#2d8fe2",
    "#559ee6",
    "#73adea",
    "#8ebcee",
    "#a8ccf2",
    "#c1dbf6",
    "#daeafa",
    # "#f4f9fe",
]
SEQUENTIAL_ORANGE = [
    "#ff5600",
    "#ff712f",
    "#ff8950",
    "#ffa06f",
    "#ffb68f",
    "#ffcbaf",
    "#ffe1d0",
]
SEQUENTIAL_GRAY = [
    "#68849d",
    "#7d96ac",
    "#94aaba",
    "#abbdc9",
    "#c3d0d9",
    "#dce4e9",
    "#f6f8f9",
    "#53718f",
]
QUALITATIVE = [
    "#2d8fe2",
    "#39b54a",
    "#f1c232",
    "#ff5600",
    "#b70000",
    "#da00a8",
    "#662d91",
    "#bac5ce",
]
DIVERGING = [
    "#2d8fe2",
    "#69a1e5",
    "#90b4e9",
    "#b2c8ec",
    "#d2dcee",
    "#f1f1f1",
    "#fed4c3",
    "#ffb796",
    "#ff996a",
    "#ff793e",
    "#ff5600",
]

FONT = "Roboto"

MARK_COLOR = SEQUENTIAL_BLUE[0]


def datarobot_theme() -> t.Dict[str, t.Any]:
    """Theme and formatting for drx generated altair charts"""
    return {
        "config": {
            "mark": {"color": SEQUENTIAL_BLUE[0], "FONT": FONT},
            "view": {
                "stroke": "transparent",
                "continuousWidth": 350,
                "discreteWidth": 350,
                "continuousHeight": 300,
                "discreteHeight": 300,
            },
            "range": {
                "category": QUALITATIVE,
                "_DIVERGING": DIVERGING,
                "heatmap": DIVERGING,
                "ordinal": SEQUENTIAL_ORANGE,
                "ramp": SEQUENTIAL_BLUE,
            },
            "axis": {
                "labelFONT": FONT,
                "titleFONT": FONT,
                "labelColor": "gray",
                "ticks": False,
                "labelOffset": 0,
                "domainWidth": 4,
                "domainColor": "darkgray",
                "labelPadding": 9,
                "domainCap": "round",
            },
            "axisX": {"grid": False},
            "axisY": {"domain": False},
            "legend": {"titleFONT": FONT, "labelFONT": FONT},
            "arc": {"fill": MARK_COLOR},
            "area": {"fill": MARK_COLOR},
            "line": {
                "stroke": MARK_COLOR,
                "strokeWidth": 4,
                "strokeCap": "round",
                "strokeJoin": "round",
                "interpolate": "natural",
            },
            "path": {"stroke": MARK_COLOR},
            "rect": {"fill": MARK_COLOR},
            "shape": {"stroke": MARK_COLOR, "color": MARK_COLOR, "filled": True},
            "point": {
                "stroke": MARK_COLOR,
                "color": MARK_COLOR,
                "filled": True,
                "size": 85,
            },
            "symbol": {"fill": MARK_COLOR},
            "title": {
                "FONT": FONT,
                "anchor": "start",
                "FONTSize": 18,
                "FONTStyle": 900,
            },
        }
    }


def datarobot_dark() -> t.Dict[str, t.Any]:
    """Dark theme and formatting for drx generated altair charts"""
    base = datarobot_theme()
    base_config = base["config"]
    base_config["view"] = {
        "stroke": "transparent",
        "background": "#333",
        "continuousWidth": 350,
        "discreteWidth": 350,
        "continuousHeight": 300,
        "discreteHeight": 300,
    }
    base_config["background"] = "#333"
    base_config["legend"] = {
        "labelColor": "white",
        "titleColor": "white",
        "symbolStrokeColor": "lightgray",
        "symbolFillColor": "lightgray",
    }
    base_config["axisY"] = {"domain": False, "gridColor": "gray"}
    base_config["axis"] = {
        "labelFONT": FONT,
        "titleFONT": FONT,
        "labelColor": "lightgray",
        "ticks": False,
        "labelOffset": 0,
        "domainWidth": 4,
        "domainColor": "darkgray",
        "labelPadding": 9,
        "domainCap": "round",
        "titleColor": "white",
    }
    base_config["title"] = {"color": "white"}
    base["config"] = base_config
    return base


@contextmanager
def drx_viz_theme() -> PluginEnabler:
    current_state = alt.themes.active
    if context.theme == "dark":
        new_theme = "datarobot_dark"
    else:
        new_theme = "datarobot_light"
    try:
        yield alt.themes.enable(new_theme)
    finally:
        alt.themes.enable(current_state)


def set_viz_theme() -> None:
    """Set the viz theme for your entire environment based on current context"""
    if context.theme == "dark":
        alt.themes.enable("datarobot_dark")
    else:
        alt.themes.enable("datarobot_light")


class ThreadedIpywidgetsHandler(logging.Handler):
    """
    Widget logging handler that formats records in a new thread

    Useful if formatting logic might block the calling thread.
    Creates a new widget and then updates the widget in place.

    Takes advantage of the custom async hook "add_format_context"
    on the formatter (if it exists) to perform any async work
    to append required context on the LoggingRecord to format.

    Parameters
    ----------
    output_widget : widgets.Widget
        The container widget where the new widget should be created
    """

    def __init__(self, output_widget: widgets.Widget):
        super().__init__()
        self.output_widget = output_widget

    def emit(self, record: logging.LogRecord) -> None:
        """Format and update widget in separate thread to avoid blocking"""

        async def _wrapper() -> None:
            """Format and create or update widget"""
            nonlocal record
            logging_output_widget.set(self.output_widget)
            if hasattr(self.formatter, "add_format_context"):
                record = await self.formatter.add_format_context(record)  # type: ignore[union-attr]
            new_widget = widgets.HTML(self.format(record))
            new_widget._id = id(self)

            box_widget = get_widget_for_output()
            if (
                len(
                    list(
                        filter(
                            lambda x: getattr(x, "_id", None) == id(self),  # type: ignore[arg-type]
                            box_widget.children,  # type: ignore[union-attr]
                        )
                    )
                )
                > 0
            ):
                box_widget.children = [  # type: ignore[union-attr]
                    child if not getattr(child, "_id", None) == id(self) else new_widget
                    for child in box_widget.children  # type: ignore[union-attr]
                ]
            else:
                box_widget.children = box_widget.children + (new_widget,)  # type: ignore[union-attr]

        utils.create_task_new_thread(_wrapper())


@contextmanager
def designated_widget_handler(
    formatter: t.Optional[logging.Formatter] = None,
    filter_on: t.Optional[t.Callable] = None,  # type: ignore[type-arg]
    remove_when: t.Optional[t.Callable] = None,  # type: ignore[type-arg]
) -> t.Iterator:  # type: ignore[type-arg]
    """
    Setup and teardown context manager for a widget logging handler

    Used to dynamically setup/destroy a handler for a specific, designated
    purpose.

    Parameters
    ----------
    formatter : logging.Formatter, optional
        Formatter to be used with the designated handler
    filter_on : logging.Filter or callable, optional
        Function to be used for filtering to the records that
        the handler should process
    remove_when : callable, optional
        If specified, designated handler will be removed when
        the provided function evaluates True, polling every second.
        If omitted, the handler will be removed when the scope of
        the context manager ends.

    """
    if not is_widgets_nb_env():
        yield
        return

    handler = ThreadedIpywidgetsHandler(get_widget_for_output())
    if formatter is not None:
        handler.setFormatter(formatter)
    if filter_on is not None:
        handler.addFilter(filter_on)
    logger.addHandler(handler)

    yield

    if remove_when is not None:

        async def _wrapper() -> None:
            while 1:
                if remove_when():  # type: ignore[misc]
                    logger.removeHandler(handler)
                    break
                await asyncio.sleep(1)

        utils.create_task_new_thread(_wrapper())
    else:
        logger.removeHandler(handler)


alt.themes.register("datarobot_light", datarobot_theme)
alt.themes.register("datarobot_dark", datarobot_dark)
jinja_env = Environment(
    loader=PackageLoader(
        "datarobotx",
        package_path="viz/templates",
    ),
    autoescape=select_autoescape(),
)
