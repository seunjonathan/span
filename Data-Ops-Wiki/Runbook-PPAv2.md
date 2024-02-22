|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.3|
|**Date**|17-January-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2435 <br> #2440 <br> #2560 <br> #2649 <br> #2819 <br> #3036 <br> #3037 <br> #3048 <br> #3094


[[_TOC_]]

# Introduction

A new ETL pipeline is proposed to ingest data from the PPA ([Pacific Pilotage Authority](https://www.ppa.gc.ca/)). This data is currently ingested via an ADF pipeline that is closely tied to the Towworks v1 solution. The source of the PPA data is the [PDAMS API](https://seaspan-my.sharepoint.com/:w:/r/personal/yuri_fedoruk_seaspan_com/_layouts/15/Doc.aspx?sourcedoc=%7B702806E1-3318-443E-A556-C263A378A6A6%7D&file=PortLink_PDAMS_API_v2.0.docx&action=default&mobileredirect=true). However, this existing ETL connects to a MS SQL Db containing the data. That database is populated by a separate Azure solution built by Chase Huber. 

The intention of this new ETL mechanism is to leverage the work done for [Towworks v2](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/84/Runbook-Towworksv2) and rebuild an ingestion mechanism that procures data from source. Given that the [PDAMS API](https://seaspan-my.sharepoint.com/:w:/r/personal/yuri_fedoruk_seaspan_com/_layouts/15/Doc.aspx?sourcedoc=%7B702806E1-3318-443E-A556-C263A378A6A6%7D&file=PortLink_PDAMS_API_v2.0.docx&action=default&mobileredirect=true) exposes a JSON based REST API, it should be possible to re-use the [generic-curate-json](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) library to easily process and flatten JSON formatted data.

# Scope
The scope of this document in limited to the ETL of raw data and its curation into the `silver` layer.

# Requirements
The base set of requirements are to ingest raw transactional data, at a minimum frequency of once a day. The data should be processed, cleaned and curated so that it is available via a Synapse SQL serverless endpoint for reporting purposes.

The requirements include but are not limited to those shown in the table below.

# | Requirement | Description
---|---|---
1 | Procurement | The ETL shall procure raw JSON data from the PPA REST endpoint. Raw data shall be archived once processed and stored indefinitely.
2 | Curation | The ETL shall curate raw data into a `silver` layer.
3 | Incremental | The ETL shall support _incremental_ curation of data.
4 | Data transformation | The ETL shall support transformation of JSON data into Delta formatted data
5 | Serve | The ETL shall serve the data to the end user via a Synapse SQL Serverless endpoint
6 | Scheduling | It shall be possible to independently configure the frequency with which different tables are procured.

# Design
## Azure Infrastructure Design
![PPA Infrastructure.png](/.attachments/PPA%20Infrastructure-0936af1c-a330-48eb-80a3-48890555ad29.png =600x)

Compared with Towworks v2, no new infrastructure is necessary. The only change is the adoption of a generic mechanism to flatten JSON. The `generic-curatejson-sparkapp` used the code in the `towworks-bronze2silver-sparkapp` repository as it's baseline but adapted it to represent a more general purpose solution by removing Towworks specific references.

### Components
Name | Component | Description
------|-----|--------
`adlssmgdev/prod` | Azure Data Lake Storage Account (Gen 2) | The storage account will host two containers, `landing` and `processed` as well as a table store.
`dbw-smg-dev/prod` | Azure Databricks Workspace | The workspace will host a `Shared`, auto-scalable cluster. All production PySpark code will be deployed as scripts uploaded to the `dfbs://FileStore/pyspark-scripts` folder.
`adfv2-towworks-dev/CICDprod` | Azure Datafactory (v2) | While the preferred approach is to use a single data factory for each ingestion source. In this case, since PPA data is closely related to Towworks, we have chosen to host the PPA pipelines in the same data factory used to host Towwworks. Also note that instance name in production is `adfv2-towworks-CICDprod`.
`syn-smg-dev/prod`| Azure Synapse | Azure Synapse is used to expose Delta formatted tables as SQL endpoints. This is done via SQL scripts which define views on the data. Otherwise, no other data is stored or managed by Synapse. At this point, Databricks, not Synapse was chosen to host the Spark compute environments. That may change in the future. A change that should be easy since all PySpark code is recommended to be written as portable PySpark scripts rather than as notebooks.
`law-smg-dev/prod` | Azure Log Analytics Workspace | The Azure Log Analytics Workspace will be used to collect metrics from all infrastructure components. This will includes ingestion start/stop times from the data factory as well as data sizes and row counts from PySpark scripts.
`kv-smg-dev/prod` | Azure Key Vault | Azure Key Vault is the standard approach for protecting sensitive information such as keys and passwords. The PPA REST API `Email`, `Password` and Databricks `Client Secret` will be stored here.


### Resource Groups

Resource Group | Description
------ | -----
`rg-smg-common-dev/prod`| This contains infrastructure components that would be common to all SMG ingestion projects. For example: Databricks, Synapse, LAW, Key Vault
`rg-smg-towworks-dev/prod`| This is the same resource group as used for Towworksv2. The PPA related pipelines are hosted in the same data factory in a sub folder. <br/> ![image.png](/.attachments/image-f76d6137-3f5e-4953-93ff-ae11432bcc1f.png =200x)

 

## ETL Design
The solution adopts the same design implemented for the Towworks v2 ETL solution. Namely:
1. Flattening of JSON is abstracted away from the code
2. Conversion of JSON data types is abstracted away from the code

We are able to easily re-use the [generic-curate-json](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) solution for PPA which supports all PPA JSON flatten and type-conversion requirements.

## Data Serving
1. All curated data is served via Synapse SQL Serverless.
2. The production endpoint is `syn-smg-prod-ondemand.sql.azuresynapse.net`.
3. Data will appear in the `silver` database under the `ppa` schema.
    `TODO: The schema as deployed needs to be updated. Currently it appears in uppercase. To follow the convention adopted in SMG, it should be lowercase`
4. As with Towworks v2, configuration and checkpointing data associated with PPA table is persisted to an Azure Table Store called `cfgBronze` which appears in `adlsdsmgdev/adlssmgprod`

# Deployment
1. Upload [curate_json.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) to `dbfs:/FileStore/pyspark-scripts`
2. Provision `cfgBronze`. The following contents can be used as a starting point: [PPA(cfgBronze).csv](/.attachments/PPA(cfgBronze)-b64e0c45-66a8-49c3-9c2c-da912eadfc51.csv)



# Data Sources & Sinks
This section describes where the incoming data comes from and where the ETL persists it to.

## Data Sources

|Name|Source|Description|Sample|
|--|--|--|--|
|PPA Dataset Details<p>`cfgBronze`|An Azure Table store called `cfgBronze` located in `adlssmgdev/prod`| The table store holds configuration data used to identify source PPA datasets and related tracking information. | ![Screenshot 2023-08-29 110051.png](/.attachments/Screenshot%202023-08-29%20110051-875cc943-bd35-495b-9f17-94a21e8ba220.png)
|Checkpoint|Table store<p>`cfgBronze`|The checkpoint is stored at<br> `PropertyName`=`Watermark_End`<br>`PartitionKey`=`PPA`<br>`RowKey`=<TableName>|`2021-12-29T07:51:21.0030666Z`|
|Dataset Contents|REST API|`https://ppa.portlink.co/api/DataApiV2/pdams/GetPdamsVessels?updatedSinceUtc=2020-01-01T00:00:00Z&updatedToUtc=2022-07-20T17:38:13.9631623Z`<p>|![Screenshot 2023-08-29 232519.png](/.attachments/Screenshot%202023-08-29%20232519-8f00dcac-a59f-4766-8687-d51f84cfe92d.png)|


## Data Sinks

The following describe the data generated by the ETL:
|Name|Sink|Description|Sample|
|--|--|--|--|
|Raw JSON|* storage: `adlssmgprod`<br/>* container: `landing` <br/> * folder: `bronze/PPA`|Raw JSON data from the PPA REST API lands here. This location is transient. After processing the data is moved out.|
|Parquet|* storage: `adlssmgprod`<br/>* container: `processed` <br/> * folder: `silver/PPA`|Each Towworks dataset is flattened and persisted as a Delta formatted table.|

### Bronze to Silver
Having seen the difficulty with managing one notebook per table per silver/gold layer, we strongly advocate an approach where we minimize the number of development artifacts. To address this, the goal is to develop a single JSON to Delta processing engine that abstracts the specifics of how to flatten each JSON dataset as well as how to type cast each field in the dataset. 

# Troubleshooting and Maintenance
`TBD`

## Promoting Content from `Dev` to `Prod`
This section discusses the process of provisioning the `prod` environment with the latest version of the PPA ETL implementation artifacts (ADF pipelines, Synapse scripts & Pyspark code).

#### Note
The target is for a fully automated CICD pipeline implemented in Azure DevOps that completes this promotion process. Typically such a process would take the latest version of each artifact in the `main` branch of the repo and install it in its appropriate infrastructure component in the target (`prod`) environment. At the moment no such fully automated process/script exists. As such, the recommended process is to complete the provisioning manually.

### Azure Data Factory
#### Manual Process
1. Export the ARM template from the ADF in the `dev` environment while on the `main` branch.
2. Import it in the `prod` ADF.

#### Automatic Process
`TBD`

### Synapse
#### Manual Process
1. Manually copy the script from the `dev` to the `prod` Synapse.

#### Automatic Process
`TBD`

### Pyspark Code
#### Manual Process
1. Upload the latest version of `curate_json.py` in the `main` branch into dbfs:/FileStore/pyspark-scripts 
#### Automatic Process
`TBD`

# Backfill Data

A common pattern when curating data incrementally, is the need to bulk load historical data. In order to build reports for the PPA data it is required to have data since 2020 Jan 01 so backfilling data from 2020 Jan 01 is necessary. These requirements appear in story #2560. A further complication is that the [PPA API](https://ppa.portlink.co/api/DataApiV2/pdams/) REST endpoint recently replaced an older endpoint. The new one makes data available only back to March 2023. Our approach to backfilling is thus to rely on the data already curated in the existing `edw` solution. This data appears in the storage account `adlsedwprod`

The following table captures the differences observed between the data procured from the new [PPA API](https://ppa.portlink.co/api/DataApiV2/pdams/) and the data curated in `adlsedwprod`. 

|Old API Table| New API Table| Table Type| Description| Changes|
|--|--|--|--|--|
|Pilots| Pilots| Dimension| This table contains data regarding Pilot Id, Name, nickname etc., and table data is mostly static.| Column names have been changed from old API to new API and data remained mostly same but `pilotRemarks` column from old API is removed.|
|Locations| Locations| Dimension| This table contains data regarding Location id, name, short code, district name etc., and table data is mostly static.| Column names have been modified from old to new API and most of data is same and `Tariff_Area` column is being added from static csv in old API data.|
|Customers| Organizations| Dimension| This table contains data regarding Organization id, name, location, type etc., and table data is mostly static.| Table and Column names have been updated but the data mostly remained same in both tables.|
|Ships| Vessels| Dimension| This table contains data regarding Vessel id, name, type, type id etc., and data is mostly static.| Table and Column name have been modified and mostly data remained same.|
|Jobs| Jobs| Fact| This table contains data regarding Job number, id, Vessel Type, organization type, organization id, arrival and departure times, order and dispatch times etc., and data is continuously updated as new jobs keep coming everyday.| Column names have been changed but data remained same and in old API there are some extra columns which are being added manually for example `Seaspan Time` etc., and main data remained same between old and new API links.|

## Content Differences Between Old (`adlsedwprod`) and New (PPA API)

We have noticed some differences between the data curated by the ETL documented here and the data curated by the old version ETL. The scope of the differences are limited to variations in datetime columns.

In the old ETL process, JSON data from the API is stored in a SQL database and then modified and persisted as parquet files in `bronze` and then processed using Databricks notebooks and persisted to a `silver` container. Reports are generated and saved in a `gold` container.

When the JSON data is converted to parquet files, some changes are applied to the incoming data an example of which can be seen in screenshots below.

### Old API data:

![Screenshot 2023-08-30 043121.png](/.attachments/Screenshot%202023-08-30%20043121-2f51ef85-88d7-4caa-b749-a7cd2de75454.png)

### New API data:

![Screenshot 2023-08-30 042955.png](/.attachments/Screenshot%202023-08-30%20042955-7bdc71b6-9f62-4fc6-985f-83dff0800a48.png)

As per screenshots above it can be seen for Job number `314201` that `lastUpdatedUTC` and `updatedAt` values differ from each other for the same job, as the data is being manually intervened before being sent to `bronze` container.

It appears also that columns `eta_ata, etd_atd, orderTime, dispatchTime, updatedAt, createdAt` are in UTC time zone where as `PPA_orderTime, PPA_disptachTime, PPA_arrivalTime, PPA_dispatchTime, PPA_lastmodifieddate, PPA_LastUpdatedUTC, Seaspan_Time` are in PST time zone. To address the possible need to adopt PST as the timezone for storing datetimes, a new task has been created in the backlog under ticket #2649


## Backfill process

The general approach to backfilling is to merge historical data sourced from the original ETL mechanism with new data procured via the PPA API. If records match (according to their unique Ids), then the record procured from the new PPA API is favoured.

Historical data that was not availble from the PPA API was obtained from the previously procured data stored in `adlsedwprod silver container`. This satisfied the requirement to backfill to 2020 Jan 01. 

For tables `Locations, Pilots, Vessels (Ships), Organizations (Customers)` as these are dimension tables we can get either latest parquet file or file from until 2023 Feb and perform the `upsert` function with data from new API link.

Databricks notebooks were created for backfilling each table in `dbw-smg2-dev` where we copied the latest parquet file for the dimension tables from `adlsedwprod` `silver` container and place it in `adlssmgdev` `test` container and performed `upsert` function with backfilled data from 2023 March in `adlssmgdev` `silver` container and merged records for the existing id with new data on old ones and inserted new records.

For the `Jobs` table, which is a fact table, records are updated continuously. Again the data from `adlsedwprod` `silver` container, after comparing data from the delta lake in `SSMS` and after total records of parquet file matched with total delta lake, taken the parquet file and performed `upsert` function as of dimension tables. Only difference between old and new API data is, in old pipeline data is being modified before being sent into `bronze` container where as in new API getting data in JSON as per `etd_atd` column rather than `updatedAt` column depending on `Watermark_End` from `cfgBronze`, because of which data is being mismatched compared to old and new API link.

Notebooks for the tables are as follows:
*  [Pilots](https://adb-1750204433604091.11.azuredatabricks.net/?o=1750204433604091#notebook/3149842698128521/command/3149842698128522)
* [Locations](https://adb-1750204433604091.11.azuredatabricks.net/?o=1750204433604091#notebook/3149842698128526/command/3149842698128527)
* [Organizations](https://adb-1750204433604091.11.azuredatabricks.net/?o=1750204433604091#notebook/1080893042358882/command/1080893042358883)
* [Vessels](https://adb-1750204433604091.11.azuredatabricks.net/?o=1750204433604091#notebook/3149842698128532/command/3149842698128533)
* [Jobs](https://adb-1750204433604091.11.azuredatabricks.net/?o=1750204433604091#notebook/4198560238293288/command/4198560238293289)

# User Sourced Updates

## Introduction

     --- This story is temporarily on hold ---

Story #2819 introduces a requirement in which an end user is able to make updates to records in the PPA Jobs table. The app is expected to be developed as  Power App. This section describes the approach and design implemented for supporting this requirement. 

A hypothetical UI for such a Power App may look like this:

![ppav2.png](/.attachments/ppav2-f732d8bf-c708-4263-97c6-947398b5c94c.png =600x)

## Design
We describe the design in terms of the components that will interact with the Power App.

### UI Interactions
The diagram below identifies the prominent views and tables involved in the solution.

![ppav2 2.png](/.attachments/ppav2%202-8a735d16-1fb5-41ff-9d76-e9d2a24a9093.png =600x)


Component | Description
---|---
User | The end user. Expected to be using the Power App to query/search for PPA Job records and update them.
Power App | Presents the user with a UI. It is expected that the user will have to identify themselves to the App using their Active Directory credentials. The App will authenticate with Synapse using a service account.
Logic App | The Power App will submit updated PPA Job records via a Logic App. This Logic App will then persist the record in CSV format in `transient/silver/PPA/JOB_AMENDMENTS/amendments.csv`
Synapse `[gold].[ppa].[vw_FACT_Jobs_Reconciled]` | This view will merge `[silver].[ppa].[vw_FACT_Jobs]` and `[silver].[ppa].[vw_FACT_Job_Amendments]`
Synapse `[silver].[ppa].[vw_FACT_Job_Amendments]` | This is a Synapse view backed by the contents of `transient/silver/PPA/JOB_AMENDMENTS/amendments.csv`

### ETL Updates
There is also a batch component to the design. Prior to running the existing PPA ETL, which inserts new Job records or updates existing ones, the currently outstanding amendments have to be merged permanently into `processed/silver/PPA/Jobs`. One reason for doing so is so that `transient/silver/PPA/JOB_AMENDMENTS/amendments.csv` does not grow indefinitely. Another is `TODO`: `Look into this scenario carefully - can an incoming Job record overwrite an amendment record`.

![ppa v2 3.png](/.attachments/ppa%20v2%203-0bae7e20-246e-43fa-b72d-3b1d58c991ce.png =600x)

A new Spark activity is introduced. This Spark application (deployed into Databricks) will permanently merge  into `transient/silver/PPA/JOB_AMENDMENTS/amendments.csv` `processed/silver/PPA/Jobs`.

# Appendix
## Updates to ETL of Jobs Table.
ETL of the Jobs table initially used `toUTC` and `fromUTC` parameters to identify the most recent data to retrieve. However, it came to light that the API returns data using these datetimes filtered against the `orderTime` field. This unfortunately meant that we missed _updates_ to records previously fetched. 

Temporarily, the ETL (`PL_PPA_API2Silver`) was modified to go back 30 days when specifying a `fromUTC` datetime. While this mitigated the issue, it is inefficient.

Following guidance from PPA that the Jobs table also supports the `updatedSinceUTC` parameter. It always had, sadly this was not documented in the API documentation [1]. So the ADF pipeline and related config in `cfgBronze` was updated so that all PPA tables are incrementally updated in the same way. _Ref_: #3094. 

# References
1. [PDAMS API](https://seaspan-my.sharepoint.com/:w:/r/personal/yuri_fedoruk_seaspan_com/_layouts/15/doc2.aspx?sourcedoc=%7B702806e1-3318-443e-a556-c263a378a6a6%7D&action=view&wdAccPdf=0&wdparaid=6E6F8987)