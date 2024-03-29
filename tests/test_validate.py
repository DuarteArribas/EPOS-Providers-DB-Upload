import unittest
from src.utils.config import *
from src.dbConnection import *
from src.validate     import *

class TestValidation(unittest.TestCase):
  def test_validateSnxFilename(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator._validateSnxFilenameAbbr("path/ARR3OPSSNX_20002340000_01D_01D_SOL.SNX.gz","ARR3OPSSNX_20002340000_01D_01D_SOL.SNX.gz",["ING","WUT","ROB"])
      validator._validateSnxFilenameAbbr("path/3OPSSNX_20002340000_01D_01D_SOL.SNX.gz","3OPSSNX_20002340000_01D_01D_SOL.SNX.gz",["ING","WUT","ROB"])
      validator._validateSnxFilenameAbbr("path/INV3OPSSNX_20002340000_01D_01D_SOL.SNX.gz","INV3OPSSNX_20002340000_01D_01D_SOL.SNX.gz",["ING","WUT","ROB"])
      validator._validateSnxFilenameAbbr("path/ING3OPSSNX_20002340000_01D_01D_SOL.SNX.gz","ING3OPSSNX_20002340000_01D_01D_SOL.SNX.gz",["WUT","ROB"])
      validator._validateSnxFilenameVersion("path/INGaOPSSNX_20002340000_01D_01D_SOL.SNX.gz","INGaOPSSNX_20002340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameVersion("path/ING_OPSSNX_20002340000_01D_01D_SOL.SNX.gz","ING_OPSSNX_20002340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant("path/ING1OP1SNX_20002340000_01D_01D_SOL.SNX.gz","ING1OP1SNX_20002340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant("path/ING1OPSNNX_20002340000_01D_01D_SOL.SNX.gz","ING1OPSNNX_20002340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameYear("path/ING1OPSSNX_20352340000_01D_01D_SOL.SNX.gz","ING1OPSSNX_20352340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameYear("path/ING1OPSSNX_30002340000_01D_01D_SOL.SNX.gz","ING1OPSSNX_30002340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameYear("path/ING1OPSSNX_aaaa2340000_01D_01D_SOL.SNX.gz","ING1OPSSNX_aaaa2340000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameDayOfYear("path/ING1OPSSNX_20005120000_01D_01D_SOL.SNX.gz","ING1OPSSNX_20005120000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameDayOfYear("path/ING1OPSSNX_2000AAA0000_01D_01D_SOL.SNX.gz","ING1OPSSNX_2000AAA0000_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant2("path/ING1OPSSNX_20002450001_01D_01D_SOL.SNX.gz","ING1OPSSNX_20002450001_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant2("path/ING1OPSSNX_20002450002_01D_01D_SOL.SNX.gz","ING1OPSSNX_20002450002_01D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameSamplePeriod("path/ING1OPSSNX_20002450000_02D_01D_SOL.SNX.gz","ING1OPSSNX_20002450000_02D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameSamplePeriod("path/ING1OPSSNX_20002450000_aaD_01D_SOL.SNX.gz","ING1OPSSNX_20002450000_aaD_01D_SOL.SNX.gz")
      validator._validateSnxFilenameSamplePeriod("path/ING1OPSSNX_20002450000___D_01D_SOL.SNX.gz","ING1OPSSNX_20002450000___D_01D_SOL.SNX.gz")
      validator._validateSnxFilenameSamplePeriod("path/ING1OPSSNX_20002450000_02W_01D_SOL.SNX.gz","ING1OPSSNX_20002450000_02W_01D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant3("path/ING1OPSSNX_20002450000_01F_01D_SOL.SNX.gz","ING1OPSSNX_20002450000_01F_01D_SOL.SNX.gz")
      validator._validateSnxFilenameSamplePeriod2("path/ING1OPSSNX_20002450000_01D_02D_SOL.SNX.gz","ING1OPSSNX_20002450000_01D_02D_SOL.SNX.gz")
      validator._validateSnxFilenameConstant4("path/ING1OPSSNX_20002450000_01D_01D_LUA.SNX.gz","ING1OPSSNX_20002450000_01D_01D_LUA.SNX.gz")
      validator._validateSnxFilenameConstant4("path/ING1OPSSNX_20002450000_01D_01F_SOL.SNX.gz","ING1OPSSNX_20002450000_01D_01F_SOL.SNX.gz")
      validator._validateSnxFilenameExtension("path/ING1OPSSNX_20002450000_01D_01D_SOL.POS.gz","ING1OPSSNX_20002450000_01D_01D_SOL.POS.gz")
      validator._validateSnxFilenameExtension("path/ING1OPSSNX_20002450000_01D_01D_SOL.SXN.gz","ING1OPSSNX_20002450000_01D_01D_SOL.SXN.gz")
      validator._validateSnxFilenameExtension("path/ING1OPSSNX_20002450000_01D_01D_SOL.SXN.gz","ING1OPSSNX_20002450000_01D_01D_SOL.SXN.gz")
      validator._validateSnxFilenameCompressExtension("path/ING1OPSSNX_20002450000_01D_01D_SOL.SNX","ING1OPSSNX_20002450000_01D_01D_SOL.SNX")
      validator._validateSnxFilenameCompressExtension("path/ING1OPSSNX_20002450000_01D_01D_SOL.SNX.zip","ING1OPSSNX_20002450000_01D_01D_SOL.SNX.zip")
      validator._validateSnxLongFilename("path/ING","ING")
      validator._validateSnxLongFilename("path/ING1OPSSNX_20002450000_01D_01D_SOL.POS.gz","ING1OPSSNX_20002450000_01D_01D_SOL.POS.gz")
  
  def test_validateSnxLine(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator._validateMetadataLineSnx("AnalysisCentre            ARRR   ","data/in/test/validation/wrong/snx/wrongAnalysisCentre/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator._validateMetadataLineSnx("AnalysisCentre            ING   ","data/in/test/validation/wrong/snx/wrongAnalysisCentre/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator._validateMetadataLineSnx("Software                  GIPSY-OASIS 6.3 ","data/in/test/validation/wrong/snx/wrongSoftware/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator._validateMetadataLineSnx("DOI                       aaaaa            ","data/in/test/validation/wrong/snx/wrongDoi/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator._validateMetadataLineSnx("CreationDate              02/02/2123 13:24:18","data/in/test/validation/wrong/snx/wrongCreationDate/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator._validateMetadataLineSnx("CreationDate              02/02/2023 13:24_18","data/in/test/validation/wrong/snx/wrongCreationDate/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator._validateMetadataLineSnx("CreationDate              2001/02/25 13:24:18","data/in/test/validation/wrong/snx/wrongCreationDate/3/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator._validateMetadataLineSnx(" ReleaseVersion                          ","data/in/test/validation/wrong/snx/wrongReleaseVersion/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator._validateMetadataLineSnx("SamplingPeriod            monthly      ","data/in/test/validation/wrong/snx/wrongSamplingPeriod/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("AnalysisCentre            INGV  ","data/in/test/validation/right/snx/rightAnalysisCentre/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("Software                  GIPSY-OASIS ","data/in/test/validation/right/snx/rightSoftware/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("DOI                       unknown            ","data/in/test/validation/right/snx/rightDoi/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("CreationDate              02/02/2023 13:24:18","data/in/test/validation/right/snx/rightCreationDate/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx(" ReleaseVersion              2222.0         ","data/in/test/validation/right/snx/rightReleaseVersion/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("SamplingPeriod            daily      ","data/in/test/validation/right/snx/rightSamplingPeriod/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator._validateMetadataLineSnx("SamplingPeriod            daily      ","data/in/test/validation/right/snx/rightSamplingPeriod/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
  
  def test_validateSnx(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongAnalysisCentre/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongAnalysisCentre/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongSoftware/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongDoi/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongCreationDate/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongCreationDate/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongCreationDate/3/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongReleaseVersion/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongSamplingPeriod/1/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongFile/1/NG1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
      validator.validateSnx("data/in/test/validation/wrong/snx/wrongFile/2/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    validator.validateSnx("data/in/test/validation/right/snx/rightFile/ING1OPSSNX_20053650000_01D_01D_SOL.snx.gz")
    
  def test_validateTSFilename(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator._validatePosFilenameAbbr("path/ARR_ANK200UKN_01D.pos","ARR_ANK200UKN_01D.pos",["ING","WUT","ROB"])
      validator._validatePosFilenameAbbr("path/ING_ANK200UKN_01D.pos","ARR_ANK200UKN_01D.pos",["WUT","ROB"])
      validator._validatePosFilenameConstant("path/ING1ANK200UKN_01D.pos","ING1ANK200UKN_01D.pos")
      validator._validatePosFilenameSamplingPeriod("path/ING_ANK200UKN_01F.pos","ING_ANK200UKN_01F.pos")
      validator._validatePosFilenameSamplingPeriod("path/ING_ANK200UKN_02D.pos","ING_ANK200UKN_02D.pos")
      validator._validatePosFilenameExtension("path/ING_ANK200UKN_01D.pbo","ING_ANK200UKN_01D.pbo")
      validator._validatePosFilename("data/in/test/validation/wrong/ts/wrongFilename/INGV_ANK200UKN_01D.pos")
    validator._validatePosFilenameAbbr("path/ING_ANK200UKN_01D.pos","ING_ANK200UKN_01D.pos",["ING","WUT","ROB"])
    validator._validatePosFilenameSamplingPeriod("ING_ANK200UKN_01D.pos","ING_ANK200UKN_01D.pos")
    validator._validatePosFilenameExtension("path/ING_ANK200UKN_01D.pos","ING_ANK200UKN_01D.pos")
    validator._validatePosFilename("data/in/test/validation/right/ts/rightFilename/ING_ANK200UKN_01D.pos")
  
  def test_validateTSLine(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator._validateMetadataLinePos("9-character ID: ANK300UKN","data/in/test/validation/wrong/ts/wrong9CharId/ING_ANK200UKN_01D.pos")
    validator._validateMetadataLinePos("9-character ID: ANK200TUR","data/in/test/validation/right/ts/right9CharId/ING_ANK200TUR_01D.pos")
  
  
  def test_validateTS(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator.validatePos("data/in/test/validation/wrong/ts/wrongFile/1/ING_ANK200UKN_01D.pos")
      validator.validatePos("data/in/test/validation/wrong/ts/wrongFile/2/ING_ANK200UKN_01D.pos")
    validator.validatePos("data/in/test/validation/right/ts/rightFile/ING_ANK200TUR_01D.pos")
    
  def test_validateVelFilename(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    validator = Validator(cfg,pgConnection.conn,pgConnection.cursor)
    with self.assertRaises(ValidationError):
      validator._validateVelFilenameAbbr("path/ARR_2023.1_IGb14.vel","ARR_2023.1_IGb14.vel",["SGO","WUT","ROB"])
      validator._validateVelFilenameVersion("data/in/test/validation/wrong/vel/wrongFilenameVersion/SGO_2023.1_IGb14.vel","SGO_2023.1_IGb14.vel")
      validator._validateVelFilenameReferenceFrame("data/in/test/validation/wrong/vel/wrongFilenameReferenceFrame/SGO_2023.1_IGb14.vel","SGO_2023.1_IGb14.vel")
      validator._validateVelFilenameExtension("path/SGO_2023.1_IGb14.pos","SGO_2023.1_IGb14.pos")
      validator._validateVelFilename("data/in/test/validation/wrong/vel/wrongFilename/SGO_2023.1_IGb14.vel")
    validator._validateVelFilenameAbbr("path/SGO_2023.1_IGb14.vel","SGO_2023.1_IGb14.vel",["SGO","WUT","ROB"])
    validator._validateVelFilenameVersion("data/in/test/validation/right/vel/rightFilenameVersion/SGO_2221.0_IGb14.vel","SGO_2221.0_IGb14.vel")
    validator._validateVelFilenameReferenceFrame("data/in/test/validation/right/vel/rightFilenameReferenceFrame/SGO_2221.0_IGb14.vel","SGO_2221.0_IGb14.vel")
    validator._validateVelFilenameExtension("path/SGO_2023.1_IGb14.vel","SGO_2023.1_IGb14.vel")
    validator._validateVelFilename("data/in/test/validation/right/vel/rightFilename/SGO_2221.0_IGb14.vel")
    
if __name__ == '__main__':
  unittest.main()