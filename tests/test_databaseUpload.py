import unittest
from src.utils.logs     import *
from src.utils.config   import *
from src.dbConnection   import *
from src.databaseUpload import *

class TestDatabaseUpload(unittest.TestCase):
  def test_get_TS(self):
    logger = Logs("logs/logsTest.log",10000)
    pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
    pgConnection.connect()
    tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
    self.assertEqual(tsUpload._getListOfTSFiles("inOutTest/bucket/INGV/1"),["HBLT00UKN.pos","WARN00DEU.pos"])
  
  #def test_checkSolutionAlreadyThere(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  self.assertEqual(tsUpload._checkSolutionAlreadyInDB("INGV","timeseries"),[8,9])
  #  print(tsUpload._checkSolutionAlreadyInDB("INGV","timeseries"))
  
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
  #  print(tsUpload._getTimeseriesFilesID(13))

  #def test_erasePreviousTimeseriesFilesFromDB(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"dummy1","tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._erasePreviousTimeseriesFilesFromDB(6)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")

  #def test_handlePreviousSolution(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._handlePreviousSolution("INGV","timeseries")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  #def test_getSolutionParameters(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  print(tsUpload._getSolutionParameters("inOutTest/bucket/INGV/1/WARN00DEU.pos"))
  
  def test_checkReferenceFrameInDB(self):
    logger = Logs("logs/logsTest.log",10000)
    pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
    pgConnection.connect()
    cfg = Config("config/appconf.cfg")
    tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
    self.assertEqual(tsUpload._checkReferenceFrameInDB("IGb08"),["IGb08"])
  
  def test_checkReferenceFrameInDB2(self):
    logger = Logs("logs/logsTest.log",10000)
    pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
    pgConnection.connect()
    cfg = Config("config/appconf.cfg")
    tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
    self.assertEqual(tsUpload._checkReferenceFrameInDB("IGb01"),[])
  
  #def test_uploadReferenceFrame(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._uploadReferenceFrame("arrrozlol2","2022-11-11")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")

  #def test_uploadReferenceFrame(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._handleReferenceFrame("arrrozlol3","2022-11-11")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  #def test_uploadSolution(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  cfg = Config("config/appconf.cfg")
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
  #  solutionParameters = {'reference_frame': 'IGb14', 'ac_acronym': 'ROB-EUREF', 'software': 'CATREF', 'processing_parameters_url': 'https://youtube.com', 'doi': '10.24414/ROB-EUREF-C2220', 'release_version': '2220.0', 'sampling_period': 'daily', 'creation_date': '2022-10-13 00:00:00'}
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._uploadSolution("timeseries",solutionParameters)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  def test_getFormatVersion(self):
    logger = Logs("logs/logsTest.log",10000)
    pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
    pgConnection.connect()
    cfg = Config("config/appconf.cfg")
    tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp")
    tsUpload._getPosFormatVersion("inOutTest/bucket/INGV/1/WARN00DEU.pos")
  
if __name__ == '__main__':
  unittest.main()