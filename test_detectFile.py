from detectFile import getFilenamesAndHashes
from detectFile import getNewFiles
import unittest
import sqlite3

class TestDetectFile(unittest.TestCase):
  def test_get_files(self):
    self.assertEqual(getFilenamesAndHashes("inTest/1"),[])
    
  def test_check(self):
    con = sqlite3.connect("db/detectFiles.db")
    cur = con.cursor()
    self.assertEqual(getNewFiles(con,cur,["file7.txt","file6.txt","file5.txt"]),["file7.txt","file6.txt","file5.txt"])
    
if __name__ == '__main__':
  unittest.main()