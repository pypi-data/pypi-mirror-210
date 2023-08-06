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
from typing import Any, cast, Dict, List, Optional, Union

import pandas as pd

import datarobotx.client.projects as proj_client
from datarobotx.common import utils
from datarobotx.models.autopilot import AutopilotModel
from datarobotx.models.intraproject import IntraProjectModel
from datarobotx.models.model import Model, ModelOperator

logger = logging.getLogger("drx")


@utils.blank_ipython_display
@utils.hidden_instance_classmethods
class PreviouslyFitModel(AutopilotModel):
    """Helper Class for instantiating a model from an existing project"""

    def __init__(self, project_id: str):
        super().__init__()
        self._project_id = project_id

    async def _fit(  # type: ignore[no-untyped-def]
        self,
        X: Union[pd.DataFrame, str, None],
        *args,
        champion_handler=None,
        **kwargs,
    ) -> None:
        """Updates internal champion model reference

        Parameters
        ----------
        champion_handler : callable
            Function to call to evaluate and update the champion model
        """
        autopilot_done = (
            await proj_client.get_projects_status(self._project_id)
            if self._project_id is not None
            else False
        )
        if not autopilot_done:
            raise ValueError(
                """
                Column reduction is intended to be used on completed automl
                projects. Wait for autopilot to finish modeling before running
                column reduction.
                """
            )
        await self._refresh_leaderboard(callback=champion_handler)


class ColumnReduceModel(IntraProjectModel):
    """
    Column reduction orchestrator

    Iteratively trains challenger models on increasingly column-reduced
    training data until diminishing returns on model performance are
    reached. Uses Feature Importance Rank Ensembling (FIRE) for column
    reduction.

    Delegates training on column reduced data to the provided base model.
    Blenders and frozen models are excluded from champion model consideration.

    Parameters
    ----------
    base_model : AutopilotModel or IntraProjectModel
        Base model to fit on column reduced training data
    ranking_ensemble_size : int, default=5
        Number of top models from the leaderboard to include in the ensemble when
        computing the median feature importance rank for each feature
    initial_retain_ratio : float, default=0.95
        Initial percent (expressed as a decimal) of cumulative feature importance
        to retain when performance column reduction
    initial_lives : int, default=3
        Stopping criteria; number of reduction iterations to complete without
        establishing a new champion model
    """

    def __init__(
        self,
        base_model: Union[AutopilotModel, IntraProjectModel],
        ranking_ensemble_size: int = 5,
        initial_retain_ratio: float = 0.95,
        initial_lives: int = 3,
    ):
        super().__init__(
            base_model,
            ranking_ensemble_size=ranking_ensemble_size,
            initial_retain_ratio=initial_retain_ratio,
            initial_lives=initial_lives,
        )

        self.features = None

    @property
    def _leaderboard(self) -> Optional[list[str]]:
        """Leaderboard for column reduction"""
        return self.__leaderboard

    @_leaderboard.setter
    def _leaderboard(self, value: Optional[list[str]]) -> None:
        self.__leaderboard = value

    @property
    def _best_model(self) -> Optional[Model]:
        """Top of column reducer leaderboard"""
        return super(IntraProjectModel, self)._best_model

    @property
    def features(self) -> Optional[List[str]]:
        """
        List of features used by the current best model

        Returns
        -------
        list
            Column names of features used in current best model
        """
        return cast(Optional[List[str]], self._features)

    @features.setter
    def features(self, value: List[str]) -> None:
        self._features = value

    @classmethod
    def run_column_reduction(
        cls,
        project_id: str,
        ranking_ensemble_size: int = 5,
        initial_retain_ratio: float = 0.95,
        initial_lives: int = 3,
    ) -> ColumnReduceModel:
        """
        Runs feature reduction on the provided project iteratively

        Parameters
        ----------
        project_id : str
            project id of an existing project to fit on column reduced training data
        ranking_ensemble_size : int, default=5
            Number of top models from the leaderboard to include in the ensemble when
            computing the median feature importance rank for each feature
        initial_retain_ratio : float, default=0.95
            Initial percent (expressed as a decimal) of cumulative feature importance
            to retain when performance column reduction
        initial_lives : int, default=3
            Stopping criteria; number of reduction iterations to complete without
            establishing a new champion model

        Returns
        -------
        ColumnReduceModel:
            Model object that can be used to make predictions and deploy models

        Examples
        -------

        >>> import datarobotx as drx
        >>> project_id = "123456"
        >>> colreduce_model = ColumnReduceModel.run_column_reduction(project_id)

        """
        base_model = PreviouslyFitModel(project_id)

        model = cls(
            base_model,
            ranking_ensemble_size=ranking_ensemble_size,
            initial_retain_ratio=initial_retain_ratio,
            initial_lives=initial_lives,
        )
        model._fitting_underway = True
        utils.create_task_new_thread(model._fit(X=None))
        return model

    def fit(self, *args, **kwargs) -> ColumnReduceModel:  # type: ignore[no-untyped-def]
        """
        Fit column-reduced challenger models using the underlying base model

        Parameters
        ----------
        args
            Arguments to be passed to the base model fit()
        kwargs
            Keyword arguments to be passed to the base model fit()

        """
        utils.create_task_new_thread(self._fit(*args, **kwargs))
        return self

    @ModelOperator._with_fitting_underway
    async def _fit(  # type: ignore[no-untyped-def]
        self, X: Optional[Union[pd.DataFrame, str]], *args, **kwargs
    ) -> None:
        """
        Fit base model and iteratively feature reduce, rerun autopilot until
        stopping criteria reached
        """
        logger.info("Fitting base model", extra={"is_header": True})
        champion_handler = kwargs.pop("champion_handler", None)
        await self.base_model._fit(
            X,
            *args,
            champion_handler=partial(self._refresh_leaderboard, callback=champion_handler),
            **kwargs,
        )

        logger.info("Performing column reduction", extra={"is_header": True})
        impacts = await self._get_feature_impacts()
        last_featurelist = cast(List[str], self.features)
        ratio = self._intra_config["initial_retain_ratio"]
        lives = self._intra_config["initial_lives"]

        while lives > 0:
            next_featurelist = self._reduce_features(impacts, ratio)
            if set(next_featurelist) == set(last_featurelist):
                ratio *= ratio
                continue
            assert self._best_model is not None
            last_best_model = self._best_model._model_id
            await self._fit_featurelist(
                next_featurelist,
                lives,
                champion_handler=champion_handler,
            )
            last_featurelist = next_featurelist

            if last_best_model == self._best_model._model_id:
                lives -= 1
                ratio *= ratio
            await self._log_champion(best_model=self._best_model, ascii_art=(lives == 0))
            if lives > 0:
                impacts = await self._get_feature_impacts()

        logger.info("Column reduction complete", extra={"is_header": True})

    async def _refresh_leaderboard(self, callback: Optional[Callable] = None) -> None:  # type: ignore[type-arg]
        """
        Refresh the leaderboard

        May result in a new champion being exposed by this IntraprojectModel for
        predictions, deployment, etc.

        ColumnReduceModel uses a different ranking than the DR leaderboard.

        Parameters
        ----------
        callback : Callable
            If passed, will ensure callback is triggered after updating
        """
        if self._project_id is not None:
            last_best_model = self._best_model
            models_json: List[Dict[str, Any]] = await self._get_models_for_ranking()
            if len(models_json) > 0:
                self._leaderboard = [model["id"] for model in models_json]
                if (
                    last_best_model is None
                    or last_best_model._model_id != self._best_model._model_id  # type: ignore[union-attr]
                ):
                    await self._update_features(models_json[0])
        await super()._refresh_leaderboard(callback=callback)

    async def _update_features(self, model_json: Dict[str, Any]) -> None:
        """Asynchronously update the current best features."""
        fl_json = await proj_client.get_featurelist(
            pid=self._project_id, featurelist_id=model_json["featurelistId"]  # type: ignore[arg-type]
        )
        self.features = fl_json["features"]

    async def _fit_featurelist(
        self, features: List[str], lives: int, champion_handler: Optional[Callable] = None  # type: ignore[type-arg]
    ) -> None:
        """Start autopilot on a new featurelist."""
        fl_id = await proj_client.post_featurelist(
            pid=self._project_id,  # type: ignore[arg-type]
            featurelist_json={
                "name": "Top {n} (Reduced by FIRE)".format(n=len(features)),
                "features": features,
            },
        )

        ap_json = self._dr_config._to_json("post_autopilots")
        ap_json["featurelistId"] = fl_id
        ap_json["blendBestModels"] = False

        await proj_client.post_autopilots(
            pid=self._project_id,  # type: ignore[arg-type]
            ap_json=ap_json,
        )
        logger.info(
            "Running autopilot with top %s features (%s live(s) remaining)...", len(features), lives
        )
        await proj_client.await_autopilot(
            pid=self._project_id,  # type: ignore[arg-type]
            featurelist_id=fl_id,
            champion_handler=partial(self._refresh_leaderboard, callback=champion_handler),
        )

    async def _get_feature_impacts(self) -> pd.DataFrame:
        """
        Retrieve the feature impacts for all models in the rank ensemble.

        Thanks: Vitalii P.
        """
        models = await self._get_models_for_ranking()
        actual_ensemble_size = min(len(models), self._intra_config["ranking_ensemble_size"])
        logger.info("Calculating feature impact for top %s models...", actual_ensemble_size)
        models = [model["id"] for model in models[0:actual_ensemble_size]]
        coros = [
            proj_client.get_feature_impact(pid=self._project_id, model_id=model_id)  # type: ignore[arg-type]
            for model_id in models
        ]
        feature_impact_responses = await asyncio.gather(*coros)

        all_impact = pd.DataFrame()
        for response_dict in feature_impact_responses:
            feature_impact = pd.DataFrame(response_dict["featureImpacts"])
            feature_impact = feature_impact.sort_values(
                by="impactUnnormalized", ascending=False
            ).reset_index(drop=True)
            feature_impact["rank"] = feature_impact.index.values
            all_impact = pd.concat([all_impact, feature_impact], ignore_index=True)
        return all_impact

    @staticmethod
    def _reduce_features(all_impact: pd.DataFrame, ratio: int) -> List[str]:
        """
        Identify the set of features in a DR project that comprise *self.ratio* percent
        of the cumulative permutation importance summed across the top *n* models in the
        project (when ordered by the project loss metric on the validation partition).

        https://www.datarobot.com/blog
        /using-feature-importance-rank-ensembling-fire-for-advanced-feature-selection/

        Returns a list of the top features meeting this criteria

        Thanks: Vitalii P
        """
        all_impact_agg = (
            all_impact.groupby("featureName")[["impactNormalized", "impactUnnormalized"]]
            .sum()
            .sort_values("impactUnnormalized", ascending=False)
            .reset_index()
        )
        all_impact_agg["impactCumulative"] = all_impact_agg["impactUnnormalized"].cumsum()

        total_impact = all_impact_agg["impactCumulative"].max() * ratio
        tmp_fl = list(
            set(
                all_impact_agg[all_impact_agg.impactCumulative <= total_impact][
                    "featureName"
                ].values.tolist()
            )
        )
        n_feats = len(tmp_fl)
        top_ranked_feats = list(
            all_impact.groupby("featureName")
            .median()
            .sort_values("rank")
            .head(n_feats)
            .index.values
        )
        return top_ranked_feats

    async def _get_models_for_ranking(self) -> List[Dict[str, Any]]:
        """
        Retrieve all models from project, remove blenders, frozen models
        and filter to the top n remaining models ordered by the proj loss metric
        on the validation partition.

        Returns a list of model_ids after filtering
        """
        models = await proj_client.get_models(pid=self._project_id)  # type: ignore[arg-type]
        return [
            model  # type: ignore[misc]
            for model in models
            if (
                # ex-blenders
                model["modelCategory"] == "model"  # type: ignore[index]
                and (
                    model["samplePct"] is None or model["samplePct"] <= 65.0  # type: ignore[index, operator]
                )
                and not model["isFrozen"]  # type: ignore[index]
                and "DR Reduced Features M"
                # model-specific auto-featurelists
                not in model["featurelistName"]  # type: ignore[index]
                and "Auto-Tuned Word N-Gram Text" not in model["modelType"]  # type: ignore[index]
            )
        ]
