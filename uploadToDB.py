import sqlite3
from src.utils.config import *
from src.fileHandler  import *
from src.validate     import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

#Functions
def handleProviders(fileHandler,providerDirs,publicDirs,hashesChanged):
  for i in range(5):
    if hashesChanged[i]:
      provider    = list(providerDirs.keys())[i]
      providerDir = list(providerDirs.items())[i][1]
      publicDir   = list(publicDirs.items())[i][1]
      validator   = Validator(providerDir)
      validate,validationError = validator.validateProviderDir()
      if validate:
        fileHandler.moveToPublic(providerDir,publicDir)
      else:
        fileHandler.sendEmail(
          f"Validation failure (requires attention in {provider}) | {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
          f"{validationError}"
        )
        
# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # In and Out folders
  providerDirs = {
    "INGV" : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_ingv/uploads",
    "ROB"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_rob/uploads",
    "SGO"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_sgo/uploads",
    "UGA"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_uga/uploads",
    "WUT"  : f"{cfg.getAppConfig('PROVIDERS_DIR')}/providers_wut/uploads"
  }
  publicDir = {
    "INGV" : f"{cfg.getAppConfig('PUBLIC_DIR')}/INGV",
    "ROB"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/ROB-EUREF",
    "SGO"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/SGO-EPND",
    "UGA"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/UGA-CNRS",
    "WUT"  : f"{cfg.getAppConfig('PUBLIC_DIR')}/WUT-EUREF"
  }
  # Get a connection to the local database
  con = sqlite3.connect(cfg.getAppConfig("DATABASE_FILE"))
  # Get list of the hashes changed of each provider
  fileHandler   = FileHandler(con,cfg.getAppConfig("PROVIDERS_DIR"),cfg.getEmailConfig("FROM_EMAIL"),cfg.getEmailConfig("TO_EMAIL"),cfg.getEmailConfig("FROM_EMAIL_PWD_FILE"))
  hashesChanged = fileHandler.getListOfFilesChanged()
  # Move the files to the corresponding public folder or email the providers if an error occurred
  handleProviders(fileHandler,providerDirs,publicDir,hashesChanged)
  
if __name__ == '__main__':
  main()