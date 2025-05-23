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
from dotenv import load_dotenv

print("plainbi_backend.py starting")
log = logging.getLogger()

# Create a new ArgumentParser object
parser = argparse.ArgumentParser(description='PlainBI Application Backend')
# Define the command-line arguments
#parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
#parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
parser.add_argument('-v', '--verbose', action='count', default=0, help='verbose mode (debug=True)')
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
parser.add_argument('-b', '--base64', type=str, nargs=2, help='insert a file base64 encoded into repository static_file expects <id> and <path>')

# Parse the arguments
print("plainbi_backend.py get args")
args = parser.parse_args()

if args.verbose:
    os.environ["PLAINBI_VERBOSE"] = str(args.verbose)
else:
    os.environ["PLAINBI_VERBOSE"] = str(0)

if args.config is not None:
    """
    when using wsgi directly plainbi_backend is not used, to pass a config file we use the environment here
    it is read out later when config is imported
    """
    print("apply config command parameter to environ")
    os.environ["PLAINBI_BACKEND_CONFIG"]=args.config

"""
# load environment / configuration
print("get environment")
if args.config:
    print(f"load config from --config file in command line specification ({args.config})")
    if not os.path.isfile(args.config):
        print(f"ERROR: {args.config} does not exist")
        sys.exit(1)
    load_dotenv(args.config)
else:
    if "PLAINBI_BACKEND_CONFIG" in os.environ:
        print(f"load config given in environment ({os.environ['PLAINBI_BACKEND_CONFIG']})")
        if not os.path.isfile(os.environ["PLAINBI_BACKEND_CONFIG"]):
            print(f"ERROR: {os.environ['PLAINBI_BACKEND_CONFIG']} does not exist")
            sys.exit(1)
        load_dotenv(os.environ["PLAINBI_BACKEND_CONFIG"])
    else:
        print("try to find a config file")
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
"""

print("plainbi_backend.py imports dbg")
from plainbi_backend.utils import dbg
print("plainbi_backend.py imports db")
from plainbi_backend.db import db_passwd, db_connect, db_connect_test, db_exec, db_add_base64
print("plainbi_backend.py imports create_app")
from plainbi_backend.api import create_app
print("plainbi_backend.py imports create_repo_db")
from plainbi_backend.repo import create_repo_db

print("plainbi_backend.py testdb")
# for convenience a sqlalchemy connect string can be tested here
if args.testdb:
    d=db_connect(args.testdb)
    if db_connect_test(d):
       print("connection to %s successful" % (args.testdb))
    else:
       print("ERROR: cannot connect to %s" % (args.testdb))
    sys.exit(0)

########################## before #############################
########################## before end #############################

print("plainbi_backend.py create app")
app = create_app(p_verbose=args.verbose, p_logfile=args.logfile, p_repository=args.repository, p_database=args.database, p_port=args.port )

print("plainbi_backend.py import config")
from plainbi_backend.config import config

########################## after #############################

# show the version of the backend (defined in the config.py)
if args.version:
    print(app.config["VERSION"])
    sys.exit(0)

# for the next actions we need to connect to the repository
#config.repoengine = db_connect(config.repository)
if "PLAINBI_REPOSITORY" not in app.config:
    log.error("No repository database connection description is specified in environment or config file")
    sys.exit(0)

config.repoengine = db_connect(app.config["PLAINBI_REPOSITORY"])
log.debug("repository is %s",(app.config["PLAINBI_REPOSITORY"])[:15]+"...")

# initialize the repository
if args.initrepo:
    log.info("initialize repo")
    create_repo_db(config.repoengine)
    log.info("repository initialized")
    sys.exit(0)

if not db_connect_test(config.repoengine):
    log.error("cannot connect to repository. Check repository database connection description 'PLAINBI_REPOSITORY' in config file or environment or on command line")
    sys.exit(0)

# help function to base64 encode static files
if args.base64:
    id,p = args.base64
    log.info("upload file <%s> base64 encode to id %s",p,id)
    db_add_base64(config.repoengine,int(id),p)
    sys.exit(0)

########################## after end #############################

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


if __name__ == '__main__':
    # run the flask app standalone
    app.run(debug=config.dbg, host=config.host, port=config.port, use_reloader=False)
