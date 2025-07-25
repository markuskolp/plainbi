# -*- coding: utf-8 -*-
"""
Created on Thu May  4 08:11:27 2023

@author: kribbel
"""
import base64
import os
from plainbi_backend.config import config
import logging
import inspect
from datetime import datetime

#log = logging.getLogger(config.logger_name)
log = logging.getLogger(__name__)

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from plainbi_backend.utils import is_id, last_stmt_has_errors, make_pk_where_clause, urlsafe_decode_params,add_filter_to_where_clause,dbg,err,warn,show_call_stack
#import bcrypt
from threading import Lock

config.database_lock = Lock()

metadata_col_query_mssql = """SELECT 
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

metadata_col_query_sqlite="select * from pragma_table_info('<fulltablename>')"

metadata_col_query_postgres="""SELECT
    current_database() AS database_name,
    c.table_schema AS schema_name,
    c.table_name,
    current_database()||'-'||c.table_schema||'.'||c.table_name AS full_table_name,
    c.column_name,
    c.ordinal_position as column_id,
    c.data_type,
    c.character_maximum_length  as max_length,
    c.numeric_precision  as precision,
    c.numeric_scale as scale,
    case when pk.position_in_pk is not null then 1 else 0 end as is_primary_key
from information_schema.columns c
LEFT JOIN (
    SELECT
        tc.table_schema,
        tc.table_name,
        kcu.column_name,
        kcu.ordinal_position AS position_in_pk
    FROM
        information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.constraint_type = 'PRIMARY KEY'
) AS pk
ON c.table_schema = pk.table_schema
AND c.table_name = pk.table_name
AND c.column_name = pk.column_name
where 1=1
and current_database()||'-'||c.table_schema||'.'||c.table_name = '<fulltablename>'
"""

metadata_col_query_oracle="""SELECT
    to_char(null) AS database_name,
    atc.owner AS schema_name,
    atc.table_name,
    atc.owner||'.'||atc.table_name AS full_table_name,
    atc.column_name,
    atc.column_id,
    atc.data_type,
    atc.data_length  as max_length,
    atc.data_precision  as precision,
    atc.data_scale as scale,
    case when acc.owner is not null then 1 else 0 end as is_primary_key
from all_tab_columns atc
LEFT JOIN all_constraints ac
ON atc.table_name = ac.table_name
AND atc.owner = ac.owner
AND ac.constraint_type='P'
LEFT JOIN all_cons_columns acc
ON ac.owner=acc.owner
AND ac.constraint_name=acc.constraint_name
AND atc.column_name=acc.column_name
where 1=1
and atc.owner||'.'||atc.table_name = UPPER('<fulltablename>')
"""


repo_columns_to_hash = { "plainbi_user" : ["password_hash"], "plainbi_datasource" : ["db_pass_hash"] }

config.conn={}

   
def db_exec(engine, sql, params=None, metadata=None):
    dbg(f"+++ entering {inspect.currentframe().f_code.co_name} "+str(sql)[:50]+" ...")
    
    dbg("sql is <%s>",str(sql),dbglevel=2)
    dbg("sql params are <%s>",str(params),dbglevel=3)
    #
    is_select=False
    if not engine.url in config.conn.keys():
        config.conn[engine.url]=None
    if params is not None:
        if not (isinstance(params, dict) or isinstance(params, list)):
            warn("called with params WITHOUT dict or list of dict")
    dbtyp=get_db_type(engine)
    # using the flask server with wgsi requires sequential access to the sqlite repo
    with config.database_lock:
        dbg("check connection")
        if not isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            dbg("connect")
            try:
                config.conn[engine.url] = engine.connect()
            except Exception as e_connect:
                err("cannot connect to database: %s",str(e_connect))
                log.exception(e_connect)
                raise e_connect
        if config.conn[engine.url].closed:
            dbg("open connection")
            config.conn[engine.url] = engine.connect()
        dbg("execute")
        dml_anz=0
        if not isinstance(sql,list):
            stmts=[(sql,params)]
        else:
            stmts=[]
            for i,s in enumerate(sql):
               stmts.append((sql[i],params[i]))
        stmt_anz=len(stmts)
        for stmt_nr,stmt in enumerate(stmts):
            dbg("sql entry tuple %d/%d %s",stmt_nr,stmt_anz,str(stmt)[:25]+" ...")
            mysqltxt=stmt[0]
            mysql=sqlalchemy.text(mysqltxt)
            myparams=stmt[1]
            if mysqltxt.lower().strip().startswith("select") or mysqltxt.lower().strip().startswith("with"):
                dbg("sql is a select statement")
                is_select=True
            else:
                is_select=False
                dml_anz+=1 
            try:
                if myparams is not None:
                    # handle encodings
                    myparams=urlsafe_decode_params(myparams)
                    if dbtyp=="oracle" and metadata is not None:
                        if isinstance(metadata,list):
                            mymetadata=metadata[stmt_nr]
                        else:
                            mymetadata=metadata
                        handle_oracle_date_literals(myparams,mymetadata)
                    # exec in database
                    res=config.conn[engine.url].execute(mysql,myparams)
                    dbg("sql=%s params=%s",mysql,myparams,dbglevel=3)
                else:
                    res=config.conn[engine.url].execute(mysql)
                    dbg("sql=%s",mysql,dbglevel=3)
            except Exception as e:
                err("ERROR: %s",str(e))
                err("ERROR: SQL is %s",str(mysqltxt))
                err("ERROR: params are %s",str(myparams))
                if "Can't reconnect until invalid transaction is rolled back.  Please rollback()" in str(e):
                    err("Try to rollback")
                    config.conn[engine.url].rollback()
                    err("Rollback done")
                if "current transaction is aborted, commands ignored until end of transaction block" in str(e):
                    err("Try to rollback (postgres transaction aborted)")
                    config.conn[engine.url].rollback()
                    err("Rollback done (postgres transaction aborted)")
                if dbtyp == "postgres":
                    err("Try to rollback (postgres transaction)")
                    config.conn[engine.url].rollback()
                    err("Rollback done (postgres transaction)")
                raise e
            #if not is_select:
            #    config.conn[engine.url].commit()
            #   dbg("committed")
            if is_select:
                dbg("is a select statement and returns data")
                items = [row._asdict() for row in res]
                dbg("anz rows=%d",len(items))
                columns = list(res.keys())
        # commit at the end if there was any dml statement
        if dml_anz>0:
            config.conn[engine.url].commit()
            dbg("committed")
        #close connection
        if isinstance(config.conn[engine.url], sqlalchemy.engine.base.Connection):
            if not config.conn[engine.url].closed:
                config.conn[engine.url].close()
                dbg("connection closed")
            else:
                dbg("connection is already closed")
        else:
            dbg("connection is not sqlalchemy connection for closing")
        if is_select:
            dbg("+++ leaving with data result")
            return items, columns
        else:
            dbg("+++ leaving with dml result status")
            return res

def get_db_type(dbengine):
    """
    get type of database by looking at the sqlalchemy connect string
    default is mssql
    """
    if "sqlite" in str(dbengine.url).lower():
        return "sqlite"
    elif "oracle" in str(dbengine.url).lower():
        return "oracle"
    elif "post" in str(dbengine.url).lower():
        return "postgres"
    else:
        return "mssql"

def db_connect_test(db):
    """
    test if a connection string or connection is working
    """
    dbg("  ++++++++++ entering db_connect_test")
    if isinstance(db, str):
        # parameter is a string so we need to connect first
        d=db_connect(db)
    else:
        # assuming that parameter db is already a sqlalchemy engine object
        d=db
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
        log.exception(e)
        ok=False
        return ok
    if item_total_count is not None:
        ok=True
    else:
        log.error("db_connect_test did not return test row")
        ok=False
    dbg("  ++++++++++ leaving db_connect_test")
    return ok

def add_offset_limit(dbtyp,offset,limit,order_by):
    dbg("++++++++++ entering add_offset_limit")
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
    dbg("++++++++++ leaving add_offset_limit with <%s>",sql)
    return sql

def get_selectliststr(column_list,tabalias):
    if column_list is not None:
        if isinstance(column_list,str):
           mycols=column_list.split(",")
        else:
           mycols=column_list
        selectliststr = ",".join([tabalias+"."+c.strip() for c in mycols])
    else:
        selectliststr=tabalias+".*"
    return selectliststr


def sql_select(dbengine,tab,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,versioned=False,is_repo=False,user_id=None, customsql=None,column_list=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    dbg("++++++++++ entering sql_select")
    db_typ = get_db_type(dbengine)
    total_count=None
    my_where_clause=""
    my_where_clause_params=None
    w=where_clause
    tab_is_sql_stmt=False
    tabalias="x"
    selectliststr=get_selectliststr(column_list,tabalias)
    if len(tab.split(" "))==1:          # nur ein wort
        if customsql is not None:
            dbg("get_item_raw get custom sql id=%s",customsql)
            csql, csql_exec_in_repo = get_repo_customsql_sql_stmt(config.repoengine, customsql)
            sql=f'SELECT {selectliststr} FROM ({csql}) {tabalias} '
        else:
            sql=f'SELECT {selectliststr} FROM {tab} {tabalias} '
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
        if column_list is not None:
            if isinstance(column_list,str):
                # column list is a comma separated string
                mycolumns=[c.strip() for c in column_list.split(",")]
            else:
                # column_list shoe already be a list 
                mycolumns=column_list
        else:
            # column list comes (usually) from metadata
            mycolumns=metadata["columns"]
        my_where_clause, my_where_clause_params = add_filter_to_where_clause(db_typ, tab, my_where_clause, filter, mycolumns, is_versioned=versioned )
        dbg("my_where_clause:%s",my_where_clause)
        dbg("my_where_clause_params:%s",str(my_where_clause_params))
    # check repo rights
    if is_repo and user_id is not None:
        my_where_clause = add_auth_to_where_clause(tab, my_where_clause, user_id)
        dbg("sql_select auth added:%s",my_where_clause)
    # filter
    # now add where clause
    if len(my_where_clause)>0:
        sql+=my_where_clause
    sql_without_orderby_offset_limit=sql
    sql+=add_offset_limit(db_typ,offset,limit,order_by)
    dbg("sql_select: %s",sql)
    try:
        items,columns=db_exec(dbengine,sql, my_where_clause_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in sql_select: %s",str(e_sqlalchemy))
        log.exception(e_sqlalchemy)
        log.error("sql_select: --- information about error above ---")
        log.error("sql_select: param tab is <%s>",tab)
        log.error("sql_select: param order_by is <%s>",str(order_by))
        log.error("sql_select: param offset is <%s>",str(offset))
        log.error("sql_select: param limit is <%s>",str(limit))
        log.error("sql_select: param filter is <%s>",str(filter))
        log.error("sql_select: param with_total_count is <%s>",str(with_total_count))
        log.error("sql_select: param where_clause is <%s>",str(where_clause))
        log.error("sql_select: param versioned is <%s>",str(versioned))
        log.error("sql_select: param is_repo is <%s>",str(is_repo))
        log.error("sql_select: param user_id is <%s>",str(user_id))
        log.error("sql_select: param customsql is <%s>",str(customsql))
        log.error("sql_select: --- end information about error above ---")
        return None,None,None,e_sqlalchemy
    except Exception as e:
        log.error("exception in sql_select: %s",str(e))
        log.exception(e)
        log.error("sql_select: --- information about error above ---")
        log.error("sql_select: param tab is <%s>",tab)
        log.error("sql_select: param order_by is <%s>",str(order_by))
        log.error("sql_select: param offset is <%s>",str(offset))
        log.error("sql_select: param limit is <%s>",str(limit))
        log.error("sql_select: param filter is <%s>",str(filter))
        log.error("sql_select: param with_total_count is <%s>",str(with_total_count))
        log.error("sql_select: param where_clause is <%s>",str(where_clause))
        log.error("sql_select: param versioned is <%s>",str(versioned))
        log.error("sql_select: param is_repo is <%s>",str(is_repo))
        log.error("sql_select: param user_id is <%s>",str(user_id))
        log.error("sql_select: param customsql is <%s>",str(customsql))
        log.error("sql_select: --- end information about error above ---")
        return None,None,None,e
    
    dbg("sql_select: anz rows=%d",len(items))
    if with_total_count:
        dbg("check totalcount")
        sql_total_count=f'SELECT COUNT(*) AS total_count FROM ({sql_without_orderby_offset_limit}) x'
        item_total_count,columns_total_count=db_exec(dbengine,sql_total_count,my_where_clause_params)
        total_count=(item_total_count[0])['total_count']
    return items,columns,total_count,"ok"


def get_metadata_raw(dbengine,tab,pk_column_list=None,versioned=False):
    """
    holt die struktur einer Tabelle entweder aus sys.columns oder aus der query selbst
    überschreibe die PK spezifikation wenn pk_column_list befüllit ist
    retunrs dict mit keys "pk_columns", "error"
    """
    dbg("++++++++++ entering get_metadata_raw")
    dbg("get_metadata_raw: param tab is <%s>",str(tab))
    dbg("get_metadata_raw: param pk_column_list (override) is <%s>",str(pk_column_list))
    dbg("get_metadata_raw: param versioned is <%s>",str(versioned))
    cache_key=str(dbengine.url)+"||||"+str(tab)+'||||'
    if versioned: cache_key+= "v|||"
    dbg("get_metadata_raw: cache key prefix is %s",cache_key)
    if isinstance(pk_column_list,list):
         cache_key+= ";".join(pk_column_list) if pk_column_list is not None else "-"
    else:
        cache_key+=pk_column_list if pk_column_list is not None else ""
    dbg("get_metadata_raw: cache key is %s",cache_key)
    if config.use_cache:
        if hasattr(config,"metadataraw_cache"):
            if cache_key in config.metadataraw_cache.keys():
                dbg("get_metadata_raw: metadataraw_cache hit")
                return config.metadataraw_cache[cache_key]
        else:
            config.metadataraw_cache={}
            dbg("get_metadata_raw: cache created")
    out={}
    dbtype=get_db_type(dbengine)
    pkcols=[]
    items = None
    if dbtype == "mssql":
        # for mssql try metadata search
        dbg("get_metadata_raw: mssql")
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query_mssql.replace('<fulltablename>',tab))
        #dbg("get_metadata_raw: returned error %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_raw"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
            dbg("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
        #dbg("get_metadata_raw: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            dbg("get_metadata_raw: got some metadata from mssql")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1 and i["column_name"] != "invalid_from_dt"]
            else:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
            #dbg("get_metadata_raw from mssql: pkcols %s",str(pkcols))
            #dbg("get_metadata_raw from mssql: columns %s",str(columns))
            collist=[i["column_name"] for i in items]
            out["columns"]=collist
            out["column_data"]=items
    elif dbtype == "sqlite":
        # for sqlite try metadata search
        dbg("get_metadata_raw-sqlite: sqlite")
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query_sqlite.replace('<fulltablename>',tab))
        #dbg("get_metadata_raw-sqlite: returned %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_raw"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
            dbg("++++++++++ leaving get_metadata_raw-sqlite returning for %s data %s",tab,out)
            return out
        #    
        #dbg("get_metadata_raw-sqlite: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            dbg("get_metadata_raw-sqlite: got some metadata from sqlite")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["name"] for i in items if i["pk"]==1 and i["name"] != "invalid_from_dt"]
            else:
                pkcols=[i["name"] for i in items if i["pk"]==1]
            #dbg("get_metadata_raw from sqlite: pkcols %s",str(pkcols))
            #dbg("get_metadata_raw from sqlite: columns %s",str(columns))
            collist=[i["name"] for i in items]
            out["columns"]=collist
            out["column_data"]=items
    elif dbtype == "postgres":
        # for postgres try metadata search
        dbg("get_metadata_raw: postgres")
        collist=[]
        items,columns,total_count,e=sql_select(dbengine,metadata_col_query_postgres.replace('<fulltablename>',tab))
        #dbg("get_metadata_raw: returned error %s",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_raw"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
            dbg("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
            return out
        #dbg("get_metadata_raw: 1 items=%s",str(items))
        if items is not None and len(items)>0:
            # got some metadata
            dbg("get_metadata_raw: got some metadata from mssql")
            # es gibt etwas in den sqlserver metadaten
            if versioned:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1 and i["column_name"] != "invalid_from_dt"]
            else:
                pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
            #dbg("get_metadata_raw from mssql: pkcols %s",str(pkcols))
            #dbg("get_metadata_raw from mssql: columns %s",str(columns))
            collist=[i["column_name"] for i in items]
            out["columns"]=collist
            out["column_data"]=items
    elif dbtype == "oracle":
            # for oracle try metadata search
            dbg("get_metadata_raw: oracle")
            collist=[]
            items,columns,total_count,e=sql_select(dbengine,metadata_col_query_oracle.replace('<fulltablename>',tab))
            #dbg("get_metadata_raw: returned error %s",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_metadata_raw"
                out["message"]+=" beim Lesen der Tabellen Metadaten"
                dbg("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
                return out
            #dbg("get_metadata_raw: 1 items=%s",str(items))
            if items is not None and len(items)>0:
                # got some metadata
                dbg("get_metadata_raw: got some metadata from mssql")
                # es gibt etwas in den sqlserver metadaten
                if versioned:
                    pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1 and i["column_name"] != "invalid_from_dt"]
                else:
                    pkcols=[i["column_name"] for i in items if i["is_primary_key"]==1]
                #dbg("get_metadata_raw from mssql: pkcols %s",str(pkcols))
                #dbg("get_metadata_raw from mssql: columns %s",str(columns))
                collist=[i["column_name"] for i in items]
                out["columns"]=collist
                out["column_data"]=items
        
    if "columns" not in out.keys():
        # nothing in metadata - get columns from query
        dbg("get_metadata_raw: nothing in metadata - get columns from query")
        # nicht in metadaten gefunden
        try:
            sql=f'SELECT * FROM {tab} WHERE 1=0'
            dbg("get_metadata_raw: sql=%s",sql)
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
    
    dbg("sql_select in get_metadata_raw 4")
    out["pk_columns"]=pkcols
    dbg("sql_select in get_metadata_raw 4 pk_column_list=%s",str(pk_column_list))
    if pk_column_list is not None:
        dbg("sql_select in get_metadata_raw 5")
        if isinstance(pk_column_list, list):
            dbg("sql_select in get_metadata_raw 6")
            if len(pk_column_list) > 0:
                dbg("sql_select in get_metadata_raw 7")
                out["pk_columns"]=pk_column_list
                dbg("get_metadata_raw returns parameter pk_column_list")
    else:
        dbg("get_metadata_raw returns computed column_list")
    dbg("++++++++++ leaving get_metadata_raw returning for %s data %s",tab,out)
    config.metadataraw_cache[cache_key] = out
    return out


def get_item_raw(dbengine,tab,pk,pk_column_list=None,column_list=None,versioned=False,version_deleted=False, is_repo=False, user_id=None, customsql=None):
    """
    Hole einen bestimmten Datensatz aus einer Tabelle ub der Datenbank

    Parameters
    ----------
    tab : Name der Tabelle
    pk : Wert des Datensatz Identifier (Primary Key)
    pk_column_list : Wert des Datensatz Identifier (Primary Key)
    column_list: comma separated list of columns to get
    version : table is versioned
    version_deleted : return also delete item

    Returns
    -------
    dict mit den keys "data" ggf "errors"

    """
    dbg("++++++++++ entering get_item_raw[%s]")
    dbg("get_item_raw[%s]: param tab is <%s>",str(tab),str(tab))
    dbg("get_item_raw[%s]: param pk is <%s>",str(tab),str(pk))
    dbg("get_item_raw[%s]: param pk_column_list is <%s>",str(tab),str(pk_column_list))
    dbg("get_item_raw[%s]: param column_list is <%s>",str(tab),str(column_list))
    dbg("get_item_raw[%s]: param versioned is <%s>",str(tab),str(versioned))
    dbg("get_item_raw[%s]: param version_deleted is <%s>",str(tab),str(version_deleted))
    dbg("get_item_raw[%s]: param is_repo is <%s>",str(tab),str(is_repo))
    dbg("get_item_raw[%s]: param user_id is <%s>",str(tab),str(user_id))
    dbg("get_item_raw[%s]: param customsql is <%s>",str(tab),str(customsql))
    out={}
    metadata=get_metadata_raw(dbengine,tab,pk_column_list,versioned)
    if "error" in metadata.keys():
        return metadata
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("get_item_raw[%s]: implicit pk first column",str(tab))
    dbg("get_item_raw[%s]: pk_columns %s",str(tab),str(pkcols))
    tabalias="x"
    selectliststr=get_selectliststr(column_list,tabalias)
    pkwhere, pkwhere_params = make_pk_where_clause(pk, pkcols, versioned, version_deleted, table_alias=tabalias)
    dbg("get_item_raw[%s]: pkwhere <%s>, pkwhere_params <%s>",str(tab), str(pkwhere), str(pkwhere_params))
    if is_repo and user_id is not None:
        # check repo rights
        pkwhere = add_auth_to_where_clause(tab, pkwhere, user_id)
        dbg("get_item_raw[%s]: sql_select auth added: %s",str(tab), pkwhere)
    if customsql is not None:
        dbg("get_item_raw[%s]: get custom sql id=%s",str(tab),customsql)
        csql, csql_exec_in_repo = get_repo_customsql_sql_stmt(config.repoengine, customsql)
        dbg("get_item_raw[%s]: got custom sql id=%s",str(tab),csql)
        sql=f'SELECT {selectliststr} FROM ({csql}) {tabalias} {pkwhere}'
    else:    
        sql=f'SELECT {selectliststr} FROM {tab} {tabalias} {pkwhere}'
    try:
        items, columns = db_exec(dbengine,sql,pkwhere_params,metadata)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("get_item_raw[%s]: sqlalchemy exception: %s",str(tab),str(e_sqlalchemy))
        log.error("get_item_raw[%s]: failing sql=%s",str(tab),sql)
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_item_raw"
            out["message"]+=" beim Lesen einer Tabelle"
        return out
    except Exception as e:
        log.error("get_item_raw[%s]: exception: %s ",str(tab),str(e))
        log.error("get_item_raw[%s]: failing sql=%s",str(tab),sql)
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_item_raw"
            out["message"]+=" beim Lesen einer Tabelle"
        return out

    dbg("get_item_raw[%s]: columns: %s",str(tab),columns)
    out["data"]=items
    out["columns"]=columns
    out["total_count"]=len(items)
    #dbg("++++++++++ leaving get_item_raw[%s]:  returning %s",str(tab),str(out))
    dbg("++++++++++ leaving get_item_raw[%s]",str(tab))
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
    dbg("in get_next_seq")
    dbtyp = get_db_type(dbengine)
    if dbtyp =="sqlite":
        dbg("in get_next_seq repo sqlite")
        itemseq={ "seq" : seq}
        sql="SELECT curval FROM plainbi_seq WHERE sequence_name=:seq"
        dbg("sql=%s ,%s",sql,str(itemseq))
        items, columns = db_exec(dbengine,sql,itemseq)
        dbg("sql done")
        dbg("items %s",items)
        curval=items[0]["curval"]
        nextval=curval+1
        sql=f"UPDATE plainbi_seq SET curval={nextval} WHERE sequence_name='{seq}'"
        dbg("sql=%s",sql)
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
        dbg("in get_next_seq not sqlite")
        if dbtyp == "mssql":
            sql=f'SELECT NEXT VALUE FOR {seq} AS nextval'
        elif dbtyp == "postgres":
            sql=f"SELECT nextval('{seq}') AS nextval"
        elif dbtyp == "oracle":
            sql=f"SELECT {seq}.nextval AS nextval from dual"
        dbg("sql=%s",sql)
        try:
            #cursor = cnxn.cursor()
            items, columns = db_exec(dbengine,sql)
        except SQLAlchemyError as e_sqlalchemy:
            log.error("sqlalchemy exception in get_next_seq: %s",str(e_sqlalchemy))
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]="sqlerr-get_next_seq"
                out["message"]=" beim Erzeugen einer Sequenz-Id"
            return out
        except Exception as e:
            log.error("exception in get_next_seq: %s ",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]="err-get_next_seq"
                out["message"]=" beim Erzeugen einer Sequenz-Id"
            return out
        out=items[0]["nextval"] 
        #for row in data:
        #    out=row.nextval
        dbg("got sequence value %d",out)    
    return out

def get_dbversion(dbengine):
    out={}
    dbg("in get_dbversion")
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
    dbg("in get_current_timestamp")
    sql='SELECT GETDATE() as ts'
    dbg("sql=%s",sql)
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
    dbg("got timestamp value %s",out)    
    return out

def get_db_by_id_or_alias(d):
    """
    returns a sqlalchemy eninge object for the specified id or alias from the plainbi_datasource repo table
    """
    dbg("++++++++++ entering get_db_by_id_or_alias params=%s",str(d))
    k=str(d)
    if d is None or k == "def":
        k="1"
    if k in config.datasources_engine.keys():
        return config.datasources_engine[k]
    else:
        # not found yet - try to connect again
        dbg("get_db_by_id_or_alias connection not found -> reload")
        load_datasources_from_repo()
        if k in config.datasources_engine.keys():
            return config.datasources_engine[k]
        else:
            log.warning("get_db_by_id_or_alias connection not found after reload")
            return None


## repo lookup adhoc
def repo_lookup_select(repoengine,id,order_by=None,offset=None,limit=None,filter=None,with_total_count=False,where_clause=None,username=None):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    dbg("++++++++++entering repo_lookup_select")
    dbg("repo_lookup_select: param id is <%s>",str(id))
    if is_id(id):
        reposql_params={ "id" : id}
        reposql="select * from plainbi_lookup where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_lookup where alias=:alias"
    dbg("repo_lookup_select: repo sql is <%s>",reposql)
    lkp,lkp_columns = db_exec(repoengine, reposql , reposql_params)
    #lkp=[r._asdict() for r in lkpq]
    dbg("lkp=%s",str(lkp))
    sql=None
    execute_in_repodb=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                sql=lkp[0]["sql_query"]
                datasrc_id=lkp[0]["datasource_id"]
        else:
            msg="lookup with id/alias "+str(id)+" not found (or multiple defined)"
            log.error(msg)
            return None,None,None,msg
    else:
        dbg("lkp is not a list, it is a %s",str(lkp.__class__))
        
    if sql is None:
        msg="no sql in repo_lookup_select id="+str(id)
        log.error(msg)
        return None,None,None,msg
    if username is not None:
        sql=sql.replace("$(APP_USER)",username)
        dbg("lkp sql username replaced")

    dbengine=get_db_by_id_or_alias(datasrc_id)
    try:
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
def get_repo_adhoc_sql_stmt(repoengine,id,user_id):
    """
    führt ein sql aus und gibt zurück
      items .. List von dicts pro zeile
      columns .. spaltenname
      total_count .. anzahl der rows in der Tabelle (count*)
      msg ... ggf error code sonst "ok"
    """
    out={}
    dbg("++++++++++entering get_repo_adhoc_sql_stmt")
    dbg("get_repo_adhoc_sql_stmt: param id is <%s>",str(id))
    adhocid = -999
    order_by_def = None
    adhocdesc = None
    reposql="select * from plainbi_adhoc " # Leerzeichen hinten wichtig für später
    if is_id(id):
        adhocid=id
        reposql_params={ "id" : id}
        whereclause="where id=:id"
        #reposql="select * from plainbi_adhoc where id=:id"
    else:
        reposql_params={ "alias" : id}
        whereclause="where alias=:alias"
    #reposql="select * from plainbi_adhoc where alias=:alias"
    where = add_auth_to_where_clause("plainbi_adhoc", whereclause, user_id)
    reposql+=where
    dbg("repo_adhoc_select: repo sql is <%s>",reposql)
    try:
        lkp, lkp_columns = db_exec(repoengine, reposql , reposql_params)
    except SQLAlchemyError as e_sqlalchemy:
        log.error("sqlalchemy exception in get_repo_adhoc_sql_stmt: %s",str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_repo_adhoc_sql_stmt"
            out["message"]+=" beim Lesen der Adhoc-Abfrage"
        return out
    except Exception as e:
        log.error("exception in get_repo_adhoc_sql_stmt3: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_repo_adhoc_sql_stmt"
            out["message"]+=" beim Lesen der Adhoc-Abfrage"
        return out
    #lkp=[r._asdict() for r in lkpq]
    sql=None
    datasrc_id=None
    if isinstance(lkp,list):
        if len(lkp)==1:
            if isinstance(lkp[0],dict):
                out["sql"]=lkp[0]["sql_query"]
                out["datasrc_id"]=lkp[0]["datasource_id"]
                out["adhocid"]=lkp[0]["id"]
                out["order_by_def"]=lkp[0]["order_by_default"]
                out["adhocdesc"]=lkp[0]["description"]
                return out
        else:
            log.warn("get_repo_adhoc_sql_stmt:lkp list len is not 1")
            out["error"]="get_repo_adhoc_sql_stmt_not_found"
            out["message"]="Adhoc Bericht wurde nicht gefunden oder ist nicht berechtigt"
            return out
    else:
        log.warn("lkp is not a dict, it is a %s",str(lkp.__class__))
        out["error"]="get_repo_adhoc_sql_stmt_no_dict"
        out["message"]="Allgemeiner Fehler beim Lesen der Adhoc-Abfrage"
        return out
    return out

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
    dbg("++++++++++entering get_repo_customsql_sql_stmt")
    dbg("get_repo_customsql_sql_stmt: param id is <%s>",str(id))
    if is_id(id):
        reposql_params={ "id" : id}
        reposql="select * from plainbi_customsql where id=:id"
    else:
        reposql_params={ "alias" : id}
        reposql="select * from plainbi_customsql where alias=:alias"
    dbg("get_repo_customsql_sql_stmt: repo sql is <%s>",reposql)
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
            dbg("lkp list len is not 1, it is %d",len(lkp))
    else:
        dbg("lkp is not a dict, it is a %s",str(lkp.__class__))
    dbg("++++++++++leaving get_repo_customsql_sql_stmt with sql=%s",sql)
    return sql, execute_in_repodb


def check_hash_columns(tab,item):
    dbg("check_hash_columns for %s item %s",tab,item)
    if tab in repo_columns_to_hash.keys():
        for c in repo_columns_to_hash[tab]:
            if c in item.keys():
                p=config.bcrypt.generate_password_hash(item[c])
                #p=bcrypt.hashpw(item[c].encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
                item[c]=p.decode()
                dbg("check_hash_columns: hashed %s.%s",tab,c)

def get_column_metadata(c,metadata):
    if "column_data" in metadata.keys():
        for k in metadata["column_data"]:
            if k["column_name"]==c:
                return k
    else:
        return None    

def handle_oracle_date_literals(pitemlist,metadata):
    """
    oracle cannot handle date literals directly from strings as postgres does.
    that's why we have to transform data strings to datetime objects before
    passing it as dict parameters to exec sql
    we assume here that oracle column names are always upper case 
    param p_itemlist is modified (for output)
    """
    dbg("++++++++++ entering handle_oracle_date_literals")
    cnt=0
    if "column_data" not in metadata.keys():
        dbg("warning: metadata does not contain column_data datatypes")
        return
    if isinstance(pitemlist,dict):
        itemlist = [pitemlist]
    else:
        itemlist = pitemlist
    for item in itemlist:
        for k,v in item.items():
            coldat=get_column_metadata(k.upper(),metadata)
            if coldat is not None:
                if coldat["data_type"] == "DATE" or coldat["data_type"] == "TIMESTAMP":
                    if v is not None:
                        if isinstance(v,str):
                            dbg(f"handle oracle date literal {k} value {v}")
                            if len(v)==10:
                                if config.backend_date_format is not None:
                                    d = datetime.strptime(v,config.backend_date_format)
                                    dbg(f"date literal fmt {config.backend_date_format} {k} value {v} becomes {str(d)}")
                                else:
                                    d = datetime.strptime(v,"%Y-%m-%d")
                                    dbg(f"date literal {k} value {v} becomes {str(d)}")
                                item[k]=d
                                cnt+=1
                            elif len(v)>10:
                                if config.backend_datetime_format is not None:
                                    d = datetime.strptime(v,config.backend_datetime_format)
                                    dbg(f"datetime literal fmt {config.backend_datetime_format} {k} value {v} becomes {str(d)}")
                                else:
                                    d = datetime.strptime(v,"%Y-%m-%d %H:%M:%S")
                                    dbg(f"datetime literal {k} value {v} becomes {str(d)}")
                                item[k]=d
                                cnt+=1
                        else:
                            dbg(f"date/time column {k} handling skipped because value is not string but a {v.__class__.__name__}")
                    else:
                        dbg(f"date/time column {k} handling skipped because None")
            else:
                dbg(f"warning: column {k} should be in metadata list")
    dbg("++++++++++ leaving handle_oracle_date_literals with %d date literal substitutions",cnt)

## crud ops
def db_ins(dbeng,tab,item,pkcols=None,is_versioned=False,seq=None,changed_by=None,is_repo=False, user_id=None, customsql=None):
    """ 
    insert record
    """
    dbg("++++++++++ entering db_ins")
    dbg("db_ins: param tab is <%s>",str(tab))
    dbg("db_ins: param item is <%s>",str(item))
    dbg("db_ins: param pkcols is <%s>",str(pkcols))
    dbg("db_ins: param is_versioned is <%s>",str(is_versioned))
    dbg("db_ins: param seq is <%s>",str(seq))
    stmt=[]
    stmtparam=[]
    out={}
    db_typ = get_db_type(dbeng)
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols,versioned=is_versioned)
    log.info("db_ins after get_metadata_raw %s",str(metadata))
    myitem=item
    if "error" in metadata.keys():
        dbg("db_ins: error in get_metadata_raw returned")
        return metadata
    pkcols=metadata["pk_columns"]
    log.info("db_ins: now pkols=%s",str(pkcols))
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("db_ins: implicit pk first column")
    s=None
    # check hash columns
    dbg("db_ins: check hash columns")
    if is_repo: check_hash_columns(tab,myitem)
    #                    
    dbg("db_ins: after check hash columns")
    if is_versioned:
        dbg("db_ins: versioned mode" )
        ts=get_current_timestamp(dbeng)
        dbg("db_ins: ts=%s",ts)
        myitem["valid_from_dt"]=ts
        myitem["invalid_from_dt"]="9999-12-31 00:00:00"
        myitem["last_changed_dt"]=ts
        myitem["is_latest_period"]="Y"
        myitem["is_deleted"]="N"
        myitem["is_current_and_active"]="Y"
        dbg("db_ins: check last_changed_by user=%s", changed_by)
        if "last_changed_by" in metadata["columns"] and changed_by is not None:
            myitem["last_changed_by"]=changed_by
    else:
        dbg("db_ins: non versioned mode" )
    dbg("db_ins: prepare sql" )
    dbg("add missing pk columns ")
    # add missing primary key columns
    for pkcol in pkcols:
        if pkcol not in myitem.keys():
            # id ist nicht in data list so generate
            dbg("db_ins: pk column %s is not in data list so generate",pkcol)
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
                if isinstance(s,dict):
                    log.error("returned sequence has error %s",str(s))
                    dbg("Forward sequence error to caller")
                    if "error" in s.keys():
                        out["error"]="sequence error in db_ins: "+s["error"]
                    else:
                        out["error"]="sequence error in db_ins"
                    if "detail" in s.keys():
                        out["detail"]="sequence error in db_ins: "+s["detail"]
                    else:
                        out["detail"]="unspecific sequence error in db_ins"
                    return out
                else:
                    dbg("db_ins: got seq %d",s)
                    myitem[pkcol]=s
                    pkout[pkcol]=s
                    dbg("db_ins: seqence %s inserted",seq)
        else:
            pkout[pkcol]=myitem[pkcol]

    # we have to check if there is an deleted record for this pk
    if is_versioned:
        delrec=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned,version_deleted=True)
        if "total_count" in delrec.keys():
            if delrec["total_count"]>0:
                # check if is_deleted="N"
                try:
                    if delrec["data"][0]["is_deleted"] == "N":
                        out["error"]="insert-to-versioned-table-with-existing-pk"
                        out["message"]="Datensatz ist bereits vorhanden"
                        out["detail"]="es wurde versucht, einen Datensatz in einer versionierten Tabelle neu anzulegen, obwohl bereits einer existiert (der nicht bereits gelöscht wurde)"
                        log.error(out["detail"])
                        return out
                except Exception as e2:
                    out["error"]="insert-to-versioned-table-with-existing-pk-error"
                    out["message"]="Datensatz ist bereits vorhanden - error"
                    out["detail"]="es wurde versucht, einen Datensatz in einer versionierten Tabelle neu anzulegen, obwohl bereits einer existiert (der nicht bereits gelöscht wurde) - Error"
                    log.error(out["error"])
                    log.error("e2: %s",str(e2))
                    log.exception(e2)
                    return out

                # there is an existing record -> terminate id
                pkwhere, pkwhere_params = make_pk_where_clause(pkout,pkcols,is_versioned,version_deleted=True)
                delitem={}
                delitem["invalid_from_dt"]=ts
                delitem["last_changed_dt"]=ts
                delitem.update(pkwhere_params)
                dbg("marker values length is %d",len(delitem))
                dbg("db_ins: terminate deleted record")
                dsql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
                dbg("db_ins: terminate rec sql %s",dsql)
                stmt.append(dsql)
                stmtparam.append(delitem)
                #try:
                #    db_exec(dbeng, dsql, delitem) # versioned column
                #    dbg("dbins: deleted record terminated")
                #except SQLAlchemyError as e_sqlalchemy:
                #    log.error("sqlalchemy deleted record terminated; %s",str(e_sqlalchemy))
                #    if last_stmt_has_errors(e_sqlalchemy, out):
                #        out["error"]+="-db_ins-vers"
                #        out["message"]+=" beim Einfügen eines neuen versionierten Datensatzes"
                #    return out
                #except Exception as e:
                #    log.error("excp deleted record terminated: %s",str(e))
                #    if last_stmt_has_errors(e, out):
                #        out["error"]+="-db_ins-vers"
                #        out["message"]+=" beim Einfügen eines neuen versionierten Datensatzes"
                #    return out
               
    param_list=[":"+k for k in myitem.keys()]
    col_list=[k for k in myitem.keys()]
    dbg("db_ins: construct sql" )
    param_list_str=",".join(param_list)
    col_list_str=",".join(col_list)
    sql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
    dbg("db_ins sql: %s",sql)

    stmt.append(sql)
    stmtparam.append(myitem)

    #if db_typ=="oracle":
    #    handle_oracle_date_literals(stmtparam,metadata)

    try:
        #db_exec(dbeng,sql,myitem)
        db_exec(dbeng,stmt,stmtparam,metadata)
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
    dbg("++++++++++ leaving db_ins returning %s", str(out))
    return out


## crud ops
def db_upd(dbeng, tab,pk, item, pkcols, is_versioned, changed_by=None, is_repo=False, user_id=None, customsql=None):
    dbg("++++++++++ entering db_upd")
    dbg("db_upd: param tab is <%s>",str(tab))
    dbg("db_upd: param pk is <%s>",str(pk))
    dbg("db_upd: pkcols tab is <%s>",str(pkcols))
    dbg("db_upd: param is_versioned is <%s>",str(is_versioned))
    out={}
    dbg("item-keys %s",item.keys())
    myitem=item
    db_typ = get_db_type(dbeng)
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
    dbg("update_item: pkwhere %s",pkwhere)

    # check hash columns
    if is_repo: check_hash_columns(tab,myitem)

    dbg("pk_columns %s",pkcols)
    if is_versioned:
        dbg("update_item: 1")
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbeng)
        # hole then alten Datensatz aus der DB mit dem angegebenen pk
        cur_row=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        upditem={}
        upditem["invalid_from_dt"]=ts
        upditem["last_changed_dt"]=ts
        upditem.update(pkwhere_params)
        dbg("marker values length is %d",len(upditem))
        updsql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
        dbg("db_upd newrec sql: %s", updsql)
        stmt=[]
        stmtparam=[]
        stmt.append(updsql)
        stmtparam.append(upditem)
        #try:
        #    db_exec(dbeng, updsql, upditem)
        #except SQLAlchemyError as e_sqlalchemy:
        #    if last_stmt_has_errors(e_sqlalchemy, out):
        #        out["error"]+="-db_upd-old-vers"
        #        out["message"]+=" beim Aktualisieren des alten versionierten Datensatzes"
        #    log.error("++++++++++ leaving db_upd returning %s", str(out))
        #    return out
        #except Exception as e:
        #    if last_stmt_has_errors(e, out):
        #        out["error"]+="-db_upd-old-vers"
        #        out["message"]+=" beim Aktualisieren des alten versionierten Datensatzes"
        #    log.error("++++++++++ leaving db_upd returning %s", str(out))
        #    return out
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
        dbg("db_upd: construct sql" )
        param_list=[":"+k for k in newrec.keys()]
        col_list=[k for k in newrec.keys()]
        param_list_str=",".join(param_list)
        col_list_str=",".join(col_list)
        newsql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
        dbg("db_upd newrec sql: %s",newsql)
        stmt.append(newsql)
        stmtparam.append(newrec)
        #if db_typ=="oracle":
        #    handle_oracle_date_literals(stmtparam,metadata)
        try:
            #db_exec(dbeng,newsql,newrec)
            db_exec(dbeng,stmt,stmtparam,metadata)
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
        dbg("othercols %s",othercols)
        osetexp=[k+"=:"+k for k in othercols]
        osetexp_str=",".join(osetexp)
        myitem.update(pkwhere_params)
        sql=f"UPDATE {tab} SET {osetexp_str} {pkwhere}"
        dbg("update item sql %s",sql)
        dbg("update item params %s",myitem)
        #if db_typ=="oracle":
        #    handle_oracle_date_literals(myitem,metadata)
        try:
            db_exec(dbeng,sql,myitem,metadata)
        except SQLAlchemyError as e_sqlalchemy:
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-db_upd"
                out["message"]+=" beim Aktualisieren eines Datensatzes"
            dbg("++++++++++ leaving db_upd returning %s", str(out))
            return out
        except Exception as e:
            if last_stmt_has_errors(e, out):
                out["error"]+="-db_upd"
                out["message"]+=" beim Aktualisieren eines Datensatzes"
            dbg("++++++++++ leaving db_upd returning %s", str(out))
            return out
    # den aktuellen Datensatz wieder aus der DB holen und zurückgeben (könnte ja Triggers geben)
    out=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned,is_repo=is_repo,user_id=user_id,customsql=customsql)
    dbg("++++++++++ leaving db_upd returning %s", str(out))
    return out

def db_del(dbeng,tab,pk,pkcols,is_versioned=False,changed_by=None,is_repo=False, user_id=None):
    dbg("++++++++++ entering db_del")
    dbg("db_del: param tab is <%s>",str(tab))
    dbg("db_del: param pk is <%s>",str(pk))
    dbg("db_del: pkcols tab is <%s>",str(pkcols))
    dbg("db_del: param is_versioned is <%s>",str(is_versioned))
    # check options
    out={}
    db_typ = get_db_type(dbeng)
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols,versioned=is_versioned)
    if "error" in metadata.keys():
        dbg("++++++++++ leaving db_del returning %s", str(metadata))
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
            dbg("++++++++++ leaving db_del returning %s", str(out))
            return out
    else:
        out["error"]="db_del-pk-check-id-not-found"
        out["message"]="Der zu löschende Datensatz wurde nicht gefunden"
        dbg("++++++++++ leaving db_del returning %s", str(out))
        return out

    pkwhere, pkwhere_params = make_pk_where_clause(pk,pkcols,is_versioned)
    dbg("db_del: pkwhere %s",pkwhere)
        
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbeng)
        cur_row=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols,versioned=is_versioned)
        upditem={}
        upditem["invalid_from_dt"]=ts
        upditem["last_changed_dt"]=ts
        upditem.update(pkwhere_params)
        dbg("marker values length is %d",len(upditem))
        sql=f"UPDATE {tab} SET invalid_from_dt=:invalid_from_dt,last_changed_dt=:last_changed_dt,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'"
        stmt=[]
        stmtparam=[]
        stmt.append(sql)
        stmtparam.append(upditem)
        #try:
        #    db_exec(dbeng, sql, upditem)
        #except SQLAlchemyError as e_sqlalchemy:
        #    if last_stmt_has_errors(e_sqlalchemy, out):
        #        out["error"]+="-db_del-old-vers"
        #        out["message"]+=" beim Löschen des alten versionierten Datensatzes"
        #    log.error("++++++++++ leaving db_del returning %s", str(out))
        #    return out
        #except Exception as e:
        #    if last_stmt_has_errors(e, out):
        #        out["error"]+="-db_del-old-vers"
        #        out["message"]+=" beim Löschen des alten versionierten Datensatzes"
        #    log.error("++++++++++ leaving db_del returning %s", str(out))
        #    return out
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
        dbg("db_upd: construct sql" )
        param_list=[":"+k for k in newrec.keys()]
        col_list=[k for k in newrec.keys()]
        param_list_str=",".join(param_list)
        col_list_str=",".join(col_list)
        newsql = f"INSERT INTO {tab} ({col_list_str}) VALUES ({param_list_str})"
        dbg("db_del: %s",newsql)
        stmt.append(newsql)
        stmtparam.append(newrec)
        #if db_typ=="oracle":
        #    handle_oracle_date_literals(stmtparam,metadata)
        try:
            #db_exec(dbeng,newsql,newrec)
            db_exec(dbeng,stmt,stmtparam,metadata)
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
        dbg("db_del sql %s",sql)
        dbg("db_del marker values length is %d",len(pkwhere_params))
        #if db_typ=="oracle":
        #    handle_oracle_date_literals(pkwhere_params,metadata)
        try:
            db_exec(dbeng,sql,pkwhere_params,metadata)
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
    dbg("++++++++++ leaving db_del returning %s", str(out))
    return out

def get_profile(repoengine,u):
    """
    profile eines Users
    """
    if config.use_cache:
        if hasattr(config,"profile_cache"):
            if u in config.profile_cache.keys():
                dbg("get_profile: cache hit")
                return config.profile_cache[u]
        else:
            config.profile_cache={}
            dbg("get_profile: cache created")

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
        if role_id==1:
            prof["user_is_admin"] = "Y"
        else:
            prof["user_is_admin"] = "N"
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
    dbg("db_adduser: database type is %s",db_typ)
    if db_typ=="sqlite":
        sequenz="user"
    elif db_typ in ("mssql","postgres","oracle"):
        sequenz="plainbi_user_seq"
    else:
        log.error("db_adduser: unknown repo database type")
        sequenz=None
    dbg("db_adduser: database seq is %s",sequenz)
    x=db_ins(dbeng,"plainbi_user",item,pkcols='id',seq=sequenz)
    return x

def db_passwd(dbeng,u,p):
    dbg("++++++++++ entering db_passwd")
    dbg("db_passwd: param u is <%s>",str(u))
    dbg("db_passwd: param p (hashed) is <%s>",str(p))
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

def db_add_base64(dbeng,id,filep):
    """
    add a base64 encoded file to static_file
    """
    if not os.path.isfile(filep):
        log.error("path is not a file")

    with open(filep,"rb") as f:
        b=f.read()

    c=base64.b64encode(b).decode('ascii')
    item = { "id":id, "content_base64": c}
    #    out = db_upd(dbengine,tab,pk,item,pkcols,is_versioned,changed_by=tokdata['username'],customsql=mycustomsql)
    x=db_upd(dbeng,"plainbi_static_file",int(id),item,pkcols='id',is_versioned=False)
    return x



def add_auth_to_where_clause(tab,where_clause,user_id):
    dbg("++++++++++ entering add_auth_to_where_clause")
    dbg("add_auth_to_where_clause: param tab is <%s>",str(tab))
    dbg("add_auth_to_where_clause: param where_clause is <%s>",str(where_clause))
    dbg("add_auth_to_where_clause: param user_id is <%s>",str(user_id))
    w = where_clause
    if w is None: w=""
    if tab == 'plainbi_application' and user_id is not None:
        dbg("add_auth_to_where_clause: apply auth for application")
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
        dbg("add_auth_to_where_clause: apply auth for adhoc")
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
        dbg("add_auth_to_where_clause: apply auth for external_resource")
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
    dbg("++++++++++ leaving add_auth_to_where_clause with: %s",w)
    return w

#b = base64.b64encode(bytes('your string', 'utf-8')) # bytes
#base64_str = b.decode('utf-8') # convert bytes to string


def postgres_set_search_path(dbapi_connection, connection_record):
    dbg("++++++++++ entering postgres_set_search_path")
    try:
        with dbapi_connection.cursor() as cursor:
            cursor.execute('SET search_path TO plainbi, "$user", public')
        dbapi_connection.commit()
    except Exception as e:
        log.error("postgres_set_search_path: %s",str(e))
    # requery
    sql = "SELECT current_setting('search_path') as searchpath"
    with dbapi_connection.cursor() as cursor:
        cursor.execute(sql)
        res = cursor.fetchall()
    dbg("postgres search path is not %s",str(res))
    dbg("++++++++++ leaving postgres_set_search_path")

def db_connect(p_enginestr, params=None):
    dbg("++++++++++ entering db_connect")
    dbg("db_connect: param enginestr is <%s>",str(p_enginestr)[:15]+"...")
    dbg("db_connect: param params is <%s>",str(params))
    if p_enginestr is None:
        log.error("PLAINBI needs a connection string in the .env File to properly connect to a database")
    dstr=p_enginestr.split("|")
    enginestr=dstr[0]
    if params is not None:
        dbengine = sqlalchemy.create_engine(enginestr % params)
    else:
        if "postgres" in p_enginestr:
            dbg("++++++++++ enable pool_pre_ping for postgres")
            dbg("++++++++++ enable echo_pool debug for postgres")
            dbengine = sqlalchemy.create_engine(enginestr, pool_pre_ping=True, echo_pool='debug', connect_args={'connect_timeout': 10}, pool_recycle=600)
        else:
            dbengine = sqlalchemy.create_engine(enginestr)
    log.info("db_connect: engine url %s",dbengine.url)
    dbg("++++++++++ leaving db_connect")
    dbtyp=get_db_type(dbengine)
    if len(dstr)>1:
        for kv in dstr[1:]:
            kl=kv.split("=")
            if len(kl)>1:
                if kl[0].lower()=="schema":
                    # has a schema
                    if dbtyp == "postgres":
                        # jk 20240731
                        sqlalchemy.event.listen(dbengine, 'connect', postgres_set_search_path)
                    elif dbtyp == "mssql":
                        sql="use "+kl[1]
                        db_exec(dbengine,sql)
                        dbg("++++++++++ use schema %",kl[1])

    return dbengine

def audit(tokdata,req,id=None,msg=None):
    dbg("++++++++++ entering audit")
    if isinstance(tokdata,dict):
        usrnam=tokdata["username"]
    else:
        usrnam=tokdata
    dbg('Audit rec: usr=%s,url=%s,id=%s,msg=%s',usrnam,req.url,str(id),str(msg))
    if id is not None:
        dbg("Audit Adhoc %d",id)
    if "/login" in req.url: 
        audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body": None}
    else:
        #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.get_json())}
        #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":None}
        #audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.get_json(force=True))}
        audit_params={"username":usrnam, "url":req.url, "remark":msg, "id":id, "method":req.method, "body":str(req.data)}
    audit_sql="insert into plainbi_audit (username,t,url,id,remark,request_method,request_body) values (:username,CURRENT_TIMESTAMP,:url,:id,:remark,:method,:body)"
    try:
        dbg('Audit sql:%s',audit_sql )
        dbg('Audit params:%s',audit_params )
        db_exec(config.repoengine, audit_sql, audit_params)
        dbg('Audit executed')
    except SQLAlchemyError as e_sqlalchemy:
        log.error("audit error: %s",str(e_sqlalchemy))
        log.exception(e_sqlalchemy)
        dbg("continuing")
    except Exception as e:
        log.error("audit exception: %s",str(e))
        dbg("continuing")
    dbg("++++++++++ leaving audit")

def load_datasources_from_repo():
    """
    loads all datasources into a config global dictionary config.datasources and connects to config.datasources_engine
    """
    dbg("++++++++++ entering load_datasources_from_repo")
    config.datasources={}
    config.datasources_engine={}
    def nvl(b):
        return b if b is not None else "{"+b+"}"
    # first add repo
    config.datasources_engine["0"] = config.repoengine
    config.datasources_engine["repo"] = config.repoengine
    # next load all datasources from repo
    datasrc_sql = "select * from plainbi_datasource where id <> 0"
    datasrc_items, datasrc_columns = db_exec(config.repoengine,datasrc_sql)
    for i in datasrc_items:
        #dbg("load_datasources_from_repo: id=%d type=%s",i["id"],i["db_type"])
        db_type = i["db_type"]
        id = i["id"]
        alias = i["alias"]
        host = i["db_host"]
        port = i["db_port"]
        db_name = i["db_name"]
        db_user = i["db_user"]
        if "db_pass_hash" in i.keys():
            db_pass = i["db_pass_hash"]
        else:
            db_pass = i["db_pass"]
        if db_type == "mssql":
            sql_dbengine_str=f"mssql+pymssql://{db_user}:{db_pass}@{host}/{db_name}"
        elif db_type == "sqlite":
            sql_dbengine_str=f"sqlite://{host}"
        elif db_type == "postgres":
            sql_dbengine_str=f"postgresql+psycopg2://{db_user}{db_user}:{db_pass}@{host}/{db_name}"
        elif db_type == "oracle":
            sql_dbengine_str=f"oracle+cx_oracle://{db_user}:{db_pass}@{host}:{port}/{db_name}"
        else:
            if db_type is None:
                log.warning("datasource type is empty -> skip datasource")
                continue
            sql_dbengine_str = db_type
            if "{db_user}" in sql_dbengine_str and db_user is not None:
                sql_dbengine_str=sql_dbengine_str.replace("{db_user}",db_user)
            if "{db_pass}" in sql_dbengine_str and db_pass is not None:
                sql_dbengine_str=sql_dbengine_str.replace("{db_pass}",db_pass)
            if "{host}" in sql_dbengine_str and host is not None:
                sql_dbengine_str=sql_dbengine_str.replace("{host}",host)
            if "{port}" in sql_dbengine_str and port is not None:
                sql_dbengine_str=sql_dbengine_str.replace("{port}",port)
        #dbg(sql_dbengine_str)
        config.datasources[str(id)]=sql_dbengine_str
        config.datasources[alias]=sql_dbengine_str
        if db_connect_test(sql_dbengine_str):
            config.datasources_engine[str(id)] = db_connect(sql_dbengine_str)
            config.datasources_engine[alias] = db_connect(sql_dbengine_str)
        else:
            log.warning('cannot connect to datasource_id: %d engine_str: %s',id,sql_dbengine_str)

