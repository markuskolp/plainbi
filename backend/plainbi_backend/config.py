# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:57:04 2023

Configuration handling for the plainbi backend

@author: kribbel
"""
import os
import sys
import logging
import urllib
from dotenv import load_dotenv

#from plainbi_backend.utils import db_subs_env

print("import config")
log = logging.getLogger()
log.debug("start configuration")

# a class object that will be a container for the config variable that is imported in other scripts and module
class MyConfig:
    pass

# the config variable that acts more or less as a place for global values
config = MyConfig()

# check if get_config was already loaded before and if yes skip the rest.
# That means if we are in standalone mode than it is not executed again in uwsgi mode
if not hasattr(config,"is_loaded"):

    print("import config the first time")
    print("get environment (in config)")
    if "PLAINBI_BACKEND_CONFIG" in os.environ:
        print(f"load config given in environment ({os.environ['PLAINBI_BACKEND_CONFIG']})")
        if not os.path.isfile(os.environ["PLAINBI_BACKEND_CONFIG"]):
            print(f"ERROR: {os.environ['PLAINBI_BACKEND_CONFIG']} does not exist")
            sys.exit(1)
        load_dotenv(os.environ["PLAINBI_BACKEND_CONFIG"])
    else:
        print("try to find a config file")
        config_file = None
        config_file_list = [".env"]
        if os.name=="nt":
            if "USERPROFILE" in os.environ.keys():
                config_file_list.append(os.environ["USERPROFILE"]+"/.env")
        else:
            config_file_list.append("~/.env")
            config_file_list.append("/etc/plainbi.env")
        for cfile in config_file_list:
            print("testing file ",cfile)
            if os.path.isfile(cfile):
                config_file=cfile
                print("found config file ",cfile)
                break
        # if we have a config file the we load it into the environment
        if config_file is not None:
            print("load config from %s" % (config_file))
            log.info("load config from %s",config_file)
            load_dotenv(config_file)
        else:  
            print(f"INFO: no config file used")

    # just remember  the config is now loaded
    config.is_loaded = True

    # the current version number of plainbi backend
    VERSION="0.95 30.12.2025"
    config.version=VERSION

    if "PLAINBI_BACKEND_LOGFILE" in os.environ:
        log.debug("overide logfile from command line parameter")
        PLAINBI_BACKEND_LOGFILE = os.environ["PLAINBI_BACKEND_LOGFILE"]
        config.logfile = PLAINBI_BACKEND_LOGFILE

    # create a secret for the plainbi backend api jwt token
    SECRET_KEY = os.urandom(24)  # for JWT
    config.SECRET_KEY= SECRET_KEY
    config.bcrypt_salt=b'$2b$12$26lKTogIpjOIbmp2hYP2au'
    log.debug("secret key generated")

    # global variables for caches, it holds metadata and profiles so that they are fetched only once from the database
    config.use_cache = False
    config.metadataraw_cache = {}
    config.profile_cache = {}#
    config.dbg = False
    config.dbg_level = 1

    SESSION_TYPE = 'filesystem'

    if "PLAINBI_REPOSITORY" in os.environ.keys():
        PLAINBI_REPOSITORY = os.environ["PLAINBI_REPOSITORY"]
        config.repository = PLAINBI_REPOSITORY
        print("plainbi repository set")
    else:
        print("NO plainbi repository set")

    # logging

    # logging level
    if "PLAINBI_VERBOSE" in os.environ and int(os.environ["PLAINBI_VERBOSE"]) > 0:
        # parameter verbose has priority
        config.loglevel = logging.DEBUG
        config.dbg = True
        config.dbg_level = int(os.environ["PLAINBI_VERBOSE"])
    else:
        # otherwise  check environment setting
        if "PLAINBI_BACKEND_LOG_DEBUG" in os.environ.keys():
            if os.environ["PLAINBI_BACKEND_LOG_DEBUG"].lower()=="true":
                config.loglevel = logging.DEBUG
                config.dbg = True
        else:
            config.loglevel = logging.INFO

    if "PLAINBI_BACKEND_LOGFILE" in os.environ.keys():
        config.logfile = os.environ["PLAINBI_BACKEND_LOGFILE"]
    else:
        config.logfile = None

    log.setLevel(config.loglevel)
    formatter = logging.Formatter('%(message)s')  # formatter for screen log
    logfile_formatter = logging.Formatter('%(asctime)s  %(process)-7s %(module)-20s %(levelname)s %(message)s') # formatter for logfile log
    if config.logfile is not None:
        fh = logging.FileHandler(config.logfile, mode='a', encoding='utf-8')
        fh.setFormatter(logfile_formatter)
        fh.setLevel(config.loglevel)
        log.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(config.loglevel)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # welcome message
    log.info("Welcome to plainbi backend %s",config.version)
    if config.loglevel == logging.DEBUG: 
        log.info("Logging in Debug mode")


    # repository connect
    if "PLAINBI_REPOSITORY" in os.environ.keys():
        config.repository = os.environ["PLAINBI_REPOSITORY"]
    else:
        # there must be a repository, otherwise quit
        log.error("No repository database connection description is specified in environment or config file")
        sys.exit(0)
    log.debug("repository is %s",config.repository[:15]+"...")

    # a default database.
    config.database = None
    if "PLAINBI_DATABASE" in os.environ.keys():
        config.database = os.environ["PLAINBI_DATABASE"]

    # port of api rest server
    if "PLAINBI_BACKEND_PORT" in os.environ.keys():
        PLAINBI_BACKEND_PORT = os.environ["PLAINBI_BACKEND_PORT"]
        config.port = int(PLAINBI_BACKEND_PORT)
    else:
        config.port=3001 # default port
        os.environ["PLAINBI_BACKEND_PORT"] = str(config.port)

    if "PLAINBI_BACKEND_HOST" in os.environ.keys():
        PLAINBI_BACKEND_HOST = os.environ["PLAINBI_BACKEND_HOST"]
        config.host = PLAINBI_BACKEND_HOST
    else:
        config.host = "0.0.0.0"
        os.environ["PLAINBI_BACKEND_HOST"] = config.host

    # backend Date format and Datetime format
    if "PLAINBI_BACKEND_DATE_FORMAT" in os.environ.keys():
        PLAINBI_BACKEND_DATE_FORMAT = os.environ["PLAINBI_BACKEND_DATE_FORMAT"]
        config.backend_date_format = PLAINBI_BACKEND_DATE_FORMAT
        log.info("config date format is %s",config.backend_date_format)
    else: 
        config.backend_date_format = None

    if "PLAINBI_BACKEND_DATETIME_FORMAT" in os.environ.keys():
        PLAINBI_BACKEND_DATETIME_FORMAT = os.environ["PLAINBI_BACKEND_DATETIME_FORMAT"]
        config.backend_datetime_format = PLAINBI_BACKEND_DATETIME_FORMAT
        log.info("config datetime format is %s",config.backend_datetime_format)
    else: 
        config.backend_datetime_format = None

    log.info(f"plainbi backend running on port {config.port}")

    if "PLAINBI_SSO_APPLIKATION" in os.environ.keys():
        PLAINBI_SSO_APPLIKATION = os.environ["PLAINBI_SSO_APPLIKATION"]
        config.PLAINBI_SSO_APPLIKATION = PLAINBI_SSO_APPLIKATION
    else: 
        config.PLAINBI_SSO_APPLIKATION = None
    if "PLAINBI_SSO_APPLICATION_ID" in os.environ.keys():
        PLAINBI_SSO_APPLICATION_ID = os.environ["PLAINBI_SSO_APPLICATION_ID"]
        config.PLAINBI_SSO_APPLICATION_ID = os.environ["PLAINBI_SSO_APPLICATION_ID"]
    else: 
        config.PLAINBI_SSO_APPLICATION_ID = None
    if "PLAINBI_SSO_TENANTID" in os.environ.keys():
        PLAINBI_SSO_TENANTID = os.environ["PLAINBI_SSO_TENANTID"]
        config.PLAINBI_SSO_TENANTID = PLAINBI_SSO_TENANTID
    else: 
        config.PLAINBI_SSO_TENANTID = None
    if "PLAINBI_SSO_CLIENT_SECRET" in os.environ.keys():
        PLAINBI_SSO_CLIENT_SECRET = os.environ["PLAINBI_SSO_CLIENT_SECRET"]
        config.PLAINBI_SSO_CLIENT_SECRET = PLAINBI_SSO_CLIENT_SECRET
    else: 
        config.PLAINBI_SSO_CLIENT_SECRET = None
    if "PLAINBI_SSO_REDIRECT_PATH" in os.environ.keys():
        PLAINBI_SSO_REDIRECT_PATH = os.environ["PLAINBI_SSO_REDIRECT_PATH"]
        config.PLAINBI_SSO_REDIRECT_PATH = PLAINBI_SSO_REDIRECT_PATH
    else: 
        config.PLAINBI_SSO_REDIRECT_PATH = None
    if "PLAINBI_SSO_AUTHORITY" in os.environ.keys():
        PLAINBI_SSO_AUTHORITY = os.environ["PLAINBI_SSO_AUTHORITY"]
        config.PLAINBI_SSO_AUTHORITY = PLAINBI_SSO_AUTHORITY
    else: 
        config.PLAINBI_SSO_AUTHORITY = None
else:
    print("CONFIG already load by plainbi_backend.py")
    log.info("CONFIG already load by plainbi_backend.py")

print("end import config")
