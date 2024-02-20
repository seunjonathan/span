# Introduction 
This project is a PySpark command line application to process raw JSON data coming from API endpoints. The app is able to flatten json, transform it and load into a data lake in delta format. Both incremental upserting as well as full loads is supported. 

# Usage
Please read this section carefully.

The application accepts the following command line arguments:

Argument | Name | Required |Description
----|---|-----|----
-t | source_table_name | True | the name of the incoming table, e.g. `EVENTS`
-s | source_level | True | path to the source folder, e.g. `bronze`
-d | destination_level | True | path to the target folder, e.g. `silver`
-c | schema | True | schema, e.g. `PRISM`. A folder with this name must exist in the storage account
-x | flatten_instructions | True | a JSON string that specifies instructions for flattening the raw data
-f | field_types | False | a JSON string that defines which field names are to be considered for type casting.
-i | incremental | True | indicate with `y` or `n` whether the incoming data is to be incrementally added, `n` means a full overwrite
-k | pkey | False |for incrementally processed tables, the column name of primary key in source data
-w | watermark | False | for incrementally processed tables, the column name to be used as a checkpoint or watermark


# Further description of the `-x` parameter
The incoming JSON data needs to be flattened. No flattening code is hard coded into this application. Instead it must be passed in as a string containing a SQL select statement. An example of a SQL statement that can flatten the "TARGETS_SHORE_POWER_UTILIZATION" table would be for example:

```
select
       deleted_at
     , id
     , inserted_at
     , max_connect_after
     , max_disconnect_before
     , type
     , explode(vessel_ids) as vessel_id
from
   (
	  select
		 parameters.*, *
	  from (select target.* from json)
   )
```

During processing, the code loads the raw JSON into a temporary Spark view called _json_. Hence your SQL query must reference the base SQL table _json_. Following that you may `explode` or `expand col.*` as appropriate to flatten, extract and build out tabular contents as needed. You can even introduce derived columns. For example to build a primary key based upon two or more existing columns.

Here is an example of a flattening instruction:
```
 [
    {
        "destination_tablename": "MISSES_DUAL_FUEL_ENGINE_GAS_MODE",
        "flatten_command": "select ended_at, id,from.id as leg_from_id, from.name as leg_from_name, from.type as leg_from_type, to.id as leg_to_id, to.name as leg_to_name,to.type as leg_to_type,properties.engine as properties_engine,started_at, statistics.duration_min,consumer_name,amount as fuel_amount,fuel_name,unit as fuel_unit,source,fuel_oil_emissions,target.id as target_id, target.type as target_type, tenant_id, vessel_id,voyage.number as voyage_number from(select *,fuel_oil_consumption.consumer_name as consumer_name,fuel_oil_consumption.fuel_amount.*, fuel_oil_consumption.source from(select *, leg.*,statistics.* from(select entries.* from(select explode(entries) as entries from json))))"
    }
]
```

A string containing the above would be passed into the `-x (--flatten_instructions)` argument of this app. In the vast majority of cases, one source table will generate a single target table. However, notice that the flattening instructions are an array of JSON objects. This makes it possible to generate multiple tables from a single JSON object. This may be appropriate in cases of nested JSON in which the nested objects are to be flattened into separate tables to render a normalized view of the data.


# Further description of the `-f` parameter
Often REST endpoints format floating point numbers, integers and/or datetimes as JSON string objects. This is not ideal. To support casting them to more suitable types, the `--field_types` argument can be used. It is an optional parameter and it's format is as follows:
```
{
    'datetimes': ['LastChangedDate'],
    'doubles':['RateFuel', 'TotalCost'],
    'ints':['PortNumber']
}
```
Each object, `doubles`, `datetimes` and `ints` is a JSON list of case-insensitive field names. If that field name is found in the incoming data, it will be cast to `datetime`, `double` or `int` as appropriate. (Note that we prefer double to float since double is the type that `spark.json()` would return and since it uses double the number of bytes compared to float, it will work in all cases.)

## Caveats
* Attempting to cast a non-numeric string to an int or a double will result in a null value.
* Attempting to cast a string containing a double to an int will perform the cast by truncating the double value.
* Attempting to cast a string to a datetime will return a null datetime if the string is not a properly formed.
* If a column has already been ingested as a string, modifying the field type later on may not be effective. Instead follow these instructions: [Delta: change-column-type-or-name](https://docs.delta.io/latest/delta-batch.html#change-column-type-or-name) 

# Build and Test
To test the code locall-, run the unit tests using the VS Code test UI. All tests use sample JSON and are fully self contained. I.e. no external data connections are required.

`pytest` can also be used to run the unit tests at the command line. To install `pytest` in your local dev environment run the command:
```
pip install pytest
```

The application can also be invoked from the command line as shown in the example below:
```
 python spark_main.py -t TARGETS_SHORE_POWER_UTILIZATION -s bronze -d silver -c PRISM -x ' [{"destination_tablename": "TARGETS_SHORE_POWER_UTILIZATION","flatten_command": "select deleted_at, id, inserted_at, max_connect_after, max_disconnect_before, type, explode(vessel_ids) as vessel_id from (select parameters.*, * from (select target.* from json))"}]' -i y -k id
 ```

 ## Build Status
 The unit tests are automatically invoked whenever a new commit is made to the `main` branch. The status of those tests is shown below. If you observe failures, you should debug in your local dev environment. When doing so you should first run the tests at the command line using `pytest`

 [![Build Status](https://dev.azure.com/seaspan-edw/DataOps/_apis/build/status%2Fgeneric-curatejson-sparkapp?branchName=main)](https://dev.azure.com/seaspan-edw/DataOps/_build/latest?definitionId=8&branchName=main)

# Deploy
The app is intended to run in a Databricks environment and be invoked from a data factory pipeline. The file called `curate_json.py` should be uploaded to Databricks environment at the following location:
```
dbfs:///FileStore/pyspark-scripts/
```

# References
This section intentianally left empty.