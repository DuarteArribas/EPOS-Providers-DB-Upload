import sqlite3
import os
import smtplib
import keyring
import hashlib
from email.mime.text import MIMEText
from os import listdir
from os.path import isfile, join

# Global variables
DATABASE   = "db/detectFiles.db"
IN_FOLDER  = "in"
FROM_EMAIL = ""
TO_EMAIL   = ""

def getFilenamesAndHashes(dir):
  """Get filenames and hashes from a directory.

  Parameters
  ----------
  dir : str
      The directory to get the files from

  Returns
  -------
  tuple
      (List of filenames in the directory,List of file hashes in the directory)
  """
  hashing      = hashlib.sha256()
  hashList     = []
  filenameList = []
  for f in os.listdir(dir):
    if(isfile(join(dir,f))):
      with open(join(dir,f),"r"):
        hashing.update(f.encode('utf-8'))
      hashList.append(hashing.hexdigest())
      filenameList.append(f)
  return (filenameList,hashList)


def getNewFiles(con,cur,filenames,fileHashes):
  """Check if the given files already exist in the database. If not, consider them new.

  Parameters
  ----------
  con        : Connection
      A connection object
  cur        : Cursor
      A cursor object
  filenames  : lst
      List of filenames in the directory
  fileHashes : lst
      List of file hashes in the directory

  Returns
  -------
  lst
      A list of new files
  """
  filesNotInDB  = []
  res           = cur.execute("SELECT fileHash FROM previousFiles")
  hashesInDb    = res.fetchall()
  for i in range(len(filenames)):
    if fileHashes[i] not in [hashesInDbNormalized[0] for hashesInDbNormalized in hashesInDb]:
      cur.execute("INSERT INTO previousFiles VALUES(?)",(fileHashes[i],))
      con.commit()
      filesNotInDB.append(filenames[i])
  return filesNotInDB
  
def emailNewFiles(newFiles):
  """Emails new files to the specified email.

  Parameters
  ----------
  newFiles : str
      the contents of the new files
  """
  server = smtplib.SMTP("smtp-mail.outlook.com",587)
  server.connect("smtp-mail.outlook.com",587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(FROM_EMAIL,keyring.get_password("system","EMAIL_TO_SEND"))
  msg = MIMEText(F"New files available! -{newFiles}")
  msg["Subject"] = "You've got new files!"
  server.sendmail(FROM_EMAIL,TO_EMAIL,msg.as_string())
  server.quit()
  
def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  cur = con.cursor()
  # Get filenames and hashes from the specified directory
  files    = getFilenamesAndHashes(IN_FOLDER)
  # If there are new files, email them
  newFiles = getNewFiles(con,cur,files[0],files[1])
  if(newFiles):
    emailNewFiles(newFiles)
  
if __name__ == '__main__':
  main()