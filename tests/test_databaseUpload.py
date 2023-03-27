import unittest
from src.utils.logs     import *
from src.utils.config   import *
from src.dbConnection   import *
from src.databaseUpload import *
from src.uploadError    import *

class TestDatabaseUpload(unittest.TestCase):
   def test_get_TS(self):
     logger = Logs("logs/logsTest.log",10000)
     pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
     pgConnection.connect()
     tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
     self.assertEqual(tsUpload.getListOfTSFiles("inOutTest/bucket/INGV/1"),["HBLT00UKN.pos","WARN00DEU.pos"])
  
  #def test_checkSolutionAlreadyThere(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  self.assertEqual(tsUpload.checkSolutionAlreadyInDB("INGV","timeseries"),[29,30,31])
  #  print(tsUpload.checkSolutionAlreadyInDB("INGV","timeseries"))
  
  #def test_erasePreviousSolutionFromDB(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._erasePreviousSolutionFromDB("INGV","timeseries")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  #def test_getTimeseriesFilesID(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  self.assertEqual(tsUpload._getTimeseriesFilesID(32),[16])

  #def test_erasePreviousTimeseriesFilesFromDB(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._erasePreviousTimeseriesFilesFromDB(17)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")

  #def test_handlePreviousSolution(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload.handlePreviousSolution("INGV","timeseries","timeseries","velocities")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  #def test_getSolutionParameters(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  print(tsUpload.getSolutionParameters("inOutTest/bucket/INGV/1/WARN00DEU.pos"))
  
  #def test_uploadSolution(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  solutionParameters = {'reference_frame': 'IGb14', 'ac_acronym': 'INGV', 'software': 'CATREF', 'processing_parameters_url': 'https://youtube.com', 'doi': '10.24414/ROB-EUREF-C2220', 'release_version': '2220.0', 'sampling_period': 'daily', 'creation_date': '2022-10-13 00:00:00'}
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload.uploadSolution("timeseries",solutionParameters)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  #def test_uploadSolution2(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  solutionParameters = {'ac_acronym': 'INGV', 'software': 'CATREF', 'processing_parameters_url': 'https://youtube.com', 'doi': '10.24414/ROB-EUREF-C2220', 'release_version': '2220.0', 'sampling_period': 'daily', 'creation_date': '2022-10-13 00:00:00'}
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  self.assertRaises(UploadError,tsUpload.uploadSolution,"timeseries",solutionParameters)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  # def test_getFormatVersion(self):
  #   logger = Logs("logs/logsTest.log",10000)
  #   pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #   pgConnection.connect()
  #   cfg = Config("config/appconf.cfg")
  #   tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #   print(tsUpload.getPosFormatVersion("inOutTest/bucket/INGV/1/WARN00DEU.pos"))
  
  #def test_uploadTimeseriesFile(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  print(tsUpload.uploadTimeseriesFile("inOutTest/bucket/INGV/1/WARN00DEU.pos","1.1.1"))
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  # def test_getStationID(self):
  #   logger = Logs("logs/logsTest.log",10000)
  #   pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #   pgConnection.connect()
  #   cfg = Config("config/appconf.cfg")
  #   tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #   self.assertEqual(tsUpload._getStationID("OUTA00UKN"),14)
  
  #def test_formatDate(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  self.assertEqual(tsUpload._formatDate("20201013","010536"),"2020-10-13 01:05:36")
    
  #def test_saveEstimatedCoordinatesToFile(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  tsUpload.saveEstimatedCoordinatesToFile("inOutTest/bucket/INGV/1/WARN00DEU.pos",32,16)
  
  #def test_uploadEstimatedCoordinates(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload.uploadEstimatedCoordinates()
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")

  #def test_removeEstimatedCoordinatesFile(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  tsUpload.eraseEstimatedCoordinatesTmpFile()
  
  # def test_uploadAllTS(self):
  #   logger = Logs("logs/logsTest.log",10000)
  #   pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #   pgConnection.connect()
  #   cfg = Config("config/appconf.cfg")
  #   tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #   tsUpload.uploadAllTS("inOutTest/bucket")
  
if __name__ == '__main__':
  unittest.main()