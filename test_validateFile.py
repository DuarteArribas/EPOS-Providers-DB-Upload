from validate import *
import unittest

class TestDetectFile(unittest.TestCase):
  def test_validate_snx(self):
    self.assertEqual(validateSnx("in/providers_sftp/providers_wut/uploads/Coor/eur21622.snx")[0],True)
  
  def test_validate_snx_cor(self):
    print(validateCoor("in/providers_sftp/test"))
    
if __name__ == '__main__':
  unittest.main()