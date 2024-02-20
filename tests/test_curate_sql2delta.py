'''
    This file implements unit tests
'''

import os
import shutil
import unittest
import pyspark

from delta import configure_spark_with_delta_pip, DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from curate_sql2delta import get_path_to_table, load_and_create_temp_views, run_sql
from delta.tables import DeltaTable                            

# We don't need a BASE_URL wen running locally, but still need to pass one to get_path_to_table()
DUMMY_BASE_URL = ''
LOCAL_DEV_STORAGE = 'test_fixtures'

class Testing(unittest.TestCase):
    '''
        These test cases use parquet test data. 
        Please make sure to run create_test_fixtures.py 
        which will create the parquet files from CSV source files.
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

        shutil.rmtree(f"{LOCAL_DEV_STORAGE}/gold", ignore_errors=True)
        
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()


    def test_load_and_create_temp_views(self):

        source_level = "silver"
        list_source_tables = ["T_JOB", "T_JOBFIELDUPDATED", "T_TRUNK", "T_ASSIGNMENT"]
        schema = "TOPSv2"
        sql_string = "SELECT 1 FROM T_JOB UNION ALL SELECT 1 FROM T_JOBFIELDUPDATED UNION ALL SELECT 1 FROM T_TRUNK limit 5"

        # Calling the function to test
        load_and_create_temp_views(self.spark, source_level, list_source_tables, schema)

        # Assertions to check if the temp views are created successfully
        self.assertTrue(self.spark.sql("SHOW TABLES").where(f"upper(tableName) in {tuple(list_source_tables)}").count() == len(list_source_tables))


    def test_run_sql(self):
        # Test case for run_sql

        #Create temp views from Sample data
        source_level = "silver"
        list_source_tables = ["T_JOB", "T_JOBFIELDUPDATED", "T_TRUNK", "T_ASSIGNMENT"]
        schema = "TOPSv2"
        sql_string = "SELECT 1 FROM T_JOB UNION ALL SELECT 1 FROM T_JOBFIELDUPDATED UNION ALL SELECT 1 FROM T_TRUNK limit 5"
        load_and_create_temp_views(self.spark, source_level, list_source_tables, schema)

        # Call the function
        result_df = run_sql(self.spark, sql_string)

        # Assertions that the result DataFrame is not empty
        self.assertFalse(result_df.count() < 3)


 