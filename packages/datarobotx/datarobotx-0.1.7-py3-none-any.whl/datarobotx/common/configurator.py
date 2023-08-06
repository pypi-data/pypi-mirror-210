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

import datetime
from typing import Optional, Tuple, Union

import pandas as pd

from datarobotx.common import utils
from datarobotx.common.dr_config import DRConfig
from datarobotx.models.autopilot import AutopilotModel


class Configurator:
    """Synthesize and apply common DR configuration patterns

    As with drx.DRConfig, parameters that are omitted or None will be assigned
    default values automatically by DataRobot as required.

    Methods apply configuration to `base` and then return a new instance of
    Configurator to allow chaining.

    Parameters
    ----------
    base : AutopilotModel or DRConfig
        Base model or configuration object to apply configuration to.
    """

    def __init__(self, base: Union[AutopilotModel, DRConfig]):
        self.base = base

    def _apply(self, **kwargs) -> "Configurator":  # type: ignore[no-untyped-def]
        """Apply parameters"""
        for key, value in kwargs.items():
            if value is None:
                kwargs[key] = utils.DrxNull()
        if isinstance(self.base, AutopilotModel):
            return Configurator(self.base.set_params(**kwargs))
        else:
            self.base._update(DRConfig._from_dict(kwargs))
            return Configurator(self.base)

    def otv(
        self,
        n_backtests: Optional[int] = None,
        validation_duration: Optional[Union[str, datetime.timedelta]] = None,
        holdout: Optional[
            Union[bool, Tuple[Union[str, datetime.datetime], Union[str, datetime.timedelta]]]
        ] = None,
    ) -> "Configurator":
        """DataRobot OTV configuration

        When using OTV the `datetime_partition_column` keyword argument indicating
        the column name of the primary datetime feature must be subsequently
        passed to fit().

        Parameters
        ----------
        n_backtests : int
            The number of backtests folds to use
        validation_duration : str or datetime.timedelta
            The duration of the validation dataset within each backtest fold. String
            will be parsed by pandas.Timedelta()
        holdout : bool or tuple of (str or datetime.datetime, str or datetime.timedelta)
            If False, the holdout fold will be disabled. Otherwise, must be a tuple
            of strings denoting (holdout_start, holdout_duration). Start date will
            be parsed by pandas.to_datetime() and duration by pandas.Timedelta() if
            specified as strings.

        Returns
        -------
        Configurator
            New Configurator object with the OTV configuration applied
        """
        dr_params = {
            "cv_method": "datetime",
            "number_of_backtests": n_backtests,
            "validation_duration": None,
            "disable_holdout": None,
            "holdout_duration": None,
            "holdout_start_date": None,
        }

        if validation_duration is not None:
            if not isinstance(validation_duration, datetime.timedelta):
                validation_duration = pd.Timedelta(validation_duration)
            dr_params["validation_duration"] = dr_duration_str(validation_duration)

        if holdout is not None:
            if holdout is False:
                dr_params["disable_holdout"] = True
            else:
                holdout_start, holdout_duration = holdout  # type: ignore[misc]
                if not isinstance(holdout_start, datetime.datetime):
                    holdout_start = pd.to_datetime(holdout_start)
                if not isinstance(holdout_duration, datetime.timedelta):
                    holdout_duration = pd.Timedelta(holdout_duration)
                dr_params.update(
                    holdout_start_date=holdout_start.isoformat(),
                    holdout_duration=dr_duration_str(holdout_duration),
                    disable_holdout=False,
                )
        return self._apply(**dr_params)

    def __repr__(self) -> str:
        if isinstance(self.base, AutopilotModel):
            return self.base.get_params().__repr__()
        else:  # DRConfig
            return self.base.__repr__()


def dr_duration_str(td: pd.Timedelta) -> str:
    """Translate timedelta to DataRobot duration string"""
    days = td.days
    seconds = td.seconds
    return f"P{days}DT{seconds}S"
