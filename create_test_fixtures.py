'''
    This code is used to construct Delta tables from the CSV in the LOCAL_DEV_STORAGE_FOLDER/bronze folder
'''

import logging
import os
import shutil
import pyspark

from delta import configure_spark_with_delta_pip
from pyspark.sql.functions import col
from curate_sql2delta import get_path_to_table, LOCAL_DEV_STORAGE_FOLDER

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

#set list of tables to work on
list_of_tables = ['T_JOB', 'T_JOBFIELDUPDATED', 'T_JOB_MASTERLOG', 'T_MASTERLOG', 'T_WEB_CUSTOMERLOGIN', 'T_USER', 'T_TRUNK', 'T_ASSIGNMENT', 'T_JOBSUMMARY', 'T_OTG_POD', 'T_WAYPOINT', 'T_CONSIGNMENT', 'T_APPOINTMENT', 'T_ASSIGNMENTRESERVATIONLOG']

for source_table in list_of_tables:
    source_path_csv = get_path_to_table(spark, DUMMY_BASE_URL, source_table, 'csv', '')
    target_path_parquet = get_path_to_table(spark, DUMMY_BASE_URL, source_table, 'silver/TOPSv2', '')

    # Read CSV data
    csv_df = spark.read.format('csv').option('header', 'true').load(source_path_csv)

    # Write the DataFrame to delta format
    log.warning('+++ Creating %s table with %s rows @ %s', source_table, csv_df.count(), target_path_parquet)
    csv_df.write.format('delta').mode('overwrite').save(target_path_parquet)



# # Create file 1 delta

# source_path_csv = get_path_to_table(spark, DUMMY_BASE_URL, 'T_JOB', 'csv', '')
# target_path_parquet = get_path_to_table(spark, DUMMY_BASE_URL, 'T_JOB', 'silver', '')

# # Read CSV data
# csv_df = spark.read.format('csv').option('header', 'true').load(source_path_csv)

# # Write the DataFrame to delta format
# log.warning('+++ Creating T_MASTERLOG table with %s rows @ %s', csv_df.count(), target_path_parquet)
# csv_df.write.format('delta').mode('overwrite').save(target_path_parquet)