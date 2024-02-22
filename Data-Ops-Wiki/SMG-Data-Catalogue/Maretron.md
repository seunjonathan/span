|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|23-Nov-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2185 <br>

[[_TOC_]]

# Overview

This sub-page provides details of the tables and fields curated for the **Maretron** dataset.

## Source
* `Source Type`: REST API (XML)
* `URL`: https://tcs.maretron.com/get_data.php
* `Credentials`: contact @<Yuri Fedoruk> 

## Sink
* `Server`: _syn-smg-prod-ondemand.sql.azuresynapse.net_
* `Database`: _silver_
* `Credentials`: contact @<Yuri Fedoruk>

_Ref_: [Runbook Maretron](/Data-Ops-Wiki/Runbook-Maretron-ETL)

## Curated Data

Except for the _Description_ column, the contents of the table below were generated
 by running the query:

    SELECT table_schema, Table_Name, column_Name, data_type FROM information_schema.columns WHERE TABLE_SCHEMA = 'maretron'


`TODO`: Add in descriptions of each field


table_schema|Table_Name|column_Name|data_type| Description
---|---|---|---|---
maretron|vw_Telemetry|Timestamp_PST|datetimeoffset
maretron|vw_Telemetry|DAT_0|bigint
maretron|vw_Telemetry|TIM_0|bigint|time
maretron|vw_Telemetry|vessel_name|varchar
maretron|vw_Telemetry|COG_0|float|course over ground
maretron|vw_Telemetry|COG_255|float|course over ground
maretron|vw_Telemetry|EFR_0|float|port fuel rate
maretron|vw_Telemetry|EFR_1|float|starboard fuel rate
maretron|vw_Telemetry|ETH_0|float|port tachometer
maretron|vw_Telemetry|ETH_1|float|starboard tachometer
maretron|vw_Telemetry|FFR_0|float|port fuel rate
maretron|vw_Telemetry|FFR_1|float|starboard fuel rate
maretron|vw_Telemetry|L/L_255|varchar|lat;long
maretron|vw_Telemetry|SOG_0|float|speed over ground
maretron|vw_Telemetry|SOG_255|float|speed over ground
maretron|vw_Telemetry|TFT_255|float|total fuel rate
maretron|vw_Telemetry|TTF_255|float|total trip fuel used
maretron|vw_Telemetry|Lat|float|latitude
maretron|vw_Telemetry|Long|float|longitude
maretron|vw_Telemetry|STW_2|float|speed through water
maretron|vw_Telemetry|DAT_255|varchar|date
maretron|vw_Telemetry|Timestamp_UTC|datetime2
maretron|vw_Telemetry|row|bigint|Number of 5 minute epochs since 01 Jan 1970