|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|22-June-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #2855 <br>

[[_TOC_]]
#**Dev Infra**
*	Created resource groups **`rg-smg-common-dev`** and **`rg-smg-towworks-dev`** to provision the required resources and workspaces that are essential to setting up development environment.

##**Resources created under `rg-smg-common-dev`**

*	Created a Virtual Network **`vnet-smg-dev`** to provide a secure and isolated environment for the azure resources.
*	Created storage account **`adlssmgdev`** with firewall protection enabled and it’s mandatory to add in IP addresses of each user within Networking tab of storage account.
*	Created Databricks workspace **`dbw-smg2-dev`** with private and public subnets **`dbw-smg-dev-private-subnets`** and **`dbw-smg-dev-public-subnets`** to enable usage through virtual networking..
*	Created secret scope **`adlssmgdevscope`** using the URL https://adb-4379826858178347.7.azuredatabricks.net/?o=4379826858178347#secrets/createScope on **`dbw-smg-dev`** Databricks workspace to retrieve the secret values from Azure Key Vault.
*	Once the subnets are created for **`dbw-smg-dev`** it’s ideal to add them in **`adlssmgdev`** by clicking on Networking tab and adding them under virtual networks by selecting the option add from exiting virtual networks.
*	Created service principal account **`adlssmgdev-serviceprincipal`** from app-registrations and then generated a secret on top of this service principal account.
*	Created Key Vault **`kv-smg-dev`** and have generated the following secrets in it
1.	**`spSecret`** – to store the secret value for service principal secret
2.	**`TOWWORKS-RESTAPI-Secret`** – to retrieve the RESTAPI secret value for AuthToken
3.	**`TOWWORKS-RESTCOMPANYNAME`** – to retrieve the COMPANY KEY value from RESTAPI.
*	Created a synapse workspace **`syn-smg-dev`** 

##**Resources created under **`rg-smg-towworks-dev`****

*	Created azure data factory workspace **`adfv2-towworks-dev`** to provision the process of orchestration, ingesting, transforming and analysis of data by creating a pipeline.


##**Assigning access between the resources**

*	**`adlssmgdev-serviceprincipal`** , **`adfv2-towworks-dev`** and also the individual users who are going to use storage account must be given **Storage Blob Data Contributor** role on the storage account **`adlssmgdev`**.
*	**`adfv2-towworks-dev`** and **`dbw-smg2-dev`** workspace must be given get, list secret permissions in **`kv-smg-dev`** key vault by clicking on access policies tab under this key vault.
*	**`adfv2-towworks-dev`** must be assigned **Contributor** role on **`dbw-smg2-dev`** workspace.
*	**`adlssmgdev-serviceprincipal`** must be assigned **Owner** role on **`adfv2-towworks-dev`** workspace.
*	All the active users must be given **synapse-administrator** role for **`syn-smg-dev`** workspace by clicking on access control option within manage tab of  synapse studio.
****

#**Prod Infra**
*	Created resource groups **`rg-smg-common-prod`** and **`rg-smg-towworks-prod`** to provision the required resources and workspaces that are essential to setting up production environment.

##**Resources created under `rg-smg-common-prod`**

*	Created a Virtual Network **`vnet-smg-prod`** to provide a secure and isolated environment for the azure resources.
*	Created storage account **`adlssmgprod`** with firewall protection enabled and it’s mandatory to add in IP addresses of each user within Networking tab of storage account.
*	Created Databricks workspace **`dbw-smg-prod`** with private and public subnets **`dbw-smg-prod-private-subnets`** and **`dbw-smg-prod-public-subnets`** to enable usage through virtual networking..
*	Created secret scope **`adlssmgprodscope`** using the URL https://adb-4379826858178347.7.azuredatabricks.net/?o=4379826858178347#secrets/createScope on **`dbw-smg-prod`** Databricks workspace to retrieve the secret values from Azure Key Vault.
*	Once the subnets are created for **`dbw-smg-prod`** it’s ideal to add them in **`adlssmgprod`** by clicking on Networking tab and adding them under virtual networks by selecting the option add from exiting virtual networks.
*	Created service principal account **`adlssmgprod-serviceprincipal`** from app-registrations and then generated a secret on top of this service principal account.
*	Created Key Vault **`kv-smg-prod`** and have generated the following secrets in it
1.	**`spSecret`** – to store the secret value for service principal secret
2.	**`TOWWORKS-RESTAPI-Secret`** – to retrieve the RESTAPI secret value for AuthToken
3.	**`TOWWORKS-RESTCOMPANYNAME`** – to retrieve the COMPANY KEY value from RESTAPI.
*	Created a synapse workspace **`syn-smg-prod`** 

##**Resources created under **`rg-smg-towworks-prod`****

*	Created azure data factory workspace **`adfv2-towworks-prod`** to provision the process of orchestration, ingesting, transforming and analysis of data by creating a pipeline.




##**Assigning access between the resources**

*	**`adlssmgprod-serviceprincipal`** , **`adfv2-towworks-prod`** and also the individual users who are going to use storage account must be given **Storage Blob Data Contributor** role on the storage account **`adlssmgprod`**.
*	**`adfv2-towworks-prod`** and **`dbw-smg-prod`** workspace must be given get, list secret permissions in **`kv-smg-prod`** key vault by clicking on access policies tab under this key vault.
*	**`adfv2-towworks-prod`** must be assigned **Contributor** role on **`dbw-smg-prod`** workspace.
*	**`adlssmgprod-serviceprincipal`** must be assigned **Owner** role on **`adfv2-towworks-prod`** workspace.
*	All the active users must be given **synapse-administrator** role for **`syn-smg-prod`** workspace by clicking on access control option within manage tab of  synapse studio.
****

#Infra Clean Up

The following information consists details regarding the excess function or applications present in each `SMG` Resource group which are present in Development environment and not in Production environment and vice versa.

|Resource Group Name| Function/Application Name| Description|
|--|--|--|
|`rg-smg-maretron-dev`| `fa-ppa-temp`| Temporary PPA function app for checking Jobs table amendments.|
|`rg-smg-towworks-dev`| `la-amendppa-dev`| logic app for PPA Jobs amendments|
|`rg-smg-towworks-dev`| `Test_Failure_Alerts_PPA`| Alert rule for PPA failure in Dev environment|
|`rg-smg-towworks-dev`| `azureblob`| blob connection to delta lake for VPA mailer|
|`rg-smg-towworks-dev`| `azureblob-3`| blob connection to delta lake for PPA|
|`rg-smg-towworks-dev`| `office365-2`| connection to office 365 for vpa mailer|
|`rg-smg-common-dev`| `Test Failure Alert`| Alert rule created for testing purposes with only Dev members as receivers of alert|
|`rg-smg-common-prod`| `LogicAppsManagement(law-smg-prod)`| log analytics for Logic app|


