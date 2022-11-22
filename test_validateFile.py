from validate import validateCoor
from validate import validateTS
from validate import validateVel
from validate import validateProviderDir
import unittest

class TestDetectFile(unittest.TestCase):
  def test_validate_dir(self):
    self.assertEqual(validateCoor(["a.snx,b.snx"]),True)
  
  def test_validate_dir2(self):
    self.assertEqual(validateTS(["a.pos,b.pos"]),True)
    
  def test_validate_dir3(self):
    self.assertEqual(validateVel(["a.vel,b.vel"]),True)
  
  def test_validate_dir4(self):
    self.assertEqual(validateProviderDir("in/providers_sftp/providers_uga/uploads"),True)
    
if __name__ == '__main__':
  unittest.main()