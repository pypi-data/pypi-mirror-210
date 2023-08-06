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
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import BaseMemory
import pandas as pd
from pydantic import root_validator

import datarobotx.client.projects as proj_client
from datarobotx.common.client import retry_if_too_many_attempts
from datarobotx.common.utils import create_task_new_thread
from datarobotx.llm.utils import round_sig_figs

_DEFINE_FEATURE_TEMPLATE = (
    "{context}\n\n"
    + "A dataset is being used for this work; it is possible that a "
    + "data scientist has already done some common, simple "
    + "transformations on the original raw data to prepare it for "
    + "modeling.\n\n"
    + "Write a brief description for the field. \n"
    + "Do not include example values or comment on value frequency in the"
    + "in the brief description. Do not speculate on the scope of exactly what"
    + "is or is not included in the field or the time frame the field applies to.\n\n"
    + "{history}\n"
    + "Field: {feature}\n"
    + "Brief description:\n"
)


class DefineFeatureChain(LLMChain):
    """Define a feature using an LLM

    Remembers prior definitions when completing new definitions

    Notes
    -----
    Chain inputs:

    context : str
        Context of the problem / use case in which a feature definition is being requested
    feature : str
        The feature for which a definition is being requested

    Chain outputs:

    description : str
        Description of the feature in natural language
    """

    prompt: BasePromptTemplate = PromptTemplate(
        input_variables=["context", "history", "feature"], template=_DEFINE_FEATURE_TEMPLATE
    )
    memory: BaseMemory = None
    output_key: str = "description"
    default_stop: List[str] = ["\n"]

    @root_validator(pre=True)  # type: ignore[misc]
    def _init_memory(  # pylint: disable=no-self-argument
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize default memory if not explicitly specified"""
        if "memory" not in values:
            values["memory"] = ConversationTokenBufferMemory(
                llm=values["llm"],
                max_token_limit=1500,
                memory_key="history",
                input_key="feature",
                human_prefix="Field",
                ai_prefix="Brief description",
            )
        return values

    @property
    def input_keys(self) -> List[str]:
        return ["context", "feature"]

    def prep_inputs(self, inputs: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        inputs = super().prep_inputs(inputs)
        if "stop" not in inputs:
            inputs["stop"] = self.default_stop
        return inputs


class DataDictChain(Chain):
    """Generate a data dictionary using an LLM

    Parameters
    ----------
    as_json : bool, default = False
        Whether chain output should be returned as a natural language or json
        str
    def_feature_chain : LLMChain, optional
        Chain to be used for defining individual features. If not provided, will be
        initialized with a default chain that prompts and retrieves individual
        definitions
    verbose : bool, default = False
        Whether the chain should be run in verbose mode; only applies if the
        default feature definition chain is being used

    Examples
    --------
    >>> import json
    >>> import langchain
    >>> import os
    >>> from datarobotx.llm import DataDictChain
    >>> use_case_context = "Predicting hospital readmissions"
    >>> dr_project_id = "XXX"
    >>> os.environ["OPENAI_API_KEY"] = "XXX"
    >>> llm = langchain.llms.OpenAI(model_name="text-davinci-003")
    >>> chain = DataDictChain(llm=llm)
    >>> outputs = chain(inputs=dict(project_id=dr_project_id, context=use_case_context))
    """

    llm: BaseLLM
    def_feature_chain: LLMChain
    as_json: bool = False
    verbose: bool = False

    @root_validator(pre=True)  # type: ignore[misc]
    def _init_def_feature_chain(  # pylint: disable=no-self-argument
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize default memory if not explicitly injected"""
        if "def_feature_chain" not in values:
            values["def_feature_chain"] = DefineFeatureChain(
                llm=values["llm"], verbose=values.get("verbose", False)
            )
        return values

    @property
    def input_keys(self) -> List[str]:
        """Chain inputs

        context : str
            Context of the problem / use case in which a feature definition is being requested
        features : str
            The feature(s) for which a definition is being requested (comma separated)
        project_id : str, optional
            DataRobot project_id; if provided, EDA data will be retrieved from DR if available
            and will be used to attempt to improve data dictionary completions
        """
        return ["context"]

    @property
    def output_keys(self) -> List[str]:
        """Chain outputs

        data_dict : str
            Natural language or json string representation of data dictionary depending
            on how the chain was initialized with parameter 'as_json'
        """
        return ["data_dict"]

    @staticmethod
    def _parse_features(inputs: Dict[str, Any]) -> List[str]:
        """Parse feature names from the data dictionary request"""
        features = [feature.strip() for feature in inputs.get("features", "").split(",")]
        if len(features) == 1 and features[0] == "":
            return []
        else:
            return features

    async def _enrich_feature_names(self, project_id: str, features: list[str]) -> dict[str, str]:
        """Use DataRobot EDA to enrich feature names

        May improve completion quality
        """
        try:
            enriched_feature_names = self._format_dr_feature_data(
                *(await self._get_dr_feature_data(project_id, features))
            )
            if len(features) > 0:
                return {
                    feature: enriched_feature_names[feature]
                    for feature in features
                    if feature in enriched_feature_names
                }
            else:  # return all enriched names
                return enriched_feature_names
        except ValueError:
            return {}

    @staticmethod
    async def _get_dr_feature_data(
        project_id: str, features: list[str]
    ) -> Tuple[pd.DataFrame, str]:
        """Retrieve, filter, and sort features from DR project, retrieve target variable"""
        df = pd.DataFrame(await proj_client.get_features(project_id))
        if features is not None and len(features) > 0:
            df = df[df["name"].isin(features)]
        dr_features = df["name"].to_list()
        coros = [
            retry_if_too_many_attempts(proj_client.get_feature_histogram, project_id, feature)
            for feature in dr_features
        ]
        coros.append(retry_if_too_many_attempts(proj_client.get_project, project_id))
        responses = await asyncio.gather(*coros, return_exceptions=True)
        histograms = [
            pd.DataFrame(resp["plot"]) if not isinstance(resp, BaseException) else pd.DataFrame()
            for resp in responses[:-1]
        ]
        df["histogram"] = pd.Series(histograms, index=df["name"].index)
        return df, responses[-1]["target"]

    @staticmethod
    def _format_data_dict_str(features: List[str], data_dict: Dict[str, str]) -> str:
        """Format data dictionary as a natural language string"""
        dict_str = ""
        for feature in features:
            dict_str += f"{feature}: {data_dict[feature]}\n\n"
        return dict_str

    @staticmethod
    def _format_dr_feature_data(df: pd.DataFrame, target: Optional[str] = None) -> dict[str, str]:
        """Format DR features data as a dict of string prompts"""
        df = df.set_index("name")
        formatted_names = {}
        for name in df.index.to_list():
            if df["featureType"].loc[name] == "Categorical":
                field_context = (
                    "(Categorical; frequent values: '"
                    + "', '".join(
                        df.loc[name]["histogram"]
                        .sort_values("count", ascending=False)["label"]
                        .astype(str)
                        .iloc[:2]
                    )
                    + "')"
                )
            elif df["featureType"].loc[name] in ["Numeric", "Date"]:
                field_context = (
                    "("
                    + df["featureType"].loc[name]
                    + "; median of "
                    + round_sig_figs(df["median"].loc[name])
                    + ", standard deviation of "
                    + round_sig_figs(df["stdDev"].loc[name])
                    + "; frequent values: '"
                    + "', '".join(
                        df.loc[name]["histogram"]
                        .sort_values("count", ascending=False)["label"]
                        .astype(str)
                        .iloc[:2]
                    )
                    + "')"
                )
            else:
                field_context = "(" + df["featureType"].fillna("Unknown").loc[name] + ")"
            if name == target:
                field_context = f"{field_context} [this is the target variable for ML modeling]"
            formatted_names[name] = f"{name} {field_context}"
        return formatted_names

    def _call(self, inputs: Dict[str, str], run_manager: None = None) -> Dict[str, str]:
        """Complete definitions for each feature"""
        features = self._parse_features(inputs)
        enriched_features = (
            create_task_new_thread(
                self._enrich_feature_names(inputs["project_id"], features)
            ).result()
            if "project_id" in inputs
            else {}
        )

        if len(features) == 0 and len(enriched_features) == 0:
            raise ValueError(
                "At least one feature must be requested to generate a data dictionary."
            )
        elif len(features) == 0 and len(enriched_features) > 0:
            # Generate dict for all features in DR project
            features = list(enriched_features.keys())

        data_dict = {
            feature: self.def_feature_chain.predict(
                context=inputs["context"], feature=enriched_features.get(feature, feature)
            )
            for feature in features
        }

        if self.as_json:
            return {"data_dict": json.dumps(data_dict)}
        else:
            return {"data_dict": self._format_data_dict_str(features, data_dict)}

    async def _acall(self, inputs: Dict[str, str], run_manager: None = None) -> Dict[str, str]:
        """Complete definitions for each feature asynchronously

        Due to concurrency, individual completions may not
        benefit from the context of previous definitions.
        """
        features = self._parse_features(inputs)
        enriched_features = (
            await self._enrich_feature_names(inputs["project_id"], features)
            if "project_id" in inputs
            else {}
        )

        if len(features) == 0 and len(enriched_features) == 0:
            raise ValueError(
                "At least one feature must be requested to generate a data dictionary."
            )
        elif len(features) == 0 and len(enriched_features) > 0:
            # Generate dict for all features in DR project
            features = list(enriched_features.keys())

        coros = {
            feature: self.def_feature_chain.apredict(
                context=inputs["context"], feature=enriched_features.get(feature, feature)
            )
            for feature in features
        }
        definitions = await asyncio.gather(*coros.values())
        data_dict = dict(zip(coros.keys(), definitions))

        if self.as_json:
            return {"data_dict": json.dumps(data_dict)}
        else:
            return {"data_dict": self._format_data_dict_str(features, data_dict)}
