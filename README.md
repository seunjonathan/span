# Introduction 
* This Pyspark script offers a generic mechanism for upserting incoming parquet data into a corresponding Delta table.
* This offers a generic code for taking a sql query and renaming columns in table before upserting

# Build and Test
Unit tests are provided which cover the following methods:

    1. upsert_data_into_delta()
    2. column_rename()

These drivers are provided:

    1. curate_parquet.py
    
 provided which can be used to perform manual testing.

The project delivers a PySpark application that can be ran locally using the test fixtures provided.
To create the test data, simply run:
```
   python create_test_fixtures
```

This will create parquet tables in a local bronze folder. Which are then accessed by the unit test cases.

The unit test case be ran from the VS Code UI.

## Build Status