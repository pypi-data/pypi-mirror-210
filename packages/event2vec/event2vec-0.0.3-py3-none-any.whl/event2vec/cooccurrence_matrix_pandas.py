import json
import os
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from loguru import logger
from scipy.sparse import csr_matrix, save_npz
from sklearn.feature_extraction.text import CountVectorizer

from event2vec.utils import (
    WINDOW_BACKWARD_LABEL,
    WINDOW_CENTER_LABEL,
    _get_window,
)


def build_cooccurrence_matrix_pd(
    events: pd.DataFrame,
    output_dir: str = None,
    radius_in_days: int = 30,
    window_orientation: str = "center",
    colname_concept: str = "event_source_concept_id",
) -> Tuple[np.array, np.array, Dict]:
    """
    Pandas method for building the cooccurrence matrix in-memory.

    Parameters
    ----------
    events : DataFrame
        _description_
    output_dir : str, optional
        _description_, by default None
    radius_in_days : int, optional
        _description_, by default 30
    window_orientation : str, optional
        _description_, by default "center"
    colname_concept : str, optional
        _description_, by default "event_source_concept_id"

    Returns
    -------
    Tuple[np.array, np.array, Dict]
        _description_
    """
    window_start, window_end = _get_window(
        radius_in_days=radius_in_days,
        window_orientation=window_orientation,
        backend="pandas",
    )
    window = window_end - window_start
    if window_orientation == WINDOW_CENTER_LABEL:
        center = True
    elif window_orientation == WINDOW_BACKWARD_LABEL:
        center = False
    else:
        raise ValueError(
            f"Choose window_orientation in {[WINDOW_CENTER_LABEL, WINDOW_BACKWARD_LABEL]}"
        )
    events_sorted = events.sort_values(["person_id", "start"])
    events_in_window = events_sorted.groupby("person_id")[
        [colname_concept, "start"]
    ].rolling(
        on="start", window=str(window) + "D", center=center, closed="both"
    )
    sep_tok = "<SEP>"
    windowed_events = [
        sep_tok.join(w.tolist()) for w in events_in_window[colname_concept]
    ]
    # TODO: we can do better than joining the word and then making the
    # countvectorizer split them. Eg. build a dummy analyzer that does nothing
    transformer = CountVectorizer(analyzer=lambda x: x.split(sep_tok))
    logger.info("Fit, transform events with count vectorizer model")
    sparse_counts = transformer.fit_transform(windowed_events)
    logger.info(f"Vocabulary of length {len(transformer.vocabulary_)}")
    encoder = transformer.vocabulary_
    vocabulary_size = len(encoder.keys())
    # TODO: is it less efficient than a join ?
    context_encoded = (
        events_sorted[colname_concept].apply(lambda x: encoder[x]).values
    )
    n_words = sparse_counts.sum(axis=0)
    n_contexts = np.unique(context_encoded, return_counts=True)[1]
    # use ultra fast sparse matrix product
    rows = np.arange(len(context_encoded))
    cols = context_encoded
    values = np.ones(len(context_encoded))
    context_matrix = csr_matrix(
        (values, (rows, cols)),
        shape=(len(context_encoded), vocabulary_size),
    ).transpose()
    sparse_cooccurrence = context_matrix.dot(sparse_counts)
    # Have to withdraw the diagonal to avoid double counting
    cooccurrence_matrix = sparse_cooccurrence - csr_matrix(np.diag(n_contexts))
    if output_dir is not None:
        logger.info(
            f"Saving coocurrence_matrix, event_count and vocabulary at {output_dir}"
        )
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path2matrix = str(Path(output_dir) / "cooccurrence_matrix.npz")
        logger.info(f"Saving cooccurrence matrix as parquet at: {path2matrix}")
        save_npz(path2matrix, cooccurrence_matrix)

        with open(os.path.join(output_dir, "vocabulary.json"), "w") as file:
            json.dump(encoder, file)
        np.save(os.path.join(output_dir, "event_count.npy"), n_contexts)
    return cooccurrence_matrix, n_contexts, encoder
