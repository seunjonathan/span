|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|11-January-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| 

[[_TOC_]]

# Introduction
This Runbook describes gold tables that are built on top of the silver `TOPSv2` tables curated by the new TOPSv2 ETL.

# Gold Tables
Item # | Name of Table| Name of Project in ADO | Name of Deployable PySpark Script | Location of resulting Delta table
--------|----|-----------|-------------|--------
1 |`tops.vw_BOL` | `generic-sql2delta-sparkapp` | `curate_sql2delta.py` | `processed/gold/TOPSv2/T_BOL`
2 |`tops.vw_SAILING`| `generic-sql2delta-sparkapp` | `curate_sql2delta.py` | `processed/gold/TOPSv2/T_SAILING`
3 |`tops.vw_NearRealTime_BOL`| `generic-sql2delta-sparkapp` | `curate_sql2delta.py` | A view that merges `transient@silver/TOPSv2/T_BOL` and `processed@silver/TOPSv2/T_BOL`
4 |`tops.vw_NearRealTime_SAILING`|`generic-sql2delta-sparkapp` |`curate_sql2delta.py`|A view that merges `transient@silver/TOPSv2/T_SAILING` and `processed@silver/TOPSv2/T_SAILING`
5 |`tops.vw_NearRealTime_LOCATION`| `generic-sql2delta-sparkapp`|`curate_sql2delta.py`|A view that augments`transient@silver/TOPSv2/T_LOCATION` by adding static GPS location information for ferry terminals to it.
6 |`tops.vw_MISSED_TRAILER_METRICS`| `generic-sql2delta-sparkapp`|`curate_sql2delta.py`|A view that exposes `transient@silver/TOPSv2/MISSED_TRAILER_METRICS`.
7 |`tops.vw_TURNAROUND_METRIC`| `generic-sql2delta-sparkapp`|`curate_sql2delta.py`|A view that exposes `transient@silver/TOPSv2/TURNAROUND_METRIC`.
8 |`tops.vw_VESSEL`| `generic-sql2delta-sparkapp`|`curate_sql2delta.py`|A view that exposes `transient@silver/TOPSv2/VESSEL`.
9 |`tops.vw_CUSTOMER`| `generic-sql2delta-sparkapp`|`curate_sql2delta.py`|A view that exposes `transient@silver/TOPSv2/CUSTOMER`.


# High Frequency Data Update Requirements
The SMG Ferry business has requirements for sailing related data such that upon query, it shall be no older than 5 minutes. The technical approach adopts a Lambda architecture whereby both a _batch_ and _fast_ path are used to obtain the data.

## Batch vs Realtime
This diagram enumerates the tables involved. 
![image.png](/.attachments/image-047c84b4-65f9-4ee0-a770-621ea826db60.png =x300)

### tops.vw_BOL & tops.vw_SAILING
These two tables are created using pre-existing SQL queries that were present in the EDW solution. While in EDW, the queries were executed on the source TOPS SQL Server, in SMG they are ported over to Databricks and run directly against locally curated silver TOPS tables. The frequency of refresh is aligned with the data factory ETL frequency for TOPS (every 2hrs).

### tops.vw_FastTrack_BOL, tops.vw_FastTrack_SAILING & tops.vw_FastTrack_LOCATION
These tables are procured by a function app that submits SQL queries directly to the on-premise TOPS SQL server. These are the same SQL queries that appear in the EDW solution. However adjusted to fetch data for only the last 5 minutes. Which is the frequency at which the function app is scheduled to run. Except for `vw_FastTrack_Location`, data is retained for a period of 2 hours only. At which point, the same data would be fetched by the batch path. The requirements for `vw_FastTrack_Location` necessitate retention of only the most recent GPS location of a ferry. There is no need to maintain a history of locations.

Since the data is fetched directly from source, it lands in the silver layer. Persisted in a special `transient` container, rather than `bronze`. Which would normally be used to land data from source.

### tops.vw_NearRealTime_BOL, tops.vw_NearRealTime_SAILING & tops.vw_NearRealTime_LOCATION
These tables appear in the gold layer of Synapse and exist purely as view definitions. The data backing them is not materialized. Instead coming from multiple sources as follows:

 #|Table | Description
---|---|---
1 | `tops.vw_NearRealTime_BOL` | A view Synapse definition that merges together the contents of `tops.vw_T_BOL` (batch) & `tops.vw_FastTrack_BOL` (fast)
2 | `tops.vw_NearRealTime_SAILING` | A view Synapse definition that merges together the contents of `tops.vw_T_SAILING` (batch) & `tops.vw_FastTrack_SAILING` (fast)
3 | `tops.vw_NearRealTime_LOCATION` | A view Synapse definition that augments the contents of `tops.vw_FastTrack_LOCATION` by adding the GPS locations of the four SMG Ferry terminals.


## Requirements
Here are the requirements provided in terms of the SQL queries used.

# | Table | Server | SQL Query
---|---|---|--
1 | `tops.vw_BOL` | Databricks | [SQL Query for vw_BOL](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_BOL)
2 | `tops.vw_SAILING` | Databricks | [SQL Query for vw_SAILING](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_SAILING)
3 | `tops.vw_FastTrack_BOL` | TOPS| [SQL Query for vw_FastTrack_BOL](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_FastTrack_BOL)
4 | `tops.vw_FastTrack_SAILING` | TOPS | [SQL Query for vw_FastTrack_SAILING](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_FastTrack_SAILING)
5 | `tops.vw_FastTrack_LOCATION` | TOPS | [SQL Query for vw_FastTrack_LOCATION](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_FastTrack_LOCATION)
6 | `tops.vw_MISSED_TRAILER_METRICS` | Databricks | [SQL Query for vw_MISSED_TRAILER_METRICS](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_MISSED_TRAILER_METRICS)
7 | `tops.vw_TURNAROUND_METRIC` | Databricks | [SQL Query for vw_TURNAROUND_METRIC](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_TURNAROUND_METRICS)
8 | `tops.vw_VESSEL` | Databricks | [SQL Query for vw_VESSEL](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_VESSEL)
9 | `tops.vw_CUSTOMER` | Databricks | [SQL Query for vw_CUSTOMER](/Data-Ops-Wiki/Runbook-TOPS-v2/Runbook-TOPS-v2-Gold-ETL/SQL-Query-for-vw_CUSTOMER)




