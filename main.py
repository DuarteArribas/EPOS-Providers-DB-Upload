import sqlite3

import keyring
import smtplib
import glob
import os
import shutil
from email.mime.text import MIMEText
from os import listdir
from datetime import datetime
from validate import validateProviderDir




from src.utils.config import *
from src.fdetect      import *

# Global variables
CONFIG_FILE   = "config/appconf.cfg"

DATABASE      = "db/detectFiles.db"
PROVIDERS_DIR = "in/providers_sftp/"
OUT_DIR       = "out/public/"

PUBLIC_DIR    = {
  "INGV" : f"{OUT_DIR}/INGV",
  "ROB"  : f"{OUT_DIR}/ROB-EUREF",
  "SGO"  : f"{OUT_DIR}/SGO-EPND",
  "UGA"  : f"{OUT_DIR}/UGA-CNRS",
  "WUT"  : f"{OUT_DIR}/WUT-EUREF"
}
FROM_EMAIL = "duarte.arribas@segal.ubi.pt"
TO_EMAIL   = "duarte.a.arribas@gmail.com"

#Functions


def sendEmail(subject,body):
  """Emails new files to the specified email.

  Parameters
  ----------
  newFiles : str
      the contents of the new files
  """
  server = smtplib.SMTP("smtp.gmail.com",587)
  server.connect("smtp.gmail.com",587)
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
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get a connection to the local database
  con = sqlite3.connect(cfg.getAppConfig("DATABASE_FILE"))
  # Get list of the hashes changed of each provider
  fd  = FileDetect(con,cfg.getAppConfig("PROVIDERS_DIR"))
  hashesChanged = fd.getListOfFilesChanged()
  
  
  
  
  print(hashesChanged)
  
  
  
  
  ## Check which hashes have changed
  #
  ## Validate dirs whose hashes have changed. If valid move them.
  #for provider,providerDir in PROVIDER_DIR.items():
  #  if provider == "INGV" and hashesChanged[0]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["INGV"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "ROB" and hashesChanged[1]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["ROB"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "SGO" and hashesChanged[2]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["SGO"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "UGA" and hashesChanged[3]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["UGA"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "WUT" and hashesChanged[4]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["WUT"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  
if __name__ == '__main__':
  main()