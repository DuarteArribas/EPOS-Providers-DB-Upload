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
  
  def test_validateSnxFilenameConstant(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA1OPASNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant1(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA10PSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA1OPSRAP_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant3(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameConstant("arroz","UGA1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_1800ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_aa29ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear3(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_2050ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear4(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_0000ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear5(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_9999ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear6(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_2024ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear7(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_1993ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear8(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_1994ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear9(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_1999ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear10(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2000ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear11(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2022ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear12(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2023ddd0000_ppD_ppD_SOL.SNX.gz")
    
if __name__ == '__main__':
  unittest.main()