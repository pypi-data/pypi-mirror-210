from databricks import koalas as ks
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
    Submit event2vec on APHP pyspark cluster for omop data:
    - cd to event2vec root folder
    - run `eds-toolbox spark submit --config bin/config.cfg --log-path logs bin/submit_omop.py `

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

    tables_to_load = {
        "care_site": None,
        "concept": None,
        "condition_occurrence": None,
        "person": None,
        "procedure_occurrence": None,
        "visit_detail": None,
        "visit_occurrence": None,
        "drug_exposure_administration": None,
        "measurement": None,
    }
    data = HiveData(
        database_name=cse_database,
        tables_to_load=tables_to_load,
    )
    observations_tables = {
        "condition_occurrence": {
            "condition_source_concept_id": "concept_id",
            "condition_start_datetime": "start",
        },
        "procedure_occurrence": {
            "procedure_source_concept_id": "concept_id",
            "procedure_datetime": "start",
        },
        "measurement": {
            "measurement_concept_id": "concept_id",
            "measurement_datetime": "start",
        },
        "drug_exposure_administration": {
            "drug_class_source_concept_id": "concept_id",
            "drug_exposure_start_datetime": "start",
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
        events_all = []
        for table_name, columns_dict in observations_tables.items():
            df = (
                data.__getattr__(table_name)
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
            .groupby(["data_source", "concept_id"])
            .count()
            .reset_index()
            .rename(columns={"start": "count"})
            .to_pandas()
            .sort_values("count")
        )
        vocabulary_size = len(n_unique_all)
        logger.info(f"Number of distinct events: {vocabulary_size}")
        vocabulary_restricted = n_unique_all[n_unique_all["count"] >= 10]
        logger.info(
            f"Number of distinct restricted events: {len(vocabulary_restricted)}"
        )

        vocabulary_w_label = (
            ks.DataFrame(vocabulary_restricted)
            .merge(
                data.concept[["concept_id", "concept_name", "concept_code"]],
                on="concept_id",
                how="left",
            )
            .to_pandas()
        )

        events = (
            events_all.to_koalas()
            .merge(
                ks.DataFrame(
                    vocabulary_restricted.loc[
                        ~vocabulary_restricted["concept_id"].isin(["nan", "0"])
                    ]
                ),
                on="concept_id",
            )
            .to_spark()
        )
        events.repartition(10).write.mode("overwrite").parquet(
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
