This is to list all the transformations in Power BI Telemetry dashboard.
#1032

[[_TOC_]]


1.	**Merge TowWorks Data with Telemetry** - The key to join is vessel and timestamp. For one eventguid there will be multiple telemetry points. All the points (lat/long) are needed to display the location of the vessel at each timestamp. I picked a 5 minutes interval. The data is merged after step 1 under Telemetry Data and Step 4 under TowWorks Events.

2.	**Task and Task Details** - This is based on eventguid and link number. One event could be a single towing, double towing or tandem towing event. In single towing there will be no link number for an event guid. For tandem or triple towing there are multiple link numbers. This is done in step 7 in TowWorks Events.
Below is an example:

**_Task_**

![1.png](/.attachments/1-f9f014aa-c902-4ad5-abeb-b7e565f1edfb.png)





**_Task Detail_** 

![2.png](/.attachments/2-e92a74b2-5e9d-4373-b0dc-f90e41da2a99.png)


_**Note:**_ I do not see the objects in red being used in the report.

**_Calculations -_**

a.	Duration - Use start and end time for an event
b.	Distance - Use lat/long from Telemetry data
c.	Fuel Used - max(ttf_255) - min(ttf_255)


**3. Route Transformation** - Combination of origin and destination of an event in TowWorks defines a route. 
            This transformation is to put route as the selection criteria for events.

**4. Zones based on RPM** 

## **Describing above steps**


## **1. Telemetry Data**


1.1) The data will look like this. UTC timestamp is converted to Pacific which is then rounded to nearest 5th minute.
![3.png](/.attachments/3-227ecfb7-55dc-47ab-ad1b-b25cee4abf70.png)

## **2. TowWorks Events**   

2.1) Pull columns from TowWork Events

2.2) Apply filter on ByAssetName. Assets listed in step#3.

2.3) Add a new column to change the 'ByAssetName'. This is done to keep the TowWorks asset name in sync with Telemetry.


**_Example:_**

![4.png](/.attachments/4-d4739794-0d46-414a-9b5a-e77a9bb3d2f6.png)


2.4) Round off the 'Start Time' to 5th minute and all the 5 minute intervals between 'start time' and 'end time'.
In this example:
Start time is 4/30/2021 12:44 
End time is 4/30/2021 20:00


Extract all the timestamps between 4/30/2021 12:40 and 4/30/2021 20:00 . This will turn one row into 87 rows.


2.5) Merge the data with WorkOrdersLink_Vw on workorderguid. Pull 'Link Number' from 'WorkOrdersLink_Vw'.

2.6) Merge with EventsSummary on EventGUID to get the 'TotalMetersTravelled'.      # Obsolete


2.7) There was the requirement to view the data in two groups based on events and linknumber.  Join the data with 'TowWorksEventsHeader' and bring in all the fields. 'TowWorksEventsHeader' is a view on on-prem db. 


2.8) Merge with Work_Order_VW to pull loadstatus, estimated start time and estimated end time.


2.9) Merge with LinkedEventSummary to pull 'TotalMetresTravelled', 'FuelUsed'.


[Route.xlsx](/.attachments/Route-3fe02837-c7f3-4eb6-b61b-17cd1db6c929.xlsx)

3.1) Create Route Key in TowWorks Events table:
KeyRoute = concatenate( CONCATENATE('TowWorks Events'[Location From],"  -  "),'TowWorks Events'[Location To])

3.2) Set up 'From Route' and 'To Route' static tables. Refer to attached spreadsheet for data.


3.3) Set up 'Route' static table, apply the transformation.


3.4) Set up 'Route Cross Join' table. This is to get all the possible combinations for 'from route' and 'to route'.


3.5) Relationship between tables:

![5.png](/.attachments/5-71bfe6c7-7f91-4a57-a2ba-23522eed96fd.png)
## **4. RPM Zone**

[Vessel Dimension.xlsx](/.attachments/Vessel%20Dimension-26b7fbac-c40e-427b-9fa8-9a07dff7b65c.xlsx)

4.1)  Calculate combined RPM 
  Formula: (Starboard RPM + Port RPM) /2

4.2) Find RPM Zone based on Combined RPM. Defined as below: 
      White - if combined RPM is 0
      Yellow - if combined RPM  is less than LowRpm for a vessel
      Green -  if combined RPM  is less than HighRPM for a vessel
      Red - if combined RPM is higher than HighRPM.


4.3) Count the number of rows from Telemetry for each RPM Zone.

