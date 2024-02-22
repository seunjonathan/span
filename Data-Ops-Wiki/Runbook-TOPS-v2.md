|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|15-January-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2906 <br> #2907 <br> #2862 <br> #2863 <br> 

[[_TOC_]]

# Introduction
[TOPS](https://www.fargosystems.com/products/tops-tms/) is an enterprise transport management system used by the Seaspan Marine Group (SMG) to operate and manage a commercial ferry business. SMG Ferries operates a fleet of vessels that connect two terminals on the Vancouver mainland to two other terminals on the east coast of Vancouver Island. Customer and voyage data is managed by an on-prem instance of the TOPS system. This includes a database hosted by a MS SQL Server. This runbook describes the design, deploy and requirements of a data pipeline responsible for procuring and curating this data in a timely fashion into the SMG data lake hosted in Azure.

TOPS v2 ETL represents a wholesale rebuild of the existing pipeline. While the current mechanism is largely functioning without error, the following reasons offer strong motivations for upgrading to a new solution:
1. Existing solution adopts a practice of fully re-loading each of the 37 TOPS tables each time. This is wasteful of Azure storage space, Azure compute and places an unnecessary burden on the production TOPS SQL server, which is also supporting an operational mission-critical application. We believe that most of these tables can be ingested incrementally. Leading to a faster, cheaper & more efficient solution.
2. Data proliferation. Many tables are materialized almost verbatim in the silver **and** the gold layer. Currently these consume upwards of 12 terabytes each! The modern practice is for gold to host tables which represent joined or aggregated forms of other tables. Not simply a copy of what is in silver.
3. The code that curates the tables comprises a poorly written set of Databricks notebooks. By poor, we mean that the code was not reviewed, lacks accompanying unit tests, is not documented, and does not adhere to commonly accepted Python coding guidelines. This makes it costly to maintain.
 
# Scope
The scope of this solution is limited to the ingestion of the following TOPS tables:

   ```
    T_APPOINTMENT
    T_ASSIGNMENT
    T_ASSIGNMENTRESERVATIONLOG
    T_ASSIGNMENTSTATUS
    T_ASSIGNMENT_CUSTOMER
    T_ASSIGNMENT_TRAILER
    T_CHARGETYPE
    T_COMPANY
    T_CONSIGNMENT
    T_CONTAINERTYPE
    T_CUSTOMER
    T_CUSTOMERTYPE
    T_E1BI_CUSTOMERGROUPING
    T_E1BI_JOBEXT
    T_HAZARD
    T_JOB
    T_JOBCATEGORY
    T_JOBSUMMARY
    T_JOB_MASTERLOG
    T_MASTERLOG
    T_MOVEMENTMODE
    T_OTG_POD
    T_ROUTE
    T_SALE
    T_SALEINVOICE
    T_TRAILERTYPE
    T_TRANSPORTPLAN
    T_TRANSPORTPLAN_CUSTOMER
    T_TRANSPORTPLAN_TRAILER
    T_TRUCK
    T_TRUNK
    T_TRUNKSUMMARY
    T_USER
    T_WAYPOINT
    T_WEB_CUSTOMERLOGIN
    V_WC_BI_ASSIGNEMNT
    V_WC_BI_SAILINGANALYSIS
   ```

Note that some of these are dimension tables and some are facts. 

# Requirements
The requirements include but are not limited to those shown in the table below.

# | Requirement | Description
---|---|---
1 | Procurement | The ETL shall procure raw data from the TOPS SQL Database. Raw data shall be archived once processed and stored indefinitely.
2 | Curation | The ETL shall curate raw data into a `silver` layer.
3 | Incremental | The ETL shall support _incremental_ curation of data.
4 | Data transformation | The ETL shall support transformation of raw data into Delta formatted data
5 | Serve | The ETL shall serve the data to the end user via a Synapse SQL Serverless endpoint
6 | Scheduling | It shall be possible to independently configure the frequency with which different tables are procured.
7 | Retention | The ETL shall move all raw data in the bronze layer from the _hot_ tier to an _archive_ tier after _n_ days.
8 | Table naming convention | The naming of tables curated in the silver layer will include a prefix that identifies them as dimension or fact tables. E.g. `vw_FACT_Appointment`, or `vw_DIM_Customer`. All tables will belong to the `tops` schema.
9 | Monitoring | Metrics associated with the ETL shall be tracked and made available via a reporting dashboard.

# Design
## Azure Infrastructure Design
![1.png](/.attachments/1-eb3e0b23-8eec-41a2-a9d5-87fa25c8b455.png =700x)


### Components
Name | Component | Description
------|-----|--------
`adfv2-smg-tops-prod` | Data Factory | This data factory is used to host all TOPS related pipelines, including not just TOPS but also PRISM. _Ref_: [Runbook Prism](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20Data%20Ops%20Wiki/125/Runbook-Prism)
`dbw-smg-prod` | Databricks | Used to host PySpark code needed to curate data into Delta tables
`adlssmgprod` | Azure Storage Account | Raw data will land at `landing@bronze/TOPS`. Curated silver data will go to `processed@silver/TOPS`. Raw data will be archived to `processed@bronze/TOPS`
`kv-smg-prod` | Key vault | Sensitive data such as TOPS Db access credentials will be secured in this key vault.
`syn-smg-prod` | Synapse | SQL scripts to create views will be hosted in a Synapse server.
`law-smg-prod` | Log Analytics Workspace | Logging of metrics to monitor ETL progress and accuracy will be persisted in here.
`curateparquet-sparkapp` | PySpark Code | This is a single item of PySpark code responsible for taking the raw data (in parquet format) and upserting it into a target Delta formatted table. It is involved in the bronze to delta curation.
`fa-tops-prod` | Function App | A Python function app that is used to fetch data directly from the TOPS Db in order to support near real time use cases.
`asp-smg-prod` | App Service Plan | This provides the compute service required to run non-consumption plan function apps.
`generic-sql2delta-sparkapp` | PySpark Code | This spark app is used to execute SQL statements. This is the first SMG ETL which will generate gold tables from aggregations of silver tables directly using (Databricks flavour) SQL.



### Resource Groups

Resource Group | Description
------ | -----
`TODO: Describe rgs`
 

## ETL Design
The ETL design adopts the familiar _medallion_ design pattern adopted by other SMG pipelines. In general a data factory pipeline orchestrates data procurement into `bronze`, curation into `silver` and then `gold`. The `bronze` to `silver` transformation is implemented by a **single** PySpark application (version controlled in the `curateparquet-sparkapp` repository).

`silver` to `gold` transformations will be built as required. Each is expected to be realised by its own PySpark application.

The pipeline is scheduled to run every two hours.

### Data Factory Pipeline Design
`ADF PIPELINE`: The pipeline is designed in such a way that it handles both the incremental and full load tables. These are processed based on the configuration details extracted from `cfgBronze` at runtime.

A common checkpoint timestamp used in many incremental tables is the `LastUpdate_ts` column, for other tables without this column, other timestamp column are used. No timestamp column (_None_) is considered for tables that are full load.

Consider a snapshot of `CfgBronze` as it relates to this.

![image.png](/.attachments/image-c9781ae7-92c0-4ac7-b19f-c33b684916be.png =700x)

The general category of table processed are:

1. Tables with `LastUpdate_ts` as Watermark Column.
1. Tables with `Other timestamp` as Watermark Column.
1. Tables with `None` as Watermark Column (Full Load)

The ADF pipeline is then processed as per the details extracted from `CfgBronze`.



![image.png](/.attachments/image-2c8396ea-8a59-4852-ad5a-e1999b7f6666.png)

 

 

### Near Real Time Requirements
Operational requirements include the need to update data at a far higher frequency than twice-hourly. As an example, in the existing TOPS v1 deployment, the refresh rate is every 5 minutes. This is referred to as _near real time_.

The requirements are for three different tables which are to update on a minimum frequency of 5 minutes. The contents of each table is defined by a SQL query defined against the source TOPS Server (ref [1]). These tables are referred to as follows:

1. `BOL`
2. `Sailing`
3. `Location`

#### BOL & Sailing Tables
The contents of these tables are to be updated or inserted into every 5 minutes 

#### Location Table
The requirements are to fetch and store the most recent GPS locations of the vessels every 5 minutes. There is no requirement to store historical GPS locations. The location table also contains the GPS locations of the 4 SFC ferry terminals. These values are static, but never-the-less are to appear in the same table.

## Near Real Time Design
Instead of increasing the trigger frequency of an ADF pipeline, the solution proposed here adopts the _lambda_ data engineering design pattern _ref_: [lambda-architecture](https://www.databricks.com/glossary/lambda-architecture).

![2.png](/.attachments/2-c678f5d6-3750-4b7f-ba70-86538471978b.png =600x)

### Design Highlights
* An ADF pipeline delivers data into the silver layer in a batch manner.
* A light-weight function app is used to _stream_ data into bronze layer. Only differentials since the last run are fetched.
* Streamed data is discarded once the same has been delivered via batch.
* A view in Synapse merges or unifies the batch and streamed data. Which will appear to the end user as a single, rapidly updating table.
* Running a function app at high frequency is deemed to be cheaper, more efficient and more effective than running a data factory pipeline at high frequency. This is because little to no processing is performed along the _streaming_ path and data is persisted close to it's raw form.

#### Design: Fast Path
A function app, called `fa-tops-dev/prod` implements functionality to:
1. Query the TOPS server directly
2. Store the response as a parquet file
3. Delete parquet files older than a pre-configured time
4. The SQL query, expiry time, SQL connection strings and other parameters are abstracted outside of the code and exist as configuration parameters on the function app.
5. The function app fetches and stores data for all three tables mentioned earlier.


#### Design: Batch Path 
Since there is no need to store historic location data, the batch path is not involved in curating the location table.

For the BOL and Sailing tables, the fast path is to retain only the most recent 2 hours of data. The data factory triggers every two hours and is the primary mechanism for long term curation of the data in these tables. These two tables are aggregations of silver TOPS tables and will be implemented as such. The tables are built using a new 

##### Generic SQL to Delta Spark App
![3.png](/.attachments/3-b6ddeb32-0c81-4960-961b-f3450ccfc4f3.png =150x) As part of this design a new generic Spark App was developed (ref: [2]) The intent is for this app to support the general construction of gold tables using (Databricks) SQL queries against silver tables. The first two uses will be for the construction of the BOL and Sailing table. The Spark App materializes the data in Delta format in the gold folder of the processed container. The Spark App is triggered from a Data Factory pipeline. Parameters for the Spark App are persisted as parameters of the pipeline.

![4.png](/.attachments/4-c0579ca9-7985-4f15-9005-3d9797d77c0d.png =500x)

It is hoped that this becomes a standard for all future silver to gold aggregations.


### Summary of Near Real Time Data Sources, Sinks and Views
The following table is provided to help in identifying the views and storage account folders that participate in the near real time solution.

-| Path(batch/fast)|Source | Sink | Sink Data Format | View Name | Comments
--|---|---|---|---|---|--
`BOL` Table | _fast_ | TOPS SQL server | container: `transient`. <br>folder: `silver/TOPSv2/T_BOL` | Parquet | `[silver].[tops].[vw_FastTrack_BOL]` | _Files are persisted for 2 hours. To match frequency of batch processing._
`Sailing` Table| _fast_ | TOPS SQL server | container: `transient`. <br>folder: `silver/TOPSv2/T_SAILING` | Parquet | `[silver].[tops].[vw_FastTrack_SAILING]` | _Files are persisted for 2 hours. To match frequency of batch processing._
`Location` Table | _fast_ | TOPS SQL server | tcontainer: `transient`. <br>folder: `silver/TOPSv2/T_LOCATION` | Parquet | `[silver].[tops].[vw_FastTrack_LOCATION]` | _Only the last fetched data is persisted_
`BOL` Table | _batch_ | multiple tables in [silver].[tops] | container: `processed`. <br>folder: `gold/TOPSv2/T_BOL` | Delta | `[gold].[tops].[vw_BOL]` | -
`Sailing` Table | _batch_ | multiple tables in [silver].[tops] | container: `processed`. <br>folder: `gold/TOPSv2/T_SAILING` | Delta | `[gold].[tops].[vw_SAILING]` | -
`Location` Table | _batch_ | - | - | - | - | _Location data is only fetched via the fast path_

The `BOL` and `Sailing` _fast_ and _batch_ views are unified and each is made available via a single view.

 -|Source Views | Unified View
--|---|---
`BOL` Table | [silver].[tops].[vw_FastTrack_BOL], [gold].[tops].[vw_BOL] | [gold].[tops].[vw_NearRealTime_BOL]
`Sailing` Table | [silver].[tops].[vw_FastTrack_SAILING], [gold].[tops].[vw_SAILING] | [gold].[tops].[vw_NearRealTime_SAILING]
`Location` Table | [silver].[tops].[vw_FastTrack_SAILING] | -

#### Design: Union of Views
The following is an example of the SQL used to unify the BOL _fast_ and _batch_ views.

 
    CREATE OR ALTER VIEW [tops].[vw_NearRealTime_BOL] AS
    SELECT
         [BOL_Number]
        ,[Sailing_ID]
        ,[Container_Type]
        ,[Assignment_Status]
        ,[Hazardous_Goods]
        ,[Trailer_Length]
        ,[Trailer_Overhang_Front]
        ,[Trailer_Overhang_Back]
        ,[Signature_Date_Time]
        ,CAST([Signature_Date_Time] AS DATE) AS [Signature_Date]
        ,CAST([Signature_Date_Time] AS TIME) AS [Signature_Time]
        ,[Actual_Picked_Up_Date_Time]
        ,CAST([Actual_Picked_Up_Date_Time] AS DATE) AS [Actual_Picked_Up_Date]
        ,CAST([Actual_Picked_Up_Date_Time] AS TIME) AS [Actual_Picked_Up_Time]
        ,[Route]
        ,[Category]
        ,[Added_Date]
        ,[Preferred_Pickup_Date_Time_official]
        ,CAST([Preferred_Pickup_Date_Time_official] AS DATE) AS [Preferred_Pickup_Date_official]
        ,CAST([Preferred_Pickup_Date_Time_official] AS TIME) AS [Preferred_Pickup_Time_official]
        ,[Preferred_Pickup_Date_Time]
        ,CAST([Preferred_Pickup_Date_Time] AS DATE) AS [Preferred_Pickup_Date]
        ,CAST([Preferred_Pickup_Date_Time] AS TIME) AS [Preferred_Pickup_Time]
        ,[Deleted_Date]
        ,[DG_Authorized]
        ,[Status]
        ,[pk_Job_in]
        ,[fk_Customer_in]
        ,[fk_MovementMode_in]
        ,[Unit_Number]
        ,[Reservation_used_TEU]
        ,[Refresh_Time_UTC]
    FROM (
        select 
            *,
            ROW_NUMBER () OVER (PARTITION BY BOL_Number ORDER BY Refresh_Time_UTC desc) as rn
        from (
            select * from [gold].[tops].[vw_BOL]
            UNION
            select * from [silver].[tops].[vw_FastTrack_BOL]
        ) c
    ) d
    where rn = 1
    GO
   
### Other Gold Tables.

Aside the Nearrealtime tables, the other Gold tables created #3195 are:

- MISSED_TRAILER_METRICS
- TURNAROUND_METRICS

They were deployed using the already developed process (triggering curate_sql2delta.py via the existing ADF pipeine).

![image.png](/.attachments/image-14e6af0b-6e70-4c52-ae7a-a954de9825d6.png)

These tables are similarly available in the Gold layer.

- [gold].[tops].[vw_MISSED_TRAILER_METRICS]
- [gold].[tops].[vw_TURNAROUND_METRICS]


## Data Serving
1. All curated data is served via Synapse SQL Serverless.
2. The production endpoint is `syn-smg-prod-ondemand.sql.azuresynapse.net`.
3. Data will appear in the `silver` database under the `tops` schema.
4. As with Towworks v2, configuration and checkpointing data associated with TOPS table is persisted to an Azure Table Store called `cfgBronze` which appears in `adlsdsmgdev/adlssmgprod`

# Deployment
`TODO: Adjust the below for TOPSv2`
1. Upload [curate_parquet2delta.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) to `dbfs:/FileStore/pyspark-scripts`
2. Provision `cfgBronze`. The output of #2875 can be used to guide the contents of this table.

# Data Sources & Sinks
## Data Sources

|Name|Source|Description|Sample|
|--|--|--|--|
TOPS Db |`jdbc:sqlserver://van-ss-sql15ag.seaspan.com:1433;databaseName=TOPSSEASPAN_PROD` | On premise MS SQL Server used to back the TOPS Operational Application | N/A


## Data Sinks

The following describe the data generated by the ETL:
|Name|Sink|Description|Sample|
|--|--|--|--|
Bronze landing zone| `adlsedwprod@landing/bronze/TOPS/<table-name>` | Raw data obtained from source, stored as-is. | N/A
Bronze archive zone| `adlsedwprod@processed/bronze/TOPS/<table-name>` | Post processing, raw data is archived indefinitely | N/A
Silver zone| `adlsedwprod@processed/silver/TOPS/<table-name>` | Source data is processed, converted to delta format and merged to the target folder | N/A
Gold zone| `adlsedwprod@processed/gold/TOPS/<report-name>` | Data from multiple sources/tables is aggregated or joined together to form tables that support business requirements.| N/A


### Bronze to Silver
`TODO` 

# Troubleshooting and Maintenance
## Fast Path Data
When correctly functioning, `fa-tops-prod` should be delivering new files every 5 minutes into:

      transient@silver/TOPSv2/T_BOL
      transient@silver/TOPSv2/T_SAILING
      transient@silver/TOPSv2/T_LOCATION

The first two folders are expected to contain 2 hours of data, with files older than 20 hours being automatically removed. The last, `T_LOCATION` folder is expected to only ever contain a single file. Representing data received within the last 5 minutes.

## Promoting Content from `Dev` to `Prod`
No automatic mechanism (e.g. via ADO CICD Release Pipeline) exists. The recommended approach is instead to perform manual deployment. The following notes should help:
1. _Azure Data Factory_: Manual deployment is performed using the ARM template.
1.1 From `adfv2-tops-dev` export the ARM template
1.2 Import into `adfv2-tops-prod`, remembering to modify `dev` specific linked service parameters. e.g. the storage account reference. 
1.3 Remember to configure `adfv2-tops-prod` to use the shared self-hosted integration runtime. _Ref_: [access-to-on-prem-tops-sql-server-from-data-factory](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20DataOps.wiki?wikiVersion=GBwikiMaster&_a=edit&pagePath=/Data%20Ops%20Wiki/Runbook%20TOPS%20v2&pageId=289#access-to-on-prem-tops-sql-server-from-data-factory)
2. _cfgBronze_
2.1 The `TOPS` partition needs to be deployed only once. The recommended approach for initial deployment to `prod` is via the `export` / `import` feature available in the `Azure Data Explorer` app.
3. _Azure Function App_:
3.1 From VS Code, open the `topsv2-functionapp` project and switch to the `main` branch.
3.2 From the `Azure` extension, initiate deployment to `fa-tops-prod`. Upon completion, VS Code will prompt you to upload settings. Select this option.
3.3 From the Azure portal, monitor the function app to verify that it is running successfully.
3.4 For initial deployment, you will need help from WashCorp IT to configure the network settings of the function app to include this hybrid connection `hyc-van-ss-sql15ag`. This is how the function app is able to access the on-prem server at `van-ss-sql15ag.seaspan.com : 1433`. _Ref_: #2975

# Scheduling Pipeline Runs

|Table Name| Schedule| Description|
|--|--|--|
|T_APPOINTMENT|Runs Bi-Hourly| 
|T_ASSIGNMENT |Runs Bi-Hourly| For this table Primary_Key in _cfgBronze_ is **Sailing_ID** rather than pk_Assignment_in as we are renaming some column names for this table as per requirement.|   
|T_ASSIGNMENTRESERVATIONLOG| Runs Bi-Hourly|
|T_ASSIGNMENTSTATUS| Scheduled to run daily once at 02/03|
|T_ASSIGNMENT_CUSTOMER| Runs Bi-Hourly|
|T_ASSIGNMENT_TRAILER| Runs Bi-Hourly|
|T_CHARGETYPE| Runs Bi-Hourly|
|T_COMPANY| Scheduled to run daily once at 02/03|
|T_CONSIGNMENT| Runs Bi-Hourly|
|T_CONTAINERTYPE| Scheduled to run daily once at 02/03|
|T_CUSTOMER| Scheduled to run daily once at 02/03|
|T_CUSTOMERTYPE| Scheduled to run daily once at 02/03|
|T_E1BI_CUSTOMERGROUPING| Runs Bi-Hourly|
|T_E1BI_JOBEXT| Runs Bi-Hourly|
|T_HAZARD| Runs Bi-Hourly|
|T_JOB| Runs Bi-Hourly|
|T_JOBCATEGORY| Scheduled to run daily once at 02/03|
|T_JOBSUMMARY| Runs Bi-Hourly|
|T_JOB_MASTERLOG| Runs Bi-Hourly|
|T_MASTERLOG| Runs Bi-Hourly|
|T_MOVEMENTMODE| Scheduled to run daily once at 02/03|
|T_OTG_POD| Runs Bi-Hourly|
|T_ROUTE| Scheduled to run daily once at 02/03|
|T_SALE| Runs Bi-Hourly|
|T_SALEINVOICE| Runs Bi-Hourly|
|T_TRAILERTYPE| Scheduled to run daily once at 02/03|
|T_TRANSPORTPLAN| Scheduled to run daily once at 02/03|
|T_TRANSPORTPLAN_CUSTOMER| Runs Bi-Hourly|
|T_TRANSPORTPLAN_TRAILER| Runs Bi-Hourly|
|T_TRUCK| Scheduled to run daily once at 02/03|
|T_TRUNK| Runs Bi-Hourly|
|T_TRUNKSUMMARY| Runs Bi-Hourly|
|T_USER| Runs Bi-Hourly|
|T_WAYPOINT| Runs Bi-Hourly|
|T_WEB_CUSTOMERLOGIN| Runs Bi-Hourly|
|V_WC_BI_ASSIGNEMNT| Runs Bi-Hourly|
|V_WC_BI_SAILINGANALYSIS| Runs Bi-Hourly|


# Appendix
## Access to On-Prem TOPS SQL Server from Data Factory
* This image illustrates how to access the self-hosted (shared) Integration Runtime from adfv2-edw-prod/dev:
<IMG  src="https://dev.azure.com/seaspan-edw/389e7261-06a8-4ed2-b07e-f354ad51ff21/_apis/wit/attachments/0392a015-bb83-4abd-a954-f2f59944f786?fileName=image.png"/>

# References
1. SQL queries for near real time feature: [near-real-time-queries.sql](/.attachments/near-real-time-queries-5d29d02c-a785-4551-9d13-6af17bbff178.sql)  
2. [generic-sql2delta-sparkapp](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/generic-sql2delta-sparkapp)