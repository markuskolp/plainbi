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
curl --header "Content-Type: application/json" --request GET "localhost:3002/api/crud/DWH.CONFIG.crud_api_testtable?order_by=name&offset=3" -w "%{http_code}\n"
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


"""


import argparse
import urllib
import logging
from sys import platform
import os
import sys
import json
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv

home_directory = os.path.expanduser( '~' )
dotenv_path = os.path.join(home_directory, '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
log=app.logger
log.setLevel(logging.DEBUG)

pbi_env={}
pbi_env["db_server"] = os.environ.get("db_server")
pbi_env["db_username"] = os.environ.get("db_username")
pbi_env["db_password"] = os.environ.get("db_password")
pbi_env["db_database"] = os.environ.get("db_database")

def db_subs_env(s,d):
    if s is None: return None
    for k,v in d.items():
        if v is None:
            s=s.replace("{"+k+"}","")
        else:
            s=s.replace("{"+k+"}",v)
    return s

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

api_root="/api"
api_prefix=api_root+"/crud"
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
metadata_col_query="""
SELECT 
    DB_NAME() AS database_name,
    SCHEMA_NAME(t.schema_id) AS schema_name,
    t.name AS table_name,
    DB_NAME()+'.'+SCHEMA_NAME(t.schema_id)+'.'+t.name AS full_table_name,
    c.name AS column_name,
    c.column_id,
    TYPE_NAME(c.system_type_id) AS data_type,
    c.max_length,
    c.precision,
    c.scale,
    CASE 
        WHEN EXISTS (
            SELECT 1
            FROM sys.indexes i 
            INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            WHERE i.is_primary_key = 1 AND ic.object_id = c.object_id AND ic.column_id = c.column_id
        )
        THEN 1 
        ELSE 0 
    END AS is_primary_key
FROM sys.columns c
INNER JOIN sys.tables t ON c.object_id = t.object_id
WHERE DB_NAME()+'.'+SCHEMA_NAME(t.schema_id)+'.'+t.name = '<fulltablename>'
ORDER BY database_name, schema_name, table_name, column_id
"""

def sql_select(tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    total_count=None
    log.debug("sql_select tab parameter: %s",tab)
    try:
        if len(tab.split(" "))==1:          # nur ein wort
            sql=f'SELECT * FROM {tab}'
        else:                               # ein komplettes select statement expected
            sql=tab
        if where_clause is not None:
            sql+=" WHERE "+where_clause
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        if offset is not None:
            sql+=" OFFSET "+offset+ " ROWS"
        if limit is not None:
            sql+=" FETCH NEXT "+limit+" ROWS ONLY"
        log.debug("sql_select: %s",sql)
        data=dbengine.execute(sql)
        items = [dict(row) for row in data]
        print("sql_select: anz rows=%d",len(items))
        columns = list(data.keys())
        if with_total_count:
            sql_total_count=f'SELECT COUNT(*) AS total_count FROM {tab}'
            data_total_count=dbengine.execute(sql_total_count)
            item_total_count=[dict(r) for r in data_total_count]
            total_count=(item_total_count[0])['total_count']
        return items,columns,total_count,"ok"
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        return None,None,None,str(e)

def get_metadata_raw(tab,pk_column_list):
    """
    holt die struktur einer Tabelle entweder aus sys.columns oder aus der query selbst
    überschreibe die PK spezifikation wenn pk_column_list befüllit ist
    retunrs dict mit keys "pk_columns", "error"
    """
    log.debug("----------get_metadata_raw ------ %s ----------",tab)
    out={}
    items,columns,total_count,msg=sql_select(metadata_col_query.replace('<fulltablename>',tab))
    if len(items)>0:
        # es gibt etwas in den sqlserver metadaten
        out["columns"]=columns
        pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
        log.debug("get_metadata_raw1: pkcols %s",str(pkcols))
        out["column_data"]=items
    else:
        # nicht in metadaten gefunden
        pkcols=[]  # default leer (1ste spalte regel in den crud operations)
        try:
            sql=f'SELECT * FROM {tab} WHERE 1=0'
            log.debug("get_metadata_raw sql=%s",sql)
            data=dbengine.execute(sql)
            columns = list(data.keys())
            out["columns"]=columns
            log.debug("get_metadata_raw: pkcols []")
            #out["metadata"]=mitems
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            out["errors"]="get_metadata_raw/sqlalchemy:"+error
        except Exception as e:
            log.debug("get_metadata_raw: error")
            if "message" in e:
               estruc={ "message" : e.message}    
               log.debug("get_metadata_raw: estruc1 %s",estruc)
            else:
               estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}    
               log.debug("get_metadata_raw2: estruc2 %s",estruc)
            out["errors"]="get_metadata_raw/exception:"+estruc
    if pk_column_list is not None:
        out["pk_columns"]=pk_column_list
    else:
        out["pk_columns"]=pkcols
    log.debug("get_metadata_raw: %s pk:%s",tab,out["pk_columns"])
    return out

def get_item_raw(tab,pk,pk_column_list=None,versioned=False):
    """
    Hole einen bestimmten Datensatz aus einer Tabelle ub der Datenbank

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    pk_column_list : Wert des Datensatz Identifier (Primary Key)
    

    Returns
    -------
    dict mit den keys "data" ggf "errors"

    """
    out={}
    log.debug("in get_item raw")
    metadata=get_metadata_raw(tab,pk_column_list)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    print("get_item_raw: pk_columns",str(pkcols))
    if len(pkcols) > 1:
        out["errors"]="get_item_raw:PK mit mehr als einer Spalte ist nicht implementiert"
        return out        
    try:
        #cursor = cnxn.cursor()
        pkstr1=pkcols[0]
        sql=f'SELECT * FROM {tab} where {pkstr1}={pk}'
        if versioned:
           sql+=" AND invalid_from_dt='9999-12-31 00:00:00'" 
        log.debug("sql=%s",sql)
        data=dbengine.execute(sql)
        items = [dict(row) for row in data]
        columns = list(data.keys())
        for r in items:
            for k,v in r.items():
                if type(v).__name__=="datetime":
                    r[k]=v.strftime("%Y-%m-%d %H:%M:%S.%f")
        log.debug("columns: %s",columns)
        out["data"]=items
        out["columns"]=columns
        out["total_count"]=len(items)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        out["errors"]="get_item_raw:sqlalchemy:"+error
        out["error_sql"]=sql
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}    
        else:
           estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}    
        out["errors"]="get_item_raw:exception:"+estruc
    return out

def get_next_seq(seq):
    """
    Hole den nächsten wert einer sequence

    Parameters
    ----------
    seq : Name der Sequence

    Returns
    -------
    sequence wert als int

    """
    out=None
    log.debug("in get_next_seq")
    try:
        #cursor = cnxn.cursor()
        sql=f'SELECT NEXT VALUE FOR {seq}'
        log.debug("sql=%s",sql)
        data=dbengine.execute(sql)
        for row in data:
            out=row[0]
        log.debug("got sequence value %d",out)    
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        out["errors"]="get_next_seq:sqlalchemy:"+error
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}    
        else:
           estruc={ "message" : "Es ist ein Fehler bei der Squence aufgetreten", "details" : str(e)}    
        out["errors"]="get_next_seq:exception:"+estruc
    return out

def get_current_timestamp():
    """
    Hole den nächsten wert einer sequence

    Parameters
    ----------
    seq : Name der Sequence

    Returns
    -------
    sequence wert als int

    """
    out=None
    log.debug("in get_current_timestamp")
    try:
        #cursor = cnxn.cursor()
        sql='SELECT GETDATE()'
        log.debug("sql=%s",sql)
        data=dbengine.execute(sql)
        for row in data:
            out=row[0]
        log.debug("got timestamp value %s",out)    
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        out["errors"]="get_current_timestamp:sqlalchemy:"+error
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}    
        else:
           estruc={ "message" : "Es ist ein Fehler Timestamp aufgetreten", "details" : str(e)}    
        out["errors"]="get_current_timestamp:exception:"+estruc
    return out


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
    out={}
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    log.debug("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,msg=sql_select(tab,order_by,offset,limit,with_total_count=True)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=total_count
    if columns is None:  # keine Spalten
        return msg, 500
    else:
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
    log.debug("++++++++++get_item")
    # check options
    pkcols=[]
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    log.debug("tab %s pk %s")
    out=get_item_raw(tab,pk,pk_column_list=pkcols)
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
    log.debug("++++++++++create_item")
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
    metadata=get_metadata_raw(tab,pk_column_list=pkcols)
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
        ts=get_current_timestamp()
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
            s=get_next_seq(seq)
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
    out=get_item_raw(tab,s,pk_column_list=pkcols)
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
    log.debug("++++++++++update_item")
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
    log.debug("update_item tab %s pk %s pkcols %s",tab,pk,pkcols)
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    log.debug("item-keys %s",item.keys())
    metadata=get_metadata_raw(tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    if len(pkcols) > 1:
        out["errors"]="PK mit mehr als einer Spalte ist nicht implementiert"
        return (jsonify(out),500)

    if pkcols[0] not in item.keys():
        out["errors"]="PK Spalte muss beim Update (PUT) in den request daten sein"
        return (jsonify(out),500)

    chkout=get_item_raw(tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["errors"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
            return (jsonify(out),500)
    else:
        out["errors"]="PK check nicht erfolgreich"
        return (jsonify(out),500)

    if len(pkcols)==1:
        pkwhere=pkcols[0]+"=?"
    else:
        pkexp=[k+"=?" for k in pkcols]
        pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)

    log.debug("pk_columns %s",pkcols)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp()
        # hole then alten Datensatz aus der DB mit dem angegebenen pk
        cur_row=get_item_raw(tab,pk,pk_column_list=pkcols,versioned=is_versioned)
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
    out=get_item_raw(tab,pk,pk_column_list=pkcols,versioned=is_versioned)
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
    log.debug("++++++++++delete_item")
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
    log.debug("delete_item tab %s pk %s pkcols %s",tab,pk,pkcols)
    metadata=get_metadata_raw(tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    if len(pkcols) > 1:
        out["errors"]="PK mit mehr als einer Spalte ist nicht implementiert"
        return (jsonify(out),500)

    log.debug("in delete_item")
    metadata=get_metadata_raw(tab,pk_column_list=pkcols)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=(metadata["columns"])[0]
        log.warning("implicit pk first column")
        
    chkout=get_item_raw(tab,pk,pk_column_list=pkcols)
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
        ts=get_current_timestamp()
        cur_row=get_item_raw(tab,pk,pk_column_list=pkcols)
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
    offset = request.args.get('offset')
    limit = request.args.get('limit')
    order_by = request.args.get('order_by')
    items,columns,total_count,msg=sql_select(metadata_tab_query,order_by,offset,limit,with_total_count=False)
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
    pkcols=None
    if len(request.args) > 0:
        for key, value in request.args.items():
            log.info("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                log.debug("pk option %s",pkcols)
    log.debug('get_metadata_tab_columns: for %s',tab)
    metadata=get_metadata_raw(tab,pk_column_list=pkcols)
    return jsonify(metadata)

"""
"""

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

    
    log.info("start server "+__name__)
    app.run(debug=True,host='0.0.0.0', port=app_port)

