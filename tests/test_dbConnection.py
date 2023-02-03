import unittest
from src.dbConnection import *

class TestDBConnection(unittest.TestCase):
  def test_connection_unsuccess(self):
    pgConnection = DBConnection("localhost","12345","arroz","arroz","arroz")
    pgConnection.connect()
    
if __name__ == '__main__':
  unittest.main()