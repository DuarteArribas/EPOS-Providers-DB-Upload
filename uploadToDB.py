from src.utils.passwordHandler import *
from src.dbConnection          import *
from src.utils.config          import *
from src.fileHandler           import *
from src.validate              import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Functions
def uploadAllTS(self,bucketDir):
  for providerBucketDir in bucketDir:
    try:
      pass
    except UploadError:
      pass
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logger = Logs(f"{os.path.join(cfg.getLogsConfig('LOGS_DIR'),cfg.getLogsConfig('UPLOADING_LOGS'))}",cfg.getLogsConfig("MAX_LOGS"))
  # Bucket and public folders
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
    fromEmailPassword = PasswordHandler.getPwdFromFolder(cfg.getEmailConfig("PWD_PATH"),sum(ord(c) for c in cfg.getEPOSDBConfig("TOKEN")) - 34)
  )
  # Upload all ts files
  uploadAllTS()
  
if __name__ == '__main__':
  main()