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

from abc import ABC, abstractmethod
import asyncio
from asyncio import Task
import codecs
from collections.abc import AsyncIterator, Awaitable
import concurrent.futures
import contextvars
import csv
import datetime
import inspect
import io
import logging
import re
import sys
import threading
from typing import (
    Any,
    AsyncGenerator,
    cast,
    Collection,
    Coroutine,
    Dict,
    Generator,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TYPE_CHECKING,
    TypeVar,
    Union,
)
import zipfile

import names_generator
import pandas as pd

from datarobotx.common.client import session
from datarobotx.common.config import context, drx_task_entry_point, is_notebook_env
from datarobotx.common.logging import get_widget_for_output, logging_output_widget, tqdm

if TYPE_CHECKING:
    from pyspark import Row
    import pyspark.sql

logger = logging.getLogger("drx")


def create_task(coro: Coroutine) -> Task:  # type: ignore[type-arg]
    """Vestigial wrapper for asyncio.create_task"""
    return asyncio.create_task(coro)


def get_task_entry_point() -> str:
    """Retrieve the public entry point for threaded drx work"""
    try:
        return drx_task_entry_point.get()
    except LookupError:
        pass

    depth = 2  # caller -> create_task_new_thread() -> get_task_entry_point()
    stack = inspect.stack()
    try:
        while 1:
            func_name = stack[depth].function + "()"
            if func_name.startswith("_"):
                depth += 1
                continue
            break
    except IndexError:
        return "Unknown"

    self_ = stack[depth].frame.f_locals.get("self")
    if self_ is not None:
        func_name = self_.__class__.__name__ + "." + func_name
    return func_name


def create_task_new_thread(
    coro: Awaitable, wait: Optional[bool] = None  # type: ignore[type-arg]
) -> concurrent.futures.Future:  # type: ignore[type-arg]
    """
    Execute async coroutine in separate thread (with separate event loop)

    Optionally blocks until complete. Useful for forcing contained-async code
    to execute either serially or concurrently in notebook environments where:
    - Event loop is already running and managed (e.g. by Jupyter)
    - The notebook-managed event loop may be blocked at some point,
      either by user code or intentionally while we are awaiting
      the completion of concurrent work in a separate thread
    - We do not wish to force the user to learn "await" syntax or
      where said syntax is cumbersome (e.g. method chaining)

    Cascades exceptions back up to the notebook environment

    Parameters
    ----------
    coro : Awaitable
        The task to be executed in a new thread
    wait : bool
        Whether to wait for the coro to complete before returning
        Defaults to False in interactive environments (where 'get_ipython" exists)
        otherwise True

    Returns
    -------
    result : concurrent.futures.Future
        Future from which the result can be retrieved

    Notes
    -----
    Logging is setup to log any un-caught exceptions within a thread
    and cascade upward.
    """

    def thread_entry_point(coro: Coroutine) -> Optional[Any]:  # type: ignore[type-arg]
        """Run async coroutine in a thread with no existing event loop"""

        async def async_entry_point() -> Optional[Any]:
            """Schedule drx async work and clean-up"""
            session.init()
            task = create_task(coro)
            try:
                await task
                return task.result()
            finally:
                await session.close()

        try:
            return asyncio.run(async_entry_point())
        except Exception:
            logger.exception("Exception raised when running coroutine %s", coro.__name__)
            raise

    def set_context(
        injected_context: contextvars.Context, entry_point: str, widget: Any = None
    ) -> None:
        """Set contextvars in new thread"""
        for var, value in injected_context.items():
            var.set(value)
        drx_task_entry_point.set(entry_point)
        # ipywidget object for logging
        if widget is not None:
            logging_output_widget.set(widget)

    wait = wait or context._force_task_blocking
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=1,
        initializer=set_context,
        initargs=(
            contextvars.copy_context(),
            get_task_entry_point(),
            get_widget_for_output(),
        ),
    )
    future = executor.submit(thread_entry_point, coro)  # type: ignore[arg-type]
    executor.shutdown(wait=wait)

    if wait:
        e = future.exception()  # blocks until complete
        if e is None:
            return future
        else:  # child thread traceback has already been logged at this point
            if (
                threading.current_thread() is threading.main_thread() and not is_notebook_env()
            ):  # log outer call stack if in script mode and this is the main thread
                logger.error(
                    "Main thread stack trace that preceded the child thread exception:",
                    stack_info=True,
                    extra={"is_stack_trace": True},
                )
                # traceback was already logged, no need to repeat
                sys.tracebacklimit = 0
                raise e
            else:
                return future
    else:  # interactive mode
        return future


def blank_ipython_display(cls) -> Any:  # type: ignore[no-untyped-def]
    """
    Class decorator to avoid printing repr in ipython notebooks

    Avoids printing result of `__repr__()` and extraneous new lines to the notebook
    especially for methods that return self
    """

    def _ipython_display_() -> None:
        return None

    setattr(cls, "_ipython_display_", staticmethod(_ipython_display_))
    return cls


def hidden_instance_classmethods(cls) -> Any:  # type: ignore[no-untyped-def]
    """Hide class methods from autocomplete on instance variables - YOLO!!"""

    def _dir(self) -> List[Any]:  # type: ignore[no-untyped-def]
        result = []
        for item in dir(type(self)):
            if not item.startswith("_"):
                attribute = getattr(type(self), item)
                if hasattr(attribute, "__self__"):
                    continue
            result.append(item)
        return result

    setattr(cls, "__dir__", _dir)
    return cls


PayloadType = Tuple[str, Union[bytes, io.BytesIO, io.BufferedReader]]


class FilesSender:
    """Async generator used to stream in-memory files to be uploaded and report progress."""

    def __init__(self, payload: Union[PayloadType, List[PayloadType]]) -> None:
        self.size: int = 0
        self.payload_dict: Dict[str, Any] = {}
        self.chunk_size: int = 2**16
        if not isinstance(payload, list):
            payload = [payload]
        for file_name, data in payload:
            self.payload_dict[file_name] = data
            if isinstance(data, bytes):
                self.size += len(data)
                self.payload_dict[file_name] = io.BytesIO(data)
            elif isinstance(data, io.BufferedReader):
                pos = data.tell()
                data.seek(0, io.SEEK_END)
                self.size += data.tell()
                data.seek(pos)
                self.chunk_size = io.DEFAULT_BUFFER_SIZE
            elif isinstance(data, io.BytesIO):
                self.size += data.getbuffer().nbytes

        self.pbar = tqdm(total=self.size, unit="B", unit_scale=True, unit_divisor=1000)
        self.completed: Dict[str, bool] = {file_name: False for file_name, _ in payload}

    async def reader(self, file_name: str) -> AsyncGenerator[bytes, str]:
        buffer = self.payload_dict[file_name]
        chunk = buffer.read(self.chunk_size)
        while chunk:
            self.pbar.update(len(chunk))
            yield chunk
            chunk = buffer.read(self.chunk_size)
        buffer.close()
        self.completed[file_name] = True
        if all(value is True for value in self.completed.values()):
            self.pbar.close()


class SparkSender:
    """Async generators to upload rows from a spark dataframe

    Parameters
    ----------
    payload : tuple of (str, pyspark.sql.DataFrame)
        filename and dataframe
    upload_chunk_size : int, default = 250MB
        approx. bytes to upload per chunk when using multipart upload
    max_rows : int, optional
        number of rows to limit upload to (ex-header)
    """

    def __init__(
        self,
        payload: Tuple[str, pyspark.sql.DataFrame],
        upload_chunk_size: int = (250 * (10**6)),
        max_rows: Optional[int] = None,
    ) -> None:
        _, spark_df = payload
        self.spark_df: pyspark.sql.DataFrame = spark_df
        self.max_rows: Optional[int] = max_rows
        self.fieldnames: List[str] = spark_df.columns
        self.it: Iterator[Row] = self.spark_df.toLocalIterator(prefetchPartitions=True)
        self._buffer: Optional[Iterator[Row]] = next(
            self.it
        )  # have spark fetch at object construction
        self.upload_chunk_size: int = upload_chunk_size
        self.bytes_sent: int = 0
        self.pbar = tqdm(total=self.max_rows, unit=" rows", unit_scale=True, unit_divisor=1000)

    def _encode(self, data: Optional[Dict[str, Any]] = None) -> bytes:
        """Encode dictionary as a CSV row, return as bytes"""
        buff = io.BytesIO()
        StreamWriter = codecs.getwriter("utf-8")
        handle = StreamWriter(buff)
        writer = csv.DictWriter(handle, fieldnames=self.fieldnames)
        if data is None:  # header row
            writer.writeheader()
        else:
            writer.writerow(data)

        buff.seek(0)
        return buff.read()

    def _send(self, data: Optional[Dict[str, Any]] = None) -> bytes:
        """Encode a row as csv and count row size"""
        result = self._encode(data=data)
        self.bytes_sent += len(result)
        return result

    def _buffered_it(self) -> Generator[Optional[Iterator[Row]], None, None]:
        """Buffer a spark LocalIterator by 1 row to force pre-fetch"""
        while True:
            try:
                yield self._buffer
                self._buffer = next(self.it)
            except StopIteration:
                self._buffer = None
                break

    async def reader(self, *_) -> AsyncGenerator[bytes, Any]:  # type: ignore[no-untyped-def]
        """Row-level async generator for iterating across spark dataframe"""
        yield self._send(data=None)  # header row
        delta_rows = 0  # ex-header for both limit, progress tracking

        for idx, row in enumerate(self._buffered_it()):
            if self.max_rows is not None and idx == self.max_rows:
                break
            yield self._send(data=row.asDict(recursive=False))  # type: ignore[union-attr]

            delta_rows += 1
            if delta_rows > 1000:
                self.pbar.update(delta_rows)
                delta_rows = 0

        self.pbar.update(delta_rows)
        self.pbar.close()

    async def multipart_reader(
        self,
    ) -> AsyncGenerator[AsyncGenerator[bytes, AsyncGenerator[bytes, Any]], None]:
        """Break reader into smaller chunks of rows for multipart upload

        Generator that yields a row-level generator for each multipart upload chunk
        of self.upload_chunk_size bytes
        """

        async def _part_iterator(
            first_row: bytes, row_iterator: AsyncGenerator[bytes, Any]
        ) -> AsyncGenerator[bytes, AsyncGenerator[bytes, Any]]:
            chunk_bytes_sent = 0

            def chunk_full() -> bool:
                """Check if next row will exceed chunk size"""
                if self._buffer is not None:
                    next_row_size = len(
                        self._encode(self._buffer.asDict(recursive=False))  # type: ignore[attr-defined]
                    )
                    if chunk_bytes_sent + next_row_size > self.upload_chunk_size:
                        return True
                return False

            chunk_bytes_sent += len(first_row)
            yield first_row
            if chunk_full():
                return
            async for row in row_iterator:
                chunk_bytes_sent += len(row)
                yield row
                if chunk_full():
                    break

        row_iterator = self.reader()
        while 1:
            try:
                first_row = await row_iterator.__anext__()
                yield _part_iterator(first_row, row_iterator)
            except StopAsyncIteration:
                break


def archive(contents: List[Tuple[str, Any]]) -> io.BytesIO:
    """
    Return a BytesIO buffer with the provided contents archived
    Contents should be a list of tuples [('filename', data)]
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "x", zipfile.ZIP_STORED, False) as f:
        for file_name, data in contents:
            f.writestr(file_name, data)
    zip_buffer.seek(0)
    return zip_buffer


def prepare_df_upload(df: pd.DataFrame, filename: Optional[str] = None) -> Tuple[str, io.BytesIO]:
    """
    Prepare a pandas dataframe for upload to DataRobot.
    Filetype can be one of 'csv' or 'parquet'
    Returns a tuple (file_name, data: io.BytesIO)
    """

    if filename is None:
        generate_date = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        filename = f"autogenerated_by_drx_{generate_date}.{context._upload_file_type}"
    data = io.BytesIO()
    if context._upload_file_type == "parquet":
        df.to_parquet(data, index=False, engine="pyarrow")
    else:
        StreamWriter = codecs.getwriter("utf-8")
        handle = StreamWriter(data)
        df.to_csv(handle, encoding="utf-8", index=False, quoting=csv.QUOTE_ALL)
    data.seek(0)
    return filename, data


class DrxNull:
    """Null sentinel"""


T = TypeVar("T")


class DrxConfig(ABC, Generic[T]):
    """Abstract base class for DR public config classes"""

    _rest_membership: Dict[str, str]
    _public_methods = ["keys", "to_dict"]

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Concrete subclasses define their own constructor"""

    @classmethod
    def _from_dict(cls, d: Dict[str, Any]) -> DrxConfig[T]:
        """Construct config object from a dictionary"""
        try:
            config = cls(**d)
            return config
        except TypeError:
            pass

        # Fallback: attempt construction assuming dictionary is flat
        config = cls()
        for key, value in d.items():
            path = cast(str, config._resolve_path(key))
            attributes = path.split(".")[1:-1]

            obj = config
            for attribute_name in attributes:
                obj = getattr(obj, attribute_name)
            setattr(obj, key, value)
        return config

    def _resolve_path(self, key: str, relative_path: Optional[str] = None) -> Union[List[str], str]:
        """Locate path to a key in a nested config object

        Raises exception if no path found or duplicate paths found
        """
        found_paths = []
        if relative_path is None:
            relative_path = self.__class__.__name__
        if key in dir(self):
            current_path = relative_path + "." + key
            found_paths.append(current_path)

        for attribute_name in dir(self):
            if attribute_name.startswith("_") or attribute_name in self._public_methods:
                continue
            attribute = getattr(self, attribute_name)
            if isinstance(attribute, DrxConfig):
                nested_relative_path = relative_path + "." + attribute_name
                found_paths += attribute._resolve_path(key, relative_path=nested_relative_path)

        if relative_path == self.__class__.__name__:
            if len(found_paths) == 0:
                raise ValueError(f"Unexpected configuration parameter '{key}'")
            elif len(found_paths) > 1:
                paths_str = ", ".join(found_paths)
                raise ValueError(
                    f"Parameter name '{key}' is used by multiple configuration "
                    + f"objects: {paths_str}. Please specify this parameter with "
                    + "its full path."
                )
            else:
                return found_paths[0]

        return found_paths

    def _to_json(self, route_alias: str) -> Dict[str, Any]:
        """
        Prepare a aiohttp/requests-ready json object from this configuration

        Takes a subset of the full configuration using the _rest_membership
        class attribute and the provided route_alias

        Parameters
        ----------
        route_alias : str
            Alias for the REST API route that will consume the prepared json object
            e.g. "patch_projects"
        """
        UNDERSCORES = re.compile(r"([a-z]?)(_+)([a-z])")

        def underscore_to_camel(match: re.Match) -> str:  # type: ignore[type-arg]
            prefix, underscores, postfix = match.groups()
            if len(underscores) > 1:
                # underscoreToCamel('sample_pct__gte') -> 'samplePct__gte'
                return cast(str, match.group())
            return cast(str, prefix + postfix.upper())

        def camelize(value: str) -> str:
            return UNDERSCORES.sub(underscore_to_camel, value)

        json = {}
        if route_alias in self._rest_membership:
            for attribute in self._rest_membership[route_alias]:
                attribute_value = getattr(self, attribute)
                if isinstance(attribute_value, DrxConfig):
                    attribute_value = attribute_value._to_dict()
                if isinstance(attribute_value, list):
                    attribute_value = [
                        value._to_dict() if isinstance(value, DrxConfig) else value
                        for value in attribute_value
                    ]
                if attribute_value is not None:
                    json[camelize(attribute)] = attribute_value
        for attribute in dir(self):
            if (
                not attribute.startswith("_")
                and attribute not in self._public_methods
                and attribute not in self._rest_membership
                and isinstance(getattr(self, attribute), DrxConfig)
            ):
                nested_config = getattr(self, attribute)
                nested_json = nested_config._to_json(route_alias)
                json = {**json, **nested_json}
        return json

    def _update(self, additional_config: DrxConfig[T]) -> None:
        """Merge configuration, updating self with values from provided config object"""
        if not isinstance(additional_config, DrxConfig):
            raise TypeError("_update() can only be performed with objects of type DrxConfig")

        for attribute in dir(additional_config):
            value = getattr(additional_config, attribute)
            if (
                not attribute.startswith("_")
                and attribute not in self._public_methods
                and value is not None
            ):
                if isinstance(value, DrxConfig):
                    # clone object
                    value = value._from_dict(value._to_dict())
                if hasattr(self, attribute) and isinstance(getattr(self, attribute), DrxConfig):
                    getattr(self, attribute)._update(value)
                else:
                    if isinstance(value, DrxNull):
                        value = None
                    setattr(self, attribute, value)

    def _to_dict(self, flatten: Optional[bool] = False) -> Dict[str, Any]:
        """Convert configuration to a dictionary, omitting 'None' values

        Parameters
        ----------
        flatten : bool, default=False
            Whether to produce a flat, 1-layer deep dictionary. Only flattens
            attributes that are themselves nested configuration objects.
            Parameters that are a built-in collection (e.g. list or dict)
            are not further flattened.

        Returns
        -------
        output : dict
            The resulting dictionary

        Raises
        ------
        ValueError
            If a namespace conflict occurs when flattening
        """

        def assign_no_overwrite(d: Dict[str, Any], key: str, value: Any) -> None:
            if key in d:
                raise ValueError(
                    "Could not produce a flat "
                    + "dictionary because parameter "
                    + f"'{key}' occurs more than once."
                )
            else:
                d[key] = value

        output: Dict[str, Any] = {}
        rest_attributes = {
            attribute
            for route in self._rest_membership
            for attribute in self._rest_membership[route]
        }
        for attribute in dir(self):
            if attribute.startswith("_") or attribute in self._public_methods:
                continue
            value = getattr(self, attribute)
            if isinstance(value, DrxConfig):
                d = value._to_dict(flatten=flatten)
                if len(d) > 0:
                    if not flatten or (attribute in rest_attributes):
                        assign_no_overwrite(output, attribute, d)
                    else:
                        for key, value in d.items():
                            assign_no_overwrite(output, key, value)

            elif value is not None:
                if isinstance(value, list):
                    value = [
                        scalar._to_dict() if isinstance(scalar, DrxConfig) else scalar
                        for scalar in value
                    ]
                assign_no_overwrite(output, attribute, value)

        return output

    # Implementing keys and __getitem__ allows unpacking with **
    def keys(self) -> Collection[str]:
        return self._to_dict(flatten=True).keys()

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as a dict"""
        return self._to_dict(flatten=True)

    def __contains__(self, item: Any) -> bool:
        return self.keys().__contains__(item)

    def __getitem__(self, item: Any) -> Any:
        return self._to_dict(flatten=True).__getitem__(item)

    def __setitem__(self, key: str, value: Any) -> None:
        path = cast(str, self._resolve_path(key))
        attributes = path.split(".")[1:-1]
        obj = self
        for attribute_name in attributes:
            obj = getattr(obj, attribute_name)
        setattr(obj, key, value)

    def __delitem__(self, key: str) -> None:
        self.__setitem__(key, None)

    def __len__(self) -> int:
        return len(self._to_dict(flatten=True))

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self._to_dict(flatten=True))  # type: ignore[arg-type]

    def __repr__(self) -> str:
        d = self._to_dict(flatten=True)
        return d.__repr__()

    def _get(self, key: str, default: Any = None) -> Dict[str, Any]:
        return self._to_dict(flatten=True).get(key, default)


def generate_name(style: str = "hyphen", max_len: Optional[int] = None) -> str:
    """Generate a name randomly

    Used for pojects, deployments, etc.
    """
    name = names_generator.generate_name(style=style)
    if max_len is not None and max_len > 0:
        name = name[:max_len]
    return cast(str, name)


class FutureDataFrame(pd.DataFrame):  # type: ignore[misc]
    """Lazily evaluatable subclass of pandas DataFrame

    Blocks caller attempting to access any pandas attributes until future
    is completed and DataFrame can be materialized

    Parameters
    ----------
    future : concurrent.futures.Future
        Future whose result is a pandas DataFrame
    """

    def __init__(  # type: ignore[no-untyped-def]
        self, *args, future: Optional[concurrent.futures.Future] = None, **kwargs  # type: ignore[type-arg]
    ) -> None:
        if future is not None:
            object.__setattr__(self, "_future", future)
        super().__init__(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        future = object.__getattribute__(self, "_future")
        if future is not None:
            try:
                result = future.result()
                object.__setattr__(self, "_future", None)
                super().__init__(result)
            except (Exception):  # exception will be raised by the concurrent process that failed
                object.__setattr__(self, "_future", None)

        return super().__getattribute__(name)


class FutureDict(dict):  # type: ignore[type-arg]
    """Lazily evaluatable subclass of dict

    Blocks caller attempting to access any attributes until future
    is completed and dictionary can be materialized

    Parameters
    ----------
    future : concurrent.futures.Future
        Future whose result is a dict
    """

    def __init__(  # type: ignore[no-untyped-def]
        self, *args, future: Optional[concurrent.futures.Future] = None, **kwargs  # type: ignore[type-arg]
    ) -> None:
        if future is not None:
            object.__setattr__(self, "_future", future)
        super().__init__(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        future = object.__getattribute__(self, "_future")
        if future is not None:
            try:
                result = future.result()
                object.__setattr__(self, "_future", None)
                super().__init__(result)
            except (Exception):  # exception will be raised by the concurrent process that failed
                object.__setattr__(self, "_future", None)

        return super().__getattribute__(name)


async def log_when_complete(
    it: AsyncIterator[Any], msg: str, extra: Optional[Dict[str, Any]] = None
) -> AsyncIterator[Any]:
    """Wrapper for async iterator that logs a message when iterator is exhausted"""
    async for item in it:
        yield item
    logger.info(msg, extra=extra)


TIME_UNIT_MAPPING: Dict[str, Dict[str, Any]] = {
    # FEAR supported time units: Thanks Yemi!
    "to_seconds": {
        "MILLISECOND": 0.001,
        "SECOND": 1,
        "MINUTE": int(pd.Timedelta("1 minutes").total_seconds()),
        "HOUR": int(pd.Timedelta("1 hours").total_seconds()),
        "DAY": int(pd.Timedelta("1 days").total_seconds()),
        "WEEK": int(pd.Timedelta("7 days").total_seconds()),
        "MONTH": int(pd.Timedelta("365 days").total_seconds() / 12),
        "QUARTER": int(pd.Timedelta("365 days").total_seconds() / 4),
        "YEAR": int(pd.Timedelta("365 days").total_seconds()),
        "ROW": 1,
    },
    # https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
    "to_pandas_offset": {
        "MILLISECOND": "ms",
        "SECOND": "S",
        "MINUTE": "min",
        "HOUR": "H",
        "DAY": "D",
        "WEEK": "W",
        # S = start i.e. first day of month
        "MONTH": "MS",
        "QUARTER": "QS",
        "YEAR": "YS",
    },
}
