import os
import logging
from utils.config              import *
from uploader.uploadError      import *
from utils.passwordHandler     import *
from fileHandler.fileHandler   import *
from uploader.databaseUpload   import *
from dbConnection.dbConnection import *

# Global variables
CONFIG_FILE = "config/appconf.ini"

# Functions
def upload_all_ts(bucket_dir : str,cfg : Config,public_dirs : dict,provider_emails : dict,pg_connection,file_handler : FileHandler):
  """Upload all TS files from all the providers to the database.
  
  Parameters
  ----------
  bucket_dir      : str
    The bucket directory where the TS files are stored.
  cfg             : Config
    The configuration object.
  public_dirs     : dict
    The public directory of each provider.
  provider_Emails : dict
    The email of each provider.
  pg_connection   : ??
    The database connection object.
  file_handler    : FileHandler
    The file handler object.
  """
  database_upload = DatabaseUpload(
    pg_connection.conn,
    pg_connection.cursor,
    cfg,
    cfg.config.get("APP","TMP_DIR"),
    file_handler
  )
  for count,provider_bucket_dir in enumerate(os.listdir(bucket_dir)):
    provider   = provider_bucket_dir.split("-")[0]
    public_dir = public_dirs[provider_bucket_dir.split("-")[0]]
    if _handle_new_solution(provider,file_handler,database_upload,bucket_dir,provider_bucket_dir,public_dir):
      continue
    try:
      database_upload.upload_all_provider_TS(os.path.join(bucket_dir,provider_bucket_dir),public_dir)
    except UploadError as err:
      file_handler.send_email(
        f"Error uploading {provider} TS files. Attention is required!",
        "There were some errors while uploading your files: \n\n" + str(err) + "\n\n\n Please email us back for more information.",
        provider_emails[provider]
      )

def upload_all_vel(bucketDir,cfg,publicDirs,providerEmails,pg_connection,fileHandler):
  """Upload all Vel files from all the providers to the database.
  
  Parameters
  ----------
  bucketDir      : str
    The bucket directory where the Vel files are stored.
  cfg            : Config
    The configuration object.
  publicDirs     : dict
    The public directory of each provider.
  providerEmails : dict
    The email of each provider.
  pg_connection   : pg_connection
    The database connection object.
  fileHandler    : FileHandler
    The file handler object.
  """
  databaseUpload = DatabaseUpload(
    pg_connection.conn,
    pg_connection.cursor,
    cfg,
    cfg.getAppConfig("TMP_DIR"),
    fileHandler
  )
  for count,providerBucketDir in enumerate(os.listdir(bucketDir)):
    provider  = providerBucketDir.split("-")[0]
    publicDir = publicDirs[providerBucketDir.split("-")[0]]
    if _handle_new_solution(provider,fileHandler,databaseUpload,bucketDir,providerBucketDir,publicDir):
      continue
    try:
      databaseUpload.uploadAllProviderVel(os.path.join(bucketDir,providerBucketDir),publicDir)
    except UploadError as err:
      fileHandler.sendEmail(
        f"Error uploading {provider} Vel files. Attention is required!",
        "There were some errors while uploading your files: \n\n" + str(err) + "\n\n\n Please email us back for more information.",
        providerEmails[provider]
      )

def _handle_new_solution(provider : str,file_handler : FileHandler,database_upload : DatabaseUpload,bucket_dir : str,provider_bucket_dir : str,public_dir : str) -> bool:
  # Check if a new solution was uploaded
  old_solution,new_solution = database_upload.check_solution_folder_exists(os.path.join(bucket_dir,provider_bucket_dir),public_dir)
  old_solution_text = "didn't exist" if not old_solution else f"was {old_solution}"
  if not new_solution:
    file_handler.send_email_to_segal(f"Warning (to Segal only). Provider {provider} uploaded a new solution!",f"The previous solution for {provider} {old_solution} and the new one is {new_solution}. Please check that the new solution is correct and create the respective folder in the public directory, so that the files can be uploaded.")
    return True
  return False
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logs_file = os.path.join(cfg.config.get("LOGS","LOGS_DIR"),cfg.config.get("LOGS","UPLOADING_LOGS"))
  logging.basicConfig(
    filename = logs_file,
    level    = cfg.config.get("LOGS","LOG_LEVEL"),
    format   = '%(asctime)s - %(message)s'
  )
  # Provider and public directories
  providers_dir = {
    "INGV" : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","INGV_UPLOAD_DIR")),
    "ROB"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","ROB_UPLOAD_DIR")),
    "SGO"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","SGO_UPLOAD_DIR")),
    "UGA"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","UGA_UPLOAD_DIR")),
    "WUT"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","WUT_UPLOAD_DIR"))
  }
  public_dirs = {
    "INGV" : os.path.join(cfg.config.get("APP","PUBLIC_DIR"),cfg.config.get("PROVIDERS","INGV_PUBLIC_DIR")),
    "ROB"  : os.path.join(cfg.config.get("APP","PUBLIC_DIR"),cfg.config.get("PROVIDERS","ROB_PUBLIC_DIR")),
    "SGO"  : os.path.join(cfg.config.get("APP","PUBLIC_DIR"),cfg.config.get("PROVIDERS","SGO_PUBLIC_DIR")),
    "UGA"  : os.path.join(cfg.config.get("APP","PUBLIC_DIR"),cfg.config.get("PROVIDERS","UGA_PUBLIC_DIR")),
    "WUT"  : os.path.join(cfg.config.get("APP","PUBLIC_DIR"),cfg.config.get("PROVIDERS","WUT_PUBLIC_DIR"))
  }
  # Provider emails
  provider_emails = {
    "INGV" : f"{cfg.config.get("EMAIL","INGV_EMAIL")}",
    "ROB"  : f"{cfg.config.get("EMAIL","ROB_EMAIL")}",
    "SGO"  : f"{cfg.config.get("EMAIL","SGO_EMAIL")}",
    "UGA"  : f"{cfg.config.get("EMAIL","UDA_EMAIL")}",
    "WUT"  : f"{cfg.config.get("EMAIL","WUT_EMAIL")}"
  }
  # Get a connection to the EPOS database
  epos_db_pwd = PasswordHandler.get_pwd_from_folder(
    cfg.config.get("EPOSDB","PWD_PATH"),
    sum(ord(c) for c in cfg.config.get("EPOSDB","TOKEN")) - 34
  )
  pg_connection = DBConnection(
    cfg.config.get("EPOSDB","IP"),
    cfg.config.get("EPOSDB","PORT"),
    cfg.config.get("EPOSDB","DATABASE_NAME"),
    cfg.config.get("EPOSDB","USERNAME"),
    epos_db_pwd
  )
  pg_connection.connect()
  # Get a file handler object
  email_pwd = PasswordHandler.get_pwd_from_folder(
    cfg.config.get("EMAIL","PWD_PATH"),
    sum(ord(c) for c in cfg.config.get("EMAIL","TOKEN")) - 34
  )
  file_handler = FileHandler(
    providers_dir,
    cfg.config.get("EMAIL","FROM_EMAIL"),
    email_pwd,
    "dummy"
  )
  # Upload all ts files
  upload_all_ts(
    cfg.config.get("APP","BUCKET_DIR"),
    cfg,
    public_dirs,
    provider_emails,
    pg_connection,
    provider_emails
  )
  # Upload all vel files
  #upload_all_vel(
  #  cfg.config.get("APP","BUCKET_DIR"),
  #  cfg,
  #  public_dirs,
  #  provider_emails,
  #  pg_connection,
  #  provider_emails
  #)
  
if __name__ == '__main__':
  main()