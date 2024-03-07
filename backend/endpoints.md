===========
===========
GET /

    just the welcome message to the backend rest server if no specific url is given

===========
GET /api/version
GET /version

    return the version number of the backend

===========
GET /api/dbversion
GET /api/db_version
GET /api/backend_version

    return the database type and version of the backend

===========
GET /api/crud/<db>/<tab>

    get table contents (all rows)

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of database table

    returns json with keys "data", "columns", "total_count"

===========
GET /api/crud/<db>/<tab>/<pk>

    get a specific row from a table given by database tablename and id (or any primary key)

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of database table
    pk : identifier of the row in the table, primary key
         if pk=# : pk is taken request.data
         if more then on column in pk then comma separated
    
    returns jsons with key "data"  

===========
POST /api/crud/<db>/<tab>

    create a new row in the database (insert)

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of database table
    
    Url Options:
        pk=
        seq=  Name der Sequence für den PK, wenn dieser None/Null ist

    returns json mit den keys "data"  i.e. the inserted row (might have new data f.e. sequence values, trigger)

===========
PUT /api/crud/<db>/<tab>/<pk>

    update a row in a table

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of database table
    pk : identifier of the row in the table, primary key
         if pk=# : pk is taken request.data
         if more then on column in pk then comma separated
    
    Url Options:
        pk=
        v .. versioned table

    returns json with key "data"  

===========
DELETE /api/crud/<db>/<tab>/<pk>

    delete a row in a database

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of database table
    pk : Wert des Datensatz Identifier (Primary Key) dessen Datensatz gelöscht wird
    
    Url Options:
        pk=
        v -- versioned mode
    
    returns 200 or json with error msg

===========
GET api_metadata_prefix+/<db>/tables

    get names of all accessible tables in the database

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
   
    returns json with key "data"  

===========
GET api_metadata_prefix+/<db>/table/<tab>

    get metadata of a table from the database dictionary

    Parameters
    ----------
    db: id or alias of the database configured in plainbi_database (id=0 is repository)
    tab : name of the table
    
    returns json with columns and datatypes

===========
GET repo_/api/crud/resources

    get the resource from the repository

    returns json of all applications, adhocs, and external resources

===========
GET repo_/api/crud/<tab>

    get table contents of table <tab> in the repository (table name without prefix plainbi_)

    returns json with keys "data", "columns", "total_count"

===========
GET repo_/api/crud/<tab>/<pk>

    get a specific row from a repository table

    Parameters
    ----------
    tab : repository table name (without prefix plainbi_)
    pk : Primary Key Identifier (Primary Key)
    
    Url Options:
        pk=

    returns json with keys "data"  

===========
POST repo_/api/crud/<tab>

    insert a new row into a repository table 

    Parameters
    ----------
    tab : repository table name (without prefix plainbi_)
    
    Url Options:
        pk=
        seq=  Name of Sequence for PK, in case None/Null is sent

    return json with keys "data" of the newly inserted row

===========
PUT repo_/api/crud/<tab>/<pk>

    update a row in the repository

    Parameters
    ----------
    tab : repository table name (without prefix plainbi_)
    pk : Primary Key Identifier (Primary Key)
    
    Url Options:
        pk=

    returns json with keys "data" of the updated row

===========
DELETE repo_/api/crud/<tab>/<pk>

    delete a row in the repositoy

    Parameters
    ----------
    tab : repository table name (without prefix plainbi_)
    pk : Primary Key Identifier (Primary Key) of the row to be deleted
    
    Url Options:
        pk=

    returns 200 or json of error message

===========
GET repo_/api/crud/init_repo

    initialize the repository: HANDLE WITH CARE and have a backup always

===========
GET repo_/api/crud/lookup/<id>/data

    return then lookup data defined in the lookup repository table with id or alias

===========
GET repo_/api/crud/adhoc/<id>/data

    return then adhoc data defined in the adhoc repository table with id or alias

===========
===========
===========
===========
POST /api/login
POST /login

    authenticate a user - login procedure
    try LDAP first if it is configured (environment variables)
    otherwise of if no success try local authentication

===========
POST /api/passwd
POST /passwd

    change a local users password 

===========
GET /api/hash_passwd/<pwd>
GET /hash_passwd/<pwd>

    just show the hashed password ... mainly for testing reasons

===========
GET /api/cache
GET /cache

    cache handling of metadata, profile
    url params
      on .... enable caching
      off ... disable caching
      clear ... clear caching
      status ... show current cache handling setting

    returns simple string and status 200

===========
GET /api/clear_cache
GET /clear_cache

    clear caching

    returns simple string and status 200

===========
GET /api/protected
GET /protected

    show the own username

===========
GET /api/profile
GET /profile

    return json of the profile of the current user

===========
GET /api/logout
GET /logout

    logout

===========
GET /static/<id>
GET /api/static/<id>

    gets a static base64 thing from the repo by id or alias without login
    useful for logo etc.
    base table is plainbi_static_file

===========
