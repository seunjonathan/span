```
SELECT
  [pk_Truck_in]
, 'Vessel'    as 'Location_Type'
, CASE
    WHEN truck.[TruckName_vc] ='Fraser Link'
      THEN 'Pusher'
      ELSE truck.[TruckName_vc]
  END AS 'Vessel_Name'
, (
    SELECT
      TOP 1 -1*(LEFT([Longitude_vc],CHARINDEX('''',[Longitude_vc])-1) + CONVERT(decimal(10,6),SUBSTRING([Longitude_vc], CHARINDEX('''',[Longitude_vc]) + 1, CHARINDEX('''',[Longitude_vc],CHARINDEX('''',[Longitude_vc])+1) - CHARINDEX('''',[Longitude_vc]) - 1))/60 + CONVERT(decimal(10,6),SUBSTRING(longitude_vc,CHARINDEX('''',Longitude_vc,CHARINDEX('''',longitude_vc,charindex('''',longitude_vc)+1))+1,len(longitude_vc)-CHARINDEX('''',Longitude_vc,CHARINDEX('''',longitude_vc,charindex('''',longitude_vc)+1))-1))/3600 )
    FROM
      t_DeviceTracking
    WHERE
      t_DeviceTracking.DeviceID_vc = truck.DataCaptureUnit_vc
    ORDER BY
      t_DeviceTracking.Date_dt desc
    , t_DeviceTracking.Time_dt desc
  )
  'Longitude'
, (
    SELECT
      TOP 1 (LEFT([Latitude_vc],CHARINDEX('''',[Latitude_vc])-1) + CONVERT(decimal(10,6),SUBSTRING([Latitude_vc], CHARINDEX('''',[Latitude_vc]) + 1, CHARINDEX('''',[Latitude_vc],CHARINDEX('''',[Latitude_vc])+1) - CHARINDEX('''',[Latitude_vc]) - 1))/60) + CONVERT(decimal(10,6),SUBSTRING(latitude_vc,CHARINDEX('''',Latitude_vc,CHARINDEX('''',latitude_vc,charindex('''',latitude_vc)+1))+1,len(latitude_vc)-CHARINDEX('''',Latitude_vc,CHARINDEX('''',latitude_vc,charindex('''',latitude_vc)+1))-1))/3600 'Latitude'
    FROM
      t_DeviceTracking
    WHERE
      t_DeviceTracking.DeviceID_vc = truck.DataCaptureUnit_vc
    ORDER BY
      t_DeviceTracking.Date_dt desc
    , t_DeviceTracking.Time_dt desc
  )
  'Latitude'
, (
    SELECT
      TOP 1
      CASE
        WHEN DATEDIFF(mi, DATEADD(dd,2,Date_dt + Time_dt), GETDATE())> 10
          THEN 0
          ELSE SpeedKnots_dc
      END
    FROM
      t_DeviceTracking
    WHERE
      t_DeviceTracking.DeviceID_vc = truck.DataCaptureUnit_vc
    ORDER BY
      t_DeviceTracking.Date_dt desc
    , t_DeviceTracking.Time_dt desc
  )
  'Knots'
, (
    SELECT
      TOP 1 Heading_in
    FROM
      t_DeviceTracking
    WHERE
      t_DeviceTracking.DeviceID_vc = truck.DataCaptureUnit_vc
    ORDER BY
      t_DeviceTracking.Date_dt desc
    , t_DeviceTracking.Time_dt desc
  )
  'Heading'
, (
    SELECT
      TOP 1 DATEADD(dd,2,Date_dt + Time_dt)
    FROM
      t_DeviceTracking
    WHERE
      t_DeviceTracking.DeviceID_vc = truck.DataCaptureUnit_vc
    ORDER BY
      t_DeviceTracking.Date_dt desc
    , t_DeviceTracking.Time_dt desc
  )
  'Date_Time'
FROM
  [t_Truck] truck
WHERE
  truck.Deleted_dt                 IS NULL
  AND truck.DataCaptureUnit_vc IS NOT NULL
  AND truck.DataCaptureUnit_vc          <>''
  AND pk_Truck_in NOT IN (7, 19)
```