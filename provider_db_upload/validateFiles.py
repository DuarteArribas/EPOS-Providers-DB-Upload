import os
import glob
import sqlite3
import logging
from utils.config              import *
from validator.validate        import *
from utils.passwordHandler     import *
from fileHandler.fileHandler   import *
from dbConnection.dbConnection import *

# Global variables
CONFIG_FILE = "config/appconf.ini"

# Functions
def handle_providers(file_handler,providers_dir,public_dirs,bucket_dirs,hashes_changed,cfg,conn,cursor,provider_emails):
  print(ROUTINE_MSG["VALIDATING_FILES"])
  for i in range(5):
    # If the hashes of the files of the provider didn't change, skip it
    if not hashes_changed[i]:
      continue
    errors                       = []
    previous_TS_metadata_values  = [None,None,None,None,None,None]
    previous_VEL_metadata_values = [None,None,None,None,None,None]
    validated_TS_files           = []
    validated_VEL_files          = []
    validated_TS_equal_metadata  = True
    validated_VEL_equal_metadata = True
    provider                     = list(providers_dir.keys())[i]
    provider_dir                 = list(providers_dir.items())[i][1]
    public_dir                   = list(public_dirs.items())[i][1]
    bucket_dir                   = list(bucket_dirs.items())[i][1]
    validator                    = Validator(cfg,conn,cursor)
    all_files                    = [file for file in glob.glob(f"{provider_dir}/**/*",recursive = True) if not os.path.isdir(file)]
    # Check each file
    print(ROUTINE_MSG["VALIDATING_PROVIDER"].format(file_length = len(all_files),provider = provider))
    for file in all_files:
      extension_with_gzip    = os.path.splitext(os.path.splitext(file)[0])[1].lower()
      extension_without_gzip = os.path.splitext(file)[1].lower()
      # Check snx
      if extension_with_gzip == ".snx":
        print(ROUTINE_MSG["VALIDATING_SNX"].format(file = os.path.basename(file)))
        try:
          validator.validate_snx(file)
          file_handler.move_snx_file_to_public(file,public_dir)
        except ValidationError as err:
          errors.append(str(err))
      # Check pos
      elif extension_without_gzip == ".pos":
        print(ROUTINE_MSG["VALIDATING_TS"].format(file = os.path.basename(file)))
        try:
          validator.validate_pos(file)
          if not any(value is None for value in previous_TS_metadata_values):
            if any(value for value in range(len(validator.ts_metadata_values)) if validator.ts_metadata_values[value] != previous_TS_metadata_values[value]):
              file_handler.send_email_to_segal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Not all files contain the same metadata parameters--the first file with different parameters is {file}.")
              validated_TS_equal_metadata = False
            else:
              previous_TS_metadata_values = validator.ts_metadata_values.copy()
              validated_TS_files.append((file,validator.version))
          else:
            previous_TS_metadata_values = validator.ts_metadata_values.copy()
            validated_TS_files.append((file,validator.version))
        except ValidationError as err:
          errors.append(str(err))
      # Check vel
      elif extension_without_gzip == ".vel":
        print(ROUTINE_MSG["VALIDATING_VEL"].format(file = os.path.basename(file)))
        try:
          validator.validateVel(file)
          if not any(value is None for value in previous_VEL_metadata_values):
            if any(value for value in range(len(validator.vel_metadata_values)) if validator.vel_metadata_values[value] != previous_VEL_metadata_values[value]):
              file_handler.send_email_to_segal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Not all files contain the same metadata parameters--the first file with different parameters is {file}.")
              validated_VEL_equal_metadata = False
            else:
              previous_VEL_metadata_values = validator.vel_metadata_values.copy()
              validated_VEL_files.append((file,validator.version))
          else:
            previous_VEL_metadata_values = validator.vel_metadata_values.copy()
            validated_VEL_files.append((file,validator.version))
        except ValidationError as err:
          errors.append(str(err))
      # Unknown file
      else:
        file_handler.send_email_to_segal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Unknown file type: {file}.")
        break
    # If there are validated files, move them to the bucket and email them if all their metadata is the same
    if validated_TS_equal_metadata:
      for file,version in validated_TS_files:
        file_handler.move_pbo_file_to_bucket(file,bucket_dir,"TS",version)
    if validated_VEL_equal_metadata:
      for file,version in validated_VEL_files:
        file_handler.move_pbo_file_to_bucket(file,bucket_dir,"Vel",version)
    if len(validated_TS_files) > 0 and len(validated_VEL_files) > 0 and validated_TS_equal_metadata and validated_VEL_equal_metadata:
      file_handler.send_email(
        f"File validation for {provider} was successful!",
        f"{len(validated_TS_files)} new {'files were' if len(validated_TS_files) > 1 else 'file was'} validated and {len(validated_VEL_files)} new {'files were' if len(validated_VEL_files) > 1 else 'file was'} validated for {provider}.",
        provider_emails[provider]
      )
    elif len(validated_TS_files) > 0 and validated_TS_equal_metadata:
      file_handler.send_email(
        f"File validation for {provider} was successful!",
        f"{len(validated_TS_files)} new {'files were' if len(validated_TS_files) > 1 else 'file was'} validated for {provider}.",
        provider_emails[provider]
      )
    elif len(validated_VEL_files) > 0 and validated_VEL_equal_metadata:
      file_handler.send_email(
        f"File validation for {provider} was successful!",
        f"{len(validated_VEL_files)} new {'files were' if len(validated_VEL_files) > 1 else 'file was'} validated for {provider}.",
        provider_emails[provider]
      )
    # If there were any errors email them
    if len(errors) != 0:
      errors = [f"Error {count} - {error}" for count,error in enumerate(errors)]
      file_handler.send_email(
        f"Error validating some {provider} files. Attention is required!",
        "There were some errors while validating your files: \n\n" + "\n".join(errors) + "\n\n\n Please re-upload the problematic files or email us back for more information.",
        provider_emails[provider]
      )
      
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Logger
  logs_file = os.path.join(cfg.config.get("LOGS","LOGS_DIR"),cfg.config.get("LOGS","VALIDATE_LOGS"))
  logging.basicConfig(
    filename = logs_file,
    level    = cfg.config.get("LOGS","LOG_LEVEL"),
    format   = '%(asctime)s - %(message)s'
  )
  # Upload, bucket and public directories
  providers_dir = {
    "INGV" : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","INGV_UPLOAD_DIR")),
    "ROB"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","ROB_UPLOAD_DIR")),
    "SGO"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","SGO_UPLOAD_DIR")),
    "UGA"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","UGA_UPLOAD_DIR")),
    "WUT"  : os.path.join(cfg.config.get("APP","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","WUT_UPLOAD_DIR"))
  }
  bucket_dirs = {
    "INGV" : os.path.join(cfg.config.get("APP","BUCKET_DIR"),cfg.config.get("PROVIDERS","INGV_BUCKET_DIR")),
    "ROB"  : os.path.join(cfg.config.get("APP","BUCKET_DIR"),cfg.config.get("PROVIDERS","ROB_BUCKET_DIR")),
    "SGO"  : os.path.join(cfg.config.get("APP","BUCKET_DIR"),cfg.config.get("PROVIDERS","SGO_BUCKET_DIR")),
    "UGA"  : os.path.join(cfg.config.get("APP","BUCKET_DIR"),cfg.config.get("PROVIDERS","UGA_BUCKET_DIR")),
    "WUT"  : os.path.join(cfg.config.get("APP","BUCKET_DIR"),cfg.config.get("PROVIDERS","WUT_BUCKET_DIR"))
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
  # Get a connection to the local database (used to store the hashes of the files, so we can check if they changed)
  con = sqlite3.connect(cfg.config.get("APP","LOCAL_DATABASE_FILE"))
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
    con
  )
  # Get list of the hashes changed of each provider
  hashes_changed = file_handler.get_list_of_hashed_changed()
  # Move the files to the corresponding public folder or email the providers if an error occurred
  handle_providers(
    file_handler,
    providers_dir,
    public_dirs,
    bucket_dirs,
    hashes_changed,
    cfg,
    pg_connection.conn,
    pg_connection.cursor,
    provider_emails
  )
  # Update the directory hashes
  file_handler.update_hashes()
  
if __name__ == '__main__':
  main()