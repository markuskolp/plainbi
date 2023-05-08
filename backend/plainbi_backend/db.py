# -*- coding: utf-8 -*-
"""
Created on Thu May  4 08:11:27 2023

@author: kribbel
"""
import logging
log = logging.getLogger(__name__)
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import unquote

"""
import urllib
repoengine = sqlalchemy.create_engine("sqlite:////Users/kribbel/plainbi_repo.db")
params = urllib.parse.quote_plus("DSN=DWH_DEV_PORTAL;UID=portal;PWD=s7haPsjrnl3")
dbengine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


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

def get_db_type(dbengine):
    if "sqlite" in str(dbengine.url).lower():
        return "sqlite"
    else:
        return "mssql"


def sql_select(dbengine,tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None):
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

def get_metadata_raw(dbengine,tab,pk_column_list):
    """
    holt die struktur einer Tabelle entweder aus sys.columns oder aus der query selbst
    überschreibe die PK spezifikation wenn pk_column_list befüllit ist
    retunrs dict mit keys "pk_columns", "error"
    """
    log.debug("----------get_metadata_raw ------ %s ----------",tab)
    out={}
    dbtype=get_db_type(dbengine)
    items,columns,total_count,msg=sql_select(dbengine,metadata_col_query.replace('<fulltablename>',tab))
    if items is not None and len(items)>0:
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

def get_item_raw(dbengine,tab,pk,pk_column_list=None,versioned=False):
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
    metadata=get_metadata_raw(dbengine,tab,pk_column_list)
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    print("get_item_raw: pk_columns",str(pkcols))
    try:
        #cursor = cnxn.cursor()
        if isinstance(pk, dict):
            pkstr1=pkcols[0]
            sql=f'SELECT * FROM {tab}'
            i=0
            for c,v in pk.items():
                i+=1
                if i==1:
                    sql+=" WHERE "
                else:
                    sql+=" AND "
                sql+=c+"="+v
        else:
            pkstr1=pkcols[0]
            sql=f'SELECT * FROM {tab} where {pkstr1}={pk}'
        if versioned:
           #sql+=" AND invalid_from_dt='9999-12-31 00:00:00'" 
           sql+=" AND is_current_and_active = 'Y'" 
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

def get_next_seq(dbengine,seq):
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
    if get_db_type(dbengine)=="sqlite":
        log.debug("in get_next_seq repo sqlite")
        sql=f"SELECT curval FROM plainbi_seq WHERE sequence_name='{seq}'"
        log.debug("sql=%s",sql)
        data=dbengine.execute(sql)
        for row in data:
            out=row[0]
        nextval=out+1
        sql=f"UPDATE plainbi_seq SET curval={nextval} WHERE sequence_name='{seq}'"
        log.debug("sql=%s",sql)
        x=dbengine.execute(sql)    
    else:
        log.debug("in get_next_seq not sqlite")
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
               estruc={ "message" : "Es ist ein Fehler bei der Sequence aufgetreten", "details" : str(e)}    
            out["errors"]="get_next_seq:exception:"+estruc
    return out

def get_current_timestamp(dbengine):
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

## repo lookup adhoc
def repo_lookup_select(repoengine,dbengine,id,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    log.debug("sql_select tab parameter: %s",id)
    lkpq=repoengine.execute("select * from plainbi_lookup where id=?" , id)
    lkp=[dict(r) for r in lkpq]
    sql=lkp[0]["sql_query"]
    try:
        data=dbengine.execute(sql)
        items = [dict(row) for row in data]
        columns = list(data.keys())
        total_count=len(items)
        return items,columns,total_count,"ok"
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        return None,None,None,str(e)

## repo lookup adhoc
def repo_adhoc_select(repoengine,dbengine,id,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    log.debug("sql_select tab parameter: %s",id)
    lkpq=repoengine.execute("select * from plainbi_adhoc where id=?" , id)
    lkp=[dict(r) for r in lkpq]
    sql=lkp[0]["sql_query"]
    data = dbengine.execute(sql)
    return data
