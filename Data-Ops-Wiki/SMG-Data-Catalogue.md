|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|17-Oct-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2185 <br>


[[_TOC_]]

[[_TOSP_]]


# Introduction
One of the core initiatives of the Strategy & Transformation organization within the Seaspan Marine Group (SMG) is to develop a central data warehouse. Its purpose is to curate the many sources of operational and business data and make it readily available for reporting and analytics.

This document catalogues all data that has been curated to date. The intention is to provide the reader a comprehensive reference which describes from where, when and how the data is procured and where and how it is curated and available for consumption.


## Summary Information
In this document, the term _dataset_ will be used to refer to a different source or application provider of the data. For each set of data, the following summary information will be provided:

Metadata | Description
----|----
Dataset name | Examples include _Towworks_, _TOPS_, _Maretron_, _Prism_.
Source | The source of the data. Examples include a _REST API_, a _database_, _FTP server_, _email_.
Source format | The format of the source data. Examples include _CSV_, _XML_, _JSON_, _tabular_.
Update frequency | How often is the source accessed. Hourly, daily, weekly? Or perhaps at a higher frequency.
Archive location | Location where the raw incoming data is archived
Archive size | An approximate size in bytes of the archived data.
Curated location | The final curated location of the data.
Curated format | The format used to curate the data. Examples include _delta_, _parquet_, _CSV_.
Curated size | An approximate size in bytes of the formatted data.

## Detailed Information
Each dataset is typically curated as a set of tables within the data warehouse, each with its own set of fields. In addition to the above then, sub pages will provide details of each dataset. These will include references to the source of the data and details to the table and field level.

Metadata | Description
---|---
Dataset name | Examples include _Towworks_, _TOPS_, _Maretron_, _Prism_.
Database | Name of the Synapse database where the dataset is curated
Schema | The name of the schema in the database
Table name | The name of the table in the schema
Field name | The name of the field in the table
Field type | Examples include _int_, _varchar_, _numeric_, _datetime2_.
Description | Optional manually entered description. Use this to capture as-needed knowledge of each field.

----------------------------

## Instructions for Updating this Catalogue
This wiki is a living document which is expected to change over time. When a new dataset is added, this catalogue should be updated accordingly. The instructions for updating this document are as follows:
1. Add a new entry for the dataset into the [Dataset Summary](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20Data%20Ops%20Wiki?wikiVersion=GBwikiMaster&_a=edit&pagePath=/Data%20Ops%20Wiki/SMG%20Data%20Catalogue&pageId=206#dataset-summary) section.
2. Collect statistics using the ![data catalogue.png](/.attachments/data%20catalogue-aba22c5a-fa96-4990-8c6d-e23e80c63411.png =75x) feature in Azure Storage Explorer. (**You must navigate to one level inside the folder for which statistics are to be collected**. Simply selecting it is not correct).
3. Add a new sub-page for the dataset and link to it from the Dataset Summary table
4. Follow the pattern/template observed in other sub-pages, ensuring to include a `Source`, `Sink` and `Curated Data` section.

-----------------------------

# Dataset Summary
Dataset name | Source | Source format | Update frequency | Archive location | Archive size | Curated location | Curated format | Curated size | As-of date
---|---|---|---|---|---|---|---|---|--|
[Towworks](/Data-Ops-Wiki/SMG-Data-Catalogue/Towworks)| API | JSON | 1 hr | `adlssmgprod`@processed/bronze/TOWWORKSv2 | 8.54 GB | `adlssmgprod`@processed/silver/TOWWORKSv2 | Delta | 11.59 GB | 2023-10-16
[Prism](/Data-Ops-Wiki/SMG-Data-Catalogue/Prism)| API | JSON | once daily | `adlssmgprod`@processed/bronze/PRISM| 730 MB | `adlssmgprod`@processed/silver/PRISM | Delta | 78 MB | 2023-10-16
[TOPS](/Data-Ops-Wiki/SMG-Data-Catalogue/TOPS)| MS SQL| Parquet | 2 hr | `adlsedwprod`@processed/bronze/TOPS | 31.06 TB | `adlsedwprod`@processed/silver/TOPS| Delta | 12.30 TB | 2023-10-16
[Maretron](/Data-Ops-Wiki/SMG-Data-Catalogue/Maretron)| API | XML| 5 min | `adlssmgprod`@processed/bronze/MARETRON| 479 MB | `adlssmgprod`@processed/silver/MARETRON| CSV | 26.8 MB | 2023-10-17
[PPA](/Data-Ops-Wiki/SMG-Data-Catalogue/PPA)| API | JSON | 1 hr | `adlssmgprod`@processed/bronze/PPA| 3.86 MB | `adlssmgprod`@processed/silver/PPA | Delta | 286 MB | 2023-10-16
[BeaverLabs](/Data-Ops-Wiki/SMG-Data-Catalogue/BeaverLabs)| WebHook | JSON | NA | `adlsedwprod`@bronze/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS| 9.91 MB | `adlsedwprod`@silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS | Parquet | 363 MB | 2023-10-16



 