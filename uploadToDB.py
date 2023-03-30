from src.utils.passwordHandler import *
from src.dbConnection          import *
from src.utils.config          import *
from src.fileHandler           import *
from src.validate              import *
from src.uploadError           import *
from src.databaseUpload        import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Functions
def uploadAllTS(bucketDir,cfg,logger,publicDirs,providerEmails,pgConnection,fileHandler):
  """Upload all TS files from all the providers to the database.
  
  Parameters
  ----------
  bucketDir      : str
    The bucket directory where the TS files are stored.
  cfg            : Config
    The configuration object.
  logger         : Logs
    The logger object.
  publicDirs     : dict
    The public directory of each provider.
  providerEmails : dict
    The email of each provider.
  pgConnection   : PgConnection
    The database connection object.
  fileHandler    : FileHandler
    The file handler object.
  """
  databaseUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,cfg.getAppConfig("TMP_DIR"),fileHandler)
  for count,providerBucketDir in enumerate(os.listdir(bucketDir)):
    provider  = list(publicDirs.keys())[count]
    publicDir = list(publicDirs.items())[count][1]
    try:
      databaseUpload.uploadAllProviderTS(os.path.join(bucketDir,providerBucketDir),publicDir)
    except UploadError as err:
      fileHandler.sendEmail(
        f"Error uploading {provider} TS files. Attention is required!",
        "There were some errors while uploading your files: \n\n" + str(err) + "\n\n\n Please email us back for more information.",
        providerEmails[provider]
      )

def uploadAllVel(bucketDir,cfg,logger,publicDirs,providerEmails,pgConnection,fileHandler):
  """Upload all Vel files from all the providers to the database.
  
  Parameters
  ----------
  bucketDir      : str
    The bucket directory where the Vel files are stored.
  cfg            : Config
    The configuration object.
  logger         : Logs
    The logger object.
  publicDirs     : dict
    The public directory of each provider.
  providerEmails : dict
    The email of each provider.
  pgConnection   : PgConnection
    The database connection object.
  fileHandler    : FileHandler
    The file handler object.
  """
  databaseUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,cfg.getAppConfig("TMP_DIR"),fileHandler)
  for count,providerBucketDir in enumerate(os.listdir(bucketDir)):
    provider  = list(publicDirs.keys())[count]
    publicDir = list(publicDirs.items())[count][1]
    try:
      databaseUpload.uploadAllProviderVel(os.path.join(bucketDir,providerBucketDir),publicDir)
    except UploadError as err:
      fileHandler.sendEmail(
        f"Error uploading {provider} Vel files. Attention is required!",
        "There were some errors while uploading your files: \n\n" + str(err) + "\n\n\n Please email us back for more information.",
        providerEmails[provider]
      )
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logger = Logs(f"{os.path.join(cfg.getLogsConfig('LOGS_DIR'),cfg.getLogsConfig('UPLOADING_LOGS'))}",cfg.getLogsConfig("MAX_LOGS"))
  # Public directories
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
    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
    fromEmail         = cfg.getEmailConfig("FROM_EMAIL"),
    fromEmailPassword = PasswordHandler.getPwdFromFolder(cfg.getEmailConfig("PWD_PATH"),sum(ord(c) for c in cfg.getEPOSDBConfig("TOKEN")) - 34)
  )
  # Upload all ts files
  uploadAllTS(
    cfg.getAppConfig('BUCKET_DIR'),
    cfg,
    logger,
    publicDirs,
    providerEmails,
    pgConnection,
    fileHandler,
  )
  # Upload all vel files
  uploadAllVel(
    cfg.getAppConfig('BUCKET_DIR'),
    cfg,
    logger,
    publicDirs,
    providerEmails,
    pgConnection,
    fileHandler,
  )
  
if __name__ == '__main__':
  main()