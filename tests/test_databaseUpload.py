import unittest
from src.utils.logs     import *
from src.dbConnection   import *
from src.databaseUpload import *

class TestDatabaseUpload(unittest.TestCase):
  def test_get_TS(self):
    logger = Logs("logs/logsTest.log",10000)
    pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
    pgConnection.connect()
    tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
    self.assertEqual(tsUpload._getListOfTSFiles("inOutTest/bucket/INGV/1"),["HBLT00UKN.pos","WARN00DEU.pos"])
  
  #def test_checkSolutionAlreadyThere(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  self.assertEqual(tsUpload._checkSolutionAlreadyInDB("INGV","timeseries"),[8,9])
  #  print(tsUpload._checkSolutionAlreadyInDB("INGV","timeseries"))
  
  #def test_erasePreviousSolutionFromDB(self):
  #  logger = Logs("logs/logsTest.log",10000)
  #  pgConnection = DBConnection("localhost","5432","epos_dev","postgres","arroz123",logger)
  #  pgConnection.connect()
  #  tsUpload = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  tsUpload._erasePreviousSolutionFromDB("INGV","timeseries")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  
  
if __name__ == '__main__':
  unittest.main()