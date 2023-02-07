import unittest
from src.utils.logs     import *
from src.dbConnection   import *
from src.databaseUpload import *

class TestTDDatabaseUpload(unittest.TestCase):
  #def test_getSolutionParameters(self):
  #  tsUpload = TSDatabaseUpload("dummy","dummy2","dummy3","dummy4")
  #  print(tsUpload._getSolutionParameters("outTest/public/INGV/5/TS/arroz.pos.gz"))
  #  
  #def test_writeSolutionParameters(self):
  #  tsUpload = TSDatabaseUpload("dummy","dummy2","dummy3","tmp")
  #  print(tsUpload._saveSolutionToFile("outTest/public/INGV/5/TS/arroz.pos.gz"))
  #
  #def test_upload_solution_opt(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  logger = Logs("logs/logsTest.log",10000)
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  pgConnection.cursor.execute("BEGIN TRANSACTION")
  #  tsUpload._uploadSolutionOptimized()
  #  pgConnection.cursor.execute("COMMIT TRANSACTION")
  #
  #def test_getTSFiles(self):
  #  tsUpload = TSDatabaseUpload("dummy","dummy2","dummy3","dummy4")
  #  self.assertEqual([file.split("/")[-1] for file in tsUpload._getListOfTSFiles("outTest/public")].sort(),["a.pos","b.vel","aab.pos","pp.vel","1.pos","a2.pos","a3.vel","b2.vel","p9.vel","arroz.pos.gz"].sort())
  #
  #def test_remove_from_dir(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  logger = Logs("logs/logsTest.log",10000)
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  tsUpload._removeFilesInDir("tmp")
  # 
  #def test_upload_TS_opt(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  logger = Logs("logs/logsTest.log",10000)
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  tsUpload._uploadTSOptimized()
  #def test_upload_solution(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  logger = Logs("logs/logsTest.log",10000)
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  pgConnection.cursor.execute("BEGIN TRANSACTION")
  #  tsUpload._uploadSolution(tsUpload._getSolutionParameters("outTest/public/INGV/5/TS/arroz.pos.gz"),"outTest/public/INGV/5/TS/arroz.pos.gz")
  #  pgConnection.cursor.execute("COMMIT TRANSACTION")
  #def test_upload_TS(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  logger = Logs("logs/logsTest.log",10000)
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
  #  tsUpload._uploadTS("outTest/public/INGV/5/TS/arroz.pos.gz")
  def test_upload_all_TS(self):
    pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
    pgConnection.connect()
    logger = Logs("logs/logsTest.log",10000)
    tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,"tmp")
    tsUpload.uploadAllTS("outTest/public")
  
if __name__ == '__main__':
  unittest.main()