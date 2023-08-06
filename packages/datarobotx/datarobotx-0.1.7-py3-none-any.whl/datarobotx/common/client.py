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
import io
import logging
import platform
import re
import textwrap
import threading
from typing import Any, Awaitable, Callable, cast, Coroutine, Dict, Mapping, Tuple

import aiohttp
import tenacity
import tqdm

from datarobotx._version import __version__ as VERSION
from datarobotx.common.config import context, drx_task_entry_point

logger = logging.getLogger("drx")
_local = threading.local()
_local.session = None


class Session:
    """Wraps aiohttp.ClientSession and implements get, post, etc.,
    managing the session and constructing full URLs."""

    def build_dr_url(self, path: str) -> str:
        """Harmonize url format

        Some calls are made with the fully qualified url (e.g. redirects from /status/)
        Others will only include the relative path from the endpoint for convenience"""
        self.validate_configuration()
        if path.startswith("https://") or path.startswith("http://"):
            return path
        else:
            return context.endpoint + path

    @property
    def session(self) -> aiohttp.ClientSession:
        """Session associated with current thread"""
        cs = _local.session
        if cs is None or cs.closed:
            self.init()
        return cast(aiohttp.ClientSession, _local.session)

    def init(self) -> None:
        """Start session associated with current thread"""
        self.validate_configuration()
        headers = self._user_agent()
        headers.update(context._auth_header)
        _local.session = aiohttp.ClientSession(headers=headers)

    async def close(self) -> None:
        """Close session associated with current thread"""
        cs = _local.session
        if cs is not None and not cs.closed:
            await cs.close()

    def get(self, path: str, *args, **kwargs) -> aiohttp.client._RequestContextManager:  # type: ignore[no-untyped-def]
        url = self.build_dr_url(path)
        return self.session.get(url, *args, **kwargs)

    def patch(  # type: ignore[no-untyped-def]
        self, path: str, *args, **kwargs
    ) -> aiohttp.client._RequestContextManager:
        url = self.build_dr_url(path)
        return self.session.patch(url, *args, **kwargs)

    def post(self, path: str, *args, **kwargs) -> aiohttp.client._RequestContextManager:  # type: ignore[no-untyped-def]
        url = self.build_dr_url(path)
        return self.session.post(url, *args, **kwargs)

    def put(self, path: str, *args, **kwargs) -> aiohttp.client._RequestContextManager:  # type: ignore[no-untyped-def]
        url = self.build_dr_url(path)
        return self.session.put(url, *args, **kwargs)

    @staticmethod
    def validate_configuration() -> None:
        """Check if we appear properly configured for DR REST interactions"""
        if not re.search(r"^[a-zA-Z0-9]+$", context.token) or not re.search(
            r"^http.+/api/.+$", context.endpoint
        ):
            raise ValueError(
                "DataRobot API token or endpoint not properly configured. "
                + "See https://app.datarobot.com/docs/api/api-quickstart/index.html "
                + "for instructions to setup a drconfig.yaml or call drx.Context() "
                + "to initialize your credentials."
            )

    @staticmethod
    def _user_agent() -> Dict[str, str]:
        """User-Agent header to be used with any requests"""
        py_version = platform.python_version()
        agent_components = [
            f"drxClient/{VERSION}",
            f"({platform.system()} {platform.release()} {platform.machine()})",
            f"Python-{py_version}",
        ]
        function = drx_task_entry_point.get(None)
        if function is not None:
            agent_components.append(f"[{function}]")
        return {
            "User-Agent": " ".join(agent_components),
        }


async def raise_value_error(resp: aiohttp.ClientResponse) -> None:
    """Raise a ValueError if DR provides unexpected response code"""

    message = (
        f"Received unexpected {resp.status} response code from DataRobot from " + f'"{resp.url}".'
    )
    try:
        json = await resp.json()
        dr_message = json["message"]
        message += f' Message: "{dr_message}"'
        if "errors" in json:
            errors = str(json["errors"])
            message += f' Errors: "{errors}"'
    except Exception:
        pass
    message = "\n".join(
        textwrap.wrap(
            message,
            width=100,
            subsequent_indent="    ",
            break_on_hyphens=False,
            break_long_words=False,
        )
    )
    e = ValueError(message)
    setattr(e, "status", resp.status)
    raise e


def raise_timeout_error(
    timeout: float, coro: Coroutine, coro_args: Tuple[Any], coro_kwargs: Mapping[str, Any]  # type: ignore[type-arg]
) -> None:
    """Raise a runtime error if polling has timed out"""
    qualname = coro.__qualname__
    args = str(coro_args)
    kwargs = str(coro_kwargs)
    message = f'Polling using coroutine "{qualname}"'
    if len(coro_args) > 0:
        message += f', with positional arguments "{args}"'
    if len(coro_kwargs) > 0:
        message += f', with keyword arguments "{kwargs}"'
    message += f" timed out after {timeout} seconds."
    raise RuntimeError(message)


def raise_status_error(json: Dict[str, Any]) -> None:
    """Raise a runtime error if error received while polling DR /status/ endpoint"""
    status_id = json.get("statusId", json.get("id", "UNKNOWN"))
    message = (
        "DataRobot error detected while checking the status of task id "
        + f"'{status_id}'.\n"
        + f"Status: {json['status']}\n"
        + f"Message: {json['message']}"
    )
    raise RuntimeError(message)


session = Session()


async def read_resp_data(
    resp: aiohttp.ClientResponse, f: io.BytesIO, pbar: tqdm.tqdm  # type: ignore[type-arg]
) -> None:
    """Read response data with progress updating

    Designed to be easily mocked due to:
    https://github.com/kevin1024/vcrpy/issues/502
    """
    async for data in resp.content.iter_chunked(1024):
        f.write(data)
        pbar.update(len(data))


async def retry_if_too_many_attempts(  # type: ignore[no-untyped-def]
    coro: Callable[..., Awaitable[Any]], *args, **kwargs
) -> Awaitable[Any]:
    """Wrapper to retry a coroutine if HTTP 429 encountered

    e.g. too many attempts
    """

    class DrxTooManyAttempts(Exception):
        pass

    @tenacity.retry(  # type: ignore[misc]
        reraise=True,
        stop=tenacity.stop_after_attempt(10),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        retry=tenacity.retry_if_exception_type(DrxTooManyAttempts),
    )
    async def retry_wrapper() -> Awaitable[Any]:
        try:
            return await coro(*args, **kwargs)
        except ValueError as e:
            try:
                assert getattr(e, "status", None) == 429
                raise DrxTooManyAttempts("Received HTTP 429")
            except AssertionError:
                raise e

    return await retry_wrapper()
