import os
from src.utils.constants import *
from src.utils.logs      import *
from src.uploadError     import *

class DatabaseUpload:
  """Upload data to the database."""
  
  # == Class variables ==
  ESTIMATED_COORDINATES_TEMP         = "estimatedCoordinatesTemp.csv"
  REFERENCE_POSITION_VELOCITIES_TEMP = "referencePositionVelocitiesTemp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,logger,cfg,tmp,fileHandler):
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
    fileHandler : FileHandler
      A file handler object
    """
    self.conn   = conn
    self.cursor = cursor
    self.logger = logger
    self.cfg    = cfg
    self.tmpDir = tmp + "/" if tmp[-1] != "/" else tmp
    if not os.path.exists(self.tmpDir):
      os.makedirs(self.tmpDir)
    self.fileHandler = fileHandler
  
  def uploadAllProviderTS(self,provBucketDir,publicDir):
    """Upload all timeseries files from a provider bucket directory to the database.
    
    Parameters
    ----------
    provBucketDir : str
      The path to the provider bucket directory
    publicDir     : str
      The path to the provider's public directory
    
    Raises
    ------
    UploadError
      If the upload was unsuccessful
    """
    self.cursor.execute("START TRANSACTION;")
    try:
      ac       = os.path.basename(provBucketDir)
      dataType = self.cfg.getUploadConfig("TS_DATATYPE")
      for filetype in os.listdir(provBucketDir):
        if filetype == "TS":
          for version in os.listdir(os.path.join(provBucketDir,filetype)):
            currDir = os.path.join(os.path.join(provBucketDir,filetype),version)
            allTSFiles = self.getListOfTSFiles(currDir)
            if len(allTSFiles) == 0:
              break
            self.handlePreviousSolution(
              ac,
              dataType,
              self.cfg.getUploadConfig("TS_DATATYPE"),
              self.cfg.getUploadConfig("VEL_DATATYPE")
            )
            self.uploadSolution(dataType,self.getSolutionParametersTS(os.path.join(currDir,allTSFiles[0])))
            currentSolutionID = self.checkSolutionAlreadyInDB(ac,dataType)[0]
            for file in allTSFiles:
              currFile = os.path.join(currDir,file)
              timeseriesFileID = self.uploadTimeseriesFile(
                currFile,
                self.getPBOFormatVersion(currFile)
              )
              self.saveEstimatedCoordinatesToFile(
                currFile,
                currentSolutionID,
                timeseriesFileID
              )
            self.uploadEstimatedCoordinates()
            self.eraseEstimatedCoordinatesTmpFile()
            self.cursor.execute("COMMIT TRANSACTION;")
            self.fileHandler.moveSolutionToPublic(currDir,publicDir,"TS")
    except UploadError as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise UploadError(str(err))
  
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
  
  def handlePreviousSolution(self,ac,dataType,tsDatatype,velDatatype):
    """Handle a previous solution, i.e., if a previous solution exists, erase it from the database, along with its associated timeseries files and estimated coordinates.
    
    Parameters
    ----------
    ac          : str
      The analysis centre acronym
    dataType    : str
      The data type of the solution (timeseries or velocity)
    tsDatatype  : str
      The timeseries data type
    velDatatype : str
      The velocity data type
    """
    solutionIDInDB = self.checkSolutionAlreadyInDB(ac,dataType)
    if(len(solutionIDInDB) > 0):
      for solutionID in solutionIDInDB:
        if dataType == tsDatatype:
          timeseriesFilesIDInDB = self._getTimeseriesFilesID(solutionID)
          for timeseriesFileID in timeseriesFilesIDInDB:
            self._erasePreviousTimeseriesFilesFromDB(timeseriesFileID)
        elif dataType == velDatatype:
          velocityFilesInDB = self._getVelocityFilesID(solutionID)
          for velocityFileID in velocityFilesInDB:
            self._erasePreviousVelocityFilesFromDB(velocityFileID)
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
    """Erase a previous solution from the database.
    
    Parameters
    ----------
    ac       : str
      The analysis centre acronym
    dataType : str
      The data type of the solution (timeseries or velocity)
    """
    self.cursor.execute("DELETE FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,dataType))
  
  def _getTimeseriesFilesID(self,solutionID):
    """Get the timeseries files ID from the database.
    
    Parameters
    ----------
    solutionID : int
      The solution ID
    
    Returns
    -------
    list
      A list of timeseries files IDs
    """
    self.cursor.execute("SELECT id_timeseries_files FROM estimated_coordinates WHERE id_solution = %s GROUP BY id_timeseries_files;",(solutionID,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousTimeseriesFilesFromDB(self,timeseriesFilesID):
    """Erase a previous timeseries file from the database.
    
    Parameters
    ----------
    timeseriesFilesID : int
      The timeseries files ID to remove
    """
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
      raise UploadError(f"Could not upload solution to database. Error: {UploadError.formatError(str(err))}.")
  
  def getSolutionParametersTS(self,posFile):
    """Get the solution parameters from a POS file.
    
    Parameters
    ----------
    posFile : str
      The path to the POS file
    
    Returns
    -------
    dict
      The solution parameters
    """
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
      return solutionParameters
  
  def uploadTimeseriesFile(self,posFile,posFormatVersion):
    """Upload a time series file to the database.
    
    Parameters
    ----------
    posFile           : str
      The path to the time series file on the bucket directory
    posFormatVersion  : str
      The version of the POS format used
    
    Raises
    ------
    UploadError
      If the time series file could not be uploaded to the database
    
    Returns
    -------
    list
      A list, containing the ID of the uploaded time series file
    """
    try:
      self.cursor.execute(
        f"""
        INSERT INTO timeseries_files(
          url,
          version,
          file_type
        )
        VALUES(
          'public/{"/".join(posFile.split("/")[-4:])}', 
          '{posFormatVersion}',
          'pos'
        )
        RETURNING id;
        """
      )
      return [item[0] for item in self.cursor.fetchall()][0]
    except Exception as err:
      raise UploadError(f"Could not upload time series file to database. Error: {UploadError.formatError(str(err))}.")
  
  def getPBOFormatVersion(self,pboFile):
    """Get the version of the PBO format used. (e.g. 1.1.1)
    
    Parameters
    ----------
    pboFile : str
      The path to the PBO file
    """
    with open(pboFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      for line in lines:
        match [part.strip() for part in line.split(":",1)]:
          case ["Format Version",*values]:
            value = " ".join(values)
            return value
            
  def saveEstimatedCoordinatesToFile(self,posFile,idSolution,idTimeseriesFiles):
    """Save the estimated coordinates to a temporary file for bulk upload.
    
    Parameters
    ----------
    posFile           : str
      The path to the POS file
    idSolution        : int
      The ID of the solution
    idTimeseriesFiles : int
      The ID of the time series file
    """
    with open(posFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      stationName = None
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["9-character ID",*values]:
            stationName = " ".join(values)
      station = self._getStationID(stationName)
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [YYYYMMDD,HHMMSS,JJJJJ_JJJJ,X,Y,Z,Sx,Sy,Sz,Rxy,Rxz,Ryz,NLat,Elong,Height,dN,dE,dU,Sn,Se,Su,Rne,Rnu,Reu,Soln] if YYYYMMDD[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"a") as tmp:
              tmp.write(
                str(station)                           + "," +
                str(X)                                 + "," +
                str(Y)                                 + "," +
                str(Z)                                 + "," +
                str(Sx)                                + "," +
                str(Sy)                                + "," +
                str(Sz)                                + "," +
                str(Rxy)                               + "," +
                str(Rxz)                               + "," +
                str(Ryz)                               + "," +
                str(1 if Soln == "outlier" else 0)     + "," +
                str(self._formatDate(YYYYMMDD,HHMMSS)) + "," +
                str(Soln)                              + "," +
                str(idSolution)                        + "," +
                str(idTimeseriesFiles)                 + "\n"      
              )
  
  def _getStationID(self,stationName):
    """Get the ID of a station.
    
    Parameters
    ----------
    stationName : str
      The long marker name of the station
    
    Returns
    -------
    int
      The ID of the correspondent station
    """
    self.cursor.execute("SELECT id FROM station WHERE marker = %s",(stationName,))
    return [item[0] for item in self.cursor.fetchall()][0]
  
  def _formatDate(self,YYYYMMDD,HHMMSS):
    """Format a date in the format YYYYMMDD HHMMSS to YYYY-MM-DD HH:MM:SS.
    
    Parameters
    ----------
    YYYYMMDD  : str
      The date in the format YYYYMMDD
    HHMMSS    : str
      The time in the format HHMMSS
    
    Returns
    -------
    str
      The date in the format YYYY-MM-DD HH:MM:SS 
    """
    return f"{YYYYMMDD[0:4]}-{YYYYMMDD[4:6]}-{YYYYMMDD[6:8]} {HHMMSS[0:2]}:{HHMMSS[2:4]}:{HHMMSS[4:6]}"
  
  def uploadEstimatedCoordinates(self):
    """Bulk upload the estimated coordinates from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the estimated coordinates could not be uploaded to the database
    """
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
      raise UploadError(f"Could not upload estimated coordinates to database. Error: {UploadError.formatError(str(err))}.")
  
  def eraseEstimatedCoordinatesTmpFile(self):
    """Erase the temporary file containing the previous estimated coordinates."""
    tempPath = os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP)
    if os.path.exists(tempPath):
      os.remove(tempPath)
  
  def uploadAllProviderVel(self,provBucketDir,publicDir):
    """Upload all velocity files from a provider bucket directory to the database.
    
    Parameters
    ----------
    provBucketDir : str
      The path to the provider bucket directory
    publicDir     : str
      The path to the provider's public directory
    
    Raises
    ------
    UploadError
      If the upload was unsuccessful
    """
    self.cursor.execute("START TRANSACTION;")
    try:
      ac       = os.path.basename(provBucketDir)
      dataType = self.cfg.getUploadConfig("VEL_DATATYPE")
      for filetype in os.listdir(provBucketDir):
        if filetype == "VEL":
          for version in os.listdir(os.path.join(provBucketDir,filetype)):
            currDir = os.path.join(os.path.join(provBucketDir,filetype),version)
            allVelFiles = self.getListOfVelFiles(currDir)
            if len(allVelFiles) == 0:
              break
            self.handlePreviousSolution(
              ac,
              dataType,
              self.cfg.getUploadConfig("TS_DATATYPE"),
              self.cfg.getUploadConfig("VEL_DATATYPE")
            )
            self.uploadSolution(dataType,self.getSolutionParametersVel(os.path.join(currDir,allVelFiles[0])))
            currentSolutionID = self.checkSolutionAlreadyInDB(ac,dataType)[0]
            for file in allVelFiles:
              currFile = os.path.join(currDir,file)
              velocityFileID = self.uploadVelocityFile(
                currFile,
                self.getPBOFormatVersion(currFile)
              )
              self.saveEstimatedCoordinatesToFile(
                currFile,
                currentSolutionID,
                velocityFileID
              )
            self.uploadEstimatedCoordinates()
            self.eraseEstimatedCoordinatesTmpFile()
            self.cursor.execute("COMMIT TRANSACTION;")
            self.fileHandler.moveSolutionToPublic(currDir,publicDir,"Vel")
    except UploadError as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise UploadError(str(err))
  
  def getListOfVelFiles(self,bucketDir):
    """Get a list of all velocity files in a directory.
    
    Parameters
    ----------
    bucketDir : str
      The bucket directory to search for velocity files
      
    Returns
    -------
    list
      A list of all velocity files in the directory
    """
    return [file for file in os.listdir(bucketDir) if os.path.splitext(file)[1].lower() == ".vel"]
  
  def _getVelocityFilesID(self,solutionID):
    """Get the velocity files ID from the database.
    
    Parameters
    ----------
    solutionID : int
      The solution ID
    
    Returns
    -------
    list
      A list of velocity files IDs
    """
    self.cursor.execute("SELECT id_velocities_files FROM reference_position_velocities WHERE id_solution = %s GROUP BY id_velocities_files;",(solutionID,))
    return [item[0] for item in self.cursor.fetchall()]
  
  def _erasePreviousVelocityFilesFromDB(self,velocityFilesID):
    """Erase a previous velocity file from the database.
    
    Parameters
    ----------
    velocityFilesID : int
      The velocity files ID to remove
    """
    self.cursor.execute("DELETE FROM velocities_files WHERE id = %s;",(velocityFilesID,))
  
  def getSolutionParametersVel(self,velFile):
    """Get the solution parameters from a Vel file.
    
    Parameters
    ----------
    velFile : str
      The path to the Vel file
    
    Returns
    -------
    dict
      The solution parameters
    """
    with open(velFile,"rt") as f:
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
          case ["ReleaseVersion",*values]:
            value = " ".join(values)
            solutionParameters["release_version"] = value
          case ["SamplingPeriod",*values]:
            value = " ".join(values)
            solutionParameters["sampling_period"] = value
      return solutionParameters
  
  def uploadVelocityFile(self,velFile,velFormatVersion):
    """Upload a velocity file to the database."""
    try:
      self.cursor.execute(
        f"""
        INSERT INTO velocities_files(
          url,
          epoch,
          version,
          file_type,
          data_type
        )
        VALUES(
          'public/{"/".join(velFile.split("/")[-4:])}',
          '2011-01-01 00:00:00'
          '{velFormatVersion}',
          'vel',
          'vel'
        )
        RETURNING id;
        """ #TODO: Mudar epoch aqui!!!!!!!!!!!!
      )
      return [item[0] for item in self.cursor.fetchall()][0]
    except Exception as err:
      raise UploadError(f"Could not upload velocity file to database. Error: {UploadError.formatError(str(err))}.")
  
  def saveReferencePositionVelocitiesToFile(self,velFile,idSolution,idVelocityFiles):
    """Save the reference position velocities to a temporary file for bulk upload.
    
    Parameters
    ----------
    velFile           : str
      The path to the Vel file
    idSolution        : int
      The ID of the solution
    idVelocityFiles    : int
      The ID of the velocities file
    """
    with open(velFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [Dot,Name,Ref_epoch,Ref_jday,Ref_X,Ref_Y,Ref_Z,Ref_Nlat,Ref_Elong,Ref_Up,dXDt,dYDt,dZDt,SXd,SYd,SZd,Rxy,Rxz,Rzy,dNDt,dEDt,dUDt,SNd,SEd,SUd,Rne,Rnu,Reu,first_epoch,last_epoch] if Dot[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP),"a") as tmp:
              tmp.write(
                str(self._getStationID(Name))      + "," +
                str(dXDt)                          + "," +
                str(dYDt)                          + "," +
                str(dZDt)                          + "," +
                str(SXd)                           + "," +
                str(SYd)                           + "," +
                str(SZd)                           + "," +
                str(Rxy)                           + "," +
                str(Rxz)                           + "," +
                str(Rzy)                           + "," +
                str(dNDt)                          + "," +
                str(dEDt)                          + "," +
                str(dUDt)                          + "," +
                str(SNd)                           + "," +
                str(SEd)                           + "," +
                str(SUd)                           + "," +
                str(Rne)                           + "," +
                str(Rnu)                           + "," +
                str(Reu)                           + "," +
                str(self._formatDate(first_epoch)) + "," +
                str(self._formatDate(last_epoch))  + "," +
                str(self._formatDate(Ref_epoch))   + "," +
                str(idVelocityFiles)               + "," +   
                str(idSolution)                    + "\n"
              )
              
  def uploadReferencePositionVelocities(self):
    """Bulk upload the reference position velocities from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the reference position velocities could not be uploaded to the database
    """
    try:
      with open(os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP),"r") as csvFile:
        self.cursor.copy_expert(
          f"""
          COPY reference_position_velocities(
            id_station,
            velx,
            vely,
            velz,
            velx_sigma,
            vely_sigma,
            velz_sigma,
            vel_rho_xy,
            vel_rho_xz,
            vel_rho_yz,
            reference_position_x,
            reference_position_y,
            reference_position_z,
            reference_position_x_sigma,
            reference_position_y_sigma,
            reference_position_z_sigma,
            reference_position_rho_xy,
            reference_position_rho_xz,
            reference_position_rho_yz,
            start_epoch,
            end_epoch,
            ref_epoch,
            id_velocities_files,
            id_solution
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csvFile
        )
    except Exception as err:
      raise UploadError(f"Could not upload reference position velocities to database. Error: {UploadError.formatError(str(err))}.")