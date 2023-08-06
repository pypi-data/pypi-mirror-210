"""
Build the svd ppmi
"""

from datetime import datetime

import numpy as np
import pandas as pd
import scipy.sparse as sp
from loguru import logger
from scipy.sparse.linalg import svds

from event2vec.cooccurrence_matrix_pandas import build_cooccurrence_matrix_pd
from event2vec.utils import WINDOW_BACKWARD_LABEL, WINDOW_CENTER_LABEL


def build_ppmi(
    cooccurrence_matrix: np.array,
    event_count: np.array,
    smoothing_factor: float = 0.75,
    k: int = 1,
) -> np.array:
    """
    Description: Build the pmi matrix from the cooccurrence matrix M:
    $$pmi = log[\frac{p(w,c)}{p(w)p(c)}]$$
    # Take the raw item count as the Z denominator
    # We might try some large definition of context where we throws up from the denominator
    # all self-cooccurrence (ie windows of size 1 with an item alone)
    # Our lines/columns do not sum to 1 because we exclude the column where there are counts of
    # the line item co-occurring with the same occurrence of itself.
    # The diagonal corresponds only to co-occurrences of the item with a different occurrence of
    # itself.
    :param cooccurrence_matrix:
    :param item_count:
    :param smoothing_factor:
    :param k: shift value, default 1 which is log(1) = 0 shift.
    :return:
    """

    total_event_count = event_count.sum()
    cooccurrence_ratio = cooccurrence_matrix / total_event_count
    item_ratio = (event_count / total_event_count) ** smoothing_factor
    inverse_item_ratio = 1 / item_ratio
    pmi_matrix = np.log(
        cooccurrence_ratio * np.outer(inverse_item_ratio, inverse_item_ratio)
    )
    ppmi = pmi_matrix - np.log(k)
    ppmi[ppmi <= 0] = 0

    return ppmi


def build_embeddings(
    ppmi: np.array, d: int, window_orientation="center", sparse: bool = True
):
    """
    TODO should use pyspark.mlib if the matrix is too big for numpy
    Description: perform symetric singular value reconstruction
    :param window_orientation: choose position of the reference word in the context window:
        ['centered', 'future'], this changes the focus of the co-occurrence matrix.
        NB : The future configuration leads to an asymetric cooccurrence matrix.
    :param ppmi:
    :param d:
    :return:
    """
    if window_orientation == WINDOW_CENTER_LABEL:
        pass
    elif window_orientation == WINDOW_BACKWARD_LABEL:
        # TODO: I think that the symetrization is not necessary. A symmetric ppmi means word and context
        # embeddings are the same. We could use different ones.
        # Symetrization of the cooccurrence matrix
        ppmi = (ppmi + np.transpose(ppmi)) / 2
    else:
        raise ValueError(
            f"Choose window_orientation in {[WINDOW_CENTER_LABEL, WINDOW_BACKWARD_LABEL]}"
        )
    if d > ppmi.shape[0]:
        raise Exception(
            "Continuous vector dimension should be lower than vocabulary size!"
        )
    # TODO: Why not using [sklearn truncated
    # svd ?](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html)

    if sparse:
        sparse_ppmi = sp.csr_matrix(ppmi)
        u_d, s_d, v_d = svds(sparse_ppmi, k=d)
    else:
        u, s, v = np.linalg.svd(ppmi)
        u_d = u[:, :d]
        v_d = v[:d, :]
        s_d = s[:d]
    embeddings = u_d.dot(np.diag(np.sqrt(s_d))) + v_d.transpose().dot(
        np.diag(np.sqrt(s_d))
    )

    return embeddings


# TODO: test for the existence for required columns instead of having an argument for colname_concept
def event2vec(
    events=pd.DataFrame,
    output_dir: str = None,
    colname_concept: str = "event_source_concept_id",
    window_radius_in_days=30,
    window_orientation: str = "center",
    matrix_type: str = "numpy",
    backend="pandas",
    d: int = 300,
    smoothing_factor: float = 0.75,
    k: int = 1,
):
    """
    Wrapper around build_cooccurrence_matrix, build_ppmi and build_embeddings to
    create concept embeddings from raw event codes.

    Args:
        events (_type_, optional): _description_. Defaults to DataFrame.
        output_dir (str, optional): _description_. Defaults to None.
        colname_concept (str, optional): _description_. Defaults to
        "event_source_concept_id". window_radius_in_days (int, optional):
        _description_. Defaults to 30. window_orientation (str, optional):
        _description_. Defaults to "centered". matrix_type (str, optional):
        _description_. Defaults to "numpy". d (int, optional): _description_.
        Defaults to 300. smoothing_factor (float, optional): _description_.
        Defaults to 0.75. k (int, optional): _description_. Defaults to 1.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if backend == "spark":
        from event2vec.cooccurrence_matrix_spark import (
            build_cooccurrence_matrix_spark,
        )

        (
            cooccurrence_matrix,
            event_count,
            label2ix,
        ) = build_cooccurrence_matrix_spark(
            events,
            output_dir=output_dir,
            radius_in_days=window_radius_in_days,
            colname_concept=colname_concept,
            matrix_type=matrix_type,
        )
    elif backend == "pandas":
        (
            cooccurrence_matrix,
            event_count,
            label2ix,
        ) = build_cooccurrence_matrix_pd(
            events,
            output_dir=output_dir,
            radius_in_days=window_radius_in_days,
            colname_concept=colname_concept,
        )
    if window_orientation not in [WINDOW_BACKWARD_LABEL, WINDOW_CENTER_LABEL]:
        raise ValueError(
            f"Choose window_orientation in {[WINDOW_BACKWARD_LABEL, WINDOW_CENTER_LABEL]}"
        )
    t_0 = datetime.now()
    logger.info(
        f"Shape of the co-occurrence matrix: {cooccurrence_matrix.shape}"
    )
    logger.info(
        f"Build PPMI with smoothing factor {smoothing_factor} and shift {k}"
    )
    ppmi = build_ppmi(
        cooccurrence_matrix=cooccurrence_matrix,
        event_count=event_count,
        smoothing_factor=smoothing_factor,
        k=k,
    )
    logger.info("PPMI factorization with SVD")
    event_embeddings = build_embeddings(
        ppmi=ppmi, d=d, window_orientation=window_orientation
    )
    t_1 = datetime.now()
    logger.info(
        f"Embeddings of dimension {d} created from the co-occurrence matrix in {t_1 - t_0}"
    )
    embeddings_dict = dict(zip(label2ix.keys(), np.array(event_embeddings)))

    embeddings_df = pd.DataFrame.from_dict(embeddings_dict, orient="columns")
    if output_dir is not None:
        path2emb = (
            output_dir
            / f"tuto_snds2vec_alpha={smoothing_factor}_k={k}_d={d}.parquet"
        )
        logger.info(f"Saving embeddings as parquet dataframe at {path2emb}")
        embeddings_df.to_parquet(path2emb)
    return embeddings_df
