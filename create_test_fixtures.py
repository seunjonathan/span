'''
    This code is used to construct Delta tables from the CSV in the LOCAL_DEV_STORAGE_FOLDER/bronze folder
'''

import logging
import os
import shutil
import pyspark

from delta import configure_spark_with_delta_pip
from pyspark.sql.functions import col
from curate_parquet import get_path_to_table, LOCAL_DEV_STORAGE_FOLDER

log = logging.getLogger(__name__)

# Default logging level is WARNING
#   To see more output, change to logging.INFO
logging.basicConfig(level=logging.WARNING)

DUMMY_BASE_URL = ''

builder = pyspark.sql.SparkSession.builder.appName("Local-Spark-Unittest-Driver") \
.config("spark.master", "local") \
.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
.config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
.config("log4j.logger.org.apache.spark.util.ShutdownHookManager", "OFF") \
.config("log4j.logger.org.apache.spark.SparkEnv", "ERROR") \
.config("spark.local.dir", "./tmp/spark-temp")
spark = configure_spark_with_delta_pip(builder).getOrCreate()

shutil.rmtree(os.path.join(f'{LOCAL_DEV_STORAGE_FOLDER}', 'silver'), ignore_errors = True)

# Create file 1 parquet

source_path_csv = get_path_to_table(spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE1', 'csv', '')
target_path_parquet = get_path_to_table(spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE1', 'bronze', '')

# Read CSV data
csv_df = spark.read.format('csv').option('header', 'true').load(source_path_csv)

# Write the DataFrame to Parquet format
log.warning('+++ Creating T_CUSTOMERTYPE table with %s rows @ %s', csv_df.count(), target_path_parquet)
csv_df.write.format('parquet').mode('overwrite').save(target_path_parquet)


# Create file 2 parquet

source_path_csv = get_path_to_table(spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE2', 'csv', '')
target_path_parquet = get_path_to_table(spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE2', 'bronze', '')

# Read CSV data
csv_df = spark.read.format('csv').option('header', 'true').load(source_path_csv)

# Write the DataFrame to Parquet format
log.warning('+++ Creating T_CUSTOMERTYPE table with %s rows @ %s', csv_df.count(), target_path_parquet)
csv_df.write.format('parquet').mode('overwrite').save(target_path_parquet)


# Create T_ASSIGNMENTRESERVATIONLOG parquet

source_path_csv = get_path_to_table(spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'csv', '')
target_path_parquet = get_path_to_table(spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'bronze', '')

# Read CSV data
csv_df = spark.read.format('csv').option('header', 'true').load(source_path_csv)

# Write the DataFrame to Parquet format
log.warning('+++ Creating T_CUSTOMERTYPE table with %s rows @ %s', csv_df.count(), target_path_parquet)
csv_df.write.format('parquet').mode('overwrite').save(target_path_parquet)