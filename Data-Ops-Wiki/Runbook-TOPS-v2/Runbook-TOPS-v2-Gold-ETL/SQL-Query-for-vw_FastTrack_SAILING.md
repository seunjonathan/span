```
SELECT Distinct
  assignment.pk_Assignment_in 'Sailing_ID'
, dateadd(dd,2,appointment.StartDate_dt + appointment.StartTime_dt) 'Scheduled_Departure_Date_time'
, assignment.DepartureTime_dt 'Actual_Departure_DateTime'
, DATEDIFF(mi,assignment.DepartureTime_dt, dateadd(dd,2,appointment.StartDate_dt + appointment.StartTime_dt)) 'Departure_Variance'
, dateadd(dd,2,appointment.EstimatedEndDate_dt + appointment.EstimatedEndTime_dt) 'Scheduled_Arrival_Date_time'
, DATEADD(dd, 2, appointment.EndDate_dt        + appointment.EndTime_dt) 'Actual_Arrival_DateTime'
, DATEDIFF(mi, dateadd(dd,2,appointment.EstimatedEndDate_dt + appointment.EstimatedEndTime_dt), DATEADD(dd, 2, appointment.EndDate_dt + appointment.EndTime_dt)) 'Arrival_Variance'
, assignment.Added_dt 'Add_Date'
, assignment.Deleted_dt 'Deleted_Date'
, assignment.HaulierInformed_bt 'Lock_Sailing'
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
      assignment.pk_Assignment_in = assignmentmasterlog.fk_Assignment_in
  INNER JOIN
    t_MasterLog masterlog
    ON
      assignmentmasterlog.fk_MasterLog_in = masterlog.pk_MasterLog_in
      and masterlog.date_dt               > dateadd(mm,-1,getdate())
WHERE
  masterlog.Date_dt      > dateadd(ss,-300,getdate())
  OR assignment.Added_dt > dateadd(ss,-300,getdate())
```