# -*- coding: utf-8 -*-
"""
Created on Thu May  4 09:39:52 2023

@author: kribbel

/api/repo/<type>


Category	Type	Description
resource	application	CRUD application
resource	adhoc	Adhoc query
resource	external_resource	External resources e.g. of other BI tools. can be used in plainbi to show data assets in other data tools. plainbi lists them with the other resources (application, adhoc) and allows users to see a consolidated view of plainbi resources (internal) and all other data assets (external)
util	lookup	Lookup which is used in a CRUD application
util	datasource	Datasource
security	user	User
security	group	Group / used to define which user is allowed to access which resource (adhoc or application)
security	role	only entries are "Admin" and "User" / is defined initially and hardcoded in source code / NO endpoint for role (as it should not be changed over the API)
security	user_to_group	Security: assign user to a group
security	application_to_group	Security: assign application to a group
security	adhoc_to_group	Security: assign adhoc to a group


URL	Description
GET /api/repo/adhoc/<id>/data	The data of a adhoc (result of its SQL)
GET /api/repo/adhoc/<id>/data?format=XLSX|CSV	The data of a adhoc (result of its SQL), but as a Excel (XLSX) or CSV file
GET /api/repo/lookup/<id>/data	The data of a lookup (result of its SQL)


"""

import sqlite3
import time

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from plainbi_backend.db import db_exec,get_db_type

"""
sqlitecon = sqlite3.connect("plainbi_repo.db")
repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")
repoengine = sqlalchemy.create_engine("sqlite:////opt/app/portal/backend/repo.db")

import sys
sys.path.insert(0,'C:\\Users\\kribbel\\plainbi\\backend')
"""


def create_repo_db(engine):
    dbtyp = get_db_type(engine)
    if dbtyp=="sqlite":
        sql_create_list=[
"""
drop table if exists plainbi_seq
""",
"""
create table plainbi_seq (
  sequence_name text primary key not null  
 ,curval int not null
)
""",
"""
drop table if exists plainbi_role
""",
"""
create table plainbi_role (
  id int primary key not null
 ,name text  -- Admin User
)
""",
"""
INSERT INTO plainbi_role (id,name) VALUES (1,'Admin');
""",
"""
INSERT INTO plainbi_role (id,name) VALUES (2,'User');
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('role',2);
""",

"""
drop table if exists plainbi_user
""",
"""
create table plainbi_user (
  id int primary key not null 
 ,username text
 ,email text
 ,fullname text
 ,password_hash text
 ,role_id int
 ,FOREIGN KEY (role_id) REFERENCES plainbi_role(id)
)
""",
"""
insert into plainbi_user (id,username,password_hash,role_id) values (1,'admin','$2b$12$fb81v4oi7JdcBIofmi/JoeHfAK0WJUo7Mq648C2dAiewztltywHHu',1)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('user',1)
""",
"""
drop table if exists plainbi_group
""",
"""
create table plainbi_group (
  id int primary key not null
 ,name text
 ,alias text
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('group',0)
""",

"""
drop table if exists plainbi_user_to_group
""",
"""
create table plainbi_user_to_group (
  user_id int not null
 ,group_id int not null
 ,primary key (user_id,group_id)
 ,FOREIGN KEY (user_id) REFERENCES plainbi_user(id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",

"""
drop table if exists plainbi_datasource
""",
"""
create table plainbi_datasource (
  id int primary key not null
 ,name text
 ,alias text
 ,db_type text  -- db_types enum mssql,postgres,mysql,oracle,sqllite
 ,db_host text 
 ,db_port text 
 ,db_name text
 ,db_user text
 ,db_pass_hash text
)
""",
"""
insert into plainbi_datasource (id,alias,name) values (0,'repo','internal repository')
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('datasource',0)
""",

"""
drop table if exists plainbi_application
""",
"""
create table plainbi_application(
  id int primary key not null
 ,name text
 ,alias text
 ,spec_json text
 ,datasource_id int
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('application',0)
""",
"""
drop table if exists plainbi_application_to_group
""",
"""
create table plainbi_application_to_group (
  application_id int not null
 ,group_id int not null
 ,primary key (application_id,group_id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",
"""
drop table if exists plainbi_lookup
""",
"""
create table plainbi_lookup (
  id int primary key not null
 ,name text
 ,alias text
 ,sql_query text
 ,datasource_id int
 ,FOREIGN KEY (datasource_id) REFERENCES plainbi_datasource(id)
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('lookup',0)
""",

"""
drop table if exists plainbi_external_resource
""",
"""
create table plainbi_external_resource (
  id int primary key not null
 ,name text
 ,alias text
 ,url text
 ,description text
 ,source text
 ,dataset text
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('external_resource',0)
""",

"""
drop table if exists plainbi_external_resource_to_group
""",
"""
create table plainbi_external_resource_to_group (
  external_resource_id int not null
 ,group_id int
 ,primary key (external_resource_id,group_id)
 ,FOREIGN KEY (external_resource_id) REFERENCES plainbi_external_resource(id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",
"""
drop table if exists plainbi_adhoc
""",
"""
create table plainbi_adhoc (
  id int primary key not null
 ,name varchar
 ,alias text
 ,sql_query varchar
 ,output_format text -- enum outputformats -- HTML Excel CSV
 ,datasource_id int
 ,owner_user_id int
 ,order_by_default varchar
 ,description varchar
 ,FOREIGN KEY (datasource_id) REFERENCES plainbi_datasource(id)
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('adhoc',0)
""",
"""
drop table if exists plainbi_adhoc_to_group
""",
"""
create table plainbi_adhoc_to_group (
  adhoc_id int not null 
 ,group_id int not null
 ,primary key (adhoc_id,group_id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
 ,FOREIGN KEY (adhoc_id) REFERENCES plainbi_adhoc(id)
)
""",
"""
-- application: adhoc, external_resource
INSERT INTO plainbi_application (id,name,alias,spec_json,datasource_id) VALUES
       (-100,'Adhoc Konfiguration','adhoc','{
   "pages":[
{
   "id":"2",
   "name":"Adhoc Konfiguration",
   "alias":"adhoc",
   "pages":[
      {
         "id":"1",
         "name":"Adhocs",
         "alias":"all",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["id"],
         "table":"adhoc",
         "table_columns":[
            {
               "column_name":"id",
               "column_label":"ID",
               "datatype":"number",
               "editable":"false",
               "required":"true"
            },
            {
               "column_name":"name",
               "column_label":"Adhoc Name",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"owner_user_id",
               "column_label":"Besitzer",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"user",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"sql_query",
               "column_label":"SQL Abfrage",
               "datatype":"text",
               "ui":"textarea",
               "editable":"true",
               "required":"true",
               "showdetailsonly":"true"
            },
            {
               "column_name":"output_format",
               "column_label":"Ausgabeformat",
               "ui":"lookup",
               "lookup":"output_format",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            }
         ]
      },
      {
         "id":"2",
         "name":"Berechtigung",
         "alias":"rights",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["adhoc_id","group_id"],
         "table":"adhoc_to_group",
         "table_columns":[
            {
               "column_name":"adhoc_id",
               "column_label":"Adhoc",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"adhoc",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"group_id",
               "column_label":"Gruppe",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"group",
               "editable":"true",
               "required":"true"
            }
         ]
      }
   ]
}',0),
       (-101,'externe Ressourcen','ext_res','{
   "pages":[
      {
         "id":"1",
         "name":"externe Ressourcen",
         "alias":"all",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["id"],
         "table":"external_resource",
         "table_columns":[
            {
               "column_name":"id",
               "column_label":"ID",
               "datatype":"number",
               "editable":"false",
               "required":"true"
            },
            {
               "column_name":"name",
               "column_label":"Name",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"url",
               "column_label":"Aufruf URL",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true",
               "showdetailsonly":"true"
            },
            {
               "column_name":"description",
               "column_label":"Beschreibung",
               "ui":"textarea_markdown",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"source",
               "column_label":"Quelle / System",
               "ui":"textinput",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"dataset",
               "column_label":"Datensatz",
               "ui":"textinput",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            }
         ]
      },
      {
         "id":"2",
         "name":"Berechtigung",
         "alias":"rights",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["external_resource_id","group_id"],
         "table":"external_resource_to_group",
         "table_columns":[
            {
               "column_name":"external_resource_id",
               "column_label":"Ext. Ressource",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"external_resource",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"group_id",
               "column_label":"Gruppe",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"group",
               "editable":"true",
               "required":"true"
            }
         ]
      }
   ]
}',0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-100, 'output_format', 'select ''HTML'' as d, ''HTML'' as r union select ''Excel'' as d, ''XLSX'' as r union select ''CSV'' as d, ''CSV'' as r', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-101, 'datasource', 'select name as d, id as r from plainbi_datasource', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-102, 'db_type', 'select ''SQLite'' as d, ''sqlite'' as r union select ''MS SQL Server'' as d, ''mssql'' as r', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-103, 'user', 'select coalesce(fullname || ''('' || username || '')'', username) as d, id as r from plainbi_user', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-104, 'group', 'select name as d, id as r from plainbi_group', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-105, 'application', 'select name as d, id as r from plainbi_application', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-106, 'role', 'select name as d, id as r from plainbi_role', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-107, 'adhoc', 'select name as d, id as r from plainbi_adhoc', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-108, 'external_resource', 'select name as d, id as r from plainbi_external_resource', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-109, 'username', 'select fullname || ''('' || username || '')'' as d, username as r from plainbi_user where username != ''admin'';', 0);
""",
"""
drop view if exists plainbi_resources;
""",
"""
drop table if exists plainbi_audit
""",
"""
create table plainbi_audit (
  username varchar
 ,t TIMESTAMP
 ,url varchar
 ,id varchar
 ,remark varchar
 ,request_method varchar
 ,request_body varchar
)
""",
"""
DROP VIEW IF EXISTS plainbi_audit_adhoc;
""",
"""
create view plainbi_audit_adhoc
as
select 
coalesce(u.fullname, u.username) as user
, a.t as datum
, a.id as adhoc_id
, pa.name as adhoc_name
, case 
when a.url like '%XLSX' then 'Excel'
when a.url like '%CSV' then 'CSV'
when a.url like '%HTML' then 'HTML'
else 'HTML' 
end as ausgabe_format
from plainbi_audit a, plainbi_user u, plainbi_adhoc pa 
where 1=1
and a.username = u.username
and a.id = pa.id
and url like '%/api/repo/adhoc/%/data%'
order by a.t desc;
""",
"""
drop table if exists plainbi_customsql
""",
"""
create table plainbi_customsql (
  id int primary key not null
 ,alias text
 ,name varchar
 ,sql_query varchar
)
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('customsql',0)
""",
"""
drop table if exists plainbi_adhoc_parameter
""",
"""
CREATE TABLE plainbi_adhoc_parameter (
  id int primary key not null,
  name varchar,
  name_technical varchar,
  adhoc_id int,
  datatype varchar,
  ui varchar,
  lookup varchar,
  default_value varchar,
  required varchar
);
""",
"""
insert into plainbi_seq (sequence_name, curval) values ('adhoc_parameter', 0);
""",
"""
insert into plainbi_lookup (id, name, alias, sql_query, datasource_id) values (-110, null, 'ui_for_parameter', 'select ''textinput'' as r, ''Eingabefeld (Text)'' as d union select ''numberinput'' as r, ''Eingabefeld (Zahl)'' as d union select ''datepicker'' as r, ''Datumsauswahl'' as d union select ''lookup'' as r, ''Lookup'' as d', 0);
""",
"""
insert into plainbi_lookup (id, name, alias, sql_query, datasource_id) values (-111, null, 'lookup_for_parameter', 'select case when name is null then alias else name || '' ('' || alias || '')'' end as d, alias as r from plainbi_lookup', 0);
""",
"""
insert into plainbi_lookup (id, name, alias, sql_query, datasource_id) values (-112, null, 'datatype', 'select ''text'' as r, ''Text'' as d union select ''number'' as r, ''Zahl'' as d union select ''date'' as r, ''Datum'' as d', 0);
""",
    ]
    if dbtyp=="mssql":
        sql_create_list=[
"""
drop table if exists plainbi_role
""",
"""
create table plainbi_role (
  id int primary key not null
 ,name varchar(100)  -- Admin User
)
""",
"""
INSERT INTO plainbi_role (id,name) VALUES (1,'Admin');
""",
"""
INSERT INTO plainbi_role (id,name) VALUES (2,'User');
""",
"""
drop sequence if exists plainbi_role_seq
""",
"""
create sequence plainbi_role_seq start with 3;
""",
"""
drop table if exists plainbi_user
""",
"""
create table plainbi_user (
  id int primary key not null 
 ,username varchar(100)
 ,email varchar(100)
 ,fullname varchar(100)
 ,password_hash varchar(100)
 ,role_id int
 ,FOREIGN KEY (role_id) REFERENCES plainbi_role(id)
)
""",
"""
insert into plainbi_user (id,username,password_hash,role_id) values (1,'admin','$2b$12$fb81v4oi7JdcBIofmi/JoeHfAK0WJUo7Mq648C2dAiewztltywHHu',1)
""",
"""
drop sequence if exists plainbi_user_seq
""",
"""
create sequence plainbi_user_seq start with 2;
""",
"""
drop table if exists plainbi_group
""",
"""
create table plainbi_group (
  id int primary key not null
 ,name varchar(100)
 ,alias varchar(100)
)
""",
"""
drop sequence if exists plainbi_group_seq
""",
"""
create sequence plainbi_group_seq start with 1;
""",
"""
drop table if exists plainbi_user_to_group
""",
"""
create table plainbi_user_to_group (
  user_id int not null
 ,group_id int not null
 ,primary key (user_id,group_id)
 ,FOREIGN KEY (user_id) REFERENCES plainbi_user(id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",
"""
drop table if exists plainbi_datasource
""",
"""
create table plainbi_datasource (
  id int primary key not null
 ,name varchar(100)
 ,alias varchar(100)
 ,db_type varchar(100)  -- db_types enum mssql,postgres,mysql,oracle,sqllite
 ,db_host varchar(100) 
 ,db_port varchar(100) 
 ,db_name varchar(100)
 ,db_user varchar(100)
 ,db_pass_hash varchar(100)
)
""",
"""
insert into plainbi_datasource (id,alias,name) values (0,'repo','internal repository')
""",
"""
drop sequence if exists plainbi_datasource_seq
""",
"""
create sequence plainbi_datasource_seq start with 1;
""",
"""
drop table if exists plainbi_application
""",
"""
create table plainbi_application(
  id int primary key not null
 ,name varchar(100)
 ,alias varchar(100)
 ,spec_json varchar(4000)
 ,datasource_id int
)
""",
"""
drop sequence if exists plainbi_application_seq
""",
"""
create sequence plainbi_application_seq start with 1;
""",
"""
drop table if exists plainbi_application_to_group
""",
"""
create table plainbi_application_to_group (
  application_id int not null
 ,group_id int not null
 ,primary key (application_id,group_id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",
"""
drop table if exists plainbi_lookup
""",
"""
create table plainbi_lookup (
  id int primary key not null
 ,name text
 ,alias text
 ,sql_query text
 ,datasource_id int
 ,FOREIGN KEY (datasource_id) REFERENCES plainbi_datasource(id)
)
""",
"""
drop sequence if exists plainbi_lookup_seq
""",
"""
create sequence plainbi_lookup_seq start with 1;
""",

"""
drop table if exists plainbi_external_resource
""",
"""
create table plainbi_external_resource (
  id int primary key not null
 ,name varchar(100)
 ,alias varchar(100)
 ,url varchar(100)
 ,description varchar(100)
 ,source varchar(100)
 ,dataset varchar(100)
)
""",
"""
drop sequence if exists plainbi_external_resource_seq
""",
"""
create sequence plainbi_external_resource_seq start with 1;
""",

"""
drop table if exists plainbi_external_resource_to_group
""",
"""
create table plainbi_external_resource_to_group (
  external_resource_id int not null
 ,group_id int
 ,primary key (external_resource_id,group_id)
 ,FOREIGN KEY (external_resource_id) REFERENCES plainbi_external_resource(id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
)
""",
"""
drop table if exists plainbi_adhoc
""",
"""
create table plainbi_adhoc (
  id int primary key not null
 ,name varchar(100)
 ,alias varchar(100)
 ,sql_query varchar(4000)
 ,output_format varchar(100) -- enum outputformats -- HTML Excel CSV
 ,datasource_id int
 ,owner_user_id int
 ,order_by_default varchar(1000)
 ,description varchar
 ,FOREIGN KEY (datasource_id) REFERENCES plainbi_datasource(id)
)
""",
"""
drop sequence if exists plainbi_adhoc_seq
""",
"""
create sequence plainbi_adhoc_seq start with 1;
""",
"""
drop table if exists plainbi_adhoc_to_group
""",
"""
create table plainbi_adhoc_to_group (
  adhoc_id int not null 
 ,group_id int not null
 ,primary key (adhoc_id,group_id)
 ,FOREIGN KEY (group_id) REFERENCES plainbi_group(id)
 ,FOREIGN KEY (adhoc_id) REFERENCES plainbi_adhoc(id)
)
""",
"""
-- application: adhoc, external_resource
INSERT INTO plainbi_application (id,name,alias,spec_json,datasource_id) VALUES
       (-100,'Adhoc Konfiguration','adhoc','{
   "pages":[
{
   "id":"2",
   "name":"Adhoc Konfiguration",
   "alias":"adhoc",
   "pages":[
      {
         "id":"1",
         "name":"Adhocs",
         "alias":"all",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["id"],
         "table":"adhoc",
         "table_columns":[
            {
               "column_name":"id",
               "column_label":"ID",
               "datatype":"number",
               "editable":"false",
               "required":"true"
            },
            {
               "column_name":"name",
               "column_label":"Adhoc Name",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"owner_user_id",
               "column_label":"Besitzer",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"user",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"sql_query",
               "column_label":"SQL Abfrage",
               "datatype":"text",
               "ui":"textarea",
               "editable":"true",
               "required":"true",
               "showdetailsonly":"true"
            },
            {
               "column_name":"output_format",
               "column_label":"Ausgabeformat",
               "ui":"lookup",
               "lookup":"output_format",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            }
         ]
      },
      {
         "id":"2",
         "name":"Berechtigung",
         "alias":"rights",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["adhoc_id","group_id"],
         "table":"adhoc_to_group",
         "table_columns":[
            {
               "column_name":"adhoc_id",
               "column_label":"Adhoc",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"adhoc",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"group_id",
               "column_label":"Gruppe",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"group",
               "editable":"true",
               "required":"true"
            }
         ]
      }
   ]
}',0),
       (-101,'externe Ressourcen','ext_res','{
   "pages":[
      {
         "id":"1",
         "name":"externe Ressourcen",
         "alias":"all",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["id"],
         "table":"external_resource",
         "table_columns":[
            {
               "column_name":"id",
               "column_label":"ID",
               "datatype":"number",
               "editable":"false",
               "required":"true"
            },
            {
               "column_name":"name",
               "column_label":"Name",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"url",
               "column_label":"Aufruf URL",
               "datatype":"text",
               "ui":"textinput",
               "editable":"true",
               "required":"true",
               "showdetailsonly":"true"
            },
            {
               "column_name":"description",
               "column_label":"Beschreibung",
               "ui":"textarea_markdown",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"source",
               "column_label":"Quelle / System",
               "ui":"textinput",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"dataset",
               "column_label":"Datensatz",
               "ui":"textinput",
               "datatype":"text",
               "editable":"true",
               "required":"true"
            }
         ]
      },
      {
         "id":"2",
         "name":"Berechtigung",
         "alias":"rights",
         "allowed_actions":[
            "create",
            "update",
            "delete"
         ],
         "datasource":"repo",
         "pk_columns":["external_resource_id","group_id"],
         "table":"external_resource_to_group",
         "table_columns":[
            {
               "column_name":"external_resource_id",
               "column_label":"Ext. Ressource",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"external_resource",
               "editable":"true",
               "required":"true"
            },
            {
               "column_name":"group_id",
               "column_label":"Gruppe",
               "datatype":"number",
               "ui":"lookup",
               "lookup":"group",
               "editable":"true",
               "required":"true"
            }
         ]
      }
   ]
}',0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-100, 'output_format', 'select ''HTML'' as d, ''HTML'' as r union select ''Excel'' as d, ''XLSX'' as r union select ''CSV'' as d, ''CSV'' as r', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-101, 'datasource', 'select name as d, id as r from plainbi_datasource', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-102, 'db_type', 'select ''SQLite'' as d, ''sqlite'' as r union select ''MS SQL Server'' as d, ''mssql'' as r', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-103, 'user', 'select coalesce(fullname || ''('' || username || '')'', username) as d, id as r from plainbi_user', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-104, 'group', 'select name as d, id as r from plainbi_group', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-105, 'application', 'select name as d, id as r from plainbi_application', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-106, 'role', 'select name as d, id as r from plainbi_role', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-107, 'adhoc', 'select name as d, id as r from plainbi_adhoc', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-108, 'external_resource', 'select name as d, id as r from plainbi_external_resource', 0);
""",
"""
insert into plainbi_lookup (id, alias, sql_query , datasource_id ) values (-109, 'username', 'select fullname || ''('' || username || '')'' as d, username as r from plainbi_user where username != ''admin'';', 0);
""",
"""
drop table if exists plainbi_audit
""",
"""
create table plainbi_audit (
  username varchar(100)
 ,t TIMESTAMP
 ,url varchar(250)
 ,id varchar(100)
 ,remark varchar(1000)
 ,request_method varchar(100)
 ,request_body varchar(1000)
)
""",
"""
DROP VIEW IF EXISTS plainbi_audit_adhoc;
""",
"""
create view plainbi_audit_adhoc
as
select 
coalesce(u.fullname, u.username) as user
, a.t as datum
, a.id as adhoc_id
, pa.name as adhoc_name
, case 
when a.url like '%XLSX' then 'Excel'
when a.url like '%CSV' then 'CSV'
when a.url like '%HTML' then 'HTML'
else 'HTML' 
end as ausgabe_format
from plainbi_audit a, plainbi_user u, plainbi_adhoc pa 
where 1=1
and a.username = u.username
and a.id = pa.id
and url like '%/api/repo/adhoc/%/data%'
order by a.t desc;
""",
"""
drop table if exists plainbi_customsql
""",
"""
create table plainbi_customsql (
  id int primary key not null
 ,alias varchar2(100)
 ,name varchar(100)
 ,sql_query varchar(4000)
)
""",
"""
drop sequence if exists plainbi_customsql_seq
""",
"""
create sequence plainbi_customsql_seq start with 1;
""",
    ]

    print("******************************")
    for sql in sql_create_list[:]:
       print(sql)
       db_exec(engine,sql)
       #time.sleep(1)
    #con.close()
   
"""
create_repo_db(repoengine)       

import sqlalchemy
#2.-Turn on database engine
repoEngine=sqlalchemy.create_engine('sqlite:////Users/kribbel/plainbi_repo.db.db') # ensure this is the correct path for the sqlite file. 
"""

def create_pytest_tables(engine):
    t="dwh.analysis.pytest_api_testtable"
    tv="dwh.analysis.pytest_tv_api_testtable"
    tvc="dwh.analysis.pytest_tv_api_testtable_2pk"
    sq="analysis.pytest_seq"
    s="dwh."+sq
    sql_create_list=[
"""
use dwh;
""",
f"""
drop sequence if exists {sq};
""",
f"""
create sequence {sq} start with 0;
""",
f"""
DROP TABLE IF EXISTS {t}
""",
f"""
CREATE TABLE {t} (
    nr int NOT NULL
  , name varchar(200)
  , dat date
  , PRIMARY KEY (nr)
);
""",
f"""
drop table if exists {tv}
""",
f"""
CREATE TABLE {tv} (
    nr int NOT NULL
  , name varchar(200)
  , dat date
  , valid_from_dt datetime NOT NULL
  , invalid_from_dt datetime NOT NULL
  , last_changed_dt datetime NOT NULL
  , is_deleted char(1) NOT NULL
  , is_latest_period char(1) NOT NULL
  , is_current_and_active char(1) NOT NULL
  , last_changed_by varchar(120)
  , PRIMARY KEY (nr, invalid_from_dt)
);
""",
f"""
drop table if exists {tvc}
""",
f"""
CREATE TABLE {tvc} (
    nr int NOT NULL
  , typ int NOT NULL  
  , name varchar(200)
  , valid_from_dt datetime NOT NULL
  , invalid_from_dt datetime NOT NULL
  , last_changed_dt datetime NOT NULL
  , is_deleted char(1) NOT NULL
  , is_latest_period char(1) NOT NULL
  , is_current_and_active char(1) NOT NULL
  , last_changed_by varchar(120)
  , PRIMARY KEY (nr, typ, invalid_from_dt)
)
""",
    ]
    print("******************************")
    for sql in sql_create_list[:]:
       print(sql)
       db_exec(engine,sql)
    return t,tv,s,tvc