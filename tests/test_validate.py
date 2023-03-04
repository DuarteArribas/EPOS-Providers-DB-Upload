import unittest
from src.utils.config import *
from src.dbConnection import *
from src.validate     import *

class TestValidation(unittest.TestCase):    
  def test_validateSnxFilenameAbbr(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameAbbr,"arroz","XXXvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameAbbr,"arroz","ROBvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr2(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameAbbr("arroz","UGAvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr3(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameAbbr("arroz","INGvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameAbbr4(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameAbbr("arroz","EURvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz",["ING","UGA","EUR"])
  
  def test_validateSnxFilenameVersion(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameVersion,"arroz","XXXaOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameVersion,"arroz","XXX-1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion2(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameVersion("arroz","XXX1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion3(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameVersion("arroz","XXX5OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion4(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameVersion("arroz","XXX9OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameVersion5(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameVersion("arroz","XXX0OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA1OPASNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA10PSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant,"arroz","UGA1OPSRAP_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameConstant3(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameConstant("arroz","UGA1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_1800ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_aa29ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_2050ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_0000ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear5(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_9999ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear6(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_2024ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear7(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameYear,"arroz","UGA1OPSSNX_1993ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear8(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_1994ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear9(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_1999ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear10(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2000ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear11(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2022ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameYear12(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameYear("arroz","UGA1OPSSNX_2023ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_isLeapYear(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertTrue(a._isLeapYear(2000))
  
  def test_isLeapYear1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertFalse(a._isLeapYear(2001))
  
  def test_isLeapYear2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertFalse(a._isLeapYear(2002))
  
  def test_isLeapYear3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertFalse(a._isLeapYear(2003))
  
  def test_isLeapYear4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertTrue(a._isLeapYear(2004))
  
  def test_validateSnxFilenameDayOfYear(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_20003670000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_20000000000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000aaa000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000-12000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear5(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_2000999000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear6(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameDayOfYear,"arroz","UGA1OPSSNX_1999366000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear7(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_2000366000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear8(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_1999365000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear9(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_1999001000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameDayOfYear10(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameDayOfYear("arroz","UGA1OPSSNX_2000001000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyydddOOOO_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyyddd0100_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant2,"arroz","UGA1OPASNX_yyyyddd0000-ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2Constant3(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameConstant2("arroz","UGA1OPASNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_00D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_05D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_06D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_08D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod5(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_09D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod6(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_01D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilenameSamplePeriod7(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_07D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant3,"arroz","UGA1OPASNX_yyyydddOOOO_00A_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant3,"arroz","UGA1OPASNX_yyyydddOOOO_00D-ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3Constant2(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameConstant3("arroz","UGA1OPASNX_yyyydddOOOO_00D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_05D_05D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_06D_06D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_08D_08D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod5(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameSamplePeriod,"arroz","UGA1OPASNX_yyyydddOOOO_09D_09D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod6(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_01D_01D_SOL.SNX.gz")
  
  def test_validateSnxFilename2SamplePeriod7(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameSamplePeriod("arroz","UGA1OPASNX_yyyydddOOOO_07D_07D_SOL.SNX.gz")
  
  def test_validateSnxFilename4Constant(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant4,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.SNX.gz")
  
  def test_validateSnxFilename4Constant1(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant4,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_5OL.SNX.gz")
  
  def test_validateSnxFilename4Constant2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant4,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D-SOL.SNX.gz")
  
  def test_validateSnxFilename4Constant3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant4,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00P_SOL.SNX.gz")
  
  def test_validateSnxFilename4Constant4(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameConstant4,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_SOK.SNX.gz")
  
  def test_validateSnxFilename4Constant5(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameConstant4("arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_SOL.SNX.gz")
  
  def test_validateSnxFilenameExtension(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.pos.gz")
  
  def test_validateSnxFilenameExtension2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.vel.gz")
  
  def test_validateSnxFilenameExtension3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.sxn.gz")
  
  def test_validateSnxFilenameExtension4(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameExtension("arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.snx.gz")
  
  def test_validateSnxFilenameCompressExtension(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameCompressExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.pos...")
  
  def test_validateSnxFilenameCompressExtension2(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameCompressExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.pos.pz")
  
  def test_validateSnxFilenameCompressExtension3(self):
    a = Validator("dummy","dummy2","dummy3")
    self.assertRaises(ValidationError,a._validateSnxFilenameCompressExtension,"arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.pos.lz")
  
  def test_validateSnxFilenameCompressExtension4(self):
    a = Validator("dummy","dummy2","dummy3")
    a._validateSnxFilenameCompressExtension("arroz","UGA1OPASNX_yyyydddOOOO_00D_00D_S0L.pos.gz")
  
  def test_validateSnxFilename(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/XXXvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename1(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/INGvOPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename2(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING1OPSSNX_yyyyddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename3(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING2OPSSNX_1999ddd0000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename4(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING3OPSSNX_19993450000_ppD_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename5(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING4OPSSNX_19993450000_01D_ppD_SOL.SNX.gz")
  
  def test_validateSnxFilename6(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING5OPSSNX_19993450000_01D_07D_SOL.pos.gz")
  
  def test_validateSnxFilename7(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ROB5OPSSNX_19993450000_01D_07D_SOL.SNX.gz")
  
  def test_validateSnxFilename8(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING5OPSSNX_19993450000_01D_07D_SOL.SNX")
  
  def test_validateSnxFilename9(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz/ING")
  
  def test_validateSnxFilename10(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    self.assertRaises(ValidationError,a._validateSnxLongFilename,"arroz")
  
  def test_validateSnxFilename11(self):
    cfg = Config("config/appconf.cfg")
    a = Validator(cfg,"dummy","dummy3")
    a._validateSnxLongFilename("arroz/ING5OPSSNX_19993450000_01D_07D_SOL.SNX.gz")
   
#  def test_getAnalysisCentreValues(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertEqual(a._getAllowedAnalysisCentreValues(),["INGV","LM","NOA","ROB-EUREF","SGO-EPND","UGA-CNRS","WUT-EUREF"])
#  
#  def test_validateAnalysisCentreMetadataLines(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," AnalysisCentre     WUT-EURIF                                                   ","arroz")
#  
#  def test_validateAnalysisCentreMetadataLines2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," AnalysisCentre     UGA-EUREF                                                   ","arroz")
#  
#  def test_validateAnalysisCentreMetadataLines3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," AnalysisCentre     arroz                                                   ","arroz")
#  
#  def test_validateAnalysisCentreMetadataLines4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," AnalysisCentre                                                       ","arroz")
#  
#  def test_validateAnalysisCentreMetadataLines5(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" AnalysisCentre     WUT-EUREF                                                   ","arroz")
#  
#  def test_validateAnalysisCentreMetadataLines6(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" AnalysisCentre     INGV                                                   ","arroz")
#    
#  def test_validateCreationDateMetadataLines(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," CreationDate       15/06/2021 12:00:00                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," CreationDate       15/2021/06 12:00:00                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," CreationDate       2021/06/33 12:00:00                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," CreationDate       2021/02/29 12:00:00                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines5(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" CreationDate       2021/06/15 12:00:00                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines6(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" CreationDate       2021/06/15 12:11:33                                         ","arroz")
#  
#  def test_validateCreationDateMetadataLines7(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" CreationDate       2023/02/11 12:11:33                                         ","arroz")
#  
#  def test_validateDOIMetadataLines(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," DOI                                                                     ","arroz")
#  
#  def test_validateDOIMetadataLines2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," DOI             10.24414/ROB-EUREF-C3220                                                    ","arroz")
#    
#  def test_validateDOIMetadataLines3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" DOI                unknown                                                     ","arroz")
#  
#  def test_validateDOIMetadataLines4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" DOI                10.24414/ROB-EUREF-C2220                                                     ","arroz")
#
#  def test_validateSoftwareMetadataLines(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," Software           Berese GNSS Software 5.2                                   ","arroz")
#
#  def test_validateSoftwareMetadataLines2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," Software           Berese GNSS Software 5.3                                   ","arroz")
#
#  def test_validateSoftwareMetadataLines3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," Software                                             ","arroz")
#
#  def test_validateSoftwareMetadataLines4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" Software           Bernese GNSS Software 5.2                                   ","arroz")
#
#  def test_validateSoftwareMetadataLines5(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" Software           GIPSY-OASIS                                   ","arroz")
#
#  def test_validateSoftwareMetadataLines6(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" Software           CATREF                                   ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," SamplingPeriod     aily                                                       ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," SamplingPeriod     week                                                       ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," SamplingPeriod     monthly                                                       ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a._validateMetadataLineSnx," SamplingPeriod                                                           ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines5(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" SamplingPeriod    daily                                                ","arroz")
#
#  def test_validateSamplingPeriodMetadataLines6(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a._validateMetadataLineSnx(" SamplingPeriod    weekly                                                ","arroz")
#
#  def test_validateSnxFile(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    a.validateSnx("inTest/ING5OPSSNX_19993450000_01D_07D_SOL.snx.gz")
#
#  def test_validateSnxFile2(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a.validateSnx,"inTest/ING5OPSSNX_19993450000_02D_07D_SOL.snx.gz")
#    
#  def test_validateSnxFile3(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a.validateSnx,"inTest/ING5OPSSNX_20003450000_01D_07D_SOL.snx.gz")
#  
#  def test_validateSnxFile4(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a.validateSnx,"inTest/ING5OPSSNX_20013450000_01D_07D_SOL.snx.gz")
#  
#  def test_validateSnxFile5(self):
#    logger = Logs("logs/logsTest.log",10000)
#    pgConnection = DBConnection("localhost","5432","eposTest","postgres","arroz123",logger)
#    pgConnection.connect()
#    cfg = Config("config/appconf.cfg")
#    a = Validator("dummy",cfg,pgConnection.conn,pgConnection.cursor)
#    self.assertRaises(ValidationError,a.validateSnx,"inTest/ING5OPSSNX_20023450000_01D_07D_SOL.snx.gz")

if __name__ == '__main__':
  unittest.main()