from src.utils.passwordHandler import *
from src.dbConnection          import *
from src.utils.config          import *
from src.fileHandler           import *
from src.validate              import *

# Global variables
CONFIG_FILE = "config/appconf.cfg"

# Functions
def uploadAllTS(self,bucketDir):
  dataType = self.cfg.getUploadConfig("TS_DATATYPE")
  for provBucketDir in os.listdir(bucketDir):
    for version in os.listdir(os.path.join(bucketDir,provBucketDir)):
      currDir = os.path.join(os.path.join(bucketDir,provBucketDir),version)
      allTSFiles = self.getListOfTSFiles(currDir)
      if len(allTSFiles) == 0:
        return
      self.cursor.execute("START TRANSACTION;")
      self.handlePreviousSolution(provBucketDir,dataType)
      self.cursor.execute("COMMIT TRANSACTION;")
      solutionParameters = self.getSolutionParameters(os.path.join(currDir,allTSFiles[0]))
      self.cursor.execute("START TRANSACTION;")
      self.handleReferenceFrame(solutionParameters["reference_frame"],"2021-11-11") # TODO: add correct epoch
      self.cursor.execute("COMMIT TRANSACTION;")
      self.cursor.execute("START TRANSACTION;")
      self.uploadSolution(dataType,solutionParameters)
      self.cursor.execute("COMMIT TRANSACTION;")
      currentSolutionID = self.checkSolutionAlreadyInDB(provBucketDir,dataType)[0]
      for file in allTSFiles:
        self.cursor.execute("START TRANSACTION;")
        timeseriesFileID = self.uploadTimeseriesFile(os.path.join(currDir,file),1.1) # TODO: add correct version
        self.cursor.execute("COMMIT TRANSACTION;")
        self.saveEstimatedCoordinatesToFile(os.path.join(currDir,file),currentSolutionID,timeseriesFileID[0])
      self.cursor.execute("START TRANSACTION;")
      self.uploadEstimatedCoordinates()
      self.cursor.execute("COMMIT TRANSACTION;")
      self.eraseEstimatedCoordinatesTmpFile()
      
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