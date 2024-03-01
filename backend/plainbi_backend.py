# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

Plainbi Backend Standalone

This part does not run in normal UWSGI mode or in Unitests

Link to github Project and more Doku
https://github.com/markuskolp/plainbi

@author: kribbel
"""
import os
import sys
import argparse
import logging
log = logging.getLogger()

from plainbi_backend.config import config, get_config
from plainbi_backend.db import db_passwd, db_connect, db_connect_test, db_exec
from plainbi_backend.api import create_app
from plainbi_backend.repo import create_repo_db
#from dotenv import load_dotenv

# Create a new ArgumentParser object
parser = argparse.ArgumentParser(description='PlainBI Application Backend')
# Define the command-line arguments
#parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
parser.add_argument('-c', '--config', type=str, help='path to the config file')
parser.add_argument('-l', '--logfile', type=str, help='logfile')
parser.add_argument('-P', '--port', type=int, help='The port number to use (default 3001)')
parser.add_argument('-d', '--database', type=str, help='The database connection description')
parser.add_argument('-r', '--repository', type=str, help='The repository database connection description')
# help function not running the backend server process
parser.add_argument('-V', '--version', action='store_true', help='show plainbi backend version')
parser.add_argument('-I', '--initrepo', action='store_true', help='Repository initialisieren')
parser.add_argument('-u', '--username', type=str, help='The username for the database connection')
parser.add_argument('-p', '--passwd', type=str, help='set the password for plainbi internal user args.username')
parser.add_argument('-t', '--testdb', type=str, help='test the sqlalchemy connection string')
# Parse the arguments
args = parser.parse_args()

# get all configuration with priority of command line arguments
get_config(verbose=args.verbose,logfile=args.logfile,configfile=args.config,repository=args.repository,database=args.database,port=args.port)

# show the version of the backend (defined in the config.py)
if args.version:
    print(config.version)
    sys.exit(0)

# for convenience a sqlalchemy connect string can be tested here
if args.testdb:
    d=db_connect(args.testdb)
    if db_connect_test(d):
       print("connection to %s successfull" % (args.testdb))
    else:
       print("ERROR: cannot connect to %s" % (args.testdb))
    sys.exit(0)

# for the next actions we need to connect to the repository
config.repoengine = db_connect(config.repository)
if not db_connect_test(config.repoengine):
    log.error("cannot connect to repository. Check repository database connection description 'PLAINBI_REPOSITORY' in config file or environment or on command line")
    sys.exit(0)

app=create_app()

# here we can set a passwort for a user in the repository
# this works only for plainbi internal users - it does not change AD/LDAP passwords
if args.passwd:
    if not args.username:
       print("ERROR: there must be a -u <username> on the commandline for setting a password")
       sys.exit(0)
    log.info("setting passwd for user %s to %s",args.username,args.passwd)
    # the passwort is stored as hash
    p=config.bcrypt.generate_password_hash(args.passwd)
    pwd_hashed=p.decode()
    log.info(f"hashed password is {pwd_hashed}")
    #p=bcrypt.hashpw(item[c].encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
    db_passwd(config.repoengine,args.username,pwd_hashed)
    log.info("password for %s set",args.username)
    sys.exit(0)

log.info("start standalone server "+__name__)
log.warning("Use WSGI for production!")

# initialize the repository
if args.initrepo:
    log.info("initialize repo")
    create_repo_db(config.repoengine)
    log.info("repository initialized")
    sys.exit(0)

if __name__ == '__main__':
    # run the flask app standalone
    app.run(debug=config.dbg, host='0.0.0.0', port=config.port, use_reloader=False)
