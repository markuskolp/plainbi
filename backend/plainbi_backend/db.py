# -*- coding: utf-8 -*-
"""
Created on Thu May  4 08:11:27 2023

@author: kribbel
"""
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import base64
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import unquote
from plainbi_backend.utils import is_id, last_stmt_has_errors, make_pk_where_clause
#import bcrypt
from plainbi_backend.config import config
from threading import Lock

config.database_lock = Lock()

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

repo_columns_to_hash = { "plainbi_user" : ["password_hash"], "plainbi_datasource" : ["db_pass_hash"] }

config.conn={}

def db_exec(engine,sql,params=None):
    log.debug("++++++++++ entering db_exec")
    log.debug("db_exec: param sql is <%s>",str(sql))
    log.debug("db_exec: params is <%s>",str(params))
    #
    is_select=False
    if not engine.url in config.conn.keys():
        config.conn[engine.url]=None
    #with engine.connect() as conn:
    #    res=execute(sql,params)
    #    return res
    if params is not None:
        if not isinstance(params, dict):
            log.warning("db_exec called with params WITHOUT dict")
    #sqlalchemy 2.0
    mysql=sqlalchemy.text(sql)

    with config.database_lock:
        log.debug("db_exec: check connection")
        if not isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            log.debug("db_exec: connect")
            config.conn[engine.url] = engine.connect()
    
        if config.conn[engine.url].closed:
            log.debug("db_exec: open connection")
            config.conn[engine.url] = engine.connect()
        log.debug("db_exec: execute")
    
        if sql.lower().strip().startswith("select"):
            log.debug("db_exec: sql is a select")
            is_select=True
        try:
            if params is not None:
                res=config.conn[engine.url].execute(mysql,params)
                #with engine.begin() as connection:
                #    res=connection.execute(mysql,params)
            else:
                res=config.conn[engine.url].execute(mysql)
                #with engine.begin() as connection:
                #    res=connection.execute(mysql)
            if int(sqlalchemy.__version__[:1])>1:
                if not is_select:
                    config.conn[engine.url].commit()
        except Exception as e:
            log.error("db_exec ERROR: %s",str(e))
            log.error("db_exec ERROR: SQL is %s",str(sql))
            log.error("db_exec ERROR: params are %s",str(params))
            raise e
        if is_select:
            log.debug("db_exec: is select and returns data")
            items = [row._asdict() for row in res]
            log.debug("db_exec: anz rows=%d",len(items))
            columns = list(res.keys())
        #close connection
        if isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            if not config.conn[engine.url].closed:
                config.conn[engine.url].close()
                log.debug("db_exec: connection closed")
            else:
                log.debug("db_exec: connection is already closed")
        else:
                log.debug("db_exec: connection is not sqlalchemy connection for closing")
        if is_select:
            log.debug("++++++++++ leaving db_exec with data result")
            return items, columns
        else:
            log.debug("++++++++++ leaving db_exec with dml result status")
            return res

def get_db_type(dbengine):
    if "sqlite" in str(dbengine.url).lower():
        return "sqlite"
    else:
        return "mssql"
def add_offset_limit(dbtyp,offset,limit,order_by):
    log.debug("++++++++++ entering add_offset_limit")
    sql=""
    if dbtyp=="mssql":
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        else:
            if limit is not None or offset is not None:
                sql+=" ORDER BY 1"
        if offset is not None:
            sql+=" OFFSET "+offset+ " ROWS"
        if limit is not None:
            sql+=" FETCH NEXT "+limit+" ROWS ONLY"
    elif dbtyp=="sqlite":
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        if limit is not None:
            sql+=" LIMIT "+limit
        else:
            sql+=" LIMIT -1"
        if offset is not None:
            sql+=" OFFSET "+offset
    log.debug("++++++++++ leaving add_offset_limit with <%s>",sql)
    return sql


def sql_select(dbengine,tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,versioned=False,is_repo=False,user_id=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    log.debug("++++++++++ entering sql_select")
    log.debug("sql_select: param tab is <%s>",tab)
    log.debug("sql_select: param order_by is <%s>",str(order_by))
    log.debug("sql_select: param offset is <%s>",str(offset))
    log.debug("sql_select: param limit is <%s>",str(limit))
    log.debug("sql_select: param filter is <%s>",str(filter))
    log.debug("sql_select: param with_total_count is <%s>",str(with_total_count))
    log.debug("sql_select: param where_clause is <%s>",str(where_clause))
    log.debug("sql_select: param versioned is <%s>",str(versioned))
    log.debug("sql_select: param is_repo is <%s>",str(is_repo))
    log.debug("sql_select: param user_id is <%s>",str(user_id))
    total_count=None
    my_where_clause=""
    w=where_clause
    tab_is_sql_stmt=False
    if len(tab.split(" "))==1:          # nur ein wort
        sql=f'SELECT * FROM {tab}'
        tab_is_sql_stmt = False
    else:                               # ein komplettes select statement expected
        sql=tab
        tab_is_sql_stmt = True
    if versioned:
        if w is not None:
            if len(my_where_clause)==0: my_where_clause=" WHERE "
            my_where_clause += "("+w+") AND is_current_and_active = 'Y'"
        else:
            if len(my_where_clause)==0: my_where_clause=" WHERE "
            my_where_clause += "is_current_and_active = 'Y'"
    else:
        if w is not None:
            if len(my_where_clause)==0: my_where_clause=" WHERE "
            my_where_clause += " ("+w+") "
    # check repo rights
    if is_repo and user_id is not None:
        my_where_clause = add_auth_to_where_clause(tab, my_where_clause, user_id)
        log.debug("sql_select auth added:%s",my_where_clause)
    if len(my_where_clause)>0:
        sql+=my_where_clause
    sql_without_orderby_offset_limit=sql
    sql+=add_offset_limit(get_db_type(dbengine),offset,limit,order_by)
    log.debug("sql_select: %s",sql)

    try:
        items,columns=db_exec(dbengine,sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in sql_select: %s",str(e_sqlalchemy))
        return None,None,None,e_sqlalchemy
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        return None,None,None,e
    
    log.debug("sql_select: anz rows=%d",len(items))
    if with_total_count:
        log.debug("check totalcount")
        sql_total_count=f'SELECT COUNT(*) AS total_count FROM ({sql_without_orderby_offset_limit}) x'
        item_total_count,columns_total_count=db_exec(dbengine,sql_total_count)
        total_count=(item_total_count[0])['total_count']
    return items,columns,total_count,"ok"


def get_metadata_raw(dbengine,tab,pk_column_list,versioned):
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
        log.debug("get_metadata_raw: mssql")
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query.replace('<fulltablename>',tab))
        log.debug("get_metadata_raw: returned error %s",str(e))
        if last_stmt_has_errors(e, out):
            log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
        #    
        log.debug("get_metadata_raw: 1")
        log.debug("get_metadata_raw: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            log.debug("get_metadata_raw: got some metadata from mssql")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1 and i["column_name"] != "invalid_from_dt"]
            else:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
            log.debug("get_metadata_raw from mssql: pkcols %s",str(pkcols))
            log.debug("get_metadata_raw from mssql: columns %s",str(columns))
            collist=[i["column_name"] for i in items]
            out["columns"]=collist
            out["column_data"]=items
    if "columns" not in out.keys():
        # nothing in metadata - get columns from query
        log.debug("get_metadata_raw: nothing in metadata - get columns from query")
        # nicht in metadaten gefunden
        try:
            sql=f'SELECT * FROM {tab} WHERE 1=0'
            log.debug("get_metadata_raw: sql=%s",sql)
            _,columns=db_exec(dbengine,sql)
            out["columns"]=columns
            #out["metadata"]=mitems
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_metadata:raw: %s",str(e_sqlalchemy))
            last_stmt_has_errors(e_sqlalchemy, out)
            log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
        except Exception as e:
            log.debug("exception in get_metadata_raw: error %s",str(e))
            last_stmt_has_errors(e, out)
            log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
    log.debug("sql_select in get_metadata_raw 4")
    out["pk_columns"]=pkcols
    log.debug("sql_select in get_metadata_raw 4 pk_column_list=%s",str(pk_column_list))
    if pk_column_list is not None:
        log.debug("sql_select in get_metadata_raw 5")
        if isinstance(pk_column_list, list):
            log.debug("sql_select in get_metadata_raw 6")
            if len(pk_column_list) > 0:
                log.debug("sql_select in get_metadata_raw 7")
                out["pk_columns"]=pk_column_list
                log.debug("get_metadata_raw returns parameter pk_column_list")
    else:
        log.debug("get_metadata_raw returns computedd column_list")
    log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
    return out

def get_item_raw(dbengine,tab,pk,pk_column_list=None,versioned=False,version_deleted=False, is_repo=False, user_id=None):
    """
    Hole einen bestimmten Datensatz aus einer Tabelle ub der Datenbank

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    pk_column_list : Wert des Datensatz Identifier (Primary Key)
    version : table is versioned
    version_deleted : return also delete item
    

    Returns
    -------
    dict mit den keys "data" ggf "errors"

    """
    log.debug("++++++++++ entering get_item_raw")
    log.debug("get_item_raw: param tab is <%s>",str(tab))
    log.debug("get_item_raw: param pk is <%s>",str(pk))
    log.debug("get_item_raw: param pk_column_list is <%s>",str(pk_column_list))
    log.debug("get_item_raw: param versioned is <%s>",str(versioned))
    log.debug("get_item_raw: param version_deleted is <%s>",str(version_deleted))
    out={}
    log.debug("in get_item raw")
    metadata=get_metadata_raw(dbengine,tab,pk_column_list,versioned)
    if "error" in metadata.keys():
        return metadata        
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    print("get_item_raw: pk_columns",str(pkcols))
    pkwhere, pkwhere_params = make_pk_where_clause(pk, pkcols, versioned, version_deleted)
    if is_repo and user_id is not None:
        # check repo rights
        pkwhere = add_auth_to_where_clause(tab, pkwhere, user_id)
        log.debug("sql_select auth added:%s",pkwhere)
    sql=f'SELECT * FROM {tab} {pkwhere}'
    log.debug("sql=%s",sql)
    try:
        items, columns = db_exec(dbengine,sql,pkwhere_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_item_raw: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_item_raw: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out

    log.debug("columns: %s",columns)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=len(items)
    log.debug("++++++++++ leaving get_item_raw returning %s",str(out))
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
        itemseq={ "seq" : seq}
        sql="SELECT curval FROM plainbi_seq WHERE sequence_name=:seq"
        log.debug("sql=%s ,%s",sql,str(itemseq))
        items, columns = db_exec(dbengine,sql,itemseq)
        log.debug("sql done")
        log.debug("items %s",items)
        curval=items[0]["curval"]
        nextval=curval+1
        sql=f"UPDATE plainbi_seq SET curval={nextval} WHERE sequence_name='{seq}'"
        log.debug("sql=%s",sql)
        try:
            _=db_exec(dbengine,sql)    
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
        sql=f'SELECT NEXT VALUE FOR {seq} AS nextval'
        log.debug("sql=%s",sql)
        try:
            #cursor = cnxn.cursor()
            items, columns = db_exec(dbengine,sql)
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
            last_stmt_has_errors(e_sqlalchemy, out)
            return out
        except Exception as e:
            log.debug("exception in get_next_seq: %s ",str(e))
            last_stmt_has_errors(e, out)
            return out

        out=items[0]["nextval"] 
        #for row in data:
        #    out=row.nextval
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
    sql='SELECT GETDATE() as ts'
    log.debug("sql=%s",sql)
    try:
        #cursor = cnxn.cursor()
        items, columns = db_exec(dbengine,sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_next_seq: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out
    out=items[0]["ts"] 
    #for row in data:
    #    out=row.ts
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
        reposql_params={ "id" : id}
        reposql="select * from plainbi_lookup where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_lookup where alias=:alias"
    log.debug("repo_lookup_select: repo sql is <%s>",reposql)
    lkp,lkp_columns = db_exec(repoengine, reposql , reposql_params)
    #lkp=[r._asdict() for r in lkpq]
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
        log.debug("lkp is not a list, it is a %s",str(lkp.__class__))
        
    if sql is None:
        msg="no sql in repo_lookup_select"
        log.error(msg)
        return None,None,None,msg
    try:
        if execute_in_repodb:
            log.debug("lookup query execution in repodb")
            items, columns = db_exec(repoengine,sql)
        else:
            log.debug("lookup query execution")
            items, columns = db_exec(dbengine,sql)
        #items = [row._asdict() for row in data]
        #columns = list(data.keys())
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
        reposql_params={ "id" : id}
        reposql="select * from plainbi_adhoc where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_adhoc where alias=:alias"
    log.debug("repo_adhoc_select: repo sql is <%s>",reposql)
    try:
        lkp, lkp_columns = db_exec(repoengine, reposql , reposql_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        return out
    except Exception as e:
        log.debug("exception in get_next_seq: %s ",str(e))
        last_stmt_has_errors(e, out)
        return out
    #lkp=[r._asdict() for r in lkpq]
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


# repo lookup adhoc
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
    if execute_in_repodb:
        log.debug("adhoc query execution in repodb")
        items, columns = db_exec(repoengine,sql)
    else:
        log.debug("adhoc query execution")
        items, columns =db_exec(dbengine,sql)
    return items, columns


def check_hash_columns(tab,item):
    log.debug("check_hash_columns for %s item %s",tab,item)
    if tab in repo_columns_to_hash.keys():
        for c in repo_columns_to_hash[tab]:
            if c in item.keys():
                p=config.bcrypt.generate_password_hash(item[c])
                #p=bcrypt.hashpw(item[c].encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
                item[c]=p.decode()
                log.debug("check_hash_columns: hashed %s.%s",tab,c)

## crud ops
def db_ins(dbeng,tab,item,pkcols=None,is_versioned=False,seq=None,changed_by=None,is_repo=False, user_id=None):
    """ 
    insert record
    """
    log.debug("++++++++++ entering db_ins")
    log.debug("db_ins: param tab is <%s>",str(tab))
    log.debug("db_ins: param item is <%s>",str(item))
    log.debug("db_ins: param pkcols is <%s>",str(pkcols))
    log.debug("db_ins: param is_versioned is <%s>",str(is_versioned))
    log.debug("db_ins: param seq is <%s>",str(seq))
    out={}
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols,versioned=is_versioned)
    log.info("db_ins after get_metadata_raw %s",str(metadata))
    myitem=item
    if "error" in metadata.keys():
        log.debug("db_ins: error in get_metadata_raw returned")
        return metadata
    pkcols=metadata["pk_columns"]
    log.info("db_ins: now pkols=%s",str(pkcols))
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("db_ins: implicit pk first column")
    s=None
    # check hash columns
    if is_repo: check_hash_columns(tab,myitem)
    #                    
    if is_versioned:
        log.debug("db_ins: versioned mode" )
        ts=get_current_timestamp(dbeng)
        log.debug("db_ins: ts=%s",ts)
        myitem["valid_from_dt"]=ts
        myitem["invalid_from_dt"]="9999-12-31 00:00:00"
        myitem["last_changed_dt"]=ts
        myitem["is_latest_period"]="Y"
        myitem["is_deleted"]="N"
        myitem["is_current_and_active"]="Y"
        log.debug("db_ins: check last_changed_by user=%s", changed_by)
        if "last_changed_by" in metadata["columns"] and changed_by is not None:
            myitem["last_changed_by"]=changed_by
    else:
        log.debug("db_ins: non versioned mode" )
    log.debug("db_ins: prepare sql" )
    log.debug("add missing pk columns ")
    # add missing primary key columns
    for pkcol in pkcols:
        if pkcol not in myitem.keys():
            # id ist nicht in data list so generate
            log.debug("db_ins: pk column %s is not in data list so generate",pkcol)
            myitem[pkcol]=None
    # check if sequence should be applied
    pkout={}
    for pkcol in pkcols:
        if myitem[pkcol] is None:
            if seq is not None:
                # override none valued sequence pk column with seq 
                if len(pkcols)>1:
                    out["error"]="sequences are only allowed for single column primary keys"
                    return out
                s=get_next_seq(dbeng,seq)
                log.debug("db_ins: got seq %d",s)
                myitem[pkcol]=s
                pkout[pkcol]=s
                log.debug("db_ins: seqence %s inserted",seq)
        else:
            pkout[pkcol]=myitem[pkcol]

    # we have to check if there is an deleted record for this pk
    if is_versioned:
        delrec=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned,version_deleted=True)
        if "total_count" in delrec.keys():
            if delrec["total_count"]>0:
                # there is an existing record -> terminate id
                pkwhere, pkwhere_params = make_pk_where_clause(pkout,pkcols,is_versioned,version_deleted=True)
                delitem={}
                delitem["invalid_from_dt"]=ts
                delitem["last_changed_dt"]=ts
                delitem.update(pkwhere_params)
                log.debug("marker values length is %d",len(delitem))
                log.debug("db_ins: terminate deleted record")
                dsql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
                log.debug("db_ins: terminate rec sql %s",dsql)
                try:
                    db_exec(dbeng,dsql,delitem)
                    log.debug("dbins: deleted record terminated")
                except SQLAlchemyError as e_sqlalchemy:
                    print("sqlalchemy deleted record terminated",str(e_sqlalchemy))
                    last_stmt_has_errors(e_sqlalchemy, out)
                    if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
                    return out
                except Exception as e:
                    print("excp deleted record terminated",str(e))
                    last_stmt_has_errors(e, out)
                    return out
               
    param_list=[":"+k for k in myitem.keys()]
    col_list=[k for k in myitem.keys()]
    log.debug("db_ins: construct sql" )
    param_list_str=",".join(param_list)
    col_list_str=",".join(col_list)
    sql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
    log.debug("db_ins sql: %s",sql)
    try:
        db_exec(dbeng,sql,myitem)
    except SQLAlchemyError as e_sqlalchemy:
        print("sqlalchemy",str(e_sqlalchemy))
        last_stmt_has_errors(e_sqlalchemy, out)
        if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
        return out
    except Exception as e:
        print("excp",str(e))
        last_stmt_has_errors(e, out)
        return out
    # read new record from database and send it back
    out=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned,is_repo=is_repo,user_id=user_id)
    log.debug("++++++++++ leaving db_ins returning %s", str(out))
    return out

## crud ops
def db_upd(dbeng,tab,pk,item,pkcols,is_versioned,changed_by=None,is_repo=False, user_id=None):
    log.debug("++++++++++ entering db_upd")
    log.debug("db_upd: param tab is <%s>",str(tab))
    log.debug("db_upd: param pk is <%s>",str(pk))
    log.debug("db_upd: pkcols tab is <%s>",str(pkcols))
    log.debug("db_upd: param is_versioned is <%s>",str(is_versioned))
    out={}
    log.debug("item-keys %s",item.keys())
    myitem=item
    
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols,versioned=is_versioned)
    if "error" in metadata.keys():
        return metadata
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("update_item implicit pk first column")

    chkout=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["error"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
            return out
    else:
        out["error"]="PK check nicht erfolgreich"
        return out
    
    pkwhere, pkwhere_params = make_pk_where_clause(pk,pkcols,is_versioned)
    log.debug("update_item: pkwhere %s",pkwhere)

    # check hash columns
    if is_repo: check_hash_columns(tab,myitem)

    log.debug("pk_columns %s",pkcols)
    if is_versioned:
        log.debug("update_item: 1")
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbeng)
        # hole then alten Datensatz aus der DB mit dem angegebenen pk
        cur_row=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        upditem={}
        upditem["invalid_from_dt"]=ts
        upditem["last_changed_dt"]=ts
        upditem.update(pkwhere_params)
        log.debug("marker values length is %d",len(upditem))
        updsql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
        log.debug("db_upd newrec sql: %s", updsql)
        db_exec(dbeng, updsql, upditem)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        newrec=reclist[0]
        # überschreibe mit neuen werten
        newrec.update(myitem)
        newrec["valid_from_dt"]=ts
        newrec["invalid_from_dt"]="9999-12-31 00:00:00"
        newrec["last_changed_dt"]=ts
        newrec["is_latest_period"]='Y'
        newrec["is_current_and_active"]='Y'
        if "last_changed_by" in metadata["columns"] and changed_by is not None:
            newrec["last_changed_by"]=changed_by
        log.debug("db_upd: construct sql" )
        param_list=[":"+k for k in newrec.keys()]
        col_list=[k for k in newrec.keys()]
        param_list_str=",".join(param_list)
        col_list_str=",".join(col_list)
        newsql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
        log.debug("db_upd newrec sql: %s",newsql)
        try:
            db_exec(dbeng,newsql,newrec)
        except SQLAlchemyError as e_sqlalchemy:
            last_stmt_has_errors(e_sqlalchemy, out)
            if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            last_stmt_has_errors(e, out)
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
    else:
        # nicht versionierter Standardfall
        othercols=[col for col in myitem.keys() if col not in pkcols]
        log.debug("othercols %s",othercols)
        osetexp=[k+"=:"+k for k in othercols]
        osetexp_str=",".join(osetexp)
        myitem.update(pkwhere_params)
        sql=f"UPDATE {tab} SET {osetexp_str} {pkwhere}"
        log.debug("update item sql %s",sql)
        log.debug("update item params %s",myitem)
        try:
            db_exec(dbeng,sql,myitem)
        except SQLAlchemyError as e_sqlalchemy:
            last_stmt_has_errors(e_sqlalchemy, out)
            if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            last_stmt_has_errors(e, out)
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
    # den aktuellen Datensatz wieder aus der DB holen und zurückgeben (könnte ja Triggers geben)
    out=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned,is_repo=is_repo,user_id=user_id)
    log.debug("++++++++++ leaving db_upd returning %s", str(out))
    return out

def db_passwd(dbeng,u,p):
    log.debug("++++++++++ entering db_passwd")
    log.debug("db_passwd: param u is <%s>",str(u))
    log.debug("db_passwd: param p (hashed) is <%s>",str(p))
    out={}
    sql="UPDATE plainbi_user SET password_hash=:password_hash WHERE username=:username"
    try:
        db_exec(dbeng,sql,{ "password_hash":p,"username":u})
    except SQLAlchemyError as e_sqlalchemy:
        last_stmt_has_errors(e_sqlalchemy, out)
        if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
        log.debug("++++++++++ leaving db_passwd returning %s", str(out))
        return out
    except Exception as e:
        last_stmt_has_errors(e, out)
        log.debug("++++++++++ leaving db_passwd returning %s", str(out))
        return out
    return out


def db_del(dbeng,tab,pk,pkcols,is_versioned=False,changed_by=None,is_repo=False, user_id=None):
    log.debug("++++++++++ entering db_del")
    log.debug("db_del: param tab is <%s>",str(tab))
    log.debug("db_del: param pk is <%s>",str(pk))
    log.debug("db_del: pkcols tab is <%s>",str(pkcols))
    log.debug("db_del: param is_versioned is <%s>",str(is_versioned))
    # check options
    out={}
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols,versioned=is_versioned)
    if "error" in metadata.keys():
        log.debug("++++++++++ leaving db_del returning %s", str(metadata))
        return metadata
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("db_del implicit pk first column")

    chkout=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols)
    if "total_count" in chkout.keys():
        if chkout["total_count"]==0:
            out["error"]="PK ist nicht vorhanden"
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
    else:
        out["error"]="PK check nicht erfolgreich"
        log.debug("++++++++++ leaving db_del returning %s", str(out))
        return out

    pkwhere, pkwhere_params = make_pk_where_clause(pk,pkcols,is_versioned)
    log.debug("db_del: pkwhere %s",pkwhere)
        
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbeng)
        cur_row=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        upditem={}
        upditem["invalid_from_dt"]=ts
        upditem["last_changed_dt"]=ts
        upditem.update(pkwhere_params)
        log.debug("marker values length is %d",len(upditem))
        sql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'"
        db_exec(dbeng,sql,upditem)
        # neuen datensatz anlegen
        # die alten werte mit ggf den neuen überschreiben
        reclist=cur_row["data"]
        newrec=reclist[0]
        newrec["valid_from_dt"]=ts
        newrec["invalid_from_dt"]="9999-12-31 00:00:00"
        newrec["last_changed_dt"]=ts
        newrec["is_latest_period"]='Y'
        newrec["is_current_and_active"]='N'
        newrec["is_deleted"]='Y'
        if "last_changed_by" in metadata["columns"] and changed_by is not None:
            newrec["last_changed_by"]=changed_by
        log.debug("db_upd: construct sql" )
        param_list=[":"+k for k in newrec.keys()]
        col_list=[k for k in newrec.keys()]
        param_list_str=",".join(param_list)
        col_list_str=",".join(col_list)
        newsql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
        log.debug("db_del: %s",newsql)
        try:
            db_exec(dbeng,newsql,newrec)
        except SQLAlchemyError as e_sqlalchemy:
            last_stmt_has_errors(e_sqlalchemy, out)
            if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
        except Exception as e:
            last_stmt_has_errors(e, out)
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
    else:
        sql=f"DELETE FROM {tab} {pkwhere}"
        log.debug("db_del sql %s",sql)
        log.debug("db_del marker values length is %d",len(pkwhere_params))
        try:
            db_exec(dbeng,sql,pkwhere_params)
        except SQLAlchemyError as e_sqlalchemy:
            last_stmt_has_errors(e_sqlalchemy, out)
            if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
        except Exception as e:
            last_stmt_has_errors(e, out)
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
    log.debug("++++++++++ leaving db_del returning %s", str(out))
    return out

def get_profile(repoengine,u):
    usr_sql = "select * from plainbi_user where username=:username"
    usr_items, usr_columns = db_exec(repoengine,usr_sql,{ "username" : u })
    prof = {}
    if len(usr_items)==1:
        prof["username"] = (usr_items[0])["username"]
        prof["email"] = (usr_items[0])["email"]
        prof["fullname"] = (usr_items[0])["fullname"]
        user_id = (usr_items[0])["id"]
        prof["user_id"] = user_id
        role_id=(usr_items[0])["role_id"]
        print(role_id)
        role_sql = "select * from plainbi_role where id=:role_id"
        role_items, role_columns = db_exec(repoengine,role_sql,{ "role_id": role_id})
        if len(role_items)==1:
            prof["role"] = (role_items[0])["name"]
        grp_sql = "select g.id,g.name,g.alias,* from plainbi_group g join plainbi_user_to_group ug on ug.group_id=g.id where ug.user_id=:user_id"
        grp_items, grp_columns = db_exec(repoengine,grp_sql,{"user_id":user_id})
        l_groups=[]
        for i in grp_items:
            l_groups.append({ "name" : i["name"], "alias" : i["alias"] })
        prof["groups"] = l_groups
    return prof 

    
def db_adduser(dbeng,usr,fullname=None,email=None,pwd=None,is_admin=False):
    """
    ,username text
    ,email text
    ,fullname text
    ,password_hash text
    ,role_id int
    
    example: db_adduser(repoengine,"joe",fullname="Johannes Kribbel",pwd="joe123")
    """
    if is_admin:
        role_id=1
    else:
        role_id=2
    item = { "id":None, "username":usr,"fullname":fullname,"role_id":role_id}
    if email is not None:
        item["email"]=email
    if pwd is not None:
        #p=bcrypt.hashpw(pwd.encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
        p=config.bcrypt.generate_password_hash(pwd)
        item["password_hash"]=p.decode()
    x=db_ins(dbeng,"plainbi_user",item,pkcols='id',seq="user")
    return x

def add_auth_to_where_clause(tab,where_clause,user_id):
    log.debug("++++++++++ entering add_auth_to_where_clause")
    log.debug("add_auth_to_where_clause: param tab is <%s>",str(tab))
    log.debug("add_auth_to_where_clause: param where_clause is <%s>",str(where_clause))
    log.debug("add_auth_to_where_clause: param user_id is <%s>",str(user_id))
    w = where_clause
    if w is None: w=""
    if tab == 'plainbi_application' and user_id is not None:
        log.debug("add_auth_to_where_clause: apply auth for application")
        if len(w)==0: 
            w=" WHERE "
        else:
            w+=" AND "
        w+=f"""id in (
  select atg.application_id
  from plainbi_application_to_group atg
  join plainbi_user_to_group utg
  on atg.group_id=utg.group_id 
  join plainbi_user u
  on utg.user_id = u.id
  where utg.user_id = {user_id}
  union
  select a.id
  from plainbi_application a
  cross join plainbi_user u
  where u.id = {user_id}
  and u.role_id = 1
)"""
    if tab == 'plainbi_adhoc' and user_id is not None:
        log.debug("add_auth_to_where_clause: apply auth for adhoc")
        if len(w)==0: 
            w=" WHERE "
        else:
            w+=" AND "
        w+=f"""id in (
  select atg.adhoc_id
  from plainbi_adhoc_to_group atg
  join plainbi_user_to_group utg
  on atg.group_id=utg.group_id 
  join plainbi_user u
  on utg.user_id = u.id
  where utg.user_id = {user_id}
  union
  select a.id
  from plainbi_adhoc a
  cross join plainbi_user u
  where u.id = {user_id}
  and u.role_id = 1
  union
  select a.id
  from plainbi_adhoc a
  where a.owner_user_id = {user_id}
)"""
    if tab == 'plainbi_external_resource' and user_id is not None:
        log.debug("add_auth_to_where_clause: apply auth for external_resource")
        if len(w)==0: 
            w=" WHERE "
        else:
            w+=" AND "
        w+=f"""id in (
  select atg.external_resource_id
  from plainbi_external_resource_to_group atg
  join plainbi_user_to_group utg
  on atg.group_id=utg.group_id 
  join plainbi_user u
  on utg.user_id = u.id
  where utg.user_id = {user_id}
  union
  select a.id
  from plainbi_external_resource a
  cross join plainbi_user u
  where u.id = {user_id}
  and u.role_id = 1
)"""
    log.debug("++++++++++ leaving add_auth_to_where_clause with: %s",w)
    return w

#b = base64.b64encode(bytes('your string', 'utf-8')) # bytes
#base64_str = b.decode('utf-8') # convert bytes to string
    

def db_connect(enginestr, params=None):
    log.debug("++++++++++ entering db_connect")
    log.debug("db_connect: param enginestr is <%s>",str(enginestr))
    log.debug("db_connect: param params is <%s>",str(params))
    if params is not None:
        dbengine = sqlalchemy.create_engine(enginestr % params)
    else:
        dbengine = sqlalchemy.create_engine(enginestr)
    log.info("db_connect: dbengine url %s",dbengine.url)
    log.debug("++++++++++ leaving db_connect")
    return dbengine

def audit(tokdata,req,id=None,msg=None):
    log.debug("++++++++++ entering audit")
    if isinstance(tokdata,dict):
        usrnam=tokdata["username"]
    else:
        usrnam=tokdata
    log.debug('Audit rec: usr=%s,url=%s,id=%s,msg=%s',usrnam,req.url,str(id),str(msg))
    #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.get_json())}
    #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":None}
    #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.get_json(force=True))}
    audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.data)}
    audit_sql="insert into plainbi_audit (username,t,url,id,remark,request_method,request_body) values (:username,CURRENT_TIMESTAMP,:url,:id,:remark,:method,:body)"
    try:
        log.debug('Audit sql:%s',audit_sql )
        log.debug('Audit params:%s',audit_params )
        db_exec(config.repoengine, audit_sql, audit_params)
        log.debug('Audit executed')
    except SQLAlchemyError as e_sqlalchemy:
        log.error("audit error: %s",str(e_sqlalchemy))
        log.debug("continuing")
    except Exception as e:
        log.error("audit exception: %s",str(e))
        log.debug("continuing")
    log.debug("++++++++++ leaving audit")
