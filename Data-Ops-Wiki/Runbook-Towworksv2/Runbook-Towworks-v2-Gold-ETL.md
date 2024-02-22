|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.4|
|**Date**|14-Feb-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**|  #2293 <br> #2397 <br> #2471 <br> #2527 <br> #2675 <br> #2670 <br> #2937 <br> #3060 <br> #3072 <br> #3137 <br>  <br> #3141 <br> #3316 <br> #3283

[[_TOC_]]

# Introduction

This runbook captures technical details of the solutions implemented and deployed to support building of reports and visualizations for Towworks. Whereas [Runbook Towworks v2](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/84/Runbook-Towworksv2) addressed the ETL process for generating `silver` tables from the raw `bronze` data, this runbook deals with the construction of tables in the `gold` layer.

# Design

The general design approach is as follows:
1. Build a new `PySpark` app for each new gold view. This app addresses the requirements for the report by implementing the necessary data transformations and aggregations.
    * The implementation of the app follows the [Definition of Done](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/83/Definition-of-Done-for-Technical-Work) criteria. Which means that it will include unit tests, will follow a review process and be accompanied by documentation. The documentation can be included in or added to this runbook.
2. The App is triggered from the `_PL_Towworks_Silver2Gold` pipeline within `adf-towworks`.

# Gold Tables
Item # | Name of Report | Name of Project in ADO | Name of Deployable PySpark Script | Location of resulting Delta table
--------|----|-----------|-------------|--------
1 |Exception Report | `towworks-exception-report` | `towworks-overlaps.py` | processed/gold/TOWWORKSv2/EXCEPTIONS
2 |Valid Events| `towworks-validevents-report` | `build-validevents-report.py` | processed/gold/TOWWORKSv2/VALIDEVENTS
3 |Fleet & Vessel Performance| `towworks-fleetperformance-report` | `build_events_report.py` | processed/gold/TOWWORKSv2/FLEETANDVESSELPERFORMANCE
4 |VPA| `towworks-vpa-report`|`build_vpa_report.py`|processed/gold/TOWWORKSv2/VPA
5 |TRANSPORT CANADA| generic-sql2delta-sparkapp|`curate_sql2delta.py`|processed/gold/TOWWORKSv2/TRANSPORT_CANADA


# SparkApps

## Exception Report
### Introduction
As part of tug & barge operations at Seaspan, incoming job requests have to be allocated to tugs based upon availability of resources. Typically this information comes by way of the `WorkOrders` and `WorkOrderLinks` tables. The actual activity of tugs and barges, the _events_ are captured in the `Events` table. This information, for example can then be used to determine billing information.

At times however it is possible for the data in these tables to become inconsistent. Maybe due to data entry errors for example. Subsequently the data may show that a tug, was working on more than one job at a time. Clearly something that is not possible. The purpose of the _exception report_ is to point out these inconsistencies. Once identified, the error can be corrected for. Perhaps a date was entered incorrectly. 

### Requirements
The base requirement is to look for different events that involve the same asset, but have overlapping start and end times. Although the requirement is not as simple as that and depends upon the type or name of event.

The specific requirements will not be reproduced here. The reader is referred to the [unit tests](https://dev.azure.com/seaspan-edw/DataOps/_git/towworks-exception-report?path=/tests&version=GBmain) and the [output of these tests](https://dev.azure.com/seaspan-edw/DataOps/_git/towworks-exception-report?path=/unittest.log&version=GBmain).

### Dependent Silver Tables
To build the exception report, the following silver tables are used:
```
   EVENTS
   WORKORDERS
   WORKORDERLINKS
```
### Transformations
The following data transformations applied are:
1. Join `WORKORDERS` to `EVENTS` on `Work_Order_Number`
2. Filter `WORKORDERLINKS` for the most recent record associated with a `WORKORDERGUID`
3. Left join output of `2` to output of `1` on `WORKORDERGUID`
4. Perform overlap/exception detection on output of `3`

### Project Repo
This PySpark app is hosted in Azure DevOps at [towworks-exception-report](https://dev.azure.com/seaspan-edw/DataOps/_git/towworks-exception-report).


## Valid Events Report
### Introduction
As part of tug & barge operations at Seaspan, Event report should consist of details like what type of Action and Event is performing like, Towing, Pick-Up etc.,  For each type of Action there are different type of information needs to be linked like for Pick-Up location regarding where to pick-up, where to drop-off. In the same way in case of Towing how many barges are performing the action and how many tugs are being used to complete work and along with these where are these Events being linked to in Workorders.

This `Valid Event Report` will be sum of all these information into one report so the stake-holders will be able to get all the information required at one place.

### Requirements
The base requirement is to generate a `Valid Event Report` with checking the `Action` type of the `Event` and adding new columns like `Link_Number`, `Tug_Service_Group`, `Tow-Type` and renaming some of the existing columns as per requirement provided in the story #2471, #3060

Added `Billing_Company_Name` column to the report as per requirement in story #2675

### Dependent Silver Tables
To build the Valid Events report, the following silver tables are used:
```
   EVENTS
   LOCATION
   WORKORDERLINKS
   TUGSERVICEGROUPS
   ASSET
   COMPANY
```
### Transformations
The following data transformations applied are:
1. Filter `EVENTS` with column `Action` with [Event Ignore List.txt](/.attachments/Event%20Ignore%20List-3f04ad43-9fdb-4b80-aa85-ce981e2cc4a3.txt), stop, start and delay and `MARKED_AS_DELETED` column is false.
2. Left join `EVENTS` to `LOCATION` on `LOCATIONGUID` for `to_location` and `from_location`.
3. Left join output of `2` (from_location) with `WORKORDERLINKS` on 'WORKORDERGUID' for `Link_Number`.
4. Left join output of `3` (Link_Number) with `COMPANY` on `COMPANYGUID` for `Billing_Company_Name`.
5. Cast the columns of StartTime, EndTime, Hours into integer and renamed them as `Start_Time_DI, End_Time_DI, Time_Hours`.
6. Left join output of `5` (integer cast) with `TUGSERVICEGROUPS` CSV provided for `ByAssetGuid` and joined the service group name and renamed column as `Tug_Service_Group`.
7. Left join output of `6` (tug_service_group) with `ASSET` table provided for Asset_Guid and concatenated `SERVICEGROUPNAME` from `ASSET` table to `Tug_Service_Group`. 
8. Aggregated `Barge and Tug` count based on the `Link_Number` to get the count of the barges and tows in the Events as `num_barges` and `num_tugs`.
9. Depending on count of `num_barges` left joined new column `Tow_Type` to output `7` if `Action` is `Towing`. 
10. Depending on `Link_Number, Tug and Tow_Type` with `Event_Name = Towing` calculate `Min_Start_Time and Max_End_Time` for each tug and calculate `Tug_Time_Hours`.

_Note: If `Tow_Type` is Single show the value for `Tug_Time_Hours` and when `Tow_Type` is `Tandem, Triple or Super_Tow` only first row shows value for `Tug_Time_Hours` and other rows will show zero._

### Project Repo
This PySpark app is hosted in Azure DevOps at [towworks-validevents-report](https://dev.azure.com/seaspan-edw/DataOps/_git/towworks-validevents-report).


## Fleet and Vessel Performance Report
### Introduction
As part of tug & barge operations at Seaspan, Event report should consist of details like what type of Action and Event is performing like, Towing, Pick-Up etc.,  For each type of Action there are different type of information needs to be linked like for Pick-Up location regarding where to pick-up, where to drop-off. In the same way in case of Towing how many barges are performing the action and how many tugs are being used to complete work and along with these where are these Events being linked to in Workorders.

This `Fleet and Vessel Performance Report` will be sum of all these information into one report so the stake-holders will be able to get all the information required at one place.

### Requirements
The base requirement is to generate a `Fleet and Vessel Performance Report` with checking the `Action` type of the `Event` and adding new columns like `day_StartTime`, `day_EndTime`,`Link_Number`, `Tug_Service_Group`, `Tow-Type`, `Tug_Time_Hours` and renaming some of the existing columns as per requirement provided in the story #2527, #3072, #3137

### Dependent Silver Tables
To build the Valid Events report, the following silver tables are used:
```
   EVENTS
   LOCATION
   WORKORDERLINKS
   TUGSERVICEGROUPS
   ASSET
```
### Transformations
The following data transformations applied are:
1. Filter `EVENTS` with column `Action` with stop, start and delay and `MARKED_AS_DELETED` column is false.
2. Left join exploeded `EVENTS` to `LOCATION` on `LOCATIONGUID` for `to_location` and `from_location`.
3. Left join output of `2` (from_location) with `WORKORDERLINKS` on 'WORKORDERGUID' for `Link_Number`.
4. Aggregated `Barge and Tug` count based on the `Link_Number` to get the count of the barges and tows in the Events as `num_barges` and `num_tugs`.
5. Depending on count of `num_barges` left joined new column `Tow_Type` to output `4` if `Action` is `Towing`. 
6. Aggregated `Barge and Tug` count based on the `Link_Number` to get the count of the barges and tows in the Events as `num_barges` and `num_tugs`.
7. Depending on count of `num_barges` left joined new column `Tow_Type` to output `6` if `Action` is `Towing`.
6. Depending on `Link_Number, Tug and Tow_Type` with `Event_Name = Towing` calculate `Min_Start_Time and Max_End_Time` for each tug.
7. Explode `EVENTS` records so that an event that spawns for multiple days is enumerated on a daily basis based on `Min_Start_Time and Max_End_Time` and place them in `day_StartTime` and `day_EndTime` columns.
8. Cast the columns of StartTime, EndTime, Hours into integer and renamed them as `Start_Time_DI, End_Time_DI`.
9. Left join output of `8` (integer cast) with `TUGSERVICEGROUPS` CSV provided for `ByAssetGuid` and joined the service group name and renamed column as `Tug_Service_Group`.
10. Left join output of `9` (tug_service_group) with `ASSET` table provided for `Asset_Guid` and concatenated `SERVICEGROUPNAME` from `ASSET` table to `Tug_Service_Group`. 
11. Depending on `Event_Name` calculate `Time_Hours = End_Time - Start_Time` and when `Event_Name` is `Towing`, assign `Time_Hours` for first row and others are zero.
12. Depending on `Tow_Type and Event_Name` calculate `Tug_Time_Hours` and add it to output `12`.

### Calculation of Tug_Time_Hours
```
    'IDLE TIME - Crew On',
    'REPOSITIONING', 
    'Towing', 
    'FUEL', 
    'Tug Assist', 
    'UNSCHEDULED MAINTENANCE CREW ON', 
    'Crew On Time', 
    'SCHEDULED MAINTENANCE CREW ON', 
    'Ship Assist (Hourly Work)', 
    'Crew Change', 
    'Crew Off Time', 
    'Barge Maintenance', 
    'TRAINING', 
    'GRUB', 
    'Lite Boat', 
    'StandBy', 
    'Tie-Up Checks', 
    'Dock', 
    'PREP FOR REGULATORY INSPECTION', 
    'REGULATORY INSPECTION', 
    'Undock', 
    'Harbour Barging (Hourly Work)', 
    'Launch Internal', 
    'Undock and Dock', 
    'Lines', 
    'Relief Tug', 
    'WORK AS DIRECTED', 
    'Escort MRA', 
    'Launch', 
    'Undock and Escort', 
    'Escort 2nd Narrow', 
    'Escort and Dock', 
    'IDLE TIME - Crew Off', 
    'SCHEDULED MAINTENANCE CREW OFF', 
    'Shift Hourly', 
    'Shift Repair to Fleet', 
    'Tanker Escort', 
    'TANKER TETHERED TOW', 
    'Tug Assist Time', 
    'Undock Escort and Dock', 
    'UNSCHEDULED MAINTENANCE CREW OFF'
```
If Event_Name is equal to any name mentioned above except `Towing`, then Event is split day wise and Tug_Time_Hours are calculated as per day basis. In case of `Towing`, if `Tow_Type` is Single show the value for `Tug_Time_Hours` and when `Tow_Type` is `Tandem, Triple or Super_Tow` only first row shows value for `Tug_Time_Hours` and other rows will show zero.

If `Event_Name` is `Towing` and `Link_Number` is null then `Tow_Type` is always `Single`.

`Note: When Link_Number is null perform partition by considering Work_Order_Number as partition key and calculate Tug_Time_Hours and Time_Hours. If Link_Number is not null then Link_Number is primary key.`

### Project Repo
This PySpark app is hosted in Azure DevOps at [towworksv2-fleetandvesseltughours-report](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/towworksv2-fleetandvesseltughours-report?path=/build_fleetandvesseltughours_report.py).

## VPA Report
### Introduction
This report is compiled to satisfy a requirement for Seaspan to share cargo traffic information with the Vancouver Port and Vancouver Fraser Port Authorities (VFA & VFPA). To date, this data has been manually compiled into an Excel file and sent via email.

### Requirements
1. The latest requirements indicate that the report should have the following content:
<IMG  src="https://attachments.office.net/owa/ssarkaria%40seaspan.com/service.svc/s/GetAttachmentThumbnail?id=AAMkAGFmNDRlMmJmLThkYTQtNGJmOC04NzZjLTliMWNkNWYyMWRhZQBGAAAAAAA1QyY8UWD4T474UGIEzqayBwDHHnGnAJjKQJUar5wySdE6AAAAAAEJAADHHnGnAJjKQJUar5wySdE6AAGKrT1yAAABEgAQAAt9Zmtr0kRElcQt8J1dzh4%3D&amp;thumbnailType=2&amp;token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjczRkI5QkJFRjYzNjc4RDRGN0U4NEI0NDBCQUJCMTJBMzM5RDlGOTgiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJjX3VidnZZMmVOVDM2RXRFQzZ1eEtqT2RuNWcifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZDkzY2U0NjVkYjAyNGJhOGE3ZGM4ZmMzNmI5ZmUzNDMiLCJ2ZXIiOiJFeGNoYW5nZS5DYWxsYmFjay5WMSIsImFwcGN0eHNlbmRlciI6Ik93YURvd25sb2FkQDAyYzQwMTdjLWQ2MDYtNGQzNS1iMDY3LWFmZjg5ZTkwNjllYiIsImlzc3JpbmciOiJXVyIsImFwcGN0eCI6IntcIm1zZXhjaHByb3RcIjpcIm93YVwiLFwicHVpZFwiOlwiMTE1MzgwMTEyMTc0NjQwNjM2NlwiLFwic2NvcGVcIjpcIk93YURvd25sb2FkXCIsXCJvaWRcIjpcImQwYmM2ZTJjLWUyMTgtNDdmNC05MWY0LWNmNGY3M2Q5NTQyYlwiLFwicHJpbWFyeXNpZFwiOlwiUy0xLTUtMjEtMTUxMjg5MzY0Mi0yOTAzNzgyMDg5LTM2NTkzNDUwMjYtMjQ0MTIyNzFcIn0iLCJuYmYiOjE2OTUzMzQxMjksImV4cCI6MTY5NTMzNDcyOSwiaXNzIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwQDAyYzQwMTdjLWQ2MDYtNGQzNS1iMDY3LWFmZjg5ZTkwNjllYiIsImF1ZCI6IjAwMDAwMDAyLTAwMDAtMGZmMS1jZTAwLTAwMDAwMDAwMDAwMC9hdHRhY2htZW50cy5vZmZpY2UubmV0QDAyYzQwMTdjLWQ2MDYtNGQzNS1iMDY3LWFmZjg5ZTkwNjllYiIsImhhcHAiOiJvd2EifQ.OeQgwtJl2pO2rHrfFWf2CDQDiFyZrJRuBfu9mWvof2CdRinTdSrxf7xQDkFeQewjEy52xMtzLNnbK_MX8ywOZxhLb2OqlmkGr_JO2dd1q5J9yDtcqu4PpyNJkHk0AysTybpI1PWazljZwLuImg9LTR6IRFx_XnELBmUqxMwlxvXsvX0qtXhZGJUE4k0I9AHB9vZuU3U7O2HB8uqL22xivDNs07z_dk1P6trU_RGWimJfybSte3rdMDwlDEHyppAIGcZE6Pt8tzemtU1YyPkjPyhdYaJgV7hUUOHdnqwzY84lvy4RbidqEua8n4NrTgjff1dCHuKKyPgZlmg4WMg8eQ&amp;X-OWA-CANARY=DIeAIP_vzEmnlUCvtwOxahAmtVbvutsY93qXwwVz-FlUJ3em34hinysVbBlBUQzTZBfgH846vAU.&amp;owa=outlook.office.com&amp;scriptVer=20230915006.11&amp;animation=true"/>
2. The process of creating and transmitting the report are to be automated, with a frequency of once a month.
3. The report should exist both as a view in the `gold` database and as a file that can be attached to an email.

### Dependent Silver Tables
To build the VPA report, the following silver tables are used:
```
   EVENTS
   LOGISTICORDERS
   CARGO
   LOCATION
```

### Transformations

The purpose of the transformation is to summarize each `Freight Order`, data for which will appear in more than one record in the `EVENTS` table. Each summarized record is to include load/unload times, load/unload ports, load/unload locations, cargo types and quantities for a single `Freight Order`. The following should be noted:

* The data transformations made to build the report focus only on the events with the _Action_=`Barge Cargo Load` and _Action_=`Barge Cargo Unload`. All other events are filtered out. (The predicate is **case-sensitive**)
* The transformation merges the `Barge Cargo Load` event and the `Barge Cargo Unload` events with the same `Freight_Order` number into a single record.
* The transformation assumes that each freight order has only two events. A `load` followed chronologically by an `unload`. It is understood that there are some cases when a tug will perform multiple loads and multiple unloads for one freight order. **In such cases, the summary may not be accurate.**
* The column `num_rows_in_order` indicates how many records were involved in the summary. Accuracy is only guaranteed for the case `num_rows_in_order`=2.
* `Start_Load_DateTime` is the `StartTime` of the *second* event in the freight order as ordered by `StartTime`
* `Port_Unloaded` is the `Port_Loaded` of the *second* event in the freight order as ordered by `StartTime`
* `Location_Unloaded` is the `Location_Loaded` of the *second* event in the freight order as ordered by `StartTime`

#### Implementation of Transformations
The rendering of this report takes a new approach. Instead of realising the table in Python  code, a PySpark application was built around an existing SQL query. The application simply loads the dependent tables in to Spark as temp views and executes a SQL.
The query below implements the transformations described above:
```
select
        Freight_Order,
        ToAsset,
        Location_Loaded,
        Port_Loaded,
        Start_Load_DateTime,
        Location_Unloaded,
        Port_Unloaded, 
        Start_Unload_DateTime,
        Cargo,
        Cargo_Type_Name,
        Cargo_Event_Quantity,
        Event_Name,
        num_rows_in_order
from (
    select
        l.ordernumber as Freight_Order,
        e.ToAssetName as ToAsset,
        fl.LocationName as Location_Loaded,
        FromLocationPortName as Port_Loaded,
        StartTime as Start_Load_DateTime,
        lead(fl.LocationName, 1)  over (partition by l.ordernumber order by StartTime) as Location_Unloaded,
        lead(FromLocationPortName, 1) over (partition by l.ordernumber order by StartTime) as Port_Unloaded, 
        lead(StartTime, 1) over (partition by l.ordernumber order by StartTime) as Start_Unload_DateTime,
        e.CargoName as Cargo,
        CargoTypeName as Cargo_Type_Name,
        CargoEventQuantity as Cargo_Event_Quantity,
        Action as Event_Name,
        row_number() over (partition by l.ordernumber order by StartTime) as row_num,
        sum(1) over (partition by l.ordernumber) as num_rows_in_order
    from vw_FACT_EVENTS e
    left join vw_FACT_LOGISTICSORDERS l on e.LOGISTICSORDERGUID = l.LOGISTICSORDERGUID
    left join vw_DIM_LOCATION fl on e.FromLocationGuid = fl.LOCATIONGUID
    left join vw_DIM_CARGO c on c.CARGONAME = e.CargoName -- ?? Some e.g. HEMLOCK not found in DIM_CARGO ??
    where Action like 'Barge Cargo%'
) r
where row_num = 1
```


### Export File
A new view is created in the `gold` database at `towworks.vw_REPORT_VPA`. The contents of this view are filtered and exported to a CSV file. This CSV file is created by Pyspark by coalescing the dataframe contents into a CSV file. The export location is `processed/exports/TOWWORKSv2/VPA`.

 
The report creation ETL will run every 15th of the month. E.g. Oct 15th, 2023. The previous month is deemed to start at `20230901T00:00` and end at `20230930T23:59`. Jobs will be included in the report if:
1. The job `Start_Unload_DateTime` comes on or after the start time, in the example above `20230901T00:00`
2. The job `Start_Load_DateTime` comes on or before the end time, in the example above, `20230930T23:59`

Thus, jobs overlapping a month boundary may appear in two reports.

    Jobs that span longer than one month will be reported in all months that the job overlaps with.
    E.g. if the job starts in May and ends in July, it will appear in the May, June & July reports.


This illustration helps to describe the inclusion criteria:
![VPA report.png](/.attachments/VPA%20report-e2cce0bf-dcc4-4acc-a388-91037b33114a.png =700x)

    Note that the observed behaviour may differ from the diagram shown since a job may not have an unload date until it has completed. In which case, the job will appear in the report for the month it completed in.

A logic app called, `la-vpamailer-dev/prod` reads the contents of this location in the storage account and emails it to a predefined recipient(s).
The name of the attachment includes a year and a month. The month is computed as the current date minus 28 days. Given that the report runs on the 15th of the month, this shoul squarely return the previous month, even in case of different numbers of days in a month.

The logic app is triggered by a pipeline in `towworks-adf-dev/prod` called `PL_Towworks-Monthly_Reports`.

### Project Repo
The project is hosted at [towworks-vpa-report](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/towworks-vpa-report)

## Transport Canada Report

### Introduction
The design of this report adopts a brand new approach. Similar to the VPA report the specification of the contents of the report is achieved using a (Databricks) SQL statement. However we now re-use a generic sparkapp, rather than build a new one. The `curate_sql2delta.py` script in [generic-ssql2delta-spark repo](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/generic-sql2delta-sparkapp) accepts parameters for the source tables and the SQL query to be applied. It will then submit the query to Databricks and store the result, in Delta format in a specified folder of the storage account. The script is fully parameterized and can be called from an ADF pipeline.

This diagram shows how the list of dependent tables and the SQL query itself is embedded into the ADF Python activity:
![image.png](/.attachments/image-1903e150-1c81-4eec-a551-5091e7c2f910.png =x400)

And the next illustrates how `curate_sql2delta.py` is invoked:
![image.png](/.attachments/image-3e87a488-bd73-4102-acf0-ffd48ad868a9.png =x500)

### Requirements
The Transport Canada report is fairly similar in nature to the VPA described earlier in this Wiki. With the addition of more columns.

The requirements of this report are captured in an Excel spreadsheet that is attached to the story #2937. 

`TBD`
  * Some aspects of these requirements are not well understood. Namely the nature of the TUG IMO and TUG IDs that are to be included. The report generates rows which summarize each cargo load/unload event. However, it seems that multiple tugs can participate in a single order and it is not clear which tug to select, or if all are to be reported, how to report all tugs.

### Dependent Silver Tables
The following silver tables are used;

     TOWWORKSv2/EVENTS
     TOWWORKSv2/LOGISTICORDERS
     TOWWORKSv2/CARGO
     TOWWORKSv2/UNITOFMEASURE

Note that some adjustments to the contents may be necessary. This is because the name of the tugs or barges in the source Excel do not necessarily match the names that appear in `TOWWORKSv2/EVENTS`.

* For example, the names of barges in the Events table do not contain spaces. E.g. `SS486` whereas the name in Excel, `SS 486`, did.
* Similarly for the names of tugs. The Excel for example referred to the tug as `Hawk` whereas in the Events table, the name used is `SS Hawk`



### Transformations
The transformations applied to the data are based on the VPA report. For details see [VPA Report Transformations](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20DataOps.wiki?wikiVersion=GBwikiMaster&pagePath=/Data%20Ops%20Wiki/Runbook%20Towworks%20v2%20Gold%20ETL&pageId=181&_a=edit#transformations).

#### Implementation of Transformations
`Ref`: See #3095 for the SQL definition of the report.

### Export File
The report is not triggered automatically and no export file is auto-generated. The approach is that the contents of the gold table are embedded manually into a larger Excel sheet that further prepares the data to be sent to Transport Canada.

### Project Repo
The report uses the code hosted at [generic-ssql2delta-spark repo](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/generic-sql2delta-sparkapp)

# Job Board Report

### Introduction
This report is to provide a backup solution of data for business owners during downtimes of `TowWorks UI`.  

### Requirements
Build a gold `Job Board Report` by using the SQL query provided in the story #3283.

### Dependent Silver Tables
```
   TOWWORKSv2/LOCATION
   TOWWORKSv2/LOGISTCSORDERS
   TOWWORKSv2/WORKORDERS
```

### Transformations

SQL query is sent from `ADF` parameters into `sql2delta spark app` and report is generated. Following SQL query is run to perform required transformations.
```
   SELECT   
   RESPONSIBLEPARTYNAME AS Operational_Group,
   BYASSETNAME AS Tug,
   LOG_ORDERS.ORDERNUMBER AS Logistic_Order_Number,
   WORKORDERNUMBER AS Work_Order_Number,
   WORKORDERSTATUSNAME AS Work_Order_Status,
   TOASSETNAME AS Barge_or_Ship,
   WORKORDERTYPENAME AS Task_Type,
   WORKLOCATIONNAME AS From_Location,
   DIM_LOCATION.LOCATIONNAME AS Task_To_Location,
   ESTIMATEDSTARTDATE AS Estimated_Start_Date,
   ESTIMATEDCOMPLETIONDATE AS Estimated_Completion_Date,
   WORKORDERINSTRUCTIONS AS Shoreside_Notes
   FROM WORKORDERS LEFT JOIN LOGISTICSORDERS AS LOG_ORDERS
   ON  LINKEDLOGISTICSLINEGUID = LOG_ORDERS.LOGISTICSORDERGUID
   LEFT JOIN LOCATION DIM_LOCATION   ON WORKTOLOCATIONGUID = DIM_LOCATION.LOCATIONGUID 
   WHERE MARKED_AS_DELETED = 0   
   AND WORKORDERSTATUSNAME IN ('Completed','Dispatched','In Planning','In Progress','Released','Created')
```

### Export file

After the delta format of report is generated, we will be copying it to a `csv` format and will be stored `processed/exports/TOWWORKSv2/REPORT_JOB_BOARD/` folder. By calling a `Logic App` this file will be updated in sharepoint everytime pipeline is run.

### Project Repo
The report uses the code hosted at [generic-ssql2delta-spark repo](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/generic-sql2delta-sparkapp)

<br>