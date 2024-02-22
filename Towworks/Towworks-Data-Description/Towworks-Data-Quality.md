|||
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|08-Dec-2022|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Ticket**| #1784

# Introduction
This document attempts to assess the quality of the Towworks data at source. Quality is a vague term that could refer to many things. Two such measures could be consistency of data (are all like fields the same type/format) or completeness of data (are fields missing).

To perform this analysis, previously available tools are used. Here the [pandas-profiling](https://pypi.org/project/pandas-profiling/) package was chosen.

# Scope
The analysis will instrument data taken directly off the [Towworks] API(https://seaspan.towworks.com/custom/seaspan/processes/TWDataBroker.aspx) and rather than perform an exhaustive analysis, just one or two selected datasets will be audited. Specifically:

    EVENTS
    WORKORDERS

The data was taken for the period 01 June to 30 November 2022

# Results

To view the files, download them, then right click the file. Which should give the option to open in a browser.

![data quality towworks.png](/.attachments/data%20quality%20towworks-a3da7acf-c75b-4f68-beae-eaa6d2e37071.png =300x)

## EVENTS
[towworks-events-2022-06-01T0000_to_2022-11-30T2359.html](/.attachments/towworks-events-2022-06-01T0000_to_2022-11-30T2359-c49459a4-5f72-41ff-b17e-6e790bff1629.html)


### Quick Summary
Field(s) | Problem Description
-----|------
`TowOrderNumber`, `TowOrderLineNumber` | All null
`FuelOnBoard`, `FuelUsed`, `FuelPurchased` | All null
`LubeOnBoard`, `LubeUsed`, `LubePurchased` | All null
`GearOil`, `SlopOil`, `OilyWater`| All null
`FleetSchedule` | 99.7% are null/missing
`ToLocationPortName` | 64% null/missing
`BillableHours`, `CostHours` | 0, 65% of the time
`QuotedRate` | 0, 99% of the time
`CargoEventQuantity` | Numeric field detected as a string

## WORKORDERS
[towworks-workorders-2022-06-01_to_2022-12-08.html](/.attachments/towworks-workorders-2022-06-01_to_2022-12-08-e74997ac-3e66-4817-a112-78d5d84aa7ba.html)

### Quick Summary
Field(s) | Problem Description
-----|------
`WORKWATERWAYGUID` | Always null
`WORKTOWATERWAYGUID` | Always null
`PURCHASEORDERGUID` | Always null
`PURCHASEORDERLINEGUID` | Always null
`LINKEDISSUEGUID` | Always null
`TERTIARYASSETGUID` | Always null
`RESPONSIBLEPERSONGUID` | Always null
`PURCHASEORDERLINE` | Always null
`SAFETYINSTRUCTIONS` | Always null
`LOCATIONINSTRUCTIONS` | Always null
`EQUIPMENTINSTRUCTIONS` | Always null
`ESTIMATEDCOST` | Always null
`ACTUALCOST` | Always null
`ESTIMATEDREVENUE` | Always null
`ACTUALREVENUE` | Always null
`REQUESTEDSTARTDATE` | Always null
`REQUESTEDCOMPLETIONDATE` | Always null
`LIMITGUID` | Always null
`PARENTWORKORDERGUID` | Always null
`CARGOINSTRUCTIONS` | Always null
`ACKNOWLEDGEDDATE` | Always null
`INNAGE` | Always null
`OUTAGE` | Always null
`ORDERTAKENDATE` | Always null
`REQUESTEDDATE` | Always null
`CONSIGNEDTOGUID` | Always null
`COMMODITYOWNERGUID` | Always null
`TERTIARYASSETNAME` | Always null
`CONSIGNEDTOGUID_NAME` | Always null
`COMMODITYOWNERGUID_NAME` | Always null


 