from databricks import koalas as ks

# might be cool to remove this one (but don't want to put the 30 lines of codes here....
from deepacau.io import load_spark_database
from eds_scikit import improve_performances
from eds_scikit.io import HiveData
from edstoolbox import SparkApp
from loguru import logger
from pyspark.sql import SparkSession

from event2vec.config import DIR2DATA, DIR2RESULTS
from event2vec.cooccurrence_matrix_spark import event2vec

app = SparkApp("event2vec")


@app.submit
def run(spark, sql, config):
    """
    Submit event2vec on APHP pyspark cluster for i2b2 data format:
    - cd to event2vec root folder
    - run `eds-toolbox spark submit --config bin/config.cfg --log-path logs bin/submit_i2b2.py`

    Warning: the local file system is not accessible for write access for the client, so the hdfs file system will be used (supposingly faster)

    More documentation at : https://datasciencetools-pages.eds.aphp.fr/edstoolbox/cli/spark/

    Arguments
    ---------
    spark :
        Spark session object, for querying tables
    sql :
        Spark sql object, for querying tables
    config :
        Dictionary containing the configuration
    """

    event2vec_config = config["event2vec"]

    alpha = event2vec_config["alpha"]
    k = event2vec_config["k"]
    d = event2vec_config["d"]
    window_radius_in_days = event2vec_config["window_radius_in_days"]
    #
    cse_id = event2vec_config["cse_id"]
    cse_database = event2vec_config["cse_database"]
    expe_name = event2vec_config["expe_name"]
    dir2output = expe_name
    logger.info(f"Saving directory is hdfs {dir2output}")

    observations_tables = {
        "i2b2_observation_cim10": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
        "i2b2_observation_ccam": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
        "i2b2_observation_lab": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
        "i2b2_observation_med": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
        "i2b2_observation_microbio": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
        "i2b2_observation_ufr": {
            "concept_cd": "concept_id",
            "start_date": "start",
            "patient_num": "person_id",
        },
    }
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark._jsc.hadoopConfiguration()
    )
    hdfs_url = f"hdfs://bbsedsi/user/{cse_id}/"
    existing_events = fs.exists(
        spark._jvm.org.apache.hadoop.fs.Path(
            hdfs_url + dir2output + "/events.parquet"
        )
    )
    if not existing_events:
        data = load_spark_database(cse_database)
        events_all = []
        for table_name, columns_dict in observations_tables.items():
            df = (
                data[table_name]
                .rename(columns=columns_dict)
                .astype({"concept_id": str})
            )
            df["data_source"] = table_name
            events_all.append(
                df[["person_id", "data_source", "start", "concept_id"]]
            )

        events_all = ks.concat(events_all, axis=0).to_spark().repartition(10)
        logger.info(f"Number of events: {events_all.count()}")
        n_unique_all = (
            events_all.to_koalas()
            .groupby(["data_source", "concept_id"])["start"]
            .count()
            .reset_index()
            .rename(columns={"start": "count"})
            .to_pandas()
            .sort_values("count")
        )
        vocabulary_size = len(n_unique_all)
        logger.info(f"Number of distinct events: {vocabulary_size}")
        # prepare vocabulary for event2vec
        concepts = data["i2b2_ontology"].rename(
            columns={"c_name": "concept_name", "c_basecode": "concept_code"}
        )
        concepts["concept_id"] = concepts["concept_code"]

        vocabulary_w_label = (
            ks.DataFrame(n_unique_all)
            .merge(
                concepts[["concept_id", "concept_name", "concept_code"]],
                on="concept_id",
                how="left",
            )
            .to_pandas()
        )
        vocabulary_w_label["vocabulary_id"] = vocabulary_w_label[
            "concept_id"
        ].apply(lambda x: x.split(":")[0])

        k_private = 50
        vocabulary_w_label_private = vocabulary_w_label.loc[
            vocabulary_w_label["count"] >= k_private
        ]
        logger.info(
            f"Number of distinct restricted events: {len(vocabulary_w_label_private)}"
        )
        ks.DataFrame(vocabulary_w_label_private).to_spark().write.csv(
            dir2output + "/concept_labels.csv"
        )

        events = (
            events_all.to_koalas()
            .merge(
                ks.DataFrame(vocabulary_w_label_private)[["concept_id"]],
                on="concept_id",
                how="inner",
            )
            .to_spark()
        )

        events.repartition(20).write.mode("overwrite").parquet(
            dir2output + "/events.parquet"
        )
        events = spark.read.parquet(dir2output + "/events.parquet")
    else:
        logger.info("Logging precomputed events")
        events = spark.read.parquet(dir2output + "/events.parquet")
        logger.info(f"Number of events: {events.count()}")

    embeddings, label2ix = event2vec(
        events=events,
        output_dir=dir2output,
        colname_concept="concept_id",
        window_orientation="centered",
        window_radius_in_days=window_radius_in_days,
        d=d,
        smoothing_factor=alpha,
        k=k,
        matrix_type="parquet",
    )


if __name__ == "__main__":
    app.run()
