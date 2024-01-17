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
  
  def test_formatDate(self):
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
    self.assertEqual(databaseDump._formatDate("20231005","103000"),"2023-10-05 10:30:00")
  
  def test_saveEstimatedCoordinatesToFile(self):
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
        "*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y             Z            Sx        Sy       Sz     Rxy    Rxz    Ryz           NLat         Elong         Height         dN        dE        dU         Sn       Se       Su      Rne    Rnu    Reu  Soln\n"
        "20000101 120000 51544.5000  4594489.76148  -678367.89073  4357066.08151  0.00226  0.00072  0.00204 -0.324  0.838 -0.285      43.3643828359  351.6010658151   66.93416    -0.20017  -0.24748   0.03413    0.00087  0.00068  0.00292  0.001 -0.102  0.109 final\n"
        "20000102 120000 51545.5000  4594489.76474  -678367.89143  4357066.08379  0.00211  0.00068  0.00190 -0.308  0.821 -0.277      43.3643828303  351.6010658125   66.93815    -0.20078  -0.24769   0.03812    0.00085  0.00065  0.00272 -0.021 -0.097  0.110 final\n"
        "20000103 120000 51546.5000  4594489.76309  -678367.89125  4357066.08328  0.00208  0.00069  0.00184 -0.345  0.821 -0.344      43.3643828371  351.6010658117   66.93659    -0.20003  -0.24776   0.03656    0.00083  0.00065  0.00266 -0.067 -0.136  0.043 final\n"
        "20000104 120000 51547.5000  4594489.76964  -678367.89181  4357066.09010  0.00222  0.00071  0.00196 -0.350  0.825 -0.304      43.3643828412  351.6010658167   66.94604    -0.19954  -0.24735   0.04601    0.00088  0.00066  0.00284  0.003 -0.134  0.081 final\n"
        "20000105 120000 51548.5000  4594489.76749  -678367.89057  4357066.08665  0.00224  0.00073  0.00199 -0.348  0.834 -0.317      43.3643828329  351.6010658279   66.94199    -0.20048  -0.24644   0.04197    0.00087  0.00068  0.00288 -0.012 -0.135  0.068 final\n"
        "20000106 120000 51549.5000  4594489.76376  -678367.89161  4357066.08285  0.00212  0.00069  0.00185 -0.327  0.815 -0.303      43.3643828300  351.6010658085   66.93681    -0.20082  -0.24801   0.03679    0.00086  0.00065  0.00269 -0.038 -0.153  0.083 final\n"
        "20000107 120000 51550.5000  4594489.76389  -678367.89184  4357066.08661  0.00226  0.00074  0.00198 -0.344  0.835 -0.301      43.3643828536  351.6010658060   66.93951    -0.19819  -0.24822   0.03948    0.00087  0.00069  0.00289  0.010 -0.154  0.079 final\n"
      )
      test_pos.write(posFileContent)
      test_pos.close()
      databaseDump.saveEstimatedCoordinatesToFile(os.path.join(d.path,"test.pos"),1,"test.pos")
      with open("tmp/estimatedCoordinatesTemp.csv","r") as f:
        self.assertEqual(f.readlines()[0],"ACOR00ESP,4594489.76148,-678367.89073,4357066.08151,0.00226,0.00072,0.00204,-0.324,0.838,-0.285,0,2000-01-01 12:00:00,final,1,test.pos\n")
      os.remove("tmp/estimatedCoordinatesTemp.csv")
    
  #def test_uploadEstimatedCoordinates(self):
  #  cfg          = Config("config/appconf.cfg")
  #  logger       = Logs("logs/logsTest.log",1000)
  #  pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
  #  pgConnection.connect()
  #  fileHandler = FileHandler(
  #    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
  #    fromEmail         = "arroz123",
  #    fromEmailPassword = "arroz123"
  #  )
  #  databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST5/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  solutionID = databaseDump.checkSolutionAlreadyInDB("INGV","timeseries")[0]
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
  #    databaseDump.saveEstimatedCoordinatesToFile(os.path.join(d.path,"test.pos"),solutionID,"test.pos")
  #    databaseDump.uploadEstimatedCoordinates()
  #    pgConnection.cursor.execute("COMMIT TRANSACTION;")
  #    databaseDump.eraseEstimatedCoordinatesTmpFile()
  
  def test_getUpdatedAndNewLines(self):
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
    self.assertEqual(
      databaseDump._getUpdatedAndNewLines(
        ["20221222 120000 59935.5000  4650653.87675  1328492.15977  4145013.35121  0.00191  0.00084  0.00162  0.629  0.812  0.597      40.7866593286   15.9423650461  764.69430     0.15500   0.19439   0.00444    0.00076  0.00063  0.00245  0.038 -0.135  0.076 final","20221223 120000 59936.5000  4650653.87609  1328492.16003  4145013.34922  0.00189  0.00082  0.00160  0.617  0.804  0.590      40.7866593183   15.9423650512  764.69257     0.15385   0.19482   0.00272    0.00077  0.00062  0.00242  0.056 -0.132  0.061 final","20221224 120000 59937.5000  4650653.87869  1328492.15960  4145013.35133  0.00186  0.00081  0.00157  0.614  0.806  0.582      40.7866593187   15.9423650378  764.69576     0.15391   0.19369   0.00590    0.00075  0.00062  0.00238  0.043 -0.139  0.056 final","20221225 120000 59938.5000  4650653.87448  1328492.15593  4145013.34808  0.00185  0.00081  0.00157  0.619  0.804  0.585      40.7866593262   15.9423650097  764.68981     0.15473   0.19132  -0.00005    0.00075  0.00062  0.00237  0.038 -0.136  0.068 final","20221226 120000 59939.5000  4650653.87528  1328492.15783  4145013.35005  0.00188  0.00083  0.00163  0.626  0.808  0.597      40.7866593321   15.9423650288  764.69208     0.15539   0.19293   0.00221    0.00077  0.00062  0.00244  0.049 -0.098  0.077 final","20221227 120000 59940.5000  4650653.87863  1328492.16046  4145013.35312  0.00192  0.00085  0.00167  0.608  0.807  0.594      40.7866593298   15.9423650478  764.69706     0.15515   0.19453   0.00719    0.00078  0.00065  0.00248  0.073 -0.095  0.069 final","20221228 120000 59941.5000  4650653.87766  1328492.15763  4145013.35139  0.00201  0.00089  0.00176  0.617  0.814  0.605      40.7866593281   15.9423650188  764.69464     0.15495   0.19208   0.00478    0.00080  0.00067  0.00261  0.072 -0.087  0.078 final","20221229 120000 59942.5000  4650653.87434  1328492.15970  4145013.35085  0.00188  0.00083  0.00160  0.619  0.807  0.590      40.7866593399   15.9423650531  764.69230     0.15625   0.19498   0.00244    0.00076  0.00063  0.00242  0.046 -0.130  0.071 final","20221230 120000 59943.5000  4650653.87673  1328492.15977  4145013.35387  0.00186  0.00081  0.00159  0.619  0.805  0.586      40.7866593468   15.9423650462  764.69603     0.15703   0.19439   0.00616    0.00076  0.00062  0.00238  0.042 -0.123  0.063 final","20221231 120000 59944.5000  4650653.87658  1328492.15766  4145013.34994  0.00191  0.00084  0.00162  0.626  0.811  0.588      40.7866593243   15.9423650226  764.69290     0.15452   0.19241   0.00304    0.00077  0.00063  0.00245  0.027 -0.131  0.066 final"],
        ["20221225 120000 59938.5000  5650653.87448  2328492.15593  3145013.34808  0.00185  0.00081  0.00157  0.619  0.804  0.585      40.7866593262   15.9423650097  764.68981     0.15473   0.19132  -0.00005    0.00075  0.00062  0.00237  0.038 -0.136  0.068 final","20221229 120000 59942.5000  1650653.87434  5328492.15970  2145013.35085  0.00188  0.00083  0.00160  0.619  0.807  0.590      40.7866593399   15.9423650531  764.69230     0.15625   0.19498   0.00244    0.00076  0.00063  0.00242  0.046 -0.130  0.071 final","20221208 120000 59921.5000  4650653.87835  1328492.15705  4145013.35107  0.00192  0.00083  0.00162  0.614  0.808  0.573      40.7866593229   15.9423650100  764.69481     0.15438   0.19134   0.00495    0.00077  0.00063  0.00245  0.026 -0.139  0.043 final","20221209 120000 59922.5000  4650653.88960  1328492.15790  4145013.35569  0.00199  0.00087  0.00169  0.636  0.815  0.596      40.7866592894   15.9423649830  764.70620     0.15069   0.18906   0.01635    0.00079  0.00064  0.00255  0.021 -0.141  0.071 final"]
      ),
      (
        [["20221225","120000","59938.5000","5650653.87448","2328492.15593","3145013.34808","0.00185","0.00081","0.00157","0.619","0.804","0.585","40.7866593262","15.9423650097","764.68981","0.15473","0.19132","-0.00005","0.00075","0.00062","0.00237","0.038","-0.136","0.068","final"],["20221229","120000","59942.5000","1650653.87434","5328492.15970","2145013.35085","0.00188","0.00083","0.00160","0.619","0.807","0.590","40.7866593399","15.9423650531","764.69230","0.15625","0.19498","0.00244","0.00076","0.00063","0.00242","0.046","-0.130","0.071","final"]],
        [["20221208","120000","59921.5000","4650653.87835","1328492.15705","4145013.35107","0.00192","0.00083","0.00162","0.614","0.808","0.573","40.7866593229","15.9423650100","764.69481","0.15438","0.19134","0.00495","0.00077","0.00063","0.00245","0.026","-0.139","0.043","final"],["20221209","120000","59922.5000","4650653.88960","1328492.15790","4145013.35569","0.00199","0.00087","0.00169","0.636","0.815","0.596","40.7866592894","15.9423649830","764.70620","0.15069","0.18906","0.01635","0.00079","0.00064","0.00255","0.021","-0.141","0.071","final"]]
      )
    )
    
  #def test_updateEstimatedCoordinates(self):
  #  cfg          = Config("config/appconf.cfg")
  #  logger       = Logs("logs/logsTest.log",1000)
  #  pgConnection = DBConnection("localhost",5432,"db305","postgres","postgres",logger)
  #  pgConnection.connect()
  #  fileHandler = FileHandler(
  #    providersDir      = cfg.getAppConfig("PROVIDERS_DIR"),
  #    fromEmail         = "arroz123",
  #    fromEmailPassword = "arroz123"
  #  )
  #  databaseDump = DatabaseUpload(pgConnection.conn,pgConnection.cursor,logger,cfg,"tmp",fileHandler)
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  databaseDump.uploadSolution("timeseries",{"reference_frame" : "IGS14", "ac_acronym" : "INGV","software" : "GIPSY 6.3","processing_parameters_url" : "https://gnssproducts.epos.ubi.pt/TEST5/INGV_TS.pdf","doi" : "not_specified","release_version" : "2023.1","sampling_period" : "daily","creation_date" : "2023-02-03 18:00:00"})
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  solutionID = databaseDump.checkSolutionAlreadyInDB("INGV","timeseries")[0]
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
  #    databaseDump.saveEstimatedCoordinatesToFile(os.path.join(d.path,"test.pos"),solutionID,"test.pos")
  #    databaseDump.uploadEstimatedCoordinates()
  #    pgConnection.cursor.execute("COMMIT TRANSACTION;")
  #    databaseDump.eraseEstimatedCoordinatesTmpFile()
  #  pgConnection.cursor.execute("START TRANSACTION;")
  #  databaseDump.updateEstimatedCoordinates(["20000101","120000","59938.5000","5650653.87448","2328492.15593","3145013.34808","0.00185","0.00081","0.00157","0.619","0.804","0.585","40.7866593262","15.9423650097","764.68981","0.15473","0.19132","-0.00005","0.00075","0.00062","0.00237","0.038","-0.136","0.068","final"])
  #  pgConnection.cursor.execute("COMMIT TRANSACTION;")
    
if __name__ == '__main__':
  unittest.main()