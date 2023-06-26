# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 11:19:08 2023

@author: kribbel


# login
curl -H "Content-Type: application/json" --request POST --data '{\"username\":\"joe\",\"password\":\"joe123\"}' "localhost:3002/login" -w "%{http_code}\n"
windows comman cmd set tok=ldkasaölsfjaölsdkf

python -m pytest tests\test_version.py

# resource
curl -H "Content-Type: application/json"  -H "Authorization: %tok%" --request GET "localhost:3002/api/repo/resource?order_by=name&offset=1" -w "%{http_code}\n"

# GET ALL
curl -H "Content-Type: application/json"  -H "Authorization: %tok%" --request GET "localhost:3002/api/crud/DWH.analysis.crud_api_testtable?order_by=name&offset=1" -w "%{http_code}\n"
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?order_by=name&offset=1" -w "%{http_code}\n"
# GET
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/1" -w "%{http_code}\n"
# POST
curl -H "Content-Type: application/json" --request POST --data '{\"nr\":\"1\",\"name\":\"name1\",\"dat\":\"2023-04-24\"}' localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable
curl -H "Content-Type: application/json" --request POST --data '{\"nr\":\"2\",\"name\":\"name2\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable?pk=nr&seq=DWH.CONFIG.crud_api_test_seq"
curl -H "Content-Type: application/json" --request POST --data '{\"nr\":\"23\",\"name\":\"wert22\",\"dat\":\"2023-04-20\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable"
# PUT
curl -H "Content-Type: application/json" --request PUT --data '{\"nr\":\"24\",\"name\":\"wert24\",\"dat\":\"2023.04-20\"}' localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/4
# DELETE
curl -H "Content-Type: application/json" --request DELETE localhost:3001/api/crud/DWH.CONFIG.crud_api_testtable/6 -w "%{http_code}\n"
curl -H "Content-Type: application/json" --request DELETE localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/9?pk=nr -w "%{http_code}\n"

# METADATA tables
curl -H "Content-Type: application/json" --request GET localhost:3002/api/metadata/tables -w "%{http_code}\n"

# METADATA
curl -H "Content-Type: application/json" --request GET localhost:3002/api/metadata/table/DWH.CONFIG.crud_api_testtable -w "%{http_code}\n"

#versioned 
# GET
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1" -w "%{http_code}\n"
# POST
curl -H "Content-Type: application/json" --request POST --data '{\"nr\":\"1\",\"name\":\"name1\",\"dat\":\"2023-04-24\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?v&pk=nr"
curl -H "Content-Type: application/json" --request POST --data '{\"nr\":\"2\",\"name\":\"name2\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?v&pk=nr&seq=DWH.CONFIG.crud_api_test_seq"
# PUT
curl -H "Content-Type: application/json" --request PUT --data '{\"nr\":\"1\",\"name\":\"wert1_v2\",\"dat\":\"2023-04-27\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr"
curl -H "Content-Type: application/json" --request PUT --data '{\"nr\":\"1\",\"name\":\"wert1_v3\",\"dat\":\"2023-04-27\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr"
# DELETE
curl -H "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr" -w "%{http_code}\n"

# Repo
curl -H "Content-Type: application/json" --request POST "localhost:3002/api/repo/init_repo" -w "%{http_code}\n"
Latin1_General_100_CS_AS_WS_SC_UTF8
# new application POST
curl -H "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application" -w "%{http_code}\n"
curl -H "Content-Type: application/json" --request POST --data '{\"name\":\"app2\"}' "localhost:3002/api/repo/application"
curl -H "Content-Type: application/json" --request POST --data '{\"name\":\"group1\"}' "localhost:3002/api/repo/group"
curl -H "Content-Type: application/json" --request POST --data '{\"application_id\":\"1\",\"group_id\":\"7\"}' "localhost:3002/api/repo/application_to_group?pk=application_id,group_id"

# GET ALL
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/application?order_by=name&offset=1" -w "%{http_code}\n"
# GET
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/application/5" -w "%{http_code}\n"
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/application/adhoc" -w "%{http_code}\n"
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/application_to_group/(application_id:1:group_id:7)" -w "%{http_code}\n"


# PUT
curl -H "Content-Type: application/json" --request PUT --data '{\"name\":\"app3\"}' localhost:3002/api/repo/application/3
curl -H "Content-Type: application/json" --request PUT --data '{\"id\":\"3\",\"name\":\"app3\"}' localhost:3002/api/repo/application/3
# DELETE
curl -H "Content-Type: application/json" --request DELETE localhost:3002/api/repo/application/5 -w "%{http_code}\n"

# lookup
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/lookup/1" -w "%{http_code}\n"
#adhoc
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/adhoc/1/data?format=XLSX" -w "%{http_code}\n" -o hugo.xlsx
curl -H "Content-Type: application/json" --request GET "localhost:3002/api/repo/adhoc/1/data" -w "%{http_code}\n" -o hugo.csv


curl -H "Content-Type: application/json" --request POST -H "Authorization: %tok%" --data '{\"nr\":\"-8\",\"typ\":\"-2\",\"name\":\"xx\"}' "localhost:3002/api/crud/dwh.analysis.pytest_tv_api_testtable_2pk?v" -w "%{http_code}\n"

"""


import urllib
import logging
import os
import sys
from datetime import date,datetime
import json
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import csv
import pandas as pd
from flask_bcrypt import Bcrypt
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

try:
    import ldap3
except:
    print("LDAP disabled because not installed")

#import bcrypt

from functools import wraps


from flask import Flask, jsonify, request, Response, Blueprint
#from flask.json import JSONEncoder
from json import JSONEncoder
import jwt

from plainbi_backend.utils import db_subs_env, prep_pk_from_url, is_id, last_stmt_has_errors, make_pk_where_clause
from plainbi_backend.db import sql_select, get_item_raw, get_current_timestamp, get_next_seq, get_metadata_raw, repo_lookup_select, repo_adhoc_select, get_repo_adhoc_sql_stmt, db_ins, db_upd, db_del, get_profile, db_connect, add_auth_to_where_clause,db_passwd,db_exec,audit,db_adduser
from plainbi_backend.repo import create_repo_db

from plainbi_backend.config import config,load_pbi_env


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

api = Blueprint('api', __name__)

pbi_env = load_pbi_env()

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(obj, date):
                return obj.strftime("%Y-%m-%d")
            elif isinstance(obj, Exception):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        log.debug("token req")
        token = request.headers.get('Authorization')
        log.debug("token=%s",str(token))

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            tokdata = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
            log.debug("data2=%s",str(tokdata))
            #config.current_user=tokdata['username']
            #log.debug("cur user=%s",str(config.current_user))
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token x'}), 401

        return f(tokdata, *args, **kwargs)

    return decorated

dbengine=None
repoengine=None

repo_table_prefix="plainbi_"

api_root="/api"
api_prefix=api_root+"/crud"
repo_api_prefix=api_root+"/repo"
api_metadata_prefix=api_root+"/metadata"
cursor_desc_fields=["name","type_code","display_size","internal_size","precision","scale","null_ok"]

metadata_tab_query="""
SELECT 
    DB_NAME() AS database_name,
    SCHEMA_NAME(t.schema_id) AS schema_name,
    t.name AS table_name,
    DB_NAME()+'.'+SCHEMA_NAME(t.schema_id)+'.'+t.name AS full_table_name
FROM sys.tables t
ORDER BY database_name, schema_name, table_name
"""

#
@api.route(api_root+'/version', methods=['GET'])
def get_version():
    return config.version

###########################
##
## CRUD
##
###########################


# Define routes for CRUD operations
@api.route(api_prefix+'/<tab>', methods=['GET'])
@token_required
def get_all_items(tokdata,tab):
    """
    Hole (mehrere) Datensätze aus einer Tabelle

    Parameters
    ----------
    tab : Name der Tabelle

    Returns
    -------
    dict mit den keys "data", "columns", "total_count"

    """
    log.debug("++++++++++ entering get_all_items")
    log.debug("get_all_items: param tab is <%s>",str(tab))
    audit(tokdata,request)
    out={}
    is_versioned=False
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,e=sql_select(dbengine,tab,order_by,offset,limit,with_total_count=True,versioned=is_versioned)
    log.debug("get_all_items sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return jsonify(out),500
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    log.debug("leaving get_all_items and return json result")
    log.debug("out=%s",str(out))
    return jsonify(out)

# Define routes for CRUD operations


@api.route(api_prefix+'/<tab>/<pk>', methods=['GET'])
@token_required
def get_item(tokdata,tab,pk):
    """
    Hole einen bestimmten Datensatz aus einer Tabelle

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    
    Url Options:
        pk=

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering get_items")
    log.debug("get_items: param tab is <%s>",str(tab))
    log.debug("get_items: param pk/id is <%s>",str(pk))
    audit(tokdata,request)
    # check options
    out={}
    is_versioned=False
    pkcols=[]
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    log.debug("tab %s pk %s")
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    #
    out=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
    if "data" in out.keys():
        if len(out["data"])>0:
            print("out:"+str(out))
            log.debug("out:%s",str(out))
            log.debug("leaving get_item with success and json result")
            return jsonify(out)
            #return Response(jsonify(out),status=204)
        else:
            log.debug("no record found")
            # return Response(status=204)
            log.debug("leaving get_item with 204 no record forund")
            return ("kein datensatz gefunden",204,"")
    # return (resp.text, resp.status_code, resp.headers.items())
    log.debug("leaving get_item with error 500 and return json result")
    return jsonify(out),500


@api.route(api_prefix+'/<tab>', methods=['POST'])
@token_required
def create_item(tokdata,tab):
    """
    einen neuen Datensatz in einer Tabelle anlegen

    Parameters
    ----------
    tab : Name der Tabelle
    
    Url Options:
        pk=
        seq=  Name der Sequence für den PK, wenn dieser None/Null ist

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering create_item")
    log.debug("create_item: param tab is <%s>",str(tab))
    audit(tokdata,request)
    out={}
    pkcols=[]
    is_versioned=False
    seq=None
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="seq":
                seq=value
                log.debug("pk sequence %s",seq)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    log.debug("create_item tab %s pkcols %s seq %s",tab,pkcols,seq)

    data_bytes = request.get_data()
    log.debug("create_item 7")
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))

    out = db_ins(dbengine,tab,item,pkcols,is_versioned,seq,changed_by=tokdata['username'])
    return jsonify(out)


@api.route(api_prefix+'/<tab>/<pk>', methods=['PUT'])
@token_required
def update_item(tokdata,tab,pk):
    """
    einen bestimmten Datensatz aktualisieren

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    
    Url Options:
        pk=

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering update_item")
    log.debug("update_item: param tab is <%s>",str(tab))
    log.debug("update_item: param pk is <%s>",str(pk))
    audit(tokdata,request)
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    # check pk from compound key 
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           log.debug("pk columns from url form (col:val[:col2:val2...])")
    else:
        log.debug("pk columns explicitly from url parameter")
    #
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    
    out = db_upd(dbengine,tab,pk,item,pkcols,is_versioned,changed_by=tokdata['username'])

    #return 'Item updated successfully', 200
    return jsonify(out)

@api.route(api_prefix+'/<tab>/<pk>', methods=['DELETE'])
@token_required
def delete_item(tokdata,tab,pk):
    """
    einen bestimmten Datensatz löschen

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key) dessen Datensatz gelöscht wird
    
    Url Options:
        pk=
        v -- versioned mode
    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering delete_item")
    log.debug("delete_item: param tab is <%s>",str(tab))
    log.debug("delete_item: param pk is <%s>",str(pk))
    audit(tokdata,request)
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    log.debug("delete_item tab %s pkcols %s ",tab,pkcols)

    pk=prep_pk_from_url(pk)
    log.debug("delete_item tab %s pk %s",tab,pk)
    # check pk from compound key 
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           log.debug("pk columns from url form (col:val[:col2:val2...])")
    else:
        log.debug("pk columns explicitly from url parameter")

    log.debug("############# pk columns for delete is %s",str(pkcols))
    out = db_del(dbengine,tab,pk,pkcols,is_versioned,changed_by=tokdata['username'])
    if isinstance(out,dict):
        if "error" not in out.keys():
            return 'Record deleted successfully', 200
    return jsonify(out)


@api.route(api_metadata_prefix+'/tables', methods=['GET'])
@token_required
def get_metadata_tables(tokdata):
    log.debug("++++++++++ entering get_metadata_tables")
    audit(tokdata,request)
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    out={}
    items,columns,total_count,e=sql_select(dbengine,metadata_tab_query,order_by,offset,limit,with_total_count=False)
    log.debug("get_metadata_tables sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return jsonify(out),500
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    return jsonify(out)

@api.route(api_metadata_prefix+'/table/<tab>', methods=['GET'])
@token_required
def get_metadata_tab_columns(tokdata,tab):
    """
    Metadaten einer Tabelle holen

    Parameters
    ----------
    tab : Name der Tabelle
    
    Url Options:
        pk=
    Returns
    -------

    """
    log.debug("++++++++++ entering get_metadata_tab_columns")
    log.debug("get_metadata_tab_columns: param tab is <%s>",str(tab))
    audit(tokdata,request)
    out={}
    pkcols=None
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    log.debug('get_metadata_tab_columns: for %s',tab)
    try:
        metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    except SQLAlchemyError as e_sqlalchemy:
        last_stmt_has_errors(e_sqlalchemy, out)
        if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
        return jsonify(out),500
    except Exception as e:
        last_stmt_has_errors(e, out)
        return jsonify(out),500
    return jsonify(metadata)

"""
"""

###########################
##
## REPO
##
###########################

# Define routes for CRUD operations
@api.route(repo_api_prefix+'/resources', methods=['GET'])
@token_required
def get_resource(tokdata):
    """
    Hole (mehrere) Datensätze aus dem Repository

    Parameters
    ----------
    tab : Name der Repository Tabelle (ohne plainbi_ prefix)

    Returns
    -------
    dict mit den keys "data", "columns", "total_count"

    """
    log.debug("++++++++++ entering get_resource")
    audit(tokdata,request)
    prof=get_profile(repoengine,tokdata['username'])
    user_id=prof["user_id"]
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("pagination offset=%s limit=%s",offset,limit)
    
    w_app=add_auth_to_where_clause("plainbi_application",None,user_id)
    w_adhoc=add_auth_to_where_clause("plainbi_adhoc",None,user_id)
    w_ext_res=add_auth_to_where_clause("plainbi_external_resource",None,user_id)
    
    resource_sql=f"""select
'application_'||id as id
, name
, '/apps/'||alias as url
, '_self' as target
, null as output_format
, null as description
, null as source
, null as dataset
, 'application' as resource_type
, 'Applikation' as resource_type_de
from plainbi_application pa
{w_app}
union all
select
'adhoc_'||id as id
, name
, '/adhoc/' || id || case when coalesce(output_format, 'HTML') <> 'HTML' then '?format='||output_format else '' end as url
, '_self' as target
, coalesce(output_format, 'HTML') output_format
, null as description
, 'Adhoc' as source
, null as dataset
, 'adhoc' as resource_type
, 'Adhoc' as resource_type_de
from plainbi_adhoc padh
{w_adhoc}
union all
select
'external_resource_'||id as id
, name
, url
, '_blank' as target
, null as output_format
, description
, source
, dataset
, 'external_resource' as resource_type
, 'Extern' as resource_type_de
from plainbi_external_resource per
{w_ext_res}
"""
    items,columns,total_count,e=sql_select(repoengine,resource_sql,order_by,offset,limit,with_total_count=True,is_repo=True,user_id=prof["user_id"])
    log.debug("get_resource sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return jsonify(out),500
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    return jsonify(out)


# Define routes for CRUD operations
@api.route(repo_api_prefix+'/<tab>', methods=['GET'])
@token_required
def get_all_repos(tokdata,tab):
    """
    Hole (mehrere) Datensätze aus dem Repository

    Parameters
    ----------
    tab : Name der Repository Tabelle (ohne plainbi_ prefix)

    Returns
    -------
    dict mit den keys "data", "columns", "total_count"

    """
    log.debug("++++++++++ entering get_all_repos")
    log.debug("get_all_repos: param tab is <%s>",str(tab))
    audit(tokdata,request)
    prof=get_profile(repoengine,tokdata['username'])
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,e=sql_select(repoengine,repo_table_prefix+tab,order_by,offset,limit,with_total_count=True,is_repo=True,user_id=prof["user_id"])
    log.debug("get_all_repos sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return jsonify(out),500
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    return jsonify(out)

# Define routes for CRUD operations


@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['GET'])
@token_required
def get_repo(tokdata,tab,pk):
    """
    Hole einen bestimmten Datensatz aus einer Tabelle

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    
    Url Options:
        pk=

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering get_repo")
    log.debug("get_repo: param tab is <%s>",str(tab))
    log.debug("get_repo: param pk is <%s>",str(pk))
    audit(tokdata,request)
    # check options
    prof=get_profile(repoengine,tokdata['username'])
    pkcols=[]
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    if tab=="application" and (not is_id(pk)):
        # use alias
        out=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=["alias"],is_repo=True,user_id=prof["user_id"])
    else:    
        out=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols,is_repo=True,user_id=prof["user_id"])
    if "data" in out.keys():
        if len(out["data"])>0:
            print("out:"+str(out))
            log.debug("out:%s",str(out))
            return jsonify(out)
            #return Response(jsonify(out),status=204)
        else:
            log.debug("no record found")
            # return Response(status=204)
            return ("kein datensatz gefunden",204,"")
    # return (resp.text, resp.status_code, resp.headers.items())
    return jsonify(out),500


@api.route(repo_api_prefix+'/<tab>', methods=['POST'])
@token_required
def create_repo(tokdata,tab):
    """
    einen neuen Datensatz in einer Tabelle anlegen

    Parameters
    ----------
    tab : Name der Tabelle
    
    Url Options:
        pk=
        seq=  Name der Sequence für den PK, wenn dieser None/Null ist

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering create_repo")
    log.debug("create_repo: param tab is <%s>",str(tab))
    audit(tokdata,request)
    prof=get_profile(repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    log.debug("create_repo: check url params")
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    log.debug("create_repo tab %s pkcols %s",tab,pkcols)

    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    if tab in ["adhoc","application","datasource","external_resource","group","lookup","role","user","group"]:
        seq=tab
    else:
        seq=None
    out = db_ins(repoengine,repo_table_prefix+tab,item,pkcols,is_versioned,seq,is_repo=True)
    return jsonify(out)


@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['PUT'])
@token_required
def update_repo(tokdata,tab,pk):
    """
    einen bestimmten Datensatz aktualisieren

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    
    Url Options:
        pk=

    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering update_repo")
    log.debug("update_repo: param tab is <%s>",str(tab))
    log.debug("update_repo: param pk is <%s>",str(pk))
    audit(tokdata,request)
    prof=get_profile(repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    # check pk from compound key 
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           log.debug("pk columns from url form (col:val[:col2:val2...])")
    else:
        log.debug("pk columns explicitly from url parameter")
    
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))

    out = db_upd(repoengine,repo_table_prefix+tab,pk,item,pkcols,is_versioned,is_repo=True)
    return jsonify(out)


@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['DELETE'])
@token_required
def delete_repo(tokdata,tab,pk):
    """
    einen bestimmten Datensatz löschen

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key) dessen Datensatz gelöscht wird
    
    Url Options:
        pk=
        v -- versioned mode
    Returns
    -------
    dict mit den keys "data"  

    """
    log.debug("++++++++++ entering delete_repo")
    log.debug("delete_repo: param tab is <%s>",str(tab))
    log.debug("delete_repo: param pk is <%s>",str(pk))
    audit(tokdata,request)
    prof=get_profile(repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                log.debug("versions enabled")
    log.debug("delete_item tab %s pkcols %s ",tab,pkcols)

    pk=prep_pk_from_url(pk)
    log.debug("delete_repo tab %s pk %s",tab,pk)
    # check pk from compound key 
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           log.debug("pk columns from url form (col:val[:col2:val2...])")
    else:
        log.debug("pk columns explicitly from url parameter")

    log.debug("############# pk columns for delete is %s",str(pkcols))
    out = db_del(repoengine,repo_table_prefix+tab,pk,pkcols,is_versioned,is_repo=True)
    if isinstance(out,dict):
        if "error" not in out.keys():
            return 'Repo Record deleted successfully', 200
    return jsonify(out)




@api.route(repo_api_prefix+'/init_repo', methods=['POST'])
@token_required
def init_repo(tokdata):
    log.debug("++++++++++ entering init_repo")
    audit(tokdata,request)
    with repoengine.connect() as conn:
        pass
    create_repo_db(repoengine)
    return 'Repo initialized successfully', 200


###########################
##
## Adhoc
##
###########################

"""
GET /api/repo/adhoc/<id>/data	The data of a adhoc (result of its SQL)
GET /api/repo/adhoc/<id>/data?format=XLSX|CSV	The data of a adhoc (result of its SQL), but as a Excel (XLSX) or CSV file
GET /api/repo/lookup/<id>/data
"""
@api.route(repo_api_prefix+'/lookup/<id>/data', methods=['GET'])
@token_required
def get_lookup(tokdata,id):
    log.debug("++++++++++ entering get_lookup")
    log.debug("get_lookup: param id is <%s>",str(id))
    audit(tokdata,request)
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("get_lookup pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,e=repo_lookup_select(repoengine,dbengine,id,order_by,offset,limit,with_total_count=True)
    log.debug("get_lookup sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return jsonify(out),500
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    return jsonify(out)

@api.route(repo_api_prefix+'/adhoc/<id>/data', methods=['GET'])
@token_required
def get_adhoc_data(tokdata,id):
    log.debug("++++++++++ entering get_adhoc_data")
    log.debug("get_adhoc_data: param id is <%s>",str(id))
    audit(tokdata,request,id=str(id))
    out={}
    fmt="JSON"
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="format":
                fmt=value
                log.debug("adhoc format %s",fmt)
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("get_adhoc_data pagination offset=%s limit=%s",offset,limit)
    adhoc_sql, execute_in_repodb = get_repo_adhoc_sql_stmt(repoengine,id)
    if fmt=="JSON":
        if adhoc_sql is None:
            msg="adhoc id/name invalid oder kein sql beim adhoc hinterlegt"
            log.error(msg)
            return msg, 500
        if execute_in_repodb:
            log.debug("adhoc query execution in repodb")
            items, columns = db_exec(repoengine,adhoc_sql)
        else:
            log.debug("adhoc query execution")
            items, columns = db_exec(dbengine,adhoc_sql)
        if not isinstance(items,list):
            return "adhoc json result error",500
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        order_by = request.args.get('order_by')
        log.debug("get_adhoc_data pagination offset=%s limit=%s",offset,limit)
        total_count=len(items)
        out["data"]=items
        out["columns"]=columns
        out["total_count"]=total_count
        return jsonify(out)
    else:
        items, columns=repo_adhoc_select(repoengine,dbengine,id,order_by,offset,limit,with_total_count=True)
        if isinstance(items,list):
            if len(items)==0:
                out["message"] = "adhoc returns no rows"
                return jsonify(out),500
            else:
                df = pd.DataFrame(items, columns=columns)
                # Save the DataFrame to an Excel file
                if fmt=="XLSX":
                    log.debug("adhoc excel")
                    tmpfile='mydata.xlsx'
                    datasheet_name="daten"
                    infosheet_name="info"
                    output = pd.ExcelWriter(tmpfile)
                    df.to_excel(output, index=False, sheet_name=datasheet_name)
                    output.close()
                    # add sheet with sql
                    book = load_workbook(tmpfile)
                    #autofit columns
                    sheet = book[datasheet_name]
                    font = Font(name='Arial', size=9, bold=True, italic=False)
                    for column in sheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(cell.value)
                            except:
                                pass
                        adjusted_width = (max_length + 2) * 1.2  # Zusätzlicher Puffer und Skalierungsfaktor für die Breite
                        sheet.column_dimensions[column_letter].width = adjusted_width
                        sheet[f'{column_letter}1'].font = font

                    # Iterate over each column and set the filter
                    sheet.auto_filter.ref = sheet.dimensions
                    #for col_num in range(1, sheet.max_column + 1):
                    #    column_letter = get_column_letter(col_num)
                    #    column_range = f'{column_letter}1:{column_letter}{sheet.max_row}'
                    #    sheet.auto_filter.ref = column_range
                    # Create a new sheet
                    book.create_sheet(title=infosheet_name)
                    new_sheet = book[infosheet_name]
                    new_sheet['A1'] = "erstellt am:"
                    new_sheet['A2'] = "adhoc:"
                    new_sheet['B1'] = str(datetime.now())
                    new_sheet['B2'] = id
                    #autofit columns
                    for column in new_sheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(cell.value)
                            except:
                                pass
                        adjusted_width = (max_length + 2) * 1.2  # Zusätzlicher Puffer und Skalierungsfaktor für die Breite
                        new_sheet.column_dimensions[column_letter].width = adjusted_width                    
                    # new sql sheet
                    book.create_sheet(title="sql")
                    sql_sheet = book["sql"]
                    sql_sheet.sheet_state = 'hidden'
                    sql_sheet['A1'] = "sql:"
                    sql_sheet['A2'] = adhoc_sql

                    book.save(tmpfile)                    
                    # Return the Excel file as a download
                    with open(tmpfile, 'rb') as file:
                        response = Response(
                            file.read(),
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={'Content-Disposition': 'attachment;filename=mydata.xlsx'}
                        )
                        return response
                elif fmt=="CSV":
                    log.debug("adhoc csv")
                    tmpfile='mydata.csv'
                    # Prepare the CSV file
                    df.to_csv(tmpfile, index=False)
                    # Return the Excel file as a download
                    with open(tmpfile, 'rb') as file:
                        response = Response(
                            file.read(),
                            mimetype='text/csv',
                            headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
                        )
                        return response
                elif fmt=="TXT":
                    log.debug("adhoc txt separated with tabs")
                    tmpfile='mydata.csv'
                    # Prepare the CSV file
                    df.to_csv(tmpfile, index=False, sep='\t', quoting=csv.QUOTE_NONE)
                    # Return the Excel file as a download
                    with open(tmpfile, 'rb') as file:
                        response = Response(
                            file.read(),
                            mimetype='text/csv',
                            headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
                        )
                        return response
                else: 
                    return "adhoc format invalid XLSX/CSV/TXT/JSON", 500
        else:
            out["message"] = "error from adhoc"
            return jsonify(out),500
    return "adhoc error that should not happen", 500


users=dict()

def load_repo_users():
    log.debug("++++++++++ entering load_repo_users")
    global pbi_env,users
    out={}
    plainbi_users,columns,cnt,e=sql_select(repoengine,'plainbi_user')
    if last_stmt_has_errors(e,out):
        log.error('error in select users %s', str(e))
        return False
    users = {u["username"]: u["password_hash"] for u in plainbi_users}
    
def authenticate_local(username,password):
    log.debug("++++++++++ entering authenticate_local")
    global pbi_env,users
    load_repo_users()
    if not username or not password:
        log.error('error invalid cred')
        return False

    p=config.bcrypt.generate_password_hash(password)
    pwd_hashed=p.decode()
    log.debug("login: hashed input pwd is %s",pwd_hashed)
    if username in users.keys():
        if config.bcrypt.check_password_hash(users[username], password):
            log.debug("login: pwd ok")
            return True
    else:
        log.debug("login: user %s is unknown in repo",username)
    log.debug("++++++++++ leaving login")
    return False
    
def authenticate_ldap(username,password):
    log.debug("++++++++++ entering authenticate_ldap")
    global pbi_env,users
    load_repo_users()
    authenticated=False
    s = ldap3.Server(host=pbi_env["LDAP_HOST"], port=int(pbi_env["LDAP_PORT"]), use_ssl=False, get_info=ldap3.ALL)
    conn_bind = ldap3.Connection(s, user=pbi_env["LDAP_BIND_USER_DN"], password=pbi_env["LDAP_BIND_USER_PASSWORD"], auto_bind='NONE', version=3, authentication='SIMPLE')
    if not conn_bind.bind():
        log.error('error in bind %s', str(conn_bind.result))
        log.debug("++++++++++ entering authenticate_ldap with status %s",authenticated)
        return authenticated
    conn_bind.search(pbi_env["LDAP_BASE_DN"], f'(&(cn={username}))', attributes=['*'])
    for entry in conn_bind.entries:
        log.debug("ldap entry=%s",entry.entry_dn)
        conn_auth = ldap3.Connection(s, user=entry.entry_dn, password=password, auto_bind='NONE', version=3, authentication='SIMPLE')
        if not conn_auth.bind():
            log.warning("error in bind ldap entry=%s",entry.entry_dn)
            authenticated=False
        else:
            authenticated=True
            if username not in users.keys():
                log.warning("new user %s from ldap registered",username)
                db_adduser(config.repoengine,username,pwd="x",is_admin=False)
            break
    log.debug("++++++++++ entering authenticate_ldap with status %s",authenticated)
    return authenticated


@api.route('/login', methods=['POST'])
def login():
    log.debug("++++++++++ entering login")
    log.debug("login")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    print("login items ",str(item))

    username = item['username']
    log.debug("login: username=%s",username)
    password = item['password']
    log.debug("login: password=%s",password)
    audit(item['username'],request)

    authenticated = False
    if "LDAP_HOST" in pbi_env.keys():  # if LDAP is defined in config environment
        authenticated = authenticate_ldap(username,password)
        log.debug("login authenticated by ldap = %s",authenticated)
        if not authenticated:
            log.debug("try locally authenticated")
            authenticated = authenticate_local(username,password)
            log.debug("login authenticated local = %s",authenticated)
    else: 
        authenticated = authenticate_local(username,password)
        log.debug("login authenticated local = %s",authenticated)
    if authenticated:
        log.debug("login authenticated")
        token = jwt.encode({'username': username}, config.SECRET_KEY, algorithm='HS256')
        return jsonify({'access_token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@api.route('/passwd', methods=['POST'])
@token_required
def passwd(tokdata):
    out={}
    log.debug("passwd")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    print("passwd items ",str(item))
    prof=get_profile(repoengine,tokdata['username'])
    
    plainbi_users,columns,cnt,e=sql_select(repoengine,'plainbi_user')
    if last_stmt_has_errors(e,out):
        return jsonify({'error': 'Invalid User collecting'}), 500
    users = {u["username"]: u["password_hash"] for u in plainbi_users}
    print(str(users))

    password = item['password']
    log.debug("login: password=%s",password)
    p=config.bcrypt.generate_password_hash(password)
    pwd_hashed=p.decode()
    print(pwd_hashed)
    
    if prof["role"] == "Admin":
        username = item['username']
        log.debug("passwd: username=%s",username)
    else:
        username=prof["username"]
        oldpassword = item['old_password']
        log.debug("login: password=%s",oldpassword)
        if username in users.keys():
            if config.bcrypt.check_password_hash(users[username], oldpassword):
                log.debug("old pwd ok")
                out["message"]="old password does not match"
                return jsonify(out)
    out=db_passwd(repoengine,username,p)
    log.debug("++++++++++ leaving passwd with %s",out)
    return jsonify(out)


@api.route('/hash_passwd/<pwd>', methods=['GET'])
def hash_passwd(pwd):
    out={}
    out["pwd"]=pwd
    #p=config.bcrypt.generate_password_hash(pwd.encode('utf-8'))
    #pwd_hashed=p.decode()
    p=config.bcrypt.generate_password_hash(pwd)
    pwd_hashed=p.decode()
    out["hashed"]=pwd_hashed
    print(pwd_hashed)
    return jsonify(out)

@api.route('/protected', methods=['GET'])
@token_required
def protected(tokdata):
    log.debug("current user=%s",tokdata['username'])
    u=tokdata['username']
    return jsonify({'message': f'Hello, {u}! You are authenticated.'}), 200

@api.route('/profile', methods=['GET'])
@token_required
def profile(tokdata):
    audit(tokdata,request)
    out=get_profile(repoengine,tokdata['username'])
    return jsonify(out)


@api.route('/logout', methods=['GET'])
def logout(tokdata):
    log.debug("logout")
    audit(tokdata,request)
    return jsonify({'message': 'logged out'})


def create_app(config_filename=None,p_repository=None):
    global app, dbengine, repoengine
    app = Flask(__name__)
    #app.config.from_pyfile(config_filename)
    app.json_encoder = CustomJSONEncoder ## wegen jsonify datetimes
    app.register_blueprint(api)
    
    if p_repository is not None:
        repoengine = db_connect(p_repository)
    else:
        repoengine = db_connect(pbi_env["repo_engine"], pbi_env["repo_params"] if "repo_params" in pbi_env.keys() else None)
    log.info("repoengine %s",repoengine.url)
    config.repoengine=repoengine
    log.info("config.repoengine set to %s",repoengine.url)

    dbengine = db_connect(pbi_env["db_engine"], pbi_env["db_params"] if "db_params" in pbi_env.keys() else None)
    log.info("dbengine %s",dbengine.url)

    if "repo_engine" not in pbi_env.keys():
        log.error("repo_engine must be defined")
        sys.exit(1)


    #from yourapplication.model import db
    #db.init_app(app)

    #from yourapplication.views.admin import admin
    #from yourapplication.views.frontend import frontend
    #app.register_blueprint(admin)
    #app.register_blueprint(frontend)

    app.config['JWT_SECRET_KEY'] = config.SECRET_KEY
    config.bcrypt = Bcrypt(app)

    #jwt = JWTManager(app)

    return app

