# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 11:19:08 2023

@author: kribbel

how to run


first window
~/plainbi/backend> python plainbi_backend.py
oder 
---
gunicorn -c gunicorn.conf.py "plainbi_backend.api:create_app()"
---

second window
~/plainbi/frontend> npm start

02.07.2026

in Browser:
http://localhost:3001/
# swagger testing
http://localhost:3001/apidocs/

"""

import os
import sys
import logging
import traceback
import tempfile
import time
from datetime import date,datetime
from contextvars import ContextVar
from types import SimpleNamespace
from typing import Optional

import base64
import hashlib
import requests
from urllib.parse import urlparse, parse_qs
import json

import pprint
import re
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text as sql_text
import decimal
import math
import csv
import pandas as pd
import bcrypt
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.table import Table #, TableStyleInfo
from openpyxl.utils import get_column_letter
import smtplib
import pandas.io.formats.excel as fmt_xl
import ast

from dotenv import load_dotenv

from functools import wraps
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, Response, HTMLResponse, PlainTextResponse
from fastapi.security import APIKeyHeader
import jwt
from jwt import PyJWKClient
import secrets

# FastAPI ships an OpenAPI/Swagger UI (/docs) out of the box - no flasgger dependency needed

from plainbi_backend.utils import db_subs_env, prep_pk_from_url, is_id, last_stmt_has_errors, make_pk_where_clause, urlsafe_decode_params, pre_jsonify_items_transformer, parse_filter, dbg, err, warn, dbg_api_call
from plainbi_backend.db import sql_select, get_item_raw, get_metadata_raw, db_connect, db_connect_test, db_exec, db_ins, db_upd, db_del, get_current_timestamp, get_next_seq, repo_lookup_select, get_repo_adhoc_sql_stmt, get_repo_customsql_sql_stmt, get_profile, add_auth_to_where_clause, add_offset_limit, _safe_order_by, audit, db_adduser, db_passwd, get_db_type, get_dbversion, load_datasources_from_repo, get_db_by_id_or_alias
from plainbi_backend.repo import create_repo_db, create_app_db

# import the global variable config
from plainbi_backend.config import config


#log = logging.getLogger(config.logger_name)
log = logging.getLogger(__name__)

try:
    import ldap3
    config.with_ldap3=True
    log.info("LDAP3 enabled")
except:
    print("LDAP disabled because not installed")
    config.with_ldap3=False
    log.info("LDAP disabled because not installed")

# try to load identiy for microsoft sso authentication if available
auth = None
try:
    #from msal import ConfidentialClientApplication, ClientCredential
    import msal
    config.with_sso=True
    print("Microsoft SSO enabled")
    log.info("Microsoft SSO enabled")
except:
    config.with_sso=False
    print("Microsoft SSO disabled because not installed")
    log.info("Microsoft SSO disabled because not installed")

api_router = APIRouter()

def _plainbi_json_default(obj):
    """default= callback for json.dumps, mirrors the old Flask CustomJSONEncoder.default"""
    dbg("_plainbi_json_default %s / %s",str(type(obj)),str(obj))
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, Exception):
        return str(obj)
    try:
        return list(iter(obj))
    except TypeError:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class PlainBIJSONResponse(JSONResponse):
    """like starlette's JSONResponse but with the same datetime/date/Decimal/Exception/iterable
    fallback encoding the old Flask CustomJSONEncoder provided, and a real 500 (not a silent 200)
    if the content still can't be serialized"""
    def render(self, content) -> bytes:
        try:
            return json.dumps(content, default=_plainbi_json_default, ensure_ascii=False).encode("utf-8")
        except Exception as e:
            err("cannot jsonify dict %s",str(content))
            log.exception(e)
            self.status_code = 500
            return json.dumps({"error":"cannot jsonify output", "detail":str(e)}).encode("utf-8")

def myjsonify(d: dict, status: int = 200) -> PlainBIJSONResponse:
    if config.dbg_level >= 3 and log.getEffectiveLevel() == logging.DEBUG:
        dbg("--- myjsonify json output")
        pprint.pprint(d)
        dbg("--- end myjsonify json output")
    return PlainBIJSONResponse(content=d, status_code=status)


_api_key_header_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(authorization: Optional[str] = Depends(_api_key_header_scheme)) -> dict:
    """FastAPI dependency replacing the old @token_required decorator.
    Injected as: tokdata: dict = Depends(get_current_user)
    Accepts the Authorization header both as a raw token and as 'Bearer <token>'
    (the frontend always sends the Bearer form, the pytest suite sends the raw form).
    Declared via APIKeyHeader (not a plain Header()) so FastAPI's /docs shows an
    Authorize button, replacing the old flasgger securityDefinitions.APIKeyHeader."""
    dbg("token req")
    dbg("token=%s",str(authorization))
    if not authorization:
        raise HTTPException(status_code=401, detail={'message': 'Token is missing'})
    token = authorization[7:] if authorization.lower().startswith("bearer ") else authorization
    try:
        tokdata = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
        dbg("data2=%s",str(tokdata))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={'message': 'Token has expired'})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={'message': 'Invalid token x'})
    return tokdata


async def get_raw_body(request: Request) -> bytes:
    """FastAPI dependency replacing request.get_data(). Injected as
    raw_body: bytes = Depends(get_raw_body) - on every route, including GET-only ones
    (where it resolves to b''), for a uniform signature and to feed audit()'s body logging."""
    return await request.body()


def parse_json_body(raw: bytes):
    """replaces the old request.get_data().decode('utf-8').strip("'") idiom used
    throughout this module - keeps tolerating stray quotes some clients send around the body"""
    return json.loads(raw.decode('utf-8').strip("'"))


# carries get_adhoc_data's audit id across to the audited() wrapper below, replacing flask's g.audit_id
_audit_id_ctxvar: ContextVar = ContextVar('plainbi_audit_id', default=None)


def audited(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        tokdata = kwargs.get('tokdata')
        req = kwargs.get('request')
        raw_body = kwargs.get('raw_body', b'')
        audit_req = SimpleNamespace(url=str(req.url) if req is not None else '',
                                     method=req.method if req is not None else '')
        t0 = time.monotonic()
        try:
            result = f(*args, **kwargs)
            code = getattr(result, 'status_code', 200)
            duration_ms = int((time.monotonic() - t0) * 1000)
            if int(code) < 400:
                audit(tokdata, audit_req, id=_audit_id_ctxvar.get(),
                      status='ok', duration_ms=duration_ms, body=raw_body)
            else:
                error_msg = None
                try:
                    body_bytes = getattr(result, 'body', None)
                    if body_bytes:
                        data = json.loads(bytes(body_bytes).decode('utf-8'))
                        parts = [data.get('message'), data.get('detail')]
                        error_msg = ' | '.join(p for p in parts if p) or data.get('error')
                    if not error_msg and body_bytes:
                        error_msg = bytes(body_bytes).decode('utf-8', 'ignore')[:500]
                except Exception:
                    pass
                audit(tokdata, audit_req, id=_audit_id_ctxvar.get(),
                      status='error', error_msg=error_msg, duration_ms=duration_ms, body=raw_body)
            return result
        except Exception as e:
            duration_ms = int((time.monotonic() - t0) * 1000)
            audit(tokdata, audit_req, id=_audit_id_ctxvar.get(),
                  status='error', error_msg=str(e)[:2000], duration_ms=duration_ms, body=raw_body)
            raise
    return decorated


async def _http_exception_handler(request: Request, exc: HTTPException) -> PlainBIJSONResponse:
    """FastAPI's default HTTPException handler wraps `detail` as {"detail": ...}, which
    breaks the frontend's flat {error, message, detail} error-shape contract - unwrap it."""
    if isinstance(exc.detail, dict):
        return PlainBIJSONResponse(exc.detail, status_code=exc.status_code)
    return PlainBIJSONResponse({"message": exc.detail}, status_code=exc.status_code)


async def _unhandled_exception_handler(request: Request, exc: Exception) -> PlainBIJSONResponse:
    """Safety net mirroring last_stmt_has_errors' error shape for anything a route's own
    try/except didn't already catch and format."""
    log.exception(exc)
    out = {}
    last_stmt_has_errors(exc, out)
    return PlainBIJSONResponse(out, status_code=500)


repo_table_prefix="plainbi_"

api_root="/api"
api_prefix=api_root+"/crud"
repo_api_prefix=api_root+"/repo"
api_metadata_prefix=api_root+"/metadata"
cursor_desc_fields=["name","type_code","display_size","internal_size","precision","scale","null_ok"]

nodb_msg = { "error" :"-no-open-db", "message":"Datenbankverbindung ungültig in datasources, prüfe die Repo Konfiguration" }

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
@api_router.get('/')
def welcome():
    """
    welcome message to the backend rest server if no specific url is given
    """
    dbversion=get_dbversion(config.repoengine)
    p=f"""
    <html>
    <body>
    <h1>Welcome to PLAINBI Backend</h1>
    <p>Version {config.version}</p>
    <p>Repo Database version {dbversion}</p>
    <p>If you want to initialize the repository click <a href="{repo_api_prefix+'/init_repo'}">here</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=p)

@api_router.get('/version')
@api_router.get(api_root+'/version')
def get_version():
    """
    return the version number of the backend
    """
    return PlainTextResponse(content=config.version)

@api_router.get(api_root+'/backend_version')
@api_router.get(api_root+'/db_version')
@api_router.get(api_root+'/dbversion')
def get_backend_version(request: Request):
    """
    return the database type and version of the backend
    """
    dbg_api_call(request)
    dbversion=get_dbversion(config.repoengine)
    return PlainTextResponse(content="Plainbi Backend: "+config.version+"\nRepository: "+str(dbversion))

@api_router.get(api_root+'/loglevel/{loglevel}')
def set_log_level(loglevel: str, request: Request):
    """
    set log level log.setLevel(
    """
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            log.info("loglevel arg: %s val: %s",key,value)
            if key=="loggers":
                lognames=value.split(",")
                dbg("loggers are: "+str(lognames))
                loggers = [logging.getLogger(name) for name in lognames]
    else:
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if "plainbi" in name]
        dbg("all plainbi loggers")

    for l in loggers:
      if loglevel=="INFO":
        l.setLevel(logging.INFO)
        log.info(f"LogLevel {loglevel} for {l.name} enabled")
        config.dbg_level = 1
      if loglevel=="DEBUG":
        l.setLevel(logging.DEBUG)
        log.info(f"LogLevel {loglevel} for {l.name} enabled")
        config.dbg_level = 1
      if loglevel=="DEBUG1":
        l.setLevel(logging.DEBUG)
        log.info(f"LogLevel {loglevel} for {l.name} enabled")
        config.dbg_level = 1
      if loglevel=="DEBUG2":
        l.setLevel(logging.DEBUG)
        log.info(f"LogLevel {loglevel} for {l.name} enabled")
        config.dbg_level = 2
      if loglevel=="DEBUG3":
        l.setLevel(logging.DEBUG)
        log.info(f"LogLevel {loglevel} for {l.name} enabled")
        config.dbg_level = 3
    return PlainTextResponse(content='set log level '+loglevel, status_code=200)

@api_router.get('/status')
@api_router.get(api_root+'/status')
def get_api_status():
    """
    return status of the backend
    """
    s=""
    s+="API Version: "+config.version+"\n"
    dbversion=get_dbversion(config.repoengine)+"\n"
    s+="Repository: "+str(dbversion)+"\n"

    for l in logging.root.manager.loggerDict:
        if "plainbi" in l:
            lg=logging.getLogger(l)
            s+=l+": "+logging.getLevelName(lg.getEffectiveLevel())

    s+="\nLog Level: "+str(config.dbg_level)+"\n"

    s+="\nall loggers: "+", ".join(logging.root.manager.loggerDict)

    return PlainTextResponse(content=s)


@api_router.post(api_root+'/email')
@audited
def sndemail(request: Request, tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    send an smtp email

    needs environment variables SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    """
    dbg("++++++++++ entering sndemail")
    out={}

    dbg("sndemail: parse request data")
    item = parse_json_body(raw_body)

    dbg("sndemail: get smtp config")
    try:
        # SMTP server configuration
        smtp_server = os.environ["SMTP_SERVER"] # "smtp.gmail.com"
        smtp_port = int(os.environ["SMTP_PORT"])
        smtp_user = os.environ["SMTP_USER"] # "your_email@gmail.com"
        smtp_password = os.environ.get("SMTP_PASSWORD") # "your_password" or none if env does not exist
        if isinstance(smtp_password,str):
          if len(smtp_password)==0:
              smtp_password=None
    except Exception as e:
        err("sendmail error: %s", str(e))
        out["error"]="sendemail"
        out["message"]="Email Konfiguration invalid"
        return myjsonify(out, 500)
        # Create the email headers and body

    dbg("sndemail: check email params")
    if "to" not in item.keys() or "subject" not in item.keys() or "body" not in item.keys():
        err("sendmail error: to, subject or body in request post arguments missing")
        out["error"]="sendemail"
        out["message"]="Email invalid"
        return myjsonify(out, 500)
    email_message = f"From: {smtp_user}\nTo: {item['to']}\nSubject: {item['subject']}\n\n{item['body']}"
    dbg("sndemail: send email")
    try:
        # Connect to the SMTP server
        dbg("sndemail: connect to smtp server")
        server = smtplib.SMTP(smtp_server, smtp_port)
        # Log in to the server
        if smtp_password is not None:
            # login to mailserver if password is specified
            dbg("sndemail: login to smtp server (there is a password)")
            server.login(smtp_user, smtp_password)
        # Send the email
        dbg("sndemail: send the mail")
        server.sendmail(smtp_user, item["to"], email_message)
        # Disconnect from the server
        dbg("sndemail: quit from server")
        server.quit()
    except Exception as e:
        err("sendmail error: %s", str(e))
        out["error"]="sendemail"
        out["message"]="Email konnte nicht versendet werden"
        return myjsonify(out, 500)
    out["message"]="Email wurde versendet"
    return myjsonify(out)


@api_router.get(api_root+'/distinctvalues/{db}/{tabnam}/{colnam}')
@audited
def distinctvalues(db: str, tabnam: str, colnam: str, request: Request,
                    tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get distinct values of a column in a table

    returns json with keys "data", "total_count"
    """
    dbg("++++++++++ entering distinctvalues")
    dbg("distinctvalues param tab is <%s>",str(tabnam))
    dbg("distinctvalues param col is <%s>",str(colnam))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    if db in ("0", "repo"):
        tabnam = repo_table_prefix + tabnam
    out={}
    q=request.query_params.get('q')
    limit=request.query_params.get('limit')
    offset=request.query_params.get('offset')
    db_typ=get_db_type(dbengine)
    if db_typ=="mssql": cast_typ="varchar(max)"
    elif db_typ=="oracle": cast_typ="varchar2(4000)"
    else: cast_typ="varchar"
    inner=f"SELECT DISTINCT {colnam} AS dv FROM {tabnam} WHERE {colnam} IS NOT NULL"
    params=None
    if q:
        wrapped=f"SELECT dv FROM ({inner}) dv_sub WHERE LOWER(CAST(dv AS {cast_typ})) LIKE :q"
        params={"q": f"%{q.lower()}%"}
    else:
        wrapped=f"SELECT dv FROM ({inner}) dv_sub"
    try:
        count_items,count_cols=db_exec(dbengine,f"SELECT COUNT(*) FROM ({wrapped}) cnt_sub",params)
        real_total=int(count_items[0][count_cols[0]]) if count_items else 0
    except Exception:
        real_total=None
    data_sql=wrapped+add_offset_limit(db_typ,offset,limit,"dv")
    try:
        items,columns=db_exec(dbengine,data_sql,params)
    except Exception as e:
        out["error"]="distinctvalues error"
        out["detail"]=str(e)
        return myjsonify(out, 500)
    out["data"]=[row["dv"] for row in pre_jsonify_items_transformer(items)]
    out["total_count"]=real_total if real_total is not None else len(items)
    dbg("leaving distinctvalues and return json result")
    return myjsonify(out)

@api_router.post(api_root+'/exec/{db}/{procname}')
@audited
def dbexec(db: str, procname: str, request: Request,
           tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    run execute procedure in database
    currently only for MSSQL
    """
    dbg("++++++++++ entering dbexec")
    dbg_api_call(request)
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    dbtype=get_db_type(dbengine)

    sqlstmt = None # init
    item = parse_json_body(raw_body)
    if dbtype=="mssql":
        sqlstmt = f"EXEC {procname}"
    else:
        out["error"] = "dbexec"
        out["message"] = "database type not supported"
        return myjsonify(out, 500)

    first_key=True
    for key, value in item.items():
        if first_key:
            first_key = False
            sqlstmt += " "
        else:
            sqlstmt += ", "
        sqlstmt += f"{key} = {value}"
    dbg("dbexec: sql=%s",sqlstmt)

    try:
        #items, columns = db_exec(dbengine,sqlstmt)
        x = db_exec(dbengine,sqlstmt)
        dbg(str(type(x)))
        if isinstance(x,tuple):
            out["data"]=x[0]
            out["columns"]=x[1]
        else:
            out["message"]="sql executed"
    except SQLAlchemyError as e_sqlalchemy:
        err("dbexec_sql_errors: %s", str(e_sqlalchemy))
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-dbexec"
            out["message"]+=" bei dbexec"
        return myjsonify(out, 500)
    except Exception as e:
        err("dbexec exception: %s ",str(e))
        if last_stmt_has_errors(e, out):
            out["error"]+="-dbexec"
            out["message"]+=" beim dbexec"
        return myjsonify(out, 500)

    if isinstance(out,dict):
        if "error" in out.keys():
            return myjsonify(out, 500)
    return myjsonify(out)

###########################
##
## CRUD
##
###########################

# Define routes for CRUD operations
@api_router.get(api_prefix+'/{db}/{tab}')
@audited
def get_all_items(db: str, tab: str, request: Request,
                   tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get database table contents (all rows)

    returns json with keys "data", "columns", "total_count"
    """
    dbg("++++++++++ entering get_all_items")
    dbg_api_call(request)
    dbg("get_all_items: param tab is <%s>",str(tab))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    cols=request.query_params.get('cols')
    is_versioned = True if request.query_params.get('v') is not None else False
    myfilter, out = parse_filter(request.query_params.get('q'),request.query_params.get('filter'), out)
    if "error" in out.keys():
        return myjsonify(out, 500)
    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    mycustomsql = request.query_params.get('customsql')
    dbg("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,e=sql_select(dbengine,tab,order_by,offset,limit,with_total_count=True,versioned=is_versioned,filter=myfilter,customsql=mycustomsql,column_list=cols)
    if isinstance(e,str) and e=="ok":
        dbg("get_all_items sql_select ok")
    else:
        dbg("get_all_items sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    has_format_param = True if request.query_params.get('format') is not None else False
    if has_format_param: # we want to download the data in CSV or Excel Format
        dbg("get_all_items: download data")
        fmt=request.query_params.get('format')
        df = pd.DataFrame(items)
        html_cols=request.query_params.get('html_cols')
        if html_cols:
            _strip=lambda x: re.sub(r'<[^>]+>','',str(x)) if x is not None and str(x)!='None' else x
            for _hc in html_cols.split(','):
                _hc=_hc.strip()
                if _hc in df.columns: df[_hc]=df[_hc].apply(_strip)
        if fmt=="XLSX":
            dbg("get_all_items: XLSX format")
            tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.xlsx')
            try:
                output = pd.ExcelWriter(tmpfile,engine="xlsxwriter")
                output.book.set_properties({"encoding":"utf-8"})
                fmt_xl.header_style = None
                df.to_excel(output, index=False, sheet_name="daten")
                output.close()
            except Exception as e0:
                err("get_all_items to_excel exception: %s ",str(e0))
                out["error"]="get_all_items-toxls"
                out["message"]="Fehler beim Prozessieren der Daten für den Download (XLSX)"
                out["detail"]=str(e0)
                err(traceback.format_exc())
                log.exception(e0)
                return myjsonify(out, 500)
            try:
                with open(tmpfile, 'rb') as file:
                    content = file.read()
            finally:
                try: os.remove(tmpfile)
                except OSError: pass
            dbg("get_all_items: return response")
            return Response(
                content,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment;filename=mydata.xlsx'}
            )
        elif fmt=="CSV":
            dbg("get_all_items: CSV format")
            tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.csv')
            # Prepare the CSV file
            try:
                df.to_csv(tmpfile, index=False)
            except Exception as e0:
                err("get_all_items to_csv exception: %s ",str(e0))
                out["error"]="get_all_items-tocsv"
                out["message"]="Fehler beim Prozessieren der Daten für den Download (CSV)"
                out["detail"]=str(e0)
                err(traceback.format_exc())
                log.exception(e0)
                return myjsonify(out, 500)
            # Return the CSV file as a download
            try:
                with open(tmpfile, 'rb') as file:
                    content = file.read()
            finally:
                try: os.remove(tmpfile)
                except OSError: pass
            return Response(
                content,
                media_type='text/csv',
                headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
            )
        elif fmt=="TXT":
            dbg("get_all_items txt separated with tabs")
            tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.txt')
            df.to_csv(tmpfile, index=False, sep='\t', quoting=csv.QUOTE_NONE)
            # Return the file as a download
            try:
                with open(tmpfile, 'rb') as file:
                    content = file.read()
            finally:
                try: os.remove(tmpfile)
                except OSError: pass
            return Response(
                content,
                media_type='text/csv',
                headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
            )
        else:
            out["error"]="get_all_items-invalid-format"
            out["message"]="Das Format muss XLSX/CSV/TXT sein"
            out["detail"]=None
            return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    dbg("leaving get_all_items and return json result")
    dbg("out=%s",str(out))
    return myjsonify(out)

# Define routes for CRUD operations

def _get_item_common(tab, pk, request):
    """shared body for get_item / get_item_post: resolve pk, fetch the row, build the response"""
    out={}
    is_versioned=False
    pkcols=[]
    cols=None
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="cols":
                cols=value
                dbg("cols option %s",cols)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
    mycustomsql = request.query_params.get('customsql')
    return is_versioned,pkcols,cols,mycustomsql

@api_router.get(api_prefix+'/{db}/{tab}/{pk}')
@audited
def get_item(db: str, tab: str, pk: str, request: Request,
             tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get a specific row from a table given by database tablename and id (or any primary key)

    returns jsons with key "data"
    """
    dbg("++++++++++ entering get_item")
    dbg_api_call(request)
    dbg("get_items: param tab is <%s>",str(tab))
    dbg("get_items: param pk/id is <%s>",str(pk))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    is_versioned,pkcols,cols,mycustomsql=_get_item_common(tab,pk,request)
    dbg("tab %s pk %s")
    # check if pk is compound
    if pk == '#' or pk == '@':
        dbg("get_item: data")
        pk = parse_json_body(raw_body)
    else:
        pk=prep_pk_from_url(pk)

    #
    out=get_item_raw(dbengine, tab, pk, pk_column_list=pkcols, column_list=cols, versioned=is_versioned, customsql=mycustomsql)
    if "data" in out.keys():
        if len(out["data"])>0:
            # jk20240910 for date formatting on output
            pre_jsonify_items_transformer(out["data"])
            dbg("out:%s",str(out))
            dbg("leaving get_item with success and json result")
            return myjsonify(out)
        else:
            dbg("no record found")
            dbg("leaving get_item with 204 no record forund")
            return Response(status_code=204)
    dbg("leaving get_item with error 500 and return json result")
    return myjsonify(out, 500)

@api_router.post(api_prefix+'/{db}/{tab}/{pk}')
@audited
def get_item_post(db: str, tab: str, pk: str, request: Request,
                   tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get a specific row from a table given by database tablename and id (or any primary key)

    returns jsons with key "data"
    """
    dbg("++++++++++ entering get_item_post")
    dbg_api_call(request)
    dbg("get_items: param tab is <%s>",str(tab))
    dbg("get_items: param pk/id is <%s>",str(pk))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    is_versioned,pkcols,cols,mycustomsql=_get_item_common(tab,pk,request)
    dbg("tab %s pk %s")
    # check if pk is compound
    if pk == '#' or pk == '@':
        dbg("get_item: data")
        pk = parse_json_body(raw_body)
    else:
        pk=prep_pk_from_url(pk)

    #
    out=get_item_raw(dbengine, tab, pk, pk_column_list=pkcols, column_list=cols, versioned=is_versioned, customsql=mycustomsql)
    if "data" in out.keys():
        if len(out["data"])>0:
            dbg("get_item_raw call output in get_item_post:"+str(out))
            pre_jsonify_items_transformer(out["data"])
            dbg("out:%s",str(out))
            dbg("leaving get_item with success and json result")
            return myjsonify(out)
        else:
            dbg("no record found")
            dbg("leaving get_item with 204 no record forund")
            return Response(status_code=204)
    dbg("leaving get_item with error 500 and return json result")
    return myjsonify(out, 500)


@api_router.post(api_prefix+'/{db}/{tab}')
@audited
def create_item(db: str, tab: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    create a new row in the database (insert)

    returns json mit den keys "data"  i.e. the inserted row (might have new data f.e. sequence values, trigger)
    """
    dbg("++++++++++ entering create_item")
    dbg_api_call(request)
    dbg("create_item: param tab is <%s>",str(tab))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    pkcols=[]
    is_versioned=False
    seq=None
    usercol=None
    # check options
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="seq":
                seq=value
                dbg("pk sequence %s",seq)
            if key=="usercol":
                usercol=value
                dbg("usercol %s",usercol)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
    dbg("create_item tab %s pkcols %s seq %s",tab,pkcols,seq)
    mycustomsql = request.query_params.get('customsql')

    dbg("create_item 7")
    item = parse_json_body(raw_body)
    if usercol is not None:
        item[usercol]=tokdata['username']
        dbg("usercol %s set to %s",usercol,item[usercol])
    out = db_ins(dbengine,tab,item,pkcols,is_versioned,seq,changed_by=tokdata['username'],customsql=mycustomsql)
    if isinstance(out,dict):
        if "error" in out.keys():
            return myjsonify(out, 400)
    return myjsonify(out)


@api_router.put(api_prefix+'/{db}/{tab}/{pk}')
@audited
def update_item(db: str, tab: str, pk: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    update a row in a table
    """
    dbg("++++++++++ entering update_item")
    dbg_api_call(request)
    dbg("update_item: param tab is <%s>",str(tab))
    dbg("update_item: param pk is <%s>",str(pk))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    pkcols=[]
    is_versioned=False
    usercol=None
    # check options
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
            if key=="usercol":
                usercol=value
                dbg("usercol enabled for col %s",usercol)
    mycustomsql = request.query_params.get('customsql')
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    # check pk from compound key
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           dbg("pk columns from url form (col:val[:col2:val2...])")
    else:
        dbg("pk columns explicitly from url parameter")
    #
    item = parse_json_body(raw_body)
    dbg("item %s",item,dbglevel=3)
    if usercol is not None:
        item[usercol]=tokdata['username']
        dbg("usercol %s set to %s",usercol,item[usercol])


    out = db_upd(dbengine, tab, pk, item, pkcols, is_versioned, changed_by=tokdata['username'], customsql=mycustomsql)
    if isinstance(out,dict):
        if "error" in out.keys():
            err("=update_item out error (see stdout for more) ======================")
            print("==============================================")
            print("=update_item out error================================")
            pprint.pprint(out)
            print("==============================================")
            return myjsonify(out, 400)

    return myjsonify(out)

@api_router.delete(api_prefix+'/{db}/{tab}/{pk}')
@audited
def delete_item(db: str, tab: str, pk: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    delete a row in a database

    returns 200 or json with error msg
    """
    dbg("++++++++++ entering delete_item")
    dbg_api_call(request)
    dbg("delete_item: param tab is <%s>",str(tab))
    dbg("delete_item: param pk is <%s>",str(pk))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    pkcols=[]
    is_versioned=False
    usercol=None
    # check options
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
            if key=="usercol":
                usercol=value
                dbg("usercol enabled for col %s",usercol)
    dbg("delete_item tab %s pkcols %s ",tab,pkcols)

    pk=prep_pk_from_url(pk)
    dbg("delete_item tab %s pk %s",tab,pk)
    # check pk from compound key
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           dbg("pk columns from url form (col:val[:col2:val2...])")
    else:
        dbg("pk columns explicitly from url parameter")

    dbg("############# pk columns for delete is %s",str(pkcols))
    out = db_del(dbengine, tab, pk, pkcols, is_versioned, changed_by=tokdata['username'])
    if isinstance(out,dict):
        if "error" not in out.keys():
            return PlainTextResponse(content='Record deleted successfully', status_code=200)
        else:
            return myjsonify(out, 400)
    return myjsonify(out)


@api_router.get(api_metadata_prefix+'/{db}/tables')
@audited
def get_metadata_tables(db: str, request: Request,
                         tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get names of all accessible tables in the database

    returns json with key "data"
    """
    dbg("++++++++++ entering get_metadata_tables")
    dbg_api_call(request)
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    out={}
    items,columns,total_count,e=sql_select(dbengine,metadata_tab_query,order_by,offset,limit,with_total_count=False)
    dbg("get_metadata_tables sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)

@api_router.get(api_metadata_prefix+'/{db}/table/{tab}')
@audited
def get_metadata_tab_columns(db: str, tab: str, request: Request,
                              tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get metadata of a table from the database dictionary

    returns json with columns and datatypes
    """
    dbg("++++++++++ entering get_metadata_tab_columns")
    dbg_api_call(request)
    dbg("get_metadata_tab_columns: param tab is <%s>",str(tab))
    dbengine=get_db_by_id_or_alias(db)
    if dbengine is None:
        return myjsonify(nodb_msg, 500)
    out={}
    pkcols=None
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
    dbg('get_metadata_tab_columns: for %s',tab)
    try:
        metadata=get_metadata_raw(dbengine,tab,pk_column_list=pkcols)
    except SQLAlchemyError as e_sqlalchemy:
        if last_stmt_has_errors(e_sqlalchemy, out):
            out["error"]+="-get_metadata_tab_columns"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
        return myjsonify(out, 500)
    except Exception as e:
        if last_stmt_has_errors(e, out):
            out["error"]+="-get_metadata_tab_columns"
            out["message"]+=" beim Lesen der Tabellen Metadaten"
        return myjsonify(out, 500)
    return myjsonify(metadata)

###########################
##
## REPO
##
###########################

# Define routes for REPO operations
@api_router.get(repo_api_prefix+'/resources')
@audited
def get_resource(request: Request,
                  tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get the resources from the repository

    returns json of all applications, adhocs, and external resources
    """
    dbg("++++++++++ entering get_resource")
    dbg_api_call(request)
    prof=get_profile(config.repoengine,tokdata['username'])
    user_id=prof["user_id"]
    out={}
    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    dbg("pagination offset=%s limit=%s",offset,limit)
    
    w_app=add_auth_to_where_clause("plainbi_application",None,user_id)
    w_adhoc=add_auth_to_where_clause("plainbi_adhoc",None,user_id)
    w_ext_res=add_auth_to_where_clause("plainbi_external_resource",None,user_id)
    if not hasattr(config,"repo_db_type"):
        config.repo_db_type=get_db_type(config.repoengine)
    dbg("get_resource config.repo_db_type=%s",config.repo_db_type)
    if config.repo_db_type == 'mssql':
        concat_op='+'
    else:
        concat_op='||'
    dbg("get_resource concat_op=%s",concat_op)
    
    resource_sql=f"""select
'application_'{concat_op}cast(id as varchar) as id
, name
, '/apps/'{concat_op}alias as url
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
'adhoc_'{concat_op}cast(id as varchar) as id
, name
, '/adhoc/' {concat_op} cast(id as varchar) {concat_op} case when coalesce(output_format, 'HTML') <> 'HTML' then '?format='{concat_op}output_format else '' end as url
, '_self' as target
, coalesce(output_format, 'HTML') output_format
, description
, 'Adhoc' as source
, null as dataset
, 'adhoc' as resource_type
, 'Adhoc' as resource_type_de
from plainbi_adhoc padh
{w_adhoc}
union all
select
'external_resource_'{concat_op}cast(id as varchar) as id
, name
, url
, '_blank' as target
, null as output_format
, description
, source
, dataset
, 'external_resource' as resource_type
, source as resource_type_de
from plainbi_external_resource per
{w_ext_res}
"""
    items,columns,total_count,e=sql_select(config.repoengine,resource_sql,order_by,offset,limit,with_total_count=True,is_repo=True,user_id=prof["user_id"])
    dbg("get_resource sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)


# mir zugeordnete Gruppen
@api_router.get(repo_api_prefix+'/groups')
@audited
def get_my_groups(request: Request,
                   tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get my groups
    """
    dbg("++++++++++ entering get_my_groups")
    dbg_api_call(request)
    prof=get_profile(config.repoengine,tokdata['username'])
    user_id=prof["user_id"]
    out={}
    if not hasattr(config,"repo_db_type"):
        config.repo_db_type=get_db_type(config.repoengine)
    #mysql="select g.id, g.name from plainbi_user_to_group ug join plainbi_group g on ug.group_id = g.id where ug.user_id="+prof["user_id"]
    mysql=f"select distinct g.id, g.name from plainbi_user_to_group ug join plainbi_group g on ug.group_id = g.id where ug.user_id={user_id} or {user_id} in (select id from plainbi_user where role_id=1)"
    dbg("get_my_groups sql: %s",mysql)
    items,columns,total_count,e=sql_select(config.repoengine,mysql,order_by=None,offset=None,limit=None,with_total_count=True,is_repo=True,user_id=prof["user_id"])
    dbg("get_my_groups sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)

#
@api_router.get(repo_api_prefix+'/group/{gid}/resources')
@audited
def get_group_resources(gid: str, request: Request,
                         tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    Resourcen gefiltert auf die Gruppe (gid="nogroup" for all resources not in a group, admins only)
    """
    dbg("++++++++++ entering get_my_groups")
    dbg_api_call(request)
    prof=get_profile(config.repoengine,tokdata['username'])
    user_id=prof["user_id"]
    user_is_admin_flag=prof["user_is_admin"]
    out={}
    if not hasattr(config,"repo_db_type"):
        config.repo_db_type=get_db_type(config.repoengine)
    dbg("get_resource config.repo_db_type=%s",config.repo_db_type)
    if config.repo_db_type == 'mssql':
        concat_op='+'
    else:
        concat_op='||'
    dbg("get_resource concat_op=%s",concat_op)
    if gid=="nogroup":
        resource_sql=f"""select
    'application_'{concat_op}cast(id as varchar) as id
    , name
    , '/apps/'{concat_op}alias as url
    , '_self' as target
    , null as output_format
    , null as description
    , null as source
    , null as dataset
    , 'application' as resource_type
    , 'Applikation' as resource_type_de
    from plainbi_application pa
    where '{user_is_admin_flag}'='Y'
    and pa.id not in (select application_id from plainbi_application_to_group)
    union all
    select
    'adhoc_'{concat_op}cast(id as varchar) as id
    , name
    , '/adhoc/' {concat_op} cast(id as varchar) {concat_op} case when coalesce(output_format, 'HTML') <> 'HTML' then '?format='{concat_op}output_format else '' end as url
    , '_self' as target
    , coalesce(output_format, 'HTML') output_format
    , description
    , 'Adhoc' as source
    , null as dataset
    , 'adhoc' as resource_type
    , 'Adhoc' as resource_type_de
    from plainbi_adhoc padh
    where '{user_is_admin_flag}'='Y'
    and padh.id not in (select adhoc_id from plainbi_adhoc_to_group)
    union all
    select
    'external_resource_'{concat_op}cast(id as varchar) as id
    , name
    , url
    , '_blank' as target
    , null as output_format
    , description
    , source
    , dataset
    , 'external_resource' as resource_type
    , source as resource_type_de
    from plainbi_external_resource per
    where '{user_is_admin_flag}'='Y'
    and per.id not in (select external_resource_id from plainbi_external_resource_to_group)
    """
    else:
        if not is_id(gid):
            items, columns = db_exec(config.repoengine,f"select id from plainbi_group where alias='{gid}'")
            if len(items) > 0:
                gid=items[0]["id"]
            else:
                out["error"]="no-such-group-alias"
                out["message"]=f"Berechtigungsgruppe mit dem alias {gid} nicht gefunden"
                return myjsonify(out, 500)
        else:
            items, columns = db_exec(config.repoengine,f"select id from plainbi_group where id={gid}")
            if len(items) < 1:
                out["error"]="no-such-group-id"
                out["message"]=f"Berechtigungsgruppe mit der ID {gid} nicht gefunden"
                return myjsonify(out, 500)
        resource_sql=f"""select
    'application_'{concat_op}cast(id as varchar) as id
    , name
    , '/apps/'{concat_op}alias as url
    , '_self' as target
    , null as output_format
    , null as description
    , null as source
    , null as dataset
    , 'application' as resource_type
    , 'Applikation' as resource_type_de
    from plainbi_application pa
    join plainbi_application_to_group ag
    on pa.id=ag.application_id
    and ag.group_id={gid}
    and ag.group_id in (select ug.group_id from plainbi_user_to_group ug where ug.user_id={user_id} or {user_id} in (select id from plainbi_user where role_id=1))
    union all
    select
    'adhoc_'{concat_op}cast(id as varchar) as id
    , name
    , '/adhoc/' {concat_op} cast(id as varchar) {concat_op} case when coalesce(output_format, 'HTML') <> 'HTML' then '?format='{concat_op}output_format else '' end as url
    , '_self' as target
    , coalesce(output_format, 'HTML') output_format
    , description
    , 'Adhoc' as source
    , null as dataset
    , 'adhoc' as resource_type
    , 'Adhoc' as resource_type_de
    from plainbi_adhoc padh
    join plainbi_adhoc_to_group ag
    on padh.id = ag.adhoc_id
    and ag.group_id={gid}
    and ag.group_id in (select ug.group_id from plainbi_user_to_group ug where ug.user_id={user_id} or {user_id} in (select id from plainbi_user where role_id=1))
    union all
    select
    'external_resource_'{concat_op}cast(id as varchar) as id
    , name
    , url
    , '_blank' as target
    , null as output_format
    , description
    , source
    , dataset
    , 'external_resource' as resource_type
    , source as resource_type_de
    from plainbi_external_resource per
    join plainbi_external_resource_to_group rg
    on per.id=rg.external_resource_id
    and rg.group_id={gid}
    and rg.group_id in (select ug.group_id from plainbi_user_to_group ug where ug.user_id={user_id} or {user_id} in (select id from plainbi_user where role_id=1))
    """
    dbg("get_group_resources sql: %s",resource_sql)
    items,columns,total_count,e=sql_select(config.repoengine,resource_sql,order_by=None,offset=None,limit=None,with_total_count=True,is_repo=True,user_id=prof["user_id"])
    dbg("get_group_resources sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)


# Define routes for REPO operations
@api_router.get(repo_api_prefix+'/{tab}')
@audited
def get_all_repos(tab: str, request: Request,
                   tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get table contents of table <tab> in the repository (table name without prefix plainbi_)

    returns json with keys "data", "columns", "total_count"
    """
    dbg("++++++++++ entering get_all_repos")
    dbg_api_call(request)
    dbg("get_all_repos: param tab is <%s>",str(tab))
    prof=get_profile(config.repoengine,tokdata['username'])
    out={}
    myfilter, out = parse_filter(request.query_params.get('q'),request.query_params.get('filter'), out)
    if "error" in out.keys():
        return myjsonify(out, 500)
    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    mycustomsql = request.query_params.get('customsql')
    dbg("pagination offset=%s limit=%s",offset,limit)
    items,columns,total_count,e=sql_select(config.repoengine,repo_table_prefix+tab,order_by,offset,limit,filter=myfilter,with_total_count=True,is_repo=True,user_id=prof["user_id"],customsql=mycustomsql)
    dbg("get_all_repos sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)

@api_router.get(repo_api_prefix+'/{tab}/{pk}')
@audited
def get_repo(tab: str, pk: str, request: Request,
             tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    get a specific row from a repository table

    returns json with keys "data"
    """
    dbg("++++++++++ entering get_repo")
    dbg("get_repo: param tab is <%s>",str(tab))
    dbg("get_repo: param pk is <%s>",str(pk))
    # check options
    prof=get_profile(config.repoengine,tokdata['username'])
    pkcols=[]
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
    # check if pk is compound
    mycustomsql = request.query_params.get('customsql')
    pk=prep_pk_from_url(pk)
    if tab=="application" and (not is_id(pk)):
        # use alias
        out=get_item_raw(config.repoengine,repo_table_prefix+tab,pk,pk_column_list=["alias"],is_repo=True,user_id=prof["user_id"],customsql=mycustomsql)
    else:
        out=get_item_raw(config.repoengine,repo_table_prefix+tab,pk,pk_column_list=pkcols,is_repo=True,user_id=prof["user_id"],customsql=mycustomsql)
    if "data" in out.keys():
        if len(out["data"])>0:
            pre_jsonify_items_transformer(out["data"])
            dbg("return get_repo out:%s",str(out)[:255],dbglevel=3)
            return myjsonify(out)
        else:
            dbg("no record found")
            return Response(status_code=204)
    dbg("return get_repo but no data")
    return myjsonify(out, 500)


@api_router.post(repo_api_prefix+'/{tab}')
@audited
def create_repo(tab: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    insert a new row into a repository table

    tab : repository table name (without prefix plainbi_)
    Url Options: pk=, seq= (Name of Sequence for PK, in case None/Null is sent)

    return json with keys "data" of the newly inserted row
    """
    dbg("++++++++++ entering create_repo")
    dbg("create_repo: param tab is <%s>",str(tab))
    prof=get_profile(config.repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    dbg("create_repo: check url params")
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
    dbg("create_repo tab %s pkcols %s",tab,pkcols)
    mycustomsql = request.query_params.get('customsql')

    item = parse_json_body(raw_body)
    db_typ = get_db_type(config.repoengine)
    if tab in ["adhoc","application","datasource","external_resource","group","lookup","role","user","group","customsql","adhoc_parameter"]:
        if db_typ=="sqlite":
           seq=tab
        elif db_typ in ("mssql","postgres","oracle"):
           seq="plainbi_"+tab+"_seq"
        else:
           err("create_repo: unknown repo database type")
           seq=None
    else:
        seq=None
    out = db_ins(config.repoengine,repo_table_prefix+tab,item,pkcols,is_versioned,seq,is_repo=True,customsql=mycustomsql)
    if isinstance(out,dict):
        if "error" in out.keys():
            return myjsonify(out, 400)
    return myjsonify(out)


@api_router.put(repo_api_prefix+'/{tab}/{pk}')
@audited
def update_repo(tab: str, pk: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    update a row in the repository

    tab : repository table name (without prefix plainbi_)
    pk : Primary Key Identifier (Primary Key)
    Url Options: pk=

    returns json with keys "data" of the updated row
    """
    dbg("++++++++++ entering update_repo")
    dbg_api_call(request)
    dbg("update_repo: param tab is <%s>",str(tab))
    dbg("update_repo: param pk is <%s>",str(pk))
    prof=get_profile(config.repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
    mycustomsql = request.query_params.get('customsql')
    # check if pk is compound
    pk=prep_pk_from_url(pk)
    # check pk from compound key
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           dbg("pk columns from url form (col:val[:col2:val2...])")
    else:
        dbg("pk columns explicitly from url parameter")

    item = parse_json_body(raw_body)
    dbg("datastring: %s",str(item),dbglevel=3)

    out = db_upd(config.repoengine,repo_table_prefix+tab,pk,item,pkcols,is_versioned,is_repo=True,customsql=mycustomsql)
    if isinstance(out,dict):
        if "error" in out.keys():
            err("=update_repo out error (see stdout for more) ======================")
            print("==============================================")
            print("=update_repo out error================================")
            pprint.pprint(out)
            print("==============================================")
            return myjsonify(out, 400)
    return myjsonify(out)


@api_router.delete(repo_api_prefix+'/{tab}/{pk}')
@audited
def delete_repo(tab: str, pk: str, request: Request,
                 tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    delete a row in the repositoy

    tab : repository table name (without prefix plainbi_)
    pk : Primary Key Identifier (Primary Key) of the row to be deleted
    Url Options: pk=

    returns 200 or json of error message
    """
    dbg("++++++++++ entering delete_repo")
    dbg_api_call(request)
    dbg("delete_repo: param tab is <%s>",str(tab))
    dbg("delete_repo: param pk is <%s>",str(pk))
    prof=get_profile(config.repoengine,tokdata['username'])
    out={}
    pkcols=[]
    is_versioned=False
    # check options
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="pk":
                pkcols=value.split(",")
                dbg("pk option %s",pkcols)
            if key=="v":
                is_versioned=True
                dbg("versions enabled")
    dbg("delete_item tab %s pkcols %s ",tab,pkcols)

    pk=prep_pk_from_url(pk)
    dbg("delete_repo tab %s pk %s",tab,pk)
    # check pk from compound key
    if len(pkcols)==0:
        # pk columns are not explicitly given as url parameter
        if isinstance(pk,dict):
           # there is an url pk in form (col:val)
           pkcols=list(pk.keys())
           dbg("pk columns from url form (col:val[:col2:val2...])")
    else:
        dbg("pk columns explicitly from url parameter")

    dbg("############# pk columns for delete is %s",str(pkcols))
    out = db_del(config.repoengine,repo_table_prefix+tab,pk,pkcols,is_versioned,is_repo=True)
    if isinstance(out,dict):
        if "error" not in out.keys():
            return PlainTextResponse(content='Repo Record deleted successfully', status_code=200)
        else:
            return myjsonify(out, 400)
    return myjsonify(out)

@api_router.get(repo_api_prefix+'/init_repo')
def init_repo():
    """
    initialize the repository: HANDLE WITH CARE and have a backup always
    """
    dbg("++++++++++ entering init_repo")
    with config.repoengine.connect() as conn:
        pass
    create_repo_db(config.repoengine)
    create_app_db(config.repoengine)
    return PlainTextResponse(content='Repo initialized successfully', status_code=200)


###########################
##
## Lookup
##
###########################

@api_router.get(repo_api_prefix+'/lookup/{id}/data')
@audited
def get_lookup(id: str, request: Request,
               tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    return then lookup data defined in the lookup repository table with id or alias
    """
    dbg("++++++++++ entering get_lookup")
    dbg_api_call(request)
    dbg("get_lookup: param id is <%s>",str(id))
    out={}
    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    q = request.query_params.get('q')
    selected = request.query_params.get('selected')
    dbg("get_lookup pagination offset=%s limit=%s q=%s selected=%s",offset,limit,q,selected)
    items,columns,total_count,e=repo_lookup_select(config.repoengine,id,order_by,offset,limit,filter=q,with_total_count=True,username=tokdata["username"],selected=selected)
    dbg("get_lookup sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    return myjsonify(out)

###########################
##
## Adhoc
##
###########################
"""
GET /api/repo/adhoc/<id>/distinctvalues/<col>  Distinct values of a column from the adhoc result (for column filters)
GET /api/repo/adhoc/<id>/data	The data of a adhoc (result of its SQL)
GET /api/repo/adhoc/<id>/data?format=XLSX|CSV	The data of a adhoc (result of its SQL), but as a Excel (XLSX) or CSV file
"""

@api_router.get(repo_api_prefix+'/adhoc/{id}/distinctvalues/{colnam}')
@audited
def adhoc_distinctvalues(id: str, colnam: str, request: Request,
                          tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    dbg("++++++++++ entering adhoc_distinctvalues id=%s col=%s", str(id), str(colnam))
    if not all(c.isalnum() or c == '_' for c in colnam):
        return myjsonify({"error": "Invalid column name"}, 400)
    prof = get_profile(config.repoengine, tokdata['username'])
    user_id = prof["user_id"]
    get_rep_adhoc_res = get_repo_adhoc_sql_stmt(config.repoengine, id, user_id)
    if "error" in get_rep_adhoc_res.keys():
        return myjsonify(get_rep_adhoc_res, 500)
    adhoc_sql = get_rep_adhoc_res["sql"]
    adhoc_datasrc_id = get_rep_adhoc_res["datasrc_id"] or 1
    adhoc_sql = adhoc_sql.replace("$(APP_USER)", tokdata['username'])
    adhoc_sql = adhoc_sql.replace("$(APP_USER_EMAIL)", prof.get("email") or "")
    for key, value in request.query_params.items():
        if key not in ("limit", "offset", "q"):
            adhoc_sql = adhoc_sql.replace("$("+key+")", value)
    q = request.query_params.get('q')
    limit = request.query_params.get('limit')
    offset = request.query_params.get('offset')
    adhoc_dbengine = get_db_by_id_or_alias(adhoc_datasrc_id)
    db_typ = get_db_type(adhoc_dbengine)
    if db_typ == "mssql": cast_typ = "varchar(max)"
    elif db_typ == "oracle": cast_typ = "varchar2(4000)"
    else: cast_typ = "varchar"
    inner = f"SELECT DISTINCT x.{colnam} AS dv FROM ({adhoc_sql}) x WHERE x.{colnam} IS NOT NULL"
    params = None
    if q:
        wrapped = f"SELECT dv FROM ({inner}) dv_sub WHERE LOWER(CAST(dv AS {cast_typ})) LIKE :q"
        params = {"q": f"%{q.lower()}%"}
    else:
        wrapped = f"SELECT dv FROM ({inner}) dv_sub"
    out = {}
    try:
        count_items, count_cols = db_exec(adhoc_dbengine, f"SELECT COUNT(*) FROM ({wrapped}) cnt_sub", params)
        real_total = int(count_items[0][count_cols[0]]) if count_items else 0
    except Exception:
        real_total = None
    data_sql = wrapped + add_offset_limit(db_typ, offset, limit, "dv")
    try:
        items, columns = db_exec(adhoc_dbengine, data_sql, params)
    except Exception as e:
        out["error"] = "adhoc_distinctvalues error"
        out["detail"] = str(e)
        return myjsonify(out, 500)
    out["data"] = [row["dv"] for row in pre_jsonify_items_transformer(items)]
    out["total_count"] = real_total if real_total is not None else len(items)
    return myjsonify(out)

@api_router.get(repo_api_prefix+'/adhoc/{id}/data')
@api_router.post(repo_api_prefix+'/adhoc/{id}/data')
@audited
def get_adhoc_data(id: str, request: Request,
                    tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    return then adhoc data defined in the adhoc repository table with id or alias
    """
    dbg("++++++++++ entering get_adhoc_data")
    dbg_api_call(request)
    dbg("get_adhoc_data: param id is <%s>",str(id))
    prof=get_profile(config.repoengine,tokdata['username'])
    user_id=prof["user_id"]
    out={}
    myparams=None
    fmt="JSON"
    dbg("get_adhoc_data: check request arguments")
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="format":
                fmt=value
                dbg("adhoc format %s",fmt)
            if key=="params":
                myparams = {}
                slist=value.split(",")
                for s in slist:
                    p=s.split(":")
                    if len(p)>1:
                        myparams[p[0]]=p[1]
                    else:
                        return PlainTextResponse(content="adhoc json parameter is invalid, does not contain semicolon", status_code=500)

    dbg("get_adhoc_data: get request data")
    dbg("get_adhoc_data: databytes: %s",raw_body)
    dataitem = None
    if raw_body is not None:
        dbg("get_adhoc_data: databytes is not None: %s",raw_body)
        if len(raw_body)>0:
            dbg("get_adhoc_data: databytes len > 0: %s",raw_body)
            data_string = raw_body.decode('utf-8')
            dbg("get_adhoc_data: datastring: %s",data_string)
            if data_string is not None:
                dataitem = json.loads(data_string)
                dbg("get_adhoc_data: dataitem: %s",str(dataitem))

    offset = request.query_params.get('offset')
    limit = request.query_params.get('limit')
    order_by = request.query_params.get('order_by')
    dbg("get_adhoc_data pagination offset=%s limit=%s",offset,limit)
    dbg("get_adhoc_data pagination order_by=%s",order_by)
    dbg("get_adhoc_data: get adhoc stmt")
    get_rep_adhoc_res = get_repo_adhoc_sql_stmt(config.repoengine,id,user_id)
    if "error" in get_rep_adhoc_res.keys():
        return myjsonify(get_rep_adhoc_res, 500)
    adhoc_sql = get_rep_adhoc_res["sql"]
    adhoc_datasrc_id = get_rep_adhoc_res["datasrc_id"]
    adhocid  = get_rep_adhoc_res["adhocid"]
    order_by_def  = get_rep_adhoc_res["order_by_def"]
    adhoc_desc  = get_rep_adhoc_res["adhocdesc"]
    adhoc_name  = get_rep_adhoc_res.get("adhocname") or ""
    _audit_id_ctxvar.set(adhocid)
    if adhoc_datasrc_id is None:
        msg="adhoc datasource_id is not set - assuming 1"
        adhoc_datasrc_id = 1
        #log.warning(msg) 
        #return msg, 500
    dbg("get_adhoc_data: parameter substitution")
    # substitute params
    if isinstance(myparams,dict):
        for p,v in myparams.items():
            adhoc_sql=adhoc_sql.replace("$("+p+")",v)
        dbg("get_adhoc_data: adhoc sql after subsitution: %s",adhoc_sql)
    # substitute global environment params
    adhoc_sql=adhoc_sql.replace("$(APP_USER)",tokdata['username'])
    adhoc_sql=adhoc_sql.replace("$(APP_USER_EMAIL)",prof.get("email") or "")
    # substitute request data
    if isinstance(dataitem,dict):
        for p,v in dataitem.items():
            adhoc_sql=adhoc_sql.replace("$("+p+")",v)
    dbg("get_adhoc_data: adhoc sql after data subsitution: %s",adhoc_sql)
    if adhoc_sql is None:
        msg="adhoc id/name invalid oder kein sql beim adhoc hinterlegt"
        err(msg)
        return msg, 500
    dbg("get_adhoc_data: get db type")
    adhoc_dbengine = get_db_by_id_or_alias(adhoc_datasrc_id)
    db_typ = get_db_type(adhoc_dbengine)
    dbg("get_adhoc_data: prepare json pagination")
    effective_order_by = order_by if order_by is not None else order_by_def
    # column filters: filter=col~val (LIKE, case-insensitive) — shared for all formats
    col_filters = []
    for fval in request.query_params.getlist('filter'):
        if '~' in fval:
            parts = fval.split('~', 1)
            col = parts[0]
            if re.match(r'^[\w\s]+$', col, re.UNICODE):
                col_filters.append((col, parts[1]))
    filter_params = None
    if col_filters:
        if db_typ == "mssql": cast_typ = "varchar(max)"
        elif db_typ == "oracle": cast_typ = "varchar2(4000)"
        else: cast_typ = "varchar"
        filter_parts = []
        filter_params = {}
        for i, (col, val) in enumerate(col_filters):
            col_q = f"[{col}]" if db_typ == "mssql" else f'"{col}"'
            filter_parts.append(f"LOWER(CAST(x.{col_q} AS {cast_typ})) LIKE :cf_{i}")
            filter_params[f"cf_{i}"] = f"%{val.lower()}%"
        adhoc_sql = f"SELECT x.* FROM ({adhoc_sql}) x WHERE " + " AND ".join(filter_parts)
        dbg("get_adhoc_data: column filters applied: %s", adhoc_sql)
    if fmt=="JSON":
        dbg("get_adhoc_data: fmt JSON")
        real_total=None
        if limit is not None:
            try:
                count_items,count_cols=db_exec(adhoc_dbengine,f"SELECT COUNT(*) FROM ({adhoc_sql}) cnt_sub",filter_params)
                real_total=int(count_items[0][count_cols[0]]) if count_items else 0
            except Exception:
                pass
        if not col_filters:
            adhoc_sql = f"select x.* from ({adhoc_sql}) x"
        adhoc_sql += add_offset_limit(db_typ,offset,limit,effective_order_by)
        dbg("get_adhoc_data JSON pagination: %s",adhoc_sql)
        dbg("get_adhoc_data pagination offset=%s limit=%s",offset,limit)
    else:
        dbg("get_adhoc_data: not fmt JSON/HTML")
        if effective_order_by is not None:
            dbg("get_adhoc_data: apply effective order by (order by added)")
            adhoc_sql += " order by " + _safe_order_by(effective_order_by, db_typ)
    #
    # handle formats
    dbg("get_adhoc_data: fmt= %s",fmt)
    if fmt=="JSON":
        # execute adhoc sql
        dbg("get_adhoc_data: execute adhoc sql")
        try:
            items, columns = db_exec(adhoc_dbengine,adhoc_sql,filter_params)
        except SQLAlchemyError as e_sqlalchemy:
            err("adhoc_sql_errors: %s", str(e_sqlalchemy))
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-get_adhoc_data"
                out["message"]+=" beim Lesen der Adhoc Daten"
            return myjsonify(out, 500)
        except Exception as e:
            err("get_adhoc_data exception: %s ",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_adhoc_data"
                out["message"]+=" beim Lesen der Adhoc Daten"
            return myjsonify(out, 500)
        dbg("get_adhoc_data: fmt JSON")
        if not isinstance(items,list):
            return PlainTextResponse(content="adhoc json result error", status_code=500)
        out["data"]=pre_jsonify_items_transformer(items)
        out["columns"]=columns
        out["total_count"]=real_total if real_total is not None else len(items)
        return myjsonify(out)
    else:
        dbg("get_adhoc_data: other formats")
        # read data with pandas
        try:
            dbg("adhoc_dbengine %s",str(adhoc_dbengine))
            with adhoc_dbengine.connect() as conn:
                dbg("adhoc_dbengine querying")
                stmt = sql_text(adhoc_sql)
                if filter_params:
                    stmt = stmt.bindparams(**filter_params)
                df = pd.read_sql_query(stmt, conn)
                dbg("adhoc_dbengine query done")
        except SQLAlchemyError as e_sqlalchemy:
            err("adhoc_sql_errors(pd): %s", str(e_sqlalchemy))
            if last_stmt_has_errors(e_sqlalchemy, out):
                out["error"]+="-get_adhoc_data(pd)"
                out["message"]+=" beim Lesen der Adhoc Daten"
            return myjsonify(out, 500)
        except Exception as e:
            err("get_adhoc_data exception(pd): %s ",str(e))
            if last_stmt_has_errors(e, out):
                out["error"]+="-get_adhoc_data(pd)"
                out["message"]+=" beim Lesen der Adhoc Daten"
            return myjsonify(out, 500)

        #dbg("get_adhoc_data: items=%s",str(items))
        dbg("adhoc_dbengine got pandas dataframe")
        if len(df)==0:
            out["error"]="adhoc-no-rows"
            out["message"]="Die Adhoc Abfrage liefert keine Daten"
            out["detail"]="Die Adhoc Abfrage liefert keine Daten"
            dbg("get_adhoc_data: no rows result")
            return myjsonify(out, 500)
        else:
            try:
                # Save the DataFrame to an Excel file
                if fmt=="XLSX":
                    dbg("get_adhoc_data: XLSX format")
                    dbg("adhoc excel")
                    tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.xlsx')
                    datasheet_name="daten"
                    infosheet_name="info"
                    try:
                        output = pd.ExcelWriter(tmpfile,engine="xlsxwriter")
                        output.book.set_properties({"encoding":"utf-8"})
                        fmt_xl.header_style = None
                        #pd.formats.format.header_style = None
                        dbg("get_adhoc_data: df to excel")
                        df.to_excel(output, index=False, sheet_name=datasheet_name)
                        # 20251228 number format
                        workbook = output.book
                        worksheet = output.sheets[datasheet_name]
                        # Apply number format to float columns
                        float_format = workbook.add_format({'num_format': '#,##0.00'})
                        for col_idx, col in enumerate(df.columns, start=1):
                            if df[col].dtype in ['float64', 'float32']:
                                col_letter = get_column_letter(col_idx)
                                float_col_range_str = col_letter+":"+col_letter
                                for row in range(2, len(df) + 2):
                                    worksheet.set_column(float_col_range_str, row, float_format)  
                        # 20251228 end number format
                        output.close()
                    except Exception as e0:
                        err("get_adhoc_data to_excel exception: %s ",str(e0))
                        out["error"]="get-adhoc-data-toxls"
                        out["message"]="Fehler beim Prozessieren der Adhoc-Daten für den Download (XLSX)"
                        out["detail"]=str(e0)
                        err(traceback.format_exc())
                        log.exception(e0)
                        return myjsonify(out, 500)
                    # add sheet with sql
                    book = load_workbook(tmpfile)
                    #autofit columns
                    dbg("get_adhoc_data: add autofit volumns")
                    sheet = book[datasheet_name]
                    sheet_tab = Table(displayName="daten", ref=sheet.dimensions)
                    #default font
                    dbg("get_adhoc_data: default xls font")
                    deffont = Font(name='Arial', size=9, bold=False, italic=False)
                    for row in sheet.iter_rows():
                        for cell in row:
                            cell.font = deffont
                    #header font
                    dbg("get_adhoc_data: header xls font")
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
                    #sheet.auto_filter.ref = sheet.dimensions
                    sheet.add_table(sheet_tab)
                    #for col_num in range(1, sheet.max_column + 1):
                    #    column_letter = get_column_letter(col_num)
                    #    column_range = f'{column_letter}1:{column_letter}{sheet.max_row}'
                    #    sheet.auto_filter.ref = column_range
                    # Create a new sheet "info"
                    dbg("get_adhoc_data: add info sheet")
                    param_labels = {}
                    param_lookup_ids = {}
                    try:
                        param_rows, _ = db_exec(config.repoengine,
                            "SELECT name, name_technical, ui, lookup FROM plainbi_adhoc_parameter WHERE adhoc_id=:adhoc_id",
                            {"adhoc_id": adhocid})
                        if isinstance(param_rows, list):
                            param_labels = {row["name_technical"]: row["name"] for row in param_rows}
                            param_lookup_ids = {
                                row["name_technical"]: row["lookup"]
                                for row in param_rows
                                if row.get("ui") in ("lookup", "lookupn") and row.get("lookup")
                            }
                    except Exception:
                        pass
                    active_params = dataitem if dataitem else (myparams if myparams else {})
                    info_rows = [
                        ("Erstellt am:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        ("Adhoc:", f"{adhoc_name} ({adhocid})"),
                        ("Beschreibung:", adhoc_desc or ""),
                    ]
                    if active_params:
                        info_rows.append(("Filter:", ""))
                        for k, v in active_params.items():
                            display_v = str(v)
                            lkp_id = param_lookup_ids.get(k)
                            if lkp_id and v:
                                try:
                                    lkp_items, _, _, _ = repo_lookup_select(
                                        config.repoengine, lkp_id,
                                        selected=str(v), username=tokdata["username"]
                                    )
                                    if isinstance(lkp_items, list) and lkp_items:
                                        display_v = str(lkp_items[0].get("d", v))
                                except Exception:
                                    pass
                            info_rows.append((param_labels.get(k, k) + ":", display_v))
                    if col_filters:
                        info_rows.append(("Spaltenfilter:", ""))
                        for col, val in col_filters:
                            info_rows.append((col + ":", val))
                    header_labels = {"Filter:", "Spaltenfilter:"}
                    book.create_sheet(title=infosheet_name)
                    new_sheet = book[infosheet_name]
                    for row_idx, (a_val, b_val) in enumerate(info_rows, start=1):
                        new_sheet[f'A{row_idx}'] = a_val
                        new_sheet[f'B{row_idx}'] = b_val
                        cell_font = font if a_val in header_labels else deffont
                        new_sheet[f'A{row_idx}'].font = cell_font
                        new_sheet[f'B{row_idx}'].font = deffont
                    # description: wrap text + row height based on line count
                    DESC_COL_WIDTH = 80
                    desc_cell = new_sheet['B3']
                    desc_cell.alignment = Alignment(wrap_text=True, vertical='top')
                    new_sheet['A3'].alignment = Alignment(vertical='top')
                    desc_text = adhoc_desc or ""
                    desc_lines = desc_text.splitlines() if desc_text else [""]
                    desc_line_count = sum(max(1, math.ceil(len(line) / DESC_COL_WIDTH)) for line in desc_lines)
                    new_sheet.row_dimensions[3].height = max(15, desc_line_count * 15)
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
                        if column_letter == 'B':
                            adjusted_width = min((max_length + 2) * 1.2, DESC_COL_WIDTH)
                        else:
                            adjusted_width = (max_length + 2) * 1.2
                        new_sheet.column_dimensions[column_letter].width = adjusted_width
                    # new sql sheet
                    dbg("get_adhoc_data: add sql sheet")
                    book.create_sheet(title="sql")
                    sql_sheet = book["sql"]
                    sql_sheet.sheet_state = 'hidden'
                    sql_sheet['A1'] = "sql:"
                    sql_sheet['A2'] = adhoc_sql

                    book.save(tmpfile)
                    dbg("get_adhoc_data: xlsx saved")
                    # Return the Excel file as a download
                    try:
                        with open(tmpfile, 'rb') as file:
                            content = file.read()
                    finally:
                        try: os.remove(tmpfile)
                        except OSError: pass
                    dbg("get_adhoc_data: return response")
                    return Response(
                        content,
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        headers={'Content-Disposition': 'attachment;filename=mydata.xlsx'}
                    )
                elif fmt=="CSV":
                    dbg("adhoc csv")
                    tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.csv')
                    # Prepare the CSV file
                    try:
                        df.to_csv(tmpfile, index=False)
                    except Exception as e0:
                        err("get_adhoc_data to_csv exception: %s ",str(e0))
                        out["error"]="get-adhoc-data-tocsv"
                        out["message"]="Fehler beim Prozessieren der Adhoc-Daten für den Download (CSV)"
                        out["detail"]=str(e0)
                        err(traceback.format_exc())
                        log.exception(e0)
                        return myjsonify(out, 500)
                    # Return the CSV file as a download
                    try:
                        with open(tmpfile, 'rb') as file:
                            content = file.read()
                    finally:
                        try: os.remove(tmpfile)
                        except OSError: pass
                    return Response(
                        content,
                        media_type='text/csv',
                        headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
                    )
                elif fmt=="TXT":
                    dbg("adhoc txt separated with tabs")
                    tmpfile=os.path.join(tempfile.gettempdir(),'mydata'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.txt')
                    # Prepare the CSV file
                    df.to_csv(tmpfile, index=False, sep='\t', quoting=csv.QUOTE_NONE)
                    # Return the file as a download
                    try:
                        with open(tmpfile, 'rb') as file:
                            content = file.read()
                    finally:
                        try: os.remove(tmpfile)
                        except OSError: pass
                    return Response(
                        content,
                        media_type='text/csv',
                        headers={'Content-Disposition': 'attachment;filename=mydata.csv'}
                    )
                else:
                    out["error"]="adhoc-invalid-format"
                    out["message"]="Das Format des Adhocs muss XLSX/CSV/TXT/JSON sein"
                    out["detail"]=None
                    return myjsonify(out, 500)
            except Exception as e:
                err("get_adhoc_data exception: %s ",str(e))
                out["error"]="get-adhoc-data-fai"
                out["message"]="Fehler beim Prozessieren der Adhoc-Daten für den Download"
                out["detail"]=str(e)
                return myjsonify(out, 500)
    out["error"]="get_adhoc_data-should-not-occur"
    out["message"] = "adhoc error that should not happen"
    return myjsonify(out, 500)

users=dict()

def load_repo_users():
    """
    load all users defined in the repository into a global dictionary "user"
    i.e. caching for performance reasons
    """
    dbg("++++++++++ entering load_repo_users")
    global users
    out={}
    plainbi_users,columns,cnt,e=sql_select(config.repoengine,'plainbi_user')
    if last_stmt_has_errors(e,out):
        err('error in select users %s', str(e))
        return False
    users = {u["username"]: { "password_hash": u["password_hash"], "email" : u["email"], "rolename" : "Admin" if u["role_id"]==1 else "User" } for u in plainbi_users}

def get_user_by_email(emailname):
    """
    find a user by his email
    i.e. caching for performance reasons
    """
    global users
    dbg("++++++++++ entering get_user_by_email for %s",emailname)
    if not isinstance(emailname,str):
        log.warning("calling get_user_by_email with no string")
        return None
    for unam,u in users.items():
      if "email" in u.keys():
          m = u["email"]
          if isinstance(m,str):
              if m.lower() == emailname.lower():
                  return unam
    return None

def load_repo_users():
    """
    load all users defined in the repository into a global dictionary "user"
    i.e. caching for performance reasons
    """
    dbg("++++++++++ entering load_repo_users")
    global users
    out={}
    plainbi_users,columns,cnt,e=sql_select(config.repoengine,'plainbi_user')
    if last_stmt_has_errors(e,out):
        err('error in select users %s', str(e))
        return False
    users = {u["username"]: { "password_hash": u["password_hash"], "email" : u["email"], "rolename" : "Admin" if u["role_id"]==1 else "User" } for u in plainbi_users}


def authenticate_local(username,password):
    """
    authenticate a local (repository) user
    """
    dbg("++++++++++ entering authenticate_local")
    global users
    load_repo_users()
    if not username or not password:
        err('error invalid cred')
        return False

    if username in users.keys():
        stored_hash = users[username]["password_hash"]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash):
            dbg("login: pwd ok")
            return True
    else:
        dbg("login: user %s is unknown in repo",username)
    dbg("++++++++++ leaving login")
    return False


def authenticate_ldap(login_username,password=None):
    """
    authenticate a user via LDAP Active Directory
    login_username can be ntaccount (cn) or email (mail)
    if no password is then just find the user in the LDAP 
    """
    dbg("++++++++++ entering authenticate_ldap")
    global users
    mail=None
    full_name=None
    load_repo_users()
    authenticated=False
    bindpwd=os.environ.get("LDAP_BIND_USER_PASSWORD")
    bindpwd=bindpwd.strip()
    username=login_username
    dbg("login username from ldap=%s",username)
    s = ldap3.Server(host=os.environ.get("LDAP_HOST"), port=int(os.environ.get("LDAP_PORT")), use_ssl=False, get_info=ldap3.ALL)
    conn_bind = ldap3.Connection(s, user=os.environ.get("LDAP_BIND_USER_DN"), password=bindpwd, auto_bind='NONE', version=3, authentication='SIMPLE')
    if not conn_bind.bind():
        err('error in bind %s', str(conn_bind.result))
        err('check environent variables LDAP_HOST=%s LDAP_PORT=%s LDAP_BIND_USER_DN=%s', os.environ.get("LDAP_HOST"),os.environ.get("LDAP_PORT"),os.environ.get("LDAP_BIND_USER_DN"))
        if "LDAP_BIND_USER_PASSWORD" not in list(dict(os.environ).keys()):
            err("environment variable LDAP_BIND_USER_PASSWORD is missing")
        dbg("++++++++++ entering authenticate_ldap with status %s",authenticated)
        return authenticated,username
    if "LDAP_BASE_DN" not in list(dict(os.environ).keys()):
        err("environment variable LDAP_BASE_DN is missing")
        return authenticated,username
    if os.environ.get("LDAP_SEARCH_EXPR") is not None:
        search_expr=os.environ.get("LDAP_SEARCH_EXPR")
        search_expr=search_expr.replace("{username}",username)
    else:
        if "@" in username:
            # login by email adress
            search_expr=f'(mail={username})'
        else:
            search_expr=f'(&(cn={username}))'
    dbg("LDAP Search Expression is %s",search_expr)
    conn_bind.search(os.environ.get("LDAP_BASE_DN"), search_expr, attributes=['*'])
    for entry in conn_bind.entries:
        dbg("ldap entry=%s",entry.entry_dn)
        # substitute username by returned cn
        #username=entry.cn.value
        try:
            username=entry.sAMAccountName.value.lower()
        except Exception as e:
            dbg("authenticate_ldap:%s",str(e))
            return authenticated, username
        dbg("username (sAMAccountName) from ldap=%s",username)
        if password is not None:
            # validate the login with thepassword
            conn_auth = ldap3.Connection(s, user=entry.entry_dn, password=password, auto_bind='NONE', version=3, authentication='SIMPLE')
            if not conn_auth.bind():
                log.warning("error in bind ldap entry=%s",entry.entry_dn)
                authenticated=False
            else:
                authenticated=True
        # add user to repository
        if username not in users.keys():
            log.warning("new user %s from ldap registered",username)
            mail = entry.mail.value if 'mail' in entry else None
            full_name = entry.displayName.value if 'displayName' in entry else None
            db_adduser(config.repoengine,username,pwd=None,is_admin=False,email=mail,fullname=full_name)
            dbg("refresh profile cache")
            config.profile_cache={}
        break # user was found in ldap, no need to search more
    dbg("++++++++++ entering authenticate_ldap with status %s",authenticated)
    return authenticated,username


@api_router.post('/login')
@api_router.post('/api/login')
def login(request: Request, raw_body: bytes = Depends(get_raw_body)):
    """
    User login, authenticate a user - login procedure
    try LDAP first if it is configured (environment variables)
    otherwise of if no success try local authentication
    summary: login to plainbi backend (Active Directory LDAP or internal user management)
    If the login is successful one can enter the returned access token into the dialog of the Swagger Authorize button. Afterwards you can try out the protected endpoints
    """
    out={}
    dbg("++++++++++ entering login")
    dbg_api_call(request)
    dbg("login")
    audit_req = SimpleNamespace(url=str(request.url), method=request.method)
    referer = request.headers.get('Referer')
    dbg("login referer is %s",str(referer))
    username = None # init
    data_string = raw_body.decode('utf-8')
    item = json.loads(data_string.strip("'"))

    login_username = item['username'].lower()
    dbg("login: username=%s",login_username)
    password = item['password']
    if len(login_username)==0:
        out["message"]='Username muss angegeben werden'
        out["error"]="empty-credentials"
        out["detail"]="invalid-credentials no username"
        return myjsonify(out, 401)
    if len(password)==0:
        out["message"]='Passwort darf nicht leer sein'
        out["error"]="empty-credentials"
        out["detail"]="invalid-credentials no password"
        return myjsonify(out, 401)

    t0 = time.monotonic()

    used_ldap=False
    used_local=False
    authenticated = False
    if "LDAP_HOST" in list(dict(os.environ).keys()):  # if LDAP is defined in environment
        used_ldap=True
        authenticated,username = authenticate_ldap(login_username,password)
        dbg("login authenticated by ldap = %s",authenticated)
        if not authenticated:
            dbg("try locally authenticated")
            username = login_username  # use original name in login mask for local auth
            authenticated = authenticate_local(username,password)
            dbg("login authenticated local = %s",authenticated)
    else:
        username = login_username
        dbg("ldap authentication skipped because no LDAP_HOST environment variable")
        used_local=True
        authenticated = authenticate_local(username,password)
        dbg("login authenticated local = %s",authenticated)
    if authenticated:
        dbg("login authenticated")
        token = jwt.encode({'username': username}, config.SECRET_KEY, algorithm='HS256')
        if username not in users.keys():
            dbg('refresh users array')
            load_repo_users()
        if len(request.query_params) > 0:
            for key, value in request.query_params.items():
                dbg("arg: %s val: %s",key,value)
                if key=="tokenonly":  # this helps for testing
                    return PlainTextResponse(content=token)
        else:
            audit(item['username'], audit_req, status='ok', duration_ms=int((time.monotonic()-t0)*1000), body=None)
            return myjsonify({'access_token': token, "message":"Login erfolgreich", 'role': users[username]["rolename"]}, 200)
    else:
        out["message"]='Benutzername oder Passwort ist falsch'
        out["error"]="invalid-credentials"
        if used_ldap and used_local:
            out["detail"]="invalid-credentials in ldap and local auth"
        elif used_ldap:
            out["detail"]="invalid-credentials in ldap auth"
        elif used_local:
            out["detail"]="invalid-credentials in local auth"
        else:
            out["detail"]="invalid-credentials without ldap and local"
    audit(item['username'], audit_req, status='error', error_msg='invalid-credentials', duration_ms=int((time.monotonic()-t0)*1000), body=None)
    return myjsonify(out, 401)



@api_router.post('/login_sso')
@api_router.post('/api/login_sso')
def login_sso(request: Request, raw_body: bytes = Depends(get_raw_body)):
    """
    User login with sso, authenticate a user
    """
    out={}
    dbg("++++++++++ entering login_sso")
    dbg_api_call(request)
    dbg("login_sso")
    referer = request.headers.get('Referer')
    dbg("login referer is %s",str(referer))
    used_ldap=False
    used_local=False
    authenticated = False
    data_string = raw_body.decode('utf-8')
    dbg("login_sso datastring: %s",data_string,dbglevel=3)
    item = json.loads(data_string.strip("'"))
    dbg("login_sso item: %s",str(item))
    dbg("login_sso state: %s",item.get("state"))
    dbg("now validate data we've got from Microsoft")
    
    dbg("calling auth2 token")
    token_url = f"https://login.microsoftonline.com/{config.PLAINBI_SSO_TENANTID}/oauth2/v2.0/token" 
    dbg("token url is: %s",token_url)
    dbg("config.PLAINBI_SSO_REDIRECT_PATH is: %s",config.PLAINBI_SSO_REDIRECT_PATH)
    #payload = { 'grant_type': 'authorization_code', 'code' : item["code"], 'redirect_uri' : 'http://localhost:5000/getSSOToken',
    payload = { 'grant_type': 'authorization_code', 'code' : item["code"], 'redirect_uri' : config.PLAINBI_SSO_REDIRECT_PATH, 
                'client_id' : config.PLAINBI_SSO_APPLICATION_ID,  'scope' : "User.Read",    'client_secret' :  config.PLAINBI_SSO_CLIENT_SECRET
    }
    response = requests.post(token_url, data=payload)
    dbg("response= "+str(response.text))
    tokens = response.json()
    dbg("tokens= "+str(tokens))
    ms_id_token = tokens['id_token']
    i_ms_key=0
    for ms_key in config.ms_keys:
        try:
            i_ms_key+=1
            #log.info("validate id token try %d ",i_ms_key)
            decoded_id_token = jwt.decode(ms_id_token, key=jwt.algorithms.RSAAlgorithm.from_jwk(ms_key), algorithms=['RS256'], audience = config.PLAINBI_SSO_APPLICATION_ID, issuer=f"https://login.microsoftonline.com/{config.PLAINBI_SSO_TENANTID}/v2.0")
            #dbg("decoded_id_token is %s",str(decoded_id_token))
            useremail = decoded_id_token["preferred_username"]
            username = get_user_by_email(useremail)
            if username is None:
                # try to add user from ldap to plainbi
                warn(f"User {useremail} is not yet in the user table. Try to find it in LDAP and create the user")
                authenticate_ldap(useremail,password=None)
                dbg('refresh users array')
                load_repo_users()
                username = get_user_by_email(useremail)
                if username is None:
                    warn("user %s is not in know users",str(username))
            if username is not None: 
                dbg("username is %s",str(username))
                log.info("Valid Id Token: User unique name: %s",username)
                authenticated = True
            else:
                authenticated = False
                warn("No Valid Id Token : %s",username)
            break
        #except (jwt.InvalidTokenError,jwt.DecodeError):
        except Exception as e_validate:
            warn("validing id token failed with %s",str(e_validate))
            continue
    else:
      err("calling auth2 token: ID Token validation failed")

    if authenticated:
        dbg("login authenticated by SSO for %s",username)
        # create a new token for plainbi web
        token = jwt.encode({'username': username}, config.SECRET_KEY, algorithm='HS256')
        if username not in users.keys():
            dbg('refresh users array')
            load_repo_users()
        if len(request.query_params) > 0:
            for key, value in request.query_params.items():
                dbg("arg: %s val: %s",key,value)
                if key=="tokenonly":  # this helps for testing
                    return PlainTextResponse(content=token)
        else:
            dbg("++++++++++ leaving login_sso authenticated ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            return myjsonify({'access_token': token, "message":"Login erfolgreich", 'role': users[username]["rolename"]}, 200)
    else:
        dbg("login NOT authenticated")
        out["message"]='SSO Login war nicht erfolgreich'
        out["error"]="sso invalid-credentials"
        if used_ldap and used_local:
            out["detail"]="invalid-credentials in ldap and local auth"
        elif used_ldap:
            out["detail"]="invalid-credentials in ldap auth"
        elif used_local:
            out["detail"]="invalid-credentials in local auth"
        else:
            out["detail"]="invalid-credentials without ldap and local"
    return myjsonify(out, 401)


@api_router.post('/passwd')
@api_router.post('/api/passwd')
@audited
def passwd(request: Request,
           tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    change a local users password
    """
    out={}
    dbg("passwd")
    dbg_api_call(request)
    item = parse_json_body(raw_body)
    dbg("passwd items ",str(item),dbglevel=3)
    prof=get_profile(config.repoengine,tokdata['username'])

    plainbi_users,columns,cnt,e=sql_select(config.repoengine,'plainbi_user')
    if last_stmt_has_errors(e,out):
        return myjsonify({'error': 'Invalid User collecting'}, 500)
    users_by_name = {u["username"]: u["password_hash"] for u in plainbi_users}
    dbg(str(users_by_name),dbglevel=3)

    password = item['password']
    dbg("login: password=%s",password)
    p=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    pwd_hashed=p.decode()
    dbg(pwd_hashed,dbglevel=3)

    if prof["role"] == "Admin":
        username = item['username']
        dbg("passwd: username=%s",username)
    else:
        username=prof["username"]
        oldpassword = item['old_password']
        dbg("login: password=%s",oldpassword)
        if username in users_by_name.keys():
            stored_hash = users_by_name[username]
            if bcrypt.checkpw(oldpassword.encode('utf-8'), stored_hash.encode('utf-8') if isinstance(stored_hash, str) else stored_hash):
                dbg("old pwd ok")
                out["error"]="old-password-does-not-match"
                out["message"]="Altes Passwort ist falsch"
                return myjsonify(out)
    out=db_passwd(config.repoengine,username,p)
    dbg("++++++++++ leaving passwd with %s",out)
    return myjsonify(out)


@api_router.get('/hash_passwd/{pwd}')
@api_router.get('/api/hash_passwd/{pwd}')
def hash_passwd(pwd: str):
    """
    just show the hashed password ... mainly for testing reasons
    """
    out={}
    out["pwd"]=pwd
    p=bcrypt.hashpw(pwd.encode('utf-8'),bcrypt.gensalt())
    pwd_hashed=p.decode()
    out["hashed"]=pwd_hashed
    dbg("hashed pwd: "+pwd_hashed,dbglevel=3)
    return myjsonify(out)

@api_router.get('/cache')
@api_router.get('/api/cache')
@audited
def cache(request: Request,
          tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    cache handling of metadata, profile
    url params
      on .... enable caching
      off ... disable caching
      clear ... clear caching
      status ... show current cache handling setting

    returns simple string and status 200
    """
    dbg_api_call(request)
    config.metadataraw_cache={}
    config.profile_cache={}
    dbg("clear_cache: get_metadata_raw: cache created")
    dbg("clear_cache: get_profile: cache created")
    if len(request.query_params) > 0:
        for key, value in request.query_params.items():
            dbg("arg: %s val: %s",key,value)
            if key=="on":
                config.use_cache=True
                dbg("caching enabled")
                config.metadataraw_cache = {}
                config.profile_cache = {}
                return PlainTextResponse(content='cacheing enabled', status_code=200)
            if key=="off":
                config.use_cache=False
                dbg("caching disabled")
                return PlainTextResponse(content='cacheing disabled', status_code=200)
            if key=="clear":
                config.metadataraw_cache={}
                config.profile_cache={}
                dbg("clear_cache: get_metadata_raw: cache created")
                dbg("clear_cache: get_profile: cache created")
                return PlainTextResponse(content='caches cleared', status_code=200)
            if key=="status":
                if config.use_cache:
                    return PlainTextResponse(content='cache is enabled', status_code=200)
                else:
                    return PlainTextResponse(content='cache is disabled', status_code=200)

    return PlainTextResponse(content='caches cleared', status_code=200)

@api_router.get('/clear_cache')
@api_router.get('/api/clear_cache')
@audited
def clear_cache(request: Request,
                tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    clear caches (metadata and profile cache)
    returns simple string and status 200
    """
    dbg_api_call(request)
    config.metadataraw_cache={}
    config.profile_cache={}
    dbg("clear_cache: get_metadata_raw: cache cleared")
    dbg("clear_cache: get_profile: cache cleared")
    return PlainTextResponse(content='caches cleared', status_code=200)

@api_router.get('/protected')
@api_router.get('/api/protected')
@audited
def protected(request: Request,
              tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    show the own username
    """
    dbg("current user=%s",tokdata['username'])
    u=tokdata['username']
    return myjsonify({'message': f'Hello, {u}! You are authenticated.'}, 200)

@api_router.get('/profile')
@api_router.get('/api/profile')
@audited
def profile(request: Request,
            tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    return json of the profile of the current user
    """
    out=get_profile(config.repoengine,tokdata['username'])
    return myjsonify(out)


@api_router.get('/logout')
@api_router.get('/api/logout')
@audited
def logout(request: Request,
           tokdata: dict = Depends(get_current_user), raw_body: bytes = Depends(get_raw_body)):
    """
    logout
    """
    dbg("logout")
    return myjsonify({'message': 'logged out'})

# dsdb export
# Note: intentionally unauthenticated (matches prior behavior - @token_required was
# already disabled here in the Flask version), preserved as-is per migration decision.
@api_router.get(repo_api_prefix+'/application/{appid}/dsdb')
def download_app_dsdb(appid: str, request: Request):
    """
    download a dsdb file for the application object in the repository
    can/should be used for deployments
    """
    dbg("++++++++++ entering download_app_dsdb")
    dbg_api_call(request)
    dbg("download_app_dsdb: app_id is <%s>",str(appid))
    out=get_item_raw(config.repoengine, "plainbi_application", str(appid))
    if "data" in out.keys():
        print("app=",str(out))
        rec=out["data"][0]
        s='{\n  objectList:\n  [\n    {\n      dsdbFormat: 1\n      deploymentType: always\n      current:\n      {\n        version: 1.0\n'
        s+='        statements: [\n          DELETE FROM plainbi_application WHERE id IN ('+str(rec["id"])+');\n        ]\n        data:\n        [\n'
        s+='          {\n            target: plainbi_application\n            columns: [ "id", "name", "alias", "datasource_id", "spec_json"]\n            rows: [\n'
        s+='              [\n                '+str(rec["id"])+', "'+rec["name"]+'", "'+rec["alias"]+'", '+str(rec["datasource_id"])+'\n'
        s+="                '''\n"
        s+= rec["spec_json"]
        s+="\n                '''\n"
        s+="              ]\n            ]\n          }\n        ]\n      }\n    }\n  ]\n}\n"
        # Return the data as a download
        return Response(
            s,
            media_type='text/plain',
            headers={'Content-Disposition': 'attachment; filename=mydata.dsdb'}
        )
    else:
        return PlainTextResponse(content="error getting application or application does not exist", status_code=500)


@api_router.get(repo_api_prefix+'/lookup/{lkpid}/dsdb')
def download_lkp_dsdb(lkpid: str, request: Request):
    """
    download a dsdb file for the lookup object in the repository
    can/should be used for deployments
    """
    dbg("++++++++++ entering download_lkp_dsdb")
    dbg_api_call(request)
    dbg("download_lkp_dsdb: app_id is <%s>",str(lkpid))
    out=get_item_raw(config.repoengine, "plainbi_lookup", lkpid)
    if "data" in out.keys():
        rec=out["data"][0]
        print("lkp=",str(out))
        s='{\n  objectList:\n  [\n    {\n      dsdbFormat: 1\n      deploymentType: always\n      current:\n      {\n        version: 1.0\n'
        s+='        statements: [\n          DELETE FROM plainbi_lookup WHERE id IN ('+str(rec["id"])+');\n        ]\n        data:\n        [\n'
        s+='          {\n            target: plainbi_lookup\n            columns: [ "id", "name", "alias", "datasource_id", "sql_query"]\n            rows: [\n'
        s+='              [\n                '+str(rec["id"])+', "'+rec["name"]+'", "'+rec["alias"]+'", '+str(rec["datasource_id"])+'\n'
        s+="                '''\n"
        s+=rec["sql_query"]
        s+="\n                '''\n"
        s+="              ]\n            ]\n          }\n        ]\n      }\n    }\n  ]\n}\n"
        # Return the data as a download
        return Response(
            s,
            media_type='text/plain',
            headers={'Content-Disposition': 'attachment; filename=mydata.dsdb'}
        )
    else:
        return PlainTextResponse(content="error getting lookup or lookup does not exist", status_code=500)



###########################
##
## Static
##
###########################


@api_router.get('/api/static/{id}')
@api_router.get('/static/{id}')
def getstatic(id: str, request: Request):
    """
    gets a static base64 thing from the repo by id or alias without login
    useful for logo etc.
    base table is plainbi_static_file
    """
    dbg_api_call(request)
    if is_id(id):
        sql_params={ "id" : id}
        sql="select * from plainbi_static_file where id=:id"
    else:
        sql_params={ "alias" : id}
        sql="select * from plainbi_static_file where alias=:alias"
    dbg("getstatic: sql is <%s>",sql)
    s,s_columns = db_exec(config.repoengine, sql , sql_params)
    #dbg("static resource = %s",str(s))
    if len(s)>0:
        for r in s:
            b64 = r["content_base64"]
            return Response(content=base64.b64decode(b64), media_type=r["mimetype"])
    else:
        return PlainTextResponse(content="no data found", status_code=404)

@api_router.get('/api/settings.js')
def getsettingsjs(request: Request):
    """
    base table is plainbi_setting
    """
    dbg("++++++++++ entering getsettingsjs")
    dbg_api_call(request)

    out={}
    dbg("getsettings from db")
    items,columns,total_count,e=sql_select(config.repoengine,"plainbi_settings",with_total_count=True)
    if isinstance(e,str) and e=="ok":
        dbg("getsettings sql_select ok")
    else:
        dbg("getsettings sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)

    def get_setting_from_list(items,nam):
        for i in items:
            if i["setting_name"]==nam:
                if i["setting_value"] is None:
                    return ""
                else:
                    return i["setting_value"]
        return ""

    dbg("construct javascript")
    dbg("settings are %s",str(items))
    s=  "// header and footer\n"
    s=s+f"var APP_TITLE = '"+get_setting_from_list(items,'app_title')+"';\n"
    s=s+f"var HEADER_TITLE = '"+get_setting_from_list(items,'header_title')+"';\n"
    s=s+f"var FOOTER = '"+get_setting_from_list(items,'footer')+"';\n"
    s=s+"\n"
    s=s+"// environment banner\n"
    s=s+f"var ENVIRONMENT_BANNER_TEXT = '"+get_setting_from_list(items,'environment_banner_text')+"'; // e.g. DEV, TEST - leave empty for PROD, as you mostly don't need a banner there\n"
    s=s+"\n"
    s=s+"// theme\n"
    s=s+f"var THEME_COLOR_PRIMARY = '"+get_setting_from_list(items,'color_primary')+"';\n"
    s=s+f"var THEME_COLOR_SUCCESS = '"+get_setting_from_list(items,'color_success')+"';\n"
    s=s+f"var THEME_COLOR_ERROR = '"+get_setting_from_list(items,'color_error')+"';\n"
    s=s+f"var THEME_COLOR_INFO = '"+get_setting_from_list(items,'color_info')+"';\n"
    s=s+f"var THEME_FONT_SIZE = "+get_setting_from_list(items,'font_size')+";\n"
    s=s+f"var CONTACT_EMAIL = '"+get_setting_from_list(items,'contact_email')+"';\n"
    if config.PLAINBI_SSO_APPLICATION_ID is not None:
        dbg("get SSO signin Link")
        #config.PLAINBI_SSO_REDIRECT_PATH
        config.PLAINBI_SSO_SCOPE = ["User.Read"]
        dbg(f"config.PLAINBI_SSO_SCOPE = {config.PLAINBI_SSO_SCOPE}")
        dbg(f"config.PLAINBI_SSO_REDIRECT_PATH = {config.PLAINBI_SSO_REDIRECT_PATH}")
        try:
            ssoapp = msal.ConfidentialClientApplication(client_id=config.PLAINBI_SSO_APPLICATION_ID, authority=config.PLAINBI_SSO_AUTHORITY, client_credential=config.PLAINBI_SSO_CLIENT_SECRET)
            dbg("ssoapp initialized")
            ssourl = ssoapp.get_authorization_request_url(config.PLAINBI_SSO_SCOPE, redirect_uri = config.PLAINBI_SSO_REDIRECT_PATH, state="hugo" )
            dbg(f"sso auth url is: %s",ssourl)
            uri = ssourl
            dbg("auth uri is %s",uri)
            parsed_uri = urlparse(uri)
            query_params = parse_qs(parsed_uri.query)
            vstate=query_params.get('state', [None])[0]
            config.SSO_CODE_CHALLENGE = query_params.get('code_challenge', [None])[0]
            dbg("SSO_CODE_CHALLENGE %s",config.SSO_CODE_CHALLENGE)
            s=s+f"var SSO_SIGNIN_LINK = '"+uri+"';\n"
        except Exception as e_ssoapp:
            err("SSO msal app error: "+str(e_ssoapp))
            config.PLAINBI_SSO_APPLICATION_ID = None
            config.with_sso = False
            log.warning("SSO disabled due to error in msal create app")

    return Response(content=s, media_type="text/javascript; charset=utf-8")

@api_router.get('/api/settings')
def getsettings(request: Request):
    """
    get all settings
    base table is plainbi_setting
    """
    out={}
    dbg("++++++++++ entering getsettings")
    dbg_api_call(request)
    items,columns,total_count,e=sql_select(config.repoengine,"plainbi_settings",with_total_count=True)
    if isinstance(e,str) and e=="ok":
        dbg("getsettings sql_select ok")
    else:
        dbg("getsettings sql_select error %s",str(e))
    if last_stmt_has_errors(e,out):
        return myjsonify(out, 500)
    out["data"]=pre_jsonify_items_transformer(items)
    out["columns"]=columns
    out["total_count"]=total_count
    dbg("leaving getsettings and return json result")
    dbg("out=%s",str(out))
    return myjsonify(out)

@api_router.get('/api/setting/{name}')
def getsetting(name: str, request: Request):
    """
    get a specific setting value by name
    base table is plainbi_settinggs
    """
    dbg("++++++++++ entering getsetting")
    sql_params={ "name" : name}
    dbg_api_call(request)
    sql="select * from plainbi_settings where setting_name=:name"
    dbg("getsetting: sql is <%s>",sql)
    s,s_columns = db_exec(config.repoengine, sql , sql_params)
    dbg("setting %s = %s",name,str(s))
    out={}
    if len(s)>0:
        for r in s:
            out["setting_name"] = r["setting_name"]
            out["setting_value"] = r["setting_value"]
            return myjsonify(out)
    else:
        return PlainTextResponse(content="no data found", status_code=404)

#p_verbose=args.verbose, p_logfile=args.logfile, p_configfile=args.config, p_repository=args.repository, p_database=args.database, p_port=args.port 
def create_app(p_verbose=None, p_logfile=None, p_repository=None, p_database=None, p_port=None):
    """
    create app is the standard FastAPI application factory

    it is called either from
      - the standalone plainbi_backend.py
      - or from the gunicorn/uvicorn factory string (plainbi_backend.api:create_app())
      - unittest scripts (the parameters p_repository and p_database are important here)
    that's why the get_config handling is necessary
    """
    dbg("++++++++++ entering create_app")
    global app

    log.info("creating FastAPI app")
    app = FastAPI(
        title="plainbi Backend API",
        description="REST API for plainbi https://github.com/markuskolp/plainbi",
        version=config.version,
        default_response_class=PlainBIJSONResponse,
    )
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
    app.include_router(api_router)

    repository = p_repository if p_repository else config.repository

    # connect to the repository
    config.repoengine = db_connect(repository)
    if not db_connect_test(config.repoengine):
        err("cannot connect to repository. Check repository database connection description 'PLAINBI_REPOSITORY' in config file or environment")
        sys.exit(0)

    # get datasources from repository
    log.info("load datasources from plainbi_datasource")
    load_datasources_from_repo()

    if not config.database:
        try:
           config.database = config.datasources["1"]
        except Exception as e:
            log.warning("config datasource %s",str(e))
            log.exception(e)

    # if there is a database database now connect to it
    if config.database:
        config.dbengine = db_connect(config.database)
        if not db_connect_test(config.dbengine):
            err("cannot connect to database. Check database connection description 'PLAINBI_DATABASE' in config file or environment")
            sys.exit(0)
        log.info(f"The default database connection description is {config.database}")

    if config.PLAINBI_SSO_APPLICATION_ID is not None:
        log.info("prepare SSO Login")
        #config.PLAINBI_SSO_REDIRECT_PATH
        dbg(f"config.PLAINBI_SSO_AUTHORITY = {config.PLAINBI_SSO_AUTHORITY}")
        dbg(f"config.PLAINBI_SSO_APPLICATION_ID = {config.PLAINBI_SSO_APPLICATION_ID}")
        #dbg(f"config.PLAINBI_SSO_CLIENT_SECRET = {config.PLAINBI_SSO_CLIENT_SECRET}")
        dbg(f"config.PLAINBI_SSO_TENANTID = {config.PLAINBI_SSO_TENANTID}")
        log.info("SSO auth initialized")

        dbg("SSO: get microsoft keys")
        try:
            ms_keys_url = f"https://login.microsoftonline.com/{config.PLAINBI_SSO_TENANTID}/discovery/v2.0/keys"
            config.ms_keys = requests.get(ms_keys_url).json()["keys"]
            #dbg("ms_keys is: %s",str(config.ms_keys))
        except Exception as e_get_ms_keys:
            err("get microsoft keys for SSO: %s",str(e_get_ms_keys))
            err("SSO disabled coz cannot get microsoft keys for tenant %s",config.PLAINBI_SSO_TENANTID)
            config.with_sso=False
            config.ms_keys=[]

    if config.use_cache:
        log.info("Metadata Caching is enabled")
    else:
        log.info("Metadata Caching is NOT enabled")

    # Note: uWSGI's postfork-based pool disposal is gone - gunicorn's post_fork
    # server hook (gunicorn.conf.py) handles this instead, and since each worker
    # process runs create_app() itself (not --preload), every worker builds its
    # own fresh engines/pools here rather than inheriting forked file descriptors.
    return app

