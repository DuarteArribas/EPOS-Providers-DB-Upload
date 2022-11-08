from detectFile import getFiles
from detectFile import check
import unittest
import sqlite3

class TestDetectFile(unittest.TestCase):
  def test_get_files(self):
    self.assertEqual(getFiles("inTest/1"),[])
  
  def test_get_files2(self):
    self.assertEqual(getFiles("inTest/2"),["1.txt","2.txt","3.txt"])
  
  def test_get_files3(self):
    self.assertEqual(getFiles("inTest/3"),["1.txt","2.txt"])
    
  def test_check(self):
    con = sqlite3.connect("db/detectFiles.db")
    cur = con.cursor()
    self.assertEqual(check(con,cur,["file7.txt","file6.txt","file5.txt"]),["file7.txt","file6.txt","file5.txt"])
    
if __name__ == '__main__':
  unittest.main()