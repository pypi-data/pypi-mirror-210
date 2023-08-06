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
import logging
from typing import Any, Dict, List, TYPE_CHECKING, Union

import datarobotx.client.datasets as dataset_client
import datarobotx.client.deployments as deploy_client
import datarobotx.client.projects as proj_client
from datarobotx.common.utils import create_task_new_thread

if TYPE_CHECKING:
    from datarobotx.models.deployment import Deployment
    from datarobotx.models.model import ModelOperator

logger = logging.getLogger("drx")


def share(any: Union[ModelOperator, Deployment, str], emails: Union[str, List[str]]) -> None:
    """
    Shares a drx object with other users.
    Object can be a dataset, project, or deployment.
    Access is set to Owner.

    Parameters
    ----------
    any : ModelOperator or Deployment or str
        A project or deployment object or a datarobot asset id to share
    emails : str or list[str]
        An email or list of emails to share a deployment with

    Returns
    -------
    None

    Examples
    --------

    Share a drx project object with a user

    >>> drx.share(project, "user1@datarobot.com")

    Share a drx project using the id with multiple users

    >>> drx.share("123456", ["user1@datarobot.com", "user2@datarobot.com"])

    """

    if isinstance(any, str):
        asset_id = any
        asset_type = create_task_new_thread(_find_asset_type(asset_id), wait=True).result()
        create_task_new_thread(_share_id(asset_id, asset_type, emails), wait=True)

    elif getattr(any, "_project_id", None) is not None:
        any.share(emails)
    elif getattr(any, "_deployment_id", None) is not None:
        any.share(emails)
    else:
        raise ValueError(
            """Invalid input. Share expects a drx project, deployment or
            a DataRobot id for a dataset, project or deployment"""
        )


async def _find_asset_type(asset_id: str) -> str:
    """Searches datasets, projects and deployments for id and returns the asset_type"""
    results = await asyncio.gather(
        proj_client.get_project(asset_id),
        deploy_client.get_deployment(asset_id),
        dataset_client.get_dataset(asset_id),
        return_exceptions=True,
    )
    asset_types = ["project", "deployment", "dataset"]
    found_asset = [j for i, j in zip(results, asset_types) if not isinstance(i, Exception)]
    if len(found_asset) > 1:
        raise ValueError("Ambiguous request: Multiple assets found with the same id!")
    elif len(found_asset) == 0:
        raise ValueError("No assets found with the provided id")
    return found_asset[0]


async def _share_id(asset_id: str, asset_type: str, emails: Union[str, List[str]]) -> None:
    """Share an asset by calling the appropriate DR API for its type"""
    if isinstance(emails, str):
        emails = [emails]

    if asset_type == "project":
        roles: List[Dict[str, Union[str, bool]]] = [
            {"role": "OWNER", "username": i} for i in emails
        ]
        json: Dict[str, Union[str, List[Any], bool]] = {"data": roles}
        await proj_client.patch_access_control(asset_id, json=json)

    elif asset_type == "deployment":
        roles = [{"shareRecipientType": "user", "role": "OWNER", "username": i} for i in emails]
        json = {"operation": "updateRoles", "roles": roles}
        await deploy_client.patch_shared_roles(asset_id, json=json)
    elif asset_type == "dataset":
        roles = [
            {
                "shareRecipientType": "user",
                "role": "OWNER",
                "canUseData": True,
                "canShare": True,
                "name": i,
            }
            for i in emails
        ]
        json = {
            "operation": "updateRoles",
            "applyGrantToLinkedObjects": True,
            "roles": roles,
        }
        await dataset_client.patch_datasets_shared_roles(asset_id, json=json)
    else:
        raise ValueError("Unexpected Exception. Asset found but exception raised on API call")
    emails = ", ".join(emails)
    logger.info(
        "%s '%s' shared with %s",
        asset_type.title(),
        asset_id,
        emails,
        extra={"is_header": True},
    )
