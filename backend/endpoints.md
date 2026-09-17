# Plainbi Backend Endpoints

Route prefixes used below:
- `api_root` = `/api`
- `api_prefix` = `/api/crud`
- `repo_api_prefix` = `/api/repo`
- `api_metadata_prefix` = `/api/metadata`

Most endpoints also exist without the `/api` prefix (e.g. `/version` alongside `/api/version`) — kept for backwards compatibility.

All endpoints except `/login`, `/login_sso`, `GET /api/repo/init_repo`, `GET /api/repo/application/<appid>/dsdb`, `GET /api/repo/lookup/<lkpid>/dsdb`, `GET(/api)/static/<id>` and the `/api/settings*` endpoints require a Bearer token (`@token_required`, obtained via `/login`). All require calls are additionally logged to `plainbi_audit` (`@audited`).

Full interactive docs (Swagger/Flasgger) are generated from the docstrings in `api.py` — this file is a condensed reference.

## Utils / misc

===========
GET /, GET /api

    welcome message

===========
GET /version, GET /api/version

    backend version number

===========
GET /api/backend_version, GET /api/db_version, GET /api/dbversion

    database type and version the backend is connected to

===========
GET /api/loglevel/<loglevel>

    change the runtime log level

===========
GET /status, GET /api/status

    API status/health check

===========
POST /api/email

    send an SMTP email (needs SMTP_SERVER/SMTP_PORT/SMTP_USER/SMTP_PASSWORD env vars, see README.md)

    Body: {"to": "...", "subject": "...", "body": "..."}

===========
GET /api/distinctvalues/<db>/<tabnam>/<colnam>

    distinct values of a column in a table (used for column-filter dropdowns)

    Parameters
    ----------
    db : id or alias of the database configured in plainbi_datasource (0/"repo" = repository)
    tabnam, colnam : table/column name

    Query params
        q       filter substring (LIKE, case-insensitive)
        offset, limit  pagination

    returns json with keys "data", "total_count"

===========
POST /api/exec/<db>/<procname>

    execute a stored procedure — MS SQL Server only

    Body: JSON object of parameter_name: value pairs, embedded directly into the EXEC statement (values are not bound as SQL params — quote string values yourself if needed)

    returns json with keys "data"/"columns" (if the proc returns a resultset) or "message"

## CRUD (api_prefix = /api/crud)

===========
GET /api/crud/<db>/<tab>

    get table contents

    Parameters
    ----------
    db : id or alias of the database configured in plainbi_datasource (0 = repository)
    tab : name of database table

    Query params
        v            versioned mode (only current/active rows)
        cols         comma-separated list of columns to return
        q            filter condition over all columns
        filter       comma-separated column:value filters — "~" = LIKE %value%, "!" = not equal
        offset, limit  pagination
        order_by     order by clause
        customsql    id/alias of a saved SQL in plainbi_customersql, replaces the table
        format       XLSX/CSV/TXT — triggers a file download instead of JSON

    returns json with keys "data", "columns", "total_count"

===========
GET /api/crud/<db>/<tab>/<pk>
POST /api/crud/<db>/<tab>/<pk>

    get a specific row by primary key. The POST variant exists so a composite/complex pk can be sent in the request body instead of the URL (`pk` in the URL is then "#" or "@").

    Parameters
    ----------
    pk : value of the primary key, comma-separated if composite. Can be url-safe-base64-encoded as `[base64@<encoded>]`. "#"/"@" means: take pk from request body (JSON) instead.

    Query params
        pk       explicit pk column name(s), if not derivable from metadata (comma-separated if composite)
        cols     comma-separated list of columns to return
        v        versioned mode
        customsql  id/alias of a saved SQL in plainbi_customersql

    returns json with key "data"; 204 if no record found

===========
POST /api/crud/<db>/<tab>

    insert a new row

    Query params
        v         versioned mode
        pk        explicit pk column name(s) if not derivable from metadata
        seq       name of a DB sequence to generate the new pk value
        usercol   column name to auto-fill with the logged-in username

    Body: JSON object of the new row's column values

    returns json with key "data" — the inserted row (incl. generated pk/trigger values)

===========
PUT /api/crud/<db>/<tab>/<pk>

    update a row

    Parameters/Query params: same pk handling as GET, plus `v`, `usercol`

    Body: JSON object of changed column values

    returns json with key "data"

===========
DELETE /api/crud/<db>/<tab>/<pk>

    delete a row

    Parameters/Query params: same pk handling as GET, plus `v` (versioned = soft delete), `usercol`

    returns 200 ("Record deleted successfully") or json with error msg

## Metadata (api_metadata_prefix = /api/metadata)

===========
GET /api/metadata/<db>/tables

    names of all accessible tables in the database

===========
GET /api/metadata/<db>/table/<tab>

    column metadata (names, datatypes, primary keys) of a table

    Query params
        pk    explicit pk column name(s), if not derivable automatically

## Repository (repo_api_prefix = /api/repo)

The repository holds plainbi's own config tables (`plainbi_*`, without the prefix in `<tab>`).

===========
GET /api/repo/resources

    all applications, adhocs and external resources visible to the current user

===========
GET /api/repo/groups

    the calling user's permission groups

===========
GET /api/repo/group/<gid>/resources

    resources visible to a specific group; `gid` can be "nogroup" for resources not assigned to any group (admins only)

===========
GET /api/repo/<tab>
GET /api/repo/<tab>/<pk>
POST /api/repo/<tab>
PUT /api/repo/<tab>/<pk>
DELETE /api/repo/<tab>/<pk>

    plain CRUD on a repository table (same semantics/params as the `/api/crud/...` endpoints above, `tab` without the `plainbi_` prefix)

===========
GET /api/repo/init_repo

    (re-)initializes the repository schema. **HANDLE WITH CARE — always have a backup.** Not token-protected.

===========
GET /api/repo/lookup/<id>/data

    resolved data of a lookup (id or alias) — used for `ui: lookup`/`lookupn` dropdowns

    Query params
        q, offset, limit, order_by   server-side search/pagination
        selected                     resolve a value outside the current page (e.g. pre-selected value not in the first 50 results)

===========
GET /api/repo/adhoc/<id>/distinctvalues/<colnam>

    distinct values of a column from an adhoc's result set (for its column-filter dropdowns)

    Query params: q, offset, limit (same as /api/distinctvalues)

===========
GET/POST /api/repo/adhoc/<id>/data

    execute an adhoc query (id or alias) and return its result

    Query params
        <name_technical>=value   adhoc parameter values (see README.md "Adhoc queries")
        format        JSON (default) / XLSX / CSV
        offset, limit  pagination
        order_by      order by clause

===========
GET /api/repo/application/<appid>/dsdb
GET /api/repo/lookup/<lkpid>/dsdb

    export an application/lookup as a `.dsdb` file (for datasqill-based DevOps deployment). Not token-protected.

## Authentication

===========
POST /login, POST /api/login

    authenticate with username/password — tries LDAP first if `LDAP_HOST` is configured, falls back to local auth

    Body: {"username": "...", "password": "..."}
    returns {"access_token": "<JWT>", "role": "..."} or 401

===========
POST /login_sso, POST /api/login_sso

    authenticate via Azure AD/Entra ID SSO (authorization code flow), see README.md "Authentication — SSO"

===========
POST /passwd, POST /api/passwd

    change a local user's password

===========
GET /hash_passwd/<pwd>, GET /api/hash_passwd/<pwd>

    show the hash of a password — for testing only

===========
GET /cache, GET /api/cache

    metadata/profile cache handling. Query params (mutually exclusive): `on`, `off`, `clear`, `status`

===========
GET /clear_cache, GET /api/clear_cache

    clear the metadata and profile caches

===========
GET /protected, GET /api/protected

    returns the calling user's username — for testing token validity

===========
GET /profile, GET /api/profile

    the calling user's profile

===========
GET /logout, GET /api/logout

    logout

## Static / settings

===========
GET /api/static/<id>, GET /static/<id>

    a static base64-encoded asset (e.g. a logo) from `plainbi_static_file`, by id or alias. Not token-protected.

===========
GET /api/settings.js

    JS snippet with app title/theme/SSO signin link etc., consumed by the frontend at startup. Not token-protected.

===========
GET /api/settings

    all settings as JSON. Not token-protected.

===========
GET /api/setting/<name>

    a single setting by name. Not token-protected.
