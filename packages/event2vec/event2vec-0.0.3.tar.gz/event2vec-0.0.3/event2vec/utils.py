from dataclasses import dataclass
from itertools import chain
from typing import List

import pandas as pd


def days_to_seconds(days: int) -> int:
    return days * 86400


def join_lists(list_2d: List[List[str]]) -> List[str]:
    return list(chain(*list_2d))


WINDOW_CENTER_LABEL = "center"
WINDOW_BACKWARD_LABEL = "backward"


def _get_window(radius_in_days: float, window_orientation: str, backend: str):
    """Create the window context for the cooccurrence matrix, adapted for each
    backend: in days for pandas, in seconds for spark.

    Args:
        radius_in_days (float): _description_
        window_orientation (str): _description_
        backend (str): Either pandas or spark

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if backend == "spark":
        # timesecond are necessary for the window function of spark
        radius_ = days_to_seconds(radius_in_days)
        # chose window orientation
    elif backend == "pandas":
        # radius_ = pd.to_timedelta(radius_in_days, unit="d")
        radius_ = radius_in_days
    if window_orientation == WINDOW_CENTER_LABEL:
        window_start = -radius_ / 2
        window_end = radius_ / 2
    elif window_orientation == WINDOW_BACKWARD_LABEL:
        window_start = -radius_
        window_end = 0
    else:
        raise ValueError(
            f"Choose window_orientation in {[WINDOW_CENTER_LABEL, WINDOW_BACKWARD_LABEL]}"
        )
    if backend == "spark":
        window_start = int(window_start)
        window_end = int(window_end)
    return window_start, window_end


@dataclass
class EventCohort:
    person: pd.DataFrame
    event: pd.DataFrame
