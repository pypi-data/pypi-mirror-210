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
from collections.abc import Callable
from functools import partial
import logging
import re
import time
from typing import Any, cast, Dict, List, Optional, Union

import pandas as pd

import datarobotx.client.datasets as dataset_client
import datarobotx.client.projects as proj_client
from datarobotx.common import utils
from datarobotx.common.config import context
from datarobotx.common.dr_config import DRConfig
from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


@utils.hidden_instance_classmethods
class AutopilotModel(ModelOperator):
    """
    Abstract base class for autopilot orchestration

    Trains challenger models asynchronously and exposes the present champion
    for predictions or deployment. Training is performed within an
    automatically created DataRobot project.

    Parameters
    ----------
    **kwargs
        Additional DataRobot configuration parameters for project creation and
        autopilot execution. See the DRConfig docs for usage examples.

    See Also
    --------
    AutoMLModel:
        Subclass that implements AutoML orchestration
    AutoTSModel:
        Subclass that implements AutoTS orchestration
    DRConfig :
        DataRobot configuration
    """

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        params = self._prepare_params(**kwargs)
        if "project_name" not in params or params["project_name"] in [None, ""]:
            params["project_name"] = utils.generate_name()
        self._dr_config: DRConfig = DRConfig._from_dict(params)  # type: ignore[assignment]
        self._segmentation_id_column: Optional[List[str]] = None

    @classmethod
    def from_project_id(cls, project_id: str) -> AutopilotModel:
        """
        Class method to create from an existing project id

        Initializes a new object from the provided project_id. Configuration
        parameters originally used to create the project and start Autopilot
        may not be recoverable.

        Parameters
        ----------
        project_id : str, optional
            DataRobot id for the project from which to initialize the object

        Returns
        -------
        model : AutopilotModel
            New AutopilotModel instance

        Examples
        --------
        >>> my_model = AutopilotModel.from_project_id('62f14505bab13ab73593d69e')

        """
        model = cls()
        model._project_id = project_id
        utils.create_task_new_thread(model._refresh_leaderboard(), wait=True)
        return model

    @classmethod
    def from_url(cls, url: str) -> AutopilotModel:
        """
        Class method to initialize from a URL string

        Useful for copy and pasting between GUI and notebook environments

        Parameters
        ----------
        url : str
            URL of a DataRobot GUI page related to the project of interest

        Returns
        -------
        model : AutopilotModel
            The constructed AutopilotModel object

        """
        try:
            project_id = re.match("^.*/projects/([0-9a-fA-F]+)/?.*$", url).group(1)  # type: ignore[union-attr]
        except AttributeError:
            raise ValueError("Could not extract a project id from the provided url.")

        model = cls()
        model._project_id = project_id
        utils.create_task_new_thread(model._refresh_leaderboard(), wait=True)
        return model

    def _prepare_params(self, **kwargs: Any) -> Dict[str, Any]:
        """Translate parameter aliases, set required DR flags"""
        if "name" in kwargs:
            kwargs["project_name"] = kwargs.pop("name")
        return kwargs

    def get_params(self) -> DRConfig:
        """
        Configuration parameters for the model

        Note that some parameters may be initialized or materialized server-side after
        creating a project or starting Autopilot. get_params() only returns the
        client-side parameters which will be (or were) passed to DataRobot.

        Returns
        -------
        config : DRConfig
            Configuration object containing the parameters to be used with DataRobot
        """
        return cast(DRConfig, self._dr_config._from_dict(self._dr_config._to_dict()))

    def set_params(self, **kwargs: Any) -> AutopilotModel:
        """
        Set or update configuration parameters for the model

        Parameters
        ----------
        **kwargs
            DataRobot configuration parameters to be set or updated.
            See the DRConfig docs for usage examples.

        Returns
        -------
        self : AutopilotModel
            AutopilotModel instance
        """
        params = self._prepare_params(**kwargs)
        for key, value in params.items():
            if value is None:
                params[key] = utils.DrxNull()
        addtl_config = self._dr_config._from_dict(params)
        self._dr_config._update(addtl_config)
        return self

    @staticmethod
    def _rank_models(
        models_json: List[Dict[str, Any]], rec_json: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Hook for ordering the leaderboard in customizable ways

        Returns
        -------
        list of str
            List of DataRobot model id's in ascending rank order
        """
        leaderboard = [
            model["id"]
            for model in models_json
            if "Auto-Tuned Word N-Gram Text" not in model["modelType"]
        ]
        if rec_json is not None:
            leaderboard.insert(0, leaderboard.pop(leaderboard.index(rec_json["id"])))
        return leaderboard

    async def _refresh_leaderboard(self, callback: Optional[Callable] = None) -> None:  # type: ignore[type-arg]
        """
        Refresh the leaderboard

        May result in a new champion being exposed for predictions, deployment, etc.

        Parameters
        ----------
        callback : Callable
            If passed, will ensure callback is triggered after updating
        """
        if self._project_id is not None:
            models_json: List[Dict[str, Any]]
            rec_json: Optional[Dict[str, Any]]
            models_json, rec_json = await asyncio.gather(
                proj_client.get_models(pid=self._project_id),
                proj_client.get_recommended_model(pid=self._project_id),
            )
            if models_json is not None:
                self._leaderboard = self._rank_models(models_json, rec_json)
                logger.info(
                    "Emitting leaderboard update",
                    extra={"model_operator": self, "opt_in": True},
                )
        if callback is not None:
            asyncio.create_task(callback())

    @ModelOperator._with_fitting_underway
    async def _fit(
        self,
        X: Union[pd.DataFrame, str],
        *args: Any,
        champion_handler: Optional[Callable] = None,  # type: ignore[type-arg]
        **kwargs: Any,
    ) -> None:
        """Private method for orchestrating autopilot

        Parameters
        ----------
        champion_handler : callable
            Function to call to evaluate and update the champion model
        """
        self._set_fit_params(**kwargs)

        logger.info("Creating project", extra={"is_header": True})
        await self._create_project(X)
        logger.info("Running autopilot", extra={"is_header": True})
        await self._start_autopilot()
        logger.info("Fitting models...")
        await proj_client.await_autopilot(
            pid=self._project_id,  # type: ignore[arg-type]
            champion_handler=partial(self._refresh_leaderboard, callback=champion_handler),
        )
        assert self._best_model is not None
        await self._log_champion(best_model=self._best_model, ascii_art=not bool(champion_handler))
        logger.info("Autopilot complete", extra={"is_header": True})

    async def _create_project(self, X: Union[pd.DataFrame, str]) -> None:
        """Create a DR project from dataframe or AI catalog dataset"""
        json_ = self._dr_config._to_json("post_projects")
        if isinstance(X, pd.DataFrame):
            payload = utils.prepare_df_upload(X)
        elif isinstance(X, str):
            payload = None
            json_["datasetId"] = await dataset_client.resolve_dataset_id(X)
        else:
            raise TypeError(
                "Provided data for model training must be a pandas.DataFrame "
                + "or the DataRobot dataset id or name."
            )
        status_url = await proj_client.post_projects(
            payload=payload,
            json=json_,
        )
        logger.info("Awaiting project initialization...")
        self._project_id = await proj_client.await_proj(status_url=status_url)

        proj_url = context._webui_base_url + f"/projects/{self._project_id}/eda"
        logger.info("Created project [%s](%s)", self._dr_config["project_name"], proj_url)
        return

    async def _start_autopilot(self) -> None:
        """Patch /projects/ settings and /aim/ to start autopilot"""
        aim_json = self._dr_config._to_json("patch_aim")
        if "multiseriesIdColumns" in aim_json:
            await proj_client.post_multiseries_properties(
                pid=self._project_id,  # type: ignore[arg-type]
                json=self._dr_config._to_json("post_multiseries_properties"),
            )

        if self._segmentation_id_column is not None:
            segmentation_task_id = await proj_client.post_segmented_properties(
                pid=self._project_id,  # type: ignore[arg-type]
                json=aim_json,
                user_defined_segment_id_columns=self._segmentation_id_column,
            )
            aim_json["segmentationTaskId"] = segmentation_task_id

        patch_aim = proj_client.patch_aim(pid=self._project_id, json=aim_json)  # type: ignore[arg-type]
        proj_json = self._dr_config._to_json("patch_projects")
        proj_json.pop("projectName", None)

        coros = [patch_aim]
        if len(proj_json) > 0:
            patch_projects = proj_client.patch_projects(pid=self._project_id, json=proj_json)  # type: ignore[arg-type]
            coros = [patch_aim, patch_projects]

        await asyncio.gather(*coros)

        if "relationships_configuration_id" in self._dr_config:
            msg = "Awaiting feature discovery and autopilot initialization..."
        else:
            msg = "Awaiting autopilot initialization..."
        logger.info(msg)
        await proj_client.await_stage_is_modeling(self._project_id)  # type: ignore[arg-type]

    def _wait(self) -> AutopilotModel:
        """Wait for autopilot to finish"""
        while self._fitting_underway:
            time.sleep(context._concurrency_poll_interval)
        return self

    def _set_fit_params(self, **kwargs: Any) -> None:
        """Set fit-time DataRobot parameters"""
        if "target" not in kwargs or kwargs["target"] is None:
            kwargs["unsupervised_mode"] = True
        self.set_params(**kwargs)
