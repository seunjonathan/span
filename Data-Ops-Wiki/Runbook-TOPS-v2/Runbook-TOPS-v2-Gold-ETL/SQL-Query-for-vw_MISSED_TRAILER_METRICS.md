   ```
WITH T_OTG_POD_EXT AS
(
    SELECT
        * ,
        TO_TIMESTAMP(CONCAT(LEFT(CAST(Sign_In_Date AS String), 10), ' ', RIGHT(CAST(Sign_In_Time AS String), 8)), 'yyyy-MM-dd HH:mm:ss') AS Signature_Date_Time
    FROM tops.vw_T_OTG_POD
),
T_JOB_EXT AS
(
    SELECT
        j.*,
        t.fk_Assignment_in
    FROM tops.vw_T_JOB j
    LEFT JOIN tops.vw_T_TRUNK t on t.fk_Job_in = j.pk_Job_in 
)
SELECT * FROM
(
    SELECT 
        job.BOL_Number,
        job.pk_Job_in,
        job.Unit_Number,
        asgmt1.Sailing_ID,
        asgmt2.Sailing_ID as other_Sailing_ID,
        pod.Signature_Date_Time,
        asgmt1.Actual_Departure_Date_Time,
        asgmt2.Actual_Departure_Date_Time as other_Actual_Departure_Date_Time,
        rt.Route,
        DATEDIFF(SECOND, pod.Signature_Date_Time, asgmt1.Actual_Departure_Date_Time) / 60 as minutes_between_signin_and_departure,
        DATEDIFF(SECOND, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) / 60 as minutes_between_signin_and_other_departure,
        ROW_NUMBER() OVER (PARTITION BY job.pk_Job_in ORDER BY asgmt2.Actual_Departure_Date_Time) as sailing_num 
    FROM T_JOB_EXT job
        INNER JOIN tops.vw_T_CONSIGNMENT con on fk_Consignment_in = con.pk_Consignment_in
        INNER JOIN tops.vw_T_TRUNK trk on job.pk_Job_in = trk.fk_Job_in
        INNER JOIN T_OTG_POD_EXT pod on trk.pk_Trunk_in = pod.fk_Trunk_in
        INNER JOIN tops.vw_T_ASSIGNMENT asgmt1 on job.fk_Assignment_in = asgmt1.Sailing_ID
        INNER JOIN tops.vw_T_ASSIGNMENT asgmt2 on (job.fk_Route_in = asgmt2.fk_Route_in)
                            and (pod.Signature_Date_Time < asgmt2.Actual_Departure_Date_Time) -- helps speed up query
                            and (DATEDIFF(SECOND, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) / 60.0 >= 30)
                            and (DATEDIFF(DAY, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) < 70)
        INNER JOIN tops.vw_T_TRANSPORTPLAN_TRAILER tpt on asgmt1.fk_TransportPlan_in = tpt.fk_TransportPlan_in
        INNER JOIN tops.vw_T_TRAILERTYPE tt on tpt.fk_TrailerType_in = tt.pk_TrailerType_in
        INNER JOIN tops.vw_T_TRANSPORTPLAN_TRAILER tpt2 on asgmt2.fk_TransportPlan_in = tpt2.fk_TransportPlan_in
        INNER JOIN tops.vw_T_TRAILERTYPE tt2 on tpt2.fk_TrailerType_in = tt2.pk_TrailerType_in
        INNER JOIN tops.vw_T_ROUTE rt on asgmt1.fk_Route_in = rt.pk_Route_in
    WHERE con.Deleted_Dt is NULL
    AND asgmt1.Deleted_dt IS NULL 
    AND asgmt2.Deleted_dt IS NULL 
    AND asgmt1.Actual_Departure_Date_Time IS NOT NULL
) t
WHERE minutes_between_signin_and_other_departure <= minutes_between_signin_and_departure
UNION
SELECT * FROM
(
    SELECT 
        job.BOL_Number,
        job.pk_Job_in,
        job.Unit_Number,
        asgmt1.Sailing_ID,
        asgmt2.Sailing_ID as other_Sailing_ID,
        pod.Signature_Date_Time,
        asgmt1.Actual_Departure_Date_Time,
        asgmt2.Actual_Departure_Date_Time as other_Actual_Departure_Date_Time,
        rt.Route,
        null  as minutes_between_signin_and_departure,
        DATEDIFF(SECOND, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) / 60 as minutes_between_signin_and_other_departure,
        ROW_NUMBER() OVER (PARTITION BY job.pk_Job_in ORDER BY asgmt2.Actual_Departure_Date_Time) as sailing_num 
    FROM T_JOB_EXT job
        INNER JOIN tops.vw_T_CONSIGNMENT con on fk_Consignment_in = con.pk_Consignment_in
        INNER JOIN tops.vw_T_TRUNK trk on job.pk_Job_in = trk.fk_Job_in
        INNER JOIN T_OTG_POD_EXT pod on trk.pk_Trunk_in = pod.fk_Trunk_in
        LEFT JOIN tops.vw_T_ASSIGNMENT asgmt1 on job.fk_Assignment_in = asgmt1.Sailing_ID
        INNER JOIN tops.vw_T_ASSIGNMENT asgmt2 on (job.fk_Route_in = asgmt2.fk_Route_in)
                            and pod.Signature_Date_Time < asgmt2.Actual_Departure_Date_Time -- helps speed up query
                            and (DATEDIFF(SECOND, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) / 60.0 >= 30)
                            and (DATEDIFF(DAY, pod.Signature_Date_Time, asgmt2.Actual_Departure_Date_Time) < 70)
        INNER JOIN tops.vw_T_ROUTE rt on asgmt2.fk_Route_in = rt.pk_Route_in
    WHERE con.Deleted_Dt is NULL
    AND asgmt2.Deleted_dt IS NULL 
    AND asgmt1.Actual_Departure_Date_Time IS NULL
) p
```