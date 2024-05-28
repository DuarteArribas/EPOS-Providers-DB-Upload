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
def handleProviders(fileHandler,providersDir,publicDirs,bucketDirs,hashesChanged,cfg,conn,cursor,providerEmails):
  for i in range(5):
    # If the hashes of the files of the provider didn't change, skip it
    if not hashesChanged[i]:
      continue
    errors                    = []
    previousTSMetadataValues  = [None,None,None,None,None,None]
    previousVelMetadataValues = [None,None,None,None,None,None]
    validatedTSFiles          = []
    validatedVelFiles         = []
    validatedTSEqualMetadata  = True
    validatedVelEqualMetadata = True
    provider                  = list(providersDir.keys())[i]
    providerDir               = list(providersDir.items())[i][1]
    publicDir                 = list(publicDirs.items())[i][1]
    bucketDir                 = list(bucketDirs.items())[i][1]
    validator                 = Validator(cfg,conn,cursor)
    allFiles                  = [file for file in glob.glob(f"{providerDir}/**/*",recursive = True) if not os.path.isdir(file)]
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
          if not any(value is None for value in previousTSMetadataValues):
            if any(value for value in range(len(validator.tsMetadataValues)) if validator.tsMetadataValues[value] != previousTSMetadataValues[value]):
              fileHandler.sendEmailToSegal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Not all files contain the same metadata parameters--the first file with different parameters is {file}.")
              validatedTSEqualMetadata = False
            else:
              previousTSMetadataValues = validator.tsMetadataValues.copy()
              validatedTSFiles.append((file,validator.version))
          else:
            previousTSMetadataValues = validator.tsMetadataValues.copy()
            validatedTSFiles.append((file,validator.version))
        except ValidationError as err:
          errors.append(str(err))
      # Check vel
      elif extensionWithoutGzip == ".vel":
        try:
          validator.validateVel(file)
          if not any(value is None for value in previousVelMetadataValues):
            if any(value for value in range(len(validator.velMetadataValues)) if validator.velMetadataValues[value] != previousVelMetadataValues[value]):
              fileHandler.sendEmailToSegal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Not all files contain the same metadata parameters--the first file with different parameters is {file}.")
              validatedVelEqualMetadata = False
            else:
              previousVelMetadataValues = validator.velMetadataValues.copy()
              validatedVelFiles.append((file,validator.version))
          else:
            previousVelMetadataValues = validator.velMetadataValues.copy()
            validatedVelFiles.append((file,validator.version))
        except ValidationError as err:
          errors.append(str(err))
      # Unknown file
      else:
        fileHandler.sendEmailToSegal(f"Error (to Segal only) validating some {provider} files. Attention is required!",f"Unknown file type: {file}.")
        break
    # If there are validated files, move them to the bucket and email them if all their metadata is the same
    if validatedTSEqualMetadata:
      for file,version in validatedTSFiles:
        fileHandler.movePboFileToBucket(file,bucketDir,"TS",version)
    if validatedVelEqualMetadata:
      for file,version in validatedVelFiles:
        fileHandler.movePboFileToBucket(file,bucketDir,"Vel",version)
    if len(validatedTSFiles) > 0 and len(validatedVelFiles) > 0 and validatedTSEqualMetadata and validatedVelEqualMetadata:
      fileHandler.sendEmail(
        f"File validation for {provider} was successful!",
        f"{len(validatedTSFiles)} new {'files were' if len(validatedTSFiles) > 1 else 'file was'} validated and {len(validatedVelFiles)} new {'files were' if len(validatedVelFiles) > 1 else 'file was'} validated for {provider}.",
        providerEmails[provider]
      )
    elif len(validatedTSFiles) > 0 and validatedTSEqualMetadata:
      fileHandler.sendEmail(
        f"File validation for {provider} was successful!",
        f"{len(validatedTSFiles)} new {'files were' if len(validatedTSFiles) > 1 else 'file was'} validated for {provider}.",
        providerEmails[provider]
      )
    elif len(validatedVelFiles) > 0 and validatedVelEqualMetadata:
      fileHandler.sendEmail(
        f"File validation for {provider} was successful!",
        f"{len(validatedVelFiles)} new {'files were' if len(validatedVelFiles) > 1 else 'file was'} validated for {provider}.",
        providerEmails[provider]
      )
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
  logs_file = os.path.join(cfg.config.get("LOGS","LOGS_DIR"),cfg.config.get("LOGS","VALIDATE_LOGS"))
  logging.basicConfig(
    filename = logs_file,
    level    = cfg.config.get("LOGS","LOG_LEVEL"),
    format   = '%(asctime)s - %(message)s'
  )
  # Upload, bucket and public directories
  providers_dir = {
    "INGV" : os.path.join(cfg.config.get("PROVIDERS","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","INGV_UPLOAD_DIR")),
    "ROB"  : os.path.join(cfg.config.get("PROVIDERS","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","ROB_UPLOAD_DIR")),
    "SGO"  : os.path.join(cfg.config.get("PROVIDERS","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","SGO_UPLOAD_DIR")),
    "UGA"  : os.path.join(cfg.config.get("PROVIDERS","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","UGA_UPLOAD_DIR")),
    "WUT"  : os.path.join(cfg.config.get("PROVIDERS","PROVIDERS_DIR"),cfg.config.get("PROVIDERS","WUT_UPLOAD_DIR"))
  }
  bucket_dirs = {
    "INGV" : os.path.join(cfg.config.get("PROVIDERS","BUCKET_DIR"),cfg.config.get("PROVIDERS","INGV_BUCKET_DIR")),
    "ROB"  : os.path.join(cfg.config.get("PROVIDERS","BUCKET_DIR"),cfg.config.get("PROVIDERS","ROB_BUCKET_DIR")),
    "SGO"  : os.path.join(cfg.config.get("PROVIDERS","BUCKET_DIR"),cfg.config.get("PROVIDERS","SGO_BUCKET_DIR")),
    "UGA"  : os.path.join(cfg.config.get("PROVIDERS","BUCKET_DIR"),cfg.config.get("PROVIDERS","UGA_BUCKET_DIR")),
    "WUT"  : os.path.join(cfg.config.get("PROVIDERS","BUCKET_DIR"),cfg.config.get("PROVIDERS","WUT_BUCKET_DIR"))
  }
  public_dirs = {
    "INGV" : os.path.join(cfg.config.get("PROVIDERS","PUBLIC_DIR"),cfg.config.get("PROVIDERS","INGV_PUBLIC_DIR")),
    "ROB"  : os.path.join(cfg.config.get("PROVIDERS","PUBLIC_DIR"),cfg.config.get("PROVIDERS","ROB_PUBLIC_DIR")),
    "SGO"  : os.path.join(cfg.config.get("PROVIDERS","PUBLIC_DIR"),cfg.config.get("PROVIDERS","SGO_PUBLIC_DIR")),
    "UGA"  : os.path.join(cfg.config.get("PROVIDERS","PUBLIC_DIR"),cfg.config.get("PROVIDERS","UGA_PUBLIC_DIR")),
    "WUT"  : os.path.join(cfg.config.get("PROVIDERS","PUBLIC_DIR"),cfg.config.get("PROVIDERS","WUT_PUBLIC_DIR"))
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
    cfg.getEPOSDBConfig("IP"),
    cfg.getEPOSDBConfig("PORT"),
    cfg.getEPOSDBConfig("DATABASE_NAME"),
    cfg.getEPOSDBConfig("USERNAME"),
    epos_db_pwd,
    logger
  )
  pg_connection.connect()
  # Get a file handler object
  emailPswd = PasswordHandler.getPwdFromFolder(
    cfg.getEmailConfig("PWD_PATH"),
    sum(ord(c) for c in cfg.getEmailConfig("TOKEN")) - 34
  )
  fileHandler = FileHandler(
    cfg.getAppConfig("PROVIDERS_DIR"),
    cfg.getEmailConfig("FROM_EMAIL"),
    emailPswd,
    con
  )
  # Get list of the hashes changed of each provider
  hashesChanged = fileHandler.getListOfHashesChanged()
  # Move the files to the corresponding public folder or email the providers if an error occurred
  handleProviders(
    fileHandler,
    providersDir,
    publicDirs,
    bucketDirs,
    hashesChanged,
    cfg,
    pgConnection.conn,
    pgConnection.cursor,
    providerEmails
  )
  # Update the directory hashes
  fileHandler.updateHashes()
  
if __name__ == '__main__':
  main()