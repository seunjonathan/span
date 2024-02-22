   ```
SELECT
    t.pk_Truck_in
    ,t.Vessel_Code
    ,t.Vessel_Name AS Vessel_Barge_Name
    ,CASE
        WHEN t.Vessel_Name = 'Coastal Spirit' THEN 'Challenger'
        WHEN t.Vessel_Name = 'Fraser Link' THEN 'Pusher'
        ELSE t.Vessel_Name
    END AS Vessel_Tug_Name
    ,tt.Footage_Capacity
    ,tt.Unit_Capacity
    ,t.Deleted_dt
FROM tops.vw_T_TRUCK t
INNER JOIN tops.vw_T_TRAILERTYPE tt ON t.Vessel_Code = tt.Vessel_Code
WHERE t.Vessel_Code <> 'ROB'
   ```