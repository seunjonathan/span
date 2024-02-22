
|||
|--|--|
|**Status**|Draft|
|**Version**|v0.6|
|**Date**|07-Feb-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Ticket**| #985 <br> #1652 <br> #1934 <br> #1935 <br> #1862 <br> #2064 <br> #3235

[[_TOC_]]


# Introduction
Seaspan Ferries Corporation uses [Beaver Labs](https://www.beaverlabs.net/), a provider of data aggregation services to visualize and monitor fleet activity. To do so requires support for transferring operational data, in this case, departure and arrival information to the Beaver Labs service.

This runbook describes the as-built solution.

## Requirements
The proposed approach is to build a secure externally accessible API that can be called by servers owned by Beaver Labs. The requirements would be as follows:

1. The API shall return JSON formatted data
1. The API shall require a start and end date to be specified
1. The API shall return data for all departures that fall within the specified start and end date
1. The API shall return departure and arrival information both actual and scheduled
1. The API shall return a response within a reasonable amount of time, typically less than 60 seconds.

# Technical Solution
The solution implements a web server and deploys it an Azure Web App. A Web App is chosen instead of say a function app, since function apps are intended to process short lived computations that last at most minutes and are not intended for tasks that run indefinitely.<p>
The data to be accessed is stored using the Databricks Delta format. Typically processing Delta formatted data involves Spark and therefore a Spark cluster. However, the Web App needs only to read the data, not write into the Delta tables. For this Databricks have provided a library called the _Delta Standalone Reader_ [[2]](#References). A `pip` installable Python implementation is available too, [[3]](#References). The Web App uses this library.

## Sequence Diagram
The diagram shows the sequence of operations each time a user hits the REST endpoint exposed by the web app.<p>
![1.png](/.attachments/1-80e5528c-47c0-4ea2-8673-0c76fcb6dc0b.png =450x)

## Web App
The Web App is coded in Python and implements a REST endpoint using [Flask](https://flask.palletsprojects.com/en/2.0.x/https://flask.palletsprojects.com/en/2.0.x/). The endpoint is secured using an API key. There are two services exposed by the server:
1. `/`
1.1 This is mostly for testing purposes. It returns version information and is useful in verifying correct deployment of the service.
1. `/get_schedules`
2.1 This service returns schedule information. A `start_date` and `end_date` parameter must be provided. Data for scheduled departures that occur on or after the `start_date` but before the `end_date` will be returned.

|Sample Query|Sample Response|
|--|--|
|GET `https://webapp-beaverlabsapi-dev.azurewebsites.net/get_schedules?start_date=2021-10-01&end_date=2021-10-02`<br>HEADER `api-key`=`<secret API key>`<br>|![2.png](/.attachments/2-9a34c0d1-e614-4638-b714-15ca8504bf09.png =300x)  |

The Web App uses the _Delta Standalone Reader_ to download four separate Delta tables that contain the necessary information. The tables are joined and filtered. The resulting table is then converted to JSON which is returned as the response of the incoming `GET` request.

### Suggested Improvements

The implementation is not optimal and could be improved in the following ways:
1. Data is downloaded from the Delta lake each time the API is called. This data could be cached.
1. The query is filtered by date. The Delta tables (particularly `T_APPOINTMENT`) should be partitioned by at least date which would cause only the relevant partitions to be downloaded, not the entire table.
1. In addition to `start_date` and `end_date`, add support to query by vessel code/name.
1. If the response size is large, add a paging mechanism.
1. If support for multiple users is required, with perhaps different access requirements, replace the API key with an authentication & authorization mechanism. This could use Azure APIM [[4]](#References).
1. If necessary, the web app can be easily scaled either vertically (larger more powerful CPU) and/or horizontally. Furthermore, Azure supports dynamic horizontal scaling based upon measured load.


## Data Sources
The following are data sources that the solution depends upon:

|Name|Source|Description|
|--|--|--|
|TOPS Data|storage account: `adlsedwdev`<p>container: `processed`<p>folders:<br> `gold/T_APPOINTMENT`<br>`gold/T_ASSIGNMENT`<br>`gold/T_TRUCK`<br>`gold/T_ROUTE`|Only data in these tables is necessary to support the query.<p><p> The schemas and how they are joined are provided in [[5]](#References).<p>![3.png](/.attachments/3-44127098-78a0-4c89-ba0c-008e70c4923c.png =500x)|

## Data Sinks
There are no data sinks related to this solution.


# Deployment

## Terminology
In this document the term _deployment_ refers to the steps required to create an instance of this ETL solution. _Provisioning_ is a part of the deployment process in which resources are configured or populated with content, such as code.

When re-creating this solution in a new target resource group, there are 3 steps to the deployment process. They are:
1. Create the resources
![4.png](/.attachments/4-01fd081f-ece0-4052-9868-b132cfa12e3a.png =200x)<p>
1. Enable resources to access the `adlsedwdev` storage account. See the _Networking_ section below.
1. Provision the resources. See the _Provisioning_ section below.



## Networking

|Resource|Description|
|--|--|
|Web App|`adlsedwdev` and the Web App must connect to the same subnet.<p>At the storage account<p>![5.png](/.attachments/5-3a96c03e-0864-439f-a72d-b05110f9951f.png =350x)<p>At the Web App<p>![6.png](/.attachments/6-5876348e-69b0-4431-ab2b-ba9027ba655b.png =350x)<p>In this case a new subnet was added to `vnet-edw-dev`. Alternatively a new `vnet` could have been created inside the Web Apps resource group and then added to the storage account.|

## Provisioning
Currently no automated CI/CD pipeline exists for provisioning the content of the resources. Instead the provisioning is to be done manually. 

|Component|Repo|Description|
|--|--|--|
|Web App|`https://dev.azure.com/seaspan-edw/DataOps/_git/beaverlabs-webapp`|The project should be opened in Visual Studio Code and the desired branch selected. This can then be uploaded to the resource.<p><p>Further details about this web app can be found in the `README.md` file [[1]](#References). The `README.md` also describes how to configure the Web App settings, such as the API key.|

## Environments
A `dev` and a `prod` instance of this solution exist which appear in the following resource groups respectively: 
1. `rg-sfc-beaverlabsapi-dev-canadacentral-001`
1. `rg-sfc-beaverlabsapi-prod-canadacentral-001`

# Monitoring & Troubleshooting
App Insights is not supported for this Web App. Instead it recommended to use the Log stream feature to monitor and/or debug the app.<br>
![7.png](/.attachments/7-04a00d96-91f5-4e75-95f4-871c62a5debe.png =500x)

## Timeouts
Gabriel has notified us on occasion of timeouts observed when fetching data. This problem is observed with the following appearing in the log stream:

    [CRITICAL] WORKER TIMEOUT

E.g.:

```
home/LogFiles/2024_01_30_pl1mdlwk000CJB_default_docker.log  (https://webapp-beaverlabsapi-prod.scm.azurewebsites.net/api/vfs/LogFiles/2024_01_30_pl1mdlwk000CJB_default_docker.log)
2024-01-30T21:37:36.162679718Z [2024-01-30 21:37:36 +0000] [360] [INFO] Booting worker with pid: 360
2024-01-30T21:38:06.341516550Z [2024-01-30 21:38:06 +0000] [73] [CRITICAL] WORKER TIMEOUT (pid:306)
2024-01-30T21:38:06.344227665Z [2024-01-30 21:38:06 +0000] [306] [INFO] Worker exiting (pid: 306)
2024-01-30T21:38:06.639485625Z [2024-01-30 21:38:06 +0000] [372] [INFO] Booting worker with pid: 372
2024-01-30T21:38:36.807534828Z [2024-01-30 21:38:36 +0000] [73] [CRITICAL] WORKER TIMEOUT (pid:318)
2024-01-30T21:38:36.809028836Z [2024-01-30 21:38:36 +0000] [318] [INFO] Worker exiting (pid: 318)
2024-01-30T21:38:37.195727838Z [2024-01-30 21:38:37 +0000] [384] [INFO] Booting worker with pid: 384
```

Workers appear to be exiting 30 seconds after boot.

If this is observed the web app is likely not going to respond to a request to fetch data.
Based upon a discussion at [stackoverflow](https://stackoverflow.com/questions/60537977/critical-worker-timeout-in-logs-when-running-hello-cloud-run-with-python-f), one suggestion is to add a timeout to the startup command.

This was found to help:

![image.png](/.attachments/image-a7e1dcef-c01b-4986-b598-5dfe9ac8888e.png =400x)

The timeout is in seconds and is defined as the length of time a worker is allowed to process requests before `gunicorn` shuts it down. Recommended practice is to pick a time long enough to allow the service to complete, but not so long that a problem would go undetected. [Official Azure documentation](https://learn.microsoft.com/en-us/azure/app-service/configure-language-python#flask-app) also suggests starting `gunicorn` with a timeout. 

On a previous occasion the server plan was scaled up. However in this case it was not obvious that the problem due to constrained resources. Both CPU and memory are below 50%:
![webapp-beaverlabsapi-health.png](/.attachments/webapp-beaverlabsapi-health-dda1f711-94c1-41e6-b1c5-2ab9fd037257.png =660x)


# Technical Debt
A potential issue exists with respect to how the Python code in the Web App is adding departure and arrival variance columns. The error/warning is shown in the figure below:<br>
![8.png](/.attachments/8-e3d7f661-7fe6-4885-b0f3-d4d2bd358c96.png =450x)

# Updates
* #1168
When the Pandas dataframe is converted to JSON, all datetimes are automatically converted to UTC and thus appear with a `Z` at the end. However the times are actually in the PST zone. Gabriel pointed out this inconsistency. While the general correct solution is to modify our Data platform to persist *all* times in UTC, the short term solution was to simply drop the `Z` after conversion to JSON and assume PST as the local timezone.

* #1652
A new table in the data lake called `BEAVERLABSAPI` is now also merged into the result before returning. This table has scheduled/departure, departure/arrival date times in UTC and is merged using the `Sailing_ID`. Data in this table is not expected to exist prior to 2022. Queries for earlier date ranges will return `null` UTC fields.

* #1925
Updating the web application to include more vessels is easy. A configuration parameter called `VESSEL_CODES_FILTER` is read upon startup. This is a comma separated list of vessel_codes as they appear in the `T_TRUCK` table.

  ![9.png](/.attachments/9-ec9fa039-d92a-4143-8609-e21d7a01c59a.png =500x)

## Accurate Ferry Arrival and Departure Times.
#1862
#1935

This requirement adds a major new piece of functionality to the BeaverLabs Web App Server. To satisfy this requirement the design approach is to add a _webhook_, to the server. The purpose of the webhook is to enable BeaverLabs systems to send data related to ferry departure and arrival events directly to Seaspan. Specifically, the need is for accurate and timely departure and arrival times.

### Requirements
Formally, the requirement is as follows:
   1. The data lake shall curate ferry departure and arrival times as captured by Beaver Labs in a timely manner.
   1. The data shall be curated no later than 5 minutes after it is captured.

### Design Approach
Two approaches were considered. (1) A Beaver Labs supported API is polled (at intervals of less than every 5 minutes. (2) A web hook is exposed allowing Beaver Labs to push data to Seaspan as and when it happens. Given that the frequency of these events is in the order of hours, the second approach was deemed more efficient and effective. Further details of this webhook are:

    1. URL: base-url/event
    2. Authentication mechanism is via the existing API-KEY.
    3. HTTP POST body must contain a valid JSON object
    4. Contents of this JSON object must confirm to specifications in ref [6]
    5. The webhook will save the incoming payload to a timestamped file in landing@bronze/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/
    6. The webhook will create parquet data and save to timestamped files in processed@silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/
    7. The parquet file will always have these and only these column names:  meta_id,meta_topic,meta_recorded_at,data_passage_id,data_passage_started_at,data_passage_completed_at,data_passage_from_dock_id,data_passage_from_dock_name,data_passage_from_dock_port_id,data_passage_from_dock_port_country_id,data_passage_from_dock_port_name,data_passage_from_dock_port_unlocode,data_passage_to_dock_id,data_passage_to_dock_name,data_passage_to_dock_port_id,data_passage_to_dock_port_country_id,data_passage_to_dock_port_name,data_passage_to_dock_port_unlocode,data_passage_vessel_id,data_passage_vessel_imo_number,data_passage_vessel_name,data_passage_voyage_id,data_passage_voyage_number

### As-Built Solution
The following captures some details of the solution that was built.
#### Web-App Updates
* A new endpoint called `/events` was added to the BeaverLabs web app
* The payload data is upon receipt landed to `landing@bronze/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/`
* The payload (JSON) is flattened and immediately curated to `processed@silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/` in parquet format.

#### Synapse Views
* A new view is created on top of `processed@silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/` named `[silver].[blabs].[vw_EVENTS]`
* A new view is created by joining `[silver].[blabs].[vw_EVENTS]` & `[gold].[dbo].[vwT_ASSIGNMENT_EXT]` called `[gold].[dbo].[vwT_ASSIGNMENT_EXT_EVENTS]`. The details of these views is available in [Synapse](https://web.azuresynapse.net/en/authoring/analyze/sqlscripts/1930%20BeaverLabs%20Events?subFolderPath=silver%2FBEAVERLABS%2FDEPARTURE_ARRIVAL_EVENTS&workspace=%2Fsubscriptions%2Fe2764bf7-bdda-4887-aa05-42f41431e1c1%2FresourceGroups%2Frg-edw-dev%2Fproviders%2FMicrosoft.Synapse%2Fworkspaces%2Fsyn-edw-dev)

Since the web app updates the folder that backs these views immediately upon receipt of the payload, the updated data is available immediately in the view too.

## Migration from `EDW` to `SMG`
#3235

The original BeaverLabs Web app was deployed in `EDW` resource groups. With the separation of Azure infrastructure to Seaspan Marine specific resource groups (and eventually SMG subscription), the as-built solution must be migrated to use the TOPS data curated by the `SMG` solution. 

### Impacts
The following enumerates the impacts known to date.

# | Component / Data | Description | Impact
---|---|---|---
1 | Web app outgoing data | The Web app builds a gold data set on-the-fly. Contents are filtered as per start / end dates in the REST API request and returned to the caller as JSON. | The source will change from `aldsedwdev/prod` to `adlssmgdev/prod`
2 | Web app incoming data | The Web exposes an endpoint to accept departure and arrival information in JSON format. | The target will change from `aldsedwdev/prod` to `adlssmgdev/prod`
3 | ADF Pipeline | An ADF pipeline is used to satisfy #1639 which adds time fields in UTC to the outgoing data. | A new equivalent pipeline must be hosted in SMG. In EDW the data is persisted to `processed/gold/BEAVERLABSAPI` and exposed by a view in Synapse called `gold.vwBEAVERLABSAPI`. Consider adopting an alternative name as this is too generic. E.g. UTC_TIMES. Consider re-using `curate_parquet.py` from the `parquet2delta_sparkapp` repo when building the new pipeline. 
4 | Web app code | The Web app accepts incoming departure_and_arrival events. It serves requests for schedule information. | The configuration (environment variables) will need to be updated to point to `adlssmgdev/prod`. The networking will have to be changed to attach the web app to a new subnet connected to `adlssmgdev/prod`. The code contains semi-hardcoded paths to the silver delta tables. These are affected (in `EDW` only gold tables were referenced).
5 | Incoming departure_arrival_events data. | This data is stored as parquet by the WebApp in EDW `silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS`| The JSON and parquet versions of the incoming departure_arrival_events data is to be copied over to corresponding locations in `adlssmgdev/prod`.

### Migration Steps
Do this all in `dev` first.
1. Update WebApp environment to point to `adlssmgdev/prod`. This includes updating the subnet, without which access will be denied.
1. Create a new pipeline in `adfv2-tops-dev/prod` called `PL_BEAVERLABS_UTC_TIMES` to address the requirements of #1639. The target table should be  `silver/BEAVERLABS/UTC_TIME`. Try to re-use the existing `curate_parquet.py` available in the `parquet2delta-sparkapp` repo. Base the pipeline in the EDW PL_TOPS_BEAVERLABSAPI pipeline.
1. Run the new PL_BEAVERLABS_UTC_Times pipeline. This will create a new BEAVERLABS/UTC_TIMES table needed by the web app.
1. Update WebApp `build_schedule_table` method to reference tables in `silver/BEAVERLABS` instead of simply `gold`.
1. Locally run `driver.py` in the `beaverlabs-webapp` project to see if the changes work. (It will attempt to pull data from the storage account). (Your IP must be included in the firewall of `adlssmgdev/prod` for this to work).
1. Upon completion, manually validate data. E.g. after migrating `dev` compare data with that returned by the pre-migrated `prod` version. 
1. In EDW, a Synapse view is available in `silver.blabs.vw_EVENTS`. This exposes the contents of `silver/BEAVERLABS/DEPARTURE_ARRIVAL_EVENTS/`. A similar view should be created in SMG for the same data.
1. In EDW, a Synapse view is available in `gold.dbo.vwBEAVERLABSAPI` that exposes data in `processed/gold/BEAVERLABSAPI`. This data is the UTC time related content for #1639 content generated by the EDW pipeline PL_TOPS_BEAVERLABS_API`. Consider adding a similar view for this in SMG, if needed.


# References
[1] [README.md](https://dev.azure.com/seaspan-edw/DataOps/_git/beaverlabs-webapp?path=/README.md&_a=preview)
[2] [Natively Query Your Delta Lake With Scala, Java, and Python](https://databricks.com/blog/2020/12/22/natively-query-your-delta-lake-with-scala-java-and-python.html)
[3] [delta-lake-reader 0.2.10](https://pypi.org/project/delta-lake-reader/)
[4] [About API Management](https://docs.microsoft.com/en-us/azure/api-management/api-management-key-concepts)
[5] [TOPS Table Schemas](https://dev.azure.com/seaspan-edw/dc79f102-b651-4c74-9c83-85a2733f6cfb/_apis/wit/attachments/7cf242f1-7f2e-46a2-8674-63c3595b39c4?fileName=TOPS-Table-Schemas.xlsx)
[6] [Beaver Labs Webhook V1](https://pitchbook.beaverlabs.net/public/webhooks_v1?token=SFMyNTY.g2gDdAAAAAJkAAljb21wb25lbnRkAANuaWxkAAVwaXRjaG0AAAALd2ViaG9va3NfdjFuBgD7pIlChgFiACeNAA.PXqfC8YG0YSMubLOdw6RKlNuCn8_rDN-QUh1e672aB4)
