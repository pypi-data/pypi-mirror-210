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

import contextvars
import os
import pathlib
from typing import Any, cast, Dict, Optional, Union

import yaml

_config_initialized = contextvars.ContextVar("config_initialized", default=False)
_token = contextvars.ContextVar("token", default="")
_endpoint = contextvars.ContextVar("endpoint", default="")
_pred_server_id = contextvars.ContextVar("pred_server_id", default="")
_rest_poll_interval = contextvars.ContextVar("rest_poll_interval", default=3)
_max_wait = contextvars.ContextVar("max_wait", default=24 * 60 * 60)
_upload_file_type = contextvars.ContextVar("upload_file_type", default="csv")
_theme = contextvars.ContextVar("theme", default="dark")

_concurrency_poll_interval = contextvars.ContextVar("concurrency_poll_interval", default=0.2)

_max_dr_ingest = contextvars.ContextVar("max_dr_ingest", default=5 * (10**9))

# Context variable for the public entry point (function name) into threaded drx work
drx_task_entry_point: contextvars.ContextVar[str] = contextvars.ContextVar("drx_task_entry_point")


def is_notebook_env() -> bool:
    """Detect if this is an interactive, ipython-based notebook"""
    try:
        from IPython import get_ipython, InteractiveShell  # pylint: disable=import-outside-toplevel

        ip: Optional[InteractiveShell] = get_ipython()  # type: ignore[no-untyped-call]
        if ip is not None and ip.has_trait("kernel"):  # type: ignore[no-untyped-call]
            return True
    except ImportError:
        pass
    return False


_force_task_blocking = contextvars.ContextVar("force_task_blocking", default=not is_notebook_env())


class ConfigReader:
    """Read configuration parameters from DataRobot YAML and environment variables
    with the latter taking precedence over the former.

    Parameters
    ----------
    config_path : Union[pathlib.Path, str]
        Path to the yaml config file
    env : bool=True
        Whether to read environment variables
    """

    def __init__(self, config_path: Optional[Union[pathlib.Path, str]] = None, env: bool = True):
        if isinstance(config_path, str):
            config_path = pathlib.Path(config_path)
        self.config_path = config_path
        self.env = env

    def load_yaml(self) -> Dict[str, Any]:
        """Read DR config yaml if it exist."""
        try:
            with self.config_path.open(mode="rb") as f:  # type: ignore[union-attr]
                return cast(Dict[str, Any], yaml.load(f, Loader=yaml.Loader))
        except (OSError, yaml.YAMLError):
            return {}

    @staticmethod
    def load_env() -> Dict[str, str]:
        """Read environment variable config values if present."""
        env_config = {}
        if "DATAROBOT_API_TOKEN" in os.environ:
            env_config["token"] = os.environ["DATAROBOT_API_TOKEN"]
        if "DATAROBOT_ENDPOINT" in os.environ:
            env_config["endpoint"] = os.environ["DATAROBOT_ENDPOINT"]
        if "DATAROBOT_PRED_SERVER_ID" in os.environ:
            env_config["pred_server_id"] = os.environ["DATAROBOT_PRED_SERVER_ID"]
        return env_config

    def read(self) -> Dict[str, Any]:
        """Dictionary of read parameters"""
        yaml_config = {}
        env_config = {}
        if self.config_path:
            yaml_config = self.load_yaml()
        if self.env:
            env_config = self.load_env()

        return {**yaml_config, **env_config}


class Context:
    """
    Interface for initializing, accessing, and setting drx context variables

    Parameters
    ----------
    token : str
        DataRobot API token
    endpoint : str
        DataRobot API endpoint
    pred_server_id : str
        Default prediction server id to use for deployments
    config_path : str
        Path to DataRobot configuration yaml file. If specified, values for token,
        endpoint, and pred_server_id in the yaml file will take precedence.

    Examples
    --------
    >>> import datarobotx as drx
    >>> drx.Context()  # show current configuration
    {'token': '***', 'endpoint': 'https://app.datarobot.com/api/v2', 'pred_server_id': '***'}
    >>> drx.Context(token='foo', endpoint='bar')  # update current configuration
    {'token': 'foo', 'endpoint': 'bar', 'pred_server_id': '***'}
    >>> c = drx.Context()
    >>> c.pred_server_id = 'foo_bar'  # alternative approach to update
    >>> drx.Context()
    {'token': 'foo', 'endpoint': 'bar', 'pred_server_id': 'foo_bar'}
    >>> drx.Context(config_path='my_path/my_config.yaml')  # update from file
    {'token': 'my_config_token', 'endpoint': 'my_config_endpoint', 'pred_server_id': 'my_config_pred_server_id'}
    """

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        getattr(self, "", None)  # trigger just-in-time defaults initialization (if needed)
        # Read from kwargs to allow user to explicitly reset params to None
        if "token" in kwargs:
            self.token = kwargs["token"]
        if "endpoint" in kwargs:
            self.endpoint = kwargs["endpoint"]
        if "pred_server_id" in kwargs:
            self.pred_server_id = kwargs["pred_server_id"]
        if "config_path" in kwargs:
            self._init_from_file(kwargs["config_path"])

    def __getattribute__(self, name: str) -> Any:
        """Initialize context from file if not previously initialized

        Notes
        -----
        Streamlit loses contextvars across multiple heads so
        initialization must be deferred to attribute access time
        """
        if not _config_initialized.get():
            _config_initialized.set(True)
            Context.__init__(
                self,
                **ConfigReader(
                    pathlib.Path("~/.config/datarobot/drconfig.yaml").expanduser().resolve()
                ).read(),
            )
        return super().__getattribute__(name)

    def _init_from_file(self, config_path: pathlib.Path) -> None:
        """Update context from config file, env variables"""
        config = ConfigReader(config_path, env=False).read()
        self.token = config.get("token", self.token)
        self.endpoint = config.get("endpoint", self.endpoint)
        self.pred_server_id = config.get("pred_server_id", self.pred_server_id)

    @property
    def token(self) -> str:
        """DataRobot API token"""
        return _token.get()

    @token.setter
    def token(self, value: str) -> None:
        _token.set(value)

    @property
    def endpoint(self) -> str:
        """DataRobot API endpoint"""
        return _endpoint.get()

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        _endpoint.set(value)

    @property
    def pred_server_id(self) -> str:
        """DataRobot prediction server id for deployments"""
        return _pred_server_id.get()

    @pred_server_id.setter
    def pred_server_id(self, value: str) -> None:
        _pred_server_id.set(value)

    @property
    def _rest_poll_interval(self) -> int:
        """HTTP polling interval in seconds for DataRobot status"""
        return _rest_poll_interval.get()

    @_rest_poll_interval.setter
    def _rest_poll_interval(self, value: int) -> None:
        _rest_poll_interval.set(value)

    @property
    def _max_wait(self) -> int:
        """Maximum polling duration before timeout in seconds"""
        return _max_wait.get()

    @_max_wait.setter
    def _max_wait(self, value: int) -> None:
        _max_wait.set(value)

    @property
    def _webui_base_url(self) -> str:
        """Base url for links to the DataRobot WebUI"""
        return self.endpoint.split("/api")[0]

    @property
    def _auth_header(self) -> Dict[str, str]:
        """DataRobot HTTP API headers for authentication"""
        return {"Authorization": "Bearer " + self.token}

    @property
    def _concurrency_poll_interval(self) -> float:
        """drx local polling interval while awaiting long running operations"""
        return _concurrency_poll_interval.get()

    @property
    def _force_task_blocking(self) -> bool:
        """Force all drx tasks to block"""
        return _force_task_blocking.get()

    @property
    def _max_dr_ingest(self) -> int:
        """Maximum DR upload size in bytes"""
        return _max_dr_ingest.get()

    @_max_dr_ingest.setter
    def _max_dr_ingest(self, value: int) -> None:
        _max_dr_ingest.set(value)

    @property
    def _upload_file_type(self) -> str:
        """
        Default file type for drx upload

        Valid types are 'csv' or 'parquet'
        """
        return _upload_file_type.get()

    @_upload_file_type.setter
    def _upload_file_type(self, value: str) -> None:
        _upload_file_type.set(value)

    @property
    def theme(self) -> str:
        """Whether charts render in dark or light"""
        return _theme.get()

    @theme.setter
    def theme(self, value: str) -> None:
        _theme.set(value)

    def __repr__(self) -> str:
        d = {
            "token": self.token,
            "endpoint": self.endpoint,
            "pred_server_id": self.pred_server_id,
        }
        return d.__repr__()


context = Context()
