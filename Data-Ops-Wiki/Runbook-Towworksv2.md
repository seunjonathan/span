|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|15-February-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2032 <br> #2106 <br> #2107 <br> #2109 <br> #2287 <br> #2406 <br> #2632 <br> #2640 <br> #3282


[[_TOC_]]

# Introduction
This runbook captures the design, implementation and operation of `Towworks v2`.  This is a new Azure based ETL built from the ground up, using industry best practices to deliver a robust and scalable solution for the procurement and curation of raw data from Towworks. An enterprise application deployed for and used by the Seaspan Marine Group (SMG).

# Scope
The scope of this document in limited to the ETL of raw data and it's curation into the `silver` layer. For details of the `gold` layer, please refer to [Runbook Towworks v2 Gold](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/90/Runbook-Towworks-v2-Gold-ETL)

# Requirements
The base set of requirements are to ingest raw transactional data, at a minimum frequency of every hour. The data should be processed, cleaned and curated so that it is available via a Synapse SQL Serverless endpoint for reporting purposes.

The requirements include but are not limited to those shown in the table below.

# | Requirement | Description
---|---|---
1 | Facts vs dimensions | The ETL shall be aware of which Towworks datasets are `facts` and which are `dimensions` 
1.1 | Table specific schedule | The ETL shall procure and curate data from source based on table specific schedules. E.g. `dimension` tables shall be processed once a day, `fact` tables once an hour.
2 | Procurement | The ETL shall procure raw JSON data from the Towworks REST endpoint. Raw data shall be archived once processed and stored indefinitely.
3 | Curation | The ETL shall curate raw data into a `silver` layer.
4 | Incremental | The ETL shall support _incremental_ curation as well as _full-load_ curation.
5 | Data transformation | The ETL shall support transformation of JSON data into Delta formatted data
6 | Serve | The ETL shall serve the data to the end user via a Synapse SQL Serverless endpoint
7 | Type transformation | The ETL shall apply type casting to ensure that integers, floats and datetimes are curated as such rather than as string.
8 | Metrics logging | The ETL shall collect and log metrics. Metrics shall include such things as the number of rows curated, the start and stop time of each ETL invocation.
9 | Data validation | The ETL shall apply data validation rules as far upstream as possible. Data validation rules shall include such things as impossible start & end dates, broken data dependencies (see ERD). `TODO`: Add ERD
10 | Data transformation 2| The ETL shall support mapping one raw incoming JSON dataset to one or more Delta tables, depending upon level of nesting in the JSON.

# Design
## Azure Infrastructure Design

![Towworksv2 Azure Infrastructure.png](/.attachments/Towworksv2%20Azure%20Infrastructure-0f9509ab-b862-4e42-87d1-a06a8d3b5e29.png)
(Subject to change)

### Resource Groups
Past experience suggests that it is beneficial to adopt a split approach to the use of resource groups. In this case a resource group `rg-smg-common-dev/prod` is used to group together infrastructure components that would be common to all SMG ingestion projects. Versus those that are specific an ingestion source such as Towworks. For example, to avoid proliferation of Databricks clusters, which would not be cost effective, we chose to make that a common component. Whereas Azure Data Factory belongs in a source specific resource group, `rg-smg-towworks-dev/prod`. With the intent of keeping it's content smaller, more focused and so easier to manage. Source specific resource groups may also house components such as function apps and logic apps. As appropriate for each solution.

### Components
Name | Component | Description
------|-----|--------
`adlssmgdev/prod` | Azure Data Lake Storage Account (Gen 2) | The storage account will host two containers, `landing` and `processed` as well as a table store.
`dbw-smg-dev/prod` | Azure Databricks Workspace | The workspace will host a `Shared`, auto-scalable cluster. All (most?) production PySpark code will be deployed as scripts uploaded to the `dfbs://FileStore/pyspark-scripts` folder.
`adfv2-towworks-dev/prod` | Azure Datafactory (v2) | The preferred approach is to use a single datafactory for each ingestion source. This ADF will host all pipelines required to ingest data from Towworks.
`syn-smg-dev/prod`| Azure Synapse | Azure Synapse is used to expose Delta formatted tables as SQL endpoints. This is done via SQL scripts which define views on the data. Otherwise, no other data is stored or managed by Synapse. At this point, Databricks, not Synapse was chosen to host the Spark compute environments. That may change in the future. A change that should be easy since all PySpark code is recommended to be written as portable PySpark scripts rather than as notebooks.
`law-smg-dev/prod` | Azure Log Analytics Workspace | The Azure Log Analytics Workspace will be used to collect metrics from all infrastructure components. This will includes ingestion start/stop times from the data factory as well as data sizes and row counts from PySpark scripts.
`kv-smg-dev/prod` | Azure Key Vault | Azure Key Vault is the standard approach for protecting sensitive information such as keys an passwords. The Towworks REST API `CompanyKey`, `API Secret` and Databricks `Client Secret` will be stored here.


## ETL Design
The approach adopts the methodology of capturing data at increasing levels of maturity, commonly referred to as 'bronze-silver-gold'.

bronze | silver | gold
----|----|------
Raw JSON data directly from the Towworks REST API. Each dataset obtained from Towworks will be archived indefinitely.| The JSON data from the bronze layer is flattened and persisted in tabular form. Each Towworks `Dataset` is flattened and persisted as one or more `Delta` tables. Each The tables represent the latest version of the curated raw data. | Tables from the silver layer are joined or aggregated to compile reports. The reports are themselves also stored using the `Delta` format.

## Data Transformation
At the core of the ETL is a Pyspark script used to flatten JSON data. The script is generalised such that it can process any JSON file given a path to the file and a string representing instructions to flatten the JSON. The flattened table is then merged into a target Delta table. The flatten instructions manifest as a `SQL` select statement.

Further details are provided in the script's "read me" file: [ReadMe for curate_towworks.py](https://dev.azure.com/seaspan-edw/DataOps/_git/towworksv2-bronze2silver-sparkapp?path=/README.md)


## Data Serving
`TODO`: Describe here how the data is served. I.e. via Synapse. Also mention how access to the data is authorized.

## Tracking Deleted Rows
The Towworks REST API provides two tables that are specifically for tracking deleted rows. The tables are:
# | Table Name | Description
----|-----|------
1 | `DELETEDEVENTS` | This table tracks deleted `EVENTS`. Each row in this table references an Event GUID. 
2 | `DELETIONAUDIT` | This table tracks deletion in a number of tables. Each row in this table references a table and a GUID in that table. 

Rather than physically removing deleted rows from the Azure storage accounts, we take the approach of marking affected rows as deleted.

This is performed by a custom PySpark application called [process_deletions](https://dev.azure.com/seaspan-edw/DataOps/_git/towworks-processdeletions-sparkapp) that is called from within  the Azure Data Factory pipeline once the currently ETLed JSON has been curated into the silver layer. The intent is to support a boolean column called `marked_as_deleted`. Such that when querying for active records, in the EVENTS table say, the following query should suffice:

```
    SELECT * FROM events WHERE marked_as_deleted = 'False'
    -- or
    SELECT * FROM events WHERE marked_as_deleted = 0
```

### Process Deletions Spark App and Schema Evolution
After landing raw JSON data from the Towworks REST API, the data factory pipeline calls a PySpark app that flattens and curates the JSON in the silver layer in `Delta` format. These curated tables will contain both deleted and active rows. As a final step of the ETL, another PySpark app is triggered which using the data in the `DELETEDEVENTS` and `DELETIONAUDIT` tables, modifies the affected table as follows:
1. If this is the very first time a deletion is processed, a column called `marked_a_deleted` is added to all rows with a default value of `False`.
   * Those rows that appear as deleted according to the before-mentioned tables are updated so that the `marked_as_deleted` field is now set to `True`.
2. If the `marked_as_deleted` column already exists, then only the most recently ingested rows in the deletion tables are processed. Again, those records that have been marked as deleted are updated such the `marked_as_deleted` field is now set to `True`.
3. When new records are added to the target Towworks tables and do not appear in the deletion tables. (This in fact will likely be the most common case). The `marked_as_deleted` column will be created with a `null` value. Such records are detected and the `null` value replaced with `False`.

The above steps describe a situation in which the schema of tables change. Ordinarily these scenarios give rise to problems and exceptions. This is the case in step 3 above in which incoming new records from Towworks do not intrinsically possess a `marked_as_deleted` field, yet the data is merged into a target `Delta` table that does. To permit this a spark configuration setting must be enabled:

```
    spark.databricks.delta.schema.autoMerge.enabled
```

This can be done via the `Advanced options` section of the databricks cluster configuration UI:

   ![env.png](/.attachments/env-336a5a30-8812-4ced-8d5c-05fcbd45326a.png =345x)

Or better in main section of the PySpark app:
![Items.png](/.attachments/Items-93fc3b7a-c580-44c1-a9ba-9265d522948f.png =900x)

## Data Validation

To help detect data quality issues, one of the requirements of this ETL is to implement validation checks against incoming data. The nature of these checks is to help address data errors such as a start time that comes after an end time. Or a impossible values for a field, such as a negative value for a billing_hours field.

### Design Approach

A simple approach may be to hard code these tests into the PySpark script that flattens the json (`curate_towworks.py`). However such an approach would quickly become unmanageable and result in code that is difficult to maintain & test. Instead, we adopted the same methodology as used for flattening the tables. I.e. the code that defines the validation checks is abstracted out of the code as SQL.

In the same way that the flatten instructions exist as configuration data for each Towworks table in the Azure table store; `cfgBronze`, so do a set of one or more _validation instructions_. Each instruction being a SQL command that defines the check. For example, a validation instruction may be defined as follows:

```
    SELECT count(*) AS num_errors FROM events WHERE StartTime > EndTime
```

The code in `curate_towworks.py` will execute this SQL and expect a count of 0 if no errors were detected. In the case that the count is > 0, the code will log the issue. The intent is that these errors are logged to the Log Analytics Workspace and be available for visualization in Power BI.

#### Adding New Validation Checks.
Validation checks are configurable via the `cfgBronze` configuration table. New checks can be added by simply updating the `Validation_Instructions` field of this table.

The following is an example of this field for the _TRANSACTIONS_ table. It shows 5 individual checks that apply.

```
[
	{
		"error_message": "Count of CPIRate failed validation :",
		"validation_command": "select count(*) as num_errors from TRANSACTIONS where CPIRate < 0"
	},
	{
		"error_message": "Count of FuelSurchargeAmount failed validation :",
		"validation_command": "select count(*) as num_errors from TRANSACTIONS where FuelSurchargeAmount < 0"
	},
	{
		"error_message": "Count of FuelSurchargeRate failed validation :",
		"validation_command": "select count(*) as num_errors from TRANSACTIONS where FuelSurchargeRate < 0"
	},
	{
		"error_message": "Count of LineTotal failed validation :",
		"validation_command": "select count(*) as num_errors from TRANSACTIONS where LineTotal < 0"
	},
	{
		"error_message": "Count of DistributionAmount failed validation :",
		"validation_command": "select count(*) as num_errors from GLCODES where DistributionAmount < 0"
	}
]
```

The `Validation_Instructions` field must be a valid JSON array object, even if it has only one entry. Each entry must specify an _error_message_ and an corresponding _validation_command_ object, which must be syntactically correct T-SQL. The output of the SQL must be a single column called `num_errors` containing a numeric value representing of course, the number of rows which tested positive to the provided condition.

The errors are automatically logged to law-smg-dev/prod, in a table called <TBD>.


# Deployment
`TODO`: In this section include any information that describes any special steps in setting up the infrastructure.

## Databricks Deployment
`TODO`: Describe here the specific details for setting up `dbw-smg-dev/prod`. E.g. the use of service principals. Also describe how the `curate_towworks.py` is deployed.


### Databricks to Storage Account Setup
There are two deployment aspects worth noting:
1.  Storage accounts in Seaspan must, by policy, be placed behind a firewall. This introduces the need to establish connectivity via virtual networks. These virtual networks can be created as part of the process of creating the Databricks workspace.
    * The image below shows a `vnet` used to attach the mandatory databricks _public_ and _private_ subnets to the storage account.

      ![vnet.png](/.attachments/vnet-06890daf-7bbe-4dfd-be1d-65f14cc40a6e.png =600x)
2. The preferred usage model for a Spark cluster is `Shared` mode. This however requires that the cluster authenticate with the storage account using a _Service Principal_ and not a Seaspan _-az@seaspan.com_ account.
    * The following environment variables must be initialised within the cluster (values are shown for `PROD`):
   ![spark.png](/.attachments/spark-8926342f-8498-4054-a71e-52f9bdb42b2a.png =400x)

    * Then the `curate_towworks.py` or any PySpark script or notebook must be configured to use them. This can be done using the following code :
     ```
    spark.conf.set(f"fs.azure.account.auth.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "OAuth")
    spark.conf.set(f"fs.azure.account.oauth.provider.type.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
    spark.conf.set(f"fs.azure.account.oauth2.client.id.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", SPCLIENTID)
    spark.conf.set(f"fs.azure.account.oauth2.client.secret.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", dbutils.secrets.get(SPSCOPE,SPSECRET))
    spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net", f"https://login.microsoftonline.com/{SPTENANTID}/oauth2/token")
     ```



# Data Sources & Sinks
This section describes where the incoming data comes from and where the ETL persists it to.

The illustration below captures below the movement of data at a high-level.

![towworksv2-data-flow.png](/.attachments/towworksv2-data-flow-ac4896ed-0290-4a74-84e2-1f8802fec36d.png =400x)

1. Raw data in JSON format first lands in the `bronze` folder of the landing container of the `adlssmgprod` storage account
2. The data is processed and the output stored in the `silver` folder of the `processed` container.
3. The incoming data is archived (moved) into the `bronze` folder of the `processed` container once processing is complete. Leaving the `bronze` folder of the `landing` container empty.

## Data Sources
|Name|Source|Description|Sample|
|--|--|--|--|
|Towworks Dataset Details<p>`cfgBronze`|An Azure Table store called `cfgBronze` located in `adlssmgdev/prod`| The table store holds configuration data used to identify source Towworks datasets and related tracking information. | ![dataset.png](/.attachments/dataset-c995aec2-57c0-45d2-a8ac-4c4cce55da15.png =x200)
|Checkpoint|Table store<p>`cfgBronze`|The checkpoint is stored at<br> `PropertyName`=`Watermark_End`<br>`PartitionKey`=`TOWWORKSv2`<br>`RowKey`=<TableName>|`2021-12-29T07:51:21.0030666Z`|
|Dataset Contents|REST API|`https://seaspan.towworks.com/custom/seaspan/processes/TWDataBroker.aspx?COMPANYKEY={{Company}}&DATASET=ASSET`<p>|![data.png](/.attachments/data-8c4465a6-fdd7-4a9a-a3b3-8506c75c44cf.png =x250)

### Static Content
Ref: #3282
Seaspan tugs can be allocated to different service groups at different periods of time. To capture these allocations, a manually curated static CSV file is used.
* This file is persisted in `landing@silver/TOWWORKSv2/ASSET_TUG`
* The contents of this file are exposed in Synapse at `[towworks].[vw_DIM_ASSET_TUG]`
* Any changes to the CSV file are immediately reflected in the Synapse view.

## Data Sinks
The goal of this ETL is to convert the data in each XML file into a tabular (parquet) form. One parquet file per XML file is generated. The output parquet files are considered to be at the `bronze` maturity level.

The following describe the data generated by the ETL:
|Name|Sink|Description|Sample|
|--|--|--|--|
|Raw JSON|Landing Blob Store|Raw JSON data from the Towworks REST API lands here. This location is transient. After processing the data is moved out.|
|Parquet|Processed Delta Store|Each Towworks dataset is flattened and persisted as a Delta formatted table.|

### Bronze to Silver
Having seen the difficulty with managing one notebook per Towworks table per silver/gold layer, we strongly advocate an approach where we minimize the number of development artifacts. To address this, the goal is to develop a single JSON to Delta processing engine that abstracts the specifics of how to flatten each JSON dataset as well as how to type cast each field in the dataset. For more details see [ETL Design](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki?wikiVersion=GBwikiMaster&pagePath=/Data%20Ops%20Wiki/Runbook%20Towworksv2&pageId=84&_a=edit#etl-design).

# Troubleshooting and Maintenance
##Problem within Databricks
*	Even though we have the library `python-dotenv==0.15.0` installed in the cluster, the python script was unable to retrieve the `dotenv` directory from the library. The below image would depict the error that was encountered when trying to retrieve the list of directories.

![databricks.png](/.attachments/databricks-d3ad4b85-6f64-417a-9eca-4d95fe1fb0a9.png =800x)
 
##Solutions
*	To change the Databricks runtime version from 9.1 LTS to any version that is above and equal to 11.3 LTS. Below is the different run-time versions available in the cluster.

![sol.png](/.attachments/sol-4c9975f7-2d12-4952-bbf9-38870c62a602.png =600x)
 
The dotenv directory is not available within the 9.1 LTS and 10.4 LTS versions.

*	Another solution would be to remove the dotenv library completely from the cluster and then also update the curate_towworks.py script by removing all the dotenv variables that we have defined in the script. The reason behind deleted them in the script is we have already defined those variables in advanced options of databricks cluster. Here are the environment variables that are defined within the databricks cluster.
 ![clustersol.png](/.attachments/clustersol-9e0308c9-b66a-4b74-8b30-a0b5006ef01e.png =600x)

These are the variables that needs to be removed from the curate_towworks.py script
 ```
load_dotenv()
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
SPCLIENTID = os.getenv("SPCLIENTID")
SPTENANTID = os.getenv("SPTENANTID")
SPSCOPE = os.getenv("SPSCOPE")
SPSECRET = os.getenv("SPSECRET")
 ```

The updated script of `curate_towworks.py` to retrieve the variables that are defined in databricks cluster should be like this
 ```
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
SPCLIENTID = os.getenv("SPCLIENTID")
SPTENANTID = os.getenv("SPTENANTID")
SPSCOPE = os.getenv("SPSCOPE")
SPSECRET = os.getenv("SPSECRET")
 ```
By updating the above changes we can still use the 9.1 LTS databricks runtime version and we need not install python-dotenv library within the cluster and databricks would work perfectly.

*	One more fix would be to talk to the databricks administration and check whether they have updated the access mode options within the cluster. Right now we only have 3 access mode options within the cluster and they are shared, no isolation, single user access. There should be one more option called custom which is not showing up now.
##Problem while provisioning of Synapse CICD Pipeline
*	Created a release pipeline for provisioning of **syn-smg-dev** to **syn-smg-prod**. I have created a new service connection **synapse-towworksv2** which serves as a Synapse Workspace connection type for the following deployment. 
*	I have added workspace_publish as an artifact from towworks-syn repo. 
* When the pipeline was deployed the following error occurred.

 ```
2023-05-16T04:26:21.8521176Z ##[error]Encountered with exception:Error: SQL script deployment status "Failed"
2023-05-16T04:26:21.8538882Z For Artifact: Create Towworksv2 views: Deploy artifact 
failed: {"error":{"code":"Unauthorized","message":"The principal '4a20a80d-bb98-4c8c-8cea-f07b3baab448' 
does not have the required Synapse RBAC permission to perform this action. 
Required permission: Action: Microsoft.Synapse/workspaces/sqlScripts/write, Scope: workspaces/syn-smg-prod."}}
 ```
          

##Solution
*	Based on the above error it was clear that it’s requesting to assign the service connection created earlier Synapse SQL Administrator access.
*	As the service connection **synapse-towworksv2** is created using Azure Resource Manager, we can’t directly assign access to this rather we can assign access to service principal linked to that specific Azure subscription which in our case would be **seaspan-edw-DataOps-e2764bf7-bdda-4887-aa05-42f41431e1c1**  
*	So by assigning **Synapse SQL Administrator** access to the service principal **seaspan-edw-DataOps-e2764bf7-bdda-4887-aa05-42f41431e1c1** in **syn-smg-prod** synapse studio the issue was resolved.


`TODO`: The purpose of this section is to aid with any issues or problems that occur during the running of this ETL.
1. To identify the last time an incrementally loaded table was successfully loaded, look at the `Watermark_End` column of `cfgBronze`.
2. To open a Databricks log from an Azure Data Factory monitor log, click on the eye glasses icon. This will provide a link to the log:

   ![databricks logs.png](/.attachments/databricks%20logs-fdbefec6-ab21-4ee4-875f-7cb500f203ba.png =x250)

## Trigger Scheduling for Hourly Pipeline Run

Main purpose of scheduling pipeline is it get incremental data from REST Api of TOWWORKSv2 for required tables to generate views from the delta table.
The below table consists of schedule instructions for each table incremental run in TOWWORKSv2:

|Table Name|Table Type|Schedule|Description|
|--|--|--|--|
|towworks.vw_DIM_ASSET| Dimension |Run at hour 09,16 PST.|Running pipeline twice a day as data being updated daily.
|towworks.vw_DIM_CARGO| Dimension |Run at hour 09 PST.| Running pipeline once per a day as data being updated daily.
|towworks.vw_DIM_COMPANY| Dimension |Run at hour 09 PST.| Running pipeline once per a day as data being updated daily.
|towworks.vw_DIM_CUSTOMCOLORS| Dimension |Run at 09 PST.| Running pipeline once per a day as data being populated daily.
|towworks.vw_DIM_ETAESTIMATES| Dimension |Run at 09 PST.| Running pipeline once per a day as data being populated daily.
|towworks.vw_DIM_LOCATION| Dimension |Run at 09 PST.| Running pipeline once per a day as data being populated daily.
|towworks.vw_DIM_UNITOFMEASURE| Dimension |Run at 09 PST.| Running pipeline once per a day as data being populated daily.
|towworks.vw_DIM_WORKORDERSTATUS| Dimension |Run hourly.| Pipeline will run every hour.
|towworks.vw_FACT_APINVOICES| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_ARINVOICES| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_BASEAUDIT| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_CONTRACTS| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_DELETEDEVENTS| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_DELETIONAUDIT| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_EVENT| Fact | Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_GLCODES| Fact | NA |GLCODES table is generated from TRANSACTIONS table and its schedule depends on TRANSACTIONS table.
|towworks.vw_FACT_LOGISTICSORDERS| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_LOGiSTICSORDERSLINEITEMCARGO| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_LOGISTICORDERSLINEITEMS| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_RATEESCALATORS| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_RATES| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_ROUTEPARTIES | Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_TRANSACTIONS | Fact| Run hourly. |Pipeline will run every hour. It will generate both TRANSACTIONS and GLCODES tables.
|towworks.vw_FACT_WORKORDERLINKS| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_WORKORDERS| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_WORKSORDERSASUPPLEMENT| Fact| Run hourly. |Pipeline will run every hour.
|towworks.vw_FACT_WORKTASKS| Fact| Run hourly.| Pipeline will run every hour.

##CargoInformation not found error

For the table `LOGISTICSORDERSLINEITEMS` there is a column under name of _CargoInformation_, whenever value of this column is null, pipeline is being failed at merge activity as merge statement is expecting same type of data which is previously existing in the delta lake and throwing error as follows:

`cannot resolve 'updates.CargoInformation' due to data type mismatch: cannot cast string to array<struct<Cargo:struct<CargoName:string,LoadDate:string,LoadVolume:string,UnloadDate:string,UnloadVolume:string,UoM:string,Volume:string>>>; `

Same information which is being generated under column _CargoInformation_ of `LOGISTICSORDERSLINEITEMS` is being populated as another table `LOGISTICSORDERSLINEITEMCARGO`.

Dropped the column _CargoInformation_ from flattening in `LOGISTICSORDERSLINEITEMS` by selecting all other existing columns in the table and ran the ADF pipeline, able to generate data without any problem and pipeline is being executed successfully. Please find the new flatten command in the link attached here [Flatten Command.txt](/.attachments/Flatten%20Command-e3c75e3c-ce09-4305-87d5-defe0a373bee.txt)

## Promoting Content from `Dev` to `Prod`
### Azure Data Factory
An Azure Release CI/CD Pipeline is used to promote content from the `main` branch of the `towworks-adf` repository to `adfv2-towworks-prod`. See [Azure CI/CD Release Pipeline Setup](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/86/Azure-CI-CD-Release-Pipeline-Setup) for more details.
### Azure Synapse
`TODO`
### Azure Databricks
`TODO`
Currently this is done manually. By uploading the latest version of `curate_towworks.py` to _dbfs://FileStore/pyspark-scripts/_


# Appendix

## Towworks Source Tables Dependencies

![source tables.png](/.attachments/source%20tables-571deb5c-7e98-4e5d-a33b-bc4dbbf8e028.png =600x)

Notes:
* Barge Jobs - The Line Item is the key record that binds all the workorders and events. Each event for 
a barge should be linked to a line item, but not necessarily linked to a work order
* Ship Assist and Internal Jobs - Events will be linked to a task and work order but probably not have 
logistics line.
* Transactions should always be linked to an even

## Status of table ingest around 30 April 2023

Table | Comment
----| -----
APINVOICES| Apr 28, Apr 30, May 1 - empty data.
CUSTOMCOLORS| same data being populated everyday.
LOGISTICLINEORDERITEMCARGO| data populated everyday.
DELETIONAUDIT| APR 30 - empty data.
WORKORDERSTATUS| No data being populated since initial run.
UNITOFMEASURE| No data being populated since initial run.
COMPANY| Apr 28,30, May 1 - empty data.
DELETEDEVENTS| data populated everyday.
CARGO| no data being populated since initial run.
CONTRACTS| no data being populated since initial run.
ASSET| data populated everyday.
LOGISTICORDERLINEITEMS| data populated everyday.
WORKTASKS| data populated everyday.
ETAESTIMATES| no data being populated since initial run.
LOGISTICSORDERS| data populated everyday.
RATEESCALATORS| no data being processed since initial run, data again populated on May 1st.
BASEAUDIT| data populated everyday,
EVENTS| data populated everyday.
WORKORDERS| data populated everyday.
LOCATION| no data being populated since initial run.
WORKORDERLINKS| data populated everyday.
WORKORDERSAUPPLEMENT| data populated everyday.
RATES| no data being populated since initial run.
ROUTEPARTIES| same data is being populated everyday.
TRANSACTIONS| data passed everyday.
ARINVOICES| APR 30 - empty data

## Towworks REST API Credentials
To use the Towworks API, a token must first be obtained using authentication credentials. The token is obtained via the following `GET` request:
```
GET https://seaspan.towworks.com/auth/login?user={{username}}&pass={{AuthKey}}
```

The _username_ is `seaspan`
The _AuthKey_ is a secret which is stored in the Azure Key Vault `kv-smg-dev/prod`. The name of the secret in the key vault is `TOWWORKS-RESTAPI-Secret`

Once a token is obtained (which has a lifetime of 1 hour), it must be sent as a header called _AUTHTOKEN_ in all requests along with a query parameter called _COMPANYKEY_. This too is stored in a secret called `TOWWORKS-RESTCOMPANYNAME` in the same key vault.

## Miscellaneous

### DBO Schema
A `dbo` schema was added to support miscellaneous tables. These tables are:
# | Table Name | Path in Storage Account | View Name | Description
---|---|--|--|---
1 | CALENDAR_DATE | `processed/silver/DBO/CALENDAR_DATE` | `[dbo].[vw_CALENDAR_DATE]` | This table is a static table containing date related information such as year, week, month, week number etc. This table was built by simply copying over the contents of the original version of this table from Towworks v1 into the SMG storage account and creating a view for it.

#Towworks API v2

##Introduction
As per request to Towworks teams, when ever there is a change in the data being sent to us, the changes should be published as a new API link with inclusion of `APIversion` in the URL.

## Modification in data
The following are changes done in tables data as per new version of Towworks API:
|Table Name| Description| Sample|
|--|--|--|
|ARINVOICES| In `ARINVOICES` table the nested JSON structure have been adjusted by removing `EVENTS, TRANSACTIONS, EVENTCARGO` JSON data have been removed and a new column `CurrencyCode` have been added to the table.| ![Screenshot 2023-09-08 102307.png](/.attachments/Screenshot%202023-09-08%20102307-f4ad89ed-7eb7-4160-ab6b-0b2dd66d667d.png)|
|APINVOICES| In `APINVOICES` table the nested JSON structure have been adjusted by removing `EVENTS, TRANSACTIONS, EVENTCARGO` JSON data have been removed.| ![Screenshot 2023-09-08 102157.png](/.attachments/Screenshot%202023-09-08%20102157-b5b10a26-f10f-4421-9591-8405c73855fa.png)|
|DISTRIBUTIONS| Nested `TRANSACTIONS` table have been spilt and `DISTRIBUTIONS` table is being sent as new table.| ![Screenshot 2023-09-08 102551.png](/.attachments/Screenshot%202023-09-08%20102551-78068422-d1d6-4cfa-857c-8fd6f86e34f6.png)|
|EVENTS| In `EVENTS` table a new column `TransactionsExpected` is added of field type varchar.| ![Screenshot 2023-09-08 102753.png](/.attachments/Screenshot%202023-09-08%20102753-e6756c8b-3c80-4145-9274-ac65fc9a2bda.png)|
|LOGISTICSORDERSLINEITEMS| In this table nested `CARGOINFORMATION` is removed and being passed as a new table. ||

###New URL 

The updated URL structure for connecting to REST API links is `https://seaspan.towworks.com/custom/seaspan/processes/TWDataBroker.aspx?COMPANYKEY={{Company}}&DATASET=ARINVOICES&DATETOPULLFROM=2023-07-19T12:35:00&DATETOPULLTO=2023-07-28T16:09:21&APIVERSION=v2`, when ever a new version is created, the `APIVERSION` value in link is updated by changing version number to the newest one available.

## Field Types

As per the document([Seaspan_APIFeed_Columns.xlsx](/.attachments/Seaspan_APIFeed_Columns-f38187ad-ef3f-46f8-b09b-df9b19c67314.xlsx)) provided by the Towworks team the field types of each columns when compared to version `v1` and `v2` are present in the document attached ([field types.txt](/.attachments/field%20types-432fec43-91d9-4a22-858f-84c94b09dc72.txt)).

Changed field type of `WorkOrderNumber` of EVENTS table from `float` to `varchar` as per the document provided by the _Towworks_ team and updated gold reports with updated field type and created new views on gold tables.

##Data Backfill for API version 2
Updated the field types column in `cgfBronze` and backfilled data since `01 Jan 2020` 
for all the tables with new API link in `dev` environment and after testing moved it into `Prod` environment.

##Synapse views
`TODO: Change in view names if any`

Created new view `towworks.vw_FACT_DISTRIBUTIONS` and dropped `towworks.vw_FACT_GLCODES` as Distributions are being sent as a new table and to match out the naming conventions modified view from GLCODES to DISTRIBUTIONS.

# References
1. [curate_towworks.py](https://dev.azure.com/seaspan-edw/DataOps/_git/towworksv2-bronze2silver-sparkapp)
2. [Azure CI/CD Release Pipeline Setup](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/86/Azure-CI-CD-Release-Pipeline-Setup)
 