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
import asyncio
import time
from typing import Any, cast, Iterable, Mapping, Optional

from datarobotx.common.client import (
    raise_status_error,
    raise_timeout_error,
    raise_value_error,
    session,
)
from datarobotx.common.config import context


async def await_status(url: str) -> Optional[str]:
    """Poll a DR API /status/ URL and pass status data to bar.update()

    Returns None if response status == 200 (still in process)
    Returns object id extracted from url if response status == 303
    """
    resp = await session.get(url, allow_redirects=False)
    if resp.status == 200:  # in process or errored update progress
        json = await resp.json()
        if json["status"].upper() in ("ERROR", "ABORTED", "EXPIRED"):
            raise_status_error(json)
        if json["status"].upper() in ("COMPLETED"):  # used for async jobs like batch predictions
            return cast(str, json["id"])
    elif resp.status == 303:  # 303 / completed
        url = resp.headers["Location"]
        obj_id = url.split("/")[-2]
        return obj_id
    else:
        await raise_value_error(resp)
    return None


async def poll(  # type: ignore[no-untyped-def]
    coro,
    coro_args: Optional[Iterable[Any]] = None,
    coro_kwargs: Optional[Mapping[str, Any]] = None,
    timeout: Optional[int] = None,
    interval: Optional[int] = None,
) -> Any:
    """Execute coro every interval seconds until a non-None value is
    returned or timeout is reached."""
    if interval is None:
        interval = context._rest_poll_interval
    if timeout is None:
        timeout = context._max_wait
    coro_args = coro_args or []
    coro_kwargs = coro_kwargs or {}
    start_time = time.time()
    final_loop = False
    while not final_loop:
        if time.time() > start_time + timeout:
            final_loop = True  # do a final loop e.g. if laptop was suspended
        return_value = await coro(*coro_args, **coro_kwargs)
        if return_value is not None:
            return return_value
        await asyncio.sleep(interval)
    raise_timeout_error(timeout, coro, coro_args, coro_kwargs)  # type: ignore[arg-type]
