import unittest
from src.dbConnection import *

class TestDBConnection(unittest.TestCase):
  def test_connection_success(self):
    pgConnection = DBConnection()
    
if __name__ == '__main__':
  unittest.main()