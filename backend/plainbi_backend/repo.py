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
    ]
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