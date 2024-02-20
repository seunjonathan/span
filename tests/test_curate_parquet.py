'''
    This file implements unit tests
'''

import os
import shutil
import unittest
import pyspark

from delta import configure_spark_with_delta_pip, DeltaTable
from delta.tables import DeltaTable
from curate_parquet import get_path_to_table, upsert_data_into_delta, column_rename
                            

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

        shutil.rmtree(f"{LOCAL_DEV_STORAGE}/silver", ignore_errors=True)
        
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()


    def test_upsert_data(self):
        '''
            This is to test inserting data into delta lake
        '''
        bronze_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE1', 'bronze/TOPSv2', '')
        silver_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE', 'silver/TOPSv2', '')
    
        path = os.path.join(bronze_path, '*.parquet')
        updated_df = self.spark.read.parquet(path)
    
        key_columns = ['pk_CustomerType_in']
        partition_columns = None  # Assuming no partitioning
        is_incremental = 'y'
        upsert_data_into_delta(self.spark, updated_df, silver_path, key_columns, is_incremental, partition_columns )
        
        # Assuming silver_path is the path to your Delta table
        delta_table = DeltaTable.forPath(self.spark, silver_path)
        last_commit = delta_table.history(1).collect()[0]

        # Check the operation type in the last commit
        operation_type = last_commit.operation

        # Assert based on the operation type
        self.assertEqual(operation_type, 'WRITE')  # 'WRITE' corresponds to an append operation



    def test_upsert_incremental_data(self):
        '''
            This is to test upserting data into delta lake
        '''
        bronze_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE2', 'bronze/TOPSv2', '')
        silver_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_CUSTOMERTYPE', 'silver/TOPSv2', '')
    
        path = os.path.join(bronze_path, '*.parquet')
        updated_df = self.spark.read.parquet(path)

        # Key Columns should always be arrays
        key_columns = ['pk_CustomerType_in']
        partition_columns = None  # Assuming no partitioning
        is_incremental = 'y'
        upsert_data_into_delta(self.spark, updated_df, silver_path, key_columns, is_incremental, partition_columns )

        #upserting into delta lake
        upsert_data_into_delta(self.spark, updated_df, silver_path, key_columns, is_incremental, partition_columns )   

        # Assuming silver_path is the path to your Delta table
        delta_table = DeltaTable.forPath(self.spark, silver_path)
        last_commit = delta_table.history(1).collect()[0]

        # Check the operation type in the last commit
        operation_type = last_commit.operation

        # Assert based on the operation type
        self.assertEqual(operation_type, 'MERGE')  # 'WRITE' corresponds to an append operation



    def test_upsert_fulload_data(self):
        '''
            This is to test full load data insert into delta lake
        '''
        bronze_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'bronze/TOPSv2', '')
        silver_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'silver/TOPSv2', '')
    
        path = os.path.join(bronze_path, '*.parquet')
        updated_df = self.spark.read.parquet(path)
        key_columns = None
        partition_columns = None  # Assuming no partitioning
        is_incremental = False
        upsert_data_into_delta(self.spark, updated_df, silver_path, key_columns, is_incremental, partition_columns )

        # upserting as full load
        upsert_data_into_delta(self.spark, updated_df, silver_path, key_columns, is_incremental, partition_columns )
        # Assuming silver_path is the path to your Delta table
        delta_table = DeltaTable.forPath(self.spark, silver_path)
        last_commit = delta_table.history(1).collect()[0]

        # Check the operation type in the last commit
        operation_type = last_commit.operation

        # Assert based on the operation type
        self.assertEqual(operation_type, 'WRITE')  # 'WRITE' corresponds to an append operation


    def test_rename_column(self):
        '''
            This is for unit testing renaming a column name
        '''
        bronze_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'bronze/TOPSv2', '')
       
        path = os.path.join(bronze_path, '*.parquet')
        source_df = self.spark.read.parquet(path)
        #renaming_instructions = '[{"table_name":"T_ASSIGNMENTRESERVATIONLOG","renaming_instructions":"select *,fk_Customer_in as fk_Customer from T_ASSIGNMENTRESERVATIONLOG"}]'
        renaming_instructions = '[{"table_name":"T_ASSIGNMENTRESERVATIONLOG","renaming_instructions":"select pk_AssignmentReservationLog_in, fk_Customer_in as fk_Customer, Added_dt, fk_Assignment_in, fk_Trunk_in, UsedReservationTEU_dc from T_ASSIGNMENTRESERVATIONLOG"}]'

        updated_df = column_rename(self.spark, source_df, renaming_instructions, 'T_ASSIGNMENTRESERVATIONLOG')
        
        columns = updated_df.columns
        expected_column_1 = 'fk_Customer'
        self.assertTrue(expected_column_1 in columns, f'--* columns name {expected_column_1} not found in dataframe')


    def test_rename_column_null_query(self):
        '''
            This is for unit testing renaming a column name
        '''
        bronze_path = get_path_to_table(self.spark, DUMMY_BASE_URL, 'T_ASSIGNMENTRESERVATIONLOG', 'bronze/TOPSv2', '')
       
        path = os.path.join(bronze_path, '*.parquet')
        source_df = self.spark.read.parquet(path)
        renaming_instructions = '[{"table_name":"","renaming_instructions":""}]'

        updated_df = column_rename(self.spark, source_df, renaming_instructions, 'T_ASSIGNMENTRESERVATIONLOG')
        
        columns = updated_df.columns
        expected_column_1 = 'fk_Customer'
        self.assertNotEqual(expected_column_1 in columns, f'--* columns name {expected_column_1} not found in dataframe')