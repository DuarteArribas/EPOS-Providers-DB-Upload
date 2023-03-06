import unittest
from src.fileHandler import *
import sqlite3

class TestFileHandler(unittest.TestCase):
  def test_getHashOfDir(self):
    fh = FileHandler("dummy1","dummy2","dummy3","dummy4")
    print(fh._getHashOfDir("inTest/providers_sftp"))
  
  def test_getListOfHashesChanged(self):
    con = sqlite3.connect("db/detectFiles.db")
    fh = FileHandler(con,"inTest/providers_sftp","arroz@gmail.com","arroz123")
    print(fh.getListOfHashesChanged())
  
  #def test_moveSnxToPublic(self):
  #  fh = FileHandler("dummy1","dummy2","dummy3","dummy4")
  #  fh.moveSnxFileToPublic("inTest/ING5OPSSNX_19993450000_01D_07D_SOL.snx.gz","outTest/public/INGV")
  
    
if __name__ == '__main__':
  unittest.main()