import sqlite3
import os
import smtplib
import keyring
import checksumdir
from email.mime.text import MIMEText
from os import listdir
from os.path import isfile, join

# Global variables
DATABASE   = "db/detectFiles.db"
IN_FOLDER  = "in/providers_sftp/"
PROVIDERS  = {
  "INGV" : f"{IN_FOLDER}/providers_ingv",
  "ROB"  : f"{IN_FOLDER}/providers_rob",
  "SGO"  : f"{IN_FOLDER}/providers_sgo",
  "UGA"  : f"{IN_FOLDER}/providers_uga",
  "WUT"  : f"{IN_FOLDER}/providers_wut"
}

#Functions
def getHashOfDir(dir):
  return checksumdir.dirhash(dir)

def checkForNewFiles(con,cur,newHashes):
  hashesChanged = [False,False,False,False,False]
  for i in range(len(list(PROVIDERS.keys()))):
    res      = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{list(PROVIDERS.keys())[i]}'")
    fileHash = res.fetchall()
    if newHashes[i] != fileHash[0][0]:
      hashesChanged[i] = True
      cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE '{list(PROVIDERS.keys())[i]}'",(newHashes[i],))
      con.commit()
  return hashesChanged
  
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
  msg = MIMEText(F"New files available! - {newFiles}")
  msg["Subject"] = "You've got new files!"
  server.sendmail(FROM_EMAIL,TO_EMAIL,msg.as_string())
  server.quit()

# Main function
def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  cur = con.cursor()
  
  
  
  # Get filenames and hashes from the specified directory
  files    = getFilenamesAndHashes(IN_FOLDER)
  # Remove from the database files that were deleted
  removeFromDatabaseIfDeleted(con,cur,files[1])
  # If there are new files, email them
  newFiles = getNewFiles(con,cur,files[0],files[1])
  if(newFiles):
    emailNewFiles(newFiles)
  
if __name__ == '__main__':
  main()