'''
    This is a driver file that can be used to exercise build_schedule_table method against the real storage account.
'''
import os

from adlfs import AzureBlobFileSystem
from dotenv import load_dotenv
from rest_app.services.Delta import build_schedule_table

load_dotenv()
HOME = os.getenv("HOME")
API_KEY = os.getenv("API_KEY")
VERSION = '2024-02-16:001'
MESSAGE = 'A REST endpoint to Seaspan vessel arrivals and departure information'
CONTAINER_VERSION='not used'
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
FS = AzureBlobFileSystem(account_name=ACCOUNT_NAME, \
    connection_string=STORAGE_ACCOUNT_CONNECTION_STRING)
VESSEL_CODES_FILTER = os.getenv("VESSEL_CODES_FILTER")
REGEX = '(\.[0-9]{3})Z'
PAYLOAD_COLUMNS = 'meta.id,meta.topic,meta.recorded_at,meta.version,data.passage.id,data.passage.started_at,data.passage.completed_at,data.passage.from_dock.id,data.passage.from_dock.name,data.passage.from_dock.port.id,data.passage.from_dock.port.country_id,data.passage.from_dock.port.name,data.passage.from_dock.port.unlocode,data.passage.to_dock.id,data.passage.to_dock.name,data.passage.to_dock.port.id,data.passage.to_dock.port.country_id,data.passage.to_dock.port.name,data.passage.to_dock.port.unlocode,data.passage.vessel.id,data.passage.vessel.code,data.passage.vessel.imo_number,data.passage.vessel.name,data.passage.voyage.id,data.passage.voyage.number'

print ('+++ This might be a little slow, as it needs to fetch data from the storage account. Please be patient...')

# The code below is an abbreviated version of the schedule method in views.py

start_date = '2023-10-29'
end_date = '2023-10-30'
print(f'+++ Using Storage Account: {ACCOUNT_NAME}')
if start_date is not None and end_date is not None:
    path = 'silver'
    pandas_df = build_schedule_table(FS, 'processed', path, start_date, end_date, VESSEL_CODES_FILTER)
    print(pandas_df.head())

print('++ Done')