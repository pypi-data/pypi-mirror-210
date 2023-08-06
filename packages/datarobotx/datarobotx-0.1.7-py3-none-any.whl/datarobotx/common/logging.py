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
import contextvars
import logging
import os
import re
import textwrap
from typing import cast, Optional, Tuple, Union

from termcolor import colored
import tqdm as tqdm_typing
from tqdm.notebook import tqdm_notebook, TqdmHBox  # type: ignore[attr-defined]
from tqdm.std import tqdm as std_tqdm

from datarobotx.common.config import is_notebook_env

logger = logging.getLogger("drx")
logger.setLevel(logging.INFO)
# Context variable for the jupyter widget logging messages  + progress bars should be directed toward
logging_output_widget: contextvars.ContextVar = contextvars.ContextVar(  # type: ignore[type-arg]
    "logging_output_widget"
)


def is_widgets_nb_env() -> bool:
    """Detect if this is an interactive notebook with ipywidgets installed"""

    if not is_notebook_env() or "DATAROBOT_NOTEBOOK_IMAGE" in os.environ:
        return False
    try:
        import ipywidgets  # noqa: F401  pylint: disable=import-outside-toplevel, unused-import

        return True
    except ImportError:
        pass
    return False


def get_widget_for_output() -> Optional[widgets.VBox]:
    """Get or create a widget to direct logging output in notebook environments"""
    try:
        return logging_output_widget.get()
    except LookupError:
        if is_widgets_nb_env():
            from IPython import display  # pylint: disable=import-outside-toplevel
            import ipywidgets as widgets  # pylint: disable=import-outside-toplevel

            box = widgets.VBox()
            # lock widget to the calling cell
            display.display(box)  # type: ignore[no-untyped-call]
            return box
        else:
            return None


class drx_tqdm(std_tqdm):  # type: ignore[type-arg]
    """Indent terminal progress bars before outputting"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if "bar_format" in kwargs:
            kwargs["bar_format"] = "    " + kwargs["bar_format"]
        else:
            kwargs["bar_format"] = "    {l_bar}{bar}{r_bar}"
        if "ncols" in kwargs:
            kwargs["ncols"] = min(kwargs["ncols"], 80)
        else:
            kwargs["ncols"] = 80
        super().__init__(*args, **kwargs)


class drx_tqdm_notebook(tqdm_notebook):  # type: ignore[type-arg]
    """Subclass that renders tqdm_notebook in the context of a drx ipywidget"""

    def __init__(self, *args, display: bool = False, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, display=display, **kwargs)  # type: ignore[call-overload]
        self.displayed = True
        self._last_total = self.total

    @staticmethod
    def status_printer(*args, **kwargs) -> TqdmHBox:  # type: ignore[no-untyped-def]
        """Render tqdm bar within existing widget container in target cell"""
        box_widget = get_widget_for_output()
        container: TqdmHBox = tqdm_notebook.status_printer(*args, **kwargs)
        outer_container = widgets.HBox()
        outer_container.children = (
            widgets.HTML("<pre>&nbsp;&nbsp;&nbsp;&nbsp;</pre>", layout=widgets.Layout(margin="0")),
            container,
        )
        if box_widget is not None:
            box_widget.children = box_widget.children + (outer_container,)
        return container

    def refresh(  # type: ignore[override]
        self,
        nolock: bool = False,
        lock_args: Optional[
            Union[Tuple[Optional[bool], Optional[float]], Tuple[Optional[bool]]]
        ] = None,
    ) -> Optional[bool]:
        """Ensure changing bar totals render properly"""
        if self.total != self._last_total:
            _, pbar, *_ = self.container.children
            pbar.max = self.total
            if self._last_total is None and self.ncols is None:
                pbar.bar_style = ""
                pbar.layout.width = None
            self._last_total = self.total
        return cast(Optional[bool], super().refresh(nolock=nolock, lock_args=lock_args))

    def close(self) -> None:
        if not self.leave:
            box_widget = logging_output_widget.get()
            box_widget.children = tuple(
                child for child in box_widget.children if not isinstance(child, widgets.HBox)
            )
        super().close()


class DrxFormatter(logging.Formatter):
    """Format log messages for ipython, terminal handlers"""

    _CHAMPION_HTML_TEMPLATE = r"""<span style="color:SlateGrey">     ,,,,,,,,,
   #-#       #-#
   # #   <span style="color:Gold">*</span>   # #    </span>CHAMPION<span style="color:SlateGrey">
    # #     # #     {champion}
      #*# #*#
        /,\
       `````</span>"""
    _CHAMPION_TERM_TEMPLATE = "\n".join(
        [
            "     ,,,,,,,,,",
            "   #-#       #-#",
            "   # #   " + colored("*", "yellow") + "   # #    CHAMPION",
            "    # #     # #     {champion}",
            "      #*# #*#",
            "        /,\\",
            "       `````",
        ]
    )
    _PRE_STYLE_TEMPLATE = (
        "line-height:1.3;"
        + "white-space:pre;"
        + "overflow-x:auto;"
        + "font-family:Menlo, Consolas, 'DejaVu Sans Mono', monospace;"
        + "padding:0;"
        + "margin:0;"
    )

    def __init__(self, *args, as_html: Optional[bool] = True, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._as_html = as_html

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)

        if self._as_html:
            s = self.format_html(record, s)
        else:
            s = self.format_terminal(record, s)
        return s

    def format_terminal(self, record: logging.LogRecord, s: str) -> str:
        """Format log messages for display in terminals (e.g. ANSI codes)"""

        if record.exc_info is not None or hasattr(record, "is_stack_trace"):
            s = colored(f"{s}", "red", attrs=["bold"])
        elif record.levelno == logging.WARNING:
            s = colored("  - WARNING:", "red", attrs=["bold"]) + f" {s}"
        elif hasattr(record, "is_header"):
            s = colored("#", "blue", attrs=["bold"]) + colored(f" {s}", attrs=["bold"])
        elif hasattr(record, "is_champion_msg"):
            s = re.sub(r"Champion model: ", "", s)
            s = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", s)
            if len(s) > 65:
                s = s[:62] + "..."
            s = self._CHAMPION_TERM_TEMPLATE.format(champion=s)
        else:
            lines = []
            for line in s.split("\n"):
                lines += textwrap.wrap(
                    line,
                    width=80,
                    initial_indent="    ",
                    subsequent_indent="    ",
                    break_on_hyphens=False,
                    break_long_words=False,
                )
            lines[0] = colored("  - ", attrs=["bold"]) + lines[0][4:]
            s = "\n".join(lines)
        return s

    def format_html(self, record: logging.LogRecord, s: str) -> str:
        """Format log messages for display in notebook (e.g. HTML)"""
        s = self.format_html_hyperlinks(s)
        if record.exc_info is not None or hasattr(record, "is_stack_trace"):
            s = f'<span style="color:IndianRed;font-weight:bold;">{s}</span>'
        elif record.levelno == logging.WARNING:
            s = (
                '<span style="font-weight:bold;">'
                + f'<span style="color:IndianRed;">  - WARNING:</span></span> {s}'
            )
        elif hasattr(record, "is_header"):
            s = (
                '<span style="font-weight:bold;">'
                + f'<span style="color:SteelBlue;">#</span> {s}</span>'
            )
        elif hasattr(record, "is_champion_msg"):
            s = re.sub(r"Champion model: ", "", s)
            s = self._CHAMPION_HTML_TEMPLATE.format(champion=s)
        else:
            lines = []
            for line in s.split("\n"):
                lines.append(textwrap.indent(line, "    "))
            lines[0] = (
                '  <span style="color:SlateGray;font-weight:bold;">-</span> ' + f"{lines[0][4:]}"
            )
            s = "\n".join(lines)
        s = f'<pre style="{self._PRE_STYLE_TEMPLATE}">{s}</pre>'
        return s

    @staticmethod
    def format_html_hyperlinks(s: str) -> str:
        """Turn markdown-style hyperlinks into HTML hyperlinks"""
        html = (
            '<a target="_blank" rel="noopener noreferrer" '
            + 'style="color:DodgerBlue;text-decoration:underline" '
            + r'href="\2">\1</a>'
        )
        return re.sub(r"\[(.+?)\]\((.+?)\)", html, s)


try:
    import ipywidgets as widgets

    class IpywidgetsHandler(logging.Handler):
        """Log handler for Jupyter environments with ipywidgets"""

        def emit(self, record: logging.LogRecord) -> None:
            box_widget = get_widget_for_output()
            assert box_widget is not None
            box_widget.children = box_widget.children + (
                widgets.HTML(self.format(record), layout=widgets.Layout(margin="0")),
            )

except ImportError:
    pass


async def refresh_bar(tqdm_bar: tqdm_typing.tqdm, delay: float = 0.5) -> None:  # type: ignore[type-arg]
    """Refreshes a bar until it is closed."""
    while not tqdm_bar.disable:
        tqdm_bar.refresh()
        await asyncio.sleep(delay)


def setup_default_log_handler(force_terminal_output: bool = False) -> logging.Handler:
    """
    Initialize and configure the logging handler

    Parameters
    ----------
    force_terminal_output: bool
        If True, the default handler will always use the terminal output
    """

    if not force_terminal_output and is_widgets_nb_env():
        handler: logging.Handler = IpywidgetsHandler()
        handler.setFormatter(DrxFormatter(as_html=True))
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(DrxFormatter(as_html=False))
    # Unsubscribe from opt-in logging messages by default
    handler.addFilter(filter=lambda x: bool(not hasattr(x, "opt_in")))
    logger.addHandler(handler)
    return handler


tqdm = drx_tqdm_notebook if is_widgets_nb_env() else drx_tqdm
default_handler = setup_default_log_handler()
