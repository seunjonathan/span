|||
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|12-Oct-2022|
|**Technical owner**|Raju Penumetcha|
|**Business lead**|John Nunes|
|**Ticket**|

[[_TOC_]]

# Introduction

TOPS is a transport management system from [Fargo Systems](https://www.fargosystems.com/). Originally implemented for ground/rail transport, it is being used by Seaspan to manage ferry operations. This document describes the source data and has been compiled to assist Deloitte with the data and analytics assessment process.

# Sources
## TOPS Source Db
Seaspan uses an on-premise (MS SQL) database, which for the purposes of this document, can be considered as the source.

|**Server Details**||
|--|--|
|URL|SMC-IT-VMSQLAG1.seaspan.com|
|Database|TOPSSEASPAN_PROD|
|Schema|dbo|
|Username|PowerBIReader_SMCBITeam|
|Password|on request|

## TOPS Source Tables
Details of the source tables can be found here:
[cfgBronze-TOPS.xlsx](/.attachments/cfgBronze-TOPS-e7604ff1-c190-4024-b4ef-4363bc4eec42.xlsx)


# Ingestion
At a high-level, the ingestion process follows the practice of capturing data at differing maturity levels. Referred to commonly in the industry as `bronze`, `silver` and `gold`. Briefly, the technology solution uses Azure Data Factory for orchestration and Azure Databricks for data manipulation.

Data from the source (on-prem SQL server) is captured in the bronze layer every _n_ hours (_n_=2?).

## High Level Architecture
The following diagram presents a general architecture for a modern data lakehouse. The main technologies of note are Azure Data Factory, Azure Synapse, Azure Databricks and for reporting PowerBI. In the future Spark, Databricks and other data science tools will be deployed for help in data mining and predictive analytics.

![1.png](/.attachments/1-da79c4c3-09a3-49a1-af7d-ffaeb9bad566.png =700x)
 

# Sinks
The final processed data is available, along with data from other systems e.g. Towworks, Intelex, TOPS as views in an Azure Synapse SQL Serverless endpoint.

It's expected that in the future, tables in the gold layer would reflect the structure of business specific reports.

TODO: Migrate all TOPS tables to a schema called `tops`.

|**Server Details**||
|--|--|
|URL|syn-edw-prod-ondemand.sql.azuresynapse.net|
|Database|gold|
|Schema|dbo|
|Username|AD Username|
|Password|AD Password|

## Gold DB Information Schema
Details of the tables, columns and column types can be found here:
[TOPS_Information_Schema.xlsx](/.attachments/TOPS_Information_Schema-9b368a6c-2d32-46a7-9214-b1ff80bbb7d0.xlsx) 

# Power BI relationships
![2.png](/.attachments/2-dd24a7bf-7642-4ed3-9863-008990a97309.png)
