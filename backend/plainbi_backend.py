# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

@author: kribbel
"""
import os
import sys
import argparse
import logging

from plainbi_backend.db import db_passwd,db_connect,db_connect_test,db_exec
from plainbi_backend.api import create_app
from plainbi_backend.config import config
from plainbi_backend.repo import create_repo_db
from dotenv import load_dotenv

# Create a new ArgumentParser object
parser = argparse.ArgumentParser(description='PlainBI Application Backend')
# Define the command-line arguments
#parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
parser.add_argument('-P', '--port', type=int, help='The port number to use (default 3001)')
parser.add_argument('-u', '--username', type=str, help='The username for the database connection')
parser.add_argument('-c', '--config', type=str, help='path to the config file')
parser.add_argument('-p', '--password', type=str, help='The password for the database connection')
parser.add_argument('-d', '--database', type=str, help='The database connection description')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
parser.add_argument('-r', '--repository', type=str, help='The repository database connection description')
parser.add_argument('-t', '--testdb', type=str, help='test the sqlalchemy connection string')
parser.add_argument('-l', '--logfile', type=str, help='logfile')
parser.add_argument('-x', '--passwd', type=str, help='Datenbankpasswort setzen')
parser.add_argument('-I', '--initrepo', action='store_true', help='Repository initialisieren')
parser.add_argument('-V', '--version', action='store_true', help='show plainbi backend version')
# Parse the arguments
args = parser.parse_args()

# logging
dbg = False
if args.verbose:
    config.loglevel = logging.DEBUG
    dbg = True
else:
    if "PLAINBI_BACKEND_LOG_DEBUG" in os.environ.keys():
        config.loglevel = logging.DEBUG
        dbg = True
    else:
        config.loglevel = logging.INFO

log = logging.getLogger()
if args.logfile:
    config.logfile = args.logfile
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

config.version="0.6 14.02.2024"
log.info("Welcome to plainbi backend %s",config.version)
if config.loglevel == logging.DEBUG: 
    log.info("Logging in Debug mode")

# show the version
if args.version:
    print(config.version)
    sys.exit(0)

if args.testdb:
    d=db_connect(args.testdb)
    if db_connect_test(d):
       print("connection to %s successfull" % (args.testdb))
    else:
       print("ERROR: cannot connect to %s" % (args.testdb))
    sys.exit(0)

# get config
config.config_file = None
if args.config:
    if os.path.isfile(args.config):
        config.config_file=args.config
    else:
        print("Config File %s does not exist" % (args.config))
        log.error("Config File from command line option %s does not exist",args.config)
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
        for config_file in [".env","~/.env",]:
            log.info("testing file %s",config_file)
            if os.path.isfile(config_file):
                config.config_file=config_file
                log.info("loading file %s",config_file)
                break
if config.config_file is not None:
    print("load config from %s" % (config.config_file))
    log.info("load config from %s",config.config_file)
    load_dotenv(config.config_file)

# repository connect
if args.repository:
    config.repository = args.repository
else:
    if "PLAINBI_REPOSITORY" in os.environ.keys():
        config.repository = os.environ["PLAINBI_REPOSITORY"]
    else:
        log.error("No repository database connection description is specified in environment or config file")
        sys.exit(0)
if dbg:
    log.debug("repository is %s",config.repository)
config.repoengine = db_connect(config.repository)
if not db_connect_test(config.repoengine):
    log.error("cannot connect to repository. Check repository database connection description 'PLAINBI_REPOSITORY' in config file or environment")
    sys.exit(0)

# get datasources from repository
config.datasources={}
datasrc_sql = "select * from plainbi_datasource"
datasrc_items, datasrc_columns = db_exec(config.repoengine,datasrc_sql)
for i in datasrc_items:
    config.datasources[str(i["id"])]=i["db_type"]
    config.datasources[i["alias"]]=i["db_type"]


# Access the argument values
if args.username:
    log.info(f"The username is {args.username}")
#else:
#    log.info("No username was provided")

if args.password:
    log.info(f"The password is {args.password}")
#else:
#    log.info("No password was provided")


if args.database:
    config.database = args.database
else:
    if "PLAINBI_DATABASE" in os.environ.keys():
        config.database = os.environ["PLAINBI_DATABASE"]
    else:
        if "1" in config.datasources.keys():
            config.database = config.datasources["1"]
        else:
            config.database = None
            log.error("No default database connection description is specified in environment or config file or in the repository")
    if config.database is not None:
        config.dbengine = db_connect(config.database)
        if not db_connect_test(config.dbengine):
            log.error("cannot connect to database. Check database connection description 'PLAINBI_DATABASE' in config file or environment")
            sys.exit(0)
        log.info(f"The default database connection description is {config.database}")

#else:
#    log.info("No database connection description was provided")


if args.port:
    app_port=args.port
    log.info(f"The port number is {args.port}")
else:
    if "PLAINBI_BACKEND_PORT" in os.environ.keys():
        app_port = os.environ["PLAINBI_BACKEND_PORT"]
    else:
        app_port=3001
log.info(f"plainbi backend running on port {app_port}")

log.info("start server "+__name__)
app=create_app()

if args.passwd:
    log.info("set passwd for user ")
    log.info(f"{args.username}")
    log.info(f"{args.passwd}")
    p=config.bcrypt.generate_password_hash(args.passwd)
    pwd_hashed=p.decode()
    log.info(f"{pwd_hashed}")
    #p=bcrypt.hashpw(item[c].encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
    db_passwd(config.repoengine,args.username,pwd_hashed)
    log.info("passwort set")
    sys.exit(0)

if args.initrepo:
    log.info("initialize repo")
    create_repo_db(config.repoengine)
    log.info("repository initialized")
    sys.exit(0)

if __name__ == '__main__':
    app.run(debug=dbg,host='0.0.0.0', port=app_port,use_reloader=False)