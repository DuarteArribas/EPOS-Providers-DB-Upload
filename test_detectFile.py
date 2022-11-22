from detectFile import getHashOfDir
from detectFile import checkForNewFiles
import unittest
import sqlite3

class TestDetectFile(unittest.TestCase):
  def test_get_hash_of_dir(self):
    self.assertEqual(getHashOfDir("in/providers_sftp/"),"e16ed00a0f5dde37b44b5f1f3fb7a01d")
  
  def test_check_for_new_files(self):
    newHashes = ["a2","b","","d","e"]
    con = sqlite3.connect("db/detectFiles.db")
    cur = con.cursor()
    print(checkForNewFiles(con,cur,newHashes))
    
if __name__ == '__main__':
  unittest.main()