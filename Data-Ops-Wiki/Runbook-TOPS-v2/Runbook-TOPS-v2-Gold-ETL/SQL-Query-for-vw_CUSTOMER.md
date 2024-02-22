```
SELECT
    cu.pk_Customer_in
    ,co.pk_Company_in
    ,cu.Customer_Number
    ,co.Customer_Name
    ,co.Customer_Short_Name
    ,tier.Tier_Name
    ,tier.Tier_Code
    ,jc.Unit_Category_Code
    ,jc.Unit_Category_Name
    ,cu.Industry_Category
    ,cm.Name_vc AS Commercial_Manager
    ,cm.Login_ch AS Commercial_Manager_Code
    ,COALESCE(co.fk_ParentCompany_in,co.pk_Company_in) AS fk_ParentCompany_in
    ,COALESCE(cu.Deleted_dt,co.deleted_dt) AS Deleted_dt

FROM tops.vw_T_CUSTOMER cu
LEFT JOIN tops.vw_T_COMPANY co ON cu.fk_Company_in = co.pk_Company_in
LEFT JOIN tops.vw_T_CUSTOMERTYPE tier ON cu.fk_CustomerType_in = tier.pk_CustomerType_in
LEFT JOIN tops.vw_T_USER cm ON cu.fk_SalesPerson_in = cm.pk_User_in
LEFT JOIN tops.vw_T_JOBCATEGORY jc ON cu.fk_JobCategory_in = jc.pk_JobCategory_in
```