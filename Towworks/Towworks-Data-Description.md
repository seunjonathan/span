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
[Towworks](https://towworks.com/) is a 3rd-party provider that is used by Seaspan for route planning and management of the tug boat operations. This document describes the source data and has been compiled to assist Deloitte with the data and analytics assessment process.

# Sources
There are two sources of data.
1. A REST API from Towworks
   - Tug boat operational data.
2. An on-prem MS SQL Database
   - This database is used to manage data related to the Pacific Pilotage Authority (PPA).

## Towworks API
Access to Towworks data is via an (undocumented) REST API. Incremental data from this API is retrieved every hour and used to update the data in the data lake.

|**REST API Details**||
|--|--|
|URL|https://seaspan.towworks.com|
|Username|seaspanapi|
|Password|on request|


### Example REST Call
Towworks provides access to a number of different tables. E.g. `EVENTS`, `WORKORDERS`, `TRANSACTIONS`. An example call to fetch data from the EVENTS Table is as follows:
```
https://seaspan.towworks.com/custom/seaspan/processes/TWDataBroker.aspx?COMPANYKEY={{Company}}&DATASET=EVENTS&DATETOPULLFROM=2022-10-05T00:00
```

### Example Response
The response would be as follows:

![1.png](/.attachments/1-08cd807e-0028-4a3f-b55f-92ecfaa6343d.png =450x)
 
Each table returns a different set of JSON objects that fall within the time frame specified in the request.

### Towworks REST API Source Tables
[cfgBronze-towworks.xlsx](/.attachments/cfgBronze-towworks-d86f07ce-ebc1-4c9d-964b-87541a735eba.xlsx)

## PPA Data
|**Server Details**||
|--|--|
|URL|VAN-SS-BIDB|
|Database|TOWWORKS|
|Schema|dbo|
|Username|PowerBIReader_SMCBITeam|
|Password|on request|

### PPA Source Tables
[cfgBronze-PPA.xlsx](/.attachments/cfgBronze-PPA-54529e1e-c272-46a3-8051-61506ae99588.xlsx)

# Sinks
The data is exposed as a set of views in the gold layer of the data lake. Details of the tables exposed are as follows:
[towworks-information-schema.xlsx](/.attachments/towworks-information-schema-859413c2-550c-46ef-80be-883b94f947ac.xlsx)

# Power BI relationships
## Events
![2.png](/.attachments/2-b78df03c-7d3e-47c4-aa6d-b4377c147465.png)
## PPA JOB

![3.png](/.attachments/3-a1118441-93f5-4a62-96fa-379a815c7f4b.png)

# Data Dictionary

[TowWorks Data Dictionary V1.xlsx](/.attachments/TowWorks%20Data%20Dictionary%20V1-e234d0a4-46e6-411e-be99-5f3d72e130fe.xlsx)