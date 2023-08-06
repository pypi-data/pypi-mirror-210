import json
from itertools import chain
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pyspark.ml.feature as ml_feature
import pyspark.sql.functions as func
from loguru import logger
from pyspark.mllib.linalg import DenseVector
from pyspark.sql import DataFrame, SparkSession, Window
from scipy.sparse import save_npz

from event2vec.utils import WINDOW_CENTER_LABEL, _get_window

"""
Spark implementation to build large cooccurrence matrix.
"""


def build_cooccurrence_matrix_spark(
    events: DataFrame,
    output_dir: str = None,
    radius_in_days: int = 30,
    window_orientation: str = WINDOW_CENTER_LABEL,
    matrix_type: str = "numpy",
    colname_concept: str = "event_source_concept_id",
) -> Tuple[np.array, np.array, Dict]:  # pragma: no cover
    """
    Description: Leverage spark backend to compute cooccurrence matrix for an
    event table.

    :param events: event dataframe
    :param output_dir:
    :param radius_in_days: size of the context window in days, this is to be thought as the radius
    around the central word of reference. Depending of the orientation of the window, the size of
    window will be 2 * radius_in_days if centered
    :param window_orientation: choose position of the reference word in the context window:
        ['centered', 'future'], this changes the focus of the co-occurrence matrix.
        NB : The future configuration leads to an asymetric cooccurrence matrix.
    :param matrix_type:
    :return:
        - cooccurrence_matrix, matrix of cooccurrence of size VxV  where V is the vocabulary size
         with M[i, j] = #|i and j occurs in a window of size window_in_days|
        - event_count, array of size V with the number of single occurrence of each word
        - label2ix, dictionary of size V giving the correspondence between a word and its index in
        the matrix
    """

    window_start, window_end = _get_window(
        radius_in_days=radius_in_days,
        window_orientation=window_orientation,
        backend="spark",
    )
    # little hack of the rangeBetween function
    w = (
        Window.partitionBy("person_id")
        .orderBy(func.col("start").cast("long"))
        .rangeBetween(window_start, window_end)
    )
    events_in_window = events.withColumn(
        "cooccurrence", func.collect_list(func.col(colname_concept)).over(w)
    )

    codes_vectorizer = ml_feature.CountVectorizer(
        inputCol="cooccurrence", outputCol="cooccurrence_ohe", minDF=0
    )

    logger.info("Fit count vectorizer model")
    codes_vectorizer_model = codes_vectorizer.fit(events_in_window)
    logger.info(
        "Vocabulary of length {}".format(
            len(codes_vectorizer_model.vocabulary)
        )
    )
    logger.info("Transform events with count vectorizer model")
    events_ohe = codes_vectorizer_model.transform(events_in_window)
    label2ix = {
        label: i
        for (label, i) in zip(
            codes_vectorizer_model.vocabulary,
            range(len(codes_vectorizer_model.vocabulary)),
        )
    }
    # adding ix for future reduced key
    mapping_expr = func.create_map(
        [func.lit(x) for x in chain(*label2ix.items())]
    )
    events_ohe_with_ix = events_ohe.withColumn(
        "ix", mapping_expr.getItem(func.col(colname_concept)).cast("int")
    )
    # sort by item ix and get back raw counts (suppres
    # s item ignored by count vectorizer)
    event_count = np.array(
        events_ohe_with_ix.groupBy("ix")
        .count()
        .filter(~func.col("ix").isNull())
        .sort(func.col("ix"))
        .drop("ix")
        .collect()
    ).reshape(-1)

    # aggregate one line per item and sort by item index
    events_ohe_grouped = (
        events_ohe_with_ix.select("ix", "cooccurrence_ohe")
        .rdd.mapValues(lambda v: v.toArray())
        .reduceByKey(lambda x, y: x + y)
        .mapValues(lambda x: DenseVector(x))
        .toDF(["ix", "cooccurrence_ohe"])
    )
    # remove excluded code from count_vectorizer and sort by ix
    events_ohe_grouped_sorted = events_ohe_grouped.filter(
        ~func.col("ix").isNull()
    ).sort(func.col("ix").asc())
    # collect and reshape the cooccurrence matrix
    if matrix_type == "numpy":
        logger.info("Collect co-occurrence matrix as numpy")
        x_3d = np.array(
            events_ohe_grouped_sorted.select("cooccurrence_ohe").collect()
        )
        rows, idx, vocab_size = x_3d.shape
        # Have to withdraw the diagonal to avoid double counting
        cooccurrence_matrix = x_3d.reshape(rows, rows) - np.diag(event_count)

    elif matrix_type == "parquet":
        # user = os.getenv("USER")
        # hdfs_path +
        # hdfs_path = f"hdfs://bbsedsi/user/{user}/"
        # We cut the computation graph by dumping the coocurrence matrix to parquet, then reading it
        spark = SparkSession.builder.getOrCreate()
        path2spark_matrix = str(output_dir) + "/spark_matrix.parquet"

        logger.info(f"Saving cooccurrence matrix at: {path2spark_matrix}")
        events_ohe_grouped_sorted.write.mode("overwrite").parquet(
            path2spark_matrix
        )
        logger.info(f"Saving event count at: {path2spark_matrix}")

        spark.createDataFrame(
            pd.DataFrame({"event_count": event_count})
        ).write.mode("overwrite").parquet(
            str(output_dir) + "/event_count.parquet"
        )
        # TODO: could ty to use [spark.ml.sparse to create sparse
        # matrix](https://spark.apache.org/docs/latest/mllib-dimensionality-reduction.html#svd-example)
        # https://spark.apache.org/docs/latest/api/java/org/apache/spark/ml/linalg/SparseMatrix.html

        # The cooccurrence matrix has to be sorted because it has been saved
        # with random row order depending on the workers.
        matrix_before_stacking = spark.read.parquet(path2spark_matrix).sort(
            "ix"
        )
        cooccurrence_matrix = np.vstack(
            matrix_before_stacking.toPandas()["cooccurrence_ohe"].values
        ) - np.diag(event_count)
    else:
        raise NotImplementedError(
            "Matrix collection should be either numpy or parquet"
        )

    if output_dir is not None:
        logger.info(
            f"Saving coocurrence_matrix, event_count and vocabulary at {output_dir}"
        )
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path2matrix = str(Path(output_dir) / "cooccurrence_matrix.npz")
        logger.info(f"Saving cooccurrence matrix as parquet at: {path2matrix}")
        save_npz(path2matrix, cooccurrence_matrix)

        with open(Path(output_dir) / "vocabulary.json", "w") as file:
            json.dump(label2ix, file)
        np.save(Path(output_dir) / "event_count.npy", event_count)
    return cooccurrence_matrix, event_count, label2ix


def sparse_to_array(v):  # pragma: no cover
    """
    Description: udf to transform to dense vector spark sparse vector
    :param v:
    :return:
    """
    v = DenseVector(v)
    new_array = list([float(x) for x in v])
    return new_array
