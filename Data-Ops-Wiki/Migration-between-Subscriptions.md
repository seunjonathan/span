|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|05-Feb-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #3207 <br>


[[_TOC_]]

# Introduction
This document consists of details regarding the different applications that are being moved from one subscription to another and contains details regarding issues faced while moving resource/application from one Subscription to another.

We don't have option to move the complete resource group at once, we have to select all the applications individually and can move them.

#Function App
Steps followed while migrating function app to a different subscription
1. Created a clone of existing function app in Dev environment and tested if working.
2. After its working in Dev environment, started migration to new Subscription.

Tried moving Function App along with Application Insights and Failure Alert to another resource group if they can be moved but encountered with an error as in image below: 
![image.png](/.attachments/image-22b4f518-59c7-4fd7-bbb7-55c5382fcd8a.png)
with error code 
```
{"message":"Resource move policy validation failed. Please see details. 
Diagnostic information:  subscription id 'e2764bf7-bdda-4887-aa05-42f41431e1c1', request correlation id '975d39f7-c730-4207-94d8-e300ee99f097'. 
(Code: ResourceMovePolicyValidationFailed) The client 'siva.Nadella-az@seaspan.com' with object id 'a9ceca7e-19fc-4af5-b5e5-285a664c0420' has permission to perform action 'microsoft.alertsmanagement/smartDetectorAlertRules/write' on scope '/subscriptions/e2764bf7-bdda-4887-aa05-42f41431e1c1/resourcegroups/rg-smg-common-dev/providers/microsoft.alertsmanagement/smartDetectorAlertRules/Failure Anomalies - fa-towworks-migration-test'; however, it does not have permission to perform action(s) 'microsoft.insights/actiongroups/read' on the linked scope(s) '/subscriptions/e2764bf7-bdda-4887-aa05-42f41431e1c1/resourcegroups/powerbi_embedded/providers/microsoft.insights/actiongroups/application insights smart detection' (respectively) or the linked scope(s) are invalid. (Code: LinkedAuthorizationFailed, Target: microsoft.alertsmanagement/microsoft.alertsmanagement/smartDetectorAlertRules/Failure Anomalies - fa-towworks-migration-test)","code":"ResourceMovePolicyValidationFailed","name":"ce7ba984-d086-46a4-b0ad-ea634e45a023","status":409}
```
As per above error message we can see that we have only access to move the `Function App` but don't have permission to move the `Application Insights` and `Failure Alerts`.

If trying to move only function app in between resources able to process validations as shown below:
![image.png](/.attachments/image-0babf447-b19f-46eb-a2a0-c3934a8dc6b8.png).
But when trying to move from one subscription to another even a single function app we are facing error as shown below: 
![image.png](/.attachments/image-9e06d06d-a0b9-4946-90e7-22a0d415da3b.png)
with error code:
```
{"message":"Resource move validation failed. Please see details. Diagnostic information: timestamp '20240205T223726Z', subscription id 'e2764bf7-bdda-4887-aa05-42f41431e1c1', tracking id '77b7c8c4-8e7e-418a-b2c9-6590b8d00796', request correlation id 'bddd5ad5-f9b4-4372-bd8b-838211e314f9'. (Code: ResourceMoveProviderValidationFailed) Please select all the Microsoft.Web resources from 'rg-smg-towworks-dev' resource group for cross-subscription migration. Also, please ensure destination resource group 'rg-smg-common-dev' doesn't have any Microsoft.Web resources before move operation. Here is the list of resources you have to move together: fa-maretron-towworksv2-dev (Microsoft.Web/sites)\r\n fa-towworks-migration-test (Microsoft.Web/sites)\r\n fa-maretron-v2-dev (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-maretron-dev', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n fa-maretron-v2-prod (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-maretron-prod', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n fa-ppa-temp (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-maretron-dev', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n fa-towworksv2-prod (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-towworks-prod', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n fa-tops-n-dev (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-tops-dev', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n fa-tops-prod (Microsoft.Web/sites). This resource is located in resource group 'rg-smg-tops-prod', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n asp-maretron-v2-dev (Microsoft.Web/serverFarms). This resource is located in resource group 'rg-smg-common-dev', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n asp-smg-prod (Microsoft.Web/serverFarms). This resource is located in resource group 'rg-smg-common-prod', but hosted in the resource group 'rg-smg-towworks-dev'. This may be a result of prior move operations. Move it back to respective hosting resource group\r\n. Please check https://portal.azure.com/?websitesextension_ext=asd.featurePath%3Ddetectors%2FMigration#resource/subscriptions/e2764bf7-bdda-4887-aa05-42f41431e1c1/resourceGroups/rg-smg-towworks-dev/providers/Microsoft.Web/sites/fa-maretron-towworksv2-dev/troubleshoot for more information. (Code: BadRequest, Target: Microsoft.Web/sites)","code":"ResourceMoveProviderValidationFailed","name":"ce7ba984-d086-46a4-b0ad-ea634e45a07f","status":409}
```
We are getting same error even if we try to move all function app resources to new subscription with failure at validations as shown:
![Screenshot 2024-02-02 104207.png](/.attachments/Screenshot%202024-02-02%20104207-8922aaaf-f34d-4368-b530-f62ded97f7df.png)

#Azure Data Factory
Created a clone Data factory in existing Azure subscription but faced issue while running the pipelines as cloned data factory don't have access to delta lake storage `adlssmgdev`. 

Following are the access required for Data Factory to connect to Delta lake storage:
1. `Storage Blob Contributor` to read/write/delete from storage.(Can be obtained by One source ticket)
2. `Private End Point` for accessing the table storage to read information. 

While approving Private End point from storage we are getting denied due to policy error with error message as shown below:
![Screenshot 2024-02-02 093355.png](/.attachments/Screenshot%202024-02-02%20093355-19bd90e9-e75e-4b00-9b4b-f3fca48e51c3.png)

This is a new policy added in month of November 2023 because of which we are unable to approve `Private End Point` and test the pipeline before performing migration.

Following are access required for Data Factory to connect to Databricks:
1. `Contributor` access is to be given for Data Factory from `Databricks` to access Notebooks, DBFS, Cluster etc., to run the python script for performing transactions.

#Databricks

When we try to migrate Databricks, it will fail at validation page of move resource.
![image.png](/.attachments/image-4fa2e321-a07e-49c3-916c-0a07cfc66335.png)

#Synapse Analytics

Synapse is not suitable for movement between subscriptions as when we try to move it we are getting validation error as shown in image below:
![image.png](/.attachments/image-194aff98-e68e-423e-86e2-b90203eb80c7.png)

Error code for synapse is as follows:
```
  {"customHtml":{"htmlTemplate":"<code><div>Resource move validation failed. 
  Please see details. Diagnostic information: timestamp '20240215T183821Z', 
  subscription id 'e2764bf7-bdda-4887-aa05-42f41431e1c1', tracking id '90f67141-2b39- 
  47fa-bc14-7c9f9f574616', request correlation id '0a700a0e-25ab-40ee-9e39- 
  3b7222e2d602'. (Code: ResourceMoveProviderValidationFailed) 
  Resource move is not supported for resource types 'Microsoft.Synapse/workspaces' 
  and 'Microsoft.Synapse/privateLinkHubs' (Code: ResourceMoveNotSupported, Target: 
  Microsoft.Synapse/workspaces)</div></code>","viewModel":null}}
```
#Key Vault

Key vault can be moved from subscription to another without any issue and it is passing at validation level for movement.

#Storage 

We are unable to move `Storage` to new subscription as our storage account consists of `Private Endpoints` for connecting ADF and other components to it, because of these Private Endpoints, move is not supported for Storage as shown in error image below

![image.png](/.attachments/image-f34012f5-32b7-45ad-b337-2d1fa6ac30a3.png)

#Success
On passing validation, we will be able to move the resource to another subscription or another resource group by allowing a check mark as shown below:

![Screenshot 2024-02-12 105233_1.png](/.attachments/Screenshot%202024-02-12%20105233_1-7a89f3be-2a91-4fd3-806d-6d5155bdb114.png)

Once we tick the checkmark we will be able to move the resource.

As of now we are only able to move ADF from one subscription to another without any problem and the moved pipeline from ADF continued working in new `Subscription`, even if `Storage, Databricks, LAW` all are existing in another subscription without any issue.

`Note: Data factory should be given all permissions and should be running in old subscription, then only it will work in new subscription.`

#Creation of New Components
We won't be able to create new components of Storage Accounts, Synapse with same existing name in different subscription as system is not allowing as shown in images below.

![image.png](/.attachments/image-2aea86e4-e8b7-4364-9660-bb141fe5d31c.png)