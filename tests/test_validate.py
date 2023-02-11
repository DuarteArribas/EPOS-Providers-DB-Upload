import unittest
from src.validate import *

class TestValidation(unittest.TestCase):
  def test_getExtension(self):
    a = Validator("dummy")
    self.assertEqual(a._getNExtension("{XXX}{v}OPSSNX_{yyyy}{ddd}0000_{pp}D_{pp}D_SOL.SNX.gz",1),"gz")
  
  def test_getExtension2(self):
    a = Validator("dummy")
    self.assertEqual(a._getNExtension("{XXX}{v}OPSSNX_{yyyy}{ddd}0000_{pp}D_{pp}D_SOL.SNX.gz",2),"snx")
    
if __name__ == '__main__':
  unittest.main()