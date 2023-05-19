# -*- coding: utf-8 -*-
"""
Created on Thu May  4 08:11:27 2023

@author: kribbel
"""
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import unquote
from plainbi_backend.utils import is_id, last_stmt_has_errors, make_pk_where_clause


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


def sql_select(dbengine,tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,versioned=False):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    total_count=None
    log.debug("sql_select tab parameter: %s",tab)
    w=where_clause
    try:
        if len(tab.split(" "))==1:          # nur ein wort
            sql=f'SELECT * FROM {tab}'
        else:                               # ein komplettes select statement expected
            sql=tab
        if versioned:
            if w is not None:
                w="("+w+") AND is_current_and_active = 'Y'"
            else:
                w="is_current_and_active = 'Y'"
        if w is not None:
            sql+=" WHERE "+w
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        if offset is not None:
            sql+=" OFFSET "+offset+ " ROWS"
        if limit is not None:
            sql+=" FETCH NEXT "+limit+" ROWS ONLY"
        log.debug("sql_select: %s",sql)
        data=dbengine.execute(sql)
        #data.fetchall()
        items = [dict(row) for row in data]
        log.debug("sql_select: anz rows=%d",len(items))
        columns = list(data.keys())
        if with_total_count:
            sql_total_count=f'SELECT COUNT(*) AS total_count FROM {tab}'
            data_total_count=dbengine.execute(sql_total_count)
            item_total_count=[dict(r) for r in data_total_count]
            total_count=(item_total_count[0])['total_count']
        return items,columns,total_count,"ok"
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in sql_select: %s",str(e_sqlalchemy))
        return None,None,None,e_sqlalchemy
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        return None,None,None,e

def get_metadata_raw(dbengine,tab,pk_column_list):
    """
    holt die struktur einer Tabelle entweder aus sys.columns oder aus der query selbst
    überschreibe die PK spezifikation wenn pk_column_list befüllit ist
    retunrs dict mit keys "pk_columns", "error"
    """
    log.debug("++++++++++ entering get_metadata_raw")
    log.debug("get_metadata_raw: param tab is <%s>",str(tab))
    log.debug("get_metadata_raw: param pk_column_list (override) is <%s>",str(pk_column_list))
    out={}
    dbtype=get_db_type(dbengine)
    pkcols=[]
    items = None
    if dbtype == "mssql":
        # for mssql try metadata search
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query.replace('<fulltablename>',tab))
        log.debug("get_metadata_raw: returned error %s",str(e))
        if last_stmt_has_errors(e, out):
            return out
        #    
        log.debug("get_metadata_raw: 1")
        log.debug("get_metadata_raw: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            log.debug("get_metadata_raw: got some metadata from mssql")
            # es gibt etwas in den sqlserver metadaten
            pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
            log.debug("get_metadata_raw from mssql: pkcols %s",str(pkcols))
            log.debug("get_metadata_raw from mssql: columns %s",str(columns))
            out["columns"]=columns
            out["column_data"]=items
    if "columns" not in out.keys():
        # nothing in metadata - get columns from query
        log.debug("get_metadata_raw: nothing in metadata - get columns from query")
        # nicht in metadaten gefunden
        try:
            sql=f'SELECT * FROM {tab} WHERE 1=0'
            log.debug("get_metadata_raw: sql=%s",sql)
            data=dbengine.execute(sql)
            columns = list(data.keys())
            out["columns"]=columns
            #out["metadata"]=mitems
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_metadata:raw: %s",str(e_sqlalchemy))
            last_stmt_has_errors(e_sqlalchemy, out)
            return out
        except Exception as e:
            log.debug("exception in get_metadata_raw: error %s",str(e))
            last_stmt_has_errors(e, out)
            return out
    log.debug("sql_select in get_metadata_raw 4")
    out["pk_columns"]=pkcols
    if pk_column_list is not None:
        if isinstance(pk_column_list, list):
            if len(pk_column_list) > 0:
                out["pk_columns"]=pk_column_list
                log.debug("get_metadata_raw returns parameter pk_column_list")
    else:
        log.debug("get_metadata_raw returns computedd column_list")
    log.debug("get_metadata_raw: returning for %s data %s",tab,out)
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
    if "error" in metadata.keys():
        return metadata        
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    print("get_item_raw: pk_columns",str(pkcols))
    pkwhere, pkwhere_val = make_pk_where_clause(pk, pkcols, versioned)
    sql=f'SELECT * FROM {tab} {pkwhere}'
    log.debug("sql=%s",sql)
    try:
        data=dbengine.execute(sql,pkwhere_val)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_item_raw: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_item_raw: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out
    items = [dict(row) for row in data]
    columns = list(data.keys())
#        for r in items:
#            for k,v in r.items():
#                if type(v).__name__=="datetime":
#                    r[k]=v.strftime("%Y-%m-%d %H:%M:%S.%f")
    log.debug("columns: %s",columns)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=len(items)
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
    out={}
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
        try:
            _=dbengine.execute(sql)    
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
            last_stmt_has_errors(e_sqlalchemy, out)
            return out
        except Exception as e:
            log.debug("exception in get_next_seq: %s ",str(e))
            last_stmt_has_errors(e, out)
            return out
        out=nextval
    else:
        log.debug("in get_next_seq not sqlite")
        sql=f'SELECT NEXT VALUE FOR {seq}'
        log.debug("sql=%s",sql)
        try:
            #cursor = cnxn.cursor()
            data=dbengine.execute(sql)
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
            last_stmt_has_errors(e_sqlalchemy, out)
            return out
        except Exception as e:
            log.debug("exception in get_next_seq: %s ",str(e))
            last_stmt_has_errors(e, out)
            return out

        for row in data:
            out=row[0]
        log.debug("got sequence value %d",out)    
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
    out={}
    log.debug("in get_current_timestamp")
    sql='SELECT GETDATE()'
    log.debug("sql=%s",sql)
    try:
        #cursor = cnxn.cursor()
        data=dbengine.execute(sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_next_seq: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out
    for row in data:
        out=row[0]
    log.debug("got timestamp value %s",out)    
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
    log.debug("++++++++++entering repo_lookup_select")
    log.debug("repo_lookup_select: param id is <%s>",str(id))
    if is_id(id):
        reposql="select * from plainbi_lookup where id=?"
    else:
        reposql="select * from plainbi_lookup where alias=?"
    log.debug("repo_lookup_select: repo sql is <%s>",reposql)
    lkpq=repoengine.execute(reposql , id)
    lkp=[dict(r) for r in lkpq]
    log.debug("lkp=%s",str(lkp))
    sql=None
    execute_in_repodb=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                sql=lkp[0]["sql_query"]
                execute_in_repodb = lkp[0]["datasource_id"]==0
        else:
            log.debug("lkp list len is not 1")
    else:
        log.debug("lkp is not a dict, it is a %s",str(lkp.__class__))
        
    if sql is None:
        msg="no sql in repo_lookup_select"
        log.error(msg)
        return None,None,None,msg
    try:
        if execute_in_repodb:
            log.debug("lookup query execution in repodb")
            data=repoengine.execute(sql)
        else:
            log.debug("lookup query execution")
            data=dbengine.execute(sql)
        items = [dict(row) for row in data]
        columns = list(data.keys())
        total_count=len(items)
        return items,columns,total_count,"ok"
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in sql_select: %s",str(e_sqlalchemy))
        return None,None,None,e_sqlalchemy
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        return None,None,None,e

## repo lookup adhoc
def get_repo_adhoc_sql_stmt(repoengine,id):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    out={}
    log.debug("++++++++++entering get_repo_adhoc_sql_stmt")
    log.debug("get_repo_adhoc_sql_stmt: param id is <%s>",str(id))
    if is_id(id):
        reposql="select * from plainbi_adhoc where id=?"
    else:
        reposql="select * from plainbi_adhoc where alias=?"
    log.debug("repo_adhoc_select: repo sql is <%s>",reposql)
    try:
        lkpq=repoengine.execute(reposql , id)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_next_seq: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out
    lkp=[dict(r) for r in lkpq]
    sql=None
    execute_in_repodb=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                sql=lkp[0]["sql_query"]
                execute_in_repodb = lkp[0]["datasource_id"]==0
        else:
            log.debug("lkp list len is not 1")
    else:
        log.debug("lkp is not a dict, it is a %s",str(lkp.__class__))
    return sql, execute_in_repodb


## repo lookup adhoc
def repo_adhoc_select(repoengine,dbengine,id,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    log.debug("++++++++++entering repo_adhoc_select")
    log.debug("repo_adhoc_select: param id is <%s>",str(id))
    sql, execute_in_repodb = get_repo_adhoc_sql_stmt(repoengine,id)
    try:
        if execute_in_repodb:
            log.debug("adhoc query execution in repodb")
            data=repoengine.execute(sql)
        else:
            log.debug("adhoc query execution")
            data=dbengine.execute(sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in repo_adhoc_select: %s",str(e_sqlalchemy))
        return e_sqlalchemy
    except Exception as e:
        log.error("exception in repo_adhoc_select: %s",str(e))
        return e
    return data
