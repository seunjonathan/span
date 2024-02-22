# Introduction

These notes capture a meeting (26th July 2022) in which Vitor Porto described the Seaspan Ferry business and process from his point of view. The meeting was very informative!

## General Business

* Seaspan provides commercial transport options between the lower mainland and Vancouver Island.
* There are 4 terminals, 2 on the mainland at Tilbury and Surrey and another 2 on the island at Duke Pt and Swartz Bay.
* Seaspan accounts for 70% of the commercial business with the remainder picked up by BC Ferries.
* Customers typically book a sailing via the TOPS system.
* Most of the ferry traffic consists of trailers.

## Terminal Activity
* As trucks arrive at the terminal, the drivers "sign in" the trailer and leave the trailer there.
* Seaspan employees are responsible for loading (and unloading) the trailers.

## Data Description
* The `Date_Time_Added` is the time at which the request by the customer for a sailing is entered into the system. At this time a Bill of Lading (BOL) is assigned.
* The time at which a trailer arrives at the terminal is different. This is the `Signature_Date_Time`.
* Each request for transport is recorded in the `Job` table.
* The `Assignment` table details an actual sailing. `Jobs` are assigned to `Assignments`.
* Some information about the sailing is also captured in the `Appointment` table and `TrailerType`. Vitor noted that TOPS is originally a ground transport application which explains why vessel information is captured a table called "TrailerType"!
* Vitor pointed out that the accuracy of the data after the trailers have arrived is not as reliable as the data upon departure. This is because once trailers are awaiting pick-up, the sign-out times may not reflect actual pick-up times, but rather when the staff noticed the trailers had gone. E.g. at the end of the day, when the terminal is checked, staff may sign out a number of trailers all at the same time because that's when they noticed the trailers are no longer there.

## Process
* The status of an assignment is as follows:
     1. `Assigned` meaning a job has been assigned to a sailing. Or `Assigned by Customer`. Seaspan would prefer customers select the sailing themselves.
     2. `Loaded`
     3. `In-transit`
     4. `Arrived`
     5. `Standby`. Job was assigned but is not guaranteed on the assigned sailing. A higher priority trailers could bump this job.
Vitor pointed out that not all of these are strictly updated as might be expected. E.g. `unloaded`?
* Upon arrival at a destination, the trailer is unloaded and remains at the terminal (occupying space) until the customer picks it up. A customer is expected to provide a `preferred pickup time` which Seaspan attempts to honour.

## KPIs
* Customers are charged by footage. This includes the length of the trailer and any front or rear overhang. The KPI is `total footage moved`.
* `Deck utilisation` is the total footage loaded / deck capacity * 100
* `Num late arrivals`
* ` Num units arriving before pick up time`
* `Trailers left behind` i.e. number of trailers that arrived at the departure terminal but did not make it on the next ferry.

## Predictive Analytics
A couple of very useful predictions would be:
1. Number of trailers arriving at a terminal for a particular sailing
2. Risk of reaching trailer capacity at a terminal.
    This is to predict the sum of the number of trailers awaiting departure and arrived trailers awaiting pick up at any given terminal.


