from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from ..base import EventDataFrame


class EventFilter(ABC):
    @abstractmethod
    def get_event_start_times(self, y: pd.Series) -> pd.DatetimeIndex:
        raise NotImplementedError


class Labeler(ABC):
    @abstractmethod
    def label_events(
        self, event_start_times: pd.DatetimeIndex, y: pd.Series
    ) -> EventDataFrame:
        raise NotImplementedError

    def get_all_possible_labels(self) -> List[int]:
        raise NotImplementedError
