import sqlite3
import sys
from utils.config    import *
from utils.constants import *

CONFIG_FILE = "config/appconf.ini"

def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get a connection to the local database and cursor
  con = sqlite3.connect(cfg.config.get("APP","LOCAL_DATABASE_FILE"))
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
    print(SUCC_MSG["DB_CREATE"])
  except sqlite3.OperationalError:
    con.rollback()
    print(ERROR_MSG["DB_EXISTS"],file = sys.stderr)

if __name__ == '__main__':
  main()