import sqlite3
from os import listdir
from os.path import isfile, join

# Global variables
DATABASE  = "db/detectFiles.db"
IN_FOLDER = "in"


def getFiles(dir):
  """Get files from a directory

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

def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  cur = con.cursor()
  
if __name__ == '__main__':
  main()