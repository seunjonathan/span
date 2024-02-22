|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|26-October-2022|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Maureen Katarama|
|**Tickets**| #1512 <br> #1565 <br> #1664

[[_TOC_]]


# Introduction
This project is an initiative motivated by requirements coming from end users of ARAS. The use case is the need to execute complex SQL queries against ARAS tables to generate fact and dimension tables. The queries are written by ARAS end users who have expert knowledge in that data.

The standard approach would be to convert these SQL queries to PySpark code in Databricks and render the data to views in a `gold` database. This is however time consuming and adds a heavy workload to a very small team.

The proposed approach is to permit the same to be done in a self-serve fashion. Specifically to build a silver-to-gold pipeline into which end users can submit or drop their own pre-built, pre-tested SQL queries.

# Requirements
1. The pipeline shall allow an end user to drop a file containing a SQL query into a specific folder in a specific storage account
2. The SQL query shall be T-SQL compliant and already have been tested against views in the Synapse silver database
3. The pipeline shall execute all SQL queries found in the specific `drop` folder.
4. The result of SQL execution shall be data rendered into external tables (CETAS) available to end users in the Synapse gold database.


# Solution
## Orchestration Pipeline
The solution is based upon building an orchestration pipeline in Synapse that executes T-SQL scripts. The design from a PoC is shown.

![1.png](/.attachments/1-bcf35697-e8d9-48a1-b43b-8ae053bd6ef1.png =400x)

where `For Each SQL Script` is:
![2.png](/.attachments/2-5caf51b3-9e3e-4633-8c6a-68dde754b9c7.png)

Of interest here is the `Build CETAS Script` activity. This is what this looks like:

![3.png](/.attachments/3-35c42c07-e879-4998-8e0f-dfc5a093c372.png)

The script is dynamically built from a JSON file. This script essentially drops the external table if it already exists. It then creates an external table (CETAS) using a SQL script passed in as an object in the JSON file. (Note that the CETAS statements will fail if either the target storage folder already exists or the target table already exists. Hence the activities to remove CETAS folder/contents.)

## Format of the JSON
The JSON file must be of the following format:
![4.png](/.attachments/4-4f04d9e2-053b-491f-8b3a-b40ae35dd93b.png)

Object | Description
-------|------------
`name_of_script`| Unused. But should be included as a way of referring back to the original .sql file 
`schema` | The schema to be used for the external table that will be created in the gold database.
`table_name` | The name of the external table to be created in the gold database.
`schedule` | Each script can specify a schedule for when it should be ran. This field expects a list of hours as strings. If left empty, the script will never run. Example: `"schedule" : []"` is an empty list. `"schedule" : ["09", "12", "15"]` would run the script at 9am PST, 12pm PST and 3pm PST. Note that the hour must be a two digit string. So `"9"` would not be detected. The scripts **cannot** be executed more frequently than once an hour. 
`script` | The SQL query that defines the contents of the target external table. It should reference views in the silver database. This query should first be tested in SSMS. 
`source_db` | **Optional**. This field would be typically used in the case that the source tables are not in `silver` but in `gold` instead say.

## Drop Box
In the PoC the drop box location is in the `processed` container of `adlsedwdev` in a folder named `CETAS_scripts`. The file must have the `.json` extension. Any number of files can be placed into this folder.

* The folder is in the same location and has the same name in the production environment. The `prod` storage account is `aldsedwprod`

* In the production environment, the trigger is automatic and as follows:
![5.png](/.attachments/5-f974d10e-c846-4353-bf6c-8cca49a4fe3d.png =450x)
Note that for `ARAS`, the tables are refreshed every 2 hours at `6:00`, `8:00`, `10:00`, `12:00`, `14:00` and `16:00` each weekday. 

## External Tables
The screenshot below shows an example of the external tables that created.

![6.png](/.attachments/6-46ed5012-957b-418f-9725-1d780c8497ec.png =300x)

## Troubleshooting
If the pipeline fails with the error `"External table references 'DATA_SOURCE' that does not exist."` it could be that the source has not been defined in the source or target database. In which case please run in a Synapse script this command:
```
CREATE EXTERNAL DATA SOURCE DeltaLakeStorage 
WITH (
	LOCATION = 'abfss://processed@adlsedwprod.dfs.core.windows.net'
)
```

It's also likely that the `FILE_FORMAT` is undefined. In which case run:
```
CREATE EXTERNAL FILE FORMAT ParquetFormat WITH ( FORMAT_TYPE = PARQUET );
``` 

  