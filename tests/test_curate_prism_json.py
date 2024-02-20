'''
    Unit tests
'''
import os
import sys
import unittest
import pyspark


# Added this due to import module error
sys.path.append(os.getcwd())

from delta import configure_spark_with_delta_pip
from curate_json import get_path_to_table, flatten_and_cast_data
from tests.flatten_commands import \
    FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, \
    FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, \
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


    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        
 
    def test_process_TARGETS_SHORE_POWER_UTILIZATION_data(self):
        path = os.path.join(get_path_to_table(self.spark, DUMMY_BASE_URL,'TARGETS', 'bronze', 'PRISM'), 'shore_power_utilization_sample.json')
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        flatten_command = 'select deleted_at, id, inserted_at, max_connect_after, max_disconnect_before, type, explode(vessel_ids) as vessel_id from (select parameters.*, * from (select target.* from json))'
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 2
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')


    def test_process_TARGET_DUAL_FUEL_ENGINE_GAS_MODE_data(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'TARGETS', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        flatten_command = 'select deleted_at, id, inserted_at, type, explode(vessel_ids) as vessel_id from (select parameters.*, * from (select target.* from json))'
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 4
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')


    def test_process_TARGETS_ENERGY_CONSUMPTION_data(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'TARGETS', 'bronze', 'PRISM') + '/energy_consumption_sample.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        flatten_command = 'select deleted_at, id, inserted_at, type,  criteria_predicate, criteria_type, criteria_value, time_window, timezone, explode(vessel_ids) as vessel_id from (select *,criteria1.predicate as criteria_predicate, criteria1.type as criteria_type, criteria1.value as criteria_value from(select *, explode(criteria) as criteria1 from (select parameters.*, * from (select target.* from json))))'
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 4
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
  
    
    def test_process_MISSES_ENERGY_CONSUMPTION_data(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/energy_consumption_sample.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_ENERGY_CONSUMPTION, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    def test_process_MISSES_ENERGY_CONSUMPTION_missing_leg_and_voyage_num(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/energy_consumption_sample_missing_leg_and_voyage.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_ENERGY_CONSUMPTION, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    def test_process_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_data(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    def test_process_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_missing_leg_and_voyage_data(self):
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample_missing_leg_and_voyage.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 2
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    # There are changing dynamics of reasons json array, need to monitor 
    def test_process_MISSES_SHORE_POWER_UTILIZATION_data(self):
        '''
            Normal case
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/shore_power_utilization_sample.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    # There are changing dynamics of reasons json array, need to monitor
    def test_process_MISSES_SHORE_POWER_UTILIZATION_missing_connected_at_field(self):
        '''
            Test case for ticket 2487 addressing scenario in which connect_at field is missing from data.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/shore_power_utilization_sample_missing_connected_at.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')

        actual_connected_at = df.select('connected_at').collect()[0][0]
        self.assertIsNone(actual_connected_at, f'--* Expected NULL connected_at but got {actual_connected_at}')


    def test_process_MISSES_SHORE_POWER_UTILIZATION_missing_leg_field(self):
        '''
            Test case for ticket 2559 addressing scenario in which connect_at field is missing from data.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/shore_power_utilization_sample_missing_leg.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 3
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')

        actual_leg_from_id = df.select('leg_from_id').collect()[0]['leg_from_id']
        self.assertIsNone(actual_leg_from_id, f'--* Expected NULL connected_at but got {actual_leg_from_id}')


    @unittest.skip('test case skipped because a new version of the flatten command is resilient to missing `to` leg')    
    def test_exception_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_missing_field(self):
        '''
            This test case implements a scenario in which the fields referenced by the flatten command do not all exist in the
            incoming JSON data. Specifically, the `to` leg is missing.
            This test case is expect to throw an exception
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample_missing_fields.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)

        with self.assertRaises(Exception) as context:
            flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)

        actual_exception_type = type(context.exception)
        expected_exception_type = pyspark.sql.utils.AnalysisException

        self.assertEqual(expected_exception_type, actual_exception_type, f'--* Expected exception {expected_exception_type}, but got {actual_exception_type}')


    def test_no_exception_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_missing_field(self):
        '''
            This test case implements a scenario in which the fields referenced by the flatten command do not all exist in the
            incoming JSON data. Specifically, the `to` leg is missing.
            In this case, the data should be successfully processed without throwing an exception. We use a different
            flatten command that uses get_json_object() and to_json() to return null values in the case that the to leg does not exist.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample_missing_fields.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)

        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')


    def test_get_json_oject_on_normal_MISSES_DUAL_FUEL_ENGINE_GAS_MODE(self):
        '''
            This is just to test that the get_json_object approach works in the normal case,
            when the leg to fields do exist in the json.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)

        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')

        # Assert that leg_to_name, for example is not null
        expected_leg_to_name = 'Berth 1'
        actual_leg_to_name = df.select('leg_to_name').collect()[0][0]
        self.assertEqual(expected_leg_to_name, actual_leg_to_name, f'Expected {expected_leg_to_name}, but got {actual_leg_to_name}')


    def test_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_missing_voyage_field(self):
        '''
            For ticket 2487 testing the case when the voyage field is missing.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample_missing_voyage_field.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)

        # Simply count the number of rows in the flattened df
        expected_rows = 2
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')

        actual_voyage_number = df.select('voyage_number').collect()[0][0]
        self.assertIsNone(actual_voyage_number, f'--* Expected NULL voyage_number but got {actual_voyage_number}')


    def test_MISSES_DUAL_FUEL_ENGINE_GAS_MODE_missing_fuel_amount_field(self):
        '''
            For ticket 2487 testing the case when the fuel_amount field is missing.
        '''
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/dual_fuel_engine_gas_mode_sample_missing_fuel_amount.json'
        json_df = self.spark.read.option("multiline", True).option('mode','DROPMALFORMED').json(path)
        df = flatten_and_cast_data(self.spark, json_df, FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE, None)

        # Simply count the number of rows in the flattened df
        expected_rows = 1
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')

        # TODO: Add assertion to check that connected_at field is populated with null


    def test_process_STATISTICS_data(self):  
        path = os.path.join(get_path_to_table(self.spark, DUMMY_BASE_URL,'STATISTICS', 'bronze', 'PRISM') , 'statistics_raw.json')
        json_df = self.spark.read.option("multiline", True).json(path)
        flatten_command = "select concat_ws('-',id,interval_start) as unique_id,interval_end,interval_start,ratio,running_hours_on_at_least_one_engine,running_hours_on_two_engines,id as vessel_id,imo_number from (select *,statistics.*,vessel.* from json)"
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 3
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')
        

    def test_process_VOYAGES_data(self):  
        path = os.path.join(get_path_to_table(self.spark, DUMMY_BASE_URL,'VOYAGES', 'bronze', 'PRISM') , 'voyages_raw.json')
        json_df = self.spark.read.option("multiline", True).json(path)
        flatten_command = "select completed_at, from_port_id, id, inserted_at, number, started_at, distance, duration, running_hours_on_all_engines, running_hours_on_at_least_one_engine, total_emissions, total_fuel_consumption.consumer_name as fuel_consumer_name, total_fuel_consumption.source as fuel_source, total_fuel_consumption.fuel_amount.amount as fuel_amount, total_fuel_consumption.fuel_amount.unit as fuel_unit, total_energy_consumption.amount as energy_amount, total_energy_consumption.source as energy_source,total_energy_consumption.consumer_name as energy_consumer_name, twin_engines_ratio, voyage_id, statistics_generated_at, to_port_id, updated_at, vessel_id from (select statistics.*,* from (select entries.* from (select explode(entries) as entries from json)))"
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 3
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')


    def test_process_ADDITIONAL_FUEL_CONSUMPTION_data(self):  
        path = get_path_to_table(self.spark, DUMMY_BASE_URL,'MISSES', 'bronze', 'PRISM') + '/shore_power_utilization_sample.json'
        json_df = self.spark.read.option("multiline", True).json(path)
        flatten_command = "select id, started_at, col.consumer_name, col.fuel_amount.amount, col.fuel_amount.fuel_name, col.fuel_amount.unit, col.source from (select e.id, e.started_at, explode_outer(e.statistics.additional_fuel_consumptions) from (select explode(entries) as e from json))"
        df = flatten_and_cast_data(self.spark, json_df, flatten_command, None)
        # Simply count the number of rows in the flattened df
        expected_rows = 4
        actual_rows = df.count()
        self.assertEqual(expected_rows, actual_rows, f'Expected {expected_rows}, but got {actual_rows}')