import unittest
from src.dbConnection   import *
from src.databaseUpload import *

class TestTDDatabaseUpload(unittest.TestCase):
  def test_upload_station(self):
    pgConnection = DBConnection("localhost","5432","postgres","postgres","arroz123")
    pgConnection.connect()
    tsUpload     = TSDatabaseUpload(pgConnection.conn,pgConnection.cursor)
    tsUpload.uploadSolution(1,2,3,4,5,6,7,8,9,1,2)
    
    
if __name__ == '__main__':
  unittest.main()