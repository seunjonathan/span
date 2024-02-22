|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|30-September-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2528 <br> #2738

[[_TOC_]]

#Introduction

This runbook captures technical details of the solutions implemented and deployed to support building of reports and visualizations for PPA. Whereas [Runbook PPA v2](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20Data%20Ops%20Wiki/124/Runbook-PPA-v2) addressed the ETL process for generating `silver` tables from the raw `bronze` data, this runbook deals with the construction of tables in the `gold` layer.

#Design

The general design approach is as follows:
1. Build a new `PySpark` app for each new gold view. This app addresses the requirements for the report by implementing the necessary data transformations and aggregations.
    * The implementation of the app follows the [Definition of Done](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG%20Data%20Ops%20Wiki/116/Definition-of-Done-for-Technical-Work) criteria. Which means that it will include unit tests, will follow a review process and be accompanied by documentation. The documentation can be included in or added to this runbook.
2. The App is triggered from the `PL_PPA_Silver2Gold` pipeline within `Curate PPA` folder of `adf-towworks`.

#Gold Tables

Item # | Name of Report | Name of Project in ADO | Name of Deployable PySpark Script | Location of resulting Delta table
--------|----|-----------|-------------|--------
1 |Market Share Report | `ppa-v2-msreport-sparkapp` | `build_ppav2_market_share_report.py` | processed/gold/PPA/REPORT_PPA_MARKET_SHARE

#Spark Apps

##Market Share Report

###Introduction
This view will provide a comprehensive and up-to-date overview of the market position and performance, including information on the competitors and customer/competitors' demographics. The requirement is to add two additional columns `AwardedJob` and `LocationJob` as stated in the story #2528

###Requirements

To have a new view in our data lake to monitor our market share for Ship Assist (PPA). This view should provide a comprehensive and up-to-date overview of our market position and performance, including information on our competitors and customer/competitors' demographics.

###Dependent Silver Tables

```
   Jobs
   Organizations
   Vessels
   Pilots
   Locations
   TugName
```

###Transformations
1. Filter `Job` table on `PREFERRED_COMPANIES = ['CATES','SEASPAN','SAAM TOWAGE','GROUP OCEAN']` with columns `AwardedFrom` and `AwardedTo`.
2. Next, perform sequence of left join operations using `Job` table as base with following tables `Vessels`,`Organizations`,`Pilots`,`Locations` and `TugName` where the columns 'AwardedFrom` and `AwardedTo` are captured from `TugName` table.
3. Store the above join in a dataframe `a1`.
4. Again perform a filter for `Job` table on `PREFERRED_COMPANIES = ['CATES','SEASPAN','SAAM TOWAGE','GROUP OCEAN']` with columns `AwardedFrom` and `AwardedTo`.
5. Next, perform sequence of left join operations using `Job` table as base with following tables `Vessels`,`Organizations`,`Pilots`,`Locations` where the columns 'AwardedFrom` and `AwardedTo` are captured from `Organizations` table.
6. Store the above join in a new dataframe `a2`.
7. Perform a union on both the dataframes `a1` and `a2` this would generate a new dataframe `b1`.
8. Create an array column using the contents of `AwardedFrom ` and `AwardedTo` generated from `b1` and then remove duplicates.
9. Explode this new set of array into rows and then the `AwardedJob` and `LocationJob` columns are added based on the requirement stated.

As per story #2738, the following columns of market share report `eta_ata, etd_atd, orderTime, dispatchTime, updatedAt, createdAt, PPA_Departure_Calendar` are in UTC timestamps. Updated view definition for the market share report by adding new columns to report as `eta_ata_PST, etd_atd_PST, orderTime_PST, dispatchTime_PST, updatedAt_PST, createdAt_PST, PPA_Departure_Calendar_PST` and renamed columns `PPA_lastmodifydate, Seaspan_Time` to `PPA_lastmodifydate_PST, Seaspan_Time_PST`.

Code sample for updating view is as follows:
![PPA v2 gold view.png](/.attachments/PPA%20v2%20gold%20view-9944e8bd-1909-48d8-b6d6-17ce0e2471a3.png)

###Project Repo

This PySpark app is hosted in Azure DevOps at [ppa-v2-msreport-sparkapp](https://dev.azure.com/seaspan-edw/SMG-DataOps/_git/ppa-v2-msreport-sparkapp)