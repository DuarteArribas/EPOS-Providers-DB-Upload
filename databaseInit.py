import sqlite3
from src.utils.config import *

CONFIG_FILE = "config/appconf.cfg"

def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get a connection to the local database and cursor
  con = sqlite3.connect(cfg.getAppConfig("DATABASE_FILE"))
  cur = con.cursor()
  # Create table
  cur.execute("CREATE TABLE previousFiles(fileName VARCHAR PRIMARY KEY,fileHash VARCHAR)")
  cur.execute("INSERT INTO previousFiles VALUES(?,?)",("INGV",""))
  cur.execute("INSERT INTO previousFiles VALUES(?,?)",("ROB",""))
  cur.execute("INSERT INTO previousFiles VALUES(?,?)",("SGO",""))
  cur.execute("INSERT INTO previousFiles VALUES(?,?)",("UGA",""))
  cur.execute("INSERT INTO previousFiles VALUES(?,?)",("WUT",""))
  con.commit()

if __name__ == '__main__':
  main()