[[_TOC_]]
# Introduction
This document describes how an Azure Release CI/CD Pipeline was set up to automate the process of promoting `adfv2-towworksv2-dev` to `adfv2-towworksv2-prod`

# Prerequisites
* `adfv2-towworksv2-dev` is connected to a version control repository.
* `adfv2-towworksv2-prod` is not.

The goal is to automate the process of provisioning `adfv2-towworksv2-prod` with the latest contents of the `main` branch from `adfv2-towworksv2-dev`. This includes adjusting any linked service connections, global parameters or network endpoints so that they are 

# Setup Process
1. Create release pipeline under name `TOWWORKSv2`.
2. Add `adf_publish` branch from `towworks-adf` repository with alias `publish_towworks-adf` in the artifacts section.
3. Assign ARM template job as agent job of staging layer under name `PROD`.
4. Pass `ARMTemplateForFactory.json` file as template for the pipeline.
5. Pass `ARMTemplateParametersForFactory.json` file as template parameters consisting of all the Linked Services, Global Parameters and Managed Private endpoints details which needs to be reproduced in the production environment.
6. Under the `Override template parameters` section of agent job, provide the updated resource details for Linked Services, Global Parameters and MPE’s, as applicable to the production environment.
7. _Deploy_ the release pipeline → The target data factory will be populated with the source content and parameters.

## Notes for remaining work
Observations in parameters while deploying pipeline are as below:

For the parameter LS_ATS_SMG connection string we are unable to update storage name because of following error – ‘This parameter is a 'secureString'. To avoid storing 'secureString' parameters in plain text, it is recommended that you use secret variables, for example `$(variableName)`. Enclose the value in quotes if there are words seperated with whitespace. For example "word1 word2" or "$(var)" if variable has whitespace. Use escaped characters if value has a quote, for example "word\"withquote" ’
For the linked service of Databricks LS_DBW_SMG, the following parameters Databrick Workspace URL, Workspace resource ID are not being populated in ARM templates because of which unable to view these properties under Override template parameters option and only Cluster ID parameter is only being populated which is accessible for overriding in job.
Tried hardcoding the Databricks Workspace URL, Workspace resource ID values in ARM templates of adf_publish because of which these options are being shown under Override template parameters option.
After modifying Databricks Workspace URL and Workspace resource ID parameters in Override parameters and passing production environment Databricks values into release pipeline, values haven’t been updated in Linked Services of production ADF.
 

Work around for the above-mentioned problems of Table storage and Databricks is to manually input values of Table Storage, Databrick Workspace URL, Workspace resource ID in production ADF linked services.

Note: Even though Managed Private Endpoint is being populated during deployment, we have to manually approve MPE in Delta Lake Storage to get it working and also enable the Virtual Network manually for the first time of pipeline run.

#Issue within LS_ATS_SMG linked service
##Root cause
*	When the provisioning is done for data factory from dev to prod the parameters defined within the `LS_ATS_SMG` linked service is not overridden.
##Solution
*	Created a linked service `LS_KV_SMG` which would point to key vault `kv_smg_dev`.
*	Created a secret with name  `ADLSSMG-ACCESSKEY` and the secret value would be pointing to  connection string value retrieved from access keys tab of storage account `adlssmgdev`.
*	Later in linked service `LS_ATS_SMG` of data factory we can connect the table storage using account key option and then opt for Azure Key Vault, under it provide the necessary key vault linked service name and also the secret name value.
*	Finally, when we generate the ARM template and provision the pipeline to prod the required parameters can be overridden.

#Issue within LS_DBW_SMG linked service
##Root cause
*	When the provisioning is done for data factory from dev to prod the following parameters **Databrick Workspace URL** and **Workspace resource ID** are not being overridden within the linked service `LS_DBW_SMG`.
##Solution
*	Once the ARMTemplate is generated and updated in the git repo. Navigate to git repo `towworks-adf` and then go to json file `ARMTemplateForFactory.json` and add the following parameters under the parameters object of json file
![arm template.png](/.attachments/arm%20template-b25d68d3-ea41-4ea5-bb71-fff4fb49cfe9.png =900x)

 

*	Update the following linked service type properties by parameterizing the **domain** and **workspaceResourceID** as shown below in the same `ARMTemplateForFactory.json` file. Earlier these values were hard-coded within the file thats the reason they are not being updated. If you scroll to the bottom of the json file you can find the linked services portion.
Once the changes are done, you need to commit the file.

 ![factory temp.png](/.attachments/factory%20temp-5820d5c1-c926-4307-8442-c1662dc6079c.png =900x)

*	Update the `ARMTemplateParametersForFactory.json` file by adding the following parameters and then commit the changes. 
![parameters.png](/.attachments/parameters-e0898540-9f9f-402a-888e-cb60f46e466b.png =900x)
 

*	Once the above changes are made, we can create a release pipeline and provision the following change from dev to Prod.