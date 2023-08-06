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
import logging
from typing import Any, Dict, Optional, Union

from datarobotx.common import utils
from datarobotx.common.dr_config import DRConfig
from datarobotx.models.autopilot import AutopilotModel
from datarobotx.models.model import Model, ModelOperator

logger = logging.getLogger("drx")


@utils.hidden_instance_classmethods
class IntraProjectModel(ModelOperator):
    """
    Abstract base class for intra-project model wrappers
    """

    def __init__(self, base_model: Union[ModelOperator], **kwargs: Any):
        super().__init__()
        self.base_model = base_model
        self._intra_config = dict(kwargs)
        self._update_root_model(**kwargs)

    @property
    def _project_id(self) -> Optional[str]:
        """Project id of base model"""
        return self.base_model._project_id

    @_project_id.setter
    def _project_id(self, value: Optional[str]) -> None:
        # Project id is composed from base model by default
        pass

    @property
    def _leaderboard(self) -> Optional[list[str]]:
        """Leaderboard of the base model"""
        return self.base_model._leaderboard

    @_leaderboard.setter
    def _leaderboard(self, value: Optional[list[str]]) -> None:
        # Leaderboard is composed from base model by default
        pass

    @property  # type: ignore[override]
    def _dr_config(self) -> DRConfig:
        """DR configuration of base model"""
        config = self.base_model._dr_config
        assert config is not None
        return config

    @_dr_config.setter
    def _dr_config(self, value: DRConfig) -> None:
        # DR config is composed from base model by default
        pass

    @property
    def _best_model(self) -> Optional[Model]:
        """Champion model exposed by base model"""
        return self.base_model._best_model

    async def _refresh_leaderboard(self, callback: Optional[Callable] = None) -> None:  # type: ignore[type-arg]
        """
        Refresh the leaderboard

        May result in a new champion being exposed by this IntraprojectModel for
        predictions, deployment, etc.

        Defaults to a passthrough (leaderboard refresh delegated to base model)

        Parameters
        ----------
        callback : Callable
            If passed, will ensure callback is triggered after updating
        """
        if self._project_id is not None:
            logger.info(
                "Emitting leaderboard update for IntraProject model",
                extra={"model_operator": self, "opt_in": True},
            )
        if callback is not None:
            asyncio.create_task(callback())

    @property
    def base_model(self) -> Union[ModelOperator]:
        """
        Base model used for fitting

        Returns
        -------
        AutopilotModel or IntraProjectModel
            Base model instance
        """
        return self._base_model

    @base_model.setter
    def base_model(self, value: Union[ModelOperator]) -> None:
        self._base_model = value

    def get_params(self) -> Dict[str, Any]:
        """
        Configuration parameters for the intra-project model

        Returns
        -------
        config : dict
            Configuration object containing the parameters for intra project model

        Notes
        -----
        Access configuration parameters for the underlying base model
        by calling get_params() on the base_model attribute
        """
        return dict(self._intra_config)

    def set_params(self, **kwargs: Any) -> IntraProjectModel:
        """
        Set configuration parameters for the intra-project model

        Parameters
        ----------
        **kwargs
            Configuration parameters to be set or updated for this model.

        Returns
        -------
        self : IntraProjectModel
            IntraProjectModel instance

        Notes
        -----
        Configuration parameters for the underlying base model can be set
        by calling set_params() on the base_model attribute
        """
        for key in kwargs:  # pylint: disable=C0206
            if key not in self._intra_config:
                raise KeyError(f"Unexpected config parameter: '{key}'")
            self._intra_config[key] = kwargs[key]
        self._update_root_model(**kwargs)
        return self

    def _get_root_model(self) -> AutopilotModel:
        """Retrieve the innermost model"""
        nested_model = self.base_model
        while hasattr(nested_model, "base_model"):
            nested_model = nested_model.base_model
        if not isinstance(nested_model, AutopilotModel):
            raise TypeError("Innermost base_model must be an instance of AutopilotModel")
        return nested_model

    def _get_params_root(self) -> DRConfig:
        """Get prameters from the innermost model"""
        return self._get_root_model().get_params()

    def _set_params_root(self, **kwargs: Any) -> AutopilotModel:
        """Update parameters on the innermost model"""
        root_model = self._get_root_model()
        return root_model.set_params(**kwargs)

    def _update_root_model(self, **kwargs: Any) -> None:
        """Optional hook for updating parameters on innermost model

        Called as part of construction and get_params()
        """
