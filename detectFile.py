import sqlite3
import os
from os import listdir
from os.path import isfile, join

# Global variables
DATABASE  = "db/detectFiles.db"
IN_FOLDER = "in"


def getFiles(dir):
  """Get files from a directory.

  Parameters
  ----------
  dir : str
      The directory to get the files from

  Returns
  -------
  lst
      List of files in the directory
  """
  return [f for f in os.listdir(dir) if isfile(join(dir,f))]


def getNewFiles(con,cur,files):
  """Check if the given files already exist in the database. If not, consider them new.

  Parameters
  ----------
  con   : Connection
      A connection object
  cur   : Cursor
      A cursor object
  files : lst
      A list of files to check against the database 

  Returns
  -------
  lst
      A list of new files
  """
  filesNotInDB = []
  res          = cur.execute("SELECT filename FROM previousFiles")
  filesInDb    = res.fetchall()
  for f in files:
    if f not in [filesInDbNormalized[0] for filesInDbNormalized in filesInDb]:
      cur.execute("INSERT INTO previousFiles VALUES(?)",(f,))
      con.commit()
      filesNotInDB.append(f)
  return filesNotInDB
  
def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  cur = con.cursor()
  
if __name__ == '__main__':
  main()