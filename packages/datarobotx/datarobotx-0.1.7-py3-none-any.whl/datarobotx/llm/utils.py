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
from functools import wraps
from math import floor, log10
from typing import Any, Callable, Optional

import langchain.cache


def round_sig_figs(value: Any, coerce: bool = False, n: int = 2) -> str:
    """LLM prompt helper function for rounding pd.Series to n sig figs
    Parameters
    ----------
    value : Any
        value to attempt to format as str with 2 sig figs
    coerce : bool (default=False)
        Whether to attempt to coerce value to float before formatting
    n : int
        Number of sig figs to trim to
    Notes
    -----
    Too much precision seems to increase the risk of hallucinations in
    certain applications (e.g. table extraction/summarization)
    """
    if coerce:
        try:
            value = float(value)
        except ValueError:
            pass
    if value == 0:
        return "0"
    try:
        # thanks stackoverflow
        rounded = round(value, n - int(floor(log10(abs(value)))) - 1)
        if rounded >= 10:
            rounded = int(rounded)
        as_str = repr(rounded)
        if as_str.endswith(".0"):
            as_str = as_str[:-2]
        return as_str
    except TypeError:
        return value


def with_llm_cache(
    cache: Optional[langchain.cache.BaseCache],
) -> Callable[[Callable[..., Any]], Any]:
    """Decorator for applying a custom llm cache for the duration of the function"""

    def outer_wrapper(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def inner_wrapper(*args, **kwargs) -> Any:  # type: ignore[no-untyped-def]
            llm_cache = langchain.llm_cache
            langchain.llm_cache = cache
            try:
                return f(*args, **kwargs)
            finally:
                langchain.llm_cache = llm_cache

        if cache is not None:
            return inner_wrapper
        else:
            return f

    return outer_wrapper
