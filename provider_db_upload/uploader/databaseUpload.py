import os
import shutil
from utils.constants      import *
from uploader.uploadError import *

class DatabaseUpload:
  """Upload data to the database."""
  
  # == Class variables ==
  ESTIMATED_COORDINATES_TEMP         = "estimatedCoordinatesTemp.csv"
  REFERENCE_POSITION_VELOCITIES_TEMP = "referencePositionVelocitiesTemp.csv"
  DEFAULT_POS_FILENAME_LENGTH        = 21
  
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
    solutions = {
      "folder_created"     : [],
      "folder_not_created" : []
    }
    if not os.path.exists(os.path.join(prov_bucket_dir,data_type)):
      os.makedirs(os.path.join(prov_bucket_dir,data_type))
    new_solutions = [f for f in os.listdir(os.path.join(prov_bucket_dir,data_type)) if f != ".DS_Store"]
    for new_solution in new_solutions:
      if os.path.exists(os.path.join(public_dir,data_type,new_solution)):
        solutions["folder_created"].append(new_solution)
      else:
        solutions["folder_not_created"].append(new_solution)
    return old_solution,solutions
  
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
    print(f"Uploading {public_dir} TS...")
    self.cursor.execute("START TRANSACTION;")
    try:
      ac        = os.path.basename(prov_bucket_dir)
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
              version 
            )
            if not is_update:
              print("It is a new solution!")
              self._merge_solution_files(curr_dir)
              all_TS_files = self.get_list_of_TS_files(curr_dir)
              self.upload_solution(data_type,self.get_solution_parameters_TS(os.path.join(curr_dir,all_TS_files[0])))
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              print("Saving estimated coordinates to file...")
              for file in all_TS_files:
                curr_file = os.path.join(curr_dir,file)
                self.save_estimated_coordinates_to_file(
                  curr_file,
                  current_solution_ID,
                  file
                )
              print("Finished saving estimated coordinates to file")
              self.upload_estimated_coordinates()
              self.erase_estimated_coordinates_tmp_file()
            else:
              print("It is NOT a new solution")
              self._merge_solution_files(curr_dir)
              all_TS_files = self.get_list_of_TS_files(curr_dir)
              previous_files = os.listdir(f"{public_dir}/TS/{version}")
              new_files      = [file for file in all_TS_files if file not in previous_files]
              updated_files  = [file for file in all_TS_files if file in previous_files]
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              if len(new_files) > 0:
                print("Saving estimated coordinates to file...")
                for file in new_files:
                  curr_file = os.path.join(curr_dir,file)
                  self.save_estimated_coordinates_to_file(
                    curr_file,
                    current_solution_ID,
                    file
                  )
                print("Finished saving estimated coordinates to file")
                self.upload_estimated_coordinates()
                self.erase_estimated_coordinates_tmp_file()
              # handle updated files
              for file in updated_files:
                oldLines = []
                newLines = []
                with open(f"{public_dir}/TS/{version}/{file}","r") as f:
                  with open(f"{prov_bucket_dir}/TS/{version}/{file}","r") as f2:
                    oldLines = [line.strip() for line in f.readlines()]
                    newLines = [line.strip() for line in f2.readlines()]
                updated_lines,new_different_lines = self._get_updated_and_new_lines_ts(
                  oldLines,
                  newLines
                )
                new_different_lines = [" ".join(line) for line in new_different_lines]
                updated_lines2      = [" ".join(line) for line in updated_lines]
                for line in updated_lines:
                  self.update_estimated_coordinates(line,file.split("_")[1].split("_")[0],current_solution_ID)
                print("Saving estimated coordinates to file...")
                for line in new_different_lines:
                  curr_file = os.path.join(curr_dir,file)
                  self.save_estimated_coordinates_to_file(
                    curr_file,
                    current_solution_ID,
                    file
                  )
                print("Finished saving estimated coordinates to file")
                if len(new_different_lines) > 0:
                  self.upload_estimated_coordinates()
                  self.erase_estimated_coordinates_tmp_file()
                old_file_initial_lines = oldLines[:self._find_index_of_ts_header_line(oldLines) + 1]
                oldLines = oldLines[self._find_index_of_ts_header_line(oldLines) + 1:]
                with open(f"{prov_bucket_dir}/TS/{version}/{file}","w") as bucket_write:
                  bucket_write.write("\n".join(old_file_initial_lines))
                  bucket_write.write("\n")
                  file_lines = []
                  has_updated_line = False
                  for old_line in oldLines:
                    has_updated_line = False
                    for updated_line in updated_lines2:
                      if old_line.split(" ")[0] == updated_line.split(" ")[0] and old_line.split(" ")[1].split(" ")[0] == updated_line.split(" ")[1].split(" ")[0]:
                        file_lines.append(updated_line)
                        has_updated_line = True
                    if not has_updated_line:
                      file_lines.append(old_line)
                  for new_line in new_different_lines:
                    file_lines.append(new_line)
                  file_lines = self._order_lines_by_date(file_lines)
                  for line in file_lines:
                    bucket_write.write(f" {line}")
                    bucket_write.write("\n")
            self.cursor.execute("COMMIT TRANSACTION;")
            self.file_handler.move_solution_to_public(curr_dir,public_dir,"TS")
            return True
    except UploadError as err:
      self.erase_estimated_coordinates_tmp_file()
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise UploadError(str(err))
    print("Finished uploading TS")  
  
  def _find_index_of_ts_header_line(self,lines):
    for count,line in enumerate(lines):
      if "*YYYYMMDD" in line:
        return count
    return None
  
  def get_list_of_TS_files(self,bucket_dir):
    """Get a list of all timeseries files in a directory.
    
    Parameters
    ----------
    bucket_dir : str
      The bucket directory to search for timeseries files
      
    Returns
    -------
    list
      A list of all timeseries files in the directory
    """
    return [file for file in os.listdir(bucket_dir) if file != ".DS_Store" and os.path.splitext(file)[1].lower() == ".pos"]
  
  def handle_previous_solution(self : "DatabaseUpload",ac : str,data_type : str,version : str = None) -> bool:
    """Handle a previous solution, i.e., if a previous solution exists, erase it from the database, along with its estimated coordinates.
    
    Parameters
    ----------
    ac          : str
      The analysis centre acronym
    data_type   : str
      The data type of the solution (timeseries or velocity)
    version     : str
      The release version of the solution
    """
    solution_ID_in_DB = self.check_solution_already_in_DB(ac,data_type)
    if(len(solution_ID_in_DB) > 0):
      for solution_ID in solution_ID_in_DB:
        if version != self.get_version_from_solution(solution_ID): 
          self._erase_previous_solution_from_DB(ac,data_type)
        else:
          return True
    return False
  
  def check_solution_already_in_DB(self : "DatabaseUpload",ac : str,data_type : str) -> list:
    """Check if a solution is already in the database.
    
    Parameters
    ----------
    ac        : str
      The analysis centre acronym
    data_type : str
      The data type of the solution (timeseries or velocity)
    
    Returns
    -------
    list
      A list of solution IDs if the solution is already in the database or an empty list otherwise
    """
    self.cursor.execute("SELECT id FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,data_type))
    return [item[0] for item in self.cursor.fetchall()]

  def get_version_from_solution(self : "DatabaseUpload",solution_ID : int) -> str:
    self.cursor.execute("SELECT release_version FROM solution WHERE id = %s",(solution_ID,))
    return [item[0] for item in self.cursor.fetchall()][0]
  
  def _erase_previous_solution_from_DB(self : "DatabaseUpload",ac : str,data_type : str) -> None:
    """Erase a previous solution from the database.
    
    Parameters
    ----------
    ac       : str
      The analysis centre acronym
    data_type : str
      The data type of the solution (timeseries or velocity)
    """
    self.cursor.execute("DELETE FROM solution WHERE ac_acronym = %s AND data_type = %s;",(ac,data_type))
  
  def upload_solution(self : "DatabaseUpload",data_type : str,solution_parameters : dict) -> None:
    """Upload a solution to the database.
    
    Parameters
    ----------
    data_type           : str
      The data type of the solution (timeseries or velocity)
    solution_parameters : dict
      The solution parameters
        
    Raises
    ------
    UploadError
      If the solution could not be uploaded to the database
    """
    print("Uploading solution...")
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
          '{solution_parameters["creation_date"]}',
          '{solution_parameters["release_version"]}',
          '{data_type}',
          '{solution_parameters["sampling_period"]}',
          '{solution_parameters["software"]}',
          '{solution_parameters["doi"]}',
          '{solution_parameters["processing_parameters_url"]}',
          '{solution_parameters["ac_acronym"]}',
          '{solution_parameters["reference_frame"]}'
        );
        """
      )
    except Exception as err:
      raise UploadError(f"Could not upload solution to database. Error: {UploadError.format_error(str(err))}.")
    print("Finished uploading solution")
  
  def get_solution_parameters_TS(self : "DatabaseUpload",pos_file : str) -> dict:
    """Get the solution parameters from a POS file.
    
    Parameters
    ----------
    pos_file : str
      The path to the POS file
    
    Returns
    -------
    dict
      The solution parameters
    """
    with open(pos_file,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      solution_parameters = {"reference_frame" : f"{lines[0].split(':')[1].strip()}"}
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["AnalysisCentre",*values]:
            value = " ".join(values)
            solution_parameters["ac_acronym"] = value
          case ["Software",*values]:
            value = " ".join(values)
            solution_parameters["software"] = value
          case ["Method-url",*values]:
            value = " ".join(values)
            solution_parameters["processing_parameters_url"] = value
          case ["DOI",*values]:
            value = " ".join(values)
            solution_parameters["doi"] = value
          case ["CreationDate",*values]:
            value = " ".join(values)
            solution_parameters["creation_date"] = value
            solution_parameters["creation_date"] = solution_parameters["creation_date"].replace("/","-")
          case ["ReleaseVersion",*values]:
            value = " ".join(values)
            solution_parameters["release_version"] = value
          case ["SamplingPeriod",*values]:
            value = " ".join(values)
            solution_parameters["sampling_period"] = value
      return solution_parameters
            
  def save_estimated_coordinates_to_file(self : "DatabaseUpload",pos_file : str,id_solution : int,timeseries_filename : str) -> None:
    """Save the estimated coordinates to a temporary file for bulk upload.
    
    Parameters
    ----------
    pos_file            : str
      The path to the POS file
    id_solution         : int
      The ID of the solution
    timeseries_filename : str
      URL of the file location in the repository
    """
    with open(pos_file,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      station_name = None
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["9-character ID",*values]:
            station_name = " ".join(values)
      lines = lines[lines.index("End Field Description") + 1:]
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [YYYYMMDD,HHMMSS,JJJJJ_JJJJ,X,Y,Z,Sx,Sy,Sz,Rxy,Rxz,Ryz,NLat,Elong,Height,dN,dE,dU,Sn,Se,Su,Rne,Rnu,Reu,Soln] if YYYYMMDD[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"a") as tmp:
              tmp.write(
                str(station_name)                           + "," +
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
                str(self._format_date(YYYYMMDD,HHMMSS)) + "," +
                str(Soln)                              + "," +
                str(id_solution)                        + "," +
                str(timeseries_filename)                + "\n"      
              )
  
  def _format_date(self : "DatabaseUpload",YYYYMMDD : str,HHMMSS : str) -> str:
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
  
  def upload_estimated_coordinates(self : "DatabaseUpload") -> None:
    """Bulk upload the estimated coordinates from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the estimated coordinates could not be uploaded to the database
    """
    print("Uploading estimated coordinates to DB...")
    try:
      with open(os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP),"r") as csv_file:
        self.cursor.copy_expert(
          f"""
          COPY estimated_coordinates(
            marker,
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
          csv_file
        )
    except Exception as err:
      raise UploadError(f"Could not upload estimated coordinates to database. Error: {UploadError.format_error(str(err))}.")
    print("Finished uploading estimated coordinates to DB")
  
  def erase_estimated_coordinates_tmp_file(self : "DatabaseUpload") -> None:
    """Erase the temporary file containing the previous estimated coordinates."""
    temp_path = os.path.join(self.tmpDir,DatabaseUpload.ESTIMATED_COORDINATES_TEMP)
    if os.path.exists(temp_path):
      os.remove(temp_path)
  
  def _get_updated_and_new_lines_ts(self : "DatabaseUpload",old_lines,new_lines):
    old_lines           = [line.strip() for line in old_lines]
    old_lines           = old_lines[self._find_index_of_ts_header_line(old_lines) + 1:]
    new_lines           = [line.strip() for line in new_lines]
    new_lines           = new_lines[self._find_index_of_ts_header_line(new_lines) + 1:]
    keys               = ["YYYYMMDD","HHMMSS","JJJJJ_JJJJ","X","Y","Z","Sx","Sy","Sz","Rxy","Rxz","Ryz","NLat","Elong","Height","dN","dE","dU","Sn","Se","Su","Rne","Rnu","Reu","Soln"]
    old_lines_dict = [dict(zip(keys, [part.strip() for part in line.split()])) for line in old_lines]
    new_lines_dict = [dict(zip(keys, [part.strip() for part in line.split()])) for line in new_lines]
    unique_date_hours_set = {(line['YYYYMMDD'],line['HHMMSS']) for line in old_lines_dict}
    matching_lines      = []
    new_lines           = []
    for line in new_lines_dict:
      date_hours = (line['YYYYMMDD'],line['HHMMSS'])
      if date_hours in unique_date_hours_set:
        matching_line_in_list1 = next(
          (l for l in old_lines_dict if l['YYYYMMDD'] == line['YYYYMMDD'] and l['HHMMSS'] == line['HHMMSS']),None
        )
        if matching_line_in_list1 and (
          matching_line_in_list1['X']      != line['X']     or
          matching_line_in_list1['Y']      != line['Y']     or
          matching_line_in_list1['Z']      != line['Z']     or
          matching_line_in_list1['Sx']     != line['Sx']    or
          matching_line_in_list1['Sy']     != line['Sy']    or
          matching_line_in_list1['Sz']     != line['Sz']    or
          matching_line_in_list1['Rxy']    != line['Rxy']   or
          matching_line_in_list1['Rxz']    != line['Rxz']   or
          matching_line_in_list1['Ryz']    != line['Ryz']   or
          matching_line_in_list1['NLat']   != line['NLat']  or
          matching_line_in_list1['Elong']  != line['Elong'] or
          matching_line_in_list1['Height'] != line['Height'] or
          matching_line_in_list1['dN']     != line['dN']     or
          matching_line_in_list1['dE']     != line['dE']     or
          matching_line_in_list1['dU']     != line['dU']     or
          matching_line_in_list1['Sn']     != line['Sn']     or
          matching_line_in_list1['Se']     != line['Se']     or
          matching_line_in_list1['Su']     != line['Su']     or
          matching_line_in_list1['Rne']    != line['Rne']    or
          matching_line_in_list1['Rnu']    != line['Rnu']    or
          matching_line_in_list1['Reu']    != line['Reu']    or
          matching_line_in_list1['Soln']   != line['Soln']
        ):
          matching_lines.append(line)
        else:
          new_lines.append(line)
    return [[line[key] for key in keys] for line in matching_lines],[[line[key] for key in keys] for line in new_lines]
  
  
  def update_estimated_coordinates(self : "DatabaseUpload",line : list,station : str,id_solution) -> None:
    """Bulk upload the estimated coordinates from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the estimated coordinates could not be uploaded to the database
    """
   
    self.cursor.execute(
      f"""
      UPDATE estimated_coordinates
      SET x = %s,y = %s,z = %s,var_xx = %s,var_yy = %s,var_zz = %s,var_xy = %s,var_xz = %s,var_yz = %s,outlier = %s,sol_type = %s
      WHERE epoch = %s AND marker = %s AND id_solution = %s;
      """,
      (line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10],line[11],1 if line[-1] == "outlier" else 0,line[-1],self._format_date(line[0],line[1]),station,id_solution)
    )
    
  def _get_set_of_equal_files(self : "DatabaseUpload",solution_dir : str) -> None:
    files = {}
    for file in os.listdir(solution_dir):
      if file != ".DS_Store":
        if file[0:17] not in files:
          if len(file) == DatabaseUpload.DEFAULT_POS_FILENAME_LENGTH:
            files[file[0:17]] = ["COMPLETE",[os.path.join(solution_dir,file)]]
          else:
            files[file[0:17]] = ["NOT_COMPLETE",[os.path.join(solution_dir,file)]]
        else:
          if len(file) == DatabaseUpload.DEFAULT_POS_FILENAME_LENGTH:
            LIST_START_POS = 0
            files[file[0:17]][0] = "COMPLETE"
            files[file[0:17]][1].insert(LIST_START_POS,os.path.join(solution_dir,file))
          else:
            files[file[0:17]][1].append(os.path.join(solution_dir,file))
    return files
  
  def _order_lines_by_date_and_file(self : "DatabaseUpload",lines : list) -> list:
    return sorted(lines,key = lambda x : x[0].split(" ")[0] + x[0].split(" ")[1] + x[1].rsplit("_")[-1].split(".")[0])
  
  def _order_lines_by_date(self : "DatabaseUpload",lines : list) -> list:
    return sorted(lines,key = lambda x : x.split(" ")[0] + x.split(" ")[1])
  
  def _delete_original_complete_file_line(self : "DatabaseUpload",lines : list) -> list:
    previous_lines = {}
    for line in lines:
      time_and_hours = str(line[0].split(" ")[0]) + str(line[0].split(" ")[1])
      if time_and_hours not in previous_lines:
        previous_lines[time_and_hours] = [line]
      else:
        previous_lines[time_and_hours].append(line)
    for key in previous_lines:
      if len(previous_lines[key]) > 1 and previous_lines[key][0][2] == "COMPLETE":
        lines.remove(previous_lines[key][0])
    return lines
  
  def _delete_repeated_lines(self : "DatabaseUpload",lines : list) -> list:
    previous_lines = {}
    for line in lines:
      time_and_hours = str(line[0].split(" ")[0]) + str(line[0].split(" ")[0])
      if time_and_hours not in previous_lines:
        previous_lines[time_and_hours] = [line]
      else:
        previous_lines[time_and_hours].append(line)   
    for key in previous_lines:
      if len(previous_lines[key]) > 1:
        for line in previous_lines[key][:-1]:
          lines.remove(line)
    return lines
      
  def _merge_solution_files(self : "DatabaseUpload",solution_dir : str) -> None:
    print("Merging files...")
    files = self._get_set_of_equal_files(solution_dir)
    print("Getting file lines, deleting repeated lines, reordering files and creating unique merged files...")
    for key in files:
      initial_lines   = []
      remaining_lines = []
      with open(files[key][1][0],"r") as f2:
        lines = [line.strip() for line in f2.readlines()]
        initial_lines = lines[:self._find_index_of_ts_header_line(lines) + 1]
        for file in files[key][1]:
          with open(file,"r") as f3:
            lines = [line.strip() for line in f3.readlines()]
            lines = lines[self._find_index_of_ts_header_line(lines) + 1:]
            for line in lines:
              remaining_lines.append((line,file,files[key][0]))
      if os.path.exists(os.path.join(solution_dir,f"{key}.pos")):
        os.remove(os.path.join(solution_dir,f"{key}.pos"))
      with open(os.path.join(solution_dir,f"{key}.pos"),"w") as f:
        f.write("\n".join(initial_lines))
        f.write("\n")
        remaining_lines = self._delete_original_complete_file_line(remaining_lines)
        remaining_lines = self._order_lines_by_date_and_file(remaining_lines)
        remaining_lines = self._delete_repeated_lines(remaining_lines)
        for line in remaining_lines:
          f.write(f" {line[0]}")
          f.write("\n")
    print("Removing daily files")
    for key in files:
      for file in files[key][1]:
        if len(os.path.basename(file)) != DatabaseUpload.DEFAULT_POS_FILENAME_LENGTH:
          if os.path.exists(file):
            os.remove(file)
    print("Finished merging files")
  
  def upload_all_provider_vel(self,prov_bucket_dir,public_dir):
    """Upload all velocity files from a provider bucket directory to the database.
    
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
    print(f"Uploading {public_dir} Vel...")
    self.cursor.execute("START TRANSACTION;")
    try:
      ac        = os.path.basename(prov_bucket_dir)
      data_type = self.cfg.config.get("UPLOAD","VEL_DATATYPE")
      for filetype in os.listdir(prov_bucket_dir):
        if filetype == "Vel":
          for version in os.listdir(os.path.join(prov_bucket_dir,filetype)):
            if version == ".DS_Store":
              continue
            curr_dir = os.path.join(os.path.join(prov_bucket_dir,filetype),version)
            all_vel_files = self.get_list_of_vel_files(curr_dir)
            if len(all_vel_files) == 0:
              break
            is_update = self.handle_previous_solution(
              ac,
              data_type,
              version
            )
            if not is_update:
              print("It is a new solution!")
              self.upload_solution(data_type,self.get_solution_parameters_vel(os.path.join(curr_dir,all_vel_files[0])))
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              print("Saving reference position velocities to file...")
              for file in all_vel_files:
                curr_file = os.path.join(curr_dir,file)
                self.save_reference_position_velocities_to_file(
                  curr_file,
                  current_solution_ID,
                  file
                )
              print("Finished saving reference position velocities to file")
              self.upload_reference_position_velocities()
              self.erase_reference_position_velocities_tmp_file()
            else:
              print("It is NOT a new solution")
              previous_files = os.listdir(f"{public_dir}/Vel/{version}")
              new_files      = [file for file in all_vel_files if file not in previous_files]
              updated_files  = [file for file in all_vel_files if file in previous_files]
              current_solution_ID = self.check_solution_already_in_DB(ac,data_type)[0]
              if len(new_files) > 0:
                print("Saving reference position velocities to file...")
                for file in new_files:
                  curr_file = os.path.join(curr_dir,file)
                  self.save_reference_position_velocities_to_file(
                    curr_file,
                    current_solution_ID,
                    file
                  )
                print("Finished saving reference position velocities to file")
                self.upload_reference_position_velocities()
                self.erase_reference_position_velocities_tmp_file()
              # handle updated files
              for file in updated_files:
                oldLines = []
                newLines = []
                with open(f"{public_dir}/Vel/{version}/{file}","r") as f:
                  with open(f"{prov_bucket_dir}/Vel/{version}/{file}","r") as f2:
                    oldLines = [line.strip() for line in f.readlines()]
                    newLines = [line.strip() for line in f2.readlines()]
                updated_lines,new_different_lines = self._get_updated_and_new_lines_vel(
                  oldLines,
                  newLines
                )
                new_different_lines = [" ".join(line) for line in new_different_lines]
                updated_lines2      = [" ".join(line) for line in updated_lines]
                for line in updated_lines:
                  self.update_reference_position_velocities(line,current_solution_ID)
                print("Saving reference position velocities to file...")
                for line in new_different_lines:
                  curr_file = os.path.join(curr_dir,file)
                  self.save_reference_position_velocities_to_file(
                    curr_file,
                    current_solution_ID,
                    file
                  )
                print("Finished saving reference position velocities to file")
                if len(new_different_lines) > 0:
                  self.upload_reference_position_velocities()
                  self.erase_reference_position_velocities_tmp_file()
                old_file_initial_lines = oldLines[:self._find_index_of_vel_header_line(oldLines) + 1]
                oldLines = oldLines[self._find_index_of_vel_header_line(oldLines) + 1:]
                with open(f"{prov_bucket_dir}/Vel/{version}/{file}","w") as bucket_write:
                  bucket_write.write("\n".join(old_file_initial_lines))
                  bucket_write.write("\n")
                  file_lines = []
                  has_updated_line = False
                  for old_line in oldLines:
                    has_updated_line = False
                    for updated_line in updated_lines2:
                      if old_line.split(" ")[1] == updated_line.split(" ")[1]:
                        file_lines.append(updated_line)
                        has_updated_line = True
                    if not has_updated_line:
                      file_lines.append(old_line)
                  for new_line in new_different_lines:
                    file_lines.append(new_line)
                  for line in file_lines:
                    bucket_write.write(f" {line}")
                    bucket_write.write("\n")
            self.cursor.execute("COMMIT TRANSACTION;")
            self.file_handler.move_solution_to_public(curr_dir,public_dir,"Vel")
            return True
    except UploadError as err:
      self.erase_reference_position_velocities_tmp_file()
      self.cursor.execute("ROLLBACK TRANSACTION")
      raise UploadError(str(err))
    print("Finished uploading vel")
  
  def _find_index_of_vel_header_line(self,lines):
    for count,line in enumerate(lines):
      if "*Dot#" in line:
        return count
    return None
  
  def get_list_of_vel_files(self,bucket_dir):
    """Get a list of all velocity files in a directory.
    
    Parameters
    ----------
    bucket_dir : str
      The bucket directory to search for velocity files
      
    Returns
    -------
    list
      A list of all velocity files in the directory
    """
    return [file for file in os.listdir(bucket_dir) if file != ".DS_Store" and os.path.splitext(file)[1].lower() == ".vel"]
  
  def get_solution_parameters_vel(self,vel_file):
    """Get the solution parameters from a Vel file.
    
    Parameters
    ----------
    vel_file : str
      The path to the Vel file
    
    Returns
    -------
    dict
      The solution parameters
    """
    with open(vel_file,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      solution_parameters = {"reference_frame" : f"{lines[0].split(':')[1].strip()}"}
      solution_parameters["creation_date"] = self._format_date(lines[2].split(':')[1].strip()[:9],lines[2].split(':')[1].strip()[9:])
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        match [part.strip() for part in line.split(":",1)]:
          case ["AnalysisCentre",*values]:
            value = " ".join(values)
            solution_parameters["ac_acronym"] = value
          case ["Software",*values]:
            value = " ".join(values)
            solution_parameters["software"] = value
          case ["Method-url",*values]:
            value = " ".join(values)
            solution_parameters["processing_parameters_url"] = value
          case ["DOI",*values]:
            value = " ".join(values)
            solution_parameters["doi"] = value
          case ["ReleaseVersion",*values]:
            value = " ".join(values)
            solution_parameters["release_version"] = value
          case ["SamplingPeriod",*values]:
            value = " ".join(values)
            solution_parameters["sampling_period"] = value
      return solution_parameters
  
  def save_reference_position_velocities_to_file(self,vel_file,id_solution,velocities_filename):
    """Save the reference position velocities to a temporary file for bulk upload.
    
    Parameters
    ----------
    vel_file            : str
      The path to the Vel file
    id_solution         : int
      The ID of the solution
    velocities_filename : int
      The velocities filename
    """
    with open(vel_file,"rt") as f:
      lines = [line.strip() for line in f.readlines()]
      for line in lines:
        match [part.strip() for part in (" ".join(line.split())).split(" ")]:
          case [Dot,Name,Ref_epoch,Ref_jday,Ref_X,Ref_Y,Ref_Z,Ref_Nlat,Ref_Elong,Ref_Up,dXDt,dYDt,dZDt,SXd,SYd,SZd,Rxy,Rxz,Rzy,dNDt,dEDt,dUDt,SNd,SEd,SUd,Rne,Rnu,Reu,first_epoch,last_epoch] if Dot[0] != "*":
            with open(os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP),"a") as tmp:
              tmp.write(
                str(Name)                                + "," +
                str(Ref_X)                               + "," +
                str(Ref_Y)                               + "," +
                str(Ref_Z)                               + "," +
                str(Ref_Nlat)                            + "," +
                str(Ref_Elong)                           + "," +
                str(Ref_Up)                              + "," +
                str(dXDt)                                + "," +
                str(dYDt)                                + "," +
                str(dZDt)                                + "," +
                str(SXd)                                 + "," +
                str(SYd)                                 + "," +
                str(SZd)                                 + "," +
                str(Rxy)                                 + "," +
                str(Rxz)                                 + "," +
                str(Rzy)                                 + "," +
                str(dNDt)                                + "," +
                str(dEDt)                                + "," +
                str(dUDt)                                + "," +
                str(SNd)                                 + "," +
                str(SEd)                                 + "," +
                str(SUd)                                 + "," +
                str(Rne)                                 + "," +
                str(Rnu)                                 + "," +
                str(Reu)                                 + "," +
                str(self._format_only_date(first_epoch)) + "," +
                str(self._format_only_date(last_epoch))  + "," +
                str(self._format_only_date(Ref_epoch))   + "," +
                str(Ref_jday)                            + "," +
                str(velocities_filename)                 + "," +   
                str(id_solution)                         + "\n"
              )
    
  def _format_only_date(self,YYYYMMDD):
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
       
  def upload_reference_position_velocities(self):
    """Bulk upload the reference position velocities from the temporary file to the database.
    
    Raises
    ------
    UploadError
      If the reference position velocities could not be uploaded to the database
    """
    print("Uploading reference position velocities to DB...")
    try:
      with open(os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP),"r") as csv_file:
        self.cursor.copy_expert(
          f"""
          COPY reference_position_velocities(
            marker,
            ref_x,
            ref_y,
            ref_z,
            ref_nlat,
            ref_elong,
            ref_up,
            vel_x,
            vel_y,
            vel_z,
            sd_vel_x,
            sd_vel_y,
            sd_vel_z,
            rho_xy,
            rho_xz,
            rho_yz,
            vel_n,
            vel_e,
            vel_u,
            sd_vel_n,
            sd_vel_e,
            sd_vel_u,
            rho_ne,
            rho_nu,
            rho_eu,
            first_epoch,
            last_epoch,
            ref_epoch,
            ref_jday,
            velocities_files_url,
            id_solution
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER FALSE);
          """,
          csv_file
        )
    except Exception as err:
      raise UploadError(f"Could not upload reference position velocities to database. Error: {UploadError.format_error(str(err))}.")
    print("Finished uploading reference position velocities to DB")
    
  def erase_reference_position_velocities_tmp_file(self):
    """Erase the temporary file containing the previous reference position velocities."""
    temp_path = os.path.join(self.tmpDir,DatabaseUpload.REFERENCE_POSITION_VELOCITIES_TEMP)
    if os.path.exists(temp_path):
      os.remove(temp_path)
      
  def _get_updated_and_new_lines_vel(self : "DatabaseUpload",old_lines,new_lines):
    old_lines           = [line.strip() for line in old_lines]
    old_lines           = old_lines[self._find_index_of_vel_header_line(old_lines) + 1:]
    new_lines           = [line.strip() for line in new_lines]
    new_lines           = new_lines[self._find_index_of_vel_header_line(new_lines) + 1:]
    keys                = ["Dot#","Name","Ref_epoch","Ref_jday","Ref_X","Ref_Y","Ref_Z","Ref_Nlat","Ref_Elong","Ref_Up","dX/dt","dY/dt","dZ/dt","SXd","SYd","SZd","Rxy","Rxz","Rzy","dN/dt","dE/dt","dU/dt","SNd","SEd","SUd","Rne","Rnu","Reu","first_epoch","last_epoch"]
    old_lines_dict = [dict(zip(keys,[part.strip() for part in line.split()])) for line in old_lines]
    new_lines_dict = [dict(zip(keys,[part.strip() for part in line.split()])) for line in new_lines]
    matching_lines      = []
    new_lines           = []
    for line in new_lines_dict:
      matching_line_in_list1 = next(
        (l for l in old_lines_dict if l["Name"] == line["Name"]),None
      )
      if matching_line_in_list1 and (
        matching_line_in_list1['Ref_epoch']   != line['Ref_epoch']   or
        matching_line_in_list1['Ref_jday']    != line['Ref_jday']    or
        matching_line_in_list1['Ref_X']       != line['Ref_X']       or
        matching_line_in_list1['Ref_Y']       != line['Ref_Y']       or
        matching_line_in_list1['Ref_Z']       != line['Ref_Z']       or
        matching_line_in_list1['Ref_Nlat']    != line['Ref_Nlat']    or
        matching_line_in_list1['Ref_Elong']   != line['Ref_Elong']   or
        matching_line_in_list1['Ref_Up']      != line['Ref_Up']      or
        matching_line_in_list1['dX/dt']       != line['dX/dt']       or
        matching_line_in_list1['dY/dt']       != line['dY/dt']       or
        matching_line_in_list1['dZ/dt']       != line['dZ/dt']       or
        matching_line_in_list1['SXd']         != line['SXd']         or
        matching_line_in_list1['SYd']         != line['SYd']         or
        matching_line_in_list1['SZd']         != line['SZd']         or
        matching_line_in_list1['Rxy']         != line['Rxy']         or
        matching_line_in_list1['Rxz']         != line['Rxz']         or
        matching_line_in_list1['Rzy']         != line['Rzy']         or
        matching_line_in_list1['dN/dt']       != line['dN/dt']       or
        matching_line_in_list1['dE/dt']       != line['dE/dt']       or
        matching_line_in_list1['dU/dt']       != line['dU/dt']       or
        matching_line_in_list1['SNd']         != line['SNd']         or
        matching_line_in_list1['SEd']         != line['SEd']         or
        matching_line_in_list1['SUd']         != line['SUd']         or
        matching_line_in_list1['Rne']         != line['Rne']         or
        matching_line_in_list1['Rnu']         != line['Rnu']         or
        matching_line_in_list1['Reu']         != line['Reu']         or
        matching_line_in_list1['first_epoch'] != line['first_epoch'] or
        matching_line_in_list1['last_epoch']  != line['last_epoch']
      ):
        matching_lines.append(line)
      else:
        new_lines.append(line)
    return [[line[key] for key in keys] for line in matching_lines],[[line[key] for key in keys] for line in new_lines]
  
  
  def update_reference_position_velocities(self : "DatabaseUpload",line : list,id_solution) -> None:
    """Update the reference position velocities in the database.
    
    Raises
    ------
    UploadError
      If the reference position velocities could not be uploaded to the database
    """
   
    self.cursor.execute(
      f"""
      UPDATE reference_position_velocities
      SET ref_x = %s,ref_y = %s,ref_z = %s,ref_nlat = %s,ref_elong = %s,ref_up = %s,vel_x = %s,vel_y = %s,vel_z = %s,sd_vel_x = %s,sd_vel_y = %s,sd_vel_z = %s,rho_xy = %s,rho_xz = %s,rho_yz = %s,vel_n = %s,vel_e = %s,vel_u = %s,sd_vel_n = %s,sd_vel_e = %s,sd_vel_u = %s,rho_ne = %s,rho_nu = %s,rho_eu = %s,first_epoch = %s,last_epoch = %s,ref_epoch = %s,ref_jday = %s
      WHERE marker = %s AND id_solution = %s;
      """,
      (line[4],line[5],line[6],line[7],line[8],line[9],line[10],line[11],line[12],line[13],line[14],line[15],line[16],line[17],line[18],line[19],line[20],line[21],line[22],line[23],line[24],line[25],line[26],line[27],self._format_date(line[28][:9],line[28][9:]),self._format_date(line[29][:9],line[29][9:]),self._format_date(line[2][:9],line[2][9:]),str(line[3]),line[1],id_solution)
    )