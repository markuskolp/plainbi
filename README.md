![](logo_plainbi.PNG)

*open source data platform* for data teams 

includes:
- data portal
- generic CRUD application to edit database tables
- adhoc tool to executes predefined SQL queries
- ... and more to come


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
            "update", "create", "delete", "duplicate", "export_dsdb", "export_excel"
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
               "default_value": "<value>"
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
  - `textinput`
  - `numberinput` (only allows numerical values)
  - `textarea`
  - `datepicker`
  - `datetimepicker`
  - `switch` (good for boolean values of 1/0)
  - `label` (only shows the value - not editable)
  - `lookup` (refers to a lookup and shows a dropdown with autocompletion)
  - `lookupn` (same, but also allows entering new values)
  - `hidden`
  - `password` (a text field but with asterisks)
  - `password_nomem` (same, but does not allow the browser to memorize/cache the entered value)
  - `html` (only used in tabular view e.g. to represent anly html code)
  - `modal_json_to_table` (only used in tabular view)
  - `textarea_base64` (textarea that displays a base64 encoded string underneath. can be used for images.)
- lookup: refers to a lookup with its alias - only used for "ui":"lookup"
- editable: allowed values `false`, `true`
- required: allowed values `false`, `true`
- multiple: **optional**: allows multiple values to be selected - only used for "ui":"lookup"
- tooltip: **optional**: shows a question icon next to the field name and shows a tooltip when hovering - good to use for explanations
- showdetailsonly: allowed value `true`: **optional**: show this field only in detail view (modal dialog)
- showsummaryonly: allowed value `true`: **optional**: show this field only in tabular view
- default_value: set a default value when creating a new data entry

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
https://<server>/apps/<app_alias>/<page_alias>?<field>=<value>&<field>:<value>&... # also more than 1 field is possible
```

