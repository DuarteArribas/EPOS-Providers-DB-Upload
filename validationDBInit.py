import sqlite3
import sys
from src.utils.config import *

CONFIG_FILE = "config/appconf.cfg"

def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get a connection to the local database and cursor
  con = sqlite3.connect(cfg.getAppConfig("LOCAL_DATABASE_FILE"))
  cur = con.cursor()
  # Create table
  try:
    cur.execute("CREATE TABLE previousFiles(fileName VARCHAR PRIMARY KEY,fileHash VARCHAR)")
    cur.execute("INSERT INTO previousFiles VALUES(?,?)",("INGV",""))
    cur.execute("INSERT INTO previousFiles VALUES(?,?)",("ROB",""))
    cur.execute("INSERT INTO previousFiles VALUES(?,?)",("SGO",""))
    cur.execute("INSERT INTO previousFiles VALUES(?,?)",("UGA",""))
    cur.execute("INSERT INTO previousFiles VALUES(?,?)",("WUT",""))
    con.commit()
    print("Database created successfully!")
  except sqlite3.OperationalError:
    con.rollback()
    print("Database already exists. Did nothing...",file = sys.stderr)

if __name__ == '__main__':
  main()