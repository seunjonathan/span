'''
    This function app implements the fast path of a lambda archicture used to 
    deliver near real time functionality to end users.

    The fast path is triggered by a timer and delivers a parquet files at regularly
    scheduled intervals. Files older than a specified age are deleted.

    Proposal going foward is to implement 3 endpoints. One for each of:
        vw_NearRealTime_BOL
        vw_NearRealtTime_Sailing
        vw_NearRealTime_Location
    Each would be timer triggered. Timers could be offset by 60s or so.
    Each would deliver a parquet containing last 5 minutes of data.
    Each would delete any parquet over 120 min old.
    '''
import logging
import os
import azure.functions as func
import pyodbc
import pandas as pd
import time

from azure.storage.blob import BlobClient
from azure.storage.blob import BlobServiceClient
from datetime import datetime
 

# app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
 
def main(topstimer: func.TimerRequest) -> None:
    '''
        This method represents a function app endpoint. It was used to test connectivity to the TOPS
        on-premise server (see local.settings.json for server URL).
    '''
    # Initialize environment variables
    sqlserver_connection_string = os.environ['ConnectionStringWOPWD']
    password = os.environ['DBPassword']
    sqlquery_bol = os.environ['SQLQuery_BOL']
    bol_folder = os.environ['BOLFolder']
    sailing_folder = os.environ['SailingFolder']
    location_folder = os.environ['LocationFolder']
    storage_connection_string = os.environ['StorageConnectionString']
    container = os.environ['Container'] # e.g. 'processed'
    sqlquery_sailing = os.environ['SQLQuery_Sailing']
    sqlquery_location = os.environ['SQLQuery_Location']
    delete_after_seconds = int(os.environ['DeleteAfterSeconds'])

    now = time.time() # timestamp as seconds since epoch as float
    timestamp = datetime.utcfromtimestamp(now)
    timestamp_str = unix2utc(now)

    # Get BOL data
    df = sql2df(sqlquery_bol, sqlserver_connection_string + f'{{{password}}}')
    filename = f'BOL_{timestamp_str}.parquet'
    folder = f'{bol_folder}'
    save(df, filename, folder, storage_connection_string, container, timestamp)

    delete_old_files(folder + '/', storage_connection_string, container, delete_after_seconds, timestamp_str)

    # Get Sailing data
    df = sql2df(sqlquery_sailing, sqlserver_connection_string + f'{{{password}}}')
    filename = f'Sailing_{timestamp_str}.parquet'
    folder = f'{sailing_folder}'
    save(df, filename, folder, storage_connection_string, container, timestamp)

    delete_old_files(folder, storage_connection_string, container, delete_after_seconds, timestamp_str)

    # Get Location data
    df = sql2df(sqlquery_location, sqlserver_connection_string + f'{{{password}}}')
    filename = 'location_latest.parquet'
    folder = f'{location_folder}'
    save(df, filename, folder, storage_connection_string, container, timestamp)




def sql2df(sql_query, sql_server_connection_string):
    '''
        This method executes a SQL query and returns the results as a pandas dataframe.
    '''
    cnxn = pyodbc.connect(sql_server_connection_string)

    logging.info('+++ Connected: NOW execting SQL query %s', sql_query)
    df = pd.read_sql(sql_query, cnxn)

    # The first column is an index - reset it so we can actually see it.
    df.reset_index(inplace=True)
    return df


def save(df, filename, folder_name, blob_connection_string, container, refresh_time):
    '''
        This method saves a pandas dataframe to a parquet file.
        The filename is built using the table_name and the current date/time.
        NOTE: Since at times, columns may be completely empty, this will lead to multiple
              parquet files in the same folder with different types. This will cause query problems.
              To avoid this, we convert all columns to strings. Side effect is that actual empty
              rows will contain the string 'None', or 'NaT, or 'nan' instead of a blank.
              This is resolved in the Synapse view definition, where TRY_CAST is used to convert
              these values to the correct type. 'nan', 'NaT', and 'None' are all converted to NULL.
    '''
    # Write dataframe to blob
    target_path = f'{folder_name}/{filename}' if folder_name else f'{filename}'
    target_blob = BlobClient.from_connection_string(blob_connection_string, container, target_path)
    df = df.astype(str)
    df['refresh_time_utc'] = refresh_time
    parquet_data = df.to_parquet()
    logging.info('+++ Writing %s', target_path)
    target_blob.upload_blob(parquet_data, overwrite=True)


def expired_files(all_files, unixtime_now, delete_after_seconds) -> list:
    '''
        This method returns a list of all files older than delete_after_seconds.
    '''
    list_of_expired_files = []
    for file in all_files:
        time_part = (file.name.split('_')[2]).split('.')[0]
        if diff_in_seconds(time_part, unixtime_now) > delete_after_seconds:
            list_of_expired_files.append(file)

    return list_of_expired_files


def delete_old_files(folder_name, storage_connection_string, container, delete_after_seconds, unixtime_now):
    '''
        This method deletes any parquet files older than delete_after_seconds.
    '''
    # Identify all blobs in current folder
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    container_client = blob_service_client.get_container_client(container)
    blobs_list = container_client.list_blobs(name_starts_with=folder_name + '/')

    files_to_be_deleted = expired_files(blobs_list, unixtime_now, delete_after_seconds)

    for blob in files_to_be_deleted:
        logging.info('+++ filename=%s is older than %s seconds', blob.name, delete_after_seconds)
        source_blob = blob_service_client.get_blob_client(container, blob.name)
        source_blob.delete_blob()


def unix2utc(unix):
    '''
        Converts unixtime to utc and then returns this as a string
    '''
    datetime_str = datetime.utcfromtimestamp(unix).strftime('%Y%m%dT%H:%M:%S')
    return datetime_str


def diff_in_seconds(t1: str, t2: str):
    '''
        Returns the difference in seconds between two timestamps
    '''
    t1 = datetime.strptime(t1, '%Y%m%dT%H:%M:%S')
    t2 = datetime.strptime(t2, '%Y%m%dT%H:%M:%S')
    return (t2 - t1).total_seconds()