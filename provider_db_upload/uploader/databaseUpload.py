import os
from uploadError     import *
from utils.constants import *

class DatabaseUpload:
  """Upload data to the database."""
  
  # == Class variables ==
  ESTIMATED_COORDINATES_TEMP         = "estimatedCoordinatesTemp.csv"
  REFERENCE_POSITION_VELOCITIES_TEMP = "referencePositionVelocitiesTemp.csv"
  
  # == Methods ==
  def __init__(self,conn,cursor,cfg,tmp,file_handler):
    """Initialize needed variables for a database upload.

    Parameters
    ----------
    conn         : Connection
      A connection object to the database
    cursor       : Cursor
      A cursor object to the database
    cfg          : Config
      A configuration object to which configuration parameters can be read
    tmp          : str
      A directory to which temporary files used for bulk database insertion (optimization) will be saved to
    file_handler : FileHandler
      A file handler object
    """
    self.conn   = conn
    self.cursor = cursor
    self.cfg    = cfg
    self.tmpDir = tmp + "/" if tmp[-1] != "/" else tmp
    if not os.path.exists(self.tmpDir):
      os.makedirs(self.tmpDir)
    self.file_handler = file_handler
  
  def check_solution_folder_exists(self : "DatabaseUpload",prov_bucket_dir : str,public_dir : str,data_type : str) -> tuple:
    """Check if a solution folder exists in the public directory.
    
    Parameters
    ----------
    prov_bucket_dir : str
      The path to the provider bucket directory
    public_dir      : str
      The path to the provider's public directory
    data_type       : str
      The data type of the solution (timeseries or velocity)
    
    Returns
    -------
    tuple
      A tuple containing the old and new solution versions
    """
    self.cursor.execute("SELECT release_version FROM solution WHERE ac_acronym = %s AND data_type = %s;",(os.path.basename(prov_bucket_dir),self.cfg.config.get("UPLOAD","TS_DATATYPE") if data_type == "TS" else self.cfg.config.get("UPLOAD","VEL_DATATYPE")))
    old_solution = [item[0] for item in self.cursor.fetchall()]
    new_solution = self.get_solution_parameters_TS(os.path.join(prov_bucket_dir,os.listdir(prov_bucket_dir)[0]))["release_version"] if data_type == "TS" else self.getSolutionParametersVel(os.path.join(prov_bucket_dir,os.listdir(prov_bucket_dir)[0]))["release_version"]
    if os.path.exists(os.path.join(public_dir,data_type,new_solution)):
      return old_solution,new_solution
    return old_solution,None
  
  def upload_all_provider_TS(self : "DatabaseUpload",prov_bucket_dir : str,public_dir : str) -> None:
    """Upload all timeseries files from a provider bucket directory to the database.
    
    Parameters
    ----------
    prov_bucket_dir : str
      The path to the provider bucket directory
    public_dir      : str
      The path to the provider's public directory
    
    Raises
    ------
    UploadError
      If the upload was unsuccessful
    """
    self.cursor.execute("START TRANSACTION;")
    try:
      ac       = os.path.basename(prov_bucket_dir)
      data_type = self.cfg.config.get("UPLOAD","TS_DATATYPE")
      for filetype in os.listdir(prov_bucket_dir):
        if filetype == "TS":
          for version in os.listdir(os.path.join(prov_bucket_dir,filetype)):
            if version == ".DS_Store":
              continue
            curr_dir = os.path.join(os.path.join(prov_bucket_dir,filetype),version)
            all_TS_files = self.get_list_of_TS_files(curr_dir)
            if len(all_TS_files) == 0:
              break
            is_update = self.handle_previous_solution(
              ac,
              data_type,
              self.cfg.config.get("UPLOAD","TS_DATATYPE"),
              self.cfg.config.get("UPLOAD","VEL_DATATYPE"),
              version 
            )
            if not is_update:
              self.upload_solution(data_type,self.get_solution_parameters_TS(os.path.join(curr_dir,all_TS_files[0])))
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              for file in all_TS_files:
                curr_file = os.path.join(curr_dir,file)
                self.save_estimated_coordinates_to_file(
                  curr_file,
                  current_solution_ID,
                  file
                )
              self.upload_estimated_coordinates()
              self.erase_estimated_coordinates_tmp_file()
            else:
              previous_files = os.listdir(f"{public_dir}/TS/{version}")
              new_files      = [file for file in all_TS_files if f"{file[0:18]}.pos" not in previous_files]
              updated_files  = [file for file in all_TS_files if f"{file[0:18]}.pos" in previous_files]
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              if len(new_files) > 0:
                for file in new_files:
                  curr_file = os.path.join(curr_dir,file)
                  self.save_estimated_coordinates_to_file(
                    curr_file,
                    current_solution_ID,
                    file
                  )
                self.upload_estimated_coordinates()
                self.erase_estimated_coordinates_tmp_file()
              # handle updated files
              for file in updated_files:
                with open(f"{public_dir}/TS/{version}/{file[0:18]}.pos","r") as f:
                  with open(f"{prov_bucket_dir}/TS/{version}/{file}","r") as f2:
                    oldLines = f.readlines()
                    newLines = f2.readlines()
                    updated_lines,new_different_lines = self._get_updated_and_new_lines(
                      oldLines,
                      newLines
                    )
                    for line in updated_lines:
                      self.update_estimated_coordinates(line)
                    if new_different_lines:
                      for line in new_different_lines:
                        curr_file = os.path.join(curr_dir,file)
                        self.save_estimated_coordinates_to_file(
                          curr_file,
                          current_solution_ID,
                          file
                        )
                      self.upload_estimated_coordinates()
                      self.erase_estimated_coordinates_tmp_file()
                      lines = []
                      with open(f"{public_dir}/TS/{version}/{file[0:18]}.pos","r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        lines = lines[:,lines.index("*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y             Z            Sx        Sy       Sz     Rxy   Rxz    Ryz            NLat         Elong         Height         dN        dE        dU         Sn       Se       Su      Rne    Rnu    Reu  Soln") + 1]
                      with open(f"{public_dir}/TS/{version}/{file[0:18]}.pos","w") as f:
                        f.write(lines)
                        has_updated_line = False
                        for old_line in oldLines:
                          has_updated_line = False
                          for updated_line in updated_lines:
                            if old_line.split(" ")[0] == updated_line[0] and old_line.split(" ")[1] == updated_line[1]:
                              f.write(updated_line)
                              has_updated_line = True
                          if not has_updated_line:
                            f.write(old_line)
                        for new_line in new_different_lines:
                          f.write(new_line)
            self.cursor.execute("COMMIT TRANSACTION;")
            self.fileHandler.move_solution_to_public(curr_dir,public_dir,"TS")
    except UploadError as err:
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise UploadError(str(err))
  
  def get_list_of_TS_files(self,bucketDir):
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
    return [file for file in os.listdir(bucketDir) if file != ".DS_Store" and os.path.splitext(file)[1].lower() == ".pos"]
  
  def handle_previous_solution(self,ac,dataType,tsDatatype,velDatatype,version = None):
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
    version     : str
      The release version of the solution
    """
    solutionIDInDB = self.check_solution_already_in_DB(ac,dataType)
    if dataType == tsDatatype:
      if(len(solutionIDInDB) > 0):
        for solutionID in solutionIDInDB:
          if version != self.getVersionFromSolution(solutionID): 
            self._erasePreviousSolutionFromDB(ac,dataType)
          else:
            return True
    else:
      if(len(solutionIDInDB) > 0):
        self._erasePreviousSolutionFromDB(ac,dataType)
    return False
  
  def check_solution_already_in_DB(self,ac,dataType):
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

  def getVersionFromSolution(self,solutionID):
    self.cursor.execute("SELECT release_version FROM solution WHERE id = %s",(solutionID,))
    return [item[0] for item in self.cursor.fetchall()][0]
  
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
  
  def upload_solution(self,dataType,solutionParameters):
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
  
  def get_solution_parameters_TS(self,posFile):
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
            
  def save_estimated_coordinates_to_file(self,posFile,idSolution,timeseriesFilename):
    """Save the estimated coordinates to a temporary file for bulk upload.
    
    Parameters
    ----------
    posFile            : str
      The path to the POS file
    idSolution         : int
      The ID of the solution
    timeseriesFilename : str
      URL of the file location in the repository
    """
    with open(posFile,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      stationName = None
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["9-character ID",*values]:
            stationName = " ".join(values)
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [YYYYMMDD,HHMMSS,JJJJJ_JJJJ,X,Y,Z,Sx,Sy,Sz,Rxy,Rxz,Ryz,NLat,Elong,Height,dN,dE,dU,Sn,Se,Su,Rne,Rnu,Reu,Soln] if YYYYMMDD[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"a") as tmp:
              tmp.write(
                str(stationName)                           + "," +
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
                str(timeseriesFilename)                + "\n"      
              )
  
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
  
  def upload_estimated_coordinates(self):
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
            timeseries_file_url
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csvFile
        )
    except Exception as err:
      raise UploadError(f"Could not upload estimated coordinates to database. Error: {UploadError.formatError(str(err))}.")
  
  def erase_estimated_coordinates_tmp_file(self):
    """Erase the temporary file containing the previous estimated coordinates."""
    tempPath = os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP)
    if os.path.exists(tempPath):
      os.remove(tempPath)
  
  def _get_updated_and_new_lines(self,oldLines,newLines):
    oldLines           = [line.strip() for line in oldLines]
    oldLines           = oldLines[oldLines.index("*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y             Z            Sx        Sy       Sz     Rxy   Rxz    Ryz            NLat         Elong         Height         dN        dE        dU         Sn       Se       Su      Rne    Rnu    Reu  Soln") + 1:]
    newLines           = [line.strip() for line in newLines]
    newLines           = newLines[newLines.index("*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y             Z            Sx        Sy       Sz     Rxy   Rxz    Ryz            NLat         Elong         Height         dN        dE        dU         Sn       Se       Su      Rne    Rnu    Reu  Soln") + 1:]
    keys               = ["YYYYMMDD","HHMMSS","JJJJJ_JJJJ","X","Y","Z","Sx","Sy","Sz","Rxy","Rxz","Ryz","NLat","Elong","Height","dN","dE","dU","Sn","Se","Su","Rne","Rnu","Reu","Soln"]
    oldLinesDict       = [dict(zip(keys,[part.strip() for part in (" ".join(line.split())).split(" ")])) for line in oldLines]
    newLinesDict       = [dict(zip(keys,[part.strip() for part in (" ".join(line.split())).split(" ")])) for line in newLines]
    uniqueDateHoursSet = {(line['YYYYMMDD'],line['HHMMSS']) for line in oldLinesDict}
    matchingLines      = []
    newLines           = []
    for line in newLinesDict:
      dateHours = (line['YYYYMMDD'],line['HHMMSS'])
      if dateHours in uniqueDateHoursSet:
        matchingLineInList1 = next(
          (l for l in oldLinesDict if l['YYYYMMDD'] == line['YYYYMMDD'] and l['HHMMSS'] == line['HHMMSS']), None
        )
        if matchingLineInList1 and (matchingLineInList1['X'] != line['X'] or matchingLineInList1['Y'] != line['Y'] or matchingLineInList1['Z'] != line['Z'] or matchingLineInList1['Sx'] != line['Sx'] or matchingLineInList1['Sy'] != line['Sy'] or matchingLineInList1['Sz'] != line['Sz'] or matchingLineInList1['Rxy'] != line['Rxy'] or matchingLineInList1['Rxz'] != line['Rxz'] or matchingLineInList1['Ryz'] != line['Ryz'] or matchingLineInList1['NLat'] != line['NLat'] or matchingLineInList1['Elong'] != line['Elong'] or matchingLineInList1['Height'] != line['Height'] or matchingLineInList1['dN'] != line['dN'] or matchingLineInList1['dE'] != line['dE'] or matchingLineInList1['dU'] != line['dU'] or matchingLineInList1['Sn'] != line['Sn'] or matchingLineInList1['Se'] != line['Se'] or matchingLineInList1['Su'] != line['Su'] or matchingLineInList1['Rne'] != line['Rne'] or matchingLineInList1['Rnu'] != line['Rnu'] or matchingLineInList1['Reu'] != line['Reu'] or matchingLineInList1['Soln'] != line['Soln']):
          matchingLines.append(line)
      else:
        newLines.append(line)
    return [[line[key] for key in keys] for line in matchingLines],[[line[key] for key in keys] for line in newLines]
  
  
  def update_estimated_coordinates(self,line):
    """Bulk upload the estimated coordinates from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the estimated coordinates could not be uploaded to the database
    """
    try:
      self.cursor.execute(
        f"""
        UPDATE estimated_coordinates
        SET x = %s,y = %s,z = %s,var_xx = %s,var_yy = %s,var_zz = %s,var_xy = %s,var_xz = %s,var_yz = %s,outlier = %s,sol_type = %s
        WHERE epoch = %s;
        """,
        (line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10],line[11],1 if line[-1] == "outlier" else 0,line[-1],self._formatDate(line[0],line[1]))
      )
    except Exception as err:
      raise UploadError(f"Could not upload estimated coordinates to database. Error: {UploadError.formatError(str(err))}.")
    
  
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
      dataType = self.cfg.config.get("UPLOAD","VEL_DATATYPE")
      for filetype in os.listdir(provBucketDir):
        if filetype == "Vel":
          for version in os.listdir(os.path.join(provBucketDir,filetype)):
            if version == ".DS_Store":
              continue
            currDir = os.path.join(os.path.join(provBucketDir,filetype),version)
            allVelFiles = self.getListOfVelFiles(currDir)
            if len(allVelFiles) == 0:
              break
            self.handle_previous_solution(
              ac,
              dataType,
              self.cfg.config.get("UPLOAD","TS_DATATYPE"),
              self.cfg.config.get("UPLOAD","VEL_DATATYPE")
            )
            self.upload_solution(dataType,self.getSolutionParametersVel(os.path.join(currDir,allVelFiles[0])))
            current_solution_ID = self.check_solution_already_in_DB(ac,dataType)[0]
            for file in allVelFiles:
              curr_file = os.path.join(currDir,file)
              self.saveReferencePositionVelocitiesToFile(
                curr_file,
                current_solution_ID,
                file
              )
            self.uploadReferencePositionVelocities()
            self.eraseReferencePositionVelocitiesTmpFile()
            self.cursor.execute("COMMIT TRANSACTION;")
            self.fileHandler.move_solution_to_public(currDir,publicDir,"Vel")
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
    return [file for file in os.listdir(bucketDir) if file != ".DS_Store" and os.path.splitext(file)[1].lower() == ".vel"]
  
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
      solutionParameters["creation_date"] = "2011-01-01 00:00:00" #TODO: Change this
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
  
  def saveReferencePositionVelocitiesToFile(self,velFile,idSolution,velocitiesFilename):
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
                str(Name)                              + "," +
                str(dXDt)                              + "," +
                str(dYDt)                              + "," +
                str(dZDt)                              + "," +
                str(SXd)                               + "," +
                str(SYd)                               + "," +
                str(SZd)                               + "," +
                str(Rxy)                               + "," +
                str(Rxz)                               + "," +
                str(Rzy)                               + "," +
                str(dNDt)                              + "," +
                str(dEDt)                              + "," +
                str(dUDt)                              + "," +
                str(SNd)                               + "," +
                str(SEd)                               + "," +
                str(SUd)                               + "," +
                str(Rne)                               + "," +
                str(Rnu)                               + "," +
                str(Reu)                               + "," +
                str(self._formatOnlyDate(first_epoch)) + "," +
                str(self._formatOnlyDate(last_epoch))  + "," +
                str(self._formatOnlyDate(Ref_epoch))   + "," +
                str(velocitiesFilename)                   + "," +   
                str(idSolution)                        + "\n"
              )
  
  def _formatOnlyDate(self,YYYYMMDD):
    """Format a date in the format YYYYMMDD to YYYY-MM-DD.
    
    Parameters
    ----------
    YYYYMMDD  : str
      The date in the format YYYYMMDD
    
    Returns
    -------
    str
      The date in the format YYYY-MM-DD
    """
    return f"{YYYYMMDD[0:4]}-{YYYYMMDD[4:6]}-{YYYYMMDD[6:8]}"
       
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
            velocities_files_url,
            id_solution
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csvFile
        )
    except Exception as err:
      raise UploadError(f"Could not upload reference position velocities to database. Error: {UploadError.formatError(str(err))}.")
  
  def eraseReferencePositionVelocitiesTmpFile(self):
    """Erase the temporary file containing the previous reference position velocities."""
    tempPath = os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP)
    if os.path.exists(tempPath):
      os.remove(tempPath)