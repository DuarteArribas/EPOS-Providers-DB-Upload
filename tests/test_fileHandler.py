import unittest
from src.fileHandler import *

class TestFileHandler(unittest.TestCase):
  def test_get_pwd_from_file(self):
    fh = FileHandler("dummy1","dummy2","dummy3","dummy4","inTest/pwd")
    self.assertEqual(fh._getPwdFromFile(),"arroz123")
    
if __name__ == '__main__':
  unittest.main()