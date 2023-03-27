import os
from src.utils.constants import *
from src.utils.logs      import *
from src.uploadError     import *

class DatabaseUpload:
  """Upload data to the database."""
  
  # == Class variables ==
  ESTIMATED_COORDINATES_TEMP = "estimatedCoordinatesTemp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,logger,cfg,tmp):
    """Initialize needed variables for a database upload.

    Parameters
    ----------
    conn   : Connection
      A connection object to the database
    cursor : Cursor
      A cursor object to the database
    logger : Logs
      A logging object to which logs can be written
    cfg    : Config
      A configuration object to which configuration parameters can be read
    tmp    : str
      A directory to which temporary files used for bulk database insertion (optimization) will be saved to
    """
    self.conn   = conn
    self.cursor = cursor
    self.logger = logger
    self.cfg    = cfg
    self.tmpDir = tmp + "/" if tmp[-1] != "/" else tmp
    if not os.path.exists(self.tmpDir):
      os.makedirs(self.tmpDir)
  
  def getListOfTSFiles(self,bucketDir):
    """Get a list of all timeseries files in a directory.
    
    Parameters
    ----------
    bucketDir : str
      The bucket directory to search for timeseries files
      
    Returns
    -------
    list
      A list of all timeseries files in the directory
    """
    return [file for file in os.listdir(bucketDir) if os.path.splitext(file)[1].lower() == ".pos"]
  
  def handlePreviousSolution(self,ac,dataType):
    solutionIDInDB = self.checkSolutionAlreadyInDB(ac,dataType)
    if(len(solutionIDInDB) > 0):
      for solutionID in solutionIDInDB:
        if dataType == self.cfg.getUploadConfig("TS_DATATYPE"):
          timeseriesFilesIDInDB = self._getTimeseriesFilesID(solutionID)
          for timeseriesFileID in timeseriesFilesIDInDB:
            self._erasePreviousTimeseriesFilesFromDB(timeseriesFileID)
        elif dataType == self.cfg.getUploadConfig("VEL_DATATYPE"):
          pass
      self._erasePreviousSolutionFromDB(ac,dataType)
  
  def checkSolutionAlreadyInDB(self,ac,dataType):
    """Check if a solution is already in the database.
    
    Parameters
    ----------
    ac       : str
      The analysis centre acronym
    dataType : str
      The data type of the solution (timeseries or velocity)
    
    Returns
    -------
    list
      A list of solution IDs if the solution is already in the database or an empty list otherwise
    """
    self.cursor.execute("SELECT id FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,dataType))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousSolutionFromDB(self,ac,dataType):
    self.cursor.execute("DELETE FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,dataType))
  
  def _getTimeseriesFilesID(self,solutionID):
    self.cursor.execute("SELECT id_timeseries_files FROM estimated_coordinates WHERE id_solution = %s GROUP BY id_timeseries_files;",(solutionID,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousTimeseriesFilesFromDB(self,timeseriesFilesID):
    self.cursor.execute("DELETE FROM timeseries_files WHERE id = %s;",(timeseriesFilesID,))
  
  def uploadSolution(self,dataType,solutionParameters):
    """Upload a solution to the database.
    
    Parameters
    ----------
    dataType           : str
      The data type of the solution (timeseries or velocity)
      
    solutionParameters : dict
      The solution parameters
        
    Raises
    ------
    UploadError
      If the solution could not be uploaded to the database
    """
    try:
      self.cursor.execute(
        f"""
        INSERT INTO solution(
          creation_date,
          release_version,
          data_type,
          sampling_period,
          software,
          doi,
          processing_parameters_url,
          ac_acronym,
          reference_frame
        )
        VALUES(
          '{solutionParameters["creation_date"]}',
          '{solutionParameters["release_version"]}',
          '{dataType}',
          '{solutionParameters["sampling_period"]}',
          '{solutionParameters["software"]}',
          '{solutionParameters["doi"]}',
          '{solutionParameters["processing_parameters_url"]}',
          '{solutionParameters["ac_acronym"]}',
          '{solutionParameters["reference_frame"]}'
        );
        """
      )
    except Exception as err:
      raise UploadError(f"Could not upload solution to database. Error: {UploadError.formatError(err)}.")
  
  def getSolutionParameters(self,posFile):
    with open(posFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      solutionParameters = {"reference_frame" : f"{lines[0].split(':')[1].strip()}"}
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["AnalysisCentre",*values]:
            value = " ".join(values)
            solutionParameters["ac_acronym"] = value
          case ["Software",*values]:
            value = " ".join(values)
            solutionParameters["software"] = value
          case ["Method-url",*values]:
            value = " ".join(values)
            solutionParameters["processing_parameters_url"] = value
          case ["DOI",*values]:
            value = " ".join(values)
            solutionParameters["doi"] = value
          case ["CreationDate",*values]:
            value = " ".join(values)
            solutionParameters["creation_date"] = value
            solutionParameters["creation_date"] = solutionParameters["creation_date"].replace("/","-")
          case ["ReleaseVersion",*values]:
            value = " ".join(values)
            solutionParameters["release_version"] = value
          case ["SamplingPeriod",*values]:
            value = " ".join(values)
            solutionParameters["sampling_period"] = value
          case ["ReferenceFrame",*values]:
            value = " ".join(values)
            solutionParameters["reference_frame"] = value
      return solutionParameters
      
  def handleReferenceFrame(self,referenceFrame,epoch):
    if len(self._checkReferenceFrameInDB(referenceFrame)) == 0:
      self._uploadReferenceFrame(referenceFrame,epoch)
  
  def _checkReferenceFrameInDB(self,referenceFrame):
    self.cursor.execute("SELECT name FROM reference_frame WHERE name = %s;",(referenceFrame,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _uploadReferenceFrame(self,name,epoch):
    try:
      self.cursor.execute(f"INSERT INTO reference_frame(name,epoch)VALUES('{name}','{epoch}')")
    except Exception as err:
      raise Exception(err)
    finally:
      pass
  
  def uploadTimeseriesFile(self,posFile,posFormatVersion):
    try:
      self.cursor.execute(
        f"""
        INSERT INTO timeseries_files(
          url,
          version,
          file_type
        )
        VALUES(
          'public/{"/".join(posFile.split("/")[-3:])}',
          '{posFormatVersion}',
          'pos'
        )
        RETURNING id;
        """
      )
      return [item[0] for item in self.cursor.fetchall()]
    except Exception as err:
      raise Exception(err)
    finally:
      pass
  
  def _getPosFormatVersion(self,posFile):
    with open(posFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      for line in lines:
        match [part.strip() for part in line.split(":",1)]:
          case ["Format Version",*values]:
            value = " ".join(values)
            return value
            
  def saveEstimatedCoordinatesToFile(self,posFile,idSolution,idTimeseriesFiles):
    with open(posFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      stationName = None
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["9-character ID",*values]:
            stationName = " ".join(values)
      station = self._getStationID(stationName)[0]
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [YYYYMMDD,HHMMSS,JJJJJ_JJJJ,X,Y,Z,Sx,Sy,Sz,Rxy,Rxz,Ryz,NLat,Elong,Height,dN,dE,dU,Sn,Se,Su,Rne,Rnu,Reu,Soln] if YYYYMMDD[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"a") as tmp:
              tmp.write(
                str(station)               + "," +
                str(X)                     + "," +
                str(Y)                     + "," +
                str(Z)                     + "," +
                str(Sx)                    + "," +
                str(Sy)                    + "," +
                str(Sz)                    + "," +
                str(Rxy)                   + "," +
                str(Rxz)                   + "," +
                str(Ryz)                   + "," +
                str(0)                     + "," + #TODO: Change outlier
                str("2021-11-11 00:00:00") + "," + #TODO: Change epoch
                str(Soln)                  + "," +
                str(idSolution)            + "," +
                str(idTimeseriesFiles)     + "\n"      
              )
  
  def _getStationID(self,stationName):
    self.cursor.execute("SELECT id FROM station WHERE marker = %s",(stationName,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def uploadEstimatedCoordinates(self):
    try:
      with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"r") as csvFile:
        self.cursor.copy_expert(
          f"""
          COPY estimated_coordinates(
            id_station,
            x,
            y,
            z,
            var_xx,
            var_yy,
            var_zz,
            var_xy,
            var_xz,
            var_yz,
            outlier,
            epoch,
            sol_type,
            id_solution,
            id_timeseries_files
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csvFile
        )
    except Exception as err:
      print(err)
      raise Exception(err)
    finally:
      pass
  
  def eraseEstimatedCoordinatesTmpFile(self):
    os.remove(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP))