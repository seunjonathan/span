|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|26-January-2024|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| #3140 <br>


[[_TOC_]]
#Scope
Need to setup an Alert notification whenever there are 3 consecutive failures in the trigger runs of the main pipeline `PL_TOPS_Bronze2Silver` in the production environment using log analytics workspace.
#Steps Followed
*	Go to `Monitor` tab from the azure portal and then click on `Alerts` and then select `Alert rules`.
*	Once you’re on the `Alert rules` tab, choose the option `+ Create` and then create the Alert rule with the name `TOPSv2_Failure_Alert`.
*	Under the `scope` tab of the Alert rule select the resource group as `rg-smg-tops-prod` and then choose the resource type as `Data Factories (V2)` and location as `Canada Central`.
*	Next would be to setup the condition rule on how this Alert should trigger. 
##Steps to be performed in Condition tab
*	In the `Condition` tab, choose the signal type as `Custom Log Search` and then for the **KQL** query to get an alert for the expected scenario as defined in the scope, type in the below **KQL** query in `search query` portion of `Condition` tab
```
ADFPipelineRun
| where TimeGenerated >= ago(3h)
| order by TimeGenerated desc 
| where PipelineName == 'PL_TOPS_Bronze2Silver' and Status == 'Failed' or Status == 'Succeeded'  
| extend prevStatus=prev(Status, 1), prevStatus2=prev(Status, 2)
| where Status == 'Failed' and prevStatus == 'Failed' and prevStatus2 == 'Failed'
```
*	Once the query was added and then we need to state the `aggregation granularity` which is set to **1 hour**. `Aggregation granularity` would focus on how the log data is grouped and summarized for analysis.
*	In the `Alert Logic portion` we need to specify the comparison that needs to be performed on the metrics that we are getting from the query results. I have kept the `Operator` as **Greater than or equal to** and the `Threshold value` to **1** and `frequency of evaluation` to **1 hour**. The reason behind keeping the operator and threshold values to >= 1 is it would check the number of rows returned from the KQL query to be >=1.
*	To summarize the `Alert logic`, this Alert would check the condition specified in the KQL query for  every 1 hour once we create the Alert rule.
##Steps to be performed in Actions tab
*	In the `Actions` tab, I have created an **Action Group** with the name `ag-smg-prod` and have added all the email id’s of the respective individuals that needs to get this Alert and also the MS Teams Channel email address as well.
*	So whenever this Alert rule is fired all the individual part of this Action Group would receive an Alert.

	Once the above steps are performed we can review and save this and then the `TOPSv2_Failure_Alert` rule is created.
