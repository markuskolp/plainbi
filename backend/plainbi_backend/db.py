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
import bcrypt


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
    log.debug("++++++++++ leavng get_metadata_raw returning for %s data %s",tab,out)
    return out

def get_item_raw(dbengine,tab,pk,pk_column_list=None,versioned=False,version_deleted=False):
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
    metadata=get_metadata_raw(dbengine,tab,pk_column_list)
    if "error" in metadata.keys():
        return metadata        
    pkcols=metadata["pk_columns"]
    if len(pkcols)==0:
        # kein PK default erste spalte
        pkcols=[(metadata["columns"])[0]]
        log.warning("implicit pk first column")
    print("get_item_raw: pk_columns",str(pkcols))
    pkwhere, pkwhere_val = make_pk_where_clause(pk, pkcols, versioned, version_deleted)
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

## crud ops
def db_ins(dbeng,tab,item,pkcols=None,is_versioned=False,seq=None):
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
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols)
    log.info("create_item after get_metadata_raw %s",str(metadata))
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
    if is_versioned:
        log.debug("db_ins: versioned mode" )
        ts=get_current_timestamp(dbeng)
        log.debug("db_ins: ts=%s",ts)
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
        log.debug("db_ins: non versioned mode" )
        collist=[k for k in item.keys()]
        vallist=[v for v in item.values()]
    log.debug("db_ins: prepare sql" )
    log.debug("add missing pk columns ")
    # add missing primary key columns
    for pkcol in pkcols:
        if pkcol not in item.keys():
            # id ist nicht in data list so generate
            log.debug("db_ins: pk column %s is not in data list so generate",pkcol)
            if pkcol not in collist:
                collist.append(pkcol)
                vallist.append(None)
    # check if sequence should be applied
    pkout={}
    for pkcol in pkcols:
        if vallist[collist.index(pkcol)] is None:
            if seq is not None:
                # override none valued sequence pk column with seq 
                if len(pkcols)>1:
                    out["error"]="sequences are only allowed for single column primary keys"
                    return out
                s=get_next_seq(dbeng,seq)
                log.debug("db_ins: got seq %d",s)
                vallist[collist.index(pkcol)]=s
                pkout[pkcol]=s
                log.debug("db_ins: seqence %s inserted",seq)
        else:
            pkout[pkcol]=vallist[collist.index(pkcol)]

    # we have to check if there is an deleted record for this pk
    if is_versioned:
        delrec=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned,version_deleted=True)
        if "total_count" in delrec.keys():
            if delrec["total_count"]>0:
                # there is an existing record -> terminate id
                pkwhere, pkwhere_val = make_pk_where_clause(pkout,pkcols,is_versioned,version_deleted=True)
                dvallist=[]
                dvallist.append(ts)
                dvallist.append(ts)
                dvallist.extend(list(pkwhere_val))
                log.debug("marker values length is %d",len(dvallist))
                dval_tuple=tuple(dvallist)
                log.debug("db_ins: terminate deleted record")
                dsql=f"UPDATE {tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'" 
                log.debug("db_ins: terminate rec sql %s",dsql)
                try:
                    dbeng.execute(dsql,dval_tuple)
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
               
    qlist=["?" for k in vallist]
    log.debug("db_ins: construct sql" )
    q_str=",".join(qlist)
    collist_str=",".join(collist)
    sql = f"INSERT INTO {tab} ({collist_str}) VALUES ({q_str})"
    log.debug("db_ins sql: %s",sql)
    try:
        dbeng.execute(sql,tuple(vallist))
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
    out=get_item_raw(dbeng,tab,pkout,pk_column_list=pkcols,versioned=is_versioned)
    log.debug("++++++++++ leaving db_ins returning %s", str(out))
    return out

## crud ops
def db_upd(dbeng,tab,pk,pkcols):
    pass

def db_del(dbeng,tab,pk,pkcols,is_versioned=False):
    log.debug("++++++++++ entering db_del")
    log.debug("db_del: param tab is <%s>",str(tab))
    log.debug("db_del: param pk is <%s>",str(pk))
    log.debug("db_del: pkcols tab is <%s>",str(pkcols))
    log.debug("db_del: param is_versioned is <%s>",str(is_versioned))
    # check options
    out={}
    metadata=get_metadata_raw(dbeng,tab,pk_column_list=pkcols)
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

    pkwhere, pkwhere_val = make_pk_where_clause(pk,pkcols,is_versioned)
    log.debug("db_del: pkwhere %s",pkwhere)
        
    #log.debug("delete_item pk_columns %s",pkcols)
    #if len(pkcols)==1:
    #    pkwhere=pkcols[0]+"=?"
    #else:
    #    pkexp=[k+"=?" for k in pkcols]
    #    pkwhere=" AND ".join(pkexp)
    #log.debug("pkwhere %s",pkwhere)
    if is_versioned:
        # aktuellen Datensatz abschließen
        # neuen Datensatz anlegen
        ts=get_current_timestamp(dbeng)
        cur_row=get_item_raw(dbeng,tab,pk,pk_column_list=pkcols)
        vallist=[]
        vallist.append(ts)
        vallist.append(ts)
        vallist.extend(list(pkwhere_val))
        log.debug("marker values length is %d",len(vallist))
        val_tuple=tuple(vallist)
        sql=f"UPDATE {tab} SET invalid_from_dt=?,last_changed_dt=?,is_latest_period='N',is_current_and_active='N' {pkwhere} AND invalid_from_dt='9999-12-31 00:00:00'"
        dbeng.execute(sql,val_tuple)
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
        log.debug("db_del: %s",sql)
        try:
            dbeng.execute(sql,tuple(vallist))
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
        log.debug("db_del marker values length is %d",len(pkwhere_val))
        try:
            dbeng.execute(sql,pkwhere_val)
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

    
def db_adduser(dbeng,usr,fullname=None,email=None,pwd=None):
    """
    ,username text
    ,email text
    ,fullname text
    ,password_hash text
    ,role_id int
    
    example: db_adduser(repoengine,"joe",fullname="Johannes Kribbel",pwd="joe123")
    """
    item = { "id":None, "username":usr,"fullname":fullname}
    if email is not None:
        item["email"]=email
    if pwd is not None:
        p=bcrypt.hashpw(pwd.encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
        item["password_hash"]=p.decode()
    x=db_ins(dbeng,"plainbi_user",item,pkcols='id',seq="user")
    return x


b = base64.b64encode(bytes('your string', 'utf-8')) # bytes
base64_str = b.decode('utf-8') # convert bytes to string
    
