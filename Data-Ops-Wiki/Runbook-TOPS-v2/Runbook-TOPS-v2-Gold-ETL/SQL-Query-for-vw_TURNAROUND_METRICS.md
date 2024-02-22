   ```

WITH T_JOB_EXT AS
(
    SELECT
        j.*,
        t.fk_Assignment_in
    FROM tops.vw_T_JOB j
    LEFT JOIN tops.vw_T_TRUNK t on t.fk_Job_in = j.pk_Job_in 
),
T_Appointment_EXT AS
(
    SELECT
        *,
        TO_TIMESTAMP(CONCAT(LEFT(CAST(Scheduled_Arrival_Date AS String), 10), ' ', RIGHT(CAST(Scheduled_Arrival_Time AS String), 8)), 'yyyy-MM-dd HH:mm:ss') AS Scheduled_Arrival_Date_Time,
        TO_TIMESTAMP(CONCAT(LEFT(CAST(Actual_Arrival_Date AS String), 10), ' ', RIGHT(CAST(Actual_Arrival_Time AS String), 8)), 'yyyy-MM-dd HH:mm:ss') AS Actual_Arrival_Date_Time,
        TO_TIMESTAMP(CONCAT(LEFT(CAST(Scheduled_Departure_Date AS String), 10), ' ', RIGHT(CAST(Scheduled_Departure_Time AS String), 8)), 'yyyy-MM-dd HH:mm:ss') AS Scheduled_Departure_Date_Time
    FROM tops.vw_T_Appointment
)
SELECT
    m.Sailing_ID,
	m.Actual_Departure_Date_Time,
	m.Actual_Arrival_Date_Time,
    m.Scheduled_Departure_Date_Time,
    m.Scheduled_Arrival_Date_Time,
    m.Origin_Port,
    m.Destination_Port,
	m.Vessel,
	m.Route,
	m.footage_consumed,
	m.num_units,
    LAG(m.footage_consumed, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_footage_consumed,
    LAG(m.num_units, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_num_units,
    LAG(m.Actual_Arrival_Date_Time, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_Actual_Arrival_Date_Time,
    LAG(m.Scheduled_Arrival_Date_Time, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_Scheduled_Arrival_Date_Time,
    LAG(m.Destination_Port, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_Destination_Port,
    LAG(m.Sailing_ID, 1) OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as previous_Sailing_ID,
    ROW_NUMBER() OVER (PARTITION BY m.Vessel ORDER BY m.Vessel, m.Actual_Departure_Date_Time) as trip_num
FROM (
	SELECT
        asgmt.Sailing_ID,
        asgmt.Actual_Departure_Date_Time,
        asgmt.Deleted_dt,
        appt.Actual_Arrival_Date_Time,
        appt.Scheduled_Arrival_Date_Time,
        appt.Scheduled_Departure_Date_Time,
        tt2.Vessel_Name AS Vessel,
        rt.Route,
        rt.Origin_Terminal as Origin_Port,
        rt.Destination_Terminal as Destination_Port,
        SUM(coalesce(job.length, 0) + coalesce(job.front_overhang, 0) + coalesce(job.rear_overhang, 0)) as footage_consumed,
        COUNT(job.BOL_Number) as num_units
	FROM T_JOB_EXT job
        INNER JOIN tops.vw_T_CONSIGNMENT con on fk_Consignment_in = con.pk_Consignment_in
        INNER JOIN tops.vw_T_ASSIGNMENT asgmt on job.fk_Assignment_in = asgmt.Sailing_ID
        INNER JOIN T_Appointment_EXT appt on appt.pk_Appointment_in = asgmt.fk_Appointment_in
        INNER JOIN tops.vw_T_Truck tt2 on tt2.pk_Truck_in = asgmt.fk_Truck_in
        INNER JOIN tops.vw_T_ROUTE rt on asgmt.fk_Route_in = rt.pk_Route_in
	WHERE asgmt.Deleted_dt IS NULL AND con.Deleted_Dt is NULL
	GROUP BY
        asgmt.Sailing_ID,
        asgmt.Actual_Departure_Date_Time,
        asgmt.Deleted_dt,
        appt.Actual_Arrival_Date_Time,
        appt.Scheduled_Arrival_Date_Time,
        appt.Scheduled_Departure_Date_Time,
        tt2.Vessel_Name,
        rt.Route,
        rt.Origin_Terminal,
        rt.Destination_Terminal
) m
```