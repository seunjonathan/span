|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|16-June-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2206 <br> #2184 <br> #2233 <br> #2235


[[_TOC_]]

# Introduction
This runbook captures the design, implementation and operation of `Prism`.  This is a new Azure based ETL built from the ground up, using industry best practices to deliver a robust and scalable solution for the procurement and curation of raw data from Prism. An enterprise application deployed for and used by the Seaspan Marine Group (SMG).

# Scope
The scope of this document is limited to the ETL of raw data and its curation into the `silver` layer.

# Requirements
The base set of requirements are to ingest raw transactional data, at a minimum frequency of once a day. The data should be processed, cleaned and curated so that it is available via a Synapse SQL serverless endpoint for reporting purposes.

The requirements include but are not limited to those shown in the table below.

# | Requirement | Description
---|---|---
1 | Endpoint '**TYPE**' specific schedule | The ETL shall procure and curate data from source based on specific schedules set for TARGETS and MISSES types in `cfgBRONZE` config table.
1 | Procurement | The ETL shall procure raw JSON data from the Prism REST endpoints. Raw data shall be archived once processed and stored indefinitely.
2 | Curation | The ETL shall curate raw data into a `silver` layer.
3 | Incremental | The ETL shall support _incremental_ curation as well as _full-load_ curation.
4 | Data transformation | The ETL shall support transformation of JSON data into Delta formatted data
5 | Serve | The ETL shall serve the data to the end user via a Synapse SQL Serverless endpoint

# Design
## Azure Infrastructure Design
Other than a separate Azure Data Factory, the solution adopts infrastructure components that are common to all SMG solutions. See [Runbook Towworks v2](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/84/Runbook-Towworksv2)


### Components
Component | Description
-----| -----
![1.png](/.attachments/1-1c7a498c-89c4-46c7-8dad-89f15c89c6f4.png =100x) | Orchestration of the PRISM ETL is hosted in a separate Azure Data Factory. The intent is that this pipeline would host all Ferry related pipelines. In the future this data factory is expected to also host v2 of the TOPS pipeline
![2.png](/.attachments/2-1f8d8dff-4390-4d7c-ad23-123bdf9eef02.png =100x) | A storage account common to all SMG data is used.
![3.png](/.attachments/3-9540f041-263c-431f-a353-e94ce584b24e.png =100x) | A databricks workspace common to all SMG solutions is used. This is to prevent proliferation of clusters and keep costs low.
![4.png](/.attachments/4-05ffcc1b-9234-4d98-86cd-f80c51528cec.png =100x) | Likewise, a common Synapse is used to host the curated data.

### Resource Groups
Resource Group | Description
------ | -----
rg-smg-tops-dev/prod | Location of adfv2-tops-dev/prod
rg-smg-common-dev/prod | Resource group common to all SMG solutions



## ETL Design
The solution adopts the same design implemented for the Towworks v2 ETL solution. Namely:
1. Flattening of JSON is abstracted away from the code
2. Conversion of JSON data types is abstracted away from the code

An initiative introduced by this project is the development of a generic code base for flattening and processing JSON. Whereas the PySpark code used in Towworks v2 [curate_towworks.py](https://dev.azure.com/seaspan-edw/DataOps/_git/towworksv2-bronze2silver-sparkapp) was designed and built specifically to address Towworks ETL requirements, [curate_json.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) delivers similar functionality but with a solution that is generic.

Both [curate_json.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) and [curate_towworks.py](https://dev.azure.com/seaspan-edw/DataOps/_git/towworksv2-bronze2silver-sparkapp) rely on flatten instructions, composed of syntactically correct SQL to be provisioned in the `cfgBronze`. Also supported (in both) is the option to provision specification of data types to be applied to incoming JSON fields. Not yet supported in [curate_json.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) is the validation feature.

## Data Serving
All curated data is served via Synapse SQL Serverless.
The production endpoint is `syn-smg-prod-ondemand.sql.azuresynapse.net`.
Data will appear in the `silver` database under the `prism` schema.

# Deployment
1. Upload [curate_json.py](https://dev.azure.com/seaspan-edw/DataOps/_git/generic-curatejson-sparkapp) to `dbfs:/FileStore/pyspark-scripts`
2. Provision `cfgBronze`. The following contents can be used as a starting point: [cfgBronze-PRISM.csv](/.attachments/cfgBronze-PRISM-ea96a83a-4311-4751-8999-098d4344cb25.csv)

## Databricks Deployment
_Specific details for setting up `dbw-smg-prod`._ 

The workspace is a "premium” type located in the `canadacentral` region. It has public network access enabled, allowing it to be accessed publicly over the internet.

Key points to note

**Network Security Group (NSG) Rules**: All network security group rules are required for the workspace.

**Managed Resource Group**: The workspace is managed by the resource group named `databricks-rg-dbw-smg-prod-5m7crwykycrlg`.

**Virtual Network and Subnets**: The workspace is deployed in a virtual network with ID `/subscriptions/e2764bf7-bdda-4887-aa05-42f41431e1c1/resourceGroups/rg-smg-common-prod/providers/Microsoft.Network/virtualNetworks/vnet-smg-prod`. It uses custom subnet names `dbw-smg-prod-private-subnet` for the private subnet and `dbw-smg-prod-public-subnet` for the public subnet.

**Public IP and NAT Gateway**: The workspace does not enable a public IP `"enableNoPublicIp": false` and uses the NAT gateway named `nat-gateway` with a public IP named `nat-gw-public-ip`.

**Storage Account**: The workspace uses a storage account named "dbstoragewjbhosomozoa6" with a SKU of "Standard_GRS" for replication.

**Service Principal Authorization**: The workspace is authorized for a specific principal identified by "principalId": "9a74af6f-d153-4348-988a-e2672920bee9" with a role defined by "roleDefinitionId": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635".
![5.png](/.attachments/5-5b583dc3-941a-467c-b891-ae7b717a0a38.png) 

**Workspace ID and URL**: The workspace ID is "4379826858178347" and can be accessed at "adb-4379826858178347.7.azuredatabricks.net".


_Description of how `curate_towworks.py` is deployed._

The `adfv2-tops-prod` pipeline is designed to retrieve data from the TOPS Prism API, transform it, and store it in the "silver" layer in Parquet format. The python file handles the transformation part.

The `curate_json.py` script is designed to transform and curate raw JSON data stored in the Databricks workspace. It accepts various arguments to specify the source table, schema, destination folder, and instructions for flattening and casting the data. The script supports both incremental updates and full overwrites, enabling efficient data processing for different use cases.

The script processes the data by flattening the JSON and applying specified transformations and then persists the processed data to Delta tables based on the given instructions and schema.

To deploy the curate_json.py script to Databricks, we:

- Upload the script file to the Databricks workspace. `dbfs:/FileStore/pyspark-scripts/`
- Invoke the script as part of your ADF pipeline run with the required arguments.
- Ensure that the necessary dependencies of Delta Lake and other Python packages, are installed on the Databricks cluster.

The script relies on the Databricks environment and expects certain environment variables to be set, such as STORAGE_ACCOUNT_NAME, SPCLIENTID, SPTENANTID, SPSCOPE, and SPSECRET.

Databricks Linked Service Name: "LS_SMG_DBW" 




### Databricks to Storage Account Setup
Details of the setup is similar to what exists in towworks.
https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/84/Runbook-Towworksv2?anchor=databricks-deployment


# Data Sources & Sinks
This section describes where the incoming data comes from and where the ETL persists it to.

We used the same mechanism used by towworksv2.
The illustration below captures below the movement of data at a high-level.
![6.png](/.attachments/6-da6cf3ca-8b18-4f30-bc2a-0fffb3a6e51d.png)

1. Raw data in JSON format first lands in the `bronze` folder of the landing container of the `adlssmgprod` storage account
2. The data is processed and the output stored in the `silver` folder of the `processed` container.
3. The incoming data is archived (moved) into the `bronze` folder of the `processed` container once processing is complete. Leaving the `bronze` folder of the `landing` container empty.

## Data Sources
|Name|Source|Description|Sample|
|--|--|--|--|
`MISSES` | https://prism.beaverlabs.net/api/performance/targets/misses ||https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-data---misses|
`TARGETS` | https://prism.beaverlabs.net/api/performance/targets ||https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-data---targets|
`STATISTICS` | https://prism.beaverlabs.net/api/twin_engines/statistics||https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-data---statistics|
`VOYAGES` | https://prism.beaverlabs.net/api/voyages?include_statistics=true||https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-data---voyages|

## Data Sinks
The goal of this ETL is to convert the data in each XML file into a tabular (parquet) form. One parquet file per XML file is generated. The output parquet files are considered to be at the `bronze` maturity level.

The following describe the data generated by the ETL:
|Name|Sink|Description|Sample|
|--|--|--|--|
`MISSES`|https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/MISSES_DUAL_FUEL_ENGINE_GAS_MODE/, https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/MISSES_ENERGY_CONSUMPTION/, https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/MISSES_SHORE_POWER_UTILIZATION/| Three separate data sets are curated into three individual tables. The data is procured incrementally. <br><br> SYNAPSE views are created on top of the data in the sink. <br><br>`[silver].[prism].[vw_MISSES_DUAL_FUEL_ENGINE_GAS_MODE]` <br> `[silver].[prism].[vw_MISSES_ENERGY_CONSUMPTION]` <br> `[silver].[prism].[vw_MISSES_SHORE_POWER_UTILIZATION]`|https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-sink-data---voyages|
`TARGETS`|https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/TARGETS_DUAL_FUEL_ENGINE_GAS_MODE/, https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/TARGETS_ENERGY_CONSUMPTION/, https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/TARGETS_SHORE_POWER_UTILIZATION/| SYNAPSE views are created on top of the data in the sink. <br><br>`[silver].[prism].[vw_TARGETS_DUAL_FUEL_ENGINE_GAS_MODE]`  `[silver].[prism].[vw_TARGETS_ENERGY_CONSUMPTION]` <br> `[silver].[prism].[vw_TARGETS_SHORE_POWER_UTILIZATION]`|https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-sink-data---targets|
`STATISTICS`|https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/STATISTICS/|`[silver].[prism].[vw_STATISTICS]`|https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-sink-data---statistics|
`VOAYAGES`|https://adlssmgdev.blob.core.windows.net/processed/silver/PRISM/VOYAGES/|`[silver].[prism].[vw_VOYAGES]`|https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/92/Runbook-Prism?anchor=sample-sink-data---voyages|

## Trigger Scheduling for Hourly Pipeline Run

The pipeline is scheduled to get incremental data from REST Api of PRISM for required tables to generate views from the delta table.
![7.png](/.attachments/7-c067b350-471d-4804-b9bb-de3d99be8d24.png)

|Table Name|Schedule|Description|
|--|--|--|
|[prism].[vw_MISSES_DUAL_FUEL_ENGINE_GAS_MODE|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_MISSES_ENERGY_CONSUMPTION]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_MISSES_SHORE_POWER_UTILIZATION]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_TARGETS_DUAL_FUEL_ENGINE_GAS_MODE]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_TARGETS_ENERGY_CONSUMPTION]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_TARGETS_SHORE_POWER_UTILIZATION]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_STATISTICS]]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.
|[prism].[vw_VOYAGES]|Run at hour 03 PST.|Running pipeline once a day as data being updated daily.



# Troubleshooting and Maintenance
`TBD`

## Promoting Content from `Dev` to `Prod`
### Azure Data Factory
The subpage has details of automating the promotiong from Dev to Prod.
[Release Pipeline Setup](/Data-Ops-Wiki/Runbook-Prism/Release-Pipeline-Setup)


# Appendix
`TBD`



# References
`TBD` 

# Sample Data - Misses
`MISSES SOURCE SAMPLES`

![8.png](/.attachments/8-500e8fd9-ee90-4369-9c15-479027d9d4ee.png)
![8.5.png](/.attachments/8.5-5e7483dc-932e-432a-a7cd-f00f917f71cb.png)
# Sample Data - Targets
`TARGETS SOURCE SAMPLES`
![9.png](/.attachments/9-c125f4b7-36b0-4fbf-ac8c-366d0147338f.png)
![9.5.png](/.attachments/9.5-221738a6-bc43-4616-8c72-1eb2067d3368.png)

# Sample Data - Statistics
`STATISTICS SOURCE SAMPLES`
![10.png](/.attachments/10-860611ad-2055-4720-8c1f-b54b49f735f3.png)
![10.5.png](/.attachments/10.5-094bb604-c830-4e0b-b83e-72a96e0cf4f5.png)
![10.6.png](/.attachments/10.6-3dfed4d3-540d-4564-b709-3c46af5e10f8.png)
# Sample Data - Voyages
`VOYAGES SOURCE SAMPLES`
![11.png](/.attachments/11-72434f36-0cbf-4e17-8252-88628898e984.png)
![11.5.png](/.attachments/11.5-80aeda25-fa33-4f3b-ae90-65de493990fd.png)
![11.6.png](/.attachments/11.6-43bdb42f-7f8f-472e-b12b-ffed740b5268.png)
![11.7.png](/.attachments/11.7-c4a84f06-1a77-4045-a06e-d8f236a978ac.png)

# Sample Sink Data - Misses
![12.png](/.attachments/12-ec1a9c7a-50b2-40d8-bcf3-6385b03b346e.png)
![13.png](/.attachments/13-a075ac01-a951-4e71-b0fa-b58ba29833a2.png)
![14.png](/.attachments/14-0d18fda6-4d16-4146-9f83-f01eca0e27b8.png)


# Sample Sink Data - Targets
![15.png](/.attachments/15-8e6f6422-70a4-4e60-a712-496530c6ce1e.png)
![16.png](/.attachments/16-bd7ee5c7-e461-4931-96b4-32c6b8fee333.png)
![17.png](/.attachments/17-302ec50c-c9d1-4182-a969-4e78538ef829.png)

# Sample Sink Data - Statistics
![18.png](/.attachments/18-536dbdcd-1f3c-4ad1-91b0-5a737a30c19c.png)


# Sample Sink Data - Voyages
![19.png](/.attachments/19-f5b7733d-6273-4608-8e3f-be5aec8ee2c0.png)
![20.png](/.attachments/20-0015a7ef-f71e-4426-8f73-1142b15985d6.png)
![21.png](/.attachments/21-5c339086-04ad-471f-b31a-b45039344515.png)