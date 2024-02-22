|||
|--|--|
|**Status**|Draft|
|**Version**|v0.1|
|**Date**|05-Jan-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|N/A|
|**Ticket**| #1722 <br>

[[_TOC_]]

# Introduction

Based loosely upon the contents of #1722, this wiki attempts to summarize the main technical improvement opportunities as they relate to the Data Platform. It is hoped that this document can be used as a basis for discussion and planning of infrastructure and architectural improvements.

## Topics

**#**|**Topic**| **Summary**
|---|---|---|
|1|Full Table Reload|Overwrite is better than delete & reload|
|2|Hive Tables|Obsolete in favour of Synapse serverless views|
|3|Archive Raw Data|Not always happening|
|4|Coding Guidelines|Opportunity to improve readability, code efficiency and maintainability.|
|5|Ingest Frequency|Opportunity to improve efficiency|
|6|Synapse Promotion Process|We don't have one|
|7|CI/CD|Overwrite parameters need review|
|8|Documentation|?|

### 1. Full Table Reload
In some cases, (TOPS?) full table reloads are performed. These delete and then re-ingest content into the data lake. Instead of performing delete operations on the `Delta` tables, overwrite operations should be performed. The benefits of doing so are as follows:
1. No downtime. The table will never appear as unavailable to the end user as is the case now.
2. Older versions of the table will be accessible via the `Delta` _timetravel_ feature.
3. No need to trigger a restart on the web app that implements the REST API used by Beaver Labs.

#### Proposed Changes
1. Instead of delete and re-load do this: `df.write.format('delta').mode('overwrite').save(target_path)`
2. Changes may be needed to ADF pipelines which may be deleting folders in the storage account prior to re-ingesting.

TODO: Identify all tables that fall into this category (full reload).

### 2. Hive Tables
All Databrick notebooks rely upon code implemented in `0_Includes/config.py`. This notebook is a good attempt at providing re-useable common code. However a good portion of it is dedicated to storing and maintaining tables in Hive. 

For the EDW, Hive is not used and is obsolete, in favour of SQL serverless Synapse views. Tables in Synapse serverless can be queried without the need of a running cluster. Not so with Hive. Other than `0_Includes/config.py` who is using the Hive tables?

#### Proposed Actions
1. New ETLs use code from `0_Includes/config.py` sparingly. Example is the notebook for `T_TRANSPORTPLAN_CUSTOMER`.
2. Simplify some gold notebooks. Example is:

  ![infrastructure.png](/.attachments/infrastructure-2dab6ff2-9709-479f-85fc-dc3ab9a478e2.png =400x)

    All this notebook is doing is copying the silver table into a gold folder. This could be performed by a copy task in a pipeline instead.
3. CDC. Also, who is using the `_change_type`, `_commit_version` and `_commit_timestamp` fields? These are added by `0_Includes/config.py` which saves tables using the `.option("delta.enableChangeDataFeed", "true")`. To use cdc, see [Delta Change Data Feed](https://docs.databricks.com/delta/delta-change-data-feed.html)

### 3. Archive of Raw Data
The industry best practice is to archive all landed data in it's raw format. There are some cases where this is not happening. E.g. #1669. Benefits will be in terms of the ability to look back at older data to verify contents and/or to re-ingest data that initially was perhaps not done properly due to a bug or error.


### 4. Coding Guidelines
A number of opportunities for improving code readability and maintainability are noted in #1834.

`0_Includes/config.py` provides a reference to coding guidelines at https://github.com/palantir/pyspark-style-guide. A review of these and those at https://github.com/google/styleguide/blob/gh-pages/pyguide.md as a team would serve as a useful reminder. 

Benefits are readability and maintainability.

#### Proposed Changes
1. Whenever a notebook has to be updated or fixed this could be used as an opportunity to make some code improvements too.

### 5. Table Specific Ingest Frequency
Currently ingest frequency is set per pipeline. Since each pipeline is processing many tables in a single `cfgBronze` partition, all tables are reprocessed with the same frequency. E.g. All TOPS tables are reloaded every 2 hours. However, not all tables change with the same level of frequency. E.g. `T_TRANSPORTPLAN_CUSTOMER` is updated at most once a day, and perhaps only once a week. Overly frequent processing translates to wasted Azure costs.

#### Proposed Actions
Introduce a frequency parameter into `cfgBronze`. Update the pipelines so that they check this parameter prior to running the ingest.

### 6. `Dev` to `Prod` Process for Synapse
Currently there is no official process adopted for the update of artefacts in Synapse `prod`.
While no doubt, that in practice an approach is being used, it is not something written down or applied consistently.

#### Proposed Actions
Write up a process. For now, any process.

### 7. CI/CD Coordination
A CI/CD release pipeline is used to deploy git controlled versions of `adfv2-edw-dev` to `adfv2-edw-prod`.
Deployment to `adfv2-edw-prod` using the CI/CD release pipeline can (incorrectly) overwrite pipeline configurations. E.g. The url for the linked service `LS_ADLS_GEN2` in git was `https://@{linkedService().storage}.dfs.core.windows.net` but was hardcoded to `adlsedwprod` by CI/CD. There are likely other instances too.

#### Proposed Actions
Review all overwrite parameters in the CI/CD pipeline. Some may be ok hardcoded to values applicable in `prod`. Others may be need to remain as variables so that they match those used in `adfv2-edw-dev`

### 8. Documentation
There is no documentation that describes or explains many of the pipelines in `adfv2-edw`. Documentation can be very helpful when it comes to maintenance.

#### Proposed Actions
1. Going forward, changes should be captured and explained in a wiki for each pipeline. The recommended practice is to create _Runbooks_ which are used to capture the overall design and operation of an ETL. Some example runbooks are [Runbook ARAS](/Data-Ops-Wiki/Runbook-ARAS), 
[Runbook P6](/Data-Ops-Wiki/Runbook-P6) & [Runbook Vessel Telemetry](/Data-Ops-Wiki/Runbook-Vessel-Telemetry)

# Glossary 

| Term | Description  |
|--|--|
| Data Platform | The term given to the set of Azure components, including but not limited to Storage Account, Data Factory, Synapse, Key Vault that together form the data lake.|
| EDW | Enterprise Data Warehouse. EDW is often used to refer to our cloud data warehouse |
| Data Lake | A generic term for EDW |
| ADF | Azure Data Factory|
| cfgBronze | An Azure table store used to provision configuration parameters used for ingesting data into the bronze layer |

