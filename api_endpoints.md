# API endpoints

## General entry points

|Entry point|Description|
|-|-|
|/api/adhoc-|
|/api/crud-|
|/api/metadata-|
|/api/repo-|







# Lookups

Lookups are saved in table "plainbi_lookup" with ID and SQL 
SQL has 2 columns: d (display), r (return)

GET /api/lookup/<id>/data    The data of a lookup (result of the its SQL)
GET /api/lookup         metadata of all lookups
GET /api/lookup/<id>    metadata of a specific lookup
PUT /api/lookup/<id>    update a lookup
POST /api/lookup/<id>   add a lookup
DELETE /api/lookup/<id>   delete a lookup

# Applications (runtime)


# Applications (administration)


# Adhoc application 


# Settings

# database connection, etc.
