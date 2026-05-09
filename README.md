![](logo_plainbi.PNG)

*open source data platform* for data teams 

includes:
- data portal
- generic CRUD application to edit database tables
- adhoc tool to executes predefined SQL queries
- ... and more to come


# Backend configuration

The backend is configured via environment variables, typically placed in a `.env` file. A custom config file path can be set via `PLAINBI_BACKEND_CONFIG`.

## General

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_BACKEND_CONFIG` | — | Path to a custom `.env` config file. If set, this file is loaded instead of the default search paths (`.env`, `~/.env`, `/etc/plainbi.env`). |
| `PLAINBI_REPOSITORY` | *(required)* | SQLAlchemy connection string for the plainbi repository database (SQLite). The backend exits on startup if this is missing. |
| `PLAINBI_DATABASE` | — | Default datasource connection string. Additional datasources are managed via the repository. |

## Server

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_BACKEND_HOST` | `0.0.0.0` | Host address the API server binds to. |
| `PLAINBI_BACKEND_PORT` | `3001` | TCP port the API server listens on. |

## Logging

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_BACKEND_LOGFILE` | — | Path to a log file. If not set, logs go to stdout only. |
| `PLAINBI_BACKEND_LOG_DEBUG` | `false` | Set to `true` to enable DEBUG-level logging. |
| `PLAINBI_VERBOSE` | — | Integer ≥ 1 enables DEBUG logging and increases internal verbosity. Takes priority over `PLAINBI_BACKEND_LOG_DEBUG`. |

## Metadata cache

plainbi caches table metadata (column names, data types, primary keys) in memory to avoid repeated queries to the database's information schema on every operation.

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_METADATA_CACHE` | `true` | Set to `false` to disable the metadata cache entirely. |
| `PLAINBI_METADATA_CACHE_TTL` | `300` | Cache lifetime in seconds. After expiry the metadata is re-fetched from the database. |

For Snowflake, metadata is fetched via `SHOW COLUMNS` / `SHOW PRIMARY KEYS` (~75ms) instead of `information_schema` (~880ms). If the `SHOW` commands fail for any reason, plainbi falls back to `information_schema` automatically.

## Snowflake connection handling

Snowflake uses JWT-based authentication (private key). JWT tokens expire after ~60 minutes. plainbi handles this transparently:

- A connection pool (`pool_size=5`, `pool_recycle=1800s`) is used for performance — connections are reused within the recycle window.
- If a query fails with a JWT expiry error (Snowflake error `390144` or similar), the connection is immediately invalidated, a fresh connection with a new JWT token is obtained, and the query is retried once — without surfacing an error to the user.
- `CLIENT_SESSION_KEEP_ALIVE=TRUE` in the connection string keeps Snowflake sessions alive during inactivity but does **not** prevent JWT token expiry. The retry mechanism above handles that.

The Snowflake connection string is stored in the `plainbi_datasource` table and typically looks like:

```
snowflake://<user>@<account>/?warehouse=<warehouse>&database=<db>&schema=PUBLIC&role=<role>&authenticator=SNOWFLAKE_JWT&CLIENT_SESSION_KEEP_ALIVE=TRUE&private_key=<key>
```

## Date and time formats

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_BACKEND_DATE_FORMAT` | — | Python `strftime` format string for date values, e.g. `%d.%m.%Y`. If not set, the database default is used. |
| `PLAINBI_BACKEND_DATETIME_FORMAT` | — | Python `strftime` format string for datetime values, e.g. `%d.%m.%Y %H:%M`. If not set, the database default is used. |

## Authentication — LDAP

If `LDAP_HOST` is set, plainbi uses LDAP for user authentication instead of local users.

| Variable | Default | Description |
|---|---|---|
| `LDAP_HOST` | — | LDAP server hostname. Setting this activates LDAP authentication. |
| `LDAP_PORT` | — | LDAP server port (e.g. `389`). |
| `LDAP_BIND_USER_DN` | — | Distinguished name (DN) of the bind user used to search the directory. |
| `LDAP_BIND_USER_PASSWORD` | — | Password of the bind user. |
| `LDAP_BASE_DN` | — | Base DN for user search (e.g. `ou=users,dc=example,dc=com`). |
| `LDAP_SEARCH_EXPR` | — | Custom LDAP search filter. `{username}` is substituted with the login username. Default: `(&(cn={username}))`. |

## Authentication — SSO (Azure AD / Entra ID)

| Variable | Default | Description |
|---|---|---|
| `PLAINBI_SSO_APPLIKATION` | — | Display name of the SSO application. |
| `PLAINBI_SSO_APPLICATION_ID` | — | Azure AD application (client) ID. |
| `PLAINBI_SSO_TENANTID` | — | Azure AD tenant ID. |
| `PLAINBI_SSO_CLIENT_SECRET` | — | Azure AD client secret. |
| `PLAINBI_SSO_AUTHORITY` | — | Authority endpoint, e.g. `https://login.microsoftonline.com/<tenant-id>`. |
| `PLAINBI_SSO_REDIRECT_PATH` | — | Redirect path after successful SSO login, e.g. `/auth/callback`. |

## Email (SMTP)

Used for password-reset and notification features.

| Variable | Default | Description |
|---|---|---|
| `SMTP_SERVER` | — | SMTP server hostname, e.g. `smtp.gmail.com`. |
| `SMTP_PORT` | — | SMTP server port, e.g. `587`. |
| `SMTP_USER` | — | SMTP login username / sender address. |
| `SMTP_PASSWORD` | — | SMTP password. If not set, unauthenticated relay is attempted. |

# CRUD applications

A CRUD application is defined as code. Following syntax is possible: 

```json 
{
   "pages":[
      {
         "id":"1", 
         "name":"<Page name>",
         "alias":"<page_alias>", 
         "allowed_actions":[ 
            "update", "create", "delete", "duplicate", "export_dsdb", "export_excel", "view_calendar"
         ],
         "pk_columns":["<primary_key_column>, ..."], 
         "table":"<table>", 
         "versioned": "true", 
         "table_for_list":"<table>", 
         "sequence":"<sequence>", 
         "hide_in_navigation":"true", 
         "show_breadcrumb":"true", 
         "parent_page": {"alias":"<alias_of_parent_page>","name":"<Label of parent page>"}, 
         "user_column":"<column>",
         "order": [
            {
               "column_name": "<technical_column_name>",
               "direction": "asc|desc"
            },
            {
               "column_name": "<technical_column_name>"
            },
            ...
         ],
         "conditional_row_formats": [
            {
               "column_name":"<technical_column_name>", 
               "operator":"eq|neq|gt|ge|lt|le",
               "value":"<value>",
               "style":{
                  "background-color":"rgb(..., ..., ...)",
                  "...":"..."
               }
            },
            ...
         ],
         "detail_pages": [
            {
               "alias":"<alias_of_detail_page>",
               "fk_column":"<fk_column_in_detail_table>",
               "label":"<Tab label>"
            },
            ...
         ],
         "external_actions": [
            {
               "type": "call_rest_api",
               "id": "1",
               "label": "<Label to show on button>",
               "tooltip": "<just a tooltip to show on button>",
               "method": "POST|GET",
               "contenttype": "application/json",
               "url": "<any endpoint url>",
               "body": "<any payload e.g plain, JSON, etc.",
               "token": "<optional Bearer token, supports ${username} and ${column_name}>",
               "wait_repeat_in_ms": "<ms>",
               "position": "detail|summary"
            },
            {
               "type": "call_stored_procedure", 
               "id": "2",
               "label": "<Label to show on button>",
               "tooltip": "<just a tooltip to show on button>",
               "name": "<name of stored procedure in database including schema e.g. <schema>.<stored_procedure>" ,
               "body": "{\"@param1\":\"value1\", ...}",
               "wait_repeat_in_ms": "<ms>",
               "position": "detail|summary"
            }
         ],
         "table_columns":[ 
            {
               "column_name":"<technical_column_name>",
               "column_label":"<Label to show>",
               "datatype":"text", 
               "ui":"textinput", 
               "lookup":"<lookup_alias>", 
               "multiple":"true", 
               "tooltip":"<just a tooltip>", 
               "editable":"false|true", 
               "required":"false|true", 
               "showdetailsonly":"true", 
               "showsummaryonly":"true",
               "default_value": "<value>",
               "calendar_field": "<column_name>"
            },
            {
               ...
            },
            {
               ...
            }
         ]
      },
      {
         "id":"2",
         "name":"<Page name 2>",
         "alias":"<page_alias>",
         ...
      },
      {
         ...
      }
  ]
}
```

## Page options

## id

Just any numerical value: 1,2,3,...

Has to be unique for all pages.

### name

A nice label for the page :)

### alias

A alias (without spaces and special characters) that is mainly used to identify the page and also used in the URL, so the page can also be adressed directly

## versioned

Treats a table as a versioned table (SCD2) and is able to generate appropriate records.

Following fields are required in such a table:

```sql
last_changed_by varchar(100)
valid_from_dt datetime
invalid_from_dt datetime
last_changed_dt datetime
is_deleted char(1) -- Y/N
is_latest_period char(1) -- Y/N
is_current_and_active char(1) -- Y/N
```

The `last_changed_by` field is filled with the username. So you can track who creates, edits or deletes a record.

### allowed_actions

leave **empty array** if no actions allowed or select between these options (in any combination)

**actions on row level**
- `update`
- `create`
- `delete`
- `duplicate` (same as `create`, but prefills the form with the data of the selected row)
- `export_dsdb` (custom functionality to export a plainbi application or lookup as .dsdb file for [datasqill](https://www.datasqill.de/) used in DevOps scenario (git versioning)

**actions on page level**
- `export_excel` (enable download of the displayed table as Excel file (.xlsx)) 
- `view_calendar` (enable switching between table view and a calendar view - if used, then you have to match the fields of the table to the calendar specific fields: id, title, subtitle, start, end, color, url - see "table_columns" for more information)

### pk_columns

Used for editing and deleting a record - composite key possible: `["primary_key_column1", "primary_key_column2", ...]`
         
### table

The most important option. Defines the table to be used for all CRUD operations (create, read, update, delete).

Has to be the fully qualified name: `<database>.schema.tablename>`

### table_for_list

**optional**: used as an alternative **only** for the tabular view of a page - can be a different table or a view e.g. with labels for ID columns etc.

### sequence

**optional**: sequence to use for the primary key column when adding a new record

### hide_in_navigation

**optional**: hides the page in the side navigation

### show_breadcrumb + parent_page

**optional**: 
- show_breadcrumb: shows a breadcrumb above the page 
- parent_page: refers to the parent page (used for the breadcrumb to show a navigation e.g. "parent page" > "current page") - array of "alias" and "name" of the parent page

### user_column

**optional**: defines which column contains the username and tells plainbi to write the username of the logged in user into this column, when creating or editing a record (insert / update)

### order

**optional**: defines a predefined / default sort order of the data. An array is given with one or more table columns and a sort direction (ascending or descending). The sort direction is optional and defaults to "ascending"

### conditional_row_formats

**optional**: allow to format a row conditionally depending on the value of a column

### table_columns

Array of one or more table columns.

Here following options are possible:

- column_name: just the technical column name
- column_label: a nice label to show
- datatype: allowed values: `text`, `number`, `date`, `datetime`, `boolean`
- ui: allowed values
  - `textinput` (standard single-line text input)
  - `email` (single-line text input, semantically typed as email)
  - `numberinput` (only allows numerical values)
  - `textarea` (multi-line plain text input)
  - `textarea_markdown` (multi-line text input with live Markdown preview)
  - `textarea_sql` (Monaco code editor for SQL — with syntax highlighting and expand/collapse; read-only when `editable` is `false`)
  - `textarea_json` (Monaco code editor for JSON — editable, with syntax highlighting, format and validate buttons, expand/collapse)
  - `textarea_base64` (textarea that displays a base64 encoded image preview underneath)
  - `datepicker` (date picker, stores value as YYYY-MM-DD)
  - `datetimepicker` (date + time picker, stores value as YYYY-MM-DD HH:mm)
  - `switch` (toggle switch, good for boolean values 1/0 or true/false)
  - `label` (shows the value as plain text — not editable)
  - `hidden` (field is not shown in the form at all)
  - `lookup` (dropdown with search/autocompletion — refers to a lookup)
  - `lookupn` (same as lookup, but also allows entering new values not in the list)
  - `password` (text input with masked characters)
  - `password_nomem` (same as password, but prevents browser from saving/autofilling the value)
  - `html` (only used in tabular view — renders raw HTML)
  - `modal_json_to_table` (only used in tabular view — renders a JSON array as a nested table)
- lookup: refers to a lookup with its alias - only used for "ui":"lookup"
- editable: allowed values `false`, `true`
- required: allowed values `false`, `true`
- multiple: **optional**: allows multiple values to be selected - only used for "ui":"lookup"
- tooltip: **optional**: shows a question icon next to the field name and shows a tooltip when hovering - good to use for explanations
- showdetailsonly: allowed value `true`: **optional**: show this field only in detail view (modal dialog)
- showsummaryonly: allowed value `true`: **optional**: show this field only in tabular view
- default_value: set a default value when creating a new data entry
- calendar_field: **optional**: matches the column to a calendar specific field- allowed values: `id`, `title`, `subtitle`, `start`, `end`, `color`, `url` - only used for action "view_calendar"

### detail_pages

**optional**: Enables Master/Detail editing. When a record is opened for editing, the modal shows tabs — "Stammdaten" for the master form plus one tab per detail page.

Each detail page must be defined as a regular page in the same `pages` array (typically with `"hide_in_navigation": true`). The `detail_pages` array just references it by alias and defines the FK mapping:

```json
"detail_pages": [
  {
    "alias": "<alias of the detail page>",
    "fk_column": "<FK column name in the detail table>",
    "label": "<Tab label to display>"
  }
]
```

- `alias`: references an existing page in this application by its alias
- `fk_column`: the column in the detail table that holds the FK value pointing to the master record
- `label`: the tab label shown in the modal

When creating a new detail record from within the master modal, the FK column is automatically pre-filled with the master's primary key value and set to read-only.

**Example** — master page `adhoc` with a detail page `adhoc_berechtigungen`:

```json
{
  "pages": [
    {
      "id": "1", "name": "Adhoc", "alias": "adhoc",
      "table": "db.schema.adhoc", "pk_columns": ["adhoc_id"],
      "allowed_actions": ["update", "create", "delete"],
      "table_columns": [ ... ],
      "detail_pages": [
        { "alias": "adhoc_berechtigungen", "fk_column": "adhoc_id", "label": "Berechtigungen" }
      ]
    },
    {
      "id": "2", "name": "Adhoc Berechtigungen", "alias": "adhoc_berechtigungen",
      "hide_in_navigation": true,
      "table": "db.schema.adhoc_berechtigungen", "pk_columns": ["berechtigung_id"],
      "allowed_actions": ["update", "create", "delete"],
      "table_columns": [
        { "column_name": "berechtigung_id", "column_label": "ID", "ui": "numberinput", "editable": false },
        { "column_name": "adhoc_id", "column_label": "Adhoc ID", "ui": "numberinput", "editable": false },
        { "column_name": "user_name", "column_label": "Benutzer", "ui": "textinput", "editable": true }
      ]
    }
  ]
}
```

### external_actions

Allows the execution of external actions. This can defined per page and each action is offered as a button (next to the "New" button).
Following actions are possible:
- **call of a REST API** (executed by the frontend) 
- **call of a stored procedure** in the source database (executed by the backend) - **only works for MS SQL Server at the moment**

**call of a REST API**

The call only reacts on a positive or negative response and tries to get the error message in case of an error.
But for a REST API call it is not possible to do a further call e.g. if you trigger an async process and want to wait/loop for a final status.

Here following options are available (and all are mandatory if not otherwise mentioned):
- type: allowed value `call_rest_api`
- id: a random unique number
- label: label to show on button
- method: only POST oder GET are supported
- contenttype: any contenttype e.g. "application/json"
- url: any endpoint url - be aware of CORS, because the frontend sends the request - if necessary add a routing (proxy path) to the webserver (e.g. Nginx)
- body: 
  - any payload e.g plain, JSON, etc. 
  - when using double-quote's then please escape them e.g. \\"
  - ${username} is substituted with the logged-in user
  - ${<column_name>} is substituted with the value of the column of a dataset (only works when "position" is set to "detail")
- wait_repeat_in_ms: time to wait in milliseconds, before a repeat of the action is allowed. this prevents an action to be called to often from the user
- **optional** token: Bearer token for authorization. If set, the request includes `Authorization: Bearer <token>`. The `Bearer ` prefix is added automatically if not already present. Supports `${username}` and `${<column_name>}` substitution (column substitution only in detail/modal position). If omitted, no Authorization header is sent.
- **optional** tooltip: a tooltip to show on the button
- **optional** position: detail (show in Modal) or summary (show on Page - is default)

**call of a stored procedure**

Calls the procedure and waits for it to finish with a success or error message.

- type: allowed value `call_stored_procedure`
- id: a random unique number
- label: label to show on button
- name: name of the stored procedure that is being called. fully qualified name with schema.
- body: 
  - used to hand over parameter values
- wait_repeat_in_ms: time to wait in milliseconds, before a repeat of the action is allowed. this prevents an action to be called to often from the user
- **optional** tooltip: a tooltip to show on the button
- **optional** position: detail (show in Modal) or summary (show on Page - is default)


# Adhoc queries

Adhoc queries are predefined SQL statements that users can execute directly from the portal. They are managed in the **Adhoc Konfiguration** application and displayed on the home page for users with access.

## SQL placeholder syntax

Any value can be injected into the SQL at runtime using the `$(placeholder_name)` syntax:

```sql
SELECT *
FROM orders
WHERE customer_id = $(customer_id)
  AND order_date >= $(date_from)
  AND order_date <= $(date_to)
```

The following global placeholder is always available without defining a parameter:

| Placeholder | Value |
|---|---|
| `$(APP_USER)` | Username of the currently logged-in user |

## Parameters

Parameters are defined per adhoc query in the **Adhoc Konfiguration** application under the **Parameter** tab. Each parameter corresponds to one `$(placeholder_name)` in the SQL.

| Field | Description |
|---|---|
| `name` | Display label shown to the user in the input form |
| `name_technical` | Must match the placeholder name in the SQL exactly (without `$()`) |
| `datatype` | Data type: `text`, `number`, `date`, `datetime` |
| `ui` | Input widget: `textinput`, `numberinput`, `datepicker`, `lookup` |
| `lookup` | Lookup alias — only used when `ui` is `lookup` (dropdown with values from a lookup table) |
| `default_value` | Pre-filled value when the form opens. The query runs immediately with this value. |
| `required` | Whether the field must be filled before executing |

When an adhoc has one or more parameters, the user sees an input form above the results. The query is executed automatically on page load using the default values, and can be re-run with different values by clicking **Ausführen**.

**Example** — SQL with two parameters:

```sql
SELECT order_id, customer_name, amount
FROM orders
WHERE status = $(status)
  AND created_by = $(APP_USER)
  AND order_date >= $(date_from)
```

Corresponding parameter definitions:

| name | name_technical | ui | default_value | required |
|---|---|---|---|---|
| Status | status | lookup | open | true |
| Datum ab | date_from | datepicker | | false |

## Human friendly URLs and parameters

Every application and page can be adressed by a well formed and human friendly URL. This is defined by the aliases.

Application:
```
https://<server>/apps/<app_alias>
```

Page within application:
```
https://<server>/apps/<app_alias>/<page_alias>
```

Also by using parameters you can achieve following...

Directly edit a record within a page:
```
https://<server>/apps/<app_alias>/<page_alias>/<id_of_a_record> # if record has 1 pk (primary key field) ... # todo: composite key
```

Filter the tabular view:

```
https://<server>/apps/<app_alias>/<page_alias>?<field>=<value> # field = technical column name
https://<server>/apps/<app_alias>/<page_alias>?<field>=<value>&<field>=<value>&... # also more than 1 field is possible
```

