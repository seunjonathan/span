'''
    This file implements unit tests
'''

import os
import shutil
import unittest
import pyspark

from delta import configure_spark_with_delta_pip
from pyspark.sql.types import StructType, StructField, StringType
from curate_json import get_or_create_spark, get_path_to_table, flatten_and_cast_data
from tests.flatten_commands import \
    FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, \
    FLATTEN_COMMAND_MISSES_ENERGY_CONSUMPTION



# We don't need a BASE_URL wen running locally, but still need to pass one to get_path_to_table()
DUMMY_BASE_URL = ''

class Testing(unittest.TestCase):
    '''
        The testing methodology is to use JSON sample data which is part of this projec/repo.
        The sample data will be used as input to the unit tests. The tests will verify that
        the output (silver data) is as expected.
    '''
    @classmethod
    def setUpClass(cls):
        builder = pyspark.sql.SparkSession.builder.appName("Local-Spark-Unittest-Driver") \
        .config("spark.master", "local") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("log4j.logger.org.apache.spark.util.ShutdownHookManager", "OFF") \
        .config("log4j.logger.org.apache.spark.SparkEnv", "ERROR") \
        .config("spark.local.dir", "./tmp/spark-temp")
        cls.spark = configure_spark_with_delta_pip(builder).getOrCreate()

        path = os.path.join(os.getcwd(), 'storage', 'silver', 'PRISM')
        if os.path.exists(path):
            shutil.rmtree(path)

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        

    def test_TARGETS_SHORE_POWER_UTILIZATION_datetime_type(self):
        path = os.path.join(get_path_to_table(self.spark, DUMMY_BASE_URL,'TARGETS', 'bronze', 'PRISM'), 'shore_power_utilization_sample.json')
        json_df = self.spark.read.option('multiline', True).option('mode','DROPMALFORMED').json(path)
        flatten_command = 'select deleted_at, id, inserted_at, max_connect_after, max_disconnect_before, type, explode(vessel_ids) as vessel_id from (select parameters.*, * from (select target.* from json))'
        field_types = {"datetimes": ['deleted_at','inserted_at'], 'doubles':[], 'ints':[]}
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, field_types)

        # Let's check the type of the 'deleted_at'. It should be TimestampType
        actual_type = str(df.schema['deleted_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected deleted_at of {expected_type}, but got {actual_type}')

        # Let's check the type of the 'inserted_at'. It should be TimestampType
        actual_type = str(df.schema['inserted_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected inserted_at of {expected_type}, but got {actual_type}')


    def test_MISSES_ENERGY_CONSUMPTION_datetime_type(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/energy_consumption_sample.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        field_types = {"datetimes": ['ended_at','started_at'], 'doubles':[], 'ints':[]}
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_ENERGY_CONSUMPTION, field_types)

        # Let's check the type of the 'ended_at'. It should be TimestampType
        actual_type = str(df.schema['ended_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected ended_at of {expected_type}, but got {actual_type}')

        # Let's check the type of the 'started_at'. It should be TimestampType
        actual_type = str(df.schema['started_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected started_at of {expected_type}, but got {actual_type}')



    def test_MISSES_SHORE_POWER_UTILIZATION_datetime_type(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/shore_power_utilization_sample.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        field_types = {"datetimes": ['ended_at','started_at','disconnected_at','connected_at','undocked_at','docked_at'], 'doubles':[], 'ints':[]}
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, field_types)

        # Let's check the type of the 'ended_at'. It should be TimestampType
        actual_type = str(df.schema['ended_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected ended_at of {expected_type}, but got {actual_type}')

        # Let's check the type of the 'started_at'. It should be TimestampType
        actual_type = str(df.schema['started_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected started_at of {expected_type}, but got {actual_type}')

        # Let's check the type of the 'disconnected_at'. It should be TimestampType
        actual_type = str(df.schema['disconnected_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected disconnected_at of {expected_type}, but got {actual_type}')

       # Let's check the type of the 'connected_at'. It should be TimestampType
        actual_type = str(df.schema['connected_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected connected_at of {expected_type}, but got {actual_type}')

      # Let's check the type of the 'undocked_at'. It should be TimestampType
        actual_type = str(df.schema['undocked_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected undocked_at of {expected_type}, but got {actual_type}')

      # Let's check the type of the 'docked_at'. It should be TimestampType
        actual_type = str(df.schema['docked_at'].dataType)
        expected_type = 'TimestampType'
        self.assertEqual(expected_type, actual_type, f'Expected docked_at of {expected_type}, but got {actual_type}')
