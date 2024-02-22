[[_TOC_]]

# Introduction
The purpose of this document is to propose a strategy for authentication and authorization of end users who would like to access Synapse views of the Data Lake.

#Steps
The following are the steps to be followed while creating Restricted Access for a User.

1. Create a login for AD Account
2. Create a user
3. Grant roles (permissions) to the user by creating Role

## 1. Creating a Login for an Active Directory Account
The login here must be one that exists with Active Directory. I.e. `firstname.lastname@seaspan.com` must exist as an identity in AD.
```
use master
CREATE LOGIN [firstname.lastname@seaspan.com] FROM EXTERNAL PROVIDER;
```

## 2. Creating a User from a Login
Users are created in each database that the user is to be permitted to access. Here the `login name` is that used in the `CREATE LOGIN` command from the step 1.
```
use <db-name>
CREATE USER [<user name>] FROM LOGIN [<login name>];
```

## 3. Grant roles (permissions) to the user by creating Role

Create a schema specific custom role for the database to include users 

    IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE 
    name='dbrole_schemaname_reader' AND type = 'R')
    BEGIN 
         CREATE ROLE dbrole_schemaname_reader;
    END

This command will check if there is any existing database role for the same schema and if none exists it will create a new role for the schema.(type='R' checks if it is database Role)

We can grant permission to single/multiple schemas for custom role using:

    -- Grant permission to multiple schemas
    GRANT SELECT ON SCHEMA :: schemaname TO dbrole_schemaname_reader 

Multiple users can be can be granted permission to role using:

    -- Then grant users to this role
    ALTER ROLE dbrole_schemaname_reader ADD MEMBER user1

To Drop a member from role:

    ALTER ROLE dbrole_schemaname_reader DROP MEMBER user1;

By following above steps 1 and 2 a new user will be created for specific database and provided with Reader access by default where as they won't be able to have access for schema. By running step 3 a custom role can be created and user can be assigned Reader  access by default to particular schema to which they will be able to access views.

#Pre-Defined Roles
The following are the pre-defined roles which are automatically allocated to database and are not created manually by us:

|DatabaseRoleName|
|--|
|db_accessadmin|
|db_backupoperator|
|db_datareader|
|db_datawriter|
|db_ddladmin|
|db_denydatareader|
|db_denydatawriter|
|db_owner|
|db_securityadmin|
|public|

These pre-defined roles can be assigned to user for particular database depending upon the access required for the user.

#SSMS Screenshots

##Login Access 

When Login for the database have Owner access they will be able to view, read and edit data in database and able to have access for all schemas and views by default as shown in the image below:

![admin.png](/.attachments/admin-8203a577-84a0-419b-9792-f5b0a50fe82b.png =300x)

In the above image for admin access they are able to view all schemas and views existing in database.

When we are creating restrict access for a user by following steps 1 and 2 as mentioned above, the user will be automatically assigned with pre-defined role of _db_datareader_ by default and by following step 3 and creating a new schema specific role, user will be able to have read access for views of that particular schema.

![user.png](/.attachments/user-a06c18da-6bca-4443-9bad-049e45c08558.png =300x)

In the image above there is small lock icon towards the views which indicates that user have only read access when compared to admin who have the owner access for the database. This read access is by default assigned to user when user is assigned to custom role generated following step 3.

##Access Roles

Admin will have access to view all the Database Roles existing (both pre-defined and custom Database Roles) for the particular database as shown in image below:

![schema admin.png](/.attachments/schema%20admin-d5cbf2ea-91ae-4562-9d17-b89cf2e8aee6.png =200x)

Restricted User/Newly created user will have visibility to all pre-defined Database Roles and assigned custom Database Roles as shown in image below:

![schema user.png](/.attachments/schema%20user-8e30f467-1fb2-4169-a2b4-517b2a4e3e5a.png =200x)

For example, from the above images the admin is able to view a custom Database Role _dbrole_TOPS_ where as user is unable to view the same role as user is not provided access to it and the user is also unable to see data from view of TOPS schema as they are not assigned to that role.

