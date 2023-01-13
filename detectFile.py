import sqlite3
import checksumdir
import keyring
import smtplib
import glob
import os
import shutil
from email.mime.text import MIMEText
from os import listdir
from datetime import datetime
from validate import validateProviderDir

# Global variables
DATABASE      = "db/detectFiles.db"
PROVIDERS_DIR = "in/providers_sftp/"
OUT_DIR       = "out/public/"
PROVIDER_DIR  = {
  "INGV" : f"{PROVIDERS_DIR}/providers_ingv/uploads",
  "ROB"  : f"{PROVIDERS_DIR}/providers_rob/uploads",
  "SGO"  : f"{PROVIDERS_DIR}/providers_sgo/uploads",
  "UGA"  : f"{PROVIDERS_DIR}/providers_uga/uploads",
  "WUT"  : f"{PROVIDERS_DIR}/providers_wut/uploads"
}
PUBLIC_DIR    = {
  "INGV" : f"{OUT_DIR}/INGV",
  "ROB"  : f"{OUT_DIR}/ROB-EUREF",
  "SGO"  : f"{OUT_DIR}/SGO-EPND",
  "UGA"  : f"{OUT_DIR}/UGA-CNRS",
  "WUT"  : f"{OUT_DIR}/WUT-EUREF"
}
FROM_EMAIL = "discoveredtheundoubtablesource@outlook.com"
TO_EMAIL   = "duarte.a.arribas@gmail.com"

#Functions
def getHashOfDir(dir):
  """Get checksum hash from a directory recursively.

  Parameters
  ----------
  dir : str
    The directory from which to get the hash

  Returns
  -------
  str
    The hash of the directory
  """
  return checksumdir.dirhash(dir)

def getListOfFilesChanged(con,newHashes):
  """Get the list of files changed.

  Parameters
  ----------
  con : Connection
    An connection to a database
  newHashes: list
    A list of the hashes of the 5 providers

  Returns
  -------
  list
    A list containing a boolean for each provider, indicating if their hash was changed (True) or not (False)
  """
  cur = con.cursor()
  hashesChanged = [False,False,False,False,False]
  for i in range(len(list(PROVIDER_DIR.keys()))):
    res      = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{list(PROVIDER_DIR.keys())[i]}'")
    fileHash = res.fetchall()
    if newHashes[i] != fileHash[0][0]:
      hashesChanged[i] = True
      cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE '{list(PROVIDER_DIR.keys())[i]}'",(newHashes[i],))
      con.commit()
  return hashesChanged

def sendEmail(subject,body):
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
  msg = MIMEText(body)
  msg["Subject"] = subject
  server.sendmail(FROM_EMAIL,TO_EMAIL,msg.as_string())
  server.quit()

def moveToPublic(providerDir,publicDir):
  files    = [file for file in glob.glob(f"{providerDir}/**/*",recursive = True) if not os.path.isdir(file)]
  version  = ""
  coorOrTs = ""
  for file in files:
    with open(file,"r") as f:
      lines = f.readlines()
      lines = [line.strip() for line in lines]
      for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
        if line.split(" ")[0] == "ReleaseNumber":
          version = "".join(line.split(" ")[1:])
          break
    coorOrTs = "TS" if "TS" in file else "Coor" 
    if not os.path.exists(f"{publicDir}/{version}/{coorOrTs}"):
      os.makedirs(f"{publicDir}/{version}/{coorOrTs}")
    shutil.move(file,f"{publicDir}/{version}/{coorOrTs}")

# Main function
def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  # Check which hashes have changed
  hashesChanged = getListOfFilesChanged(con,[getHashOfDir(providerDir) for provider,providerDir in PROVIDER_DIR.items()])
  # Validate dirs whose hashes have changed. If valid move them.
  for provider,providerDir in PROVIDER_DIR.items():
    if provider == "INGV" and hashesChanged[0]:
      validate,validationError = validateProviderDir(providerDir)
      if validate:
        moveToPublic(providerDir,PUBLIC_DIR["INGV"])
      else:
        sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        pass
    if provider == "ROB" and hashesChanged[1]:
      validate,validationError = validateProviderDir(providerDir)
      if validate:
        moveToPublic(providerDir,PUBLIC_DIR["ROB"])
      else:
        sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        pass
    if provider == "SGO" and hashesChanged[2]:
      validate,validationError = validateProviderDir(providerDir)
      if validate:
        moveToPublic(providerDir,PUBLIC_DIR["SGO"])
      else:
        sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        pass
    if provider == "UGA" and hashesChanged[3]:
      validate,validationError = validateProviderDir(providerDir)
      if validate:
        moveToPublic(providerDir,PUBLIC_DIR["UGA"])
      else:
        sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        pass
    if provider == "WUT" and hashesChanged[4]:
      validate,validationError = validateProviderDir(providerDir)
      if validate:
        moveToPublic(providerDir,PUBLIC_DIR["WUT"])
      else:
        sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        pass
  
if __name__ == '__main__':
  main()