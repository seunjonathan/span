|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|05-Oct-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2717 <br>  #2792 <br> #2952 <br>

[[_TOC_]]

# Introduction
Telemetry from Seaspan vessels presents can be used for many purposes including tracking their current position and heading, monitoring fuel usage and engine utilization. This information is provided by a third-party solution vendor called [Maretron](https://www.maretron.com/) and this runbook describes an Azure deployment that captures this data in real-time.

This solution is based upon an earlier implementation documented at [Runbook Vessel Telemetry](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20Data%20Ops%20Wiki/135/Runbook-Vessel-Telemetry). In comparison, this new solution is much simpler and lighter, involving only a single Azure Function App.

# Scope
The scope of this solution is limited to the processing and curation of data received directly from the Maretron API [1].

## Requirements
Id | Requirement | Description
---|---|---
1 | XML| The ETL shall process the incoming XML data and render it to a tabular form
2 | Frequency | The ETL shall procure data every 5 minutes from Maretron. This is because Maretron collects and reports data at 5 minute intervals
3 | Bronze | The incoming XML data shall be archived to `processed/bronze/MARETRON`
4 | Silver | The processed data shall be curated to `processed/silver/MARETRON`
5 | Curated files | Once processed & flattened, the incoming data shall be consolidated into a single file. This is to avoid many small files containing only 5 minutes of data, which would be slow to query.
6 | File size | `Future requirement`: Once the curated file size reaches 2gb, the incoming data shall be consolidated in a new target file.
7 | View | The curated data shall be exposed by a silver view in Synapse called `[maretron].[vw_Telemetry]`

# ETL Design
The ETL solution is centered around a schedule-triggered Azure function app. The function app performs all data procurement, transformation and curation operations. It is lightweight and fast, typically running in around 2.5 seconds. All data is curated in `adlssmgdev/prod`.

## Curated Data Format
Learnings from previous work suggest that creating a new parquet file for each 5-minute batch of data is not ideal. Firstly the parquet files them selves seem overly large. With each one having a size of around ~19kb. (By reference the raw XML file is ~25-30kb). Secondly, the approach leads to a maximum of 60/5 * 24 * 365 = ~100k files a year.

The data engineering Team understands that a more ideal solution is one in which incoming data is appended to a target file after flattening. However, there are some obstacles to this approach:
1. Only the Spark _Delta_ format supports appending of data. Parquet, Avro or ORC do not. Or at least would require the original contents to be read into memory, updated and then written back. Which increase function app compute and memory requirements.
2. The function app is not compatible with Spark, which by their nature are intended for lightweight, fast transformations. This means it cannot produce _Delta_ formatted content.

The solution adopted was to curate the data in CSV format. The initial write would generate CSV with a header row, with subsequent writes omitting the header. This makes for a fast and efficient write process. Read operations, it turns out are also fast. In fact queries against a CSV file of ~200k entries (~35mb) is no slower, and perhaps slightly faster than a set of parquet files with the same content.

**As the size of the CSV file grows, we do anticipate encountering some issues. With the current rate of ingest, such problems are not likely within the next 12-24 months. At which time, adjustments can be made to the function app to split the CSV files, or to manually archive some of the older content.**

## Azure Infrastructure Design
Hosting a function app requires access to a storage account. Since the storage account is firewall protected, access to it is via a virtual network. Both the storage account and function app must operate within the same vnet. Function apps can be billed on a pay-per-use basis, referred to as a consumption plan. However consumption plans do not support vnet access. As such, the function app used for this ETL operates on a service plan ([`P0V3`](https://portal.azure.com/#view/WebsitesExtension/ScaleSpecPicker.ReactView/id/%2Fsubscriptions%2Fe2764bf7-bdda-4887-aa05-42f41431e1c1%2FresourceGroups%2Frg-smg-towworks-dev%2Fproviders%2FMicrosoft.Web%2Fserverfarms%2Fasp-maretron-v2-dev)), albeit a low cost one. `TBD` The even cheaper `S1` plan should be tried.

![maretron 1.png](/.attachments/maretron%201-847b8907-61c8-4185-824d-3029428d9378.png =700x)

## Components
Item Type | Name | Description
----|---|---
Storage Account | `adlssmg` | This is the storage account is common to and used by all SMG ETL deployments.
Virtual Network | `vnet-smg` | The storage account is attached to a virtual net. All other SMG components, including function apps, data factories and Databricks workspaces can only access the data via this vnet.
Function App | `fa-maretron-v2` | The function app that is responsible for data procurement, transformation & curation. It hosts a single function called `api2csv`. The function is automatically triggered every 5 minutes.
Service Plan | `asp-maretron-v2` | The function app is associated with this service plan. The service plan can be either scaled vertically or horizontally. Given that the processing load is quite light, compute costs can be kept to a minimum. Though with a service plan, billing is 24/7.
Application Insights | `ai-maretron-v2` | An invaluable component during the development process or for troubleshooting. This enables access and visibility to the logs generated by the function app. If necessary, it is also possible to view the logs in a live stream.
### Resource Groups
RG | Scope
--|--
`rg-smg-maretron` | As with other SMG ETLs, this ETL also has it's own resource group. Doing so enables each ETL to be managed separately. As well as allowing billing costs to be tracked on an ETL basis.
`rg-smg-common` | To avoid proliferation of infrastructure components, those common to all SMG ETLs fall into this resource group.

### Networking
As mentioned earlier, access to data in a firewalled storage account is not trivial, even for other Azure components within the same subscription. The following must be established:
1. Create or identify a `VNET` associated with the target storage account:<br>
![Maretron 2.png](/.attachments/Maretron%202-69172675-7339-40e9-8e14-282a9945f2e8.png =600x)

2. Enable vnet integration on the function app and attach to an available subnet:<br>
![3.png](/.attachments/3-b471683a-50c7-4bfa-8f59-752d735cc204.png =400x)


# Data Serving
The curated data is served via a view called `maretron.vw_Telemetry` in the silver database of `smg-syn`.

# Data Sources & Sinks
## Data Sources
All data is obtained via the Maretron API.<br>
|Name|Source|Description|Sample|
|--|--|--|--|
|Dataset Contents|REST API|`https://tcs.maretron.com/get_data.php`<br> `username`: `Seaspan`<br>`password`: See @<Yuri Fedoruk> <p>|![4.png](/.attachments/4-2d183109-e4f3-4423-8cf1-bc010e6a708f.png)|
 
## Data Sinks
The goal of this function app is to convert the raw xml data into csv format. One csv file is generated and the data gets appended to same csv file whenever the function app runs.

The following describe the data generated by the function app:
|Name|Sink|Description|Sample|
|--|--|--|--|
|Raw JSON|* storage: `adlssmgprod`<br/>* container: `processed` <br/> * folder: `bronze/MARETRON`|Raw JSON data from the MARETRON REST API lands here.|
|CSV|* storage: `adlssmgprod`<br/>* container: `processed` <br/> * folder: `silver/MARETRON/telemetry.csv`|Each time the function app runs the data gets appended in the form of csv.|

# Troubleshooting and Maintenance
It is recommended that the log output accessible via application insights are used. They can be found here:<br>
![5.png](/.attachments/5-5da60f60-ec9f-4c14-b685-478ad92c4e4b.png =150x)

# Promoting Content from Dev to Prod
`TBD`

# Updates
An update was made to the ETL (to satisfy #2952) to support a new sensor that was recently installed on Cavalier. The sensor measures speed through water. The change introduces a new field called `STW_2`

# References
[1] Maretron telemetry units <br>:
![6.png](/.attachments/6-ea4a2391-e101-4b4d-8812-0dd5d153d6ba.png =300x)