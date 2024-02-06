import unittest
from src.dbConnection import *

class TestDBConnection(unittest.TestCase):
  def test_connection_success(self):
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost","5432","db305","postgres","postgres",logger)
    pgConnection.connect()
    
if __name__ == '__main__':
  unittest.main()