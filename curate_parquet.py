'''
    This file must be uploaded to the Spark workspace that is used by the ADF.
'''

import argparse
import logging
import os
import pyspark
import json
import datetime
import hashlib
import hmac
import base64
import requests

from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable
from pyspark.sql.dataframe import DataFrame

log = logging.getLogger(__name__)

# Default logging level is WARNING
#   To see more output, change to logging.INFO
logging.basicConfig(level=logging.WARN)

# Construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument('-s', '--source_level', required=True, help='Source level, e.g.bronze')
ap.add_argument('-d', '--destination_level', required=True, help='Destination level, e.g. bronze')
ap.add_argument('-t', '--table_name', required=True, help='Name of Delta table')
ap.add_argument('-k', '--key_columns', required=False, help='Primary keys as comma separated list of column names appearing in table_name')
ap.add_argument('-r', '--partition_columns', required=False, nargs='?', const=None, help='Comma separated list of columns to be used to partition the data')
ap.add_argument('-v', '--schema', required=True, help='schema, e.g. TOPSv2. A folder with this name must exist in the storage account')
ap.add_argument('-j', '--renaming_instructions', required=False, default=None, help='JSON command representing column names to be adjusted')
ap.add_argument('-i', '--incremental', required=True, help='indicates with "y" or "n" whether the incoming data is to be incrementally added or is a full overwrite')
ap.add_argument('-a', '--validation_instructions', required=False, default=None, help='a JSON string the specifies instructions for validating data after flattening data')

# Databricks configuration required:
#   1. Add python-dotenv==0.15.0 to 'Libraries' 2. Update Advanced options->Environment Variables
# load_dotenv()
# Update Advanced options->Environment Variables and calling them into code
# load_dotenv()

# Constants
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
SPCLIENTID = os.getenv("SPCLIENTID")
SPTENANTID = os.getenv("SPTENANTID")
SPSCOPE = os.getenv("SPSCOPE")
SPSECRET = os.getenv("SPSECRET")
LAWWID = os.getenv("LAWWID")
LAWPK = os.getenv("LAWPK")
# TODO: We may want to add a parameter to the command line to specify the name of the log analytics workspace
LOGS_NAME = 'TOPSv2_LOGS'
LOCAL_DEV_STORAGE_FOLDER = 'test_fixtures'
BASE_STORAGE_URL_LANDING = f'abfss://landing@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net'
BASE_STORAGE_URL_PROCESSED = f'abfss://processed@{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net'



def process_command_line(spark):
    '''
        This method is a wrapper that processes the command line and triggers processing
    '''
    log.info(f'+++ upserting using {spark.version}')
    args = vars(ap.parse_args())
    source_level : str = args['source_level']
    destination_level : str = args['destination_level']
    table_name : str = args['table_name']
    key_columns : str = (args['key_columns'])
    partition_columns :str = args['partition_columns']
    schema : str = args['schema']
    renaming_instructions : str = args['renaming_instructions']
    incremental: bool = args['incremental'] == 'y' or args['incremental'] == 'Y'
    validation_instructions: str = args['validation_instructions']

    log.info('+++ source_level=%s', source_level)
    log.info('+++ destination_level=%s', destination_level)
    log.info('+++ table_name=%s', table_name)
    log.info('+++ key_columns=%s', key_columns)
    log.info('+++ partitiona_columns=%s', partition_columns)
    log.info('+++ schema=%s', schema)
    log.info('+++ renaming_instructions=%s', renaming_instructions)
    log.info('+++ p_incremental=%s', incremental)
    log.info('+++ validation_instructions=%s', validation_instructions)

    if partition_columns is not None:
        partition_columns = (args['partition_columns']).split(',')
    else:
        partition_columns = []

    if key_columns is not None:
        key_columns = (args['key_columns']).split(',')
    else:
        key_columns = []

    process_command(spark, source_level, destination_level, table_name, key_columns, partition_columns, schema, renaming_instructions, incremental, validation_instructions)


def load_source_data(spark, source_level, table_name, schema, renaming_intructions):
    '''
        This method is to load the source data
    '''
    path_to_source_data = get_path_to_table(spark, BASE_STORAGE_URL_LANDING, table_name, source_level, schema, path_includes_yyyymmdd_subfolders=False)
    log.warning(f'+++ Reading updates from {path_to_source_data}')
    source_data_df = spark.read.parquet(path_to_source_data)
    updated_df = column_rename (spark, source_data_df, renaming_intructions, table_name)
    return updated_df


def column_rename (spark, source_df, renaming_instructions, table_name):
    '''
        This method expects a dataframe, a JSON object and a table name. 
        The format of the JSON object should be {"tablelane:"<tablename>, 
        "renaming_instructions":<A SQL select statement that references the <tablename>>}. 
        The SQL statement will be executed and is expected to be used to rename columns. 
        If the "renaming_instructions" are empty, the dataframe is returned unchanged.
    '''
    if renaming_instructions is not None:
        rename_instructions = json.loads(renaming_instructions)

        rename_df = source_df

        if rename_instructions:
            for instruction in rename_instructions:
                rename_command = instruction ['renaming_instructions']
                destination_table = instruction['table_name']
                log.info('--* Renaming columns in table %s', destination_table)
                
                if table_name in rename_command:
                    source_df.createOrReplaceTempView(table_name)
                    update_df = spark.sql((rename_command))
                    rename_df = update_df

                else:
                    log.warning('--* command does not contain table name %s', table_name)

    return rename_df


def upsert_data_into_delta(spark, updates_df: str, destination_table_path: str, key_columns: str, is_incremental: bool, partition_columns=None):
    '''
        This method will upsert updates_df into the delta table given 
        by the destination path if a key_column is provided and check if it is incremental. 
        If it is not incremental then updates_df will overwrite the delta table at the destination path.
    '''
    if not DeltaTable.isDeltaTable(spark, destination_table_path):
        log.warning(f'+++ Creating new table @ {destination_table_path}')
        if partition_columns:
            updates_df.write.format('delta').mode('overwrite').partitionBy(*partition_columns).save(destination_table_path)
        else:
            updates_df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').save(destination_table_path)
    else:
        merge_columns = key_columns

        # Check if table is incremental
        if is_incremental:
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

        else:
            log.warning(f'---* Not incremental, performing full load.')
            updates_df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').save(destination_table_path)


def process_command(spark, source_level, destination_level, table_name, key_columns, partition_columns, schema, renaming_instructions, is_incremental, validation_instructions_string):
    '''
        This method is main process method to load and perform upsert data
    '''
    log.info('+++ Generating data for %s ', table_name)
    start_time = datetime.datetime.now()
    updates_df = load_source_data(spark, source_level, table_name, schema, renaming_instructions)
    path_to_destination_table = get_path_to_table(spark, BASE_STORAGE_URL_PROCESSED, table_name, destination_level, schema) 
    upsert_data_into_delta(spark, updates_df, path_to_destination_table, key_columns, is_incremental, partition_columns)
    end_time = datetime.datetime.now()
    
    # Calculating run time from Start and End time
    time_difference = end_time - start_time
    run_time = time_difference.total_seconds()
    
    # Reading number of rows from the delta table
    target_table_df = spark.read.format("delta").load(path_to_destination_table)
    total_num_rows = target_table_df.count()

    perform_validation_and_log_metrics(spark, schema, updates_df, validation_instructions_string, table_name, total_num_rows, run_time)


def validation_check(spark, updates_df: DataFrame, validation_command, table_name):
    '''
        This method will check for data validations
        provided in validation instructions and provide information about how many
        times data validations have occured.

        Drops table_name view if it exists because renaming_instructions method might have it already created
    '''
    
    spark.sql(f"DROP VIEW IF EXISTS {table_name}")    
    updates_df.createOrReplaceTempView(table_name)
    validate_df = spark.sql(validation_command)
    
    return validate_df
    


def perform_validation_and_log_metrics(spark, schema, updates_df, validation_instructions_string, destination_tablename, total_num_rows, run_time):
    '''
        This process will perfom validations on the data 
        by checking if there are validations instructions provided from cfgBronze
        and log errors and other required metrics through send_log_metrics

        The resulting validation_df will expect the column name as num_errors else it will fail.
        E.g Select count(*) as num_errors from table_name where column_name is null
    '''    

    num_errors = 0
    if updates_df is not None:
        num_rows = updates_df.count()
        if validation_instructions_string is not None:
            validation_instructions = json.loads(validation_instructions_string)

            if validation_instructions:
                for instruction in validation_instructions:
                    validation_command = instruction['validation_command']
                    error_message = instruction['error_message']

                    if destination_tablename in validation_command:
                        validation_df = validation_check(spark, updates_df, validation_command, destination_tablename)

                        # This condition check will see if there are any records in dataframe or not
                        if validation_df is None:
                            log.info('--*  No validation checks defined for %s', destination_tablename)
                        else:
                            num_errors = validation_df.collect()[0]['num_errors']
                            log.warning('--* %s %d', error_message, num_errors)

                        send_log_metrics(spark, schema, destination_tablename, num_rows, total_num_rows, run_time, error_message, num_errors)
                    else:
                        log.info('--* No validation instructions found for the table %s', destination_tablename)
                        error_message = 'No Validation Required'
                        send_log_metrics(spark, schema, destination_tablename, updates_df.count(), total_num_rows, run_time, error_message, num_errors)
        
    else:
        # if update df have no incoming data else will be triggered
        num_rows = 0
        error_message = 'No new rows being supplied'
        send_log_metrics(spark, schema, destination_tablename, num_rows, total_num_rows, run_time, error_message, num_errors)
    
    return num_errors



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



def build_signature(wks_id, shared_key, date, content_length, method, content_type, resource):
    '''
        This method is only for the use of the log_data() method.
    '''

    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = str.encode(string_to_hash, 'utf-8')
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(wks_id, encoded_hash)

    return authorization


def log_data(spark,body, log_type) -> int:
    '''
        Use this method for sending data to a log analytics workspace. The `body`
        should be in JSON format and represent the fields of the log message.
        The `log_type` is the table name that would be used to capture the log in the LAW.
        A HTTP status will be returned which for success should in be in the range 200-299
        This method assumes that there exists a secret scope called `SPSCOPE` which points to
        an Azure key vault which has secrets called `logs-law-WID` and `logs-law-PrimaryKey`. If the scope does
        not exist a HTTP 404 is returned.
    '''
    # We check if the scope exists because in dev it likely may not.
    if spark.conf.get('spark.master') == 'local':
        return 200
    else:
        wks_id = dbutils.secrets.get(SPSCOPE, LAWWID)
        wks_shared_key = dbutils.secrets.get(SPSCOPE, LAWPK)
    
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = build_signature(wks_id, wks_shared_key, rfc1123date, content_length, method, content_type, resource)
        uri = 'https://' + wks_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

        headers = {
                'content-type': content_type,
                'Authorization': signature,
                'Log-Type': log_type,
                'x-ms-date': rfc1123date
            }
        response = requests.post(uri,data=body, headers=headers)
        
        # Warning Log if HTTP request to LAW is not successful 
        if response.status_code != 200:
            log.warning('+++ Unable to process request to Log Analytics Workspace with response code: %s',response.status_code)
        
        return response.status_code


def send_log_metrics(spark, scope, table_name, num_merge_rows, num_total_rows, run_time, error_message, num_errors):
    '''
        This method is used to build the JSON structure to log data into 
        Log Analytics Workspace from values obtained during pipeline run
    '''
    json_data = [
               {
                "scope":  scope,
                "table_name":  table_name,
                "num_merge_rows": num_merge_rows,
                "num_total_rows": num_total_rows,
                "run_time": run_time,
                "error_message": error_message,
                "num_errors": num_errors
                }
            ]
    body = json.dumps(json_data)
    log.warning('  This is what will be sent to Log analytics %s', body)
    log_type = LOGS_NAME
    response = log_data(spark, body, log_type)

    return response


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
