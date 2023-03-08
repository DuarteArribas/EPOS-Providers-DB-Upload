import psycopg2
import shutil
import glob
import gzip
import sys
import os
from src.utils.constants import *
from src.utils.logs      import *

class DatabaseUpload:
  """Upload time series to the database."""
  
  # == Class variables ==
  SOLUTION_TMP    = "solutionTmp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,logger,cfg,tmp):
    """Initialize needed variables for a time series database upload.

    Parameters
    ----------
    conn   : Connection
      A connection object to the database
    cursor : Cursor
      A cursor object to the database
    logger : Logs
      A logging object to which logs can be written
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
  
  def uploadAllTS(self,bucketDir):
    dataType = self.cfg.getUploadConfig("TS_DATATYPE")
    allTSFiles = self._getListOfTSFiles(bucketDir)
    if len(allTSFiles) == 0:
      return
    self._handlePreviousSolution(os.path.basename(bucketDir),dataType)
    solutionParameters = self._getSolutionParameters(allTSFiles[0])
    self._handleReferenceFrame(solutionParameters["reference_frame"],"2021-11-11") # TODO: add correct epoch
    self._uploadSolution(dataType,solutionParameters)
    for file in allTSFiles:
      self._uploadTimeseriesFiles(file,self._getPosFormatVersion(file))
    # TODO: upload estimated_corr
  #  for tsFile in allTSFiles:
  #    self._saveInformationToFile(tsFile)
  #  try:
  #    self._uploadTSOptimized()
  #  except:
  #    for tsFile in allTSFiles:
  #      self._uploadTS(tsFile)
  #
  
  def _getListOfTSFiles(self,bucketDir):
    return [file for file in os.listdir(bucketDir) if os.path.splitext(file)[1].lower() == ".pos"]
  
  def _handlePreviousSolution(self,ac,dataType):
    solutionIDInDB = self._checkSolutionAlreadyInDB(ac,dataType)
    if(len(solutionIDInDB) > 0):
      for solutionID in solutionIDInDB:
        if dataType == self.cfg.getUploadConfig("TS_DATATYPE"):
          timeseriesFilesIDInDB = self._getTimeseriesFilesID(solutionID)
          for timeseriesFileID in timeseriesFilesIDInDB:
            self._erasePreviousTimeseriesFilesFromDB(timeseriesFileID)
        elif dataType == self.cfg.getUploadConfig("VEL_DATATYPE"):
          pass
      self._erasePreviousSolutionFromDB(ac,dataType)
  
  def _checkSolutionAlreadyInDB(self,ac,dataType):
    self.cursor.execute("SELECT id FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,dataType))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousSolutionFromDB(self,ac,dataType):
    self.cursor.execute("DELETE FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,dataType))
  
  def _getTimeseriesFilesID(self,solutionID):
    self.cursor.execute("SELECT id_timeseries_files FROM estimated_coordinates WHERE id_solution = %s GROUP BY id_timeseries_files;",(solutionID,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousTimeseriesFilesFromDB(self,timeseriesFilesID):
    self.cursor.execute("DELETE FROM timeseries_files WHERE id = %s;",(timeseriesFilesID,))
  
  def _uploadSolution(self,dataType,solutionParameters):
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
        )
        """
      )
    except Exception as err:
      raise Exception(err)
    finally:
      pass
  
  def _getSolutionParameters(self,posFile):
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
      
  def _handleReferenceFrame(self,referenceFrame,epoch):
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
  
  def _uploadTimeseriesFiles(self,posFile,posFormatVersion):
    try:
      self.cursor.execute(
        f"""
        INSERT INTO timeseries_files(
          url,
          version,
          file_type
        )
        VALUES(
          'public/{posFile.split("/")[-3:]}',
          '{posFormatVersion}',
          'pos'
        )
        """
      )
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
            return int(value)
            
#  def _saveSolutionToFile(self,tsFile):
#    """Save the information of the solution of a time series file to a file.
#
#    Parameters
#    ----------
#    tsFile : str
#      The file that contains the solution
#    """
#    solutionParameters = self._getSolutionParameters(tsFile)
#    with open(os.path.join(self.tmpDir,TSDatabaseUpload.SOLUTION_TMP),"a") as tmp:
#      tmp.write(
#        str(solutionParameters["solution_type"])   + "," +
#        str(solutionParameters["ac_acronym"])      + "," +
#        str(solutionParameters["creation_date"])   + "," +
#        str(solutionParameters["software"])        + "," +
#        str(solutionParameters["doi"])             + "," +
#        str(solutionParameters["url"])             + "," +
#        str(solutionParameters["ac_name"])         + "," +
#        str(solutionParameters["version"])         + "," +
#        str(solutionParameters["reference_frame"]) + "," +
#        str(solutionParameters["sampling_period"]) + "\n"
#      )
#    
#  
#    

#  def _uploadSolutionOptimized(self):
#    """Bulk insert the time series files solutions to the database based on the saved information."""
#    self.logger.writeSubsubroutineLog(uploadSolutionOpt,Logs.ROUTINE_STATUS.START)
#    try:
#      with open(os.path.join(self.tmpDir,TSDatabaseUpload.SOLUTION_TMP),"r") as csvFile:
#        self.cursor.copy_expert(
#          f"""
#          COPY solution(
#            solution_type,
#            ac_acronym,
#            creation_date,
#            software,
#            doi,
#            url,
#            ac_name,
#            version,
#            reference_frame,
#            sampling_period
#          )
#          FROM STDIN
#          WITH (FORMAT CSV,HEADER FALSE);
#          """,
#          csvFile
#        )
#    except Exception as err:
#      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadAllError.format(uploadType = "solutions",errMsg = str(err).replace("\n","---")))
#      raise Exception(err)
#    finally:
#      self.logger.writeSubsubroutineLog(uploadSolutionOpt,Logs.ROUTINE_STATUS.END)