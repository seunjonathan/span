|||
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|24-January-2024|
|**Technical owner**|-|
|**Business lead**|Yuri Fedoruk|


[[_TOC_]]

# Introduction
This document will provide a high-level guideline on how to use the tag functionality on [Azure DevOps Board](https://dev.azure.com/seaspan-edw/DataOps/_workitems/recentlyupdated/) and a tagging convention to be used when creating a Work Item.



# Tagging Concept

Tagging Work Items help you quickly filter the Product Backlog, Sprint Backlog or run a Work Item query by using different parameters. A tag corresponds to one or two keywords that you define.

## Using the Tag

As seen in the example below, you can create **one or multiple tags** in a single Work Item:

![Multiple tags on ADO example.png](/.attachments/Multiple%20tags%20on%20ADO%20example-b4be661f-e506-4c4f-b9f9-ba534c6bcab2.png)

In this example, the user assigned three tags to this work item: DevOps, SMG, and TowWorks.

### Add, Delete, and Create a Tag

####Add

- Click on the ![image.png](/.attachments/image-dd184c68-5d84-4e49-af3a-7fe0e7900a7f.png) button to add a tag
- A dropdown menu will appear with tag suggestions and you can choose the tag that best  fits with your request.

####Delete
- Click on ![image.png](/.attachments/image-9210b6e8-28bc-4d66-ac83-732b0382890a.png) button to the right of an existing tag to delete it from the Work Item.

####Create
- Click on ![image.png](/.attachments/image-dd184c68-5d84-4e49-af3a-7fe0e7900a7f.png)  button  and the dropdown menu will appear. Type inside the empty field the name of a new that you wish to use.

#Common Use Cases

## `TowWorks`
- Use this tag when the source system associated with the Work Item is **TowWorks**.

## `TowWorksv2`
- Use this tag when the source system associated with the Work Item is **TowWorksv2**.

## `PPA`
- Use this tag when the source system associated with the Work Item is **PPA**.

## `TOPS`
- Use this tag when the source system associated with the Work Item is **TOPS**.

## `ABS`
- Use this tag when the source system associated with the Work Item is **ABS-NS**.

## `DevOps`
- Use this tag when the Work Item is associated with the [Azure DevOps](https://dev.azure.com/seaspan-edw) environment. A feature, or help with a query, are examples of when to use this tag, as seen in Work Item #1846 

## `Infra`
- Use this tag when the Work Item is associated with an infrastructural ask from the [Azure DevOps](https://dev.azure.com/seaspan-edw) environment. Permission or access requests are examples of when to use this tag, as seen in Work Item #1909

## `Blocked`
- Use this tag when the Work Item is blocked and for some reason, the development process cannot continue.

## `Spillover`
- Use this tag when the Work Item is a spillover from the previous Sprint.

