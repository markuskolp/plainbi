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
#from plainbi_backend.db import db_connect,db_connect_test,db_exec
from dotenv import load_dotenv


log = logging.getLogger()

#log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)
#log.debug("start configuration")


class MyConfig:
    pass
    
config = MyConfig()

config.version="0.6 15.02.2024"
config.SECRET_KEY=os.urandom(24)
log.debug("secret key generated")
config.use_cache = False
config.metadataraw_cache = {}
config.profile_cache = {}

def init_config(verbose=None,logfile=None,configfile=None,repository=None,database=None,port=None):
    if hasattr(config,"dbg") or hasattr(config,"repoengine"):
        print("CONFIG already load by plainbi_backend.py")
        log.info("CONFIG already load by plainbi_backend.py")
        return
    # logging
    config.dbg = False
    if verbose:
        config.loglevel = logging.DEBUG
        config.dbg = True
    else:
        if "PLAINBI_BACKEND_LOG_DEBUG" in os.environ.keys():
            if os.environ["PLAINBI_BACKEND_LOG_DEBUG"].lower()=="true":
                config.loglevel = logging.DEBUG
                config.dbg = True
        else:
            config.loglevel = logging.INFO

    if logfile:
        config.logfile = logfile
    else:
        if "PLAINBI_BACKEND_LOGFILE" in os.environ.keys():
            config.logfile = os.environ["PLAINBI_BACKEND_LOGFILE"]
        else:
            config.logfile = None
    log.setLevel(config.loglevel)
    formatter = logging.Formatter('%(message)s')
    logfile_formatter = logging.Formatter('%(asctime)s  %(process)-7s %(module)-20s %(message)s')
    if config.logfile is not None:
        fh = logging.FileHandler(config.logfile, mode='a', encoding='utf-8')
        fh.setFormatter(logfile_formatter)
        fh.setLevel(config.loglevel)
        log.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(config.loglevel)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.info("Welcome to plainbi backend %s",config.version)
    if config.loglevel == logging.DEBUG: 
        log.info("Logging in Debug mode")

    # get config
    config.config_file = None
    if configfile:
        if os.path.isfile(configfile):
            config.config_file=configfile
        else:
            print("Config File %s does not exist" % (configfile))
            log.error("Config File from command line option %s does not exist",configfile)
            sys.exit(0)
    else:
        if "PLAINBI_BACKEND_CONFIG" in os.environ.keys():
            if os.path.isfile(os.environ["PLAINBI_BACKEND_CONFIG"]):
                config.config_file = os.environ["PLAINBI_BACKEND_CONFIG"]
            else:
                print("Config File %s does not exist" % (os.environ["PLAINBI_BACKEND_CONFIG"]))
                log.error("Config File from environment %s does not exist",os.environ["PLAINBI_BACKEND_CONFIG"])
                sys.exit(0)
        else:
            log.info("try to find a config file")
            config_file_list = [".env"]
            if os.name=="nt":
                    if "USERPROFILE" in os.environ.keys():
                        config_file_list.append(os.environ["USERPROFILE"]+"/.env")
                    else:
                        config_file_list.append("~/.env")
            for cfile in config_file_list:
                log.info("testing file %s",cfile)
                if os.path.isfile(cfile):
                    config.config_file=cfile
                    log.info("found config file %s",cfile)
                    break

    if config.config_file is not None:
        print("load config from %s" % (config.config_file))
        log.info("load config from %s",config.config_file)
        load_dotenv(config.config_file)

    # repository connect
    if repository:
        config.repository = repository
    else:
        if "PLAINBI_REPOSITORY" in os.environ.keys():
            config.repository = os.environ["PLAINBI_REPOSITORY"]
        else:
            log.error("No repository database connection description is specified in environment or config file")
            sys.exit(0)
    if config.dbg:
        log.debug("repository is %s",config.repository)

    if database:
        config.database = database
    else:
        if "PLAINBI_DATABASE" in os.environ.keys():
            config.database = os.environ["PLAINBI_DATABASE"]
        else:
            if "1" in config.datasources.keys():
                config.database = config.datasources["1"]
            else:
                config.database = None
                log.error("No default database connection description is specified in environment or config file or in the repository")

    #else:
    #    log.info("No database connection description was provided")


    if port:
        config.port=port
        log.info(f"The port number is {port}")
    else:
        if "PLAINBI_BACKEND_PORT" in os.environ.keys():
            config.port = os.environ["PLAINBI_BACKEND_PORT"]
        else:
            config.port=3001
    log.info(f"plainbi backend running on port {config.port}")


def xload_pbi_envd():
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