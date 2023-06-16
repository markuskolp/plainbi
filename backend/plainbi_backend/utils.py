# -*- coding: utf-8 -*-
"""
Created on Thu May  4 07:43:34 2023

@author: kribbel
"""

from sqlalchemy.exc import SQLAlchemyError

import logging
log = logging.getLogger(__name__)

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
      except ValueError:
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
            pkd[pkl[i]]=pkl[i+1]
            i+=2
        log.debug("compound key:%s",str(pkd))
        return pkd
    else:
        return pk        

def make_pk_where_clause(pk, pkcols, versioned=False, version_deleted=False):
    """
      pk ... werte für primary key whereclause 
      pk ... pk column names
      returns  where_clause,vallist
    """
    log.debug("++++++++++ entering make_pk_where_clause")
    log.debug("make_pk_where_clause: param pk is <%s>",str(pk))
    log.debug("make_pk_where_clause: param pkcols is <%s>",str(pkcols))
    w=""
    val={}
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
            log.error("number of pkcols and pk values do not match")
            return None,None
       
    i=0
    for c,v in mypk.items():
        i+=1
        if i==1:
            w+=" WHERE "
        else:
            w+=" AND "
        w+=c+"=:"+c

    if versioned:
       if version_deleted:
           # get also last deleted version
           w+=" AND invalid_from_dt='9999-12-31 00:00:00'" 
       else:
           w+=" AND is_current_and_active = 'Y'" 
    log.debug("make_pk_where_clause: return whereclause=%s , vallist=%s",w,val)
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
    log.debug("++++++++++ entering last_stmt_has_errors")
    log.debug("last_stmt_has_errors: param e is <%s>",str(e))
    log.debug("last_stmt_has_errors: param out is <%s>",str(out))
    if isinstance(e, SQLAlchemyError):
        log.error(str(SQLAlchemyError))
        if hasattr(e, 'code'):
            out["error"]=e.code
        else:
            out["error"]="error"
        if hasattr(e,"__dict__"):
            if isinstance(e.__dict__,dict):
                if "orig" in e.__dict__.keys():
                    out["message"]=e.__dict__['orig']
                else:
                    out["message"]=str(e)
                if "sql" in e.__dict__.keys():
                    out["error_sql"]=e.__dict__['sql']
            else:
                out["message"]=str(e)
        else:
            out["message"]=str(e)
        out["detail"]=None
        return True
    if isinstance(e,Exception):
        log.error(str(e))
        out["error"]=1
        out["message"]=str(e.__class__)
        out["detail"]=None
        if hasattr(e, "__dict__"):
             if "message" in e.__dict__.keys(): out["message"]=str(e.__dict__['message'])
        return True
    return False