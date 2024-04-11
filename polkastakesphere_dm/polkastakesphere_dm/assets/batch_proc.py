import os

from dagster import AssetExecutionContext
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import coalesce
from pyspark.sql.functions import col
from pyspark.sql.functions import concat_ws
from pyspark.sql.functions import count
from pyspark.sql.functions import max
from pyspark.sql.functions import min
from pyspark.sql.functions import month
from pyspark.sql.functions import sha2
from pyspark.sql.functions import to_date
from pyspark.sql.functions import year

from .asset_exec_params import SubstrateExtractParameters


def update_locallake(
    context: AssetExecutionContext, params: SubstrateExtractParameters, spark: SparkSession, src_dataframe: DataFrame
) -> None:
    env_destination_local_path = os.environ.get("PSS_LHOUSE_LEV0_STAKING_INGESTION_SINK")

    context.log.info(
        f"Writing transformed data to local Parquet files : {env_destination_local_path}, {os.path.exists(env_destination_local_path)}"
    )

    parquet_files = []

    # Check if env_destination_local_path is a folder
    if os.path.isdir(env_destination_local_path):
        # Check if *.parquet files are available in sub-folders
        parquet_files = [file for root, dirs, files in os.walk(env_destination_local_path) for file in files if file.endswith(".parquet")]

    if parquet_files:
        # Load the existing DataFrame with the date filter
        df_existing = spark.read.parquet(env_destination_local_path).filter(
            f"DATE(ts) >= '{params.start_date}' AND DATE(ts) <= '{params.end_date}'"
        )

        # Deduplicate and merge
        df_final = (
            src_dataframe.alias("new")
            .join(df_existing.alias("old"), "unique_hash", "outer")
            .select(
                coalesce(col("new.unique_hash"), col("old.unique_hash")).alias("unique_hash"),
                coalesce(col("new.address_ss58"), col("old.address_ss58")).alias("address_ss58"),
                coalesce(col("new.address_pubkey"), col("old.address_pubkey")).alias("address_pubkey"),
                coalesce(col("new.section"), col("old.section")).alias("section"),
                coalesce(col("new.storage"), col("old.storage")).alias("storage"),
                coalesce(col("new.track"), col("old.track")).alias("track"),
                coalesce(col("new.block_number"), col("old.block_number")).alias("block_number"),
                coalesce(col("new.block_hash"), col("old.block_hash")).alias("block_hash"),
                coalesce(col("new.ts"), col("old.ts")).alias("ts"),
                coalesce(col("new.era"), col("old.era")).alias("era"),
                coalesce(col("new.submitted_in"), col("old.submitted_in")).alias("submitted_in"),
                coalesce(col("new.suppressed"), col("old.suppressed")).alias("suppressed"),
                coalesce(col("new.validator_total"), col("old.validator_total")).alias("validator_total"),
                coalesce(col("new.validator_own"), col("old.validator_own")).alias("validator_own"),
                coalesce(col("new.validator_commission"), col("old.validator_commission")).alias(
                    "validator_commission"
                ),
                coalesce(
                    col("new.validator_reward_shares"),
                    col("old.validator_reward_shares"),
                ).alias("validator_reward_shares"),
                coalesce(
                    col("new.validator_reward_points"),
                    col("old.validator_reward_points"),
                ).alias("validator_reward_points"),
                coalesce(
                    col("new.validator_staking_rewards"),
                    col("old.validator_staking_rewards"),
                ).alias("validator_staking_rewards"),
                coalesce(col("new.total_staked"), col("old.total_staked")).alias("total_staked"),
                coalesce(col("new.total_reward_points"), col("old.total_reward_points")).alias("total_reward_points"),
                coalesce(col("new.total_staking_rewards"), col("old.total_staking_rewards")).alias(
                    "total_staking_rewards"
                ),
                coalesce(col("new.nominationpools_id"), col("old.nominationpools_id")).alias("nominationpools_id"),
                coalesce(col("new.nominationpools_total"), col("old.nominationpools_total")).alias(
                    "nominationpools_total"
                ),
                coalesce(
                    col("new.nominationpools_member_cnt"),
                    col("old.nominationpools_member_cnt"),
                ).alias("nominationpools_member_cnt"),
                coalesce(
                    col("new.nominationpools_commission"),
                    col("old.nominationpools_commission"),
                ).alias("nominationpools_commission"),
                coalesce(
                    col("new.nominationpools_rewardpools"),
                    col("old.nominationpools_rewardpools"),
                ).alias("nominationpools_rewardpools"),
                coalesce(col("new.member_bonded"), col("old.member_bonded")).alias("member_bonded"),
                coalesce(col("new.member_unbonded"), col("old.member_unbonded")).alias("member_unbonded"),
                coalesce(col("new.member_share"), col("old.member_share")).alias("member_share"),
                coalesce(col("new.targets"), col("old.targets")).alias("targets"),
                coalesce(col("new.pv"), col("old.pv")).alias("pv"),
                coalesce(col("new.date"), col("old.date")).alias("date"),
                coalesce(col("new.month"), col("old.month")).alias("month"),
                coalesce(col("new.year"), col("old.year")).alias("year"),
            )
        )
    else:
        # If the destination path does not exist or is empty, use df as the final DataFrame
        os.makedirs(env_destination_local_path, exist_ok=True)
        df_final = src_dataframe

    # Write the transformed and deduplicated data to Parquet files
    df_final.write.partitionBy("year", "month").mode("overwrite").parquet(env_destination_local_path)

def check_is_update_required(
    context: AssetExecutionContext, params: SubstrateExtractParameters, spark: SparkSession
) -> bool:
    env_destination_local_path = os.environ.get("PSS_LHOUSE_LEV0_STAKING_INGESTION_SINK")
    parquet_files = []

    # Check if env_destination_local_path is a folder
    if os.path.isdir(env_destination_local_path):
        # Check if *.parquet files are available in sub-folders
        parquet_files = [file for root, dirs, files in os.walk(env_destination_local_path) for file in files if file.endswith(".parquet")]

    if not parquet_files:
        context.log.info("No existing Parquet files found. Update is required.")
        return True
    else:
        # Load the existing DataFrame with the date filter
        df_pq_existing = spark.read.parquet(env_destination_local_path).filter(
            f"DATE(ts) >= '{params.start_date}' AND DATE(ts) <= '{params.end_date}'"
        )

        query_str = f"""
            SELECT ts
            FROM `{params.gcp_project}.{params.gcp_dataset}.{params.gcp_table}`
            WHERE DATE({params.timestamp_column}) >= '{params.start_date}'
            AND DATE({params.timestamp_column}) <= '{params.end_date}'
        """
        df_bq_incoming = spark.read.format("bigquery").option("query", query_str).load()

        # Aggregate the dataset in dataframe `df_pq_existing` and `df_bq_incoming`
        # based on the column field `params.timestamp_column`
        # get summary info MAX(ts), MIN(ts), COUNT(*) as num_records
        df_pq_existing_summary = df_pq_existing.agg(
            max(params.timestamp_column).alias("max_ts"),
            min(params.timestamp_column).alias("min_ts"),
            count("*").alias("num_records")
        )

        df_bq_incoming_summary = df_bq_incoming.agg(
            max(params.timestamp_column).alias("max_ts"),
            min(params.timestamp_column).alias("min_ts"),
            count("*").alias("num_records")
        )

        pq_existing_summary = df_pq_existing_summary.collect()[0]
        bq_incoming_summary = df_bq_incoming_summary.collect()[0]

        context.log.info(
            f"Summary of existing Parquet data: {pq_existing_summary}"
        )
        context.log.info(
            f"Summary of incoming BigQuery data: {bq_incoming_summary}"
        )

        # If summary info from both dataframe `df_bq_incoming` and `df_pq_existing` are different
        # return True, else return False
        if pq_existing_summary != bq_incoming_summary:
            context.log.info("Differences found between existing and incoming data. Update is required.")
            return True
        else:
            context.log.info("No differences found between existing and incoming data. Update is not required.")
            return False


def process_data(context: AssetExecutionContext, params: SubstrateExtractParameters, query_str: str):
    try:
        # Create a SparkSession
        context.log.info("Creating SparkSession")

        conf = SparkConf()
        conf.set("spark.executor.memory", "8g")
        conf.set("spark.driver.memory", "4g")
        conf.set("spark.executor.cores", "1")
        conf.set("spark.dynamicAllocation.enabled", "true")
        conf.set("spark.shuffle.service.enabled", "true")
        conf.set("spark.sql.shuffle.partitions", "300")
        conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
        conf.set("spark.executor.extraJavaOptions", "-XX:+UseG1GC")
        conf.set("spark.task.maxFailures", "10")
        conf.set("spark.speculation", "true")
        conf.set("spark.sql.files.maxPartitionBytes", "256MB")
        conf.set("spark.sql.parquet.mergeSchema", "true")

        spark = (
            SparkSession.builder.appName("SubstrateETLPipeline")
            .config(conf=conf)  # Apply the configuration to the Spark Session
            .enableHiveSupport()  # Enable Hive support for reading from BigQuery
            .getOrCreate()
        )

        context.log.info("Spark Session Configuration :: ...")
        context.log.info(f"{spark.sparkContext.getConf().getAll()}")

        # Set the Google Cloud Storage path for BigQuery credentials
        context.log.info("Setting Google Cloud Storage path for BigQuery credentials")
        google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        # Validate the presence of the path
        if not google_credentials_path:
            raise OSError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

        # Check if the file exists and is accessible
        if not os.path.isfile(google_credentials_path):
            raise FileNotFoundError(f"The specified credentials file does not exist: {google_credentials_path}")

        if not os.access(google_credentials_path, os.R_OK):
            raise PermissionError(f"The credentials file is not readable: {google_credentials_path}")

        spark.conf.set("google.cloud.auth.service.account.json.keyfile", google_credentials_path)
        spark.conf.set("viewsEnabled", "true")
        spark.conf.set("materializationDataset", params.gcp_materialize_dataset)
        spark.conf.set("spark.sql.debug.maxToStringFields", "1000")

        # Check if an update is required
        if not check_is_update_required(context, params, spark):
            context.log.warning("Skipping data update. No changes found in the incoming dataset.")
            spark.stop()  # Stop the SparkSession before returning early
            return

        # Read data from BigQuery
        table = f"{params.gcp_project}.{params.gcp_dataset}.{params.gcp_table}"
        context.log.info(f"Reading data from BigQuery :: {table}, {query_str}")

        df = spark.read.format("bigquery").option("query", query_str).load()
        # Add new columns: year, month, and date
        context.log.info("Adding new columns: year, month, and date")
        df = (
            df.withColumn("year", year(df[params.timestamp_column]))
            .withColumn("month", month(df[params.timestamp_column]))
            .withColumn("date", to_date(df[params.timestamp_column]))
            .withColumn(
                "unique_hash",
                sha2(
                    concat_ws("|", "block_number", "block_hash", "ts", "address_pubkey"),
                    256,
                ),
            )
        )

        # Order by era and ts
        context.log.info("Ordering by era and ts")

        # Order by 'era' and the timestamp column
        df_ordered = df.orderBy("era", params.timestamp_column)

        # Write the transformed data to Parquet files partitioned by year and month
        if params.destination == "local":
            update_locallake(context, params, spark, df_ordered)
        else:
            raise ValueError(f"Unsupported destination: {params.destination}")

    except Exception as e:
        context.log.error(f"Error occurred during process_data: {e!s}")
        raise e

    finally:
        # Stop the SparkSession
        context.log.info("Stopping SparkSession")
        spark.stop()


def build_substrate_query(context: AssetExecutionContext, params: SubstrateExtractParameters) -> str:
    try:
        # Read the input data from BigQuery using the custom query
        return f"""
            SELECT *
            FROM `{params.gcp_project}.{params.gcp_dataset}.{params.gcp_table}`
            WHERE DATE({params.timestamp_column}) >= '{params.start_date}'
            AND DATE({params.timestamp_column}) <= '{params.end_date}'
        """

    except Exception as e:
        context.log.error(f"Error occurred during build_substrate_query: {e!s}")
        raise e
