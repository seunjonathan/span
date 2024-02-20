import json
import os
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from rest_app.services.Delta import get_table

pd.set_option('display.max_columns', None)

HOME = os.getenv("HOME")
API_KEY = os.getenv("API_KEY")
VERSION = '2021-12-10:001'
MESSAGE = 'A REST endpoint to Seaspan vessel arrivals and departure information'
CONTAINER_VERSION='not used'
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
FS = None

# prevent SettingWithCopyWarning message from appearing
# pd.options.mode.chained_assignment = None

container = None
df_appt = get_table(FS, container, 'tests/input_data/T_APPOINTMENT').drop(columns = ['Deleted_dt'])
df_asgn = get_table(FS, container, 'tests/input_data/T_ASSIGNMENT')
df_rte = get_table(FS, container, 'tests/input_data/T_ROUTE').drop(columns = ['Deleted_dt'])
df_trck = get_table(FS, container, 'tests/input_data/T_TRUCK').drop(columns = ['Deleted_dt'])

print(f'+++ len Appointment = {len(df_appt)}')
print(f'+++ len Assignment = {len(df_asgn)}')
print(f'+++ len Route = {len(df_rte)}')
print(f'+++ len Truck = {len(df_trck)}')

df_dated = df_appt.loc[
        (df_appt['Scheduled_Departure_Date_Time'] >= '2000-01-01')
        & (df_appt['Scheduled_Departure_Date_Time'] < '2022-02-28')][['Scheduled_Departure_Date_Time']]

df_merged = df_asgn.merge(df_appt, left_on='fk_Appointment_in', right_on='pk_Appointment_in')

s_id = 53185
print(f'After merge of T_ASSIGNMENT & T_APPOINTMENT table for sailing_id = {s_id}:')
print(df_merged.loc[(df_merged['Sailing_ID'] == s_id)][['Scheduled_Departure_Date_Time', 'Sailing_ID', 'Deleted_dt']])

df_merged = df_merged.merge(df_trck, left_on='fk_Truck_in', right_on='pk_Truck_in')
print(f'After merge with df_trck table for sailing_id = {s_id}:')
print(df_merged.loc[(df_merged['Sailing_ID'] == s_id)][['Scheduled_Departure_Date_Time', 'Sailing_ID', 'Deleted_dt']])

df_merged = df_merged.merge(df_rte, left_on='fk_Route_in', right_on='pk_Route_in')
print(f'After merge with df_rte for sailing_id = {s_id}:')
print(df_merged.loc[(df_merged['Sailing_ID'] == s_id)][['Scheduled_Departure_Date_Time', 'Sailing_ID', 'Deleted_dt', 'Vessel', 'Vessel_Code']])

df_narrow = df_merged[['Scheduled_Departure_Date_Time',
            'Scheduled_Arrival_Date_Time',
            'Actual_Arrival_Date_Time',
            'Actual_Departure_Date_Time',
            'RouteCode',
            'Route',
            'Vessel_Code',
            'Vessel',
            'Sailing_ID',
            'Lane',
            'Destination_Port',
            'Origin_Port',
            'Departure_Berth',
            'Arrival_Berth',
            'LastUpdate_ts',
            'Deleted_dt',
            'Added_dt']]

print('+++ Rows with Deleted_dt not null and vessel codes are SW and RE')
df_filtered = df_narrow.loc[(df_narrow['Deleted_dt'].notnull()) & ((df_narrow['Vessel_Code'].str.rstrip() == 'SW') | (df_narrow['Vessel_Code'].str.rstrip() == 'RE'))]
print(df_filtered[['Vessel', 'Vessel_Code', 'Sailing_ID', 'Deleted_dt', 'Scheduled_Departure_Date_Time']])

def to_int(b):
    return int.from_bytes(b, 'big')

df_filtered['LastUpdate_ts'] = df_filtered['LastUpdate_ts'].apply(lambda x: int.from_bytes(x, byteorder='big'))

print(df_filtered[['Vessel', 'LastUpdate_ts', 'Deleted_dt', 'Added_dt', 'Sailing_ID']])

# T_ASSIGNMENT & T_APPOINTMENT for Sailing_ID = 53185
print(f'+++ T_ASSIGNMENT for Sailing ID = {s_id}')
print(df_asgn.loc[(df_asgn["Sailing_ID"] == s_id)][['fk_Appointment_in', 'Sailing_ID', 'Deleted_dt']])

fk_Appointment_in = df_asgn.loc[(df_asgn["Sailing_ID"] == s_id)].fk_Appointment_in.to_list()[0]

print(f'+++ T_APPOINTMENT for fk_Appointment_in = {fk_Appointment_in}')
print(df_appt.loc[(df_appt["pk_Appointment_in"] == fk_Appointment_in)][['pk_Appointment_in', 'Added_dt', 'Scheduled_Departure_Date_Time']])

print(f'Merged table for sailing_id = {s_id}:')
print(df_narrow.loc[(df_narrow['Sailing_ID'] == s_id)][['Vessel', 'Vessel_Code', 'Sailing_ID', 'Deleted_dt']])

print('Merged table for sailing_id = 52552')
print(df_narrow.loc[(df_narrow['Sailing_ID'] == 52552)][['Vessel', 'Vessel_Code', 'Sailing_ID', 'Deleted_dt']])

j = df_filtered.to_json(orient='records', date_format='iso')
d = json.loads(j)
print('+++ Searching for sailing Id 44852')
for i, item in enumerate(d):
    s_id = d[i]['Sailing_ID']
    if (s_id == 35037):
        print(f'+++ Sailing_ID {s_id} at item {i}')
        print(item)