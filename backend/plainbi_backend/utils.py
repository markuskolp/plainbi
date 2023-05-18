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