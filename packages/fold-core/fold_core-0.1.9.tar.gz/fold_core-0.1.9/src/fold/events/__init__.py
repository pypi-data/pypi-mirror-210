# Copyright (c) 2022 - Present Myalo UG (haftungbeschränkt) (Mark Aron Szulyovszky, Daniel Szemerey) <info@dreamfaster.ai>. All rights reserved. See LICENSE in root folder.
from __future__ import annotations

from typing import Callable, List, Optional, Tuple

import pandas as pd

from fold.base.classes import Extras

from ..base import Artifact, Composite, Pipeline, Pipelines, T, Transformation, fit_noop
from ..utils.dataframe import concat_on_columns
from ..utils.list import wrap_in_double_list_if_needed, wrap_in_list
from .base import EventFilter, Labeler
from .filters import EveryNth, NoFilter
from .labeling import BinarizeFixedForwardHorizon


def CreateEvents(
    wrapped_pipeline: Pipeline,
    labeler: Labeler,
    filter: EventFilter = NoFilter(),
) -> _CreateEvents:
    return _CreateEvents(wrapped_pipeline, _EventLabelWrapper(filter, labeler))


class _CreateEvents(Composite):
    properties = Composite.Properties(primary_only_single_pipeline=True)
    name = "CreateEvents"
    transformation: List[_EventLabelWrapper]

    def __init__(
        self,
        wrapped_pipeline: Pipeline,
        event_label_wrapper: _EventLabelWrapper,
    ) -> None:
        self.wrapped_pipeline = wrap_in_double_list_if_needed(wrapped_pipeline)
        self.transformation = wrap_in_list(event_label_wrapper)

    def get_children_primary(self) -> Pipelines:
        return self.transformation

    def get_children_secondary(self) -> Optional[Pipelines]:
        return self.wrapped_pipeline

    def preprocess_secondary(
        self,
        X: pd.DataFrame,
        y: T,
        results_primary: List[pd.DataFrame],
        index: int,
        fit: bool,
    ) -> Tuple[pd.DataFrame, T]:
        events = results_primary[0].dropna()
        return X.loc[events.index], events["label"]

    def postprocess_result_secondary(
        self,
        primary_results: List[pd.DataFrame],
        secondary_results: List[pd.DataFrame],
        y: Optional[pd.Series],
        in_sample: bool,
    ) -> pd.DataFrame:
        return secondary_results[0].reindex(y.index)

    def postprocess_artifacts_primary(
        self, artifacts: List[Artifact], extras: Extras
    ) -> pd.DataFrame:
        return concat_on_columns(artifacts)

    def postprocess_artifacts_secondary(
        self, primary_artifacts: pd.DataFrame, secondary_artifacts: List[Artifact]
    ) -> pd.DataFrame:
        return concat_on_columns(
            [primary_artifacts, concat_on_columns(secondary_artifacts)],
        )

    def clone(self, clone_children: Callable) -> _CreateEvents:
        clone = _CreateEvents(
            clone_children(self.wrapped_pipeline),
            clone_children(self.transformation),
        )
        clone.properties = self.properties
        clone.name = self.name
        return clone


class UsePredefinedEvents(Composite):
    properties = Composite.Properties(primary_only_single_pipeline=True)
    name = "UsePredefinedEvents"

    def __init__(
        self,
        wrapped_pipeline: Pipeline,
    ) -> None:
        self.wrapped_pipeline = wrap_in_double_list_if_needed(wrapped_pipeline)

    def get_children_primary(self) -> Pipelines:
        return self.wrapped_pipeline

    def preprocess_primary(
        self, X: pd.DataFrame, index: int, y: T, extras: Extras, fit: bool
    ) -> Tuple[pd.DataFrame, T, Extras]:
        if extras.events is None:
            raise ValueError(
                "You need to pass in `events` for `UsePredefinedEvents` to use when calling train() / backtest()."
            )
        events = extras.events.dropna()
        return X.loc[events.index], events["label"], extras

    def postprocess_result_primary(
        self, results: List[pd.DataFrame], y: Optional[pd.Series]
    ) -> pd.DataFrame:
        return results[0].reindex(y.index)

    def postprocess_artifacts_primary(
        self, artifacts: List[Artifact], extras: Extras
    ) -> pd.DataFrame:
        return extras.events

    def clone(self, clone_children: Callable) -> UsePredefinedEvents:
        clone = UsePredefinedEvents(
            clone_children(self.wrapped_pipeline),
        )
        clone.properties = self.properties
        clone.name = self.name
        return clone


class _EventLabelWrapper(Transformation):
    name = "EventLabelWrapper"
    properties = Transformation.Properties(
        mode=Transformation.Properties.Mode.online,
        requires_X=False,
        _internal_supports_minibatch_backtesting=True,
        memory_size=1,
    )
    last_events: Optional[pd.DataFrame] = None

    def __init__(self, event_filter: EventFilter, labeler: Labeler) -> None:
        self.filter = event_filter
        self.labeler = labeler
        self.name = (
            f"{self.filter.__class__.__name__}-{self.labeler.__class__.__name__}"
        )

    fit = fit_noop
    update = fit

    def transform(
        self, X: pd.DataFrame, in_sample: bool
    ) -> Tuple[pd.DataFrame, Optional[Artifact]]:
        past_y = self._state.memory_y
        original_start_times = self.filter.get_event_start_times(past_y)
        events = self.labeler.label_events(original_start_times, past_y)
        if in_sample is False and events.dropna().empty:
            self.properties.memory_size += 1
        elif in_sample is False and not events.dropna().empty:
            self.properties.memory_size = 1
        return events["label"].to_frame().reindex(X.index), events
