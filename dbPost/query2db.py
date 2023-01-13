#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This a program to perform SQL queries from the command line.

    Usage:
        query2db.py (-h | --help)
        query2db.py -q <query>

    Options:
        -h --help     Show the the usage and options.
        -q --query    SQL query to execute between ""

    Example:
        query2db.py -q "SELECT version();"

    Copyright:
        Copyright (C) 2018  UBI/SEGAL

    License:
        This code is distributed under Creative Commons Attribution-Non
        Commercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License.
        For a human readable interpretation of the license, please see
        http://creativecommons.org/licenses/by-nc-sa/4.0/
        The license file and notice of copyright is included with this release.
        NOTICE

    Project:
        This is part of EPOS - European Research Infrastructure on Solid Earth
        project. The GNSS Data and Products source scripts are distributed by
        https://gitlab.com/segalubi/
        This project has received funding from the European Union’s Horizon
        2020 research and innovation programme under grant agreement N° 676564

    TODO:
        In queries with timestamp fields, the field 'date' should be replaced
        by the following function to_char(date, 'YYYY-MM-DD') to fix the output
        e.g. SELECT id,name,to_char(epoch, 'YYYY-MM-DD') FROM reference_frame;
"""
import argparse
from configparser import ConfigParser

import psycopg2

def config(file= 'query2db.cfg', section='postgresql'):
    """ Load database connection parameters

    :param file: configuration file with database access parameters
    :type file: basestring

    :param section: configuration section with the database access parameters
    :type section: basestring

    :returns database connection parameters (host, database, user, password)
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(file)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Block {0} not found in {1} file'.format(section, file))
    return db
 # ----------------------------------------------------------------------------
def connect():
    """ Connect to the PostgreSQL database server
    """
    conn = None
    # ArgumentParser to get the SQL query (-q))
    parse = argparse.ArgumentParser()
    parse.add_argument("-q","--query",required=True,help="SQL query to execute delimited by quotation marks")
    args = parse.parse_args()
    sql = {}
    params ={}
    if args.query:
        sql = args.query
    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('\nConnecting to database',params["database"])
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        print('\nQUERY->\n',sql)
        cur.execute(sql) 
        # display the query output
        print('\nRESULT->')
        rows = cur.fetchall()
        for row in rows:
            print (' ',row)
        # close the communication with the PostgreSQL server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            # close the connection to the PostgreSQL server
            conn.close()
            print('\nConnection to database ',params["database"],'closed!\n')

if __name__ == '__main__':
    connect()
