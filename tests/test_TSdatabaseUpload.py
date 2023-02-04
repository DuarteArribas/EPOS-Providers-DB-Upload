import unittest
from src.dbConnection   import *
from src.databaseUpload import *

class TestTDDatabaseUpload(unittest.TestCase):
  def test_upload_solution(self):
    pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
    pgConnection.connect()
    tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor)
    tsUpload.uploadSolution('WTF','massa','1111-12-11','a','b','c','d','a','b','c','d')
  
  def test_upload_solution_optimized(self):
    pgConnection = DBConnection("localhost","5432","arroztestDB","postgres","arroz123")
    pgConnection.connect()
    tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor)
    tsUpload.uploadSolutionOptimized("in/solution_tmp_file")
    
if __name__ == '__main__':
  unittest.main()