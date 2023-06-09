# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

@author: kribbel
"""
import os
import sys
import argparse
import logging

from plainbi_backend.db import db_passwd
from plainbi_backend.api import create_app
from plainbi_backend.config import config
from plainbi_backend.repo import create_repo_db


# Create a new ArgumentParser object
parser = argparse.ArgumentParser(description='PlainBI Application Backend')
# Define the command-line arguments
parser.add_argument('-P', '--port', type=int, help='The port number to use (default 3001)')
#parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
parser.add_argument('-u', '--username', type=str, help='The username for the database connection')
parser.add_argument('-p', '--password', type=str, help='The password for the database connection')
parser.add_argument('-d', '--database', type=str, help='The database connection description')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
parser.add_argument('-r', '--repository', type=str, help='The repository database connection description')
parser.add_argument('-x', '--passwd', type=str, help='Datenbankpasswort setzen')
parser.add_argument('-I', '--initrepo', action='store_true', help='Repository initialisieren')
# Parse the arguments
args = parser.parse_args()

# Access the argument values
if args.username:
    logging.info(f"The username is {args.username}")
else:
    logging.info("No username was provided")

if args.password:
    logging.info(f"The password is {args.password}")
else:
    logging.info("No password was provided")

if args.database:
    logging.info(f"The database connection description is {args.database}")
else:
    logging.info("No database connection description was provided")

if args.repository:
    logging.info(f"The repository database connection description is {args.repository}")
else:
    logging.info("No repository database connection description was provided")

if args.port:
    app_port=args.port
    logging.info(f"The port number is {args.port}")
else:
    app_port=3001
    logging.info(f"No port number was provided - default {args.port} is used ")

if args.verbose:
    dbg=True
else:
    dbg=False

#logging.setLevel(logging.DEBUG)
logging.info("start server "+__name__)
app=create_app(None,p_repository=args.repository)  # no config file yet
if dbg: 
    app.logger.setLevel(logging.DEBUG)
    print("debug mode")
if args.passwd:
    logging.info("set passwd for user ")
    logging.info(f"{args.username}")
    logging.info(f"{args.passwd}")
    p=config.bcrypt.generate_password_hash(args.passwd)
    pwd_hashed=p.decode()
    logging.info(f"{pwd_hashed}")
    #p=bcrypt.hashpw(item[c].encode('utf-8'),b'$2b$12$fb81v4oi7JdcBIofmi/Joe')
    db_passwd(config.repoengine,args.username,pwd_hashed)
    logging.info("passwort set")
    sys.exit(0)

if args.initrepo:
    logging.info("initialize repo")
    create_repo_db(config.repoengine)
    logging.info("repository initialzied")
    sys.exit(0)


if __name__ == '__main__':
    app.run(debug=dbg,host='0.0.0.0', port=app_port,use_reloader=False)

