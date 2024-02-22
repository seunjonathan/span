
[[_TOC_]]

# Introduction

This page will enumerate all resources to be migrated and capture the details of the method of migration for each. For now, the details are captured for the `dev` resource groups. It is expected that the process once known for `dev` would guide the migration of `prod` too.

## Resource Group - `rg-smg-tops-dev`

  Type | Name | How to migrate
---|--|--
microsoft.alertsmanagement/smartDetectorAlertRules|Failure Anomalies|ai-tops-dev|Re-create after move|
Microsoft.DataFactory/factories|adfv2-tops-dev|Use Azure move feature. After moving dependent Databricks reconnect linked service. Possibly need to do that for the storage account and key vault too|
microsoft.insights/components|ai-tops-dev|Re-create after move|
microsoft.insights/scheduledqueryrules|Test_TOPS_Failure_Alert|Re-create after move|
microsoft.insights/scheduledqueryrules|TOPS_PRISM_MISSES_FailureAlert_Dev|Re-create after move|
microsoft.insights/scheduledqueryrules|TOPS_PRISM_STATISTICS_FailureAlert_Dev|Re-create after move|
microsoft.insights/scheduledqueryrules|TOPS_PRISM_TARGETS_FailureAlert_Dev|Re-create after move|

## Resource Group - `rg-smg-towworks-dev`

  Type | Name | How to migrate
---|--|--
microsoft.alertsmanagement/smartDetectorAlertRules|Failure Anomalies - fa-maretron-towworksv2-dev|Re-create after move|
microsoft.alertsmanagement/smartDetectorAlertRules|Failure Anomalies - fa-towworks-migration-test|Re-create after move|
Microsoft.DataFactory/factories|adfv2-towworks-dev|Use Azure move feature. After moving dependent Databricks reconnect linked service. Possibly need to do that for the storage account and key vault too|
microsoft.insights/components|fa-maretron-towworksv2-dev|Delete the resource then re-create it in the new sub with the same name. Upload the code into the new resource and test|
microsoft.insights/scheduledqueryrules|Test_Failure_Alerts|Re-create after move|
microsoft.insights/scheduledqueryrules|Test_Failure_Alerts_PPA|Re-create after move|
Microsoft.Logic/workflows|la-amendppa-dev|?|
Microsoft.Logic/workflows|la-vpamailer-dev|?|
Microsoft.Web/connections|azureblob|This might be a redundant connection|
Microsoft.Web/connections|azureblob-3|This too might be a redundant connection|
Microsoft.Web/connections|office365-2|If this can't be moved, then will have to manually re-enter credentials in Logic app after move|
Microsoft.Web/sites|fa-maretron-towworksv2-dev|Delete the resource then re-create it in the new sub with the same name. Upload the code into the new resource and test|

## Resource Group - `rg-smg-maretron-dev`

  Type | Name | How to migrate
---|--|--
microsoft.alertsmanagement/smartDetectorAlertRules|Failure Anomalies - fa-maretron-v2-dev|Re-create after move|
microsoft.insights/components|fa-maretron-v2-dev|?|
Microsoft.Web/sites|fa-maretron-v2-dev|Delete the resource then re-create it in the new sub with the same name. Upload the code into the new resource and test|
Microsoft.Web/sites|fa-ppa-temp|?|

## Resource Group - `rg-smg-common-dev`

  Type | Name | How to migrate
---|--|--
microsoft.alertsmanagement/smartDetectorAlertRules|Failure Anomalies - parquet2delta|Re-create after move|
Microsoft.Databricks/workspaces|dbw-smg2-dev|Manually re-create|
microsoft.insights/actiongroups|FailureAlert|Re-create after move|
microsoft.insights/actiongroups|Test Failure Alert|Re-create after move|
Microsoft.Insights/components|parquet2delta|?|
Microsoft.KeyVault/vaults|kv-smg-dev|Can be auto moved|
Microsoft.Network/networkIntentPolicies|adb-canadacentral-3359b43a9d16ef87184f6edf|?|
Microsoft.Network/networkIntentPolicies|adb-canadacentral-560105a98e541dd7494770b4|?|
Microsoft.Network/networkIntentPolicies|adb-canadacentral-80c0b6e1090b3890d5adb1b8|?|
Microsoft.Network/networkIntentPolicies|adb-canadacentral-e6a3c9fafc63d1ec2a4dc99c|?|
Microsoft.Network/networkSecurityGroups|databricksnsglbaq6jw2j7swg|Most likely has to be manually recreated after creating new Databricks|
Microsoft.Network/virtualNetworks|vnet-smg-dev|?|
Microsoft.OperationalInsights/workspaces|law-smg-dev|?|
Microsoft.Storage/storageAccounts|adlssmgdev|Has to be moved manually. This will have to be a multi-step process. (a) create a temporary storage account. (b) copy all data to it. (c) delete `adlssmgdev` (d) create `adlssmgdev` in new sub (e) copy data from temp storage into it (f) delete temp account.|
Microsoft.Synapse/workspaces|syn-smg-dev|Must be recreated. The same name cannot be used.|
Microsoft.Web/serverFarms|asp-maretron-v2-dev|?|

## Resource Group - `rg-sfc-beaverlabsapi-dev-canadacentral-001`
  Type | Name | How to migrate
---|--|--
Microsoft.Web/serverFarms|sp-beaverlabsapi-dev|?|
Microsoft.Web/sites|webapp-beaverlabsapi-dev|Most likely has to be manually re-created.|
