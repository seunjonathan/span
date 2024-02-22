|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|13-Oct-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2185 <br>

[[_TOC_]]

# Overview

This sub-page provides details of the tables and fields curated for the **PPA** dataset.

## Source
* `Source Type`: REST API
* `URL`: https://ppa.portlink.co/api/DataAPIV2/pdams
* `Credentials`: contact @<Yuri Fedoruk> 

## Sink
* `Server`: _syn-smg-prod-ondemand.sql.azuresynapse.net_
* `Database`: _silver_
* `Credentials`: contact @<Yuri Fedoruk>

_Ref_: [Runbook PPA](/Data-Ops-Wiki/SMG-Data-Catalogue/PPA)

## Curated Data

Except for the _Description_ column, the contents of the table below were generated
 by running the query:

    SELECT table_schema, Table_Name, column_Name, data_type FROM information_schema.columns WHERE TABLE_SCHEMA = 'ppa'


`TODO`: Add in descriptions of each field


table_schema|Table_Name|column_Name|data_type| Description
---|---|---|---|---
ppa|vw_DIM_Vessels|updatedAt_PST|datetimeoffset
ppa|vw_DIM_Vessels|createdAt_PST|datetimeoffset
ppa|vw_DIM_Vessels|id|int
ppa|vw_DIM_Vessels|name|varchar
ppa|vw_DIM_Vessels|imo|int
ppa|vw_DIM_Vessels|callSign|varchar
ppa|vw_DIM_Vessels|gt|int
ppa|vw_DIM_Vessels|loa|numeric
ppa|vw_DIM_Vessels|beam|numeric
ppa|vw_DIM_Vessels|lloydSeaSpeed|numeric
ppa|vw_DIM_Vessels|summerDraft|numeric
ppa|vw_DIM_Vessels|deadWeight|int
ppa|vw_DIM_Vessels|mmsi|int
ppa|vw_DIM_Vessels|flagRegistry|varchar
ppa|vw_DIM_Vessels|yearBuilt|int
ppa|vw_DIM_Vessels|vesselRemarks|varchar
ppa|vw_DIM_Vessels|vesselType|varchar
ppa|vw_DIM_Vessels|updatedAt|datetime2
ppa|vw_DIM_Vessels|airDraft|float
ppa|vw_DIM_Vessels|createdAt|datetime2
ppa|vw_DIM_Vessels|numberOfBowThrusters|int
ppa|vw_DIM_Vessels|numberOfSternThrusters|int
ppa|vw_DIM_Vessels|ownerId|int
ppa|vw_DIM_Vessels|ownerName|varchar
ppa|vw_DIM_Vessels|powerOfBowThrusters|int
ppa|vw_DIM_Vessels|powerOfSternThrusters|int
ppa|vw_DIM_Vessels|remarks|varchar
ppa|vw_DIM_Vessels|vesselTypeId|bigint
ppa|vw_DIM_Organizations|updatedAt_PST|datetimeoffset
ppa|vw_DIM_Organizations|createdAt_PST|datetimeoffset
ppa|vw_DIM_Organizations|id|int
ppa|vw_DIM_Organizations|name|varchar
ppa|vw_DIM_Organizations|shortCode|varchar
ppa|vw_DIM_Organizations|addressLine1|varchar
ppa|vw_DIM_Organizations|city|varchar
ppa|vw_DIM_Organizations|province|varchar
ppa|vw_DIM_Organizations|postalCode|varchar
ppa|vw_DIM_Organizations|country|varchar
ppa|vw_DIM_Organizations|phone|varchar
ppa|vw_DIM_Organizations|fax|varchar
ppa|vw_DIM_Organizations|updatedAt|datetime2
ppa|vw_DIM_Organizations|Agent|varchar
ppa|vw_DIM_Organizations|createdAt|datetime2
ppa|vw_DIM_Organizations|organizationType|varchar
ppa|vw_DIM_Locations|updatedAt_PST|datetimeoffset
ppa|vw_DIM_Locations|createdAt_PST|datetimeoffset
ppa|vw_DIM_Locations|name|varchar
ppa|vw_DIM_Locations|id|int
ppa|vw_DIM_Locations|shortCode|varchar
ppa|vw_DIM_Locations|districtName|varchar
ppa|vw_DIM_Locations|updatedAt|datetime2
ppa|vw_DIM_Locations|createdAt|datetime2
ppa|vw_DIM_Locations|Tariff_Area|varchar
ppa|vw_DIM_Pilots|updatedAt_PST|datetimeoffset
ppa|vw_DIM_Pilots|createdAt_PST|datetimeoffset
ppa|vw_DIM_Pilots|id|int
ppa|vw_DIM_Pilots|pilotName|varchar
ppa|vw_DIM_Pilots|firstName|varchar
ppa|vw_DIM_Pilots|middleName|varchar
ppa|vw_DIM_Pilots|lastName|varchar
ppa|vw_DIM_Pilots|nickName|varchar
ppa|vw_DIM_Pilots|pilotHomeBaseName|varchar
ppa|vw_DIM_Pilots|serviceStart|datetime2
ppa|vw_DIM_Pilots|updatedAt|datetime2
ppa|vw_DIM_Pilots|createdAt|datetime2
ppa|vw_FACT_Jobs|updatedAt_PST|datetimeoffset
ppa|vw_FACT_Jobs|createdAt_PST|datetimeoffset
ppa|vw_FACT_Jobs|etd_atd_PST|datetimeoffset
ppa|vw_FACT_Jobs|orderTime_PST|datetimeoffset
ppa|vw_FACT_Jobs|eta_ata_PST|datetimeoffset
ppa|vw_FACT_Jobs|dispatchTime_PST|datetimeoffset
ppa|vw_FACT_Jobs|number|int
ppa|vw_FACT_Jobs|status|varchar
ppa|vw_FACT_Jobs|vesselId|int
ppa|vw_FACT_Jobs|organizationId|int
ppa|vw_FACT_Jobs|PPA_billing_agencyID|int
ppa|vw_FACT_Jobs|PPA_agentContactName|varchar
ppa|vw_FACT_Jobs|fromLocationId|int
ppa|vw_FACT_Jobs|toLocationId|int
ppa|vw_FACT_Jobs|fromLanding|varchar
ppa|vw_FACT_Jobs|toLanding|varchar
ppa|vw_FACT_Jobs|region|varchar
ppa|vw_FACT_Jobs|orderTime|datetime2
ppa|vw_FACT_Jobs|etd_atd|datetime2
ppa|vw_FACT_Jobs|eta_ata|datetime2
ppa|vw_FACT_Jobs|actualDraft|numeric
ppa|vw_FACT_Jobs|actualSpeed|numeric
ppa|vw_FACT_Jobs|pilot1Id|int
ppa|vw_FACT_Jobs|pilot2Id|int
ppa|vw_FACT_Jobs|tugCompanyFromLocation|varchar
ppa|vw_FACT_Jobs|tugCompanyToLocation|varchar
ppa|vw_FACT_Jobs|PPA_numberOfTugsRequired|int
ppa|vw_FACT_Jobs|dispatchTime|datetime2
ppa|vw_FACT_Jobs|PPA_lastmodifydate|datetime2
ppa|vw_FACT_Jobs|updatedAt|datetime2
ppa|vw_FACT_Jobs|Seaspan_Time|datetime2
ppa|vw_FACT_Jobs|createdAt|datetime2
ppa|vw_FACT_Jobs|id|bigint
ppa|vw_FACT_Jobs|jobRemarks|varchar
ppa|vw_FACT_Jobs|orderingContactId|bigint
ppa|vw_FACT_Jobs|orderingContactName|varchar
ppa|vw_FACT_Jobs|organizationName|varchar