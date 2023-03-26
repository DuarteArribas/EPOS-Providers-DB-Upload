from src.utils.passwordHandler import *
from src.dbConnection          import *
from src.utils.config          import *
from src.fileHandler           import *
from src.validate              import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"
      
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
  
if __name__ == '__main__':
  main()