# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 11:19:08 2023

@author: kribbel

http://localhost:3001/api/crud/ANALYSIS.guest.testtable
http://localhost:3001/api/crud/mm_dwh_dev.dds.par_mailing_list
http://172.27.10.165:3001/api/crud/mm_dwh_dev.dds.par_mailing_list
http://localhost:3001/api/crud/ANALYSIS.guest.testtable/1
http://localhost:3001/api/crud/ANALYSIS.guest.testtable/metadata
http://localhost:3001/testpost
# GET ALL
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable?order_by=name&offset=1" -w "%{http_code}\n"
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?order_by=name&offset=1" -w "%{http_code}\n"
# GET
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/1" -w "%{http_code}\n"
# POST
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"1\",\"name\":\"name1\",\"dat\":\"2023-04-24\"}' localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"2\",\"name\":\"name2\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable?pk=nr&seq=DWH.CONFIG.crud_api_test_seq"
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"23\",\"name\":\"wert22\",\"dat\":\"2023-04-20\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable"
# PUT
curl --header "Content-Type: application/json" --request PUT --data '{\"nr\":\"24\",\"name\":\"wert24\",\"dat\":\"2023.04-20\"}' localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/4
# DELETE
curl --header "Content-Type: application/json" --request DELETE localhost:3001/api/crud/DWH.CONFIG.crud_api_testtable/6 -w "%{http_code}\n"
curl --header "Content-Type: application/json" --request DELETE localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable/9?pk=nr -w "%{http_code}\n"

# METADATA tables
curl --header "Content-Type: application/json" --request GET localhost:3002/api/metadata/tables -w "%{http_code}\n"

# METADATA
curl --header "Content-Type: application/json" --request GET localhost:3002/api/metadata/table/DWH.CONFIG.crud_api_testtable -w "%{http_code}\n"

#versioned 
# GET
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1" -w "%{http_code}\n"
# POST
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"1\",\"name\":\"name1\",\"dat\":\"2023-04-24\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?v&pk=nr"
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"2\",\"name\":\"name2\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable?v&pk=nr&seq=DWH.CONFIG.crud_api_test_seq"
# PUT
curl --header "Content-Type: application/json" --request PUT --data '{\"nr\":\"1\",\"name\":\"wert1_v2\",\"dat\":\"2023-04-27\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr"
curl --header "Content-Type: application/json" --request PUT --data '{\"nr\":\"1\",\"name\":\"wert1_v3\",\"dat\":\"2023-04-27\"}' "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr"
# DELETE
curl --header "Content-Type: application/json" --request DELETE "localhost:3002/api/crud/DWH.CONFIG.crud_api_tv_testtable/1?v&pk=nr" -w "%{http_code}\n"

# Repo
curl --header "Content-Type: application/json" --request POST "localhost:3002/api/repo/init_repo" -w "%{http_code}\n"
Latin1_General_100_CS_AS_WS_SC_UTF8
# new application POST
curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"testapp\"}' "localhost:3002/api/repo/application"
curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"app2\"}' "localhost:3002/api/repo/application"
curl --header "Content-Type: application/json" --request POST --data '{\"name\":\"group1\"}' "localhost:3002/api/repo/group"
curl --header "Content-Type: application/json" --request POST --data '{\"application_id\":\"1\",\"group_id\":\"7\"}' "localhost:3002/api/repo/application_to_group?pk=application_id,group_id"

# GET ALL
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/application?order_by=name&offset=1" -w "%{http_code}\n"
# GET
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/application/5" -w "%{http_code}\n"
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/application_to_group/(application_id:1:group_id:7)" -w "%{http_code}\n"


# PUT
curl --header "Content-Type: application/json" --request PUT --data '{\"name\":\"app3\"}' localhost:3002/api/repo/application/3
curl --header "Content-Type: application/json" --request PUT --data '{\"id\":\"3\",\"name\":\"app3\"}' localhost:3002/api/repo/application/3
# DELETE
curl --header "Content-Type: application/json" --request DELETE localhost:3002/api/repo/application/5 -w "%{http_code}\n"

# lookup
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/lookup/1" -w "%{http_code}\n"
#adhoc
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/adhoc/1/data?format=XLSX" -w "%{http_code}\n" -o hugo.xlsx
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/repo/adhoc/1/data" -w "%{http_code}\n" -o hugo.csv

"""


import argparse
import urllib
import logging
from sys import platform
import os
import sys
from datetime import date,datetime
import json
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, jsonify, request, Response
from flask.json import JSONEncoder
from dotenv import load_dotenv
import csv
import pandas as pd
from io import StringIO
from plainbi_backend.utils import db_subs_env, is_id,prep_pk_from_url
from plainbi_backend.db import sql_select, get_item_raw, get_current_timestamp, get_next_seq, get_metadata_raw, repo_lookup_select, repo_adhoc_select, get_repo_adhoc_sql_stmt
from plainbi_backend.repo import create_repo_db

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(obj, date):
                return obj.strftime("%Y-%m-%d")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

home_directory = os.path.expanduser( '~' )
dotenv_path = os.path.join(home_directory, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

log=app.logger
log.setLevel(logging.DEBUG)

pbi_env={}
pbi_env["db_server"] = os.environ.get("db_server")
pbi_env["db_username"] = os.environ.get("db_username")
pbi_env["db_password"] = os.environ.get("db_password")
pbi_env["db_database"] = os.environ.get("db_database")


v = os.environ.get("db_params")
if v is not None:
    pbi_env["db_params"] = v
    pbi_env["db_params"] = db_subs_env(pbi_env["db_params"],pbi_env) 
    print("pbi_env",str(pbi_env))

pbi_env["db_engine"] = os.environ.get("db_engine")
pbi_env["db_engine"] = db_subs_env(pbi_env["db_engine"],pbi_env) 

if "db_engine" not in pbi_env.keys():
    log.error("db_engine must be defined")
    sys.exit(1)

if "db_params" in pbi_env.keys():
    params = urllib.parse.quote_plus(pbi_env["db_params"])
    print("params",params)
    print("db_engine",pbi_env["db_engine"])
    dbengine = sqlalchemy.create_engine(pbi_env["db_engine"] % params)
else:
    dbengine = sqlalchemy.create_engine(pbi_env["db_engine"])
log.info("dbengine %s",dbengine.url)


# repo connection
pbi_env["repo_server"] = os.environ.get("repo_server")
pbi_env["repo_username"] = os.environ.get("repo_username")
pbi_env["repo_password"] = os.environ.get("repo_password")
pbi_env["repo_database"] = os.environ.get("repo_database")

v = os.environ.get("repo_params")
if v is not None:
    pbi_env["repo_params"] = v
    pbi_env["repo_params"] = db_subs_env(pbi_env["repo_params"],pbi_env) 
    print("pbi_env",str(pbi_env))

pbi_env["repo_engine"] = os.environ.get("repo_engine")
pbi_env["repo_engine"] = db_subs_env(pbi_env["repo_engine"],pbi_env) 

if "repo_engine" not in pbi_env.keys():
    log.error("repo_engine must be defined")
    sys.exit(1)

if "repo_params" in pbi_env.keys():
    params = urllib.parse.quote_plus(pbi_env["repo_params"])
    print("repo params",params)
    print("repo_engine",pbi_env["repo_engine"])
    repoengine = sqlalchemy.create_engine(pbi_env["repo_engine"] % params)
else:
    repoengine = sqlalchemy.create_engine(pbi_env["repo_engine"])
log.info("repoengine %s",repoengine.url)
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

###########################
##
## CRUD
##
###########################


# Define routes for CRUD operations
@app.route(api_prefix+'/<tab>', methods=['GET'])
def get_all_items(tab):
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
    items,columns,total_count,msg=sql_select(dbengine,tab,order_by,offset,limit,with_total_count=True,versioned=is_versioned)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    if columns is None:  # keine Spalten
        log.debug("get_all_items: return with error 500 because no columns selected")
        return msg, 500
    else:
        log.debug("leaving get_all_items and return json result")
        log.debug("out=%s",str(out))
        return jsonify(out)

# Define routes for CRUD operations


@app.route(api_prefix+'/<tab>/<pk>', methods=['GET'])
def get_item(tab,pk):
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
    return (jsonify(out),500)


@app.route(api_prefix+'/<tab>', methods=['POST'])
def create_item(tab):
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
    metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    log.debug("create_item %s pkcols2 %s",tab,pkcols)
    log.debug("in create_item (pos)")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    s=None
    if is_versioned:
        ts=get_current_timestamp(dbengine)
        print(ts)
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
        if "valid_from_dt" not in collist:
            collist.append("valid_from_dt")
            vallist.append(ts)
        else:
            vallist[collist.index("valid_from_dt")]=ts
        if "invalid_from_dt" not in collist:
            collist.append("invalid_from_dt")
            vallist.append("9999-12-31 00:00:00")
        else:
            vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        if "last_changed_dt" not in collist:
            collist.append("last_changed_dt")
            vallist.append(ts)
        else:
            vallist[collist.index("last_changed_dt")]=ts
        if "is_latest_period" not in collist:
            collist.append("is_latest_period")
            vallist.append("Y")
        else:
            vallist[collist.index("is_latest_period")]="Y"
        if "is_deleted" not in collist:
            collist.append("is_deleted")
            vallist.append("N")
        else:
            vallist[collist.index("is_deleted")]="N"
        if "is_current_and_active" not in collist:
            collist.append("is_current_and_active")
            vallist.append("Y")
        else:
            vallist[collist.index("is_current_and_active")]="Y"
    else:
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
    try:
        qlist=["?" for k in vallist]
        if seq is not None:
            if len(pkcols)>1:
                out["errors"]="mehr als eine PK Spalte bei angegeben sequence nicht erlaubt"
                return (jsonify(out),500)
            s=get_next_seq(dbengine,seq)
            log.debug("got seq %d ",s)
            vallist[collist.index(pkcols[0])]=s
            log.debug("seqence %s inserted",seq)
        else:
            s=vallist[collist.index(pkcols[0])]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        dbengine.execute(sql,tuple(vallist))
        #cursor = cnxn.cursor()
        #cursor.execute(sql,val_tuple)
        #cnxn.commit()
        out["status"]="ok"
        #return 'Item created successfully', 201
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        out["errors"]="create_item:sqlalchemy:"+error
        return (jsonify(out),500)
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}    
        else:
           estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}    
        out["errors"]="create_item:exception:"+estruc
        return (jsonify(out),500)
    # read new record from database and send it back
    out=get_item_raw(dbengine,tab,s,pk_column_list=pkcols)
    return jsonify(out)


@app.route(api_prefix+'/<tab>/<pk>', methods=['PUT'])
def update_item(tab,pk):
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
    #
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    log.debug("item-keys %s",item.keys())
    metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")

    if pkcols[0] not in item.keys():
        out["errors"]="PK Spalte muss beim Update (PUT) in den request daten sein"
        return (jsonify(out),500)

    chkout=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["errors"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
            return (jsonify(out),500)
    else:
        out["errors"]="PK check nicht erfolgreich"
        return (jsonify(out),500)

    pkexp=[k+"=?" for k in pkcols]
    pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)

    log.debug("pk_columns %s",pkcols)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbengine)
        # hole then alten Datensatz aus der DB mit dem angegebenen pk
        cur_row=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        vallist=[]
        vallist.append(ts)
        vallist.append(ts)
        vallist.append(pk)
        val_tuple=tuple(vallist)
        sql=f"UPDATE {tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' WHERE {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
        dbengine.execute(sql,val_tuple)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        rec=reclist[0]
        collist=[k for k in rec.keys()]
        vallist=[v for v in rec.values()]
        # überschreibe mit neuen werten
        for k,v in item.items():
            log.debug("-> %s %s",k,v)
            pos=collist.index(k)
            if pos>=0:
                log.debug("overwrite: %s %s",k,v)
                vallist[pos]=v
        vallist[collist.index("valid_from_dt")]=ts
        vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        vallist[collist.index("last_changed_dt")]=ts
        vallist[collist.index("is_latest_period")]='Y'
        vallist[collist.index("is_current_and_active")]='Y'
        qlist=["?" for k in rec.keys()]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        dbengine.execute(sql,tuple(vallist))
    else:
        # nicht versionierter Standardfall
        othercols=[col for col in item.keys() if col not in pkcols]
        log.debug("othercols %s",othercols)
        osetexp=[k+"=?" for k in othercols]
        osetexp_str=",".join(osetexp)
    
        vallist=[item[col] for col in item.keys() if col not in pkcols]
        vallist.append(pk)
        val_tuple=tuple(vallist)
        
        sql=f"UPDATE {tab} SET {osetexp_str} WHERE {pkwhere}"
        log.debug("update item sql %s",sql)
        dbengine.execute(sql,val_tuple)
    # den aktuellen Datensatz wieder aus der DB holen und zurückgeben (könnte ja Triggers geben)
    out=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
    #return 'Item updated successfully', 200
    return jsonify(out)

@app.route(api_prefix+'/<tab>/<pk>', methods=['DELETE'])
def delete_item(tab,pk):
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
    # check options
    out={}
    pkcols=[]
    is_versioned=False
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
    #
    log.debug("delete_item tab %s pk %s pkcols %s",tab,pk,pkcols)
    metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")

    chkout=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["errors"]="PK ist nicht vorhanden"
            return (jsonify(out),500)
    else:
        out["errors"]="PK check nicht erfolgreich"
        return (jsonify(out),500)
        
    log.debug("delete_item pk_columns %s",pkcols)
    if len(pkcols)==1:
        pkwhere=pkcols[0]+"=?"
    else:
        pkexp=[k+"=?" for k in pkcols]
        pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbengine)
        cur_row=get_item_raw(dbengine,tab,pk,pk_column_list=pkcols)
        vallist=[]
        vallist.append(ts)
        vallist.append(ts)
        vallist.append(pk)
        val_tuple=tuple(vallist)
        sql=f"UPDATE {tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' WHERE {pkwhere}  AND invalid_from_dt='9999-12-31 00:00:00'"
        dbengine.execute(sql,val_tuple)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        rec=reclist[0]
        collist=[k for k in rec.keys()]
        vallist=[v for v in rec.values()]
        vallist[collist.index("valid_from_dt")]=ts
        vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        vallist[collist.index("last_changed_dt")]=ts
        vallist[collist.index("is_latest_period")]='Y'
        vallist[collist.index("is_current_and_active")]='N'
        vallist[collist.index("is_deleted")]='Y'
        qlist=["?" for k in rec.keys()]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        dbengine.execute(sql,tuple(vallist))
    else:
        sql=f"DELETE FROM {tab} WHERE {pkwhere}"
        log.debug("delete_item sql %s",sql)
        dbengine.execute(sql,pk)
    return 'Item deleted successfully', 200
    #return jsonify(out)


@app.route(api_metadata_prefix+'/tables', methods=['GET'])
def get_metadata_tables():
    log.debug("++++++++++ entering get_metadata_tables")
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    items,columns,total_count,msg=sql_select(dbengine,metadata_tab_query,order_by,offset,limit,with_total_count=False)
    out={}
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    if columns is None:  # keine Spalten
        return msg, 500
    else:
        return jsonify(out)

@app.route(api_metadata_prefix+'/table/<tab>', methods=['GET'])
def get_metadata_tab_columns(tab):
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
    pkcols=None
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    log.debug('get_metadata_tab_columns: for %s',tab)
    metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    return jsonify(metadata)

"""
"""

###########################
##
## REPO
##
###########################


# Define routes for CRUD operations
@app.route(repo_api_prefix+'/<tab>', methods=['GET'])
def get_all_repos(tab):
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
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,msg=sql_select(repoengine,repo_table_prefix+tab,order_by,offset,limit,with_total_count=True)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    if columns is None:  # keine Spalten
        return msg, 500
    else:
        return jsonify(out)

# Define routes for CRUD operations


@app.route(repo_api_prefix+'/<tab>/<pk>', methods=['GET'])
def get_repo(tab,pk):
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
    # check options
    pkcols=[]
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    out=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols)
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
    return (jsonify(out),500)


@app.route(repo_api_prefix+'/<tab>', methods=['POST'])
def create_repo(tab):
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
    out={}
    pkcols=[]
    is_versioned=False
    def_repo_seq="REPO"
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
    log.debug("create_repo tab %s pkcols %s",tab,pkcols)
    metadata=get_metadata_raw(repoengine,repo_table_prefix+tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    log.debug("create_item %s pkcols2 %s",tab,pkcols)
    log.debug("in create_item (pos)")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    s=None
    if is_versioned:
        ts=get_current_timestamp(repoengine)
        print(ts)
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
        if "valid_from_dt" not in collist:
            collist.append("valid_from_dt")
            vallist.append(ts)
        else:
            vallist[collist.index("valid_from_dt")]=ts
        if "invalid_from_dt" not in collist:
            collist.append("invalid_from_dt")
            vallist.append("9999-12-31 00:00:00")
        else:
            vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        if "last_changed_dt" not in collist:
            collist.append("last_changed_dt")
            vallist.append(ts)
        else:
            vallist[collist.index("last_changed_dt")]=ts
        if "is_latest_period" not in collist:
            collist.append("is_latest_period")
            vallist.append("Y")
        else:
            vallist[collist.index("is_latest_period")]="Y"
        if "is_deleted" not in collist:
            collist.append("is_deleted")
            vallist.append("N")
        else:
            vallist[collist.index("is_deleted")]="N"
        if "is_current_and_active" not in collist:
            collist.append("is_current_and_active")
            vallist.append("Y")
        else:
            vallist[collist.index("is_current_and_active")]="Y"
    else:
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
    # wenn Repo Tabelle mit Id aber keine id-spalte in data dann id spalte hinzufügen und mit sequence befüllen
    if tab in ["adhoc","application","datasource","external_resource","group","lookup","role","user","group"] and "id" not in item.keys():
        # id ist nicht in data list so generate
        collist.append("id")
        s=get_next_seq(repoengine,tab)
        vallist.append(s)
    # wenn Repo Tabelle mit Id aber null für id dann id  mit sequence befüllen
    if tab in ["adhoc","application","datasource","external_resource","group","lookup","role","user","group"] and "id" in item.keys():
        # id ist nicht in data list so generate
        s=get_next_seq(repoengine,tab)
        vallist[collist.index("id")]=s
    try:
        qlist=["?" for k in vallist]
        if len(pkcols)==1:
            s=vallist[collist.index(pkcols[0])]
        else:
            s={}
            for c in pkcols:
                s[c]=vallist[collist.index(c)]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {repo_table_prefix}{tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create repo: %s",sql)
        repoengine.execute(sql,tuple(vallist))
        #cursor = cnxn.cursor()
        #cursor.execute(sql,val_tuple)
        #cnxn.commit()
        out["status"]="ok"
        #return 'Item created successfully', 201
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        out["errors"]="create_repo:sqlalchemy:"+error
        return (jsonify(out),500)
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}    
        else:
           estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}    
        out["errors"]="create_repo:exception:"+estruc
        return (jsonify(out),500)
    # read new record from database and send it back
    out=get_item_raw(repoengine,repo_table_prefix+tab,s,pk_column_list=pkcols)
    return jsonify(out)


@app.route(repo_api_prefix+'/<tab>/<pk>', methods=['PUT'])
def update_repo(tab,pk):
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
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    log.debug("item-keys %s",item.keys())
    metadata=get_metadata_raw(repoengine,repo_table_prefix+tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")

    # get old record
    chkout=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["errors"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
            return (jsonify(out),500)
    else:
        out["errors"]="PK check nicht erfolgreich"
        return (jsonify(out),500)

    pkexp=[k+"=?" for k in pkcols]
    pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)

    log.debug("pk_columns %s",pkcols)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(repoengine)
        # hole then alten Datensatz aus der DB mit dem angegebenen pk
        cur_row=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        vallist=[]
        vallist.append(ts)
        vallist.append(ts)
        vallist.append(pk)
        val_tuple=tuple(vallist)
        sql=f"UPDATE {repo_table_prefix}{tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' WHERE {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
        repoengine.execute(sql,val_tuple)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        rec=reclist[0]
        collist=[k for k in rec.keys()]
        vallist=[v for v in rec.values()]
        # überschreibe mit neuen werten
        for k,v in item.items():
            log.debug("-> %s %s",k,v)
            pos=collist.index(k)
            if pos>=0:
                log.debug("overwrite: %s %s",k,v)
                vallist[pos]=v
        vallist[collist.index("valid_from_dt")]=ts
        vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        vallist[collist.index("last_changed_dt")]=ts
        vallist[collist.index("is_latest_period")]='Y'
        vallist[collist.index("is_current_and_active")]='Y'
        qlist=["?" for k in rec.keys()]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        repoengine.execute(sql,tuple(vallist))
    else:
        # nicht versionierter Standardfall
        othercols=[col for col in item.keys() if col not in pkcols]
        log.debug("othercols %s",othercols)
        osetexp=[k+"=?" for k in othercols]
        osetexp_str=",".join(osetexp)
    
        vallist=[item[col] for col in item.keys() if col not in pkcols]
        vallist.append(pk)
        val_tuple=tuple(vallist)
        
        sql=f"UPDATE {repo_table_prefix}{tab} SET {osetexp_str} WHERE {pkwhere}"
        log.debug("update item sql %s",sql)
        repoengine.execute(sql,val_tuple)
    # den aktuellen Datensatz wieder aus der DB holen und zurückgeben (könnte ja Triggers geben)
    out=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols,versioned=is_versioned)
    #return 'Item updated successfully', 200
    return jsonify(out)

@app.route(repo_api_prefix+'/<tab>/<pk>', methods=['DELETE'])
def delete_repo(tab,pk):
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
    # check options
    out={}
    pkcols=[]
    is_versioned=False
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
    #
    metadata=get_metadata_raw(repoengine,repo_table_prefix+tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=(metadata["columns"])[0]
        log.warning("implicit pk first column")
        
    chkout=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["errors"]="PK ist nicht vorhanden"
            return (jsonify(out),500)
    else:
        out["errors"]="PK check nicht erfolgreich"
        return (jsonify(out),500)
        
    log.debug("delete_repo pk_columns %s",pkcols)
    pkexp=[k+"=?" for k in pkcols]
    pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(repoengine)
        cur_row=get_item_raw(repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols)
        vallist=[]
        vallist.append(ts)
        vallist.append(ts)
        vallist.append(pk)
        val_tuple=tuple(vallist)
        sql=f"UPDATE {repo_table_prefix}{tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' WHERE {pkwhere}  AND invalid_from_dt='9999-12-31 00:00:00'"
        repoengine.execute(sql,val_tuple)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        rec=reclist[0]
        collist=[k for k in rec.keys()]
        vallist=[v for v in rec.values()]
        vallist[collist.index("valid_from_dt")]=ts
        vallist[collist.index("invalid_from_dt")]="9999-12-31 00:00:00"
        vallist[collist.index("last_changed_dt")]=ts
        vallist[collist.index("is_latest_period")]='Y'
        vallist[collist.index("is_current_and_active")]='N'
        vallist[collist.index("is_deleted")]='Y'
        qlist=["?" for k in rec.keys()]
        q_str=",".join(qlist)
        collist_str=",".join(collist)
        sql = f"INSERT INTO {repo_table_prefix}{tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        repoengine.execute(sql,tuple(vallist))
    else:
        sql=f"DELETE FROM {repo_table_prefix}{tab} WHERE {pkwhere}"
        log.debug("delete_item sql %s",sql)
        repoengine.execute(sql,pk)
    return 'Repo deleted successfully', 200
    #return jsonify(out)

@app.route(repo_api_prefix+'/init_repo', methods=['POST'])
def init_repo():
    log.debug("++++++++++ entering init_repo")
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
@app.route(repo_api_prefix+'/lookup/<id>/data', methods=['GET'])
def get_lookup(id):
    log.debug("++++++++++ entering get_lookup")
    log.debug("get_lookup: param id is <%s>",str(id))
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("get_lookup pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,msg=repo_lookup_select(repoengine,dbengine,id,order_by,offset,limit,with_total_count=True)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    if columns is None:  # keine Spalten
        return msg, 500
    else:
        return jsonify(out)

@app.route(repo_api_prefix+'/adhoc/<id>/data', methods=['GET'])
def get_adhoc_data(id):
    log.debug("++++++++++ entering get_adhoc_data")
    log.debug("get_adhoc_data: param id is <%s>",str(id))
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
    if fmt=="JSON":
        sql, execute_in_repodb = get_repo_adhoc_sql_stmt(repoengine,id)
        if sql is None:
            msg="adhoc id/name invalid oder kein sql beim adhoc hinterlegt"
            log.error(msg)
            return msg, 500
        if execute_in_repodb:
            log.debug("adhoc query execution in repodb")
            data=repoengine.execute(sql)
        else:
            log.debug("adhoc query execution")
            data=dbengine.execute(sql)
        out={}
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        order_by = request.args.get('order_by')
        log.debug("get_adhoc_data pagination offset=%s limit=%s",offset,limit)
        items = [dict(row) for row in data]
        columns = list(data.keys())
        total_count=len(items)
        out["data"]=items
        out["columns"]=columns
        out["total_count"]=total_count
        if columns is None:  # keine Spalten
            return "Fehler beim JSON adhoc", 500
        else:
            return jsonify(out)
    else:
        result=repo_adhoc_select(repoengine,dbengine,id,order_by,offset,limit,with_total_count=True)
        if result is None:  # keine Spalten
            return "adhoc fehler leer", 500
        else:
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
    
            # Save the DataFrame to an Excel file
            if fmt=="XLSX":
                log.debug("adhoc excel")
                tmpfile='mydata.xlsx'
                output = pd.ExcelWriter(tmpfile)
                df.to_excel(output, index=False)
                output.close()
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
                log.debug("adhoc csv")
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

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    from yourapplication.model import db
    db.init_app(app)

    from yourapplication.views.admin import admin
    from yourapplication.views.frontend import frontend
    app.register_blueprint(admin)
    app.register_blueprint(frontend)

    return app

if __name__ == '__main__':

    # Create a new ArgumentParser object
    parser = argparse.ArgumentParser(description='PlainBI CRUD Application Backend')
    # Define the command-line arguments
    parser.add_argument('-P', '--port', type=int, help='The port number to use (default 3001)')
    #parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    parser.add_argument('-u', '--username', type=str, help='The username for the database connection')
    parser.add_argument('-p', '--password', type=str, help='The password for the database connection')
    parser.add_argument('-d', '--database', type=str, help='The database connection description')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
    # Parse the arguments
    args = parser.parse_args()

    # Access the argument values
    if args.username:
        log.info(f"The username is {args.username}")
    else:
        log.info("No username was provided")
    
    if args.password:
        log.info(f"The password is {args.password}")
    else:
        log.info("No password was provided")
    
    if args.database:
        log.info(f"The database connection description is {args.database}")
    else:
        log.info("No database connection description was provided")
    
    if args.port:
        app_port=args.port
        log.info(f"The port number is {args.port}")
    else:
        app_port=3001
        log.info(f"No port number was provided - default {args.port} is used ")

    app.json_encoder = CustomJSONEncoder ## wegen jsonify datetimes
    
    log.info("start server "+__name__)
    app.run(debug=True,host='0.0.0.0', port=app_port,use_reloader=False)

