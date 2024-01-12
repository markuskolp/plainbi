# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:57:04 2023

@author: kribbel
"""
import os
import sys
import logging
import urllib
from plainbi_backend.utils import db_subs_env

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.debug("start configuration")


class MyConfig:
        pass
    
config = MyConfig()

config.version="0.5 28.11.2023"
config.SECRET_KEY=os.urandom(24)
log.debug("secret key generated")
config.use_cache = False
config.metadataraw_cache = {}
config.profile_cache = {}

def load_pbi_env():
    log.debug("++++++++++ entering load_pbi_env")

    keylist=dict(os.environ).keys()
    
    pbi_env={}
    pbi_env["db_server"] = os.environ.get("db_server")
    pbi_env["db_username"] = os.environ.get("db_username")
    pbi_env["db_password"] = os.environ.get("db_password")
    pbi_env["db_database"] = os.environ.get("db_database")
    
    
    v = os.environ.get("db_params")
    if v is not None:
        pbi_env["db_params"] = v
        pbi_env["db_params"] = db_subs_env(pbi_env["db_params"],pbi_env) 
        print("pbi_env",str(pbi_env))
    
    pbi_env["db_engine"] = os.environ.get("db_engine")
    pbi_env["db_engine"] = db_subs_env(pbi_env["db_engine"],pbi_env) 
    
    if "db_engine" not in pbi_env.keys():
        log.error("db_engine must be defined")
        log.debug("++++++++++ leaving load_pbi_env")
        sys.exit(1)
    
    
    
    # repo connection
    pbi_env["repo_server"] = os.environ.get("repo_server")
    pbi_env["repo_username"] = os.environ.get("repo_username")
    pbi_env["repo_password"] = os.environ.get("repo_password")
    pbi_env["repo_database"] = os.environ.get("repo_database")
    
    v = os.environ.get("repo_params")
    if v is not None:
        pbi_env["repo_params"] = v
        pbi_env["repo_params"] = db_subs_env(pbi_env["repo_params"],pbi_env) 
        print("pbi_env",str(pbi_env))
    
    pbi_env["repo_engine"] = os.environ.get("repo_engine")
    pbi_env["repo_engine"] = db_subs_env(pbi_env["repo_engine"],pbi_env) 
    config.repo_db_type = None

    if "LDAP_HOST" in keylist:
        pbi_env["LDAP_HOST"] = os.environ.get("LDAP_HOST")
    else:
        log.info("LDAP User authentication disabled - no LDAP_HOST in .env file")
        pbi_env["LDAP_HOST"] = None
    if "LDAP_PORT" in keylist:
        pbi_env["LDAP_PORT"] = int(os.environ.get("LDAP_PORT"))
    else:
        pbi_env["LDAP_PORT"]=None
    if "LDAP_BASE_DN" in keylist:
        pbi_env["LDAP_BASE_DN"] = os.environ.get("LDAP_BASE_DN")
    else:
        pbi_env["LDAP_BASE_DN"]=None
    if "LDAP_BIND_USER_DN" in keylist:
        pbi_env["LDAP_BIND_USER_DN"] = os.environ.get("LDAP_BIND_USER_DN")
    else:
        pbi_env["LDAP_BIND_USER_DN"]=None
    if "LDAP_BIND_USER_PASSWORD" in keylist:
        pbi_env["LDAP_BIND_USER_PASSWORD"] = os.environ.get("LDAP_BIND_USER_PASSWORD")
    else:
        pbi_env["LDAP_BIND_USER_PASSWORD"]=None
    
    log.debug(f'++++++++++ config repoengine={pbi_env["repo_engine"]}')
    log.debug("++++++++++ leaving load_pbi_env")
    return pbi_env