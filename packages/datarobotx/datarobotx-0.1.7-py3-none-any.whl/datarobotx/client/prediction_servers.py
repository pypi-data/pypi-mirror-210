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
from typing import Any, cast, Dict

from datarobotx.common.client import session


async def get_prediction_servers() -> Dict[str, Any]:
    """Retrieve available prediction servers.

    Only retrieves up to first 100
    """
    url = "/predictionServers/"
    async with session.get(url, allow_redirects=False) as resp:
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_default_pred_server() -> str:
    """Return the first prediction server as a default if non explicitly user specified"""
    servers_resp = await get_prediction_servers()
    try:
        return cast(str, servers_resp["data"][0]["id"])
    except IndexError:
        raise RuntimeError("No prediction server available to use as a default!")
