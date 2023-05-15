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

sqlitecon = sqlite3.connect("plainbi_repo.db")

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

"""
repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")
"""


def create_repo_db(engine):
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
INSERT INTO plainbi_role (id,name) VALUES (1,'Admin')
""",
"""
INSERT INTO plainbi_role (id,name) VALUES (2,'User')
""",
"""
insert into plainbi_seq (sequence_name,curval) values ('role',2)
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
insert into plainbi_seq (sequence_name,curval) values ('user',0)
""",

"""
drop table if exists plainbi_group
""",
"""
create table plainbi_group (
  id int primary key not null
 ,name text
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
 ,db_type text  -- db_types enum mssql,postgres,mysql,oracle,sqllite
 ,db_host text 
 ,db_port text 
 ,db_name text
 ,db_user text
 ,db_pass_hash text
)
""",
"""
insert into plainbi_datasource (id,name) values (0,'internal repository')
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
 ,sql_query varchar
 ,output_format text -- enum outputformats -- HTML Excel CSV
 ,datasource_id int
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
               "column_name":"sql_query",
               "column_label":"SQL Abfrage",
               "datatype":"text",
               "ui":"textarea_sql",
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
      }
   ]
}',0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-100, 'output_format', 'select ''HTML'' as d, ''HTML'' as r union select ''Excel'' as d, ''XLSX'' as r union select ''CSV'' as d, ''CSV'' as r', 0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-101, 'datasource', 'select name as d, id as r from plainbi_datasource', 0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-102, 'db_type', 'select ''SQLite'' as d, ''sqlite'' as r union select ''MS SQL Server'' as d, ''mssql'' as r', 0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-103, 'user', 'select fullname as d, id as r from plainbi_user', 0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-104, 'group', 'select name as d, id as r from plainbi_group', 0);
""",
"""
insert into plainbi_lookup (id, name, sql_query , datasource_id ) values (-105, 'application', 'select name as d, id as r from plainbi_application', 0);
""",
"""
create view plainbi_resources
as
select 
      id, name
      , '/apps/'||alias as url
      , '_self' as target
      , null as output_format 
      , null as description
      , null as source
      , null as dataset
      , 'application' as resource_type
      , 'Applikation' as resource_type_de 
from plainbi_application pa 
union all
select 
      id, name
      , '/adhoc/' || id || case when coalesce(output_format, 'HTML') <> 'HTML' then '?format='||output_format else '' end as url
      , '_self' as target
      , coalesce(output_format, 'HTML') output_format
      , null as description
      , 'Adhoc' as source
      , null as dataset
      , 'adhoc' as resource_type
      , 'Adhoc' as resource_type_de 
from plainbi_adhoc padh 
union all
select 
      id, name
      , url
      , '_blank' as target
      , null as output_format 
      , description
      , source
      , dataset
      , 'external_resource' as resource_type
      , 'Extern' as resource_type_de 
from plainbi_external_resource per 
""",
    ]
    print("******************************")
    for sql in sql_create_list[:]:
       print(sql)
       engine.execute(sql)
    #con.close()
   
"""
create_repo_db(repoengine)       

import sqlalchemy
#2.-Turn on database engine
repoEngine=sqlalchemy.create_engine('sqlite:////Users/kribbel/plainbi_repo.db.db') # ensure this is the correct path for the sqlite file. 
"""