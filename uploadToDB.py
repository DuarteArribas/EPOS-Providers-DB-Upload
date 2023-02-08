import sqlite3
from src.databaseUpload import *
from src.utils.config   import *
from src.dbConnection   import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Main function
def main():
  # Read config file
  cfg = Config(CONFIG_FILE)
  # Get logger object
  logger = Logs(f"{cfg.getLogsConfig('LOGS_DIR')}/{cfg.getLogsConfig('UPLOADING_LOGS')}",int(cfg.getLogsConfig("MAX_LOGS")))
  # Initial log
  logger.writeNewRunLog("Uploading files to the database")
  # Get a connection to the EPOS database
  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123",logger)
  pgConnection.connect()
  # Upload TS
  tsUpload = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg.getAppConfig("TMP_DIR"))
  tsUpload.uploadAllTS(cfg.getAppConfig('PUBLIC_DIR'))
  
if __name__ == '__main__':
  main()