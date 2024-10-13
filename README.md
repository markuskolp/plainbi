![](logo_plainbi.PNG)

*open source data platform* for data teams 

includes:
- data portal
- generic CRUD application to edit database tables
- adhoc tool to executes predefined SQL queries
- ... and more to come


### CRUD applications

A CRUD application is defined as code. Following syntax is possible: 

```json 
{
   "pages":[
      {
         "id":"1", // just any ID: 1,2,3,... - has to be unique between the pages
         "name":"<Page name>",
         "alias":"<page_alias>", // used for the url
         "versioned": "true", // optional 
         "allowed_actions":[ // optional: leave empty array if no actions allowed or select between these three options (in any combination)
            "update", "create", "delete" 
         ],
         "pk_columns":["<primary_key_column>"], // used for editing and deleting a record - composite key possible: ["primary_key_column1", "primary_key_column2", ...]
         "table":"<table>", // table fully qualified <database.schema.tablename>
         "table_for_list":"<table>", // optional: used as an alternative only for the tabular view of a page - can be a different table or a view e.g. with labels for ID columns etc.
         "sequence":"<sequence>", // optional: sequence to use for the primary key column when adding a new record
         "hide_in_navigation":"true", // optional: hides the page in the side navigation
         "show_breadcrumb":"true", // optional: shows a breadcrumb above the page (use in combination with "parent_page")
         "parent_page": {"alias":"<alias_of_parent_page>","name":"<Label of parent page>"}, // optional: refers to the parent page (used for the breadcrumb to show a navigation e.g. "parent page" > "current page")
         "table_columns":[ // one or more table columns
            {
               "column_name":"<technical_column_name>",
               "column_label":"<Label to show>",
               "datatype":"text", // text, number, date, datetime, boolean
               "ui":"textinput", // textinput, numberinput, textarea, datepicker, datetimepicker, switch, label, lookup, lookupn (lookup + new values), hidden, password, password_nomem (not allowing browser memory), html (only used in tabular view e.g. to represent anly html code), modal_json_to_table (only used in tabular view)
               "lookup":"<lookup_alias>", // only used for "ui":"lookup"
               "multiple":"true", // optional: allows multiple values to be selected - only used for "ui":"lookup"
               "tooltip":"<just a tooltip>", // optional: shows a question icon next to the field name and shows a tooltip when hovering - good to use for explanations
               "editable":"false", // false | true
               "required":"false" // false | true
               "showdetailsonly":"true" // optional: show this field only in detail view (modal dialog)
               "showsummaryonly":"true" // optional: show this field only in tabular view
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
