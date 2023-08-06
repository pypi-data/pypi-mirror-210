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

from typing import Any, Dict, List, Optional, Union

import pandas as pd

from datarobotx.common import utils
from datarobotx.models.autopilot import AutopilotModel


class AutoClusteringModel(AutopilotModel):
    """
    Automated clustering orchestrator

    Trains clustering models asynchronously and exposes the model
    with the present highest silhouette score for predictions or deployment.
    Training is performed within an automatically created DataRobot project.

    Parameters
    ----------
    name : str, optional
        Name to use for the DataRobot project that will be created. Alias for the DR
        'project_name' configuration parameter.
    n_clusters : int or list of int, optional
        Number of clusters to form. Specify as a single integer between 2 and 100 or a
        list of up to 10 values.

        Alias for the DR 'autopilot_cluster_list' configuration parameter.
    **kwargs
        Additional DataRobot configuration parameters for project creation and
        autopilot execution. See the DRConfig docs for usage examples.

    See Also
    --------
    DRConfig :
        Configuration object for DataRobot project and autopilot settings,
        also includes detailed examples of usage
    """

    def __init__(  # type: ignore[no-untyped-def]
        self,
        name: Optional[str] = None,
        n_clusters: Optional[Union[int, List[int]]] = None,
        **kwargs,
    ):
        super().__init__(name=name, n_clusters=n_clusters, **kwargs)

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:  # type: ignore[no-untyped-def]
        """Translate parameter aliases, set required DR flags"""
        params = super()._prepare_params(**kwargs)
        if "n_clusters" in params:
            n_clusters = params.pop("n_clusters")
            if isinstance(n_clusters, int):
                n_clusters = [n_clusters]
            params["autopilot_cluster_list"] = n_clusters

        params["unsupervised_mode"] = True
        params["unsupervised_type"] = "clustering"
        return dict(params)

    def fit(self, X: Union[pd.DataFrame, str], **kwargs) -> AutoClusteringModel:  # type: ignore[no-untyped-def]
        """
        Fit clustering models using DataRobot

        Creates a new DataRobot project, uploads `X` to DataRobot and starts Autopilot
        in clustering mode. Exposes the present model with the highest silhouette
        score for making predictions or deployment.

        Parameters
        ----------
        X : pandas.DataFrame or str
            Training dataset for anomaly detection models.
            If str, can be AI catalog dataset id or name (if unambiguous)
        **kwargs :
            Additional optional fit-time parameters to pass to DataRobot i.e. 'weights'

        See Also
        --------
        DRConfig :
            Configuration object for DataRobot project and autopilot settings,
            also includes detailed examples of usage.
        """
        utils.create_task_new_thread(self._fit(X, **kwargs))
        return self
