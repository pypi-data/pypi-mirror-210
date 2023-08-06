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

import io
import logging
import re
from typing import Any, cast, Dict, Optional, Tuple, Union

import aiohttp
import pandas as pd

from datarobotx.client.status import await_status, poll
from datarobotx.common.client import raise_value_error, session
from datarobotx.common.config import context
from datarobotx.common.utils import FilesSender, SparkSender

logger = logging.getLogger("drx")


async def patch_dataset(dataset_id: str, **kwargs) -> None:  # type: ignore[no-untyped-def]
    """Patch a dataset"""
    url = f"/datasets/{dataset_id}/"
    async with session.patch(url, json=kwargs, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)


async def post_dataset_from_file(
    payload: Tuple[str, pd.DataFrame],
    catalog_name: Optional[str] = None,
    sender: Optional[Union[SparkSender, FilesSender]] = None,
) -> str:
    """
    Upload a dataset to DR from a pandas DataFrame asynchronously

    Returns the url where project creation status can be polled.
    """
    file_name, _ = payload
    if sender is None:
        sender = FilesSender(payload)
    form_data = aiohttp.FormData()
    form_data.add_field("file", sender.reader(file_name), filename=file_name)

    url = "/datasets/fromFile/"
    async with session.post(url, data=form_data, timeout=None) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        if catalog_name is not None:
            resp_json = await resp.json()
            await patch_dataset(resp_json["catalogId"], name=catalog_name)
        return resp.headers["Location"]


async def await_dataset(status_url: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Poll dataset creation status"""
    coro_args = [status_url]
    if name is not None:
        logger.info("Awaiting dataset '%s' registration...", name)
    else:
        logger.info("Awaiting dataset registration...")
    dataset_id = await poll(await_status, coro_args=coro_args)

    dataset_json = await get_dataset(dataset_id)
    dataset_url = context._webui_base_url + f"/ai-catalog/{dataset_id}"
    logger.info("Created new AI Catalog dataset [%s](%s)", dataset_json["name"], dataset_url)
    return dataset_json


async def get_dataset(dataset_id: str) -> Dict[str, Any]:
    """Retrieve dataset"""
    url = f"/datasets/{dataset_id}/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        return cast(Dict[str, Any], json)


async def get_dataset_file(dataset_id: str) -> pd.DataFrame:
    url = f"/datasets/{dataset_id}/file/"
    async with session.get(url, allow_redirects=False) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        data = await resp.text()
        return pd.read_csv(io.StringIO(data))


async def get_datasets(offset: Optional[int] = 0) -> Any:
    """Retrieve all datasets"""
    url = "/datasets/"
    limit = 100
    params = {"offset": offset, "limit": limit}
    async with session.get(url, allow_redirects=False, params=params) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        json = await resp.json()
        data = json["data"]
        if json["next"] is not None:
            offset = re.match(r"^.*offset=(\d+).*$", json["next"]).group(1)  # type: ignore[union-attr, assignment]
            data_next = await get_datasets(offset=offset)
            data += data_next
        return data


async def patch_datasets_shared_roles(did: str, json: Dict[str, Any]) -> int:
    """Share dataset with other roles"""
    url = f"/datasets/{did}/sharedRoles/"

    async with session.patch(url, json=json) as resp:
        if resp.status != 204:
            await raise_value_error(resp)
    return resp.status


async def resolve_dataset_id(string: str) -> str:
    """Retrieve dataset id corresponding to user-provided string

    String can be a dataset id itself or the name of the AI catalog
    dataset. If name is ambiguous, ValueError will be raised
    """
    try:
        await get_dataset(string)
        return string
    except ValueError:
        pass  # Fallback to looking up by name

    datasets = await get_datasets()
    df = pd.DataFrame(datasets)
    counts = df.groupby(["name"]).count()["datasetId"]
    if string not in counts:
        raise ValueError(
            f"Could not find a DataRobot dataset associated with the name or datasetId '{string}'"
        )
    elif counts.loc[string] > 1:
        raise ValueError(
            f"Multiple distinct datasets are associated with the name '{string}', please use datasetId instead"
        )
    return cast(str, df[df["name"] == string]["datasetId"].iloc[0])


async def post_data_stages(filename: str) -> str:
    """Initiate multi stage file upload"""
    url = "/dataStages/"
    body = {"filename": filename}
    async with session.post(url, json=body) as resp:
        if resp.status != 201:
            await raise_value_error(resp)
        json_ = await resp.json()
        return cast(str, json_["id"])


async def put_parts(data_stage_id: str, payload: Tuple[str, Any], part_number: int) -> None:
    """Upload part of a multi stage upload"""
    url = f"/dataStages/{data_stage_id}/parts/{part_number}/"
    filename, data = payload
    form_data = aiohttp.FormData()
    form_data.add_field("file", data, filename=filename)

    async with session.put(url, data=form_data, timeout=None) as resp:
        if resp.status != 200:
            await raise_value_error(resp)


async def post_finalize(data_stage_id: str, n_parts: int, expected_size: int) -> Dict[str, Any]:
    """Finalize multi stage upload, validate success"""
    url = f"/dataStages/{data_stage_id}/finalize/"
    body = {"stageId": data_stage_id}
    async with session.post(url, json=body) as resp:
        if resp.status != 200:
            await raise_value_error(resp)
        finalize_json = await resp.json()

    parts = finalize_json["parts"]
    if len(parts) != n_parts:
        raise RuntimeError(
            "Multistage data upload failed, expected " + f"{n_parts} parts, found {len(parts)}"
        )

    size = 0
    for part in parts:
        size += part["size"]
    if size != expected_size:
        raise RuntimeError(
            "Multistage data upload failed, expected "
            + f" {expected_size} bytes, server received {size}"
        )
    return cast(Dict[str, Any], finalize_json)


async def post_dataset_from_stages(data_stage_id: str, catalog_name: Optional[str] = None) -> str:
    """Create an AI catalog dataset from a multi-stage upload"""
    url = "/datasets/fromStage/"
    body = {
        "stageId": data_stage_id,
    }
    async with session.post(url, json=body, timeout=None) as resp:
        if resp.status != 202:
            await raise_value_error(resp)
        if catalog_name is not None:
            resp_json = await resp.json()
            await patch_dataset(resp_json["catalogId"], name=catalog_name)
        return resp.headers["Location"]


async def post_dataset_from_spark_df(
    spark_df: "pyspark.DataFrame",  # type: ignore[name-defined] # noqa: F821
    name: str,
    max_rows: int,
) -> Dict[str, Any]:
    """Post to AI Catalog from a spark dataframe

    Upload either as a single HTTP post or as a multipart upload. Halts
    iteration on the spark partitions once max_rows has been reached

    .limit() in Spark can OOM as it collapses to a single partition

    Returns json associated with the resulting AI catalog dataset
    """
    payload = (
        f"{''.join(x for x in name if x.isalnum())}_spark_export.csv",
        spark_df,
    )
    sender = SparkSender(payload, max_rows=max_rows)

    try:  # attempt multipart upload
        stage_id = await post_data_stages(payload[0])
    except ValueError:
        stage_id = None

    if stage_id is not None:
        n_parts = 0
        async for part_reader in sender.multipart_reader():
            n_parts += 1
            await put_parts(stage_id, ("part", part_reader), n_parts)

        await post_finalize(stage_id, n_parts, sender.bytes_sent)
        status_url = await post_dataset_from_stages(stage_id, catalog_name=name)
    else:  # fall back to single part upload
        status_url = await post_dataset_from_file(payload, catalog_name=name, sender=sender)
    ds_json = await await_dataset(status_url)
    return ds_json


async def post_relationships_configurations(  # type: ignore[no-untyped-def]
    dataset_definitions, relationships, feature_discovery_settings
) -> Dict[str, Any]:
    """Create a relationships configuration"""
    url = "/relationshipsConfigurations/"
    json = {
        "datasetDefinitions": dataset_definitions,
        "relationships": relationships,
        "featureDiscoveryMode": "manual",
        "featureDiscoverySettings": feature_discovery_settings,
    }
    async with session.post(url, json=json) as resp:
        if resp.status != 201:
            await raise_value_error(resp)
        return cast(Dict[str, Any], await resp.json())
