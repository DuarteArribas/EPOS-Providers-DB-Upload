import psycopg2
import shutil
import glob
import gzip
import sys
import os
from src.utils.constants import *
from src.utils.logs      import *

class TSDatabaseUpload:
  """Upload time series to the database."""
  
  # == Class variables ==
  ANALYSIS_CENTRE = {"INGV":"ING","UGA-CNRS":"UGA","WUT-EUREF":"EUR","ROB-EUREF":"ROB","SGO-EPND":"SGO"}
  SOLUTION_TMP    = "solutionTmp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,logger,tmp):
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
    self.tmpDir = tmp + "/" if tmp[-1] != "/" else tmp
    if not os.path.exists(self.tmpDir):
      os.makedirs(self.tmpDir)
  
  def uploadAllTS(self,publicDir):
    """Upload all found time series files to the database. First, get the files to upload and save their information to temporary files.
    Then, try to bulk insert those files into the db (optimization). If it can't, upload them one by one.
    

    Parameters
    ----------
    publicDir : str
      The public directory to search the time series files
    """
    self.logger.writeNewRunLog("Uploading time series files to the database")
    allTSFiles = self._getListOfTSFiles(publicDir)
    for tsFile in allTSFiles:
      self._saveInformationToFile(tsFile)
    try:
      self._uploadTSOptimized()
    except:
      for tsFile in allTSFiles:
        self._uploadTS(tsFile)
  
  def _getListOfTSFiles(self,publicDir):
    """Get the list of time series files (pos or vel) found in the given directory.

    Parameters
    ----------
    publicDir : str
      The public directory to search the time series files

    Returns
    -------
    list[str]
      The list of time series files in the given directory
    """
    self.logger.writeRoutineLog(getTSFiles,Logs.ROUTINE_STATUS.START)
    files = [file for file in glob.glob(f"{publicDir}/**/*",recursive = True) if not os.path.isdir(file) and file.split("/")[-2] == "TS"]
    self.logger.writeRegularLog(Logs.SEVERITY.INFO,filesFound.format(files = files) if files else filesNotFound)
    self.logger.writeRoutineLog(getTSFiles,Logs.ROUTINE_STATUS.END)
    return [file for file in glob.glob(f"{publicDir}/**/*",recursive = True) if not os.path.isdir(file) and file.split("/")[-2] == "TS"]
  
  def _saveInformationToFile(self,tsFile):
    """Save the information (needed to upload a time series file) of a time series file to a file.

    Parameters
    ----------
    tsFile : str
      The file that contains the needed information
    """
    self.logger.writeRoutineLog(saveFiles,Logs.ROUTINE_STATUS.START)
    self._saveSolutionToFile(tsFile)
    # TODO: Save the rest
    self.logger.writeRoutineLog(saveFiles,Logs.ROUTINE_STATUS.END)
  
  def _saveSolutionToFile(self,tsFile):
    """Save the information of the solution of a time series file to a file.

    Parameters
    ----------
    tsFile : str
      The file that contains the solution
    """
    solutionParameters = self._getSolutionParameters(tsFile)
    with open(os.path.join(self.tmpDir,TSDatabaseUpload.SOLUTION_TMP),"a") as tmp:
      tmp.write(
        str(solutionParameters["solution_type"])   + "," +
        str(solutionParameters["ac_acronym"])      + "," +
        str(solutionParameters["creation_date"])   + "," +
        str(solutionParameters["software"])        + "," +
        str(solutionParameters["doi"])             + "," +
        str(solutionParameters["url"])             + "," +
        str(solutionParameters["ac_name"])         + "," +
        str(solutionParameters["version"])         + "," +
        str(solutionParameters["reference_frame"]) + "," +
        str(solutionParameters["sampling_period"]) + "\n"
      )
    
  def _getSolutionParameters(self,tsFile):
    """Get the solution information of a time series file.

    Parameters
    ----------
    tsFile : str
      The file that contains the solution

    Returns
    -------
    dict
      A dictionary containing the needed parameters. The keys match the database column names and the values are the respective values.
    """
    with gzip.open(tsFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      solutionParameters = {"solution_type":"TS"}
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [el.strip() for el in line.split(":",1)]:
          case ["ReferenceFrame",value]:
            solutionParameters["reference_frame"] = value
          case ["AnalysisCentre",value]:
            solutionParameters["ac_name"]    = value
            solutionParameters["ac_acronym"] = TSDatabaseUpload.ANALYSIS_CENTRE[value]
          case ["Software",value]:
            solutionParameters["software"] = value
          case ["Method-url",value]:
            solutionParameters["url"] = value
          case ["DOI",value]:
            solutionParameters["doi"] = value
          case ["ReleaseNumber",value]:
            solutionParameters["version"] = value
          case ["SamplingPeriod",value]:
            solutionParameters["sampling_period"] = value
          case ["CreationDate",value]:
            solutionParameters["creation_date"] = value
      return solutionParameters
    
  def _uploadTSOptimized(self):
    """Bulk insert the time series files information to the database based on the saved information.

    Raises
    ------
    Exception
      If an error occurred when inserting
    """
    self.logger.writeRoutineLog(uploadTSOpt,Logs.ROUTINE_STATUS.START)
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolutionOptimized()
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
      self.logger.writeRegularLog(Logs.SEVERITY.INFO,tmpFileDelete)
      self._removeFilesInDir(self.tmpDir)
    except Exception as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      self.logger.writeRegularLog(Logs.SEVERITY.INFO,tmpFileDelete)
      self._removeFilesInDir(self.tmpDir)
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbBulkUploadError)
      raise Exception(err)
    finally:
      self.logger.writeRoutineLog(uploadTSOpt,Logs.ROUTINE_STATUS.END)
  
  def _removeFilesInDir(self,dir):
    """Remove files in a dir.

    Parameters
    ----------
    dir : str
      The dir from which the files will be removed.
    """
    files = glob.glob(f"{dir}/*")
    for f in files:
      os.remove(f)
  
  def _uploadSolutionOptimized(self):
    """Bulk insert the time series files solutions to the database based on the saved information."""
    self.logger.writeSubroutineLog(uploadSolutionOpt,Logs.ROUTINE_STATUS.START)
    try:
      with open(os.path.join(self.tmpDir,TSDatabaseUpload.SOLUTION_TMP),"r") as csvFile:
        self.cursor.copy_expert(
          f"""
          COPY solution(
            solution_type,
            ac_acronym,
            creation_date,
            software,
            doi,
            url,
            ac_name,
            version,
            reference_frame,
            sampling_period
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csvFile
        )
    except Exception as err:
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadAllError.format(uploadType = "solutions",errMsg = str(err).replace("\n","---")))
      raise Exception(err)
    finally:
      self.logger.writeSubroutineLog(uploadSolutionOpt,Logs.ROUTINE_STATUS.END)
  
  def _uploadTS(self,file):
    """Insert a time series file to the database.

    Parameters
    ----------
    file : str
      The time series file to insert
    """
    self.logger.writeRoutineLog(uploadTS,Logs.ROUTINE_STATUS.START)
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolution(self._getSolutionParameters(file),file)
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
    except:
      self.cursor.execute("ROLLBACK TRANSACTION")
    finally:
      self.logger.writeRoutineLog(uploadTS,Logs.ROUTINE_STATUS.END)
  
  def _uploadSolution(self,solutionParameters,filename):
    """Insert a solution of a time series file to the database
    
    Parameters
    ----------
    solutionParameters : dict
      The solution information
    filename           : str
      The name of the time series file being inserted
    """
    self.logger.writeSubroutineLog(uploadSolution,Logs.ROUTINE_STATUS.START)
    try:
      self.cursor.execute(
        f"""
        INSERT INTO solution(
          solution_type,
          ac_acronym,
          creation_date,
          software,
          doi,
          url,
          ac_name,
          version,
          reference_frame,
          sampling_period
        )
        VALUES(
          '{solutionParameters["solution_type"]}',
          '{solutionParameters["ac_acronym"]}',
          '{solutionParameters["creation_date"]}',
          '{solutionParameters["software"]}',
          '{solutionParameters["doi"]}',
          '{solutionParameters["url"]}',
          '{solutionParameters["ac_name"]}',
          '{solutionParameters["version"]}',
          '{solutionParameters["reference_frame"]}',
          '{solutionParameters["sampling_period"]}'
        )
        """
      )
    except Exception as err:
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadError.format(file = filename,uploadType = "solution",errMsg = str(err).replace("\n","---")))
      raise Exception(err)
    finally:
      self.logger.writeSubroutineLog(uploadSolution,Logs.ROUTINE_STATUS.END)