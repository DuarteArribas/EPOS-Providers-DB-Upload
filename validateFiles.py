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
    errors                    = []
    previousTSMetadataValues  = [None,None,None,None,None,None,None]
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
    if len(validatedTSFiles) > 0 and len(validatedVelFiles) > 0:
      fileHandler.sendEmail(
        f"File validation for {provider} was successful!",
        f"{len(validatedTSFiles)} new {'files were' if len(validatedTSFiles) > 1 else 'file was'} validated and {len(validatedVelFiles)} new {'files were' if len(validatedVelFiles) > 1 else 'file was'} validated for {provider}.",
        providerEmails[provider]
      )
    elif len(validatedTSFiles) > 0:
      fileHandler.sendEmail(
        f"File validation for {provider} was successful!",
        f"{len(validatedTSFiles)} new {'files were' if len(validatedTSFiles) > 1 else 'file was'} validated for {provider}.",
        providerEmails[provider]
      )
    elif len(validatedVelFiles) > 0:
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
  logsFile = os.path.join(cfg.getLogsConfig('LOGS_DIR'),cfg.getLogsConfig('VALIDATE_LOGS'))
  logger   = Logs(
    logsFile,
    cfg.getLogsConfig("MAX_LOGS")
  )
  # Upload, bucket and public directories
  providersDir = {
    "INGV" : os.path.join(cfg.getAppConfig('PROVIDERS_DIR'),cfg.getProvidersConfig('INGV_UPLOAD_DIR')),
    "ROB"  : os.path.join(cfg.getAppConfig('PROVIDERS_DIR'),cfg.getProvidersConfig('ROB_UPLOAD_DIR')),
    "SGO"  : os.path.join(cfg.getAppConfig('PROVIDERS_DIR'),cfg.getProvidersConfig('SGO_UPLOAD_DIR')),
    "UGA"  : os.path.join(cfg.getAppConfig('PROVIDERS_DIR'),cfg.getProvidersConfig('UGA_UPLOAD_DIR')),
    "WUT"  : os.path.join(cfg.getAppConfig('PROVIDERS_DIR'),cfg.getProvidersConfig('WUT_UPLOAD_DIR'))
  }
  bucketDirs = {
    "INGV" : os.path.join(cfg.getAppConfig('BUCKET_DIR'),cfg.getProvidersConfig('INGV_BUCKET_DIR')),
    "ROB"  : os.path.join(cfg.getAppConfig('BUCKET_DIR'),cfg.getProvidersConfig('ROB_BUCKET_DIR')),
    "SGO"  : os.path.join(cfg.getAppConfig('BUCKET_DIR'),cfg.getProvidersConfig('SGO_BUCKET_DIR')),
    "UGA"  : os.path.join(cfg.getAppConfig('BUCKET_DIR'),cfg.getProvidersConfig('UGA_BUCKET_DIR')),
    "WUT"  : os.path.join(cfg.getAppConfig('BUCKET_DIR'),cfg.getProvidersConfig('WUT_BUCKET_DIR'))
  }
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
  # Get a connection to the local database (used to store the hashes of the files, so we can check if they changed)
  con = sqlite3.connect(cfg.getAppConfig("LOCAL_DATABASE_FILE"))
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
  
if __name__ == '__main__':
  main()