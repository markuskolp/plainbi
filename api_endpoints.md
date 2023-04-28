# API endpoints

The application has a REST API running on /api.
Request and response bodies generally use JSON.

## General entry points

|URL|Description|
|-|-|
|/api/repo|plainbi Repository|
|/api/crud|CRUD Applications|
|/api/metadata|Datasource metadata (e.g. of tables)|


## Repository /api/repo

### /api/repo/\<type\>

Following types of repository objects exist:

|Category|Type|Description|
|-|-|-|
|resource|application|CRUD application|
|util|lookup|Lookup which is used in a CRUD application|
|resource|adhoc|Adhoc query|
|util|datasource|Datasource|
|security|user|User|
|security|group|Group / used to define which user is allowed to access which resource (adhoc or application)|
|security|role|only entries are "Admin" and "User" / is defined initially and hardcoded in source code / NO endpoint for role (as it should not be changed over the API) |
|security|user_to_group|Security: assign user to a group|
|security|application_to_group|Security: assign application to a group|
|security|adhoc_to_group|Security: assign adhoc to a group|

The API endpoint for managing the metadata of these objects are identical.
Just replace \<type\> which one of the repository objects above:

|URL|Description|
|-|-|
|GET /api/repo/\<type\>|metadata of ALL \<type\>|
|GET /api/repo/\<type\>/\<id\>|metadata of a specific \<type\>|
|PUT /api/repo/\<type\>/\<id\>|update a \<type\>|
|POST /api/repo/\<type\>|add a \<type\>|
|DELETE /api/repo/\<type\>/\<id\>|delete a \<type\>|

Additionally, following repository objects can deliver data, as they have a sql query definition

|URL|Description|
|-|-|
|GET /api/repo/adhoc/\<id\>/data|The data of a adhoc (result of its SQL)|
|GET /api/repo/adhoc/\<id\>/data?format=XLSX|CSV|The data of a adhoc (result of its SQL), but as a Excel (XLSX) or CSV file|
|GET /api/repo/lookup/\<id\>/data|The data of a lookup (result of its SQL)|

### to be discussed 

- do I need the metadata of an adhoc sql query (to manage the datatypes) ? or is it part of the result "GET /api/repo/adhoc/\<id\>/data" ?
- use \<id\> and other unique, but stable identifier ? e.g. <alias>, <nr>, ...


## CRUD Runtime /api/crud

The CRUD API delivers data for a give table and also allows to edit/update, delete or adding a new entry/row to this table.

|URL|Description|
|-|-|
|GET /api/crud/\<tablename\>|data of table|
|GET /api/crud/\<tablename\>/\<pk\>|data of a table row, defined by the pk (primary key)|
|PUT /api/crud/\<tablename\>/\<pk\>|update a table row, identified by the pk (primary key)|
|POST /api/crud/\<tablename\>|add a table row|
|DELETE /api/crud/\<tablename\>/\<pk\>|delete a table row|

For PUT and DELETE the primary key can also be given in the request body as attributes. This is especially necessary, if the table has a composite primary key. This would be difficult as URL parameter \<pk\>.

### Versioned tables

If the table is versioned, then the parameter "?v" has to be given for all methods (GET, PUT, POST, DELETE).
The versioned table MUST have following columns:

- invalid_from_dt
- valid_from_dt
- last_changed_dt
- is_latest_period
- is_deleted
- is_current_and_active

The backend will take care of versioning each change (PUT, POST, DELETE) the right way.
And the GET method only retrieves the current and active versions.

### additional URL parameters

- POST ?pk=nr&seq=DWH.CONFIG.crud_api_test_seq"
- GET ?order_by=name&offset=3

### to be discussed

- last_changed_by field (to set the user who changed/inserted/deleted the table row) ?
- composite primary key ?
- POST and primary key ? 
  - if no pk is given, backend tries to insert and look for success (e.g. if pk column is autoincrement)
  - sequence: give it as URL parameter or does backend look itself in metadata?


## Datasource metadata (e.g. of tables) /api/metadata

Additionally the metadata of tables can be retrieved.
This is important for the CRUD frontend, as it needs to now about the datatypes, primary keys, etc. of a table that should be administered.

|URL|Description|
|-|-|
|GET /api/metadata/tables|metadata of all available tables|
|GET /api/metadata/table/\<tablename\>|metadata of a specific table|

