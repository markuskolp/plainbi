
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
curl --header "Content-Type: application/json" --request GET "localhost:3001/api/crud/ANALYSIS.guest.testtable?order_by=name&offset=3" -w "%{http_code}\n"
# GET
curl --header "Content-Type: application/json" --request GET localhost:3001/api/crud/ANALYSIS.guest.testtable/1 -w "%{http_code}\n"
# POST
curl --header "Content-Type: application/json" --request POST --data '{\"nr\":\"8\",\"name\":\"wert8\",\"dat\":\"12.12.2023\"}' localhost:3001/api/crud/ANALYSIS.guest.testtable
# PUT
curl --header "Content-Type: application/json" --request PUT --data '{\"nr\":\"4\",\"name\":\"wert44\",\"dat\":\"12.12.2023\"}' localhost:3001/api/crud/ANALYSIS.guest.testtable/4
# DELETE
curl --header "Content-Type: application/json" --request DELETE localhost:3001/api/crud/ANALYSIS.guest.testtable/6 -w "%{http_code}\n"
# METADATA tables
curl --header "Content-Type: application/json" --request GET localhost:3001/api/metadata/tables -w "%{http_code}\n"

# METADATA
curl --header "Content-Type: application/json" --request GET localhost:3001/api/metadata/table/ANALYSIS.guest.testtable -w "%{http_code}\n"

"""


from flask import Flask, jsonify, request,Response
#import pyodbc
import urllib
import sqlalchemy
import logging
import json

app = Flask(__name__)
log=app.logger
log.setLevel(logging.DEBUG)

# Connect to SQL Server database
#server = 'your-server-name'
#database = 'your-database-name'
#username = 'your-username'
#password = 'your-password'
#cnxn = pyodbc.connect("DSN=DWH_DEV")

#params = urllib.parse.quote_plus("DSN=DWH_DEV")
#dbengine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
server = 'VNTSV147'
database = 'ANALYSIS'
username="MESSE-MUENCHEN\kribbel"
password="j0E#beimesse"
eng_str = fr'mssql+pymssql://{username}:{password}@{server}/{database}'
dbengine = sqlalchemy.create_engine(eng_str)


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

def get_metadata_raw(tab):
    """
    holt die struktur einer Tabelle entweder aus sys.columns oder aus der query selbst
    """
    out={}
    items,columns,total_count,msg=sql_select(metadata_col_query.replace('<fulltablename>',tab))
    if len(items)>0:
        out["columns"]=columns
        pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
        out["pk_columns"]=pkcols
    else:
        # nicht in metadaten gefunden
        try:
            sql=f'SELECT * FROM {tab} WHERE 1=0'
            log.debug("get_metadata_raw sql=%s",sql)
            data=dbengine.execute(sql)
            columns = list(data.keys())
            out["columns"]=columns
            out["pk_columns"]=[]  # default leer (1ste spalte regel in den crud operations)
            #out["metadata"]=mitems
        except Exception as e:
            if "message" in e:
               estruc={ "message" : e.message}
            else:
               estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}
            out["errors"]=estruc
    return out

def get_item_raw(tab,pk):
    log.debug("in get_item raw")
    metadata=get_metadata_raw(tab)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=(metadata["columns"])[0]
        log.warning("implicit pk first column")
    print("pk_columns",pkcols)
    out={}
    try:
        #cursor = cnxn.cursor()
        pkstr1=pkcols[0]
        sql=f'SELECT * FROM {tab} where {pkstr1}={pk}'
        log.debug("sql=%s",sql)
        data=dbengine.execute(sql)
        items = [dict(row) for row in data]
        columns = list(data.keys())
        log.debug("columns: %s",columns)
        out["data"]=items
        out["columns"]=columns
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}
        else:
           estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}
        out["errors"]=estruc
    return out


# Define routes for CRUD operations
@app.route(api_prefix+'/<tab>', methods=['GET'])
def get_all_items(tab):
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
    out=get_item_raw(tab,pk)
    if len(out["data"])>0:
        return jsonify(out)
        #return Response(jsonify(out),status=204)
    else:
        log.debug("no record found")
        return Response(status=204)

@app.route(api_prefix+'/<tab>', methods=['POST'])
def create_item(tab):
    out={}
    log.debug("in create_item (pos)")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    try:
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
        qlist=["?" for k in item.keys()]
        collist_str=",".join(collist)
        q_str=",".join(qlist)
        sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
        log.debug("create item: %s",sql)
        dbengine.execute(sql,tuple(vallist))
        #cursor = cnxn.cursor()
        #cursor.execute(sql,val_tuple)
        #cnxn.commit()
        out["status"]="ok"
        #return 'Item created successfully', 201
    except Exception as e:
        if "message" in e:
           estruc={ "message" : e.message}
        else:
           estruc={ "message" : "Es ist ein Fehler aufgetreten", "details" : str(e)}
        out["errors"]=estruc
    return jsonify(out)


@app.route(api_prefix+'/<tab>/<pk>', methods=['PUT'])
def update_item(tab,pk):
    log.debug("in update_item")
    data_bytes = request.get_data()
    log.debug("databytes: %s",data_bytes)
    data_string = data_bytes.decode('utf-8')
    log.debug("datastring: %s",data_string)
    item = json.loads(data_string.strip("'"))
    #item = {key: request.data[key] for key in request.data}
    log.debug("item %s",item)
    log.debug("item-keys %s",item.keys())
    metadata=get_metadata_raw(tab)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=(metadata["columns"])[0]
        log.warning("implicit pk first column")
    log.debug("pk_columns %s",pkcols)
    othercols=[col for col in item.keys() if col not in pkcols]
    log.debug("othercols %s",othercols)
    osetexp=[k+"=?" for k in othercols]
    osetexp_str=",".join(osetexp)


    vallist=[item[col] for col in item.keys() if col not in pkcols]
    vallist.append(pk)
    val_tuple=tuple(vallist)

    out={}
    if len(pkcols)==1:
        pkwhere=pkcols[0]+"=?"
    else:
        pkexp=[k+"=?" for k in pkcols]
        pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)
    sql=f"UPDATE {tab} SET {osetexp_str} WHERE {pkwhere}"
    log.debug("update item sql %s",sql)
    dbengine.execute(sql,val_tuple)
    out=get_item_raw(tab,pk)
    #return 'Item updated successfully', 200
    return jsonify(out)

@app.route(api_prefix+'/<tab>/<pk>', methods=['DELETE'])
def delete_item(tab,pk):
    log.debug("in delete_item")
    metadata=get_metadata_raw(tab)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=(metadata["columns"])[0]
        log.warning("implicit pk first column")
    log.debug("delete_item pk_columns %s",pkcols)
    if len(pkcols)==1:
        pkwhere=pkcols[0]+"=?"
    else:
        pkexp=[k+"=?" for k in pkcols]
        pkwhere=" AND ".join(pkexp)
    log.debug("pkwhere %s",pkwhere)
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
    out=get_metadata_raw(tab)
    return jsonify(out)

"""
"""

if __name__ == '__main__':
    log.info("start server "+__name__)
    app.run(debug=True,host='0.0.0.0', port=3001)

