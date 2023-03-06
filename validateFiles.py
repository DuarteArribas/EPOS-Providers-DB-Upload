import sqlite3
import os
from src.dbConnection import *
from src.utils.config import *
from src.fileHandler  import *
from src.validate     import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Functions
def handleProviders(fileHandler,providerDirs,publicDirs,hashesChanged,cfg,conn,cursor,providerEmails):
  for i in range(5):
    if not hashesChanged[i]:
      continue
    errors = []
    provider    = list(providerDirs.keys())[i]
    providerDir = list(providerDirs.items())[i][1]
    publicDir   = list(publicDirs.items())[i][1]
    validator   = Validator(providerDir,cfg,conn,cursor)
    allFiles    = [file for file in glob.glob(f"{providerDir}/**/*",recursive = True) if not os.path.isdir(file)]
    # Check each file
    for file in allFiles:
      extension = os.path.splitext(file)[1].lower()
      # Check snx
      if extension == "snx":
        try:
          validator.validateSnx(file)
          fileHandler.moveSnxFileToPublic(file)
        except ValidationError as err:
          errors.append(err)
      # Check pos
      elif extension == "pos":
        try:
          validator.validatePos(file)
          fileHandler.movePosFileToBucket(file)
        except ValidationError as err:
          errors.append(err)
      elif extension == "vel":
        pass
      # Unknown file
      else:
        errors.append(f"File '{os.path.basename(file)}' with path 'file' is neither a snx or pbo file!")
    # if there were any errors email them
    if len(errors) != 0:
      fileHandler.sendEmail(
        f"Error validating some {provider} files. Attention is required!",
        "There were some errors while validating your files: \n\n" + "\n".join(errors) + "\n\n Please re-upload the problematic files or email us back for more information.",
        providerEmails[provider]
      )
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logger = Logs(f"{cfg.getLogsConfig('LOGS_DIR')}/{cfg.getLogsConfig('VALIDATE_LOGS')}",cfg.getLogsConfig("MAX_LOGS"))
  # In and Out folders
  providerDirs = {
    "INGV" : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_ingv/uploads",
    "ROB"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_rob/uploads",
    "SGO"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_ltk/uploads",
    "UGA"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_uga-cnrs/uploads",
    "WUT"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_wut/uploads"
  }
  publicDir = {
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
    cfg.getEPOSDBConfig("PASSWORD"),
    logger
  )
  pgConnection.connect()
  # Get list of the hashes changed of each provider
  fileHandler = FileHandler(
    con,
    cfg.getAppConfig("PROVIDERS_DIR"),
    cfg.getEmailConfig("FROM_EMAIL"),
    cfg.getEmailConfig("TO_EMAIL"),
    cfg.getEmailConfig("FROM_EMAIL_PWD_FILE")
  )
  hashesChanged = fileHandler.getListOfFilesChanged()
  # Move the files to the corresponding public folder or email the providers if an error occurred
  handleProviders(fileHandler,providerDirs,publicDir,hashesChanged,cfg,providerEmails)
  
if __name__ == '__main__':
  main()