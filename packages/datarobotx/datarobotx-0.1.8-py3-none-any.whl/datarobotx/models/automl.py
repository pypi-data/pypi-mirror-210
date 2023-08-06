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

from typing import Optional, Union

import pandas as pd

from datarobotx.common import utils
from datarobotx.models.autopilot import AutopilotModel


class AutoMLModel(AutopilotModel):
    """
    AutoML orchestrator

    Trains challenger models asynchronously and exposes the present champion
    for predictions or deployment. Training is performed within an
    automatically created DataRobot project.

    Parameters
    ----------
    name : str, optional
        Name to use for the DataRobot project that will be created. Alias for the DR
        'project_name' configuration parameter.
    **kwargs
        Additional DataRobot configuration parameters for project creation and
        autopilot execution. See the DRConfig docs for usage examples.

    See Also
    --------
    DRConfig :
        Configuration object for DataRobot project and autopilot settings,
        also includes detailed examples of usage
    """

    def __init__(self, name: Optional[str] = None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(name=name, **kwargs)

    def fit(self, X: Union[pd.DataFrame, str], target: str, **kwargs) -> AutoMLModel:  # type: ignore[no-untyped-def]
        """
        Fit challenger models using DataRobot

        Creates a new DataRobot project, uploads `X` to DataRobot and starts Autopilot.
        Exposes the present champion model for making predictions or deployment;
        asynchronously and automatically updates the champion model.

        Parameters
        ----------
        X : pandas.DataFrame
            Training dataset for challenger models. If str, can be AI catalog dataset
            id or name (if unambiguous)
        target : str
            Column name from the dataset to be used as the target variable
        **kwargs :
            Additional optional fit-time parameters to pass to DataRobot i.e. 'weights'

        See Also
        --------
        DRConfig :
            Configuration object for DataRobot project and autopilot settings,
            also includes detailed examples of usage.
        """
        utils.create_task_new_thread(self._fit(X, target=target, **kwargs))
        return self
