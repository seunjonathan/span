|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|14-December-2022|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|John Nunes|
|**Tickets**| #1482 <br> #1524 <br> #1596 <br> #1597 <br> #1630 <br> #1690

[[_TOC_]]

# Introduction
Seaspan Ferries would like to predict the volume of trailer traffic expected to arrive the next day at a given terminal. Seaspan would also like to predict the risk of a terminal running out of capacity due to containers awaiting to board and arrived containers awaiting for pick-up.

This page captures the results of some initial machine learning experiments performed to address the container traffic arrival problem. The experiments were conducted using the Databricks AutoML feature.

# Data
The training data for the models was compiled using a version of the query shown below, executed against the `gold` database in Synapse.

```
select route, date_signedin, count(BOL_Number) as num_BOLs
from (
	select
	Sailing_ID
	, DATEPART(WEEKDAY, Actual_Departure_Date_Time) as departure_day_num
	, DATEPART(MONTH, Actual_Departure_Date_Time) as departure_month_num
	, DATENAME(HOUR, Actual_Departure_Date_Time) as departure_hour
	, DATENAME(DAYOFYEAR, Actual_Departure_Date_Time) as departure_day_of_year
	, DATENAME(YEAR, Actual_Departure_Date_Time) as departure_year
	, DATEADD(hour, datediff(hour, 0, Date_Time_Added), 0) as date_time_added_hour
	, CAST(Date_Time_Added as DATE) as date_added
	, DATEADD(hour, datediff(hour, 0, Signature_Date_Time), 0) as date_time_signedin_hour
	, CAST(Signature_Date_Time as DATE) as date_signedin
	, Actual_Departure_Date_Time
	, Date_Time_Added
	, Origin_Port
	, Destination_Port
	, Length
	, Width
	, VIN
	, License_Plate
	, BOL_Number
	, Route
	from dbo.vwT_TRUNK trnk
	inner join dbo.vwT_ASSIGNMENT asgmt on trnk.fk_Assignment_in = asgmt.Sailing_ID
	inner join dbo.vwT_ROUTE rt on asgmt.fk_Route_in = rt.pk_Route_in
	inner join dbo.vwT_JOB job on trnk.fk_Job_in = job.pk_Job_in
	inner join dbo.vwT_OTG_POD otg on otg.fk_Trunk_in = trnk.pk_Trunk_in 
	) d
where route = 'Tilbury > Swartz Bay'
group by route, date_signedin
order by date_signedin desc
```

## Customer Traffic
An analysis of the customer traffic reveals that for the period starting 2020-01-01 to the present, that around half of the container traffic can be attributed to a small percentage of the customers.
![1.png](/.attachments/1-b26a716c-e42a-402c-aba1-f11c4616db23.png)

In fact the top 15 or so customers account for around half the total number of Bill of Ladings (BOLs) issued. See [Appendix/Total BOLs by Customer](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki?wikiVersion=GBwikiMaster&pagePath=/Tops/Prediction%20of%20Next%20Day%20Container%20Traffic&pageId=60&_a=edit#total-bols-by-customer).

# Machine Learning Experiments
## AutoML
The AutoML feature from Databricks was used to conduct some initial machine learning experiments. AutoML provides an easy way of building and training ML models without the need to write code. In fact, AutoML will generate Python notebooks which can then be updated or customised manually.

Once a satisfactory ML model has been learned, it can be saved (registered) for future use. For example to embed it into an ETL pipeline that generates prediction from incoming data. One such scenario would be to predict the number of trailers expected to arrive at a departure port the next day, given historical trailer traffic for the last `d` days, where `d` could be a large number.

## Experiments
### 1. Daily Sign-Ins Departing Tilbury to Swartz Bay
#### Sample Data
![1.5.png](/.attachments/1.5-aeefb1c7-b988-4360-a382-0607dbb8e4e9.png =500x)

#### Model Type
AutoML supports three different types of machine learning model. These are (1) Classification, (2) Regression and (3) Forecast. In a classification model the goal is to categorize or classify the input vector into one of a known number of classes. E.g. Dog or cat. As such, our prediction problem does not fit this type of problem. Both regression and forecast models are however able to generate a numeric output given some inputs. In the prediction problem, the numeric output could be the number of trailers signed-in, or the total amount of footage committed say.

This experiment was set up to build a forecast model. The data was filtered for all traffic departing Tilbury to Swartz Bay only. The diagram below shows the best model that AutoML arrived at. The bright curve shows the predictions, the dots are the actual numbers and the shading depicts the confidence in the prediction (low/high values).

![2.png](/.attachments/2-12f40f27-cfe2-4ae9-b514-ad879f9c850e.png)

This is an initial attempt and as such the means average percentage error in the model is high at around ~50%.

### 2. Daily Sign-Ins Given, Day of Month, Day of Week

#### Sample Data
![3.png](/.attachments/3-70cc09c3-8262-45d5-a192-4d908078259a.png =500x)

#### Model Type
Regression.

The motivation here was simply to see if a regression model, instead of a forecast model could perform better on a similar data set. How the training data is represented to a ML model can have a significant impact on the outcome. AutoML is known to automatically preprocess the training data and convert it to preferred formats. In this case, weekdays and months are converted to so called one-hot-encoded vectors.

The goal of the model is again to predict `num_BOLS` for the next day. Again the results require further interpretation though appear to suggest a mean average error of around 12-13 BOLs.

# Suggestions for Future Work
While some tweaking of the models will yield improved prediction accuracy, a more effective approach would be to use domain knowledge. Some suggestions follow.

## 1. Return vs Outbound Journey
If it can assumed that an outbound trailer will at some time return, then it might be possible to predict returning traffic with more accuracy. For example, when containers outbound from Tilbury depart for Swartz Bay, it's expected those containers would return (via Swartz Bay) within a short period. Gordon Food Services for example, have a depot in Delta BC. They also happen to one of SFC's biggest customer, having logged nearly 30k BOLs since the start of 2020. That's on average ~30 BOLs a day!

If we presume that all trips departing to Vancouver Island are outbound, then we would expect trailers to return as promptly as possible to make subsequent deliveries. By identifying returning vs outbound trailers, it might be possible to build a better ML model.

### 1. Update
Querying the data revealed some interesting facts:
* GFS journeys can be associated with over 70k different trailers.
* The same trailers are used by other companies.
* When filtering only for GFS journeys, it appears most trailers make a one-way trip.

From this, it's reasonable to conclude that GFS do not own 70k containers. That trailers taken to the island by one customer, are brought back by another customer. If so, the notion that a customer would want to return an empty container after making a delivery on the island no longer holds and this suggestion is likely not viable.

#### CORRECTION
The above statistics may not be correct. The query used to build that data set had the same Sailing_ID multiple times on both sides of a `join` statement. An analysis was conducted using an updated query, the results of which can be found in #1524

## 2. Predicting Customer Specific Traffic
The [Customer Traffic](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki?wikiVersion=GBwikiMaster&_a=edit&pagePath=/Tops/Prediction%20of%20Next%20Day%20Container%20Traffic&pageId=60#customer-traffic) graph above clearly shows that a share of the container traffic can be attributed to a small percentage of customers. In fact, the top 16 customers account for half of the traffic! The assumption being that these 16 are likely frequent and or regular users. A model built to predict traffic for these customers may again be more accurate that a general model.

### Scenario A
Build a training set to predict traffic from a top customer, say GFS.

sign-in-Date | Num GFS BOLs
------------ | --------

### Scenario B
If A proves successful, then build a training set to predict traffic for other top customers.

sign-in-Date | Num Customer_A BOLs | Num Customer_B BOLs | Num Customer_C BOLs | Num All_Other_Customer BOLs 
------------ | -------------|---------------------------|----------------------|-----------

This model would predict trailer traffic on a customer specific basis, for the top 16 customers say. It would also predict "other customer" traffic but with the expectation that this final prediction would be less accurate.

## 3. Analysing Container Movement
It may also prove useful to understand container traffic movement. Keeping track of how many containers are on the island or the mainland could be beneficial in improving predicting arrivals at a terminal. Or perhaps knowing typically how long a container remains on the island or the mainland is useful.

Suggested metrics of interest:
* Container pool size
  * Total number in-use/available
    * 219116
  * Total number available on the mainland at any one time
  * Total number available on the island at any one time
  * Total number available at a terminal (?) 
* Average elapsed time between next ferry crossing
  * All containers over all routes
  * All containers per route
  * All containers per industry (food/construction/courier/automotive/fuel/shipping)
      * If industry segment is not already in the data, it would have to be manually added.

#### Sample Container Crossing Data
Sample data below shows activity for container `Unit_Number=K200A/B`. Two anomalies are observed marked by `?` where it is known how the trailer made the same crossing twice without first returning. Otherwise, it seems possible to use this kind of data to compute the suggested elapsed time metrics.

```
Unit_Number	Route	                Signature_Date_Time

K200A/B    	Tilbury > Duke Point	2022-08-05 11:26:51.0000000
K200A/B    	Duke Point > Surrey	2022-08-04 13:01:46.0000000
K200A/B    	Tilbury > Swartz Bay	2022-08-03 14:51:01.0000000
K200A/B    	Duke Point > Tilbury	2022-08-02 09:56:34.0000000
K200A/B    	Surrey > Duke Point	2022-07-29 17:40:40.0000000
K200A/B    	Duke Point > Surrey	2022-07-28 14:43:56.0000000
K200A/B    	Tilbury > Duke Point	2022-07-27 11:54:04.0000000
K200A/B    	Tilbury > Duke Point	2022-07-25 10:46:00.0000000    ?
K200A/B    	Duke Point > Surrey	2022-07-22 14:33:23.0000000
K200A/B    	Tilbury > Duke Point	2022-07-21 15:17:09.0000000
K200A/B    	Duke Point > Tilbury	2022-07-18 08:35:36.0000000
K200A/B    	Tilbury > Duke Point	2022-07-15 11:15:17.0000000
K200A/B    	Duke Point > Tilbury	2022-07-14 11:32:07.0000000
K200A/B    	Surrey > Duke Point	2022-07-13 16:08:09.0000000
K200A/B    	Surrey > Duke Point	2022-07-11 16:33:05.0000000    ?
K200A/B    	Duke Point > Surrey	2022-07-08 13:00:00.0000000
K200A/B    	Tilbury > Duke Point	2022-07-07 17:09:08.0000000
K200A/B    	Duke Point > Surrey	2022-07-06 10:10:00.0000000
K200A/B    	Tilbury > Duke Point	2022-07-05 11:01:37.0000000
K200A/B    	Duke Point > Tilbury	2022-07-04 11:28:00.0000000
K200A/B    	Surrey > Duke Point	2022-06-29 14:25:05.0000000
K200A/B    	Duke Point > Surrey	2022-06-27 12:05:33.0000000
```


# Statistical Model
Understanding that many customers will be regular daily and/or weekly users of the Seaspan Ferry service, provides motivation to build a statistical model. The following were goals of & requirements for this model:
1. Split the week up into 24 x 7 = 168 hourly slots with hour 0 representing midnight Sunday (the start of the week) and hour 167 as 11pm on Saturday (the end of the week).
2. For each time slot, aggregate the number of trailers that signed-in at that time at a given terminal
3. From the aggregation, compute both the mean and the standard deviation
4. Statutory holidays should not be included in the aggregation.
5. Have the ability to aggregate data from a window of data going back to a specified date. E.g. the last 6 months.
6. Have the ability to create customer specific models. I.e. aggregate data from a specific customer.
7. Limit aggregations to sign-in times a specified window before the scheduled departure time

## Results
### General Model
Data window: `2020-01-01 to 2022-09-27`
Customer: `All`
Departure terminal: `Tilbury`
Signed-in to scheduled departure: `<= 8 hours`

![4.png](/.attachments/4-e9053f86-ca7a-4c1a-8031-71e3cd113cdf.png)

### Last 6 Months Model
Data window: `2020-03-01 to 2022-09-01`
Customer: `All`
Departure terminal: `Tilbury`
Signed-in to scheduled departure: `<= 8 hours`

![5.png](/.attachments/5-37eeacd3-0114-409c-8103-79c21e0c4666.png)

### Last 3 Months Model
Data window: `2020-06-01 to 2022-09-01`
Customer: `All`
Departure terminal: `Tilbury`
Signed-in to scheduled departure: `<= 8 hours`

![6.png](/.attachments/6-4191761d-e97a-4774-8313-da39a5dd54d7.png)



#### Compare Last 3 Month Model with Actuals week of Sep 18th
This visualization shows a comparison of the daily predictions from the "3 month" model (light blue) with actual traffic for the week starting Sun 18th Sept. 

![7.png](/.attachments/7-cafe5dea-dea5-41ff-8608-1e21f98c6916.png)

#### Compare Last 1 Month Model with Actuals week of Sep 18th
This visualization shows a comparison of the daily predictions from the "1 month" model (light blue) with actual traffic for the week starting Sun 18th Sept. There appears to be some small differences in the model. Albeit insignificant (neither much worse or much better).

![8.png](/.attachments/8-d4aa0a05-0795-4ece-9b91-4e4826d2f500.png)

# Statistical Model - Job-Added-DateTime
The previous analysis collects statistics using the sign-in time. Another variable to consider is the job-added time.

### General Model
Data window: `2020-01-01 to 2022-10-03`
Customer: `All`
Departure terminal: `Tilbury`

![9.png](/.attachments/9-63508884-5b27-4d3e-8f43-048d5465ecb9.png)

# Trailer Specific Analysis
## By Unit_Number and Company
This analysis focuses on specific trailers. We start with identifying the most travelled trailers. To do this we count the number of times a unit_number-customer_name combination appears in the data, ordered by frequency.

![10.png](/.attachments/10-7a277d48-2e83-4562-b449-3967fa7e42fe.png)

## Hours Between Signin for Trailers Departing Vancouver Island
The plot shows that the return times for just two trailers belonging to Day and Ross Dedicated Logistics are in a very narrow range indeed. We see over 300 trips in which these trailers are signing in (at Duke Point, destined for Tilbury) around 13 hours after signing in at a previous terminal (possibly Tilbury). This is consistent with what we have already observed, for example with GFS, for which trailers return from the island fairly rapidly.


![11.png](/.attachments/11-7907eb7e-28f0-4b24-a283-bb56f59dc799.png) 

Something similar is observed for Dacon Holdings and their trailer numbered 003215. Around 300 trips are signing in, mostly at Duke Point destined for Tilbury within 11 hours after signing in at, again, either Tilbury or Surrey. These too should be then easy to predict.

![12.png](/.attachments/12-7ecd750b-10c4-40b5-8272-905b96b92387.png)

And this for Martin Brower of Canada Company
![13.png](/.attachments/13-ae2186eb-27c8-4fe2-8060-a6aeaf300221.png)

Kingsley Trucking however is slightly harder to predict. Their return trips are more spread out.

![14.png](/.attachments/14-8a946d01-438e-4778-a215-e46bdb5fdfd1.png)

This is however a common pattern. Something similar observed for ACE Courier Services.

![15.png](/.attachments/15-89bb0f7a-4920-47d5-a8b4-7742cfe57493.png)

## By Trailer Type
The analysis is again for island departures only with the x-axis showing the number of hours between sign in at Tilbury or Surry and the return at Duke Point or Swartz Bay.

![16.png](/.attachments/16-3189f2bb-1a7b-4152-b916-e9618792b0dc.png)

Unit Types `Van` & `B-Train` make up the majority of trailer types with the remaining types being a small fraction. The returns are spread quite broadly perhaps with the exception of `Full Size Pickup` which looks like this:

![17.png](/.attachments/17-ba6fa2ca-26d4-4dc6-846f-d59a993face6.png)

But again is a small fraction of the trips so may not be statistically relevant.

The data distribution for Unit-Type `B-Train` looks like the following:

![18.png](/.attachments/18-7c1ccede-9c0c-403d-afba-06156bbeb9e9.png)

## TODO: Hours Between Signin & Previous Actual Departure
So far, to predict when a trailer arrives/signs-in at an island terminal, the approach has been to plot frequency histogram of the `hours-between-signin`. This measure includes variability both at the previous terminal and the current. The metric, `hours-between-previous-actual-departure-and-signin` may be better as it isolates customer variance to a single terminal.

# Cumulative Probability

For any given customer we can build a cumulative frequency chart that gives the probability of a trailer returning (signing in) at an island terminal a given number of hours after actual departure time. The graph below shows two such plots. One for Loblaws and the other for Harbour Link.

The graph shows that within at 24hrs 81% of all trailers belonging to GFS have signed in. Compare that to Coastal Pacific Xpress, where we have to wait over 100hrs before a prediction can be made with a similar level of confidence.

![19.png](/.attachments/19-a1010cb5-08b0-4615-90e4-95d82df25841.png)

Plots for the top 20 most travelled customers would be as follows:

![20.png](/.attachments/20-9fdb6227-75b5-4b07-ad95-3f6308a5820c.png)

Of interest would be those customers whose trailers return within say 24 hours. In that case, just thirteen customers were observed with a probability of 80% that the trailer would return within the first 24hrs after actual departure time.
![21.png](/.attachments/21-faa6bf58-c2b1-4074-81da-0849654bef5f.png)
Of these, 4 are in the top 50 highest Seaspan users:

![22.png](/.attachments/22-98c53699-6078-4e01-bebd-bf9a2f29dfd0.png)

The next question would be, is the ability to predict returns for these users useful? Or is the number of trailers too small a fraction of ferry traffic to make a difference?

# Appendix

## Total BOLs by Customer

<details><summary>Open to view Total BOLs by Customer Table</summary>

Customer_Name|num_Customer_BOLs|Cumulative Total BOLs
-------------|-----------------|---------------------
Comox Pacific Express Ltd- SFC|40711|619794
Van Kam Freightways Limited|32934|579083
Coastal Pacific Xpress Inc|31777|546149
Gordon Food Service Canada - Delta|29390|514372
Kingsley  Trucking|26283|484982
Hansens L Forwarding|22949|458699
Ray Peters Trucking|18895|435750
Coastal Pacific Xpress Inc- Catalyst|17801|416855
Transource Freightways Ltd|17066|399054
Central Island Distributors|15561|381988
Jerrys Transport Ltd|11902|366427
Coastal Pacific Xpress Inc - Aquatrans|11208|354525
Diamond Delivery|11182|343317
Coastal Pacific Xpress - Bison|10497|332135
Canadian National Railway|9832|321638
Trans X Limited|9389|311806
Marpole Transport Limited|7986|302417
ACE Courier Services - Vancouver|7611|294431
Western Pacific Transport Ltd|7353|286820
Loblaws Inc 1957|7236|279467
Loblaws (RTN) 1957|7231|272231
Marpole Bulk|6573|265000
Penta Transport Limited|6305|258427
Triple Eight Transport Inc|6268|252122
Van Kam (Liquor Dist. Branch) Limited|6161|245854
Loomis Express  of Transport TFI 22 L.P.|6032|239693
Clark Freightways Limited|5936|233661
Van Kam (Campbell River) Freightways Lim|5665|227725
Pepsi Bottling Group|5472|222060
Fedex Ground - Vancouver|5325|216588
Argus Carriers Limited|5257|211263
Loblaws Inc 1935|5242|206006
Loblaws (RTN) 1935|5234|200764
Island Farms Dairies Co Op|5116|195530
CCash Contract|5071|190414
Coldstar Solutions Inc|5027|185343
Seaspan Ferries (SFC Logistics)|4792|180316
Sysco Food Services of Vancouver|4476|175524
Hostess Frito Lay Company|4361|171048
Corporate Couriers Logistics|4255|166687
Island Pacific Transport|4211|162432
Martin Brower of Canada Company|4209|158221
The TDL Group Corp|3967|154012
Purolator Inc. A/R|3867|150045
West Coast Reduction - Head Office|3832|146178
United Parcel Service SCIC|3722|142346
Van Kam (CPI Traffic) Freightways Ltd|3595|138624
Harbour Link (1) Container Services Inc|3594|135029
Canada Cartage System LP|3583|131435
Van Kam (Brewers Dist.) Ltd.|3578|127852
Northwest Tank Lines (Western) Incorpora|3311|124274
Harbour Link - PSG|3282|120963
Harbour Link Container Services Inc.|2986|117681
Harbour Link - Alpine|2959|114695
Kingsley (FISH) Trucking|2950|111736
Corporate Courier - Amazon Prime|2933|108786
Starline Windows Limited|2918|105853
Tricor Transporation Incorporated|2758|102935
London Drugs Limited|2709|100177
Central Isl Dis (Vitran)|2609|97468
Central Isl Dis (Coremark)|2531|94859
Coastal Pacific Xpress - AT - VanWhole|2507|92328
DanFoss Delta|2492|89821
Bridgeway Transport Limited|2168|87329
Protrux Systems Inc|2114|85161
Lenox Logistics|2074|83047
Johnson  Ken Trucking Ltd.|1995|80973
Marpole - MTLCT|1881|78978
Pacific Coast Warehousing Limited|1861|77097
Wallace and Carey Inc.|1851|75236
Kal Tire Transport Ltd|1806|73385
Devon Transport Limited DBA Budget Rent|1705|71579
Kingsley ANW Trucking|1680|69874
Marpole - MTLS1|1650|68194
Island Pacific-Cascadia Forest Products|1637|66544
Sokil (LDL) Express Lines Limited|1499|64907
Dacon Holdings|1469|63408
Comox Pacific Express - CATALYST|1451|61939
TransCold Distribution Ltd|1451|60488
Chohan Carriers Ltd|1443|59037
Island Eggs  a div of Burnbrae Farms Ltd|1442|57594
Aerostream Cargo Services Limited - CAD|1420|56152
Linde (Tanks) Cda Edmonton|1390|54732
Day and Ross Dedicated Logistics|1281|53342
Bunzl Distribution Inc. A/R & A/P|1255|52061
TForce Integrated Solutions|1244|50806
Western Logistics Incorporated|1190|49562
Imperial Dade Canada Inc|1187|48372
Penta Transport - LMS|1173|47185
Day and Ross Inc-A/R Victoria|1168|46012
Accord Transportation Limited|1126|44844
Direct Limited Partnership (Canada Cart)|1114|43718
Waste Management of Canada Corp.|1107|42604
Island Tire Recycling|1105|41497
DanFoss Victoria|995|40392
Linde (Vans) Cda Delta|988|39397
Home Hardware-A/R only|962|38409
Halt Holdings Ltd-Nanaimo|944|37447
Tenold Transportation Incorporated|942|36503
Adesa Auctions Canada Corporation|911|35561
Avis Rent A Car-Richmond|798|34650
Tymac Launch Service Limited|791|33852
Livingston International Inc.|787|33061
Kingsley Trucking  - International|752|32274
Galaxy Motors|748|31522
Trimac Transportation Services Inc|745|30774
DanFoss Nanaimo|727|30029
Stericycle Incorporated|689|29302
ABC Recycling Limited|658|28613
ABD Solutions Ltd|652|27955
Loblaws 34|571|27303
Loblaw RTN 34|563|26732
Orica Canada Incorporated|558|26169
Loblaws Inc.|553|25611
Coastal Trucking|550|25058
J & R Hall Transport Inc|534|24508
Trail Appliances Ltd|500|23974
Enex Fuels Ltd.|446|23474
Actton Transport Limited|427|23028
Loblaws Inc DC22|411|22601
Sundowner Transport Systems|411|22190
Parkland Corporation - SFC ONLY|409|21779
Loblaws (RTN) DC22|407|21370
Enterprise Rent A Car Canada Limited|388|20963
Austin Powder Limited|379|20575
Westcan Bulk Transport Ltd|373|20196
Marshall (CR) Steve Motors 1996 Limited|366|19823
Paradise Island Foods Incorporated|366|19457
GFL Environmental - PORT ALBERNI|360|19091
GFL Environmental - Vantage Way DELTA|349|18731
Pride Truck Delivery Limited|310|18382
MFP Mohawk Fuel Products Ltd.|301|18072
Applewood Motors Inc.|300|17771
Loblaws Inc 1932|298|17471
Vancouver Island Propane Services|296|17173
Loblaws (RTN) 1932|295|16877
Mack Sales and Service of Nanaimo Limite|291|16582
Clean Harbors Canada Inc-AR ONLY|291|16291
Fortis BC Energy Inc - SFC|288|16000
Viper Fuels|285|15712
Landtran Logistics Inc.|276|15427
Global Auto Marine Exchange Ltd.|271|15151
Ewwf System Ltd.|269|14880
Sokil Express Lines Limited|269|14611
Road Runner Trailer Manufacturing|261|14342
Mid Island Towing and Transport Limited|259|14081
Westeck Windows Mfg Inc|253|13822
P and R Truck Centre|249|13569
Tak Logistics Inc|244|13320
Bouman Auto Gallery|226|13076
Port Boat House|224|12850
Gordon Homes Sales Ltd|216|12626
Bayridge Transportation|215|12410
U Haul Company|209|12195
Berry and Smith Trucking Limited|196|11986
Docktor Freight Solutions Corp|187|11790
Peden Recreation Vehicle Ltd|178|11603
Scamp Transport|173|11425
Western Force Transport|171|11252
Venco Products Limited|164|11081
Deepwater Recovery Ltd.|164|10917
Mundies Towing and Recovery|163|10753
VI Carriers Ltd|163|10590
Messer Canada Inc.|162|10427
Linnet Lane Stables|162|10265
Budget Rent A Car-Victoria Harriet|159|10103
Dolphin Delivery Limited|157|9944
Jim Hester Wholesale Division Ltd.|149|9787
E Roko Distributors|142|9638
DACT Ventures Ltd.|141|9496
Shepherd  T Trucking Limited|139|9355
Need a Lift Truck Service Ltd.|139|9216
Marios Towing Ltd.|138|9077
VK Delivery and Moving Services Ltd|138|8939
T Lane Transportation|136|8801
Air Liquide (Tanks) Vancouver|135|8665
Allteck Limited Partnership - PO|134|8530
Penguin Motors Limited|133|8396
Nanaimo Mitsubishi|129|8263
Diacon Technologies Limited|127|8134
Merco Enterprises (All Island Bailiffs)|122|8007
Dumas Trucking Limited|122|7885
Island Autopros Clearance Center Inc.|121|7763
Petrovalue Products Canada Inc.|121|7642
Canadian Utility Construction|121|7521
Canuck Towing|120|7400
Sherwood Marine Centre Limited|114|7280
Kia West|113|7166
Coastal Mountain Fuels - Langley|111|7053
Bamss Contracting Inc|109|6942
F and M Installations Limited|108|6833
Nickel Bros Industrial|107|6725
Van Isle Ford Sales Ltd.|106|6618
HTEC Hydrogen Technology and Energy Corp|106|6512
National Fast Freight|106|6406
Island GM|105|6300
Northside Transport Ltd.|105|6195
Az-Tec Freight (2018) Inc.|101|6090
Eagle Builders LP|97|5989
M and P Mercury Sales Ltd.|97|5892
Allens Transport Ltd|91|5795
Tri State Motor Transit Co|89|5704
Heavy Metal Marine Limited|88|5615
DK Motors|85|5527
Prudential Transportation Ltd|84|5442
Bailey Western Star Truck|84|5358
Express Custom Trailer Manufacturing Inc|82|5274
Wheeler Trucking Inc|81|5192
Peterbilt Pacific Inc|80|5111
Value Village|80|5031
Discovery Motors Ltd|78|4951
Maverick Trailer and Marine Ltd|78|4873
GFL Environmental - NANAIMO|73|4795
Bowmark Concrete Ltd|71|4722
Alberni Chrysler Limited|70|4651
Sumas Environmental Services Limited|69|4581
Kimberly Transport|68|4512
One Road Logistics Inc|68|4444
Parksville Boat House Limited|68|4376
Falcon Equipment Limited|68|4308
Island HIno Truck Sales Inc.|64|4240
FirstOnSite Restoration Ltd.|62|4176
Commercial Truck Shuttle Ltd|61|4114
Bekins Moving and Storage|61|4053
Liquid Transport LLC|60|3992
Peninsula Towing Limited|60|3932
Rollins Machinery Limited|60|3872
Harris Oceanside Chevrolet Ltd|59|3812
TIP Fleet Services Canada Ltd.|59|3753
Alberni Power and Marine|57|3694
Penske Truck Leasing|55|3637
Highliner Trailer Ltd|55|3582
Bayview Auto Towing 2000 Ltd|55|3527
Cross Border Vehicle Sales Ltd.|54|3472
Dept Nat Def Esquimalt|54|3418
Elite Bailiff Services Limited|53|3364
Quality Transport Inc|53|3311
Woodgrove Chrysler|52|3258
Pacific Coast Express Limited|49|3206
TriLine Carriers LP|49|3157
PRO N2 Ltd.|48|3108
Campbell River Toyota|47|3060
Alchemist Specialty Carriers Inc|47|3013
The Driving Force Inc.|46|2966
Berks Intertruck Limited|46|2920
Sunwest RV Centre Limited|45|2874
Inland Kenworth Sales Limited|45|2829
Coastline Towing|45|2784
Pacific Chevrolet Buick GMC Ltd.|44|2739
Vimar Equipment Limited|43|2695
Danor Transport Ltd|41|2652
Verrault Lowbed Service|41|2611
Western Forest Products - SFC ONLY|40|2570
Mainroad Mid-Island Contracting LP|40|2530
Ellice Recycle Ltd|39|2490
Dept Nat Def Comox|39|2451
Tyee Chevrolet Buick GMC Ltd.|39|2412
Canadian Air Crane Limited|38|2373
Ranger Transport Limited|38|2335
Aheer Transporation Limited|38|2297
WMG Employee Account (SCIC use only)|37|2259
Ryler Holdings Limited|37|2222
Howich  Bill Chrysler Limited|37|2185
Inter-Rail Transport Ltd.|37|2148
Harbour International Trucks|36|2111
Bouman Motors|36|2075
Emcon Services Incorporated|35|2039
Northland Logistics Corporation|35|2004
World Fuel Services Canada ULC|32|1969
Shannon Motors Ltd|32|1937
Westview Ford Sales Ltd.|32|1905
Okanagan Aggregates Ltd.|32|1873
Ocean Trailer|31|1841
HB Towing|31|1810
Island Barrels and Totes|30|1779
Harbourview Autohaus Limited|30|1749
Parksville Chrysler Limited|29|1719
Island Asphalt Limited|29|1690
Kitt Equipment|29|1661
Shadow Lines Limited|28|1632
Coastal Installations Ltd|28|1604
Insituform Technologies Limited|28|1576
United Initiators Canda Ltd.|27|1548
Sterling Crane|27|1521
Trimac (NH) Transportation|27|1494
DCT Chambers Trucking Limited|27|1467
Triton Transport Limited|27|1440
Alberni Toyota|27|1413
Lens Transportation Group Limited|26|1386
DL Bins Ltd|26|1360
Bluenose Motor Company Limited|25|1334
Commercial Truck Equipment Corp|24|1309
TBM Logistics|24|1285
Roadway Towing Limited|23|1261
0777625 BC Ltd.|23|1238
Pacific Nations Auto Sales and Finance|23|1215
Jones  Bruce|22|1192
Pacific Coast Distribution|22|1170
Red D Arc Limited-SCIC A/R only|22|1148
Western Canada Remarketing Inc|21|1126
PNE Propane|21|1105
Z and R Trucking and Construction|21|1084
Waynes Trucking Limited|20|1063
Inlet Marine Repairs|20|1043
Davey Tree Expert Co. of Canada Limited|20|1023
Parker Marine Limited|19|1003
Tri-R Transport Limited|19|984
Copcan Civil LP.|19|965
Motorize Auto Direct Inc.|19|946
Arrowsmith Road Maintenance Ltd|19|927
Superior Propane Inc-Nan SCIC|19|908
Peters Bros Construction Ltd.|18|889
Jacob Bros Construction Ltd.|18|871
Accurate Effective Bailiff Services Limi|18|853
Nanaimo Toyota|17|835
Menzies Transport|17|818
DNR Towing|17|801
Key West Ford Sales Ltd.|16|784
Totem Towing Limited|15|768
Nexeo Solutions Canada Corp.|15|753
Charitable Moves|15|738
Trans Global Logistics (2015) Inc|15|723
Midgley Motors Ltd.|15|708
C and F Service Limited|14|693
Bekins World Wide Moving|14|679
Leader Mercantile Ltd|14|665
SG Power Products Limited|14|651
Surespan Construction Limited|13|637
Schnitzer Steel Canada Ltd. (was BC Inc)|13|624
FKD Contracting (Alta) Ltd|13|611
Bandstra Transportation Systems|12|598
Wheaton Nanaimo|11|586
Central Island Towing Limited|11|575
Harms Pacific Transport Incorporated|11|564
Brick Warehouse LP-Bby A/R|11|553
Campbell River Honda|11|542
Harding Forklift Services Ltd|11|531
Sunwest Auto Centre|10|520
Roc Star Enterprises Ltd.|10|510
McRaes Environmental Services Limited|10|500
Classic Car Corner Ltd.(Garry Wood)|10|490
Silver Streak Boats Ltd.|10|480
Black Creek Motors Ltd|10|470
Courtenay Kia|10|460
Ridge Low-Bed Service|10|450
Lone Horse Trucking|10|440
Pauls Hauling Limited|9|430
Hino Motors Canada Ltd.|9|421
Allen Marine|9|412
Shoreline Tank Service Ltd|9|403
Westcan Rail Ltd.|8|394
Scottish Line Painting Limited|8|386
Windley Contracting|8|378
McLeods Blasting Supplies|8|370
Corporate Couriers - LTL.|8|362
Marshall  Steve Ford Lincoln|8|354
Asplundh Canada ULC|8|346
Surespan Structures Ltd.|8|338
Westgen|8|330
Sunbelt Rentals of Canada Inc|7|322
Penguin Meat Supply Limited|7|315
Ocean Construction Supplies Limited|7|308
A and K Timber|7|301
WRC (W. Robins Consulting Ltd)|6|294
Fisher Inc.|6|288
Inland CR Kenworth Limited-CRiver|6|282
Kitt Distribution Ltd.|6|276
Western Canada Marine Response Corp|6|270
South Fraser SR Container Services|5|264
GFL Environmental - NORTH VAN|5|259
Gravel Taxi Ltd|5|254
Somerset Vehicle Sales|5|249
GTS Gateway Transport Solutions Inc.|5|244
Iconic Island Dwellings Inc.|5|239
Vanderveen Hay Sales Ltd.|5|234
ABC Auto Brokers|5|229
Robinson Rentals and Sales|5|224
California Tank Lines|5|219
Envirosystems Inc|4|214
Nanoose Bay Towing|4|210
Altec Industries Limited|4|206
Raylec Power LP|4|202
Jadeline Holdings Ltd|4|198
Big Boys Toys (Nanaimo) Limited|4|194
Chevrolake Motorcars 2002 Inc.|4|190
Marlon Recreational Products Ltd|4|186
Brenntag Canada Inc.-PO Langley for99320|4|182
Family Ford Ltd.|4|178
AMH Management Limited|4|174
Dyno Nobel Transportation Inc|4|170
Rangeland Truck and Crane Ltd|4|166
Scansa Construction Ltd.|4|162
Bronco Transportation Systems Inc.|4|158
AllRoad Towing Ltd.|4|154
Tims Automotive Repair and Mobile Ltd.|4|150
Bunzl Cleaning PO (was Acme Supplies)|4|146
AMJ Campbell International|4|142
Cargo Sprout Inc.|4|138
Knight-Way Mobile Home Haulers Inc.|4|134
Knightway Mobile Haulers Ltd|4|130
Discovery Diesel Electric 2006 Ltd.|4|126
Kindersley Transport Limited|3|122
Milner Group  The|3|119
Nexcar Sales Ltd|3|116
Mertin Pontiac Buick GMC Limited|3|113
Jeglerham Enterprises Ltd|3|110
North Island Nissan|3|107
Blue Star Motors|3|104
Smithrite Delivery Services Ltd|3|101
Auto King Motors|3|98
Larrys Heavy Hauling (1990) Ltd.|3|95
Thomcat Equipment Ltd|3|92
Coastline Mazda|3|89
Island Equipment Rental (Highway Four)|2|86
RL and J Ventures Inc|2|84
R. R. Plett Trucking Ltd|2|82
Jetes Lumber Co. Ltd.|2|80
Fisher Bay Seafood Limited|2|78
Clearway Rentals Incorporated|2|76
SCK Motor Company Limited|2|74
Nissan of Duncan (2130729 AB Ltd.)|2|72
Aardvark Pavement Marking Services|2|70
NUCOR Environmental Solutions Ltd|2|68
Intercontinental Truck Body (BC) Inc|2|66
Brymark Installations Group Inc|2|64
Bowerman Excavating|2|62
Dyno Nobel Canada Inc|2|60
Mak Transportation Services Inc|2|58
RAI Express Lines Ltd|2|56
Harbour City Equipment|2|54
Thrifty Foods - Saanichton|2|52
Q-Line Trucking|2|50
B. Mobyl Feed Ltd.|2|48
Pactow Transport Limited|2|46
Northstar Propane Ltd|2|44
Pacific Dairy Centre Ltd.|2|42
Universal Freight|2|40
Campbell River Hyundai|2|38
McLean  Brian Chevrolet Buick GMC Ltd.|2|36
Williams Machinery Limited|2|34
Drive Finance Company (Canada) Limited|2|32
Restwell Mattress Company Limited|2|30
Harris Kia|2|28
Dicks Lumber-Burnaby Store|2|26
Alberni Towing|2|24
Department of National Defence -Montreal|1|22
Nanaimo Chrysler Limited|1|21
Emil Anderson Equipment Inc.|1|20
Western Sleep Products Ltd|1|19
Wolfco Bailiffs|1|18
Millennium Auto Repair Centre|1|17
Versalift Canada Industries ULC|1|16
Island Honda|1|15
Harbour Link - CPL|1|14
Cardinal Boat Movers Inc|1|13
IWC Excavation Ltd.|1|12
Jim and Joes Trucking|1|11
Southern Railway (Vancouver Island)|1|10
Town of Qualicum Beach|1|9
Westshore Towing Ltd|1|8
Pacific Industrial Movers LP|1|7
RKM Crane Services (was Crane Force)|1|6
Fireworks Spectaculars Canada|1|5
Stint Construction Ltd|1|4
Westerra Equipment LP (was Surfwood)|1|3
Mainroad Maintenance Products Ltd Part|1|2
PM Industries Ltd|1|1

</details>