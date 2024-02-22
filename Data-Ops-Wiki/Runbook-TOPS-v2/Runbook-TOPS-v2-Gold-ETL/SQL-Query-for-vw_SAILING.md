```
SELECT Distinct
                                                                                                                                        assignment.Sailing_ID
, to_timestamp(concat(date(appointment.Scheduled_Departure_Date),'T', date_format(appointment.Scheduled_Departure_Time,'HH:mm:ss'))) AS Scheduled_Depature_Date_time
, assignment.Actual_Departure_Date_Time
, floor( ( unix_timestamp(assignment.Actual_Departure_Date_Time) - unix_timestamp(to_timestamp(concat(date(appointment.Scheduled_Departure_Date),'T', date_format(appointment.Scheduled_Departure_Time,'HH:mm:ss')))) )/60 )                                                                                  AS Depature_Variance
, to_timestamp(concat(date(appointment.Scheduled_Arrival_Date),'T', date_format(appointment.Scheduled_Arrival_Time,'HH:mm:ss')))                                                                                                                                                                              AS Scheduled_Arrival_Date_time
, to_timestamp(concat(date(appointment.Actual_Arrival_Date),'T', date_format(appointment.Actual_Arrival_Time,'HH:mm:ss')))                                                                                                                                                                                    AS Actual_Arrival_DateTime
, floor( ( unix_timestamp(to_timestamp(concat(date(appointment.Actual_Arrival_Date),'T', date_format(appointment.Actual_Arrival_Time,'HH:mm:ss'))) ) - unix_timestamp(to_timestamp(concat(date(appointment.Scheduled_Arrival_Date),'T', date_format(appointment.Scheduled_Arrival_Time,'HH:mm:ss'))) ) )/60 ) AS Arrival_Variance
, assignment.Added_dt                                                                                                                                                                                                                                                                                         AS Add_Date
, assignment.Deleted_dt                                                                                                                                                                                                                                                                                       AS Deleted_Date
, TRY_CAST(assignment.HaulierInformed_bt AS VARCHAR(10)) AS                                                                                                                                                                                                                                                      Lock_Sailing
, assignment.fk_Truck_in
, assignment.fk_route_in
FROM
  t_Assignment assignment
  INNER JOIN
    t_Appointment appointment
    ON
      appointment.pk_Appointment_in = assignment.fk_Appointment_in
  INNER JOIN
    t_Assignment_MasterLog assignmentmasterlog
    ON
      assignment.Sailing_ID = assignmentmasterlog.fk_Assignment_in
  INNER JOIN
    t_MasterLog masterlog
    ON
      assignmentmasterlog.fk_MasterLog_in = masterlog.pk_MasterLog_in
      and masterlog.date_dt               > add_months(current_date(), -1)
WHERE
  (
    masterlog.Date_dt      > add_months(current_date(), -1)
    OR assignment.Added_dt > add_months(current_date(), -1)
  )
```