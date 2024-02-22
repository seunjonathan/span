|Field|Value|
|--|--|
|**Status**|Draft|
|**Version**| v0.1|
|**Date**|18-October-2023|
|**Technical owner**|Sarbjit Sarkaria|
|**Business lead**|NA|
|**Tickets**| #1716

[[_TOC_]]

# Introduction
The purpose of this document is to propose a strategy for authentication and authorization of end users who would like to access Synapse views of the Data Lake.

# Requirements
These are the requirements that we expect to support.
Req. # | Title | Description
--------|---------|------------
1 | `AD User` | All users that have an Azure account shall be authenticated via Active Directory
2 | `Service Principal` | Applications requiring access shall be authenticated using a SQL Account
3 | `Scope` | Granularity of granting access shall be scoped at the level of schema.
4 | `Read only` | All access shall be read only. By design it is not possible to modify contents of externally sourced views or tables. However, account holders shall not be further possible to run database commands that alter configuration such as adding users, granting access etc.
5 | `Full Access` | In some special cases, it shall be possible to grant an account holder access to __all__ databases, schemas, views and tables hosted in Synapse.

# Terminology
Term | Description
-----| --------
`Authentication` | The act of identifying an individual. The person using the system is authenticated as a known entity within the system.
`Authorization` | The act of granting, i.e. authorizing access (or denying access) for a known individual to certain resources within the system.
`SQL Login` | An account identifier used to login to a SQL server. Typically configured on the master database.
`SQL User` | A proxy for a SQL login account. Users can be assigned to a database and granted roles.

## Authentication Options
Option | Description
-----|------
`SQL` | The user is authenticated solely within context of the SQL Server. The user is not known by any external or hosting system, such as Azure Active Directory.
`Active Directory` | SQL Server delegates authentication to Active Directory. In this case, the SQL Server also maintains a login that references the external account.

## Authorization Options
Option | Description
---------|----------------
`Managed Identity` | A Managed Identity (MI) allows one infrastructure component in Azure, e.g. `Synapse` to be given permission to access another e.g. an `Azure Storage Account`. By using MI, a SQL account can be created which delegates authorization to Synapse when accessing underlying storage. This is necessary since a SQL account is otherwise unknown to Azure.
`Azure Security Groups` | Azure security groups provide a mechanism to manage Azure AD accounts that share common access permissions. All accounts using the `Active Directory` authentication option must have a reader permission to the underlying storage account.

# General Strategy
We propose that all end user access will be restricted to requested schemas only. I.e. access to all Synapse views and tables will not be automatically provided, except in special cases. Such cases might be necessary for cross company financial auditing or data science and analytics.

## Mapping of Schemas to Business Areas
Within Seaspan there are three business areas.
1. Seaspan Shipyards (VSY and VSL)
2. Seapsan Ferries Corporation (SFC).
3. Seaspan Marine Corporation (SMC). The tugs business.

The currently known set of schemas and how they relate to these business areas are tabled below.

Business | Related Schemas
--------|---------------
VSL / VSY |`ifs`, `aras`, `cadmatic`, `p6`
SFC | `tops`
SMC | `towworks`, `telem`
general | `intelex`
- | `dbo`

* The `intelex` schema is used to curate health and safety related data and as such does not fall in any one business area.
* The legacy default schema called `dbo` is also currently in use. For tables and views under this schema, permissions will have to be granted more granularly at the view level.

## Accounts for use by Other Applications
End users are not always expected to be humans. In some cases, an application may require access to or integration with one of the data sources provided. One such example is the _eShare_ application in use at VSY. Since login to AD accounts are Multi-Factor based Authentication (MFA), they are unsuitable for integration with 3rd-party applications which typically support only username/password based configuration. In these cases,   support for SQL based logins is necessary. Just like their AD based counter-parts, permission for SQL logins can also be scoped to one or more schemas.

# How to Create a new Account in SQL
There are three steps:
1. Create a login
   * Option A - SQL Account
   * Option B - AD Account
2. Create a user
3. Grant roles (permissions) to the user
## 1. Creating a Login for a SQL Account (option a)
Logins are always created in the master database. The login name is typically a single word.
```
use master
CREATE LOGIN [<login name>] WITH PASSWORD = '<password>';
```

As an example, connecting to the SQL Server via SSMS would look like:

![1.png](/.attachments/1-ec2cd11f-67bb-4ad5-bae5-b4ef23ec9118.png =300x)

## 1. Creating a Login for an Active Directory Account (option b)
The login here must be one that exists with Active Directory. I.e. `firstname.lastname@seaspan.com` must exist as an identity in AD.
```
use master
CREATE LOGIN [firstname.lastname@seaspan.com] FROM EXTERNAL PROVIDER;
```

As an example, connecting to the SQL Server via SSMS would look like:

![2.png](/.attachments/2-24930209-6c39-4c62-9c6a-a66c4d1192c4.png =300x) 

## 2. Creating a User from a Login
Users are created in each database that the user is to be permitted to access. The default schema is typically `dbo`. Here the `login name` is that used in the `CREATE LOGIN` command from the step 1.
```
use <db-name>
CREATE USER [<user name>] FROM LOGIN [<login name>] WITH DEFAULT_SCHEMA=<schema>
```

## 3. Granting SQL Users Access to Selected Schemas
First grant the SQL user access to a schema:
   * The user must be given access to the schema. This is so that once logged into SQL, the user can see the views & tables under that schema within the database. Examples:

      ```
      GRANT SELECT ON SCHEMA :: schema1 TO user1 WITH GRANT OPTION
      GRANT SELECT ON SCHEMA :: schema2 TO user2 WITH GRANT OPTION
      ```

Then user must now be given permission to access the underlying data in the Azure storage account. There are two options. SQL Account and AD Account.

### SQL Account
The Synapse workspace must already be given MI access to the Azure storage account. In addition to this, a MI based credential must be created in the database. Then the user must be given permission to access that credential. Any views created to access underlying data must also use that credential. Here are the steps:

   * Create a DATASOURCE protected by an MI

     ```
     CREATE DATABASE SCOPED CREDENTIAL ManagedIdCredentials
     WITH IDENTITY = 'Managed Identity'

     CREATE EXTERNAL DATA SOURCE ManagedIdDeltaLakeSource
     WITH (
    	LOCATION = 'https://<container>@<storage-account-name>.dfs.core.windows.net/<folder>/<sub-folder etc>', 
    	CREDENTIAL = ManagedIdCredentials
     )

     CREATE OR ALTER VIEW vwTestView
     AS SELECT *
     FROM  
        OPENROWSET(
            BULK '/',
            DATA_SOURCE = 'ManagedIdDeltaLakeSource',
            FORMAT='DELTA'
         ) v
     ```

    * Give access to MI to the user
       ```
       GRANT CONTROL ON DATABASE SCOPED CREDENTIAL ::ManagedIdCredentials TO [<user name>]
       ```

      This is what this looks like.
      ![Synapse Auth and Auth MI.png](/.attachments/Synapse%20Auth%20and%20Auth%20MI-0d9f6ca9-fc46-4772-8e0e-bd2c7faa2401.png =600x)

### AD Account
The Active Directory (AD) Accounts from which logins were created for these users, must be given permission to the underlying storage account. An AD group called `VSY-DataLake-Unrestricted-Reader` has already been created for this and all that is needed is for the accounts to be added as members of this group. 

The diagram below, illustrates what this looks like:
 
   ![3.png](/.attachments/3-35f56150-f7fe-42da-8f7c-51f71fab965e.png =600x)

**Notes**
* While both AD accounts associated with `user1` and `user2` have access to the underlying storage via the Azure portal, the permissions at the SQL level mean that `user1` can only see tables & views within `schema1` and `user2` can only see tables & views in `schema2`.
* The Synapse workspace is always configured with the Azure role `Storage Blob Data Contributor` to the storage account for reasons other than SQL authentication. E.g. in order to support orchestration pipelines that also read and write to the storage account.
* _To be confirmed_: Once a view has been created using an `external datasource` protected by a credential, all  users, be they linked to a SQL account or an AD account, will have to be granted permission to the credential in order to access the data.

# How to Create and Apply Database Roles
Another way of granting users access to view, tables and schemas is via database roles. SQL Server supports a number of built-in roles, such as:
Role | Description
----|-----
`db_admin` | Members of the db_owner fixed database role can perform all configuration and maintenance activities on the database, and can also drop the database in SQL Server. (In SQL Database and Azure Synapse, some maintenance activities require server-level permissions and cannot be performed by db_owners.)
`db_datareader` | 	Members of the db_datareader fixed database role can read all data from all user tables and views. User objects can exist in any schema except sys and INFORMATION_SCHEMA.
`db_datawriter` |Members of the db_datawriter fixed database role can add, delete, or change data in all user tables.
_Ref_: For a complete list of roles see, [Database-level roles](https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver16)

So for example to give permission to `user1` to read access to a database, you would alter the reader role to include the user:

    ALTER ROLE db_datareader ADD MEMBER user1;

You can also create custom roles and then assign users to those roles. E.g.

    CREATE ROLE dbrole_vsy_unrestricted_reader

    -- Grant permission to multiple schemas
    GRANT SELECT ON SCHEMA :: cadmatic TO dbrole_vsy_unrestricted_reader
    GRANT SELECT ON SCHEMA :: aras TO dbrole_vsy_unrestricted_reader

    -- Then grant users to this role
    ALTER ROLE dbrole_vsy_unrestricted_reader ADD MEMBER user1
    ALTER ROLE dbrole_vsy_unrestricted_reader ADD MEMBER user2

## Full Access
In special cases, it might be necessary to grant a user access to all tables, views and schemas exposed in a Synapse. The easiest way to do this is already shown above:

    ALTER ROLE db_datareader ADD MEMBER user1;

Or

    ALTER ROLE db_datareader ADD MEMBER dbrole_vsy_unrestricted_reader;

As such this role should be used only when requested in favour of custom roles that are scoped to a subset of available schemas.

## Denying Access
In some cases it might be necessary to hide certain views from end users.
Use the `DENY` clause to do this. For example:

    DENY SELECT ON [cadmatic].[vw_MODEL-QUERY-FULL-MPV] TO dbrole_vsy_unrestricted_reader


# Helpful Admin Commands

Item # | Command | Description
-------|----------|-----------
1 | `SELECT * FROM sys.database_scoped_credentials` | This will list all `credentials` created by the `CREATE DATABASE SCOPED CREDENTIAL` command
2 | `SELECT * FROM sys.sql_logins`|List all SQL account logins|
3|`SELECT * FROM sys.external_data_sources`| List all external data sources. Use this to see which sources have been set up for access using the `ManagedIdCredentials`
4 |See below|List members of a database role|

     SELECT 
       DP1.name AS DatabaseRoleName,
       isnull (DP2.name, 'No members') AS DatabaseUserName
     FROM sys.database_role_members AS DRM
     RIGHT OUTER JOIN sys.database_principals AS DP1
       ON DRM.role_principal_id = DP1.principal_id
     LEFT OUTER JOIN sys.database_principals AS DP2
       ON DRM.member_principal_id = DP2.principal_id WHERE DP1.type = 'R'
     ORDER BY DP1.name;

Item # | Command | Description
-------|----------|-----------
5 |See below| List permissions on roles
    SELECT DISTINCT rp.name, 
                ObjectType = rp.type_desc, 
                PermissionType = pm.class_desc, 
                pm.permission_name, 
                pm.state_desc, 
                ObjectType = CASE 
                               WHEN obj.type_desc IS NULL 
                                     OR obj.type_desc = 'SYSTEM_TABLE' THEN 
                               pm.class_desc 
                               ELSE obj.type_desc 
                             END, 
                s.Name as SchemaName,
                [ObjectName] = Isnull(ss.name, Object_name(pm.major_id)) 
    FROM   sys.database_principals rp 
       INNER JOIN sys.database_permissions pm 
               ON pm.grantee_principal_id = rp.principal_id 
       LEFT JOIN sys.schemas ss 
              ON pm.major_id = ss.schema_id 
       LEFT JOIN sys.objects obj 
              ON pm.[major_id] = obj.[object_id] 
       LEFT JOIN sys.schemas s
              ON s.schema_id = obj.schema_id
    WHERE  rp.type_desc = 'DATABASE_ROLE' 
       AND pm.class_desc <> 'DATABASE' 
    ORDER  BY rp.name, 
          rp.type_desc, 
          pm.class_desc 


Item # | Command | Description
-------|----------|-----------
6 | `GRANT CONTROL ON DATABASE SCOPED CREDENTIAL ::ManagedIdCredentials TO [role]` | For SQL accounts, it might be necessary to run this command so that the user/role has permission to use the `ManagedIdCredentials`