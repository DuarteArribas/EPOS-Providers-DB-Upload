import psycopg2
import glob
import sys
import os
from src.utils.constants import *
from src.utils.logs      import *

class TSDatabaseUpload:
  """Upload TS solutions to the database."""
  
  # == Methods ==
  def __init__(self,conn,cursor,logger):
    self.conn   = conn
    self.cursor = cursor
    self.logger = logger
  
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
    
  def _uploadTSOptimized(self):
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolutionOptimized()
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
    except Exception as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise Exception(err)
  
  def _uploadSolutionOptimized(
    self,
    solutionFile
  ):
    try:
      with open(solutionFile,"r") as csvFile:
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
            processing_parameters_url,
            sampling_period
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER TRUE);
          """,
          csvFile
        )
    except Exception as err:
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadAllError.format(uploadType = "solution",errMsg = str(err)))
      raise Exception(err)
  
  def _uploadTS(self,file):
    try:
      self.cursor.execute("BEGIN TRANSACTION")
      self._uploadSolution()
      # TODO: Upload more
      self.cursor.execute("COMMIT TRANSACTION")
    except:
      self.cursor.execute("ROLLBACK TRANSACTION")
  
  def _uploadSolution(
    self,
    solution_type,
    ac_acronym,
    creation_date,
    software,
    doi,
    url,
    ac_name,
    version,
    reference_frame,
    processing_parameters_url,
    sampling_period,
    filename
  ):
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
          processing_parameters_url,
          sampling_period
        )
        VALUES(
          '{solution_type}',
          '{ac_acronym}',
          '{creation_date}',
          '{software}',
          '{doi}',
          '{url}',
          '{ac_name}',
          '{version}',
          '{reference_frame}',
          '{processing_parameters_url}',
          '{sampling_period}'
        )
        """
      )
    except Exception as err:
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbUploadError.format(file = filename,uploadType = "solution",errMsg = str(err)))
      raise Exception(err)