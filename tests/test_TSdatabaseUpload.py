import unittest
from src.dbConnection   import *
from src.databaseUpload import *

class TestTDDatabaseUpload(unittest.TestCase):
  #def test_upload_solution(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor)
  #  tsUpload.uploadSolution('WTF','massa','1111-12-11','a','b','c','d','a','b','c','d')
  #
  #def test_upload_solution_optimized(self):
  #  pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
  #  pgConnection.connect()
  #  tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor)
  #  tsUpload.uploadSolutionOptimized("in/solution_tmp_file")
  
  def test_getTSFiles(self):
    tsUpload = TSDatabaseUpload("dummy","dummy2","dummy3")
    self.assertEqual([file.split("/")[-1] for file in tsUpload._getListOfTSFiles("outTest/public")],["a.pos","b.vel","aab.pos","pp.vel","1.pos","a2.pos","a3.vel","b2.vel","p9.vel"])
    
if __name__ == '__main__':
  unittest.main()