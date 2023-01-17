import sqlite3
from src.utils.config import *
from src.fileHandler  import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"


OUT_DIR       = "out/public/"

PUBLIC_DIR    = {
  "INGV" : f"{OUT_DIR}/INGV",
  "ROB"  : f"{OUT_DIR}/ROB-EUREF",
  "SGO"  : f"{OUT_DIR}/SGO-EPND",
  "UGA"  : f"{OUT_DIR}/UGA-CNRS",
  "WUT"  : f"{OUT_DIR}/WUT-EUREF"
}
FROM_EMAIL = "duarte.arribas@segal.ubi.pt"
TO_EMAIL   = "duarte.a.arribas@gmail.com"

#Functions




# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get a connection to the local database
  con = sqlite3.connect(cfg.getAppConfig("DATABASE_FILE"))
  # Get list of the hashes changed of each provider
  fd  = FileHandler(con,cfg.getAppConfig("PROVIDERS_DIR"))
  hashesChanged = fd.getListOfFilesChanged()
  
  
  
  
  print(hashesChanged)
  
  
  
  
  ## Check which hashes have changed
  #
  ## Validate dirs whose hashes have changed. If valid move them.
  #for provider,providerDir in PROVIDER_DIR.items():
  #  if provider == "INGV" and hashesChanged[0]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["INGV"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "ROB" and hashesChanged[1]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["ROB"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "SGO" and hashesChanged[2]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["SGO"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "UGA" and hashesChanged[3]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["UGA"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  #  if provider == "WUT" and hashesChanged[4]:
  #    validate,validationError = validateProviderDir(providerDir)
  #    if validate:
  #      moveToPublic(providerDir,PUBLIC_DIR["WUT"])
  #    else:
  #      sendEmail(
  #        f"Validation failure (requires attention in {provider}) | {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}",
  #        f"{validationError}"
  #      )
  #      pass
  
if __name__ == '__main__':
  main()