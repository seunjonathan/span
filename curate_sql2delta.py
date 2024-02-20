'''
    This file must be uploaded to the Spark workspace that is used by the ADF.
'''

import argparse
import logging
import os
import pyspark
from datetime import datetime

from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable
from pyspark.sql.functions import *
from pyspark.sql.types import *


# Constants
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
SPCLIENTID = os.getenv("SPCLIENTID")
SPTENANTID = os.getenv("SPTENANTID")
SPSCOPE = os.getenv("SPSCOPE")
SPSECRET = os.getenv("SPSECRET")
LOCAL_DEV_STORAGE_FOLDER = 'test_fixtures'
BASE_STORAGE_URL_PROCESSED = f'abfss://processed@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net'

log = logging.getLogger(__name__)

# Default logging level is WARNING
#   To see more output, change to logging.INFO
logging.basicConfig(level=logging.WARN)

# Construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument('-s', '--source_level', required=True, help='Source level, e.g.silver')
ap.add_argument('-d', '--destination_level', required=True, help='Destination level, e.g. gold')
ap.add_argument('-t', '--destination_table_name', required=True, help='Name of final Delta table')
ap.add_argument('-v', '--schema', required=True, help='schema, e.g. TOPSv2. A folder with this name must exist in the storage account')
ap.add_argument('-f', '--sql_string', required=True, help='sql query to be used to extract data and generate nearrealtime table')
ap.add_argument('-l', '--list_source_tables', required=True, help='list of tables used in the sql query e.g T_JOB,T_JOBFIELDUPDATED,T_TRUNK')
ap.add_argument('-k', '--key_columns', required=False, help='Primary key columns used for merging e.g BOL_Number Sailing_ID')

#Example of how to pass arguments to this script from local env
#python spark_main.py -s silver -d gold -t NEARREALTIME -k BOL_Number -l T_JOB,T_JOBFIELDUPDATED,T_TRUNK,T_ASSIGNMENT -v TOPSv2 -f 'WITH CTE_JobPK AS (SELECT pk_Job_IN AS JobPK FROM t_Job UNION SELECT fk_Job_in FROM t_JobFieldUpdated) SELECT job.JobNumber_vc AS BOL_Number, assignment.pk_Assignment_in AS Sailing_ID,   trunk.fk_AssignmentStatus_in AS Assignment_Status FROM t_Job job LEFT JOIN t_Trunk trunk ON job.pk_Job_in = trunk.fk_Job_in LEFT JOIN t_assignment assignment ON trunk.fk_Assignment_in = assignment.pk_Assignment_in WHERE job.pk_Job_in IN (SELECT JobPK FROM CTE_JobPK)'

def process_command_line(spark):
    '''
        This method is a wrapper that processes the command line and triggers processing
    '''
    args = vars(ap.parse_args())
    source_level : str = args['source_level']
    destination_level : str = args['destination_level']
    destination_table_name : str = args['destination_table_name']
    schema : str = args['schema']
    sql_string : str = args['sql_string']
    list_source_tables: list = args['list_source_tables'].split(',')
    key_columns : str = (args['key_columns']).split(',')

    log.info('+++ source_level=%s', source_level)
    log.info('+++ destination_level=%s', destination_level)
    log.info('+++ destination_table_name=%s', destination_table_name)
    log.info('+++ schema=%s', schema)
    log.info('+++ sql_string=%s', sql_string)
    log.info('+++ list_source_tables=%s', list_source_tables)
    log.info('+++ key_columns=%s', key_columns)

    process_command(spark, source_level, destination_level, destination_table_name, list_source_tables, schema, sql_string, key_columns)


def load_and_create_temp_views(spark, source_level, list_source_tables, schema):
    '''
        This method is to load the source data
    '''

    for source_table in list_source_tables:
        table_name = source_table
        path_to_source_data = get_path_to_table(spark, BASE_STORAGE_URL_PROCESSED, table_name, source_level, schema, path_includes_yyyymmdd_subfolders=False)
        log.warning(f'+++ Reading updates from {path_to_source_data}')

        df = spark.read.format("delta").load(path_to_source_data).distinct()
        df.createOrReplaceTempView(table_name)


def run_sql(spark, sql_string):
    '''
    This returns a dataframe which will be the result of the 
    SQL statement execution. 
    '''
    if sql_string is not None:
        sql_result_df = spark.sql(f"{sql_string}")
        return sql_result_df


def upsert_data_into_delta(spark, updates_df: str, destination_table_path: str, key_columns: str):
    '''
        This method will upsert updates_df into the delta table given 
        by the destination path if a key_column is provided and check if it is incremental. 
        If it is not incremental then updates_df will overwrite the delta table at the destination path.
    '''
    if not DeltaTable.isDeltaTable(spark, destination_table_path):
        log.warning(f'+++ Creating new table @ {destination_table_path}')
        updates_df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').save(destination_table_path)
        
    else:
        merge_columns = key_columns
        try:
            predicate_string = f'target.{merge_columns[0]} = updates.{merge_columns[0]}'
            for column in merge_columns[1:]:
                predicate_string += " AND " + f'target.{column} = updates.{column}'
                log.info(f'--* predicate string is %s',predicate_string)

            target_delta_table = DeltaTable.forPath(spark, destination_table_path)
            target_delta_table.alias("target") \
                .merge(updates_df.alias("updates"), predicate_string) \
                .whenMatchedUpdateAll() \
                .whenNotMatchedInsertAll() \
                .execute()
        
        except IndexError:
            log.warning('+++ Exception while merging')


def process_command(spark, source_level, destination_level, destination_table_name, list_source_tables, schema, sql_string, key_columns):
    '''
        This method is main process method to load, create temp views, run sql and write data
    '''

    load_and_create_temp_views(spark, source_level, list_source_tables, schema)
    updated_df = run_sql(spark, sql_string)

    #adding a column to the dataframe to indicate the time of the update
    updated_df = updated_df.withColumn("refresh_time_utc", current_timestamp())

    path_to_destination_table = get_path_to_table(spark, BASE_STORAGE_URL_PROCESSED, destination_table_name, destination_level, schema)
    upsert_data_into_delta(spark, updated_df, path_to_destination_table, key_columns)


def get_path_to_table(spark, base_url, name_of_table, level, schema, path_includes_yyyymmdd_subfolders=False) -> str:
    '''
        Given the name of a table, this method will return a path
        to a local 'test_' storage folder when running in spark local mode.
        Otherwise a path to blob storage will be returned.
        'level' should be one of bronze, silver or gold.
    '''

    # Bronze data is sorted into yyyy/mm/dd/ folders. There will only be one day, but we traverse using wildcards. 
    if spark.conf.get('spark.master') == 'local':
        if path_includes_yyyymmdd_subfolders:
            return os.path.join(os.getcwd(), 'test_fixtures', f'{level}', f'{schema}', f'{name_of_table}','*','*','*')
        else:
            return os.path.join(os.getcwd(), 'test_fixtures', f'{level}', f'{schema}', f'{name_of_table}')

    else:
        if path_includes_yyyymmdd_subfolders:
            return f'{base_url}/{level}/{schema}/{name_of_table}/*/*/*'
        else:
            return f'{base_url}/{level}/{schema}/{name_of_table}'


def get_or_create_spark(spark_app_name: str):
    '''
        This method is to factor out the same code that is used in a few
        places inside this project.
        Note that in Windows, a new spark context will create a temporary folder.
        These folders will be locate in the /tmp folder of this project.
        A known error is expected that indicates that this temp spark folder
        could not be deleted when the spark context stops. You will have to delete
        these folders in /tmp manually.
    '''
    builder = pyspark.sql.SparkSession.builder.appName(spark_app_name) \
        .config("spark.master", "local") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", True) \
        .config("spark.local.dir", "./tmp/spark-temp")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    return spark


if __name__ == "__main__":
    # If running as main, context must be a real spark job

    spark.conf.set(f"fs.azure.account.auth.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "OAuth")
    spark.conf.set(f"fs.azure.account.oauth.provider.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
    spark.conf.set(f"fs.azure.account.oauth2.client.id.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", SPCLIENTID)
    spark.conf.set(f"fs.azure.account.oauth2.client.secret.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", dbutils.secrets.get(SPSCOPE,SPSECRET))
    spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", f"https://login.microsoftonline.com/{SPTENANTID}/oauth2/token")
    process_command_line(spark)
