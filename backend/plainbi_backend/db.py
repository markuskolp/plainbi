# -*- coding: utf-8 -*-
"""
Created on Thu May  4 08:11:27 2023

@author: kribbel
"""
from plainbi_backend.config import config
import logging
#log = logging.getLogger(config.logger_name)
log = logging.getLogger(__name__)

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from plainbi_backend.utils import is_id, last_stmt_has_errors, make_pk_where_clause
#import bcrypt
from threading import Lock

config.database_lock = Lock()

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
    dbgindent="    "
    log.debug(dbgindent+"++++++++++ entering db_exec")
    log.debug(dbgindent+"db_exec: param sql is <%s>",str(sql))
    log.debug(dbgindent+"db_exec: params is <%s>",str(params))
    #
    is_select=False
    if not engine.url in config.conn.keys():
        config.conn[engine.url]=None
    #with engine.connect() as conn:
    #    res=execute(sql,params)
    #    return res
    if params is not None:
        if not isinstance(params, dict):
            log.warning(dbgindent+"db_exec called with params WITHOUT dict")
    #sqlalchemy 2.0
    mysql=sqlalchemy.text(sql)

    # using the flask server with wgsi requires sequential access to the sqlite repo
    with config.database_lock:
        log.debug(dbgindent+"db_exec: check connection")
        if not isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            log.debug(dbgindent+"db_exec: connect")
            config.conn[engine.url] = engine.connect()
    
        if config.conn[engine.url].closed:
            log.debug(dbgindent+"db_exec: open connection")
            config.conn[engine.url] = engine.connect()
        log.debug(dbgindent+"db_exec: execute")
    
        if sql.lower().strip().startswith("select"):
            log.debug(dbgindent+"db_exec: sql is a select")
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
            log.error(dbgindent+"db_exec ERROR: %s",str(e))
            log.error(dbgindent+"db_exec ERROR: SQL is %s",str(sql))
            log.error(dbgindent+"db_exec ERROR: params are %s",str(params))
            if "Can't reconnect until invalid transaction is rolled back.  Please rollback()" in str(e):
                log.error(dbgindent+"Try to rollback")
                config.conn[engine.url].rollback()
                log.error(dbgindent+"Rollback done")
            raise e
        if is_select:
            log.debug(dbgindent+"db_exec: is select and returns data")
            items = [row._asdict() for row in res]
            log.debug(dbgindent+"db_exec: anz rows=%d",len(items))
            columns = list(res.keys())
        #close connection
        if isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            if not config.conn[engine.url].closed:
                config.conn[engine.url].close()
                log.debug(dbgindent+"db_exec: connection closed")
            else:
                log.debug(dbgindent+"db_exec: connection is already closed")
        else:
                log.debug(dbgindent+"db_exec: connection is not sqlalchemy connection for closing")
        if is_select:
            log.debug(dbgindent+"++++++++++ leaving db_exec with data result")
            return items, columns
        else:
            log.debug(dbgindent+"++++++++++ leaving db_exec with dml result status")
            return res

def get_db_type(dbengine):
    if "sqlite" in str(dbengine.url).lower():
        return "sqlite"
    elif "oracle" in str(dbengine.url).lower():
        return "oracle"
    elif "post" in str(dbengine.url).lower():
        return "postgres"
    else:
        return "mssql"

def db_connect_test(d):
    log.debug("  ++++++++++ entering db_connect_test")
    ty=get_db_type(d)
    ok=False
    if ty=="oracle":
        sql="SELECT 1 FROM DUAL"
    else:
        sql="SELECT 1"
    try:
        item_total_count,columns_total_count=db_exec(d,sql,params=None)
    except Exception as e:
        log.error("db_connect_test failed %s",str(e))
        ok=False
    if item_total_count is not None:
        ok=True
    else:
        log.error("db_connect_test did not return test row")
        ok=False
    log.debug("  ++++++++++ leaving db_connect_test")
    return ok

def add_offset_limit(dbtyp,offset,limit,order_by):
    log.debug("++++++++++ entering add_offset_limit")
    sql=""
    if dbtyp=="mssql":
        # in Microsoft SQL Server a OFFSET or LIMIT clause requires a ORDER_BY
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
    elif dbtyp=="postgres":
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        if limit is not None:
            sql+=" LIMIT "+limit
        if offset is not None:
            sql+=" OFFSET "+offset
    elif dbtyp=="oracle":
        if order_by is not None:
            sql+=" ORDER BY "+order_by.replace(":"," ")
        if offset is not None:
            sql+=" OFFSET "+offset+" ROWS"
        if limit is not None:
            sql+=" FETCH NEXT "+limit+" ROWS ONLY"
    log.debug("++++++++++ leaving add_offset_limit with <%s>",sql)
    return sql


def sql_select(dbengine,tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,versioned=False,is_repo=False,user_id=None, customsql=None):
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
    log.debug("sql_select: param customsql is <%s>",str(customsql))
    db_typ = get_db_type(dbengine)
    total_count=None
    my_where_clause=""
    w=where_clause
    tab_is_sql_stmt=False
    tabalias="x"
    if len(tab.split(" "))==1:          # nur ein wort
        if customsql is not None:
            log.debug("get_item_raw get custom sql id=%s",customsql)
            csql, csql_exec_in_repo = get_repo_customsql_sql_stmt(config.repoengine, customsql)
            sql=f'SELECT {tabalias}.* FROM ({csql}) {tabalias} '
        else:
            sql=f'SELECT {tabalias}.* FROM {tab} {tabalias} '
        tab_is_sql_stmt = False
    else:                               # ein komplettes select statement expected
        sql=tab
        tab_is_sql_stmt = True          # for later use
    if w is not None:
        # a where clause is specified as parameter
        if len(my_where_clause.strip())==0: 
            my_where_clause=" WHERE "
        else:
            my_where_clause+=" AND "
        my_where_clause += "("+w+")"
    if versioned:
        if len(my_where_clause.strip())==0: 
            my_where_clause=" WHERE "
        else:
            my_where_clause+=" AND "
        my_where_clause += "is_current_and_active = 'Y'"
    if filter is not None:
        metadata=get_metadata_raw(dbengine,tab,pk_column_list=None,versioned=versioned)
        if len(my_where_clause.strip())==0: 
            my_where_clause=" WHERE "
        else:
            my_where_clause+=" AND "
        my_where_clause = add_filter_to_where_clause(db_typ,tab, my_where_clause, filter, metadata["columns"],is_versioned=versioned )
    # check repo rights
    if is_repo and user_id is not None:
        my_where_clause = add_auth_to_where_clause(tab, my_where_clause, user_id)
        log.debug("sql_select auth added:%s",my_where_clause)
    # filter
    # now add where clause
    if len(my_where_clause)>0:
        sql+=my_where_clause
    sql_without_orderby_offset_limit=sql
    sql+=add_offset_limit(db_typ,offset,limit,order_by)
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
    log.debug("get_metadata_raw: param versioned is <%s>",str(versioned))
    cache_key=str(dbengine.url)+"||||"+str(tab)+'||||'
    if versioned: cache_key+= "v|||"
    log.debug("get_metadata_raw: cache key prefix is %s",cache_key)
    if isinstance(pk_column_list,list):
         cache_key+= ";".join(pk_column_list) if pk_column_list is not None else "-"
    else:
        cache_key+=pk_column_list if pk_column_list is not None else ""
    log.debug("get_metadata_raw: cache key is %s",cache_key)
    if config.use_cache:
        if hasattr(config,"metadataraw_cache"):
            if cache_key in config.metadataraw_cache.keys():
                log.debug("get_metadata_raw: metadataraw_cache hit")
                return config.metadataraw_cache[cache_key]
        else:
            config.metadataraw_cache={}
            log.debug("get_metadata_raw: cache created")
    out={}
    dbtype=get_db_type(dbengine)
    pkcols=[]
    items = None
    if dbtype == "mssql":
        # for mssql try metadata search
        log.debug("get_metadata_raw: mssql")
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query.replace('<fulltablename>',tab))
        #log.debug("get_metadata_raw: returned error %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_raw"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
            log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
        #log.debug("get_metadata_raw: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            log.debug("get_metadata_raw: got some metadata from mssql")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1 and i["column_name"] != "invalid_from_dt"]
            else:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
            #log.debug("get_metadata_raw from mssql: pkcols %s",str(pkcols))
            #log.debug("get_metadata_raw from mssql: columns %s",str(columns))
            collist=[i["column_name"] for i in items]
            out["columns"]=collist
            out["column_data"]=items
    elif dbtype == "sqlite":
        # for sqlite try metadata search
        log.debug("get_metadata_raw-sqlite: sqlite")
        metadata_col_query_sqlite="select * from pragma_table_info('<fulltablename>')"
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query_sqlite.replace('<fulltablename>',tab))
        #log.debug("get_metadata_raw-sqlite: returned %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_raw"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
            log.debug("++++++++++ leaving get_metadata_raw-sqlite returning for %s data %s",tab,out)
            return out
        #    
        #log.debug("get_metadata_raw-sqlite: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            log.debug("get_metadata_raw-sqlite: got some metadata from sqlite")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["name"] for i in items if i["pk"]==1 and i["name"] != "invalid_from_dt"]
            else:
                pkcols=[i["name"] for i in items if i["pk"]==1]
            #log.debug("get_metadata_raw from sqlite: pkcols %s",str(pkcols))
            #log.debug("get_metadata_raw from sqlite: columns %s",str(columns))
            collist=[i["name"] for i in items]
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
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-get_metadata_raw-columns"
                out["message"]+=" beim Lesen der Tabellenspalten Metadaten"
            log.error("++++++++++ leaving get_metadata_raw with error returning for %s data %s",tab,out)
            return out
        except Exception as e:
            log.error("exception in get_metadata_raw: error %s",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_metadata_raw-columns"
                out["message"]+=" beim Lesen der Tabellenspalten Metadaten"
            log.error("++++++++++ leaving get_metadata_raw with error returning for %s data %s",tab,out)
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
        log.debug("get_metadata_raw returns computed column_list")
    log.debug("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
    config.metadataraw_cache[cache_key] = out
    return out

def get_item_raw(dbengine,tab,pk,pk_column_list=None,versioned=False,version_deleted=False, is_repo=False, user_id=None, customsql=None):
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
    log.debug("++++++++++ entering get_item_raw[%s]")
    log.debug("get_item_raw[%s]: param tab is <%s>",str(tab),str(tab))
    log.debug("get_item_raw[%s]: param pk is <%s>",str(tab),str(pk))
    log.debug("get_item_raw[%s]: param pk_column_list is <%s>",str(tab),str(pk_column_list))
    log.debug("get_item_raw[%s]: param versioned is <%s>",str(tab),str(versioned))
    log.debug("get_item_raw[%s]: param version_deleted is <%s>",str(tab),str(version_deleted))
    log.debug("get_item_raw[%s]: param is_repo is <%s>",str(tab),str(is_repo))
    log.debug("get_item_raw[%s]: param user_id is <%s>",str(tab),str(user_id))
    log.debug("get_item_raw[%s]: param customsql is <%s>",str(tab),str(customsql))
    out={}
    metadata=get_metadata_raw(dbengine,tab,pk_column_list,versioned)
    if "error" in metadata.keys():
        return metadata
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("get_item_raw[%s]: implicit pk first column",str(tab))
    log.debug("get_item_raw[%s]: pk_columns %s",str(tab),str(pkcols))
    tabalias="x"
    pkwhere, pkwhere_params = make_pk_where_clause(pk, pkcols, versioned, version_deleted, table_alias=tabalias)
    log.debug("get_item_raw[%s]: pkwhere <%s>, pkwhere_params <%s>",str(tab), str(pkwhere), str(pkwhere_params))
    if is_repo and user_id is not None:
        # check repo rights
        pkwhere = add_auth_to_where_clause(tab, pkwhere, user_id)
        log.debug("get_item_raw[%s]: sql_select auth added: %s",str(tab), pkwhere)
    if customsql is not None:
        log.debug("get_item_raw[%s]: get custom sql id=%s",str(tab),customsql)
        csql, csql_exec_in_repo = get_repo_customsql_sql_stmt(config.repoengine, customsql)
        log.debug("get_item_raw[%s]: got custom sql id=%s",str(tab),csql)
        sql=f'SELECT {tabalias}.* FROM ({csql}) {tabalias} {pkwhere}'
    else:    
        sql=f'SELECT {tabalias}.* FROM {tab} {tabalias} {pkwhere}'
    log.debug("get_item_raw[%s]: sql=%s",str(tab),sql)
    try:
        items, columns = db_exec(dbengine,sql,pkwhere_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("get_item_raw[%s]: sqlalchemy exception: %s",str(tab),str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_item_raw"
            out["message"]+=" beim Lesen einer Tabelle"
        return out
    except Exception as e:
        log.error("get_item_raw[%s]: exception: %s ",str(tab),str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_item_raw"
            out["message"]+=" beim Lesen einer Tabelle"
        return out

    log.debug("get_item_raw[%s]: columns: %s",str(tab),columns)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=len(items)
    log.debug("++++++++++ leaving get_item_raw[%s]:  returning %s",str(tab),str(out))
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
    dbtyp = get_db_type(dbengine)
    if dbtyp =="sqlite":
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
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-get_next_seq"
                out["message"]+=" beim Erzeugen einer Sequenz-Id"
            return out
        except Exception as e:
            log.error("exception in get_next_seq: %s ",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_next_seq"
                out["message"]+=" beim Erzeugen einer Sequenz-Id"
            return out
        out=nextval
    else:
        log.debug("in get_next_seq not sqlite")
        if dbtyp == "mssql":
            sql=f'SELECT NEXT VALUE FOR {seq} AS nextval'
        elif dbtyp == "postgres":
            sql=f"SELECT nextval('{seq}') AS nextval"
        elif dbtyp == "oracle":
            sql=f"SELECT {seq}.nextval AS nextval from dual"
        log.debug("sql=%s",sql)
        try:
            #cursor = cnxn.cursor()
            items, columns = db_exec(dbengine,sql)
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-get_next_seq-sqlite"
                out["message"]+=" beim Erzeugen einer Sequenz-Id"
            return out
        except Exception as e:
            log.error("exception in get_next_seq: %s ",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_next_seq-sqlite"
                out["message"]+=" beim Erzeugen einer Sequenz-Id"
            return out

        out=items[0]["nextval"] 
        #for row in data:
        #    out=row.nextval
        log.debug("got sequence value %d",out)    
    return out

def get_dbversion(dbengine):
    out={}
    log.debug("in get_dbversion")
    db_typ = get_db_type(dbengine)
    if db_typ=="mssql":
        sql="Select @@version as version"
    elif db_typ=="sqllite":
        sql="select sqlite_version() as version"
    elif db_typ=="oracle":
        sql="select version from v$instance"
    elif db_typ=="postgres":
        sql="select version() as version"
    else:
        return None
    try:
        items, columns = db_exec(dbengine,sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_dbversion: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_dbversion"
            out["message"]+=" beim Abfragen der Datenbankversion"
        return out
    except Exception as e:
        log.error("exception in get_dbversion: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_dbversion"
            out["message"]+=" beim Abfragen der Datenbankversion"
        return out
    out=items[0]["version"]
    return out

def get_current_timestamp(dbengine):
    """
    Hole die aktuelle Zeit

    Returns
    -------
    aktuelle Zeit

    """
    out={}
    log.debug("in get_current_timestamp")
    sql='SELECT GETDATE() as ts'
    log.debug("sql=%s",sql)
    try:
        #cursor = cnxn.cursor()
        items, columns = db_exec(dbengine,sql)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_current_timestamp: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_current_timestamp"
            out["message"]+=" beim Erzeugen eines aktuellen Timestamps"
        return out
    except Exception as e:
        log.error("exception in get_current_timestamp: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_current_timestamp"
            out["message"]+=" beim Erzeugen eines aktuellen Timestamps"
        return out
    out=items[0]["ts"] 
    #for row in data:
    #    out=row.ts
    log.debug("got timestamp value %s",out)    
    return out

## repo lookup adhoc
def repo_lookup_select(repoengine,dbengine,id,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,username=None):
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
    if username is not None:
        sql=sql.replace("$(APP_USER)",username)
        log.debug("lkp sql username replaced")
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
    adhocid = -999
    order_by_def = None
    adhocdesc = None
    if is_id(id):
        adhocid=id
        reposql_params={ "id" : id}
        reposql="select * from plainbi_adhoc where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_adhoc where alias=:alias"
    log.debug("repo_adhoc_select: repo sql is <%s>",reposql)
    try:
        lkp, lkp_columns = db_exec(repoengine, reposql , reposql_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_repo_adhoc_sql_stmt: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_repo_adhoc_sql_stmt"
            out["message"]+=" beim Lesen der Adhoc-Abfrage"
        return out
    except Exception as e:
        log.error("exception in get_repo_adhoc_sql_stmt: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_repo_adhoc_sql_stmt"
            out["message"]+=" beim Lesen der Adhoc-Abfrage"
        return out
    #lkp=[r._asdict() for r in lkpq]
    sql=None
    execute_in_repodb=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                sql=lkp[0]["sql_query"]
                adhocid=lkp[0]["id"]
                execute_in_repodb = lkp[0]["datasource_id"]==0
                order_by_def=lkp[0]["order_by_default"]
                adhocdesc=lkp[0]["description"]
        else:
            log.warn("get_repo_adhoc_sql_stmt:lkp list len is not 1")
    else:
        log.warn("lkp is not a dict, it is a %s",str(lkp.__class__))
    return sql, execute_in_repodb, adhocid, order_by_def, adhocdesc

## repo customsql 
def get_repo_customsql_sql_stmt(repoengine,id):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    out={}
    log.debug("++++++++++entering get_repo_customsql_sql_stmt")
    log.debug("get_repo_customsql_sql_stmt: param id is <%s>",str(id))
    if is_id(id):
        reposql_params={ "id" : id}
        reposql="select * from plainbi_customsql where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_customsql where alias=:alias"
    log.debug("get_repo_customsql_sql_stmt: repo sql is <%s>",reposql)
    try:
        lkp, lkp_columns = db_exec(repoengine, reposql , reposql_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_repo_customsql_sql_stmt: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_repo_customsql_sql_stmt"
            out["message"]+=" beim Lesen der CustomSQL-Abfrage"
        return out
    except Exception as e:
        log.error("exception in get_repo_customsql_sql_stmt: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_repo_customsql_sql_stmt"
            out["message"]+=" beim Lesen der CustomSQL-Abfrage"
        return out
    sql=None
    execute_in_repodb=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                sql=lkp[0]["sql_query"]
        else:
            log.debug("lkp list len is not 1, it is %d",len(lkp))
    else:
        log.debug("lkp is not a dict, it is a %s",str(lkp.__class__))
    log.debug("++++++++++leaving get_repo_customsql_sql_stmt with sql=%s",sql)
    return sql, execute_in_repodb


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
def db_ins(dbeng,tab,item,pkcols=None,is_versioned=False,seq=None,changed_by=None,is_repo=False, user_id=None, customsql=None):
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
                    out["error"]="sequences-only-allowed-for-single-column-pk"
                    out["message"]="Sequenzen sind nur beim Primary Keys mit einer Spalte erlaubt"
                    out["detail"]="sequences are only allowed for single column primary keys"
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
                    log.error("sqlalchemy deleted record terminated; %s",str(e_sqlalchemy))
                    if last_stmt_has_errors(e_sqlalchemy, out):
                        out["error"]+="-db_ins-vers"
                        out["message"]+=" beim Einfügen eines neuen versionierten Datensatzes"
                    return out
                except Exception as e:
                    log.error("excp deleted record terminated: %s",str(e))
                    if last_stmt_has_errors(e, out):
                        out["error"]+="-db_ins-vers"
                        out["message"]+=" beim Einfügen eines neuen versionierten Datensatzes"
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
        log.error("db_ins: sqlalchemy error: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-db_ins"
            out["message"]+=" beim Einfügen eines neuen Datensatzes"
        return out
    except Exception as e:
        log.error("db_ins: exception %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-db_ins"
            out["message"]+=" beim Einfügen eines neuen Datensatzes"
        return out
    # read new record from database and send it back
    out=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned,is_repo=is_repo,user_id=user_id,customsql=customsql)
    log.debug("++++++++++ leaving db_ins returning %s", str(out))
    return out

## crud ops
def db_upd(dbeng,tab,pk,item,pkcols,is_versioned,changed_by=None,is_repo=False, user_id=None,customsql=None):
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
            out["error"]="db_upd-id-not-found"
            out["message"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
            return out
    else:
        out["error"]="db_upd-pk-check-failed"
        out["message"]="Datensatz in %s mit PK=%s ist nicht vorhanden" % (tab,pk)
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
        try:
            db_exec(dbeng, updsql, upditem)
        except SQLAlchemyError as e_sqlalchemy:
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_upd-old-vers"
                out["message"]+=" beim Aktualisieren des alten versionierten Datensatzes"
            log.error("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_upd-old-vers"
                out["message"]+=" beim Aktualisieren des alten versionierten Datensatzes"
            log.error("++++++++++ leaving db_upd returning %s", str(out))
            return out
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
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_upd-vers"
                out["message"]+=" beim Aktualisieren eines versionierten Datensatzes"
            log.error("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_upd-vers"
                out["message"]+=" beim Aktualisieren eines versionierten Datensatzes"
            log.error("++++++++++ leaving db_upd returning %s", str(out))
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
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_upd"
                out["message"]+=" beim Aktualisieren eines Datensatzes"
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_upd"
                out["message"]+=" beim Aktualisieren eines Datensatzes"
            log.debug("++++++++++ leaving db_upd returning %s", str(out))
            return out
    # den aktuellen Datensatz wieder aus der DB holen und zurückgeben (könnte ja Triggers geben)
    out=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned,is_repo=is_repo,user_id=user_id,customsql=customsql)
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
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-db_passwd"
            out["message"]+=" beim Aktualisieren des Passwortes"
        if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
        log.error("++++++++++ leaving db_passwd returning %s", str(out))
        return out
    except Exception as e:
        if last_stmt_has_errors(e, out):
            out["error"]+="-db_passwd"
            out["message"]+=" beim Aktualisieren des Passwortes"
        log.error("++++++++++ leaving db_passwd returning %s", str(out))
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
            out["error"]="db_del-pk-id-not-found"
            out["message"]="Der zu löschende Datensatz wurde nicht gefunden"
            log.debug("++++++++++ leaving db_del returning %s", str(out))
            return out
    else:
        out["error"]="db_del-pk-check-id-not-found"
        out["message"]="Der zu löschende Datensatz wurde nicht gefunden"
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
        try:
            db_exec(dbeng,sql,upditem)
        except SQLAlchemyError as e_sqlalchemy:
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_del-old-vers"
                out["message"]+=" beim Löschen des alten versionierten Datensatzes"
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_del-old-vers"
                out["message"]+=" beim Löschen des alten versionierten Datensatzes"
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
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
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_del-vers"
                out["message"]+=" beim Löschen eines versionierten Datensatzes"
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_del-vers"
                out["message"]+=" beim Löschen eines versionierten Datensatzes"
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
    else:
        sql=f"DELETE FROM {tab} {pkwhere}"
        log.debug("db_del sql %s",sql)
        log.debug("db_del marker values length is %d",len(pkwhere_params))
        try:
            db_exec(dbeng,sql,pkwhere_params)
        except SQLAlchemyError as e_sqlalchemy:
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_del-vers"
                out["message"]+=" beim Löschen eines Datensatzes"
            if "sql" in e_sqlalchemy.__dict__.keys(): out["error_sql"]=e_sqlalchemy.__dict__['sql']
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_del-vers"
                out["message"]+=" beim Löschen eines Datensatzes"
            log.error("++++++++++ leaving db_del returning %s", str(out))
            return out
    log.debug("++++++++++ leaving db_del returning %s", str(out))
    return out

def get_profile(repoengine,u):
    """
    profile eines Users
    """
    if config.use_cache:
        if hasattr(config,"profile_cache"):
            if u in config.profile_cache.keys():
                log.debug("get_profile: cache hit")
                return config.profile_cache[u]
        else:
            config.profile_cache={}
            log.debug("get_profile: cache created")

    usr_sql = "select * from plainbi_user where username=:username"
    usr_items, usr_columns = db_exec(repoengine,usr_sql,{ "username" : u })
    prof = {}
    if len(usr_items)==1:
        # user was found in table
        prof["username"] = (usr_items[0])["username"]
        prof["email"] = (usr_items[0])["email"]
        prof["fullname"] = (usr_items[0])["fullname"]
        user_id = (usr_items[0])["id"]
        prof["user_id"] = user_id
        role_id=(usr_items[0])["role_id"]
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
        # add to cache
        config.profile_cache[u] = prof
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

    db_typ = get_db_type(dbeng)
    log.debug("db_adduser: database type is %s",db_typ)
    if db_typ=="sqlite":
        sequenz="user"
    elif db_typ in ("mssql","postgres","oracle"):
        sequenz="plainbi_user_seq"
    else:
        log.error("db_adduser: unknown repo database type")
        sequenz=None
    log.debug("db_adduser: database seq is %s",sequenz)
    x=db_ins(dbeng,"plainbi_user",item,pkcols='id',seq=sequenz)
    return x

def add_filter_to_where_clause(dbtyp, tab, where_clause, filter, columns, is_versioned=False):
    log.debug("++++++++++ entering add_filter_to_where_clause")
    log.debug("add_filter_to_where_clause: dbtyp tab is <%s>",str(dbtyp))
    log.debug("add_filter_to_where_clause: param tab is <%s>",str(tab))
    log.debug("add_filter_to_where_clause: param filter is <%s>",str(filter))
    log.debug("add_filter_to_where_clause: param columns is <%s>",str(columns))
    if dbtyp=="mssql":
        concat_operator="+"
    else:
        concat_operator="||"
    w = where_clause
    if w is None: w=""
    w+="("
    if isinstance(filter,dict):
        #filter is per column
        l_cexp=[]
        for k,v in filter.items():
            l_cexp.append("lower(cast(coalesce("+k+",'') as varchar)) like lower('%"+v+"%')")
        cexp="("+" AND ".join(l_cexp)+")"
        w+=cexp
    else:
        #filter is global fulltext search over all columns
        filter_tokens=filter.split(" ")
        cnt=0
        cnttok=0
        if True: # method with string concate all columns
            csep="|#|#|-|"
            cexp=""
            for c in columns:
                lc=c.lower()
                if is_versioned and lc in ("valid_from_dt","invalid_from_dt","last_changed_dt","is_deleted","is_latest_period","is_current_and_active"): continue
                cnt=cnt+1
                if cnt>1: cexp+=concat_operator+"'"+csep+"'"+concat_operator
                cexp+="lower(cast(coalesce("+lc+",'') as varchar))"
            log.debug("filter cexp:%s",cexp)
            for i,ftok in enumerate(filter_tokens):
                lftok=ftok.lower()
                if i>0:
                    w+=" AND "
                w+=cexp+" like lower('%"+lftok+"%')"
        else:
            for ftok in filter_tokens:
                cnttok+=1
                lftok=ftok.lower()
                for c in columns:
                    lc=c.lower()
                    # do not filter in version columns
                    if is_versioned and lc in ("valid_from_dt","invalid_from_dt","last_changed_dt","is_deleted","is_latest_period","is_current_and_active"): continue
                    cnt=cnt+1
                    if cnt>1: w+=" or "
                    w+="lower(cast("+lc+" as varchar)) like lower('%"+lftok+"%')"
    w+=")"
    log.debug("++++++++++ leaving add_filter_to_where_clause with: %s",w)
    return w


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
    if enginestr is None:
        log.error("PLAINBI needs a connection string in the .env File to properly connect to a database")
    
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
    if id is not None:
        log.debug("Audit Adhoc %d",id)
    if "/login" in req.url: 
        audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body": None}
    else:
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
