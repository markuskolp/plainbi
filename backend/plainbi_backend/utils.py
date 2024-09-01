# -*- coding: utf-8 -*-
"""
Created on Thu May  4 07:43:34 2023

@author: kribbel
"""

from sqlalchemy.exc import SQLAlchemyError

import logging
log = logging.getLogger(__name__)

import urllib.parse

def db_subs_env(s,d):
    if s is None: return None
    for k,v in d.items():
        if v is None:
            s=s.replace("{"+k+"}","")
        else:
            s=s.replace("{"+k+"}",v)
    return s

def is_id(v):
      try:
        _=int(v)
      except:
        return False
      return True
  
def prep_pk_from_url(pk):
    """

    Parameters
    ----------
    pk : int or string
        DESCRIPTION.

    Returns
    -------
    itself or a dictionary with the key for compound keys

    """
    if ":" in pk:
        pk=pk.strip("(")
        pk=pk.strip(")")
        pkl=pk.split(":")
        i=0
        pkd={}
        while i < len(pkl):
            #pkd[pkl[i]]=pkl[i+1]
            pkd[pkl[i]]=pkl[i+1].replace("+++", "/").replace("---", "?").replace("***", "%") # URL encoding problem: decode +++ to /, --- to ?, *** to %
            #pkd[pkl[i]]=urllib.parse.unquote(pkl[i+1]) # get pk value and decode it (url decoding)
            i+=2
        log.debug("prep_pk_from_url: compound key:%s",str(pkd))
        return pkd
    else:
        #return pk        
        return pk.replace("+++", "/").replace("---", "?").replace("***", "%") # URL encoding problem: decode +++ to /, --- to ?, *** to %
        #return urllib.parse.unquote(pk) # get pk value and decode it (url decoding)

def make_pk_where_clause(pk, pkcols, versioned=False, version_deleted=False, table_alias=None):
    """
      pk ... werte für primary key whereclause 
      pk ... pk column names
      returns  where_clause,vallist
    """
    log.debug("++++++++++ entering make_pk_where_clause")
    log.debug("make_pk_where_clause: param pk is <%s>",str(pk))
    log.debug("make_pk_where_clause: param pkcols is <%s>",str(pkcols))
    log.debug("make_pk_where_clause: param table_alias is <%s>",str(table_alias))
    if table_alias is None:
        alias_prefix=""
    else:
        alias_prefix=table_alias+"."
    w=""
    if isinstance(pk, dict):
        mypk=pk
    else:
        if isinstance(pkcols, list):
            pkcolnam=pkcols[0]
        else:
            pkcolnam=pkcols
        mypk={ pkcolnam : pk }

    if isinstance(pkcols, list):
        if len(pkcols) != len(mypk):
            log.warning("make_pk_where_clause: number of pkcols and pk values do not match! pkcols=<%s> vs mypk=<%s>",str(pkcols),str(mypk))
            #return None,mypk
       
    i=0
    for c,v in mypk.items():
        i+=1
        if i==1:
            w+=" WHERE "
        else:
            w+=" AND "
        w+=alias_prefix+c+"=:"+c

    if versioned:
       if version_deleted:
           # get also last deleted version
           w+=f" AND {alias_prefix}invalid_from_dt='9999-12-31 00:00:00'" 
       else:
           w+=f" AND {alias_prefix}is_current_and_active = 'Y'" 
    log.debug("++++++++++ leaving make_pk_where_clause return whereclause=%s , vallist=%s",w,str(mypk))
    return w, mypk

def last_stmt_has_errors(e,out):
    """
    check error exception

    Parameters
    ----------
    e : TYPE
        DESCRIPTION.
    out : TYPE
        DESCRIPTION.

    Returns
    -------
    True if there were errors, else False

    """
    log.debug("++++++++++ calling last_stmt_has_errors to check for sql errors")
    if str(e)=="ok":
        #log.debug("last_stmt_has_errors: ok is not an error:")
        return False
    log.debug("last_stmt_has_errors: param e is <%s>",str(e))
    log.debug("last_stmt_has_errors: param out is <%s>",str(out))
    if isinstance(e, SQLAlchemyError):
        log.error("last_stmt_has_errors: %s", str(SQLAlchemyError))
        out["error"]="sql-error"
        out["message"]="SQL Exception"
        if hasattr(e, 'code'):
            out["code"]=e.code
        if hasattr(e,"__dict__"):
            if isinstance(e.__dict__,dict):
                if "orig" in e.__dict__.keys():
                    out["detail"]=e.__dict__['orig']
                else:
                    out["detail"]=str(e)
                if "sql" in e.__dict__.keys():
                    out["error_sql"]=e.__dict__['sql']
            else:
                out["detail"]=str(e)
        else:
            out["detail"]=str(e)
        log.exception(e)
        log.debug("++++++++++ leaving last_stmt_has_errors with SQL Error")
        return True
    if isinstance(e,Exception):
        log.error("last_stmt_has_errors: exception: %s", str(e))
        out["error"]="python-error"
        out["message"]="Python Exception"
        out["detail"]=str(e.__class__)
        if hasattr(e, "__dict__"):
             if "message" in e.__dict__.keys(): out["detail"]+="/"+str(e.__dict__['message'])
        log.exception(e)
        log.debug("++++++++++ leaving last_stmt_has_errors with non-SQL Error")
        return True
    return False

