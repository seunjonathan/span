```
select *
from
  (
    SELECT          *
    , ROW_NUMBER () OVER (PARTITION BY BOL_Number ORDER BY
                          Added_dt desc) as rw_number
    FROM
      (
        WITH CTE_JobPK AS
          (
            SELECT
              pk_Job_IN AS JobPK
            FROM
              t_Job
            WHERE
              Added_dt > add_months(current_date(), -1)
            UNION
            SELECT
              fk_Job_in
            FROM
              t_JobFieldUpdated
            WHERE
              DateTime_dt > add_months(current_date(), -1)
          )
        SELECT
          job.BOL_Number
        , assignment.Sailing_ID
        , job.fk_ContainerType_in      AS Container_Type
        , trunk.fk_AssignmentStatus_in AS Assignment_Status
        , jobsummary.Hazardous_bt      AS Hazardous_Goods
        , job.Length
        , job.Front_Overhang
        , job.Rear_Overhang
        , to_timestamp(concat(date(otgpod.Sign_In_Date),'T', date_format(otgpod.Sign_In_Time,'HH:mm:ss')))                AS Signature_DateTime
        , to_timestamp(concat(date(waypoint.Picked_Up_Date_Time),'T', date_format(waypoint.DepartureTime_dt,'HH:mm:ss'))) AS Actual_Picked_Up_DateTime
        , job.fk_Route_in                                                                                                 AS Route
        , job.fk_JobCategory_in                                                                                           AS Category
        , job.Added_dt
        , CASE
            WHEN to_timestamp(concat(date(appointment.Actual_Arrival_Date),'T', date_format(appointment.Actual_Arrival_Time,'HH:mm:ss'))) > job.Preferred_Pickup_Date_Time
              THEN to_timestamp(unix_timestamp(to_timestamp(concat(date(appointment.Actual_Arrival_Date),'T', date_format(appointment.Actual_Arrival_Time,'HH:mm:ss')))) + 43200)
              ELSE job.Preferred_Pickup_Date_Time
          END AS Preferred_Pickup_Date_Time_official
        , job.Preferred_Pickup_Date_Time
        , t_Consignment.Deleted_dt AS Deleted_Date
        , job.CustomFlag2_bt       AS DG_Authorized
        , trunk.LastDoneStatus_dt  AS Status
        , job.pk_Job_in
        , t_Consignment.fk_Customer_in
        , job.fk_MovementMode_in
        , job.Unit_Number
        , CASE
            WHEN subassreslog.UsedReservationTEU_dc = 1
              THEN 1
              ELSE 0
          END AS Reservation_used_TEU
        FROM
          t_Job job
          LEFT JOIN
            t_Trunk trunk
            ON
              job.pk_Job_in = trunk.fk_Job_in
          LEFT JOIN
            t_assignment assignment
            ON
              trunk.fk_Assignment_in = assignment.Sailing_ID
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
          LEFT JOIN
            (
              select *
              from
                (
                  SELECT *
                  , ROW_NUMBER() OVER (PARTITION BY fk_Assignment_in, fk_Trunk_in ORDER BY
                                       added_dt DESC) AS row_num
                  FROM
                    t_AssignmentReservationLog
                )
              where
                row_num = 1
            )
            subassreslog
            ON
              subassreslog.fk_Trunk_in          = trunk.pk_Trunk_in
              AND subassreslog.fk_Assignment_in = assignment.Sailing_ID
        WHERE
          job.pk_Job_in IN
          (
            SELECT
              JobPK
            FROM
              CTE_JobPK
          )
          AND job.Added_dt >= '2019-11-29 15:14:19.737'
      )
  )
where
  rw_number = 1`
```