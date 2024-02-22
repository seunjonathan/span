# Introduction
Predictive analytics is just one step of the overall analysis process. Industry best practices suggest the following {_Ref_: [Data Science Association: Descriptive Predictive Prescriptive Analytics](https://www.datascienceassn.org/content/descriptive-predictive-prescriptive-analytics)}

1. Descriptive Analytics
2. Diagnostic Analytics
3. Predictive Analytics
4. Prescriptive Analytics

![1.png](/.attachments/1-927f7440-1fff-4110-8f44-baf482d6074a.png =450x) 

This wiki page captures some observations made during the descriptive analytics stage. The observations are made against a TOPS data set which contains records dating back to 2020-01-01

## Analysis of Hours Between Subsequent Sign-ins
Transportation of containers always alternates between trips to Vancouver Island and the mainland. Measuring the time between two subsequent sign-in times can tell us how long after arriving on the island, a container is returned. Or how long after being returned to the mainland the container takes it's next trip to the island.

The following example is a frequency histogram for `customer_number` = `106024`. (Gordon Food Services, GFS). The vertical axis represents the `number-of-containers` and the horizontal is the `number-of-hours-between-subsequent-sign-ins`. The different colours represent different routes.

![2.png](/.attachments/2-00384ad7-3fb2-4d8e-92ae-4b2ad5303348.png)

So for example, just under 100 containers make trips 34 hours apart.

### Trips to the Island
If we look just at trips originating at the mainland:

![3.png](/.attachments/3-bb200d88-e104-4b9a-ad62-d81ba5da8a9f.png)

We see that from the time the container is available again on the mainland, it's next trip to the island can happen almost anytime later. Compare that against the trips the other way:

### Trips to the mainland
![4.png](/.attachments/4-2b2df697-80ef-4333-9b89-a524f02e1f8e.png)
Here we see that most trips originating from Swartz Bay or Duke Pt. are made within about 24 hrs after sign-in at a terminal on the mainland.

If instead of counting containers by route, we count which are full or empty, we observe something that tells us a story. Here is a count of both empty and full containers.

![5.png](/.attachments/5-a2327f4a-7668-4005-a0d0-8cd65bd1acc3.png)

### Just Empty container trips:
![6.png](/.attachments/6-571af76a-d62f-437c-8ee5-7db837bbce6d.png)

We see that the pattern of empty trips are consistent with the return trips from the island.

This story is likely well known. GFS are a food distribution company based in the mainland. They make trips to the island to deliver food products, returning rapidly, possibly on the next ferry, with empty containers.

## Analysis of Deckspace Utilization
The most efficient trips are those in which the ferry is fully laden. The metric `percentage used deckspace` can help track efficiency. In this next graph, the horizontal axis is `percentage used deckspace` and the vertical axis is the `number of sailings`. The colours in this case represent different ferries.

![7.png](/.attachments/7-f8982fbe-36c0-4b38-8180-74fed8b5e026.png)

We can selectively focus on individual ferries. For example, `Trader`.

![8.png](/.attachments/8-ff01ea71-cecb-4389-a670-f5f72ab08819.png)

Here we see a nice distribution that shows that many trips are between about 70-90% loaded. Which doesn't seem too bad.

However, this is not always the case. Let's look at ferry `Van Isle Link`.

![9.png](/.attachments/9-74b1d21e-33f6-46fb-b9ce-70ba8f546331.png)

It seems that half of its trips are made less then 50% loaded. With the rest at above 90% loaded. So what's going on here? If we also now slice the data by route:

![10.png](/.attachments/10-ffc76a1e-c5b2-4c6c-9b7b-a183e08991ab.png)

`Van Isle Link` works the `Duke Point / Surrey` route. We can see that the trips originating Surrey are suboptimal. While this still leaves open questions, you can see that by slicing by route, we were able to identify a suboptimal ferry/route combination.

## Analysis of Missed Sailings
Customers arriving at a terminal do not always get on the next sailing. The next sailing is deemed to be one where the customer has signed in at least 30 minutes prior to the actual departure time but the container is not loaded. For example, if the ferry is already full.

This analysis, counts the number of container boarded versus the number of containers eligible but were not boarded. The visuals are grouped according to both vessel and route.

This scatter plot shows the loading for `Transporter` over many sailings.
* Each point (circle) represents two values.
   - It's `x` position is the number of containers boarded
   - The `y` position is the number of containers that were missed (and were waiting to board).
   - The size of the circle represents the number of sailings made with that x-y count.

![11.png](/.attachments/11-3e1b7a94-8ae4-4459-9e90-ca48c17a4edd.png)

### Observations
* Looking at the left side of the chart, we see that when the sailing/ferry is lightly loaded, very few if any containers are missed (left behind).
* As the ferry begins to reach capacity, we observe more data points higher up, indicating that containers are left behind. We do still see many larger circles close to the x-axis, indicating that likely many sailings are still are not missing containers. We can confirm this with the following frequency histogram. The "long tail" does indeed indicate that most ferries are not leaving containers behind. For example we see 666 sailings with no container left behind. In fact, the vast majority of sailings miss no more than 9 to 10 containers.

![12.png](/.attachments/12-49687f71-dcb2-4ae0-994e-55a0b62eecdb.png)

* We can also slice Transporter's sailings by route. Focusing on just the Duke Point and Tilbury terminals, we observe an asymmetry whereby Tilbury departures appear to contribute more to missed containers that Duke Point departures.

![13.png](/.attachments/13-2bec3acb-3d6e-4d0b-acb1-4aa8a8b4834d.png)

* The Swartz Bay / Tilbury route also exhibits asymmetry. Again, sailings departing Tilbury for Swartz Bay appear to be the main contributor to missed containers.

![14.png](/.attachments/14-1a3a9206-9786-4418-8b98-8a07ac4deddc.png)

  We can again look at the frequency histograms for these routes.

  - Swartz Bay to Tilbury:
![15.png](/.attachments/15-6b8881a8-245a-4bb1-90b6-7b4bf0440eaf.png)

  - Tilbury to Swartz Bay
![16.png](/.attachments/16-ab2bc7db-6626-421b-9593-4cd05964fcf3.png)
  While indeed there are more missed containers, the majority of sailings leaving behind no more than about 10-11 containers.   

   - Tilbury - Duke Point Routes
![17.png](/.attachments/17-b1594de9-f4db-4082-bdad-b4a6b09bebe9.png)
   Here we note that the total number of sailings on this route is much smaller than the Tilbury-Swartz Bay route. Percentagewise though, more containers are being missed in both directions.

### Princess Superior
This ferry appears to miss a large number of containers. The first plot shows a distinct group of sailings for which a containers are being left behind. The second plot shows that most of the containers being are those departing Tilbury for Swartz Bay. The third frequency histogram confirms that indeed nearly all sailings departing Tilbury for Swartz Bay are missing containers.

![18.png](/.attachments/18-12d4f142-356b-455f-8be6-52aeb61a9186.png)

If the data is accurate, further investigation would be necessary to identify, why Princess Superior is leaving behind containers at Tilbury.

# Caveat
Validation of the stats presented here is still pending. As such the actual metrics shown may be incorrect and the observations invalid.
