from typing import List, Union

import numpy as np
import pandas as pd
import scipy.sparse as sp
from loguru import logger
from sklearn.base import BaseEstimator

from event2vec.config import (
    COLNAME_FOLLOWUP_START,
    COLNAME_PERSON,
    COLNAME_SOURCE_CODE,
    COLNAME_START,
    COLNAME_VALUE,
    OBSERVATION_END,
    OBSERVATION_START,
)

# TODO: separate pyspark and pandas scripts
from event2vec.svd_ppmi import event2vec

# TODO: These transformers should  rely on a batch version of sklearn
# Countvectorizer instead of the inefficient make_count.
# This could better exploit the sparsity of the count encoding. I
# could take inspiration from
# https://github1s.com/scikit-learn/scikit-learn/blob/baf828ca1/sklearn/feature_extraction/_dict_vectorizer.py
# and populate only non-null indices.


class EventTransformerMixin:
    """Mixin class for all event transformers that requires y at the transform
    step (to align the person id with the features)."""

    def fit_transform(self, X, y=None, **fit_params):
        """
        Fit to data, then transform it.

        Fits transformer to `X` and `y` with optional parameters `fit_params`
        and returns a transformed version of `X`.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input samples.

        y :  array-like of shape (n_samples,) or (n_samples, n_outputs),
            Target values.

        **fit_params : dict
            Additional fit parameters.

        Returns
        -------
        X_new : ndarray array of shape (n_samples, n_features_new)
            Transformed array.
        """
        # fit method of arity 2 (supervised transformation)

        return self.fit(X, y, **fit_params).transform(X)


class OneHotEvent(EventTransformerMixin, BaseEstimator):
    """
    From a event table, create a vocabulary at fit, and pivot the data for a
    count one-hot encoding, ie. count for each code in the vocabulary, and for
    each patient if the event is present or not.
    """

    def __init__(
        self,
        event: pd.DataFrame,
        n_min_events: int = 10,
        colname_demographics: List[str] = None,
        decay_half_life_in_days: np.array = np.array([0]),
    ) -> None:
        self.event = event
        self.n_min_events = n_min_events
        self.colname_demographics = colname_demographics
        self.decay_half_life_in_days = decay_half_life_in_days

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame = None,
        vocabulary: List[str] = None,
        static_features: List[str] = None,
    ):
        X_event = self.event.merge(
            X[[COLNAME_PERSON]], on=COLNAME_PERSON, how="inner"
        )
        self.static_features_ = static_features
        if vocabulary is None:
            self.vocabulary_ = build_vocabulary(
                event=X_event,
                n_min_events=self.n_min_events,
            )
        else:
            self.vocabulary_ = vocabulary
        return self

    def transform(self, X: pd.DataFrame) -> np.array:
        X_event = self.event.merge(
            X[[COLNAME_PERSON]], on=COLNAME_PERSON, how="inner"
        )
        X_counts = make_counts(
            event=X_event,
            person_id=X[[COLNAME_PERSON]],
            decay_half_life_in_days=self.decay_half_life_in_days,
            vocabulary=self.vocabulary_,
            sparse=True,
        ).toarray()

        X_columns = []
        for decay in self.decay_half_life_in_days:
            for code_ in self.vocabulary_:
                X_columns.append(f"{code_}__decay_{decay}")

        X_df = pd.DataFrame(X_counts, columns=X_columns)
        if self.static_features_ is not None:
            X_df = pd.concat([X[self.static_features_], X_df], axis=1)

        return X_df


class Event2vecFeaturizer(EventTransformerMixin, BaseEstimator):
    """
    Transformer for the event2vec model.
    """

    def __init__(
        self,
        event: pd.DataFrame,
        output_dir: str = None,
        colname_code: str = COLNAME_SOURCE_CODE,
        colname_demographics: List[str] = None,
        window_radius_in_days=30,
        window_orientation: str = "center",
        matrix_type: str = "numpy",
        backend="pandas",
        d: int = 300,
        smoothing_factor: float = 0.75,
        k: int = 1,
        n_min_events: int = 10,
        decay_half_life_in_days: np.array = np.array([0]),
    ) -> None:
        self.event = event
        self.output_dir = output_dir
        self.colname_code = colname_code
        self.window_orientation = window_orientation
        self.window_radius_in_days = window_radius_in_days
        self.matrix_type = matrix_type
        self.backend = backend
        self.d = d
        self.smoothing_factor = smoothing_factor
        self.k = k
        self.n_min_events = n_min_events
        self.colname_demographics = colname_demographics
        self.decay_half_life_in_days = decay_half_life_in_days

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame = None,
        vocabulary: List[str] = None,
        static_features: List[str] = None,
    ):
        X_event = self.event.merge(
            X[[COLNAME_PERSON]], on=COLNAME_PERSON, how="inner"
        )
        self.static_features_ = static_features
        if vocabulary is None:
            self.vocabulary_ = build_vocabulary(
                event=X_event,
                n_min_events=self.n_min_events,
            )
        else:
            self.vocabulary_ = vocabulary
        restricted_event = restrict_to_vocabulary(
            event=X_event,
            vocabulary=self.vocabulary_,
        )
        embedding = event2vec(
            events=restricted_event,
            output_dir=self.output_dir,
            colname_concept=self.colname_code,
            window_radius_in_days=self.window_radius_in_days,
            window_orientation=self.window_orientation,
            matrix_type=self.matrix_type,
            backend=self.backend,
            d=self.d,
            smoothing_factor=self.smoothing_factor,
            k=self.k,
        )
        for v in self.vocabulary_:
            if v not in embedding.columns:
                embedding[v] = np.zeros(shape=embedding.shape[0])
        # order the columns to correspond to the vocabulary.
        self.embedding_ = embedding[self.vocabulary_]
        return self

    def transform(self, X: pd.DataFrame) -> np.array:
        # passing the person ids is necessary to aligne make_counts aggregated
        # rows with the person ids in y.
        X_event = self.event.merge(
            X[[COLNAME_PERSON]], on=COLNAME_PERSON, how="inner"
        )
        X_counts = make_counts(
            event=X_event,
            person_id=X[[COLNAME_PERSON]],
            decay_half_life_in_days=self.decay_half_life_in_days,
            vocabulary=self.vocabulary_,
            sparse=True,
        )
        embedding_array_ = sp.csr_matrix(
            self.embedding_[self.vocabulary_].values
        )

        embedding_accumulator = [embedding_array_.transpose()] * len(
            self.decay_half_life_in_days
        )
        embedding_repeated = sp.block_diag(embedding_accumulator)
        X_embedded = X_counts.dot(embedding_repeated)
        X_embedded = X_embedded.toarray()

        X_embedded_columns = []
        embedding_dimension = embedding_array_.shape[0]
        for decay_ in self.decay_half_life_in_days:
            for i in range(embedding_dimension):
                X_embedded_columns.append(f"dim_{i}__decay_{decay_}")
        X_embedded_df = pd.DataFrame(X_embedded, columns=X_embedded_columns)
        if self.static_features_ is not None:
            X_embedded_df = pd.concat(
                [X[self.static_features_], X_embedded_df], axis=1
            )
        return X_embedded_df


class Event2vecPretrained(Event2vecFeaturizer):
    def __init__(
        self,
        event: pd.DataFrame,
        path2embedding: str,
        colname_demographics: str = None,
        colname_code: str = COLNAME_SOURCE_CODE,
        n_min_events: int = 10,
        decay_half_life_in_days: np.array = np.array([0]),
    ) -> None:
        self.event = event
        self.path2embedding = path2embedding
        self.colname_code = colname_code
        self.n_min_events = n_min_events
        self.colname_demographics = colname_demographics
        self.decay_half_life_in_days = decay_half_life_in_days
        self.embedding = pd.read_parquet(self.path2embedding)

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame = None,
        vocabulary: List[str] = None,
        static_features: List[str] = None,
    ):
        X_event = self.event.merge(
            X[[COLNAME_PERSON]], on=COLNAME_PERSON, how="inner"
        )
        self.static_features_ = static_features
        if vocabulary is None:
            vocabulary = build_vocabulary(
                event=X_event,
                n_min_events=self.n_min_events,
            )
        self.vocabulary_ = list(
            set(self.embedding.columns).intersection(set(vocabulary))
        )
        #
        self.embedding_ = self.embedding
        return self


## Utils ##
def build_vocabulary(
    event: pd.DataFrame,
    colname_code: str = COLNAME_SOURCE_CODE,
    n_min_events: int = 10,
) -> List:
    n_event_by_code = (
        event[colname_code]
        .value_counts()
        .to_frame(name="n_events")
        .reset_index()
        .rename(columns={"index": colname_code})
    )
    restricted_codes = n_event_by_code[
        n_event_by_code["n_events"] >= n_min_events
    ]
    return restricted_codes[colname_code].values


def restrict_to_vocabulary(
    event: pd.DataFrame,
    vocabulary: List,
    colname_code: str = COLNAME_SOURCE_CODE,
) -> pd.DataFrame:
    restricted_event = event.merge(
        pd.DataFrame(vocabulary, columns=[colname_code]),
        on=colname_code,
        how="inner",
    )
    return restricted_event


def get_feature_sparsity(X: np.array):  # pragma: no cover
    return (X == 0).sum() / (X.shape[0] * X.shape[1])


def _assert_event_columns(
    event: pd.DataFrame, other_required_columns: List[str] = None
):
    """Check that the event table has the required columns.

    Args:
        event (pd.DataFrame): _description_
        other_required_columns (List[str], optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
    """
    expected_columns = [COLNAME_PERSON, COLNAME_SOURCE_CODE, COLNAME_START]
    if other_required_columns is not None:
        expected_columns += other_required_columns
    missing_columns = set(expected_columns).difference(set(event.columns))
    if len(missing_columns) > 0:
        raise ValueError(
            f"Missing columns {missing_columns} in the event table."
        )


# function tested in the test_experiences.py
def make_counts(
    event: pd.DataFrame,
    person_id: pd.DataFrame,
    decay_half_life_in_days: np.array = np.array([0, 7]),
    vocabulary: List[str] = None,
    sparse: bool = True,
) -> Union[np.array, sp.csr_matrix]:  # pragma: no cover
    """Count the event by person and by code with an option to weigth
    exponentially the counts with respect to the start of followup date.

    The exponential decay is parametrized by a half-life.

    Args:
        event (pd.DataFrame): _description_
        colname_code (str, optional): _description_. Defaults to COLNAME_SOURCE_CODE.
        decay_half_life_in_days (List[int], optional): _description_. Defaults to [0, 7].
        vocabulary (str, optional): _description_. Defaults to None.
        batch (int, optional): Allow to batch the . Defaults to 5000.
    Raises:
        ValueError: _description_

    Returns:
        Tuple(
            Features: _description_,
            person: _description_
        )
    """

    _assert_event_columns(
        event, other_required_columns=[COLNAME_FOLLOWUP_START]
    )

    if vocabulary is None:
        vocabulary = event[COLNAME_SOURCE_CODE].value_counts().index.values
    X_accumulator = []
    event[COLNAME_VALUE] = 1
    event = person_id[[COLNAME_PERSON]].merge(
        event,
        on=COLNAME_PERSON,
        how="inner",
    )
    event["delta_to_followup"] = (
        pd.to_datetime(event[COLNAME_FOLLOWUP_START])
        - pd.to_datetime(event[COLNAME_START])
    ).astype("timedelta64[D]")
    for half_life in decay_half_life_in_days:
        if half_life < 0:
            raise ValueError(f"half_life should be positive, got {half_life}")
        # not necessary to set as a variable
        if half_life > 0:
            event[COLNAME_VALUE] = np.exp(
                -event["delta_to_followup"] / half_life
            )
        decayed_X = get_event_aggregation(
            event=event,
            aggregation_periods="100",
            aggregation_functions=[sum],
            aggregation_col=COLNAME_PERSON,
            vocabulary=vocabulary,
            eps=0,
        )
        decayed_X.columns = [
            col.replace("__sum__p100", "") for col in decayed_X.columns
        ]
        decayed_X = decayed_X[vocabulary]
        decayed_X.columns = [
            col + f"_count_decay_{half_life}" for col in decayed_X.columns
        ]
        # size N x vocabulary
        decayed_X_aligned = (
            person_id[[COLNAME_PERSON]]
            .merge(decayed_X, on=COLNAME_PERSON, how="left")
            .fillna(0)
            .set_index(COLNAME_PERSON)
        )
        if sparse:
            decayed_X_aligned = sp.csr_matrix(decayed_X_aligned)
        X_accumulator.append(decayed_X_aligned)
    if sparse:
        X = sp.hstack(X_accumulator)
    else:
        X = np.concatenate(X_accumulator, axis=1)
    return X


PERIOD_MAP = {"all": [100, 10, 25, 50, -10, -25, -50], "100": [100]}


def get_event_aggregation(
    event: pd.DataFrame,
    aggregation_periods: str = "100",
    aggregation_functions: List = None,
    aggregation_col: str = COLNAME_PERSON,
    vocabulary: List[str] = None,
    eps=1e-6,
) -> pd.DataFrame:
    """
    Compute aggregate statistics by patient trajectory and chosen events over
    different subsequences of the stay


    Parameters
    ----------
    event : pd.DataFrame
        _description_
    aggregation_periods : str, optional
        _description_, by default "all"
    aggregation_functions : List, optional
        _description_, by default None
    aggregation_col : str, optional
        By default, aggregate on COLNAME_PERSON, but could change the key.
    vocabulary : str, optional
        Details the code vocabulary taken into account, by default None so it is computed over all codes.
    eps : _type_, optional
        _description_, by default 1e-6

    Returns
    -------
    pd.DataFrame
        _description_
    """
    _assert_event_columns(
        event, other_required_columns=[COLNAME_VALUE, aggregation_col]
    )
    # TODO: truncation time should be computed from events
    if aggregation_periods not in PERIOD_MAP.keys():
        raise ValueError(f"Supported aggregation periods are {PERIOD_MAP}")
    fake_lines = []

    # need to fill the value for end of events
    if vocabulary is not None:
        code_whitelist = vocabulary.copy()
        event_restricted = restrict_to_vocabulary(
            event=event, vocabulary=code_whitelist
        )
    else:
        code_whitelist = event[COLNAME_SOURCE_CODE].value_counts().index.values
        event_restricted = event
    for code in code_whitelist:
        fake_line = event.iloc[0].copy()
        fake_line[COLNAME_PERSON] = -1
        fake_line[COLNAME_SOURCE_CODE] = code
        fake_lines.append(fake_line)
    # pandas magic: the casting is necessary to avoid type error in the groupby operation
    fake_lines = pd.concat(fake_lines, axis=1).transpose()
    if aggregation_functions is None:
        aggregation_functions = [np.min, np.max, np.mean, np.std, len]
        statistics_names = ["min", "max", "mean", "std", "skew", "count"]
    elif type(aggregation_functions) == list:
        statistics_names = [func.__name__ for func in aggregation_functions]
    statistics_agg = [
        pd.NamedAgg(COLNAME_VALUE, func) for func in aggregation_functions
    ]
    statistics_dict = dict(zip(statistics_names, statistics_agg))
    periods = PERIOD_MAP[aggregation_periods]
    for sub_period in periods:
        if (sub_period <= -100) | (sub_period > 100):
            raise ValueError(
                f"period is a percentage and should be in ]-100, 100], got {sub_period}"
            )
    # add the delta observation as the difference between first and last
    # event observed by person
    first_event_datetime = (
        event_restricted.sort_values(COLNAME_START)
        .groupby(aggregation_col)
        .agg(**{OBSERVATION_START: pd.NamedAgg(COLNAME_START, "first")})
        .reset_index()
    )
    last_event_datetime = (
        event_restricted.sort_values(COLNAME_START)
        .groupby(aggregation_col)
        .agg(**{OBSERVATION_END: pd.NamedAgg(COLNAME_START, "last")})
        .reset_index()
    )
    events_of_interest = event_restricted.merge(
        first_event_datetime, on=aggregation_col, how="inner"
    ).merge(last_event_datetime, on=aggregation_col, how="inner")

    events_of_interest["observation_delta"] = (
        events_of_interest[OBSERVATION_END]
        - events_of_interest[OBSERVATION_START]
    ).astype("timedelta64[s]")
    X = []
    for sub_period in periods:
        logger.info(f"Computing period {sub_period}")
        events_of_interest["period_span_second"] = (
            events_of_interest["observation_delta"] * sub_period / 100
        )
        if sub_period >= 0:
            mask = (
                (
                    pd.to_datetime(events_of_interest[COLNAME_START])
                    - pd.to_datetime(events_of_interest[OBSERVATION_START])
                ).astype("timedelta64[s]")
                >= -eps
            ) & (
                (
                    pd.to_datetime(events_of_interest[COLNAME_START])
                    - pd.to_datetime(events_of_interest[OBSERVATION_START])
                ).astype("timedelta64[s]")
                <= (events_of_interest["period_span_second"] + eps)
            )
        else:
            mask = (
                (
                    pd.to_datetime(events_of_interest[COLNAME_START])
                    - pd.to_datetime(events_of_interest[OBSERVATION_START])
                ).astype("timedelta64[s]")
                >= (
                    (
                        events_of_interest["observation_delta"]
                        + events_of_interest["period_span_second"]
                    )
                    - eps
                )
            ) & (
                (
                    pd.to_datetime(events_of_interest[COLNAME_START])
                    - pd.to_datetime(events_of_interest[OBSERVATION_END])
                ).astype("timedelta64[s]")
                <= eps + events_of_interest["observation_delta"]
            )
        period_events = events_of_interest.loc[mask, :]
        period_events = pd.concat((period_events, fake_lines), axis=0)
        period_statistics = (
            period_events.groupby(by=[aggregation_col, COLNAME_SOURCE_CODE])
            .agg(**statistics_dict)
            .reset_index()
        )
        col_names = period_statistics[COLNAME_SOURCE_CODE].unique()
        period_statistics = period_statistics.pivot(
            index=aggregation_col,
            columns=COLNAME_SOURCE_CODE,
            values=statistics_names,
        )
        period_statistics.columns = np.array(
            [
                [
                    col + "__" + stat_name + "__" + f"p{sub_period}"
                    for col in col_names
                ]
                for stat_name in statistics_names
            ]
        ).flatten()
        X.append(period_statistics)
    X = pd.concat(X, axis=1)
    return X.drop(-1, axis=0, errors="ignore")
