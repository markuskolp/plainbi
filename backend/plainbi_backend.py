# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:02:36 2023

@author: kribbel
"""

import argparse
import logging

from plainbi_backend.api import create_app

if __name__ == '__main__':

    # Create a new ArgumentParser object
    parser = argparse.ArgumentParser(description='PlainBI Application Backend')
    # Define the command-line arguments
    parser.add_argument('-P', '--port', type=int, help='The port number to use (default 3001)')
    #parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    parser.add_argument('-u', '--username', type=str, help='The username for the database connection')
    parser.add_argument('-p', '--password', type=str, help='The password for the database connection')
    parser.add_argument('-d', '--database', type=str, help='The database connection description')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode (debug=True)')
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
    
    if args.port:
        app_port=args.port
        logging.info(f"The port number is {args.port}")
    else:
        app_port=3001
        logging.info(f"No port number was provided - default {args.port} is used ")

    #logging.setLevel(logging.DEBUG)
    logging.info("start server "+__name__)
    app=create_app(None)  # no config file yet
    app.run(debug=True,host='0.0.0.0', port=app_port,use_reloader=False)

