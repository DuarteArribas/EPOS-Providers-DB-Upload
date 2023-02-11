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
  
  def test_isLeapYear(self):
    a = Validator("dummy","dummy2")
    self.assertTrue(a._isLeapYear(2000))
  
  def test_isLeapYear1(self):
    a = Validator("dummy","dummy2")
    self.assertFalse(a._isLeapYear(2001))
  
  def test_isLeapYear2(self):
    a = Validator("dummy","dummy2")
    self.assertFalse(a._isLeapYear(2002))
  
  def test_isLeapYear3(self):
    a = Validator("dummy","dummy2")
    self.assertFalse(a._isLeapYear(2003))
  
  def test_isLeapYear4(self):
    a = Validator("dummy","dummy2")
    self.assertTrue(a._isLeapYear(2004))
  
  def test_validateSnxFilenameDayOfYear(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_20003670000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_20000000000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear3(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000aaa000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear4(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000-12000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear5(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000999000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear6(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_1999366000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear7(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_2000366000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear8(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_1999365000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear9(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_1999001000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear10(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_2000001000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyydddOOOO_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant1(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyyddd0100_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyyddd0000-ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant3(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameConstant2("arroz","UGA1OPASNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_00D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_05D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod3(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_06D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod4(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_08D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod5(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_09D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod6(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_01D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod7(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_07D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant3,"arroz","UGA1OPASNX_yyyydddOOOO_00A_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant1(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant3,"arroz","UGA1OPASNX_yyyydddOOOO_00D-ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant2(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameConstant3("arroz","UGA1OPASNX_yyyydddOOOO_00D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod2(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_05D_05D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod3(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_06D_06D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod4(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_08D_08D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod5(self):
    a = Validator("dummy","dummy2")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_09D_09D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod6(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_01D_01D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod7(self):
    a = Validator("dummy","dummy2")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_07D_07D_SOL.SNX.gz")
    
if __name__ == '__main__':
  unittest.main()