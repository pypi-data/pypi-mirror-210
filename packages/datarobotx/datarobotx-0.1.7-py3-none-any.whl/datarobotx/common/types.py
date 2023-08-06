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
from typing import Optional

from typing_extensions import TypedDict


class TimeSeriesPredictParams(TypedDict):
    """Typed dict for time series predict parameters"""

    forecastPoint: Optional[str]
    predictionsStartDate: Optional[str]
    predictionsEndDate: Optional[str]
    type: Optional[str]
    relaxKnownInAdvanceFeaturesCheck: Optional[bool]
