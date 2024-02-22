|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|10-March-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|Yuri Fedoruk|
|**Tickets**| N/A

[[_TOC_]]

# Introduction
To ensure quality and consistency of our technical assets, industry best practices for Agile teams recommend the application of [Definition of Done](https://www.agile-academy.com/en/scrum-master/what-is-the-definition-of-done-dod-in-agile/)(DoD).

A DoD captures the acceptance criteria before a technical asset, such as piece of Python code, a SQL script or any other deployable artifact is deemed complete. Only then would it be permitted for promotion into a production environment. In essence, a DoD is a _checklist_ that is used to confirm that a process has been followed.

This document will propose a DoD for all new work delivered for the Seaspan Marine Group (SMG).

## Proposed DoD Acceptance Criteria

The following are proposed:

# | Criteria | Description
---|---|---
1 | Version Control| All code assets shall be version controlled in Azure DevOps (ADO). This includes Data factory pipelines, Synapse scripts, SQL scripts/stored procedures  and Python/PySpark code.
2 | PR | All changes to an asset shall be performed on a branch other than `prod`, `main` or `master`. Any change to the master branches will be via a Pull Request (PR) in ADO.
3 | Review | All PRs shall be reviewed by at least one other member of the team. Ideally the team lead. Generally the minimum requirement here is that two pairs of eyes have looked at and agreed on the contents and or design.
4 | Coding guidelines | All Python code should adhere to the [Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md).<br> <br>Additionally PySpark code should adhere to the [PySpark Style Guide](https://github.com/palantir/pyspark-style-guide)
5 | Documentation | An ETL solution is not considered complete unless it is accompanied by a __Runbook__. A runbook is intended to cover the design of the solution and help the reader in maintaining the solution and/or troubleshooting problems. An example runbook can be found here [Runbook BeaverLabs API](https://dev.azure.com/seaspan-edw/DataOps/_wiki/wikis/DataOps.wiki/20/Runbook-Beaver-Labs-API)
6 | Unit test | An important aspect of Software and Data Engineering is building good quality code. This means code that is robust and unit tested. Unfortunately, such practices are too often overlooked, leading to problems later downstream. It's well known in the software engineering community that the cost to fix a bug grows exponentially the further downstream it is found. So it pays to catch problems as early as possible. Unit testing is one way to do this.<br><br>For Python/PySpark code, the recommended practice is to develop all code in a local development environment using Visual Studio Code. The project should implement unit tests using the Python [unittest](https://docs.python.org/3/library/unittest.html) framework. An example of PySpark unit tests can be found here [test_get_matching_events_telemetry.py](https://dev.azure.com/seaspan-edw/DataOps/_git/maretron-sparkapp?path=/tests/test_get_matching_events_telemetry.py)<br><br>When it comes to SQL code/scripts, testing practices are less well developed. However, approaches such as those described here are suggested: [SQL unit testing best practices](https://www.sqlshack.com/sql-unit-testing-best-practices/)

## Exceptions
In general, some engineering judgement should be exercised in the application of the DoD. It is understood that in some cases, the acceptance criteria may not be applicable or particularly useful.

* For example, when SQL is used to create a view of an existing table, perhaps with some simple renaming of columns. In such a case, no real value is added by attempting to build unit tests.

* Or for example it is simpler and more expeditious to deliver PySpark code directly in a Databricks notebook, rather than develop it locally.

If appropriate then, it is acceptable to ignore any given DoD criteria. So long as both team members agree to do so during the review.

## Promoting Assets to Production
Upon satisfying the DoD, an asset is now ready for promotion to the production environment. The promotion process will differ according to the type of asset to be promoted. For example deployment of code into a Databricks workspace will differ from how updates to a Data factory pipeline are made.

When completing any substantial promotion, it is recommended to do so in the presence of another team member. It is all too easy to miss a step, or make an error that breaks the production environment or otherwise introduces a problem. Having a second pair of eyes is a good way of avoiding such problems!

While somewhat anecdotal, it is not recommended to promote anything on the last day of the week. Past experience suggests that a bad promotion can lead to bugs or issues that will then persist the entire weekend. Longer possibly if it's a stat. holiday weekend!

## PR Process
The PR or Pull Request process is a quality measure to ensure that technical artifacts are peer reviewed. A pull request is an industry standard part of updating a version controlled code repository. Typically a branch in the repository, e.g. `main` is chosen as the live branch, which is to contain all reviewed and tested code. Any additions to this branch *must* be via a pull request.

### Branching
All changes proposed to the `main` branch are to be performed on a _feature_ branch. It is common for the name of the branch to include the story or task ticket number in it's name. Only once the changes on this branch have met the unit test, documentation, coding guidelines requirements and has been reviewed should the feature branch be merged into the `main` branch.

### Merging
Azure Devops supports creation of Pull Requests. In fact ADO can be configured to police the overall process by preventing, for example, a developer from merging their branch unless the pull request has been approved by one or more reviewers. ADO provides tools for the proposed branch to be compared to the target `main` branch. So that reviewers can easily see the differences/changes proposed. Reviewers can also then leave comments, on a per line basis if necessary against the code.
