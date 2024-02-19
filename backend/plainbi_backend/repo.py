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

in WSL:
podman run -dt --name my-postgres -e POSTGRES_PASSWORD=1234 -v "/home/kribbel/postgres_docker:/var/lib/postgresql/data:Z" -p 5432:5432 postgres
podman exec -it my-postgres bash


"""

import os
import hjson
import sqlite3
import time

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from plainbi_backend.db import db_exec,get_db_type,sql_select

import logging
log = logging.getLogger()

"""
import sys
sys.path.insert(0,'C:\\Users\\kribbel\\plainbi\\backend')
import os
from dotenv import load_dotenv


home_directory = os.path.expanduser( '~' )
dotenv_path = os.path.join(home_directory, '.env')
load_dotenv(dotenv_path)

sqlitecon = sqlite3.connect("plainbi_repo.db")
repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")
repoengine = sqlalchemy.create_engine("sqlite:////opt/app/portal/backend/repo.db")

repo_env=""
repo_env="_test"
repo_env="_prod"
repo_server=os.environ.get("repo_server"+repo_env)
repo_username=os.environ.get("repo_username"+repo_env)
repo_password=os.environ.get("repo_password"+repo_env)
repo_database=os.environ.get("repo_database"+repo_env)
repo_engine_str=f"mssql+pymssql://{repo_username}:{repo_password}@{repo_server}/{repo_database}"

from plainbi_backend.db import db_connect
repo_engine=db_connect(repo_engine_str)

"""


def create_repo_db(engine):
    log.debug("+++++++++++ enter create_repo_db")
    repodir=os.path.dirname(__file__)
    dbtyp = get_db_type(engine)
    repo_init_filename=os.path.join(repodir,"repo_init_"+dbtyp+".json")
    log.debug("repo_init_file is %s",repo_init_filename)
    if os.path.isfile(repo_init_filename):
        log.debug("repo_init_file exists - read it")
        with open(repo_init_filename,"r") as f:
            x=f.read()
            sql_create_list=hjson.loads(x, strict=False)
        log.debug("repo_init_file contains %d sql statements",len(sql_create_list))
            
        if dbtyp=="mssql":
            log.debug("--- mssql drop all constraints if there are some")
            sql="SELECT 'ALTER TABLE ' + TABLE_SCHEMA + '.[' + TABLE_NAME + '] DROP CONSTRAINT [' + CONSTRAINT_NAME + ']' as cmd FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_TYPE = 'FOREIGN KEY' AND TABLE_NAME LIKE 'plainbi%' AND CONSTRAINT_NAME LIKE '%FK__%'"
            items,columns=db_exec(engine,sql)
            for i in items:
                print(i["cmd"])
                db_exec(engine,i["cmd"])
            print(str(items))
            log.debug("--- mssql all constraints dropped")
        if dbtyp=="postgres":
            log.debug("--- postgres drop all constraints if there are some")
            sql="SELECT concat('ALTER TABLE ',connamespace::regnamespace,'.',conrelid::regclass,' drop constraint ',conname,' cascade') as cmd, conrelid::regclass AS table_name, connamespace::regnamespace AS schema_name FROM pg_constraint JOIN pg_namespace ON pg_constraint.connamespace = pg_namespace.oid WHERE pg_namespace.nspname = 'plainbi' and pg_constraint.contype='f'"
            items,columns=db_exec(engine,sql)
            for i in items:
                print(i["cmd"])
                db_exec(engine,i["cmd"])
            print(str(items))
            log.debug("--- postgres all constraints dropped")
        if dbtyp=="oracle":
            log.debug("--- mssql drop all constraints if there are some")
            sql="SELECT 'ALTER TABLE '||OWNER||'.'||TABLE_NAME||' DROP CONSTRAINT '||CONSTRAINT_NAME as cmd FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE = 'R' AND TABLE_NAME LIKE 'PLAINBI%'"
            items,columns=db_exec(engine,sql)
            for i in items:
                print(i["cmd"])
                db_exec(engine,i["cmd"])
            print(str(items))
            log.debug("--- oracle all constraints dropped")
        i=0
        log.debug("******************************")
        for sql in sql_create_list[:]:
           i+=1
           log.info("----------------------------------------------------------------------------------------------------")
           log.debug("-- Repo SQL %d" % (i))
           log.info("-- Repo SQL %d" %(i))
           log.info("----------------------------------------------------------------------------------------------------")
           log.info(sql)
           log.info("----------------------------------------------------------------------------------------------------")
           db_exec(engine,sql)
           log.info("----------------------------------------------------------------------------------------------------")
           #time.sleep(1)
        items,columns,total_count,e=sql_select(engine,"select * from plainbi_application",with_total_count=True,is_repo=True)
        log.info("Anzahl Applications %s" % (str(total_count)))
    else:
        log.error("repo_init_file %s does not exist",repo_init_filename)
   
"""
create_repo_db(repoengine)       

import sqlalchemy
#2.-Turn on database engine
repoEngine=sqlalchemy.create_engine('sqlite:////Users/kribbel/plainbi_repo.db.db') # ensure this is the correct path for the sqlite file. 
"""

def create_pytest_tables(engine):
    dbtyp = get_db_type(engine)
    if dbtyp=="mssql":
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
    elif dbtyp=="sqlite":
        t="pytest_api_testtable"
        tv="pytest_tv_api_testtable"
        tvc="pytest_tv_api_testtable_2pk"
        s="no seq in sqlite"
        sql_create_list=[
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