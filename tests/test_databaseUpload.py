import unittest
from testfixtures       import TempDirectory
from src.utils.logs     import *
from src.utils.config   import *
from src.dbConnection   import *
from src.databaseUpload import *
from src.uploadError    import *
from src.fileHandler    import *

class TestDatabaseUpload(unittest.TestCase):
  def test_validateTSFilename(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    with TempDirectory() as d:
      test_txt  = open(os.path.join(d.path,"test.txt"), "w")
      test_txt2 = open(os.path.join(d.path,"test2.txt"), "w")
      test_pos  = open(os.path.join(d.path,"test.pos"), "w")
      test_txt3 = open(os.path.join(d.path,"test3.txt"), "w")
      test_pos2 = open(os.path.join(d.path,"test2.pos"), "w")
      test_txt.close()
      test_txt2.close()
      test_pos.close()
      test_txt3.close()
      test_pos2.close()
      self.assertEqual(databaseDump.getListOfTSFiles(d.path),["test.pos","test2.pos"])
  
  def test_upload_solution(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    pgConnection.cursor.execute("START TRANSACTION;")
    databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
    pgConnection.cursor.execute("DELETE FROM solution WHERE processing_parameters_url = 'https://gnssproducts.epos.ubi.pt/TEST/INGV_TS.pdf';")
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  def test_checkSolutionAlreadyInDB(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    pgConnection.cursor.execute("START TRANSACTION;")
    databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST2/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
    self.assertNotEqual(databaseDump.checkSolutionAlreadyInDB("INGV","timeseries"),[])
    pgConnection.cursor.execute("START TRANSACTION;")
    pgConnection.cursor.execute("DELETE FROM solution WHERE processing_parameters_url = 'https://gnssproducts.epos.ubi.pt/TEST2/INGV_TS.pdf';")
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
    
  def test_getVersionFromSolution(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    pgConnection.cursor.execute("START TRANSACTION;")
    databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST3/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
    self.assertEqual(databaseDump.getVersionFromSolution(databaseDump.checkSolutionAlreadyInDB("INGV","timeseries")[0]),"2023.1")
    pgConnection.cursor.execute("START TRANSACTION;")
    pgConnection.cursor.execute("DELETE FROM solution WHERE processing_parameters_url = 'https://gnssproducts.epos.ubi.pt/TEST3/INGV_TS.pdf';")
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  def test_erasePreviousSolutionFromDB(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    pgConnection.cursor.execute("START TRANSACTION;")
    databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST4/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
    pgConnection.cursor.execute("START TRANSACTION;")
    databaseDump._erasePreviousSolutionFromDB("INGV","timeseries")
    pgConnection.cursor.execute("COMMIT TRANSACTION;")
  
  def test_getSolutionParametersTS(self):
    cfg          = Config("config/appconf.cfg")
    logger       = Logs("logs/logsTest.log",1000)
    pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
    pgConnection.connect()
    fileHandler = FileHandler(
      providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
      fromEmail         = "arroz123",
      fromEmailPassword = "arroz123"
    )
    databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
    with TempDirectory() as d:
      test_pos = open(os.path.join(d.path,"test.pos"),"w")
      posFileContent = (
        "PBO Station Position Time Series. Reference Frame : IGS14\n"
        "Format Version: 1.1.0\n"
        "4-character ID: ACOR\n"
        "Station name  : ACOR\n"
        "First Epoch   : 20000101 120000\n"
        "Last Epoch    : 20221231 120000\n"
        "Release Date  : 20230201 090806\n"
        "XYZ Reference position :    4594489.63752  -678367.62227  4357066.20414 (IGS14)\n"
        "NEU Reference position :     43.3643846386  351.6010688682   66.90070 (IGS14/WGS84)\n"
        "%Begin EPOS metadata\n"
        "9-character ID: ACOR00ESP\n"
        "AnalysisCentre: INGV\n"
        "Software      : GIPSY 6.3\n"
        "Method-url    : https://gnssproducts.epos.ubi.pt/methods/INGV_TS.pdf\n"
        "DOI           : not_specified\n"
        "ReleaseVersion: 2023.1\n"
        "SamplingPeriod: daily\n"
        "CreationDate  : 2023-02-03 18:00:00\n"
        "%End EPOS metadata\n"
      )
      test_pos.write(posFileContent)
      test_pos.close()
      self.assertEqual(databaseDump.getSolutionParametersTS(os.path.join(d.path,"test.pos")),{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/methods/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
  
  #def test_getPBOFormatVersion(self):
  #  cfg          = Config("config/appconf.cfg")
  #  logger       = Logs("logs/logsTest.log",1000)
  #  pgConnection = DBConnection("localhost",5432,"PP-products","postgres","postgres",logger)
  #  pgConnection.connect()
  #  fileHandler = FileHandler(
  #    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
  #    fromEmail         = "arroz123",
  #    fromEmailPassword = "arroz123"
  #  )
  #  databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
  #  with TempDirectory() as d:
  #    test_pos = open(os.path.join(d.path,"test.pos"),"w")
  #    posFileContent = (
  #      "PBO Station Position Time Series. Reference Frame : IGS14\n"
  #      "Format Version: 1.1.0\n"
  #      "4-character ID: ACOR\n"
  #      "Station name  : ACOR\n"
  #      "First Epoch   : 20000101 120000\n"
  #      "Last Epoch    : 20221231 120000\n"
  #      "Release Date  : 20230201 090806\n"
  #      "XYZ Reference position :    4594489.63752  -678367.62227  4357066.20414 (IGS14)\n"
  #      "NEU Reference position :     43.3643846386  351.6010688682   66.90070 (IGS14/WGS84)\n"
  #      "%Begin EPOS metadata\n"
  #      "9-character ID: ACOR00ESP\n"
  #      "AnalysisCentre: INGV\n"
  #      "Software      : GIPSY 6.3\n"
  #      "Method-url    : https://gnssproducts.epos.ubi.pt/methods/INGV_TS.pdf\n"
  #      "DOI           : not_specified\n"
  #      "ReleaseVersion: 2023.1\n"
  #      "SamplingPeriod: daily\n"
  #      "CreationDate  : 2023-02-03 18:00:00\n"
  #      "%End EPOS metadata\n"
  #    )
  #    test_pos.write(posFileContent)
  #    test_pos.close()
  #    self.assertEqual(databaseDump.getPBOFormatVersion(os.path.join(d.path,"test.pos")),"1.1.0")
  #
  #def test_saveEstimatedCoordinatesToFile(self):
  #  cfg          = Config("config/appconf.cfg")
  #  logger       = Logs("logs/logsTest.log",1000)
  #  pgConnection = DBConnection("localhost",5432,"PP-products","postgres","postgres",logger)
  #  pgConnection.connect()
  #  fileHandler = FileHandler(
  #    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
  #    fromEmail         = "arroz123",
  #    fromEmailPassword = "arroz123"
  #  )
  #  databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
  #  with TempDirectory() as d:
  #    test_pos = open(os.path.join(d.path,"test.pos"),"w")
  #    posFileContent = (
  #      "PBO Station Position Time Series. Reference Frame : IGS14\n"
  #      "Format Version: 1.1.0\n"
  #      "4-character ID: ACOR\n"
  #      "Station name  : ACOR\n"
  #      "First Epoch   : 20000101 120000\n"
  #      "Last Epoch    : 20221231 120000\n"
  #      "Release Date  : 20230201 090806\n"
  #      "XYZ Reference position :    4594489.63752  -678367.62227  4357066.20414 (IGS14)\n"
  #      "NEU Reference position :     43.3643846386  351.6010688682   66.90070 (IGS14/WGS84)\n"
  #      "%Begin EPOS metadata\n"
  #      "9-character ID: ACOR00ESP\n"
  #      "AnalysisCentre: INGV\n"
  #      "Software      : GIPSY 6.3\n"
  #      "Method-url    : https://gnssproducts.epos.ubi.pt/methods/INGV_TS.pdf\n"
  #      "DOI           : not_specified\n"
  #      "ReleaseVersion: 2023.1\n"
  #      "SamplingPeriod: daily\n"
  #      "CreationDate  : 2023-02-03 18:00:00\n"
  #      "%End EPOS metadata\n"
  #      "*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y             Z            Sx        Sy       Sz     Rxy    Rxz    Ryz           NLat         Elong         Height         dN        dE        dU         Sn       Se       Su      Rne    Rnu    Reu  Soln\n"
  #      "20000101 120000 51544.5000  4594489.76148  -678367.89073  4357066.08151  0.00226  0.00072  0.00204 -0.324  0.838 -0.285      43.3643828359  351.6010658151   66.93416    -0.20017  -0.24748   0.03413    0.00087  0.00068  0.00292  0.001 -0.102  0.109 final\n"
  #      "20000102 120000 51545.5000  4594489.76474  -678367.89143  4357066.08379  0.00211  0.00068  0.00190 -0.308  0.821 -0.277      43.3643828303  351.6010658125   66.93815    -0.20078  -0.24769   0.03812    0.00085  0.00065  0.00272 -0.021 -0.097  0.110 final\n"
  #      "20000103 120000 51546.5000  4594489.76309  -678367.89125  4357066.08328  0.00208  0.00069  0.00184 -0.345  0.821 -0.344      43.3643828371  351.6010658117   66.93659    -0.20003  -0.24776   0.03656    0.00083  0.00065  0.00266 -0.067 -0.136  0.043 final\n"
  #      "20000104 120000 51547.5000  4594489.76964  -678367.89181  4357066.09010  0.00222  0.00071  0.00196 -0.350  0.825 -0.304      43.3643828412  351.6010658167   66.94604    -0.19954  -0.24735   0.04601    0.00088  0.00066  0.00284  0.003 -0.134  0.081 final\n"
  #      "20000105 120000 51548.5000  4594489.76749  -678367.89057  4357066.08665  0.00224  0.00073  0.00199 -0.348  0.834 -0.317      43.3643828329  351.6010658279   66.94199    -0.20048  -0.24644   0.04197    0.00087  0.00068  0.00288 -0.012 -0.135  0.068 final\n"
  #      "20000106 120000 51549.5000  4594489.76376  -678367.89161  4357066.08285  0.00212  0.00069  0.00185 -0.327  0.815 -0.303      43.3643828300  351.6010658085   66.93681    -0.20082  -0.24801   0.03679    0.00086  0.00065  0.00269 -0.038 -0.153  0.083 final\n"
  #      "20000107 120000 51550.5000  4594489.76389  -678367.89184  4357066.08661  0.00226  0.00074  0.00198 -0.344  0.835 -0.301      43.3643828536  351.6010658060   66.93951    -0.19819  -0.24822   0.03948    0.00087  0.00069  0.00289  0.010 -0.154  0.079 final\n"
  #    )
  #    test_pos.write(posFileContent)
  #    test_pos.close()
  #    databaseDump.saveEstimatedCoordinatesToFile(os.path.join(d.path,"test.pos"),1,2)
  #    with open("tmp/estimatedCoordinatesTemp.csv","r") as f:
  #      self.assertEqual(f.readlines()[0],"568,4594489.76148,-678367.89073,4357066.08151,0.00226,0.00072,0.00204,-0.324,0.838,-0.285,0,2000-01-01 12:00:00,final,1,2\n")
  #    os.remove("tmp/estimatedCoordinatesTemp.csv")
  #
  
  #def test_upload_timeseries_files(self):
  #  cfg          = Config("config/appconf.cfg")
  #  logger       = Logs("logs/logsTest.log",1000)
  #  pgConnection = DBConnection("localhost",5432,"PP-products","postgres","postgres",logger)
  #  pgConnection.connect()
  #  fileHandler = FileHandler(
  #    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
  #    fromEmail         = "arroz123",
  #    fromEmailPassword = "arroz123"
  #  )
  #  databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  databaseDump.uploadTimeseriesFile("path/timeseriesFile",1.0)
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
    
if __name__ == '__main__':
  unittest.main()