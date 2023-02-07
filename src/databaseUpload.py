import psycopg2
import shutil
import glob
import gzip
import sys
import os
from src.utils.constants import *
from src.utils.logs      import *

class TSDatabaseUpload:
  """Upload TS solutions to the database."""
  
  # == Class variables ==
  ANALYSIS_CENTRE = {"INGV":"ING","UGA-CNRS":"UGA","WUT-EUREF":"EUR","ROB-EUREF":"ROB","SGO-EPND":"SGO"}
  SOLUTION_TMP    = "solutionTmp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,logger,tmp):
    self.conn   = conn
    self.cursor = cursor
    self.logger = logger
    self.tmpDir = tmp + "/" if tmp[-1] != "/" else tmp
    if not os.path.exists(self.tmpDir):
      os.makedirs(self.tmpDir)
  
  def uploadAllTS(self,publicDir):
    allTSFiles = self._getListOfTSFiles(publicDir)
    for tsFile in allTSFiles:
      self._saveInformationToFile(tsFile)
    try:
      self._uploadTSOptimized()
    except:
      for tsFile in allTSFiles:
        self._uploadTS(tsFile)
  
  def _getListOfTSFiles(self,publicDir):
    return [file for file in glob.glob(f"{publicDir}/**/*",recursive = True) if not os.path.isdir(file) and file.split("/")[-2] == "TS"]
  
  def _saveInformationToFile(self,tsFile):
    self._saveSolutionToFile(tsFile)
    # TODO: Save the rest
  
  def _saveSolutionToFile(self,tsFile):
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
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolutionOptimized()
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
      self._removeFilesInDir(self.tmpDir)
    except Exception as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      self._removeFilesInDir(self.tmpDir)
      raise Exception(err)
  
  def _removeFilesInDir(self,dir):
    files = glob.glob(f"{dir}/*")
    for f in files:
      os.remove(f)
  
  def _uploadSolutionOptimized(self):
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
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadAllError.format(uploadType = "solution",errMsg = str(err)))
      raise Exception(err)
  
  def _uploadTS(self,file):
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolution(self._getSolutionParameters(file),file)
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
    except:
      self.cursor.execute("ROLLBACK TRANSACTION")
  
  def _uploadSolution(self,solutionParameters,filename):
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
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadError.format(file = filename,uploadType = "solution",errMsg = str(err)))
      raise Exception(err)