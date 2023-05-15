# -*- coding: utf-8 -*-
"""
Created on Thu May  4 07:43:34 2023

@author: kribbel
"""
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
