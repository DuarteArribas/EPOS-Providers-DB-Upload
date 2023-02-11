import unittest
from src.utils.config import*
from src.validate     import *

class TestValidation(unittest.TestCase):
  def test_getExtension(self):
    a = Validator("dummy","dummy2")
    self.assertEqual(a._getNExtension("{XXX}{v}OPSSNX_{yyyy}{ddd}0000_{pp}D_{pp}D_SOL.SNX.gz",1),"gz")
  
  def test_getExtension2(self):
    a = Validator("dummy","dummy2")
    self.assertEqual(a._getNExtension("{XXX}{v}OPSSNX_{yyyy}{ddd}0000_{pp}D_{pp}D_SOL.SNX.gz",2),"snx")
    
  def test_validateSnxFilenameAbbr(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameAbbr,"arroz","XXXvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr1(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameAbbr,"arroz","ROBvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr2(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameAbbr("arroz","UGAvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr3(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameAbbr("arroz","INGvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr4(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameAbbr("arroz","EURvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameVersion(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameVersion,"arroz","XXXaOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion1(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameVersion,"arroz","XXX-1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion2(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameVersion("arroz","XXX1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion3(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameVersion("arroz","XXX5OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion4(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameVersion("arroz","XXX9OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion5(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameVersion("arroz","XXX0OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
    
if __name__ == '__main__':
  unittest.main()