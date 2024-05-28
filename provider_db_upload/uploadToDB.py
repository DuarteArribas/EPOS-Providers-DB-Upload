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
  databaseUpload = DatabaseUpload(
    pgConnection.conn,
    pgConnection.cursor,
    logger,
    cfg,
    cfg.getAppConfig("TMP_DIR"),
    fileHandler
  )
  for count,providerBucketDir in enumerate(os.listdir(bucketDir)):
    provider     = providerBucketDir.split("-")[0]
    publicDir    = publicDirs[providerBucketDir.split("-")[0]]
    if handle_new_solution(provider,fileHandler,databaseUpload,bucketDir,providerBucketDir,publicDir):
      return
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
  databaseUpload = DatabaseUpload(
    pgConnection.conn,
    pgConnection.cursor,
    logger,
    cfg,
    cfg.getAppConfig("TMP_DIR"),
    fileHandler
  )
  for count,providerBucketDir in enumerate(os.listdir(bucketDir)):
    provider  = providerBucketDir.split("-")[0]
    publicDir = publicDirs[providerBucketDir.split("-")[0]]
    if handle_new_solution(provider,fileHandler,databaseUpload,bucketDir,providerBucketDir,publicDir):
      return
    try:
      databaseUpload.uploadAllProviderVel(os.path.join(bucketDir,providerBucketDir),publicDir)
    except UploadError as err:
      fileHandler.sendEmail(
        f"Error uploading {provider} Vel files. Attention is required!",
        "There were some errors while uploading your files: \n\n" + str(err) + "\n\n\n Please email us back for more information.",
        providerEmails[provider]
      )

def handle_new_solution(provider,fileHandler,databaseUpload,bucketDir,providerBucketDir,publicDir):
  old_solution,new_solution = databaseUpload.check_solution_folder_exists(os.path.join(bucketDir,providerBucketDir),publicDir)
  if not new_solution:
    fileHandler.sendEmailToSegal(f"Warning (to Segal only). Provider {provider} uploaded a new solution!",f"The previous solution for {provider} was {old_solution} and the new one is {new_solution}. Please check that the new solution is correct and create the respective folder in the public directory.")
    return True
  return False
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logsFile = os.path.join(cfg.getLogsConfig('LOGS_DIR'),cfg.getLogsConfig('UPLOADING_LOGS'))
  logger   = Logs(
    logsFile,
    cfg.getLogsConfig("MAX_LOGS")
  )
  # Public directories
  publicDirs = {
    "INGV" : os.path.join(cfg.getAppConfig('PUBLIC_DIR'),cfg.getProvidersConfig('INGV_PUBLIC_DIR')),
    "ROB"  : os.path.join(cfg.getAppConfig('PUBLIC_DIR'),cfg.getProvidersConfig('ROB_PUBLIC_DIR')),
    "SGO"  : os.path.join(cfg.getAppConfig('PUBLIC_DIR'),cfg.getProvidersConfig('SGO_PUBLIC_DIR')),
    "UGA"  : os.path.join(cfg.getAppConfig('PUBLIC_DIR'),cfg.getProvidersConfig('UGA_PUBLIC_DIR')),
    "WUT"  : os.path.join(cfg.getAppConfig('PUBLIC_DIR'),cfg.getProvidersConfig('WUT_PUBLIC_DIR'))
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
  eposDBPswd = PasswordHandler.getPwdFromFolder(
    cfg.getEPOSDBConfig("PWD_PATH"),
    sum(ord(c) for c in cfg.getEPOSDBConfig("TOKEN")) - 34
  )
  pgConnection = DBConnection(
    cfg.getEPOSDBConfig("IP"),
    cfg.getEPOSDBConfig("PORT"),
    cfg.getEPOSDBConfig("DATABASE_NAME"),
    cfg.getEPOSDBConfig("USERNAME"),
    eposDBPswd,
    logger
  )
  pgConnection.connect()
  # Get a file handler object
  emailPswd = PasswordHandler.getPwdFromFolder(
    cfg.getEmailConfig("PWD_PATH"),
    sum(ord(c) for c in cfg.getEmailConfig("TOKEN")) - 34
  )
  fileHandler = FileHandler(
    cfg.getAppConfig("PROVIDERS_DIR"),
    cfg.getEmailConfig("FROM_EMAIL"),
    emailPswd,
    "dummy"
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