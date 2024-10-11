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
#from plainbi_backend.utils import db_subs_env
from dotenv import load_dotenv


log = logging.getLogger()
#log.setLevel(logging.DEBUG)
log.debug("start configuration")

# a class object that will be a container for the config variable that is imported in other scripts and module
class MyConfig:
    pass

# the config variable that acts more or less as a place for global values
config = MyConfig()

# the current version number of plainbi backend
config.version="0.91 10.10.2024"

# create a secret for the plainbi backend api jwt token
config.SECRET_KEY=os.urandom(24)  # for JWT
config.bcrypt_salt=b'$2b$12$26lKTogIpjOIbmp2hYP2au'
log.debug("secret key generated")

# global variables for caches, it holds metadata and profiles so that they are fetched only once from the database
config.use_cache = False
config.metadataraw_cache = {}
config.profile_cache = {}#
config.dbg = False
config.dbg_level = 1

def get_config(verbose=0,logfile=None,configfile=None,repository=None,database=None,port=None):
    """
    get_config initializes the configuration from different sources
    values from the this function parameter list override the values found in environment or config file
    
    If a config file is given or found the values inside are loaded by dotenv into the environment.
    The environment is the best place for configuration variables when plainbi runs in a container

    get_config is called in two places
      - for standalone backend in the main body
      - for uwsgi (actually the normal place when used in production) in the create_app of the Flask part
    """
    # check if get_config was already loaded before and if yes skip the rest.
    # That means if we are in standalone mode than it is not executed again in uwsgi mode
    if hasattr(config,"is_loaded"):
        print("CONFIG already load by plainbi_backend.py")
        log.info("CONFIG already load by plainbi_backend.py")
        return
    # just remember  the config is now loaded
    config.is_loaded = True

    # logging

    # logging level
    if verbose>0:
        # parameter verbose has priority
        config.loglevel = logging.DEBUG
        config.dbg = True
        config.dbg_level = verbose
    else:
        # otherwise  check environment setting
        if "PLAINBI_BACKEND_LOG_DEBUG" in os.environ.keys():
            if os.environ["PLAINBI_BACKEND_LOG_DEBUG"].lower()=="true":
                config.loglevel = logging.DEBUG
                config.dbg = True
        else:
            config.loglevel = logging.INFO

    # log file
    if logfile:
        config.logfile = logfile
    else:
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

    # get configuration file
    config.config_file = None
    if configfile:
        if os.path.isfile(configfile):
            config.config_file=configfile
        else:
            # exit if the config file is not found or readable
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
                config_file_list.append("/etc/plainbi.env")
            for cfile in config_file_list:
                log.info("testing file %s",cfile)
                if os.path.isfile(cfile):
                    config.config_file=cfile
                    log.info("found config file %s",cfile)
                    break
    # if we have a config file the we load it into the environment
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
            # there must be a repository, otherwise quit
            log.error("No repository database connection description is specified in environment or config file")
            sys.exit(0)
    log.debug("repository is %s",config.repository[:15]+"...")

    # a default database.
    config.database = None
    if database:
        config.database = database
    else:
        if "PLAINBI_DATABASE" in os.environ.keys():
            config.database = os.environ["PLAINBI_DATABASE"]
    #else:
    #    log.info("No database connection description was provided")

    # port of api rest server
    if port:
        config.port=port
    else:
        if "PLAINBI_BACKEND_PORT" in os.environ.keys():
            config.port = os.environ["PLAINBI_BACKEND_PORT"]
        else:
            config.port=3001 # default port

    # backend Date format and Datetime format
    if "PLAINBI_BACKEND_DATE_FORMAT" in os.environ.keys():
        config.backend_date_format = os.environ["PLAINBI_BACKEND_DATE_FORMAT"]
        log.info("config date format is %s",config.backend_date_format)
    else: 
        config.backend_date_format = None

    if "PLAINBI_BACKEND_DATETIME_FORMAT" in os.environ.keys():
        config.backend_datetime_format = os.environ["PLAINBI_BACKEND_DATETIME_FORMAT"]
        log.info("config datetime format is %s",config.backend_datetime_format)
    else: 
        config.backend_datetime_format = None

    log.info(f"plainbi backend running on port {config.port}")