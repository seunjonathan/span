'''
    This is a configuration file that will be elaborated once as the web server
    starts up.
'''

import os

from adlfs import AzureBlobFileSystem

HOME = os.getenv("HOME")
API_KEY = os.getenv("API_KEY")
VERSION = '2024-02-16:001' # This is the version of the REST API (Remember to update this when you make changes)
MESSAGE = 'A REST endpoint to Seaspan vessel arrivals and departure information'
CONTAINER_VERSION='not used'
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME")
FS = AzureBlobFileSystem(account_name=ACCOUNT_NAME, \
    connection_string=STORAGE_ACCOUNT_CONNECTION_STRING)
VESSEL_CODES_FILTER = os.getenv("VESSEL_CODES_FILTER")
REGEX = '(\.[0-9]{3})Z'
PAYLOAD_COLUMNS = 'meta.id,meta.topic,meta.recorded_at,meta.version,data.passage.id,data.passage.started_at,data.passage.completed_at,data.passage.from_dock.id,data.passage.from_dock.name,data.passage.from_dock.port.id,data.passage.from_dock.port.country_id,data.passage.from_dock.port.name,data.passage.from_dock.port.unlocode,data.passage.to_dock.id,data.passage.to_dock.name,data.passage.to_dock.port.id,data.passage.to_dock.port.country_id,data.passage.to_dock.port.name,data.passage.to_dock.port.unlocode,data.passage.vessel.id,data.passage.vessel.code,data.passage.vessel.imo_number,data.passage.vessel.name,data.passage.voyage.id,data.passage.voyage.number'