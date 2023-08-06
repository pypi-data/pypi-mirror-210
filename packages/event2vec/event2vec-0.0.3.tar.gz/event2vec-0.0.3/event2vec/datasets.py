import pandas as pd

from event2vec.config import (
    COLNAME_FOLLOWUP_START,
    COLNAME_PERSON,
    COLNAME_SOURCE_CODE,
    COLNAME_START,
)
from event2vec.utils import EventCohort


def get_small_cohort():  # pragma: no cover
    """Small cohort for testing and tutorials"""
    person = pd.DataFrame(
        {
            COLNAME_PERSON: [2, 3],
            "y": [0, 1],
            COLNAME_FOLLOWUP_START: [
                "2021-01-08 00:00:00",
                "2021-01-18 00:00:00",
            ],
        }
    )
    person[COLNAME_FOLLOWUP_START] = pd.to_datetime(
        person[COLNAME_FOLLOWUP_START]
    )
    event = pd.DataFrame(
        {
            COLNAME_PERSON: [2, 3, 3, 2, 2, 2, 2],
            COLNAME_SOURCE_CODE: [
                "HBBD404",
                "A04AA01",
                "A04AA01",
                "HBBD404",
                "H353",
                "DAQL009",
                "DAQL009",
            ],
            COLNAME_START: [
                "2021-01-05 00:00:00",
                "2021-01-15 00:00:00",
                "2021-01-15 00:00:00",
                "2019-05-24 19:19:14",
                "2017-05-02 00:45:25",
                "2019-09-21 05:43:03",
                "2021-01-02 23:34:59",
            ],
            COLNAME_FOLLOWUP_START: [
                "2021-01-08 00:00:00",
                "2021-01-18 00:00:00",
                "2021-01-18 00:00:00",
                "2021-01-08 00:00:00",
                "2021-01-08 00:00:00",
                "2021-01-08 00:00:00",
                "2021-01-08 00:00:00",
            ],
        },
    )
    event[COLNAME_START] = pd.to_datetime(event[COLNAME_START])
    event[COLNAME_FOLLOWUP_START] = pd.to_datetime(
        event[COLNAME_FOLLOWUP_START]
    )
    return EventCohort(person=person, event=event)
