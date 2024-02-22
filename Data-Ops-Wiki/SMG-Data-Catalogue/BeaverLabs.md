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
* `Source Type`: Web hook. Data is pushed to us by a BeaverLabs hosted system
* `URL`: webapp-beaverlabsapi-prod.azurewebsites.net
* `Credentials`: contact @<Yuri Fedoruk>

## Sink
* `Server`: _syn-edw-prod-ondemand.sql.azuresynapse.net_
* `Database`: _silver_
* `Credentials`: contact @<Yuri Fedoruk>

_Ref_: [Runbook BeaverLabs](/Data-Ops-Wiki/Runbook-Beaver-Labs-API)

## Curated Data

Except for the _Description_ column, the contents of the table below were generated
 by running the query:

    SELECT table_schema, Table_Name, column_Name, data_type FROM information_schema.columns WHERE TABLE_SCHEMA = 'blabs'


`TODO`: Add in descriptions of each field


table_schema|Table_Name|column_Name|data_type| Description
---|---|---|---|---
blabs|vw_EVENTS|meta_id|varchar
blabs|vw_EVENTS|meta_topic|varchar
blabs|vw_EVENTS|meta_version|int
blabs|vw_EVENTS|meta_recorded_at|datetime2
blabs|vw_EVENTS|data_passage_id|varchar
blabs|vw_EVENTS|data_passage_started_at|datetime2
blabs|vw_EVENTS|data_passage_completed_at|datetime2
blabs|vw_EVENTS|data_passage_from_dock_id|varchar
blabs|vw_EVENTS|data_passage_from_dock_name|varchar
blabs|vw_EVENTS|data_passage_from_dock_port_id|varchar
blabs|vw_EVENTS|data_passage_from_dock_port_country_id|varchar
blabs|vw_EVENTS|data_passage_from_dock_port_name|varchar
blabs|vw_EVENTS|data_passage_from_dock_port_unlocode|varchar
blabs|vw_EVENTS|data_passage_to_dock_id|varchar
blabs|vw_EVENTS|data_passage_to_dock_name|varchar
blabs|vw_EVENTS|data_passage_to_dock_port_id|varchar
blabs|vw_EVENTS|data_passage_to_dock_port_country_id|varchar
blabs|vw_EVENTS|data_passage_to_dock_port_name|varchar
blabs|vw_EVENTS|data_passage_to_dock_port_unlocode|varchar
blabs|vw_EVENTS|data_passage_vessel_id|varchar
blabs|vw_EVENTS|data_passage_vessel_code|varchar
blabs|vw_EVENTS|data_passage_vessel_imo_number|int
blabs|vw_EVENTS|data_passage_vessel_name|varchar
blabs|vw_EVENTS|data_passage_voyage_id|varchar
blabs|vw_EVENTS|data_passage_voyage_number|int
blabs|vw_EVENTS|rownum|bigint