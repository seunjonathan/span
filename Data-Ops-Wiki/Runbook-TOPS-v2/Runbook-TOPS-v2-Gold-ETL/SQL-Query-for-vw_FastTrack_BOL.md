```
WITH CTE_JobPK AS
  (
    SELECT
      pk_Job_IN 'JobPK'
    FROM
      t_Job
    WHERE
      Added_dt > dateadd(ss,-300,getdate())
    UNION
    SELECT
      fk_Job_in
    FROM
      t_JobFieldUpdated
    WHERE
      DateTime_dt > dateadd(ss,-300,getdate())
  )
SELECT
  job.JobNumber_vc 'BOL_Number'
, assignment.pk_Assignment_in 'Sailing_ID'
, job.fk_ContainerType_in 'Container_Type'
, trunk.fk_AssignmentStatus_in 'Assignment_Status'
, jobsummary.Hazardous_bt 'Hazardous_Goods'
, job.OOGLength_dc 'Trailer_Length'
, job.OverlengthFront_dc 'Trailer_Overhang_Front'
, job.OverlengthBack_dc 'Trailer_Overhang_Back'
, DATEADD(dd, 2, otgpod.PODDate_dt                                          + otgpod.PODTime_dt) 'Signature_Date_Time'
, DATEADD(dd, 2, DATEADD(dd, 0, DATEDIFF(dd, 0, waypoint.DepartureDate_dt)) + waypoint.DepartureTime_dt) 'Actual_Picked_Up_Date_Time'
, job.fk_Route_in 'Route'
, job.fk_JobCategory_in 'Category'
, job.Added_dt 'Added_Date'
, CASE
    WHEN DATEADD(dd, 2, appointment.EndDate_dt    + appointment.EndTime_dt) > job.ShipmentDate_dt
      THEN DATEADD(hh, 60, appointment.EndDate_dt + appointment.EndTime_dt)
      ELSE job.ShipmentDate_dt
  END                 AS 'Preferred_Pickup_Date_Time_official'
, job.ShipmentDate_dt AS 'Preferred_Pickup_Date_Time'
, t_Consignment.Deleted_dt 'Deleted_Date'
, job.[CustomFlag2_bt] 'DG_Authorized'
, trunk.LastDoneStatus_dt 'Status'
, job.pk_Job_in
, t_Consignment.fk_Customer_in
, job.fk_MovementMode_in
, job.ContainerNumber_ch 'Unit_Number'
, ISNULL(
  (
    SELECT
      TOP 1
      CASE
        WHEN [UsedReservationTEU_dc] =1
          THEN 1
          ELSE 0
      END
    FROM
      [t_AssignmentReservationLog] subassreslog
    WHERE
      subassreslog.fk_Trunk_in          = trunk.pk_Trunk_in
      AND subassreslog.fk_Assignment_in = assignment.pk_Assignment_in
    ORDER BY
      subassreslog.Added_dt desc
  )
  ,0) 'Reservation_used_TEU'
FROM
  t_Job job
  LEFT JOIN
    t_Trunk trunk
    ON
      job.pk_Job_in = trunk.fk_Job_in
  LEFT JOIN
    t_assignment assignment
    ON
      trunk.fk_Assignment_in = assignment.pk_Assignment_in
  LEFT JOIN
    t_JobSummary jobsummary
    ON
      jobsummary.fk_Job_in = job.pk_Job_in
  LEFT JOIN
    t_OTG_POD otgpod
    ON
      otgpod.fk_Trunk_in = trunk.pk_Trunk_in
  LEFT JOIN
    t_Waypoint waypoint
    ON
      waypoint.fk_Trunk_in  = trunk.pk_Trunk_in
      AND waypoint.Order_si = 2
  LEFT JOIN
    t_Consignment
    ON
      job.fk_Consignment_in = t_Consignment.pk_Consignment_in
  LEFT JOIN
    t_Appointment appointment
    ON
      assignment.fk_Appointment_in = appointment.pk_Appointment_in
WHERE
  job.pk_Job_in IN
  (
    SELECT
      JobPK
    from
      CTE_JobPK
  )
  and job.Added_dt >= '2019-11-29 15:14:19.737'
```