[[_TOC_]]
#**Dev Infra**
*	Created resource groups **`rg-smg-common-dev`** and **`rg-smg-tops-dev`** to provision the required resources and workspaces that are essential to setting up development environment.

##**Resources created under `rg-smg-common-dev`**

*	The resources listed in towworksv2 runbook are shared and also used here. Please refer to https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/88/Infrastructure-Setup?anchor=**resources-created-under-%60rg-smg-common-dev%60**

In addition to the resources created in the link above, we also -

*	Created Key Vault **`kv-smg-dev`** and have generated the following secrets in it
1.	**`TOPS-RESTAPI-Secret`** 
2.	**`TOPS-RESTACCESSID`** 

These credentials above are used to populate the authorization header that must be sent in every RESTAPI call to the PRISM endpoints.
`Credential={{api_access_id}}, Key={{api_secret_key}}`


##**Resources created under **`rg-smg-tops-dev`****

*	Created azure data factory workspace **`adfv2-tops-dev`** to provision the process of orchestration, ingesting, transforming and analysis of data by creating a pipeline.




##**Assigning access between the resources**

*	**`adlssmgdev-serviceprincipal`** , **`adfv2-tops-dev`** and also the individual users who are going to use storage account must be given **Storage Blob Data Contributor** role on the storage account **`adlssmgdev`**.
*	**`adfv2-tops-dev`** and **`dbw-smg2-dev`** workspace must be given get, list secret permissions in **`kv-smg-dev`** key vault by clicking on access policies tab under this key vault.
*	**`adfv2-tops-dev`** must be assigned **Contributor** role on **`dbw-smg2-dev`** workspace.
*	**`adlssmgdev-serviceprincipal`** must be assigned **Owner** role on **`adfv2-tops-dev`** workspace.
*	All the active users must be given **synapse-administrator** role for **`syn-smg-dev`** workspace by clicking on access control option within manage tab of  synapse studio.
****

#**Prod Infra**
*	Created resource groups **`rg-smg-common-prod`** and **`rg-smg-tops-prod`** to provision the required resources and workspaces that are essential to setting up production environment.

##**Resources created under `rg-smg-common-prod`**


*	The resources listed in towworksv2 runbook are shared and also used here. Please refer to
https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/88/Infrastructure-Setup?anchor=**resources-created-under-%60rg-smg-common-prod%60**

In addition to the resources created in the link above, we also -

*	Created Key Vault **`kv-smg-prod`** and have generated the following secrets in it
1.	**`TOPS-RESTAPI-Secret`** 
2.	**`TOPS-RESTACCESSID`** 
![prism infra.png](/.attachments/prism%20infra-c1b42a70-ebad-4e9e-87d6-58b2bc85bffb.png)

These credentials above are used to populate the authorization header that must be sent in every RESTAPI call to the PRISM endpoints.
`Credential={{api_access_id}}, Key={{api_secret_key}}`


##**Resources created under **`rg-smg-tops-prod`****

*	Created azure data factory workspace **`adfv2-tops-prod`** to provision the process of orchestration, ingesting, transforming and analysis of data by creating a pipeline.




##**Assigning access between the resources**

*	**`adlssmgprod-serviceprincipal`** , **`adfv2-tops-prod`** and also the individual users who are going to use storage account must be given **Storage Blob Data Contributor** role on the storage account **`adlssmgprod`**.
*	**`adfv2-tops-prod`** and **`dbw-smg-prod`** workspace must be given get, list secret permissions in **`kv-smg-prod`** key vault by clicking on access policies tab under this key vault.
*	**`adfv2-tops-prod`** must be assigned **Contributor** role on **`dbw-smg-prod`** workspace.
*	**`adlssmgprod-serviceprincipal`** must be assigned **Owner** role on **`adfv2-tops-prod`** workspace.
*	All the active users must be given **synapse-administrator** role for **`syn-smg-prod`** workspace by clicking on access control option within manage tab of  synapse studio.
****