|||
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|06-December-2022|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|


[[_TOC_]]

# Introduction
This document will give a step by step process to write a User Story.

#### What is a User Story?
The User Story should be an informal, general explanation of a "want" written from the perspective of the end user or customer. 

The purpose of the story is to articulate how a "want" will deliver specific value to the customer or end user. This provides context for the requirement which aids in understanding "why" the requirement is needed. 

The recommended approach is to write the story from the perspective of a user or _persona_ which involves the following steps:

    1. Define the end user or persona
    2. Specify what the user or persona wants
    3. Describe the intended benefit or value
    4. Describe the acceptance criteria for the user story

* **A good template for step 1 would be**:
   
       “As a [persona], I [want to], [so that].”

   * “As a **_persona_**":
Who are we building this for? Our team should have a shared understanding of who the persona is. We’ve hopefully interviewed them. We understand how that person works, how they think and what they feel. We have empathy for them.
   * **_Wants to_**:
Here we are describing their intent — not the features they use. What is it they are actually trying to achieve? This statement should be implementation free.
   * **_So that_**:
How does their immediate desire to do something this fit into their bigger picture? What’s the overall benefit they’re trying to achieve? What is the big problem that needs solving?

  The story only needs to describe _what_ needs to be done, not the _how_. The implementation details or the _how_ are captured later in separate `Task` type tickets. Which will be associated with the story ticket.

* **What is an Acceptance Criteria**?

  The acceptance criteria is where the abstract becomes tangible or is materialized through actual examples – metrics, pictures, and reference material should also be added to this section by clicking on the ![Attach.png](/.attachments/Attach-4b8e21a4-f768-429d-bc5b-564d436c087b.png) icon.

Typically, in Agile, this would be a _How to Demonstrate_ section. In Azure Devops, the story ticket form/template has a specific area for this, not suprisingly called `Acceptance Criteria`. This is where the acceptance criteria should be written. 


#Let's Jump Into It
## Login into Devops

Please use below URL to login

https://dev.azure.com/seaspan-edw/SMG-DataOps

## Please follow the steps below:

![5.png](/.attachments/5-b8887c7a-0a58-42f7-9e89-7265b89d4f2b.png)

On the left navigation pane, hover over **Boards**.

![6.png](/.attachments/6-f1f16250-3ab6-4a92-99ba-b910e627733d.png)

Select the **Work Items** option.

![7.png](/.attachments/7-cfcd2eab-027e-415e-934c-9f52a677d78e.png)

Select **New Work Item** and select the Work Item you wish to create - in general, they would be either User Stories or Bugs.

![8.png](/.attachments/8-93a4d412-9168-48c8-9297-0954dc15448e.png)

You don't need to assign a developer now, unless you are sure of that information.  

You can either place your Work Item in the Backlog or a specific Sprint by clicking and selecting this action on the _Iteration_ field.

Write out your User Story _Description_ and _Acceptance Criteria_.

![3.png](/.attachments/3-bec6dd2c-2c10-40a8-8e47-ecaaf6c569d0.png)

Use the _Planning_ field to rate your User Story with an adequate number of Story Points, and the _Priority_ field to attribute an urgency rating to your Work Item. The _Priority_ should be assigned based on the following scale:

* **Priority 1** - immediately urgent and should be worked on before all other stories, this priority should be reserved for stories that require immediate attention who's delay could cause immediate issues/complications.
* **Priority 2** - Standard work to be completed within a sprint, the majority of stories should fall into this category.
* **Priority 3** - Additional work to be completed within sprint but considered to be lower priority, if spillover is going to occur within a sprint these stories are the first to be delayed to the following sprint.
* **Priority 4** - Low priority work that exists as optional or _“bonus"_ features and improvements to be brought into the sprint when the development team are under loaded for a sprint.

To assess the Story Points rating, you can user the following matrix: 

![Matrix.png](/.attachments/Matrix-30c31e4c-e55a-4553-a27e-ec71acf5bcf7.png)

Don't forget to **Tag** your User Story. The **Tags** are very important for us to filter, and query the Work Items and tp capture metadata that will inform the reports and dashboards for the Data and Digital Enablement team - we have a wiki exclusively set for purpose of [tagging Work Items on ADO](https://dev.azure.com/seaspan-edw/SMG-DataOps/_wiki/wikis/SMG-DataOps.wiki/191/How-to-Use-the-Tagging-Feature-on-ADO).


## Following a User Story

After you have created your User Story, you can follow it by clicking on the ![Follow.png](/.attachments/Follow-90a4a617-b685-481a-a01e-6bbf37011d3d.png) button. Once you start following a Work Item, you will receive an alert in your email whenever a change is to it.



# Examples of User Stories for Reference:
The following are a few samples illustrating how to write good user stories :

1.   #1846

2.   #1715
    
3.   #1639
     