import unittest
from src.utils.passwordHandler import *

class TestPasswordHandler(unittest.TestCase):
  def test_getPwdFromFile(self):
    self.assertEqual(PasswordHandler.getPwdFromFolder("inTest/pwd",172),"arroz123")
    
if __name__ == '__main__':
  unittest.main()