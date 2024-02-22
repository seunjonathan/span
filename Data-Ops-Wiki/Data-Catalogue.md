|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|25-July-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**|

[[_TOC_]]

# Introduction
The purpose of this document is to catalogue all data assets curated for and behalf of the Strategy and Transformation Department of the Seaspan Marine Group (SMG). Just like the index of a book, it should be possible to look up details of each data item such as where it is stored in Azure or how to access its contents.

# Scope
Only those data items curated for SMG are in scope.

## Summary
# | Data Set | Vendor | Source | Curated Location
---|---|---|---|---
1 | Towworks |  `TBD` | `TBD` | `processed/silver/TOWWORKSv2`
2 | PRISM|  `TBD` | `TBD` | `processed/silver/PRISM`
3 | PPA |  `TBD` | `TBD` | `processed/silver/PPA`

# Data Assets
## 1. Towworks
### Description
The Towworks application captures data as it relates to all Seaspan tug towing and ship-assist operations.

### Source
`TODO: Describe here the REST API and how to access it. Include references to documentation if available`

### Location in Data Lake
`TODO: Describe the location where the curated data resides.`

#### Tables
`TODO: As part of that, describe the folder structure as it relates to the logical tables curated in the data lake`

### Access Methods
`TODO: Describe here the methods for accessing the data. E.g. end user access via a Synapse sql server endpoint, access via a notebook in Databricks.

#### Power BI Data Sets
Describe any datasets that have been created in Power BI. (This may go away if/when Microsoft Fabric is deployed).

## 2. PRISM
### Description
BeaverLabs tracks and collects usage metrics from Seaspan Ferries. The metrics include fuel consumption, engine run times, dock and undock times. These metrics are made available through BeaverLabs PRISM REST endpoint.

### Source
`TODO: Describe here the REST API and how to access it. Include references to documentation if available`

### Location in Data Lake
`TODO: Describe the location where the curated data resides.`

#### Tables
`TODO: As part of that, describe the folder structure as it relates to the logical tables curated in the data lake`

### Access Methods
`TODO: Describe here the methods for accessing the data. E.g. end user access via a Synapse sql server endpoint, access via a notebook in Databricks.

#### Power BI Data Sets
Describe any datasets that have been created in Power BI. (This may go away if/when Microsoft Fabric is deployed).


## 3. PPA
### Description
All large vessels navigating coastal BC waters are required to be assisted by experienced pilots. The Provincial Port Authority oversees these activities and makes the data available via a REST endpoint. The data collected describes all piloting activities in terms of the vessel being assisted, the tug and pilot providing the service, the customer requiring the service and of course destination location and arrival departure times.

### Source
`TODO: Describe here the REST API and how to access it. Include references to documentation if available`

### Location in Data Lake
`TODO: Describe the location where the curated data resides.`

#### Tables
`TODO: As part of that, describe the folder structure as it relates to the logical tables curated in the data lake`

### Access Methods
`TODO: Describe here the methods for accessing the data. E.g. end user access via a Synapse sql server endpoint, access via a notebook in Databricks.

#### Power BI Data Sets
Describe any datasets that have been created in Power BI. (This may go away if/when Microsoft Fabric is deployed).