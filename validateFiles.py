import sqlite3
import glob
import os
from src.utils.passwordHandler import *
from src.dbConnection          import *
from src.utils.config          import *
from src.fileHandler           import *
from src.validate              import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Functions
def handleProviders(fileHandler,providersDir,publicDirs,bucketDirs,hashesChanged,cfg,conn,cursor,providerEmails):
  for i in range(5):
    if not hashesChanged[i]:
      continue
    errors = []
    provider    = list(providersDir.keys())[i]
    providerDir = list(providersDir.items())[i][1]
    publicDir   = list(publicDirs.items())[i][1]
    bucketDir   = list(bucketDirs.items())[i][1]
    validator   = Validator(cfg,conn,cursor)
    allFiles    = [file for file in glob.glob(f"{providerDir}/**/*",recursive = True) if not os.path.isdir(file)]
    # Check each file
    for file in allFiles:
      extensionWithGzip    = os.path.splitext(os.path.splitext(file)[0])[1].lower()
      extensionWithoutGzip = os.path.splitext(file)[1].lower()
      # Check snx
      if extensionWithGzip == ".snx":
        try:
          validator.validateSnx(file)
          fileHandler.moveSnxFileToPublic(file,publicDir)
        except ValidationError as err:
          errors.append(str(err))
      # Check pos
      elif extensionWithoutGzip == ".pos":
        try:
          validator.validatePos(file)
          fileHandler.movePosFileToBucket(file,bucketDir)
        except ValidationError as err:
          errors.append(str(err))
      elif extensionWithoutGzip == ".vel":
        pass
      # Unknown file
      else:
        errors.append(f"File '{os.path.basename(file)}' with path '{file}' is neither a snx or pbo file!")
    # If there were any errors email them
    if len(errors) != 0:
      errors = [f"Error {count} - {error}" for count,error in enumerate(errors)]
      fileHandler.sendEmail(
        f"Error validating some {provider} files. Attention is required!",
        "There were some errors while validating your files: \n\n" + "\n".join(errors) + "\n\n\n Please re-upload the problematic files or email us back for more information.",
        providerEmails[provider]
      )
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logger = Logs(f"{os.path.join(cfg.getLogsConfig('LOGS_DIR'),cfg.getLogsConfig('VALIDATE_LOGS'))}",cfg.getLogsConfig("MAX_LOGS"))
  # Upload, bucket and public folders
  providersDir = {
    "INGV" : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_ingv/uploads",
    "ROB"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_rob/uploads",
    "SGO"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_ltk/uploads",
    "UGA"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_uga-cnrs/uploads",
    "WUT"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_wut/uploads"
  }
  bucketDirs = {
    "INGV" : f"{cfg.getAppConfig('BUCKET_DIR')}/INGV",
    "ROB"  : f"{cfg.getAppConfig('BUCKET_DIR')}/ROB-EUREF",
    "SGO"  : f"{cfg.getAppConfig('BUCKET_DIR')}/SGO-EPND",
    "UGA"  : f"{cfg.getAppConfig('BUCKET_DIR')}/UGA-CNRS",
    "WUT"  : f"{cfg.getAppConfig('BUCKET_DIR')}/WUT-EUREF"
  }
  publicDirs = {
    "INGV" : f"{cfg.getAppConfig('PUBLIC_DIR')}/INGV",
    "ROB"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/ROB-EUREF",
    "SGO"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/SGO-EPND",
    "UGA"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/UGA-CNRS",
    "WUT"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/WUT-EUREF"
  }
  # Provider emails
  providerEmails = {
    "INGV" : f"{cfg.getEmailConfig('INGV_EMAIL')}",
    "ROB"  : f"{cfg.getEmailConfig('ROB_EMAIL')}",
    "SGO"  : f"{cfg.getEmailConfig('SGO_EMAIL')}",
    "UGA"  : f"{cfg.getEmailConfig('UDA_EMAIL')}",
    "WUT"  : f"{cfg.getEmailConfig('WUT_EMAIL')}"
  }
  # Get a connection to the local database
  con = sqlite3.connect(cfg.getAppConfig("LOCAL_DATABASE_FILE"))
  # Get a connection to the EPOS database
  pgConnection = DBConnection(
    cfg.getEPOSDBConfig("IP"),
    cfg.getEPOSDBConfig("PORT"),
    cfg.getEPOSDBConfig("DATABASE_NAME"),
    cfg.getEPOSDBConfig("USERNAME"),
    PasswordHandler.getPwdFromFolder(cfg.getEPOSDBConfig("PWD_PATH"),sum(ord(c) for c in cfg.getEPOSDBConfig("TOKEN")) - 34),
    logger
  )
  pgConnection.connect()
  # Get a file handler object
  fileHandler = FileHandler(
    providersDir = cfg.getAppConfig("PROVIDERS_DIR"),
    fromEmail = cfg.getEmailConfig("FROM_EMAIL"),
    fromEmailPassword = PasswordHandler.getPwdFromFolder(cfg.getEmailConfig("PWD_PATH"),sum(ord(c) for c in cfg.getEPOSDBConfig("TOKEN")) - 34),
    con = con
  )
  # Get list of the hashes changed of each provider
  hashesChanged = fileHandler.getListOfHashesChanged()
  # Move the files to the corresponding public folder or email the providers if an error occurred
  handleProviders(fileHandler,providersDir,publicDirs,bucketDirs,hashesChanged,cfg,pgConnection.conn,pgConnection.cursor,providerEmails)
  
if __name__ == '__main__':
  main()