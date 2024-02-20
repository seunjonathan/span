'''
    This module helps to split up the code. Any unit-testable
    functionality should be implemented here.
'''
import json
import logging
import pandas as pd
import numpy as np

from azure.storage.blob import BlobClient
from datetime import datetime
from deltalake import DeltaTable
from rest_app.services.Config import STORAGE_ACCOUNT_CONNECTION_STRING, PAYLOAD_COLUMNS

log = logging.getLogger(__name__)
# Default logging level is WARNING
#   To see more output, change to logging.INFO
logging.basicConfig(level=logging.WARNING)


def get_table(file_system, container: str, table_path: str):
    '''
        `file_system` can be an AzureBlobFileSystem object, or None. When None, the 
        local file system will be used.
        `container` is a string with the name of the container. If None, the local file system is used,
        `table_path` is a string specifying the path to a delta folder
    '''
    path_to_table = f'{container}/{table_path}' if container else table_path
    delta_table = DeltaTable(path_to_table, file_system)
    pandas_df = delta_table.to_pandas()
    return pandas_df


def build_schedule_table(file_system, container: str, path, start_date, end_date, vessel_filter):
    '''
        `file_system` must be an AzureBlobFileSystem object or None. When None,
        the loal files system will be used.
        `container` is a string with the name of the containiner where delta tables can be
        found. If None, the local file system will be used.
        `path` is the path to the delta table folder.
        `start_date` and `end_date` are date-time strings used to filter the data.
        `vessel_filter` is a list of comma separated vessel codes of interest.

        A table is built of vessel departures and arrivals to satisfy
        the requirements of the Beaver Labs related project. Tables of interest are
        T_APPOINTMENT,
        T_ASSIGNMENT,
        T_ROUTE,
        T_TRUCK

        One additional table was added to address story https://dev.azure.com/seaspan-edw/DataOps/_workitems/edit/1639.
        This table provides UTC versions of the actual/scheduled departure/arrival timestamps:
        BEAVERLABSAPI
        
        Assignment and Appointment tables are large (~43k rows each as of 2021/12/14).
        To optimize the joins, we can filter on the date. We do so with the Appointment
        table which has schedule departure dates. (Actual dates can sometimes be empty).
        Also would be better if these tables
        were partitioned on date then a much smaller data set would be downloaded.
    '''
    df_appt = get_table(file_system, container, f'{path}/TOPSv2/T_APPOINTMENT').drop(columns = ['Deleted_dt']) # Drop in favour of the one that comes from T_Assignment
    df_appt_dated = df_appt.loc[
        (df_appt['Scheduled_Departure_Date'] >= start_date)
        & (df_appt['Scheduled_Departure_Date'] < end_date)]

    df_asgn = get_table(file_system, container, f'{path}/TOPSv2/T_ASSIGNMENT').drop(columns = ['Added_dt']) # Drop in favour of the one that comes from T_Appointment
    df_rte = get_table(file_system, container, f'{path}/TOPSv2/T_ROUTE').drop(columns = ['Deleted_dt'])
    df_trck = get_table(file_system, container, f'{path}/TOPSv2/T_TRUCK').drop(columns = ['Deleted_dt'])

    df_utc_times = get_table(file_system, container, f'{path}/BEAVERLABS/UTC_TIMES') \
        .drop(columns = ['Scheduled_Departure_Date_Time', 'Scheduled_Arrival_Date_Time', 'Actual_Arrival_Date_Time', 'Actual_Departure_Date_Time'])

    ############### CONVERTING AND RENAMING BEFORE MERGING  ############### ADDING TO ADDRESS #2668 and 2848
    df_asgn['LastUpdate_ts']       = df_asgn['LastUpdate_ts'].apply(lambda x: int.from_bytes(x, byteorder='big'))
    df_appt_dated['LastUpdate_ts'] = df_appt_dated['LastUpdate_ts'].apply(lambda x: int.from_bytes(x, byteorder='big'))

    df_asgn       = df_asgn.rename(columns={'LastUpdate_ts': 'LastUpdate_ts_asgn'})
    df_appt_dated = df_appt_dated.rename(columns={'LastUpdate_ts': 'LastUpdate_ts_appt'})

    df_utc_times.rename(columns = {'Sailing_ID':'Sailing_ID_utc'}, inplace = True)

    df_merged = df_asgn.merge(df_appt_dated, left_on='fk_Appointment_in', right_on='pk_Appointment_in')  # TODO: We should consider changing fk_Appointment_in to Sailing_ID 
    df_merged = df_merged.merge(df_trck, left_on='fk_Truck_in', right_on='pk_Truck_in')
    df_merged = df_merged.merge(df_rte, left_on='fk_Route_in', right_on='pk_Route_in')

    df_merged = df_merged.merge(df_utc_times, left_on='Sailing_ID', right_on='Sailing_ID_utc', how='left').drop(columns = ['Sailing_ID_utc'])
    
    ############### Adding both LastUpdate_Ts columns  ############### ADDING TO ADDRESS #2668 and 2848
    # Note: LastUpdate_ts is a SQL Server timestamp or rowindex - it is NOT a date/time
    df_merged['LastUpdate_ts'] = df_merged['LastUpdate_ts_asgn'] + df_merged['LastUpdate_ts_appt']      

    #Use the approach in EDW to generate needed columns
    df_merged['Scheduled_Departure_Date_Time'] = pd.to_datetime((df_merged['Scheduled_Departure_Date'].astype(str)) + ' ' + (df_merged['Scheduled_Departure_Time'].astype(str).str.split(' ').str[1]), format='%Y-%m-%d %H:%M:%S')
    df_merged['Scheduled_Arrival_Date_Time'] = pd.to_datetime((df_merged['Scheduled_Arrival_Date'].astype(str))+ ' ' + (df_merged['Scheduled_Arrival_Time'].astype(str).str.split(' ').str[1]), format='%Y-%m-%d %H:%M:%S')
    df_merged['Actual_Arrival_Date_Time'] = pd.to_datetime((pd.to_datetime((df_merged['Actual_Arrival_Date'].astype(str)), format='%Y-%m-%d').dt.date.astype(str))+ ' ' + (pd.to_datetime((df_merged['Actual_Arrival_Time'].astype(str)).str.split(' ').str[1], format='%H:%M:%S').dt.time.astype(str)), format='%Y-%m-%d %H:%M:%S', errors='coerce')

    #Add LANE column
    df_merged['Lane'] = np.select(
    [
        (df_merged['Route'] == 'Tilbury > Nanaimo') | (df_merged['Route'] == 'Nanaimo >Tilbury'),
        (df_merged['Route'] == 'Swartz Bay > Tilbury') | (df_merged['Route'] == 'Tilbury > Swartz Bay'),
        (df_merged['Route'] == 'Surrey > Duke Point') | (df_merged['Route'] == 'Duke Point > Surrey'),
        (df_merged['Route'] == 'Duke Point > Tilbury') | (df_merged['Route'] == 'Tilbury > Duke Point')
    ],
    [
        'Nanaimo Lane',
        'Swartz Bay Lane',
        'Duke Point Lane (Surrey)',
        'Duke Point Lane (Tilbury)'
    ],
    default='Unclassified'
)

    df_narrow = df_merged[['Scheduled_Departure_Date_Time',
                'Scheduled_Arrival_Date_Time',
                'Actual_Arrival_Date_Time',
                'Actual_Departure_Date_Time',
                'Route_Code',
                'Route',
                'Vessel_Code',
                'Vessel_Name',
                'Sailing_ID',
                'Lane',
                'LastUpdate_ts',
                'Added_dt',
                'Deleted_dt',
                'Destination_Terminal',
                'Origin_Terminal',
                'Departure_Berth',
                'Arrival_Berth',
                'UTC_Scheduled_Departure_Date_Time',
                'UTC_Scheduled_Arrival_Date_Time',
                'UTC_Actual_Arrival_Date_Time',
                'UTC_Actual_Departure_Date_Time'
                ]]


    # RouteCode and Vessel_Code have trailing whitespace
    df_narrow['Route_Code'] = df_narrow['Route_Code'].str.rstrip()
    df_narrow['Vessel_Code'] = df_narrow['Vessel_Code'].str.rstrip()

    # TODO: Add in trip time
    # prevent SettingWithCopyWarning message from appearing
    pd.options.mode.chained_assignment = None
    # Compute variance from scheduled times in minutes
    df_narrow['Dep_var'] = df_narrow.Actual_Departure_Date_Time.dt.minute \
                            - df_narrow.Scheduled_Departure_Date_Time.dt.minute
    df_narrow['Arr_var'] = df_narrow.Actual_Arrival_Date_Time.dt.minute \
                            - df_narrow.Scheduled_Arrival_Date_Time.dt.minute
    
    # Rename columns back to original names in EDW.
    df_narrow.rename(columns = {'Route_Code':'RouteCode', 'Vessel_Name':'Vessel', 'Destination_Terminal':'Destination_Port', 'Origin_Terminal':'Origin_port'}, inplace = True)

    if not vessel_filter :
        df_narrow_filtered = df_narrow
    else:
        vessels_of_interest = vessel_filter.split(',')
        df_narrow_filtered = df_narrow[df_narrow['Vessel_Code'].isin(vessels_of_interest)]

    return df_narrow_filtered


def upload_blob(filename: str, container: str, folder: str, data_to_upload):
    '''
        This is a helper method used to upload data into a blob
        in the specified container at the specified folder location
    '''
    target_path = f'{folder}/{filename}'
    blob = BlobClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING, container, target_path)
    logging.warning('+++ uploading %s', target_path)
    blob.upload_blob(data_to_upload, overwrite=True)


def json_to_parquet(json_payload) -> bytes:
    '''
        This method will convert a JSON object (type 'dict') into a dataframe and then
        into a bytes object containing parquet. It assumes that the payload contains a *single* JSON
        object, not an array. This method will also replace any dots in the dataframe column
        names with underscores prior to generating the parquet.

        The code also makes sure that we always have the columns defined by the config item PAYLOAD_COLUMNS
    '''

    pd_df = pd.json_normalize(json_payload)
    pd_df_cols = pd_df.columns
    expected_column_names = PAYLOAD_COLUMNS.split(',')

    # Make sure dataframe has all the expected column names 
    for expected_col in expected_column_names:
        if expected_col not in pd_df_cols:
            pd_df[expected_col] = None

    # Also remove any columns that we should not have (typically parent node of JSON objects that are coming null)
    for df_col in pd_df_cols:
        if df_col not in expected_column_names:
            pd_df.drop([df_col], axis=1, inplace=True)

    pd_df.columns = pd_df.columns.str.replace('.','_', regex=False)
    byte_array = pd_df.to_parquet()
    return byte_array


def process_event(payload, timestamp: datetime):
    '''
        This method is used to process the event payload coming from
        Beaver Labs. The payload is expected to be a 'dict' object.
        The incoming raw json is saved to landing/bronze. Once converted
        to parquet, the output is saved to processed/silver.
    '''
    # log.warning('+++ payload %s, received at %s UTC', payload, timestamp)

    # convert timestamp to string in yyymmddTHHMMSS format
    vessel_code = payload['data']['passage']['vessel']['code'] # This will throw a KeyError exception if not found!
    meta_id = payload['meta']['id'] # ditto
    filename = timestamp.strftime(f"{timestamp.strftime('%Y%m%dT%H%M%S')}_{vessel_code}_{meta_id}.json")
    # Write json payload to storage account
    upload_blob(filename, 'landing', 'bronze/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS', json.dumps(payload))

    # Convert to parquet
    parquet_data = json_to_parquet(payload)
    p_filename = f"{timestamp.strftime('%Y%m%dT%H%M%S')}_{vessel_code}_{meta_id}.parquet"
    # Write parquet to storage account
    upload_blob(p_filename, 'processed', 'silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS', parquet_data)
