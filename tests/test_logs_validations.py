import unittest
import shutil
import pyspark

from delta import configure_spark_with_delta_pip
from curate_parquet import build_signature, get_path_to_table, perform_validation_and_log_metrics

# We don't need a BASE_URL wen running locally, but still need to pass one to get_path_to_table()
DUMMY_BASE_URL = ''
LOCAL_DEV_STORAGE = 'test_fixtures'

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

        shutil.rmtree(f"{LOCAL_DEV_STORAGE}/silver", ignore_errors=True)
        shutil.copytree(f"{LOCAL_DEV_STORAGE}/silver_readonly", f"{LOCAL_DEV_STORAGE}/silver")
             
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        
    def test_build_signature(self):
        #input values
        wks_id = "xyz"
        shared_key = "abcdefgh"
        date = "2023-05-06"
        content_length = 10
        method = "POST"
        content_type = "application/json"
        resource = "/api/logs"

        # Expected output
        expected_signature = "SharedKey xyz:lHj3l130NnMK8XauKdwYXWD0s5cxn6/asgKjF3xSfWE="

        # Call the function
        signature = build_signature(wks_id, shared_key, date, content_length, method, content_type, resource)

        # Assert the signature value
        self.assertEqual(signature, expected_signature)


    def test_perform_validation_and_log_metrics(self):
        '''
            This will test the validation check method by returning number of errors
            after validations are performed on the flattened data and send metrics for logging
        '''
        target_path =  get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE1', 'silver', 'TOPSv2')
        json_df = self.spark.read.format('delta').load(target_path)
        validation_instructions_string = '[{"error_message": "Count of pk_CustomerType_in failed validation:","validation_command": "select count(*) as num_errors from T_CUSTOMERTYPE1 where pk_CustomerType_in < 1"}]'
        destination_tablename = "T_CUSTOMERTYPE1"
        schema = 'TOPSv2'
        total_num_rows = 123
        run_time = 10.25

        # Simply check number of errors after validation
        actual_errors = perform_validation_and_log_metrics(self.spark, schema, json_df, validation_instructions_string, destination_tablename, total_num_rows, run_time)
        expected_errors = 0
        self.assertEqual(expected_errors,actual_errors,f'Expected {expected_errors}, but got {actual_errors}')


    def test_perform_validation_and_log_metrics_with_errors(self):
        '''
            This will test the validation check method by returning number of errors
            after validations are performed on the flattened data and send metrics for logging 
        '''
        target_path =  get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE1', 'silver', 'TOPSv2')
        json_df = self.spark.read.format('delta').load(target_path)
        validation_instructions_string = '[{"error_message": "Count of pk_CustomerType_in failed validation:","validation_command": "select count(*) as num_errors from T_CUSTOMERTYPE1 where pk_CustomerType_in > 17"}]'
        destination_tablename = "T_CUSTOMERTYPE1"
        schema = 'TOPSv2'
        total_num_rows = 123
        run_time = 10.25

        # Simply check number of errors after validation
        actual_errors = perform_validation_and_log_metrics(self.spark, schema, json_df, validation_instructions_string, destination_tablename, total_num_rows, run_time)
        expected_errors = 1
        self.assertEqual(expected_errors,actual_errors,f'Expected {expected_errors}, but got {actual_errors}')
