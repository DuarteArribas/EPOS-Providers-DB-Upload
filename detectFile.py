import sqlite3
from os import listdir
from os.path import isfile, join

# Global variables
DATABASE  = "db/detectFiles.db"
IN_FOLDER = "in"

# Open database connection
con = sqlite3.connect(DATABASE)
cur = con.cursor()

def getFiles(dir):
  return [f for f in os.listdir(dir) if isfile(join(dir,f))]