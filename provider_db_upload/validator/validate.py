import os
import doi
import gzip
import math
import requests
from utils.config                             import *
from validator.validationError                import *
from validator.validationStationsDividedError import *
from datetime                                 import datetime

class Validator:
  """Validate provider files before handling them."""
  
  # == Class variables ==
  DEFAULT_SNX_FILENAME_LENGTH       = 41
  
  DEFAULT_POS_FILENAME_LENGTH       = 21
  
  DEFAULT_DAILY_POS_FILENAME_LENGTH = 30
  
  FILENAME_CONVENTION_ERROR_MSG_SNX = ("Please make sure that the filename conforms to the long filename specification "
  "of {{AAA}}{{v}}OPSSNX_{{yyyy}}{{ddd}}0000_{{SMP}}_{{SMP}}_SOL.SNX.gz, where AAA is the provider abbreviation, v is the "
  "version (0-9), yyyy is the year, ddd is the day of the year, and SMP is the sample period (01D for daily, 01W for weekly).")
  
  FILENAME_CONVENTION_ERROR_MSG_POS = ("Please make sure that the filename conforms to the long filename specification "
  "of {{AAA}}_{{XXXX00CCC}}_{{SMP}}.pos or {{AAA}}_{{XXXX00CCC}}_{{SMP}}_{{yyyymmdd}}.pos, where AAA is the provider abbreviation, XXXX00CCC is the Station Long Marker, SMP is the sample period (01D for daily, 01W for weekly) and yyyymmdd is the date of the file.")
  
  FILENAME_CONVENTION_ERROR_MSG_VEL = ("Please make sure that the filename conforms to the long filename specification "
  "of {{AAA}}_{{version}}_{{refframe}}.vel, where AAA is the provider abbreviation, version is the ReleaseVersion and refframe is the reference frame.")
  
  FOUND                             = 200
  # == Methods ==
  def __init__(self : "Validator",cfg : Config,conn,cursor,provider_dir : str,bucket_dir : str,file_handler) -> None:
    """Get default parameters.

    Parameters
    ----------
    cfg          : Config
      A config object
    conn         : psycopg2.extensions.connection
      A connection object to the EPOS db
    cursor       : psycopg2.extensions.cursor
      A cursor object to the EPOS db
    provider_dir : str
      The directory where the provider files are stored
    bucket_dir   : str
      The directory where the provider files are stored in the bucket
    """
    self.cfg                 = cfg
    self.conn                = conn
    self.cursor              = cursor
    self.marker              = None
    self.ts_metadata_values  = [None,None,None,None,None,None]
    self.vel_metadata_values = [None,None,None,None,None,None]
    self.provider_dir        = provider_dir
    self.bucket_dir          = bucket_dir
    self.file_handler        = file_handler
    self.warnings            = []

  def validate_snx(self,snx_file):
    """Validate a specific snx file.
    
    Parameters
    ----------
    snx_file : str
      The snx file to validate
      
    Raises
    ------
    ValidationError
      If there was an error validating the snx file
    """
    self._validate_snx_long_filename(snx_file)
    try:
      with gzip.open(snx_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        try:
          metadata_lines = lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]
        except Exception:
          raise ValidationError(f"No metadata block '+FILE/COMMENT'/'-FILE/COMMENT' in file '{os.path.basename(snx_file)}' with path '{snx_file}'.")
        mandatory_snx_headers = self.cfg.config("VALIDATION","MANDATORY_SNX_HEADERS").split("|")
        count_matching_mandatory_headers = sum([header.split(" ")[0].strip() in mandatory_snx_headers for header in metadata_lines])
        if count_matching_mandatory_headers != len(mandatory_snx_headers):
          raise ValidationError(f"Missing mandatory metadata parameters or duplicated metadata parameters in file '{os.path.basename(snx_file)}' with path '{snx_file}'.")
        for line in metadata_lines:
          self._validate_metadata_line_snx(line,snx_file)
    except ValidationError as err:
      raise ValidationError(str(err))
    except(OSError,ValueError):
      raise ValidationError(f"File '{os.path.basename(snx_file)}' with path '{snx_file}' is not a valid gzipped file.")
    except Exception:
      raise ValidationError(f"An unknown error occurred when validating file '{os.path.basename(snx_file)}' with path '{snx_file}'.")
  
  def _validate_snx_long_filename(self,snx_file):
    """Validate an snx file's long filename according to 20230707UploadGuidelines_v2.6 guidelines.

    Parameters
    ----------
    snx_file : str
      The full path of the snx file

    Raises
    ------
    ValidationError
      If the name doesn't conform to the one specified by the guidelines
    """
    snx_filename = os.path.basename(snx_file)
    if len(snx_filename) != Validator.DEFAULT_SNX_FILENAME_LENGTH:
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Incorrect length '{len(snx_filename)}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
    self._validate_snx_filename_abbr(snx_file,snx_filename,self.cfg.config("VALIDATION","COOR_ACS").split("|"))
    self._validate_snx_filename_version(snx_file,snx_filename)
    self._validate_snx_filename_constant(snx_file,snx_filename)
    self._validate_snx_filename_year(snx_file,snx_filename)
    self._validate_snx_filename_day_of_year(snx_file,snx_filename)
    self._validate_snx_filename_constant2(snx_file,snx_filename)
    self._validate_snx_filename_sample_period(snx_file,snx_filename)
    self._validate_snx_filename_constant3(snx_file,snx_filename)
    self._validate_snx_filename_sample_period2(snx_file,snx_filename)
    self._validate_snx_filename_constant4(snx_file,snx_filename)
    self._validate_snx_filename_extension(snx_file,snx_filename)
    self._validate_snx_filename_compress_extension(snx_file,snx_filename)
  
  def _validate_snx_filename_abbr(self,snx_file,snx_filename,allowed_ac):
    """Validate the snx filename's abbreviation according to the allowed analysis centers.

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name
    allowed_ac   : list
      The allowed analysis centers' abbreviations in the long file name

    Raises
    ------
    ValidationError
      If the abbreviation doesn't conform
    """
    if not snx_filename[:3] in allowed_ac:
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong abbreviation '{snx_filename[:3]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_version(self,snx_file,snx_filename):
    """Validate the snx filename's version (0-9).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the version is an incorrect value
    """
    if not snx_filename[3:4] in [str(i) for i in range(10)]:
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong version '{snx_filename[3:4]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_constant(self,snx_file,snx_filename):
    """Validate the snx filename's constant (must be OPSSNX_).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant is an incorrect value
    """
    if not snx_filename[4:11] == "OPSSNX_":
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file constant '{snx_filename[4:11]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
      
  def _validate_snx_filename_year(self,snx_file,snx_filename):
    """Validate the snx filename's year (four digits).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the year is not a four digit value
    """
    if not snx_filename[11:15] in [str(i) for i in range(1994,datetime.now().year + 1)]:
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file year '{snx_filename[11:15]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
      
  def _validate_snx_filename_day_of_year(self,snx_file,snx_filename):
    """Validate the snx filename's day of year (1-365/366).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the day of year is incorrect
    """
    num_of_days_in_year = 366 if self._is_leap_year(int(snx_filename[11:15])) else 365
    if not snx_filename[15:18] in [str(i).zfill(3) for i in range(1,num_of_days_in_year + 1)]:
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx day of the year '{snx_filename[15:18]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _is_leap_year(self,year):
    """Check if year is a leap year.

    Parameters
    ----------
    year : int
      The year to check

    Returns
    -------
    bool
      True if the year is a leap year and False otherwise
    """
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
  
  def _validate_snx_filename_constant2(self,snx_file,snx_filename):
    """Validate the snx filename's second constant value (must be 0000_).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not snx_filename[18:23] == "0000_":
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file constant 2 - '{snx_filename[18:23]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_sample_period(self,snx_file,snx_filename):
    """Validate the snx filename's sample period (01 or 07).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the sample period is incorrect
    """
    if not snx_filename[23:25] == "01":
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file sample period - '{snx_filename[23:25]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_constant3(self,snx_file,snx_filename):
    """Validate the snx filename's third constant value (must be D_).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not (snx_filename[25:27] == "D_" or snx_filename[25:27] == "W_"):
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file constant 3 - '{snx_filename[25:27]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_sample_period2(self,snx_file,snx_filename):
    """Validate the snx filename's second sample period (01 or 07).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the sample period is incorrect
    """
    if not snx_filename[27:29] == "01":
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file sample period 2 - '{snx_filename[27:29]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_constant4(self,snx_file,snx_filename):
    """Validate the snx filename's fourth constant value (must be D_SOL).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file
    snx_filename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not (snx_filename[29:34] == "D_SOL"or snx_filename[29:34] == "W_SOL"):
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file constant 4 - '{snx_filename[29:34]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_extension(self,snx_file,snx_filename):
    """Validate the snx filename's extension (should be .snx).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file.
    snx_filename : str
      The snx file name.

    Raises
    ------
    ValidationError
      If the extension is incorrect.
    """
    if not (snx_filename[34] == "." and snx_filename[35:38].lower() == "snx"):
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file extension - '{snx_filename[34:38]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_snx_filename_compress_extension(self,snx_file,snx_filename):
    """Validate the snx filename's compressed extension (should be .gz).

    Parameters
    ----------
    snx_file     : str
      The full path of the snx file.
    snx_filename : str
      The snx file name.

    Raises
    ------
    ValidationError
      If the extension is incorrect.
    """
    if not (snx_filename[38] == "." and snx_filename[39:41].lower() == "gz"):
      raise ValidationError(f"Wrong filename format for snx file '{snx_filename}' with path '{snx_file}' - Wrong snx file compress extension - '{snx_filename[38:41]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validate_metadata_line_snx(self,line,file):
    """Validate a specific metadata line from an snx file (according to 20230707UploadGuidelines_v2.6).

    Parameters
    ----------
    line : str
      The specific snx metadata line to validate
    file : str
      The file to which the metadata line belongs to

    Raises
    ------
    ValidationError
      If the metadata line is invalid
    """
    match [part.strip() for part in line.split(":",1)]:
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        if value not in self._get_allowed_analysis_centre_values():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"The software value is empty in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["Method-url",*values]:
        value = " ".join(values)
        if requests.get(value).status_code != Validator.FOUND or self.cfg.config.get("VALIDATION","METHOD_URL_START") not in value:
          raise ValidationError(f"Wrong method-url value '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["DOI",*values]:
        value = " ".join(values)
        if value != "unknown" and not self._validate_doi(value):
          raise ValidationError(f"Wrong DOI value '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["CreationDate",*values]:
        value = " ".join(values)
        if not self._validate_date(value):
          raise ValidationError(f"Wrong CreationDate format '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["ReleaseVersion",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"Wrong ReleaseVersion format '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        if value.lower() not in self.cfg.config.get("VALIDATION","SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{os.path.basename(file)}' with path: '{file}'.")
  
  def _get_allowed_analysis_centre_values(self):
    """Get analysis centers from the EPOS db.

    Returns
    -------
    list
      A list of all the analysis centers' abbreviations that are in the EPOS db
    """
    self.cursor.execute("SELECT acronym FROM analysis_centers;")
    return [item[0] for item in self.cursor.fetchall()]

  def _validate_date(self,date):
    """Validate a data according to the format `dd/mm/yyyy hh:mm:ss`, making sure that it is less than today.

    Parameters
    ----------
    date : str
      The date to validate

    Returns
    -------
    bool
      True if the date is according to the format or False otherwise
    """
    try:
      comparison = datetime.strptime(date,"%Y-%m-%d %H:%M:%S") < datetime.today()
      return comparison
    except ValueError:
      return False
    
  def _validate_doi(self,doi_value):
    """Validate a DOI value.

    Parameters
    ----------
    doi_value : str
      The DOI value to validate

    Returns
    -------
    bool
      True if the DOI value is valid and False otherwise
    """
    try:
      return doi.validate_doi(doi_value)
    except Exception:
      return False

  def validate_pos(self,pos_file):
    """Validate a specific pos file.

    Parameters
    ----------
    pos_file : str
      The pos file to validate

    Raises
    ------
    ValidationError
      If there was an error validating the pos file
    """
    self._validate_pos_filename(pos_file)
    try:
      with open(pos_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        try:
          metadata_lines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
          non_epos_metadata_lines = lines[:lines.index("%Begin EPOS metadata")]
        except Exception:
          raise ValidationError(f"No metadata block '%Begin EPOS metadata'/'%End EPOS metadata' in file '{os.path.basename(pos_file)}' with path '{pos_file}'.")
        mandatoryPosHeaders = self.cfg.config.get("VALIDATION","MANDATORY_POS_HEADERS").split("|")
        count_matching_mandatory_headers = sum([header.split(":")[0].strip() in mandatoryPosHeaders for header in metadata_lines])
        if count_matching_mandatory_headers != len(mandatoryPosHeaders):
          raise ValidationError(f"Missing mandatory metadata parameters or duplicated metadata parameters in file '{os.path.basename(pos_file)}' with path '{pos_file}'.")
        for line in metadata_lines:
          self._validate_metadata_line_pos(line,pos_file)
        x,y,z = self._extract_marker_x_y_z_ts(non_epos_metadata_lines)
        self._validate_reference_coordinates(pos_file,self.marker,x,y,z)
    except ValidationError as err:
      raise ValidationError(str(err))
    except OSError:
      raise ValidationError(f"Cannot read file '{os.path.basename(pos_file)}' with path '{pos_file}'.")
    except Exception:
      raise ValidationError(f"An unknown error occurred when validating file '{os.path.basename(pos_file)}' with path '{pos_file}'.")
  
  def _validate_pos_filename(self,pos_file):
    """Validate a pos file's filename according to 20230707UploadGuidelines_v2.6 guidelines.

    Parameters
    ----------
    pos_file : str
      The full path of the pos file

    Raises
    ------
    ValidationError
      If the name doesn't conform to the one specified by the guidelines
    """
    pos_filename = os.path.basename(pos_file)
    if len(pos_filename) != Validator.DEFAULT_POS_FILENAME_LENGTH and len(pos_filename) != Validator.DEFAULT_DAILY_POS_FILENAME_LENGTH:
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Incorrect length '{len(pos_filename)}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
    self._validate_pos_filename_abbr(pos_file,pos_filename,self.cfg.config.get("VALIDATION","POS_ACS").split("|"))
    self._validate_pos_filename_constant(pos_file,pos_filename)
    self._validate_pos_filename_9_character_ID(pos_file,pos_filename)
    self._validate_pos_filename_sampling_period(pos_file,pos_filename)
    if len(pos_filename) == Validator.DEFAULT_POS_FILENAME_LENGTH:
      self._validate_pos_filename_extension(pos_file,pos_filename)
    if len(pos_filename) == Validator.DEFAULT_DAILY_POS_FILENAME_LENGTH:
      self._validate_pos_daily_date(pos_file,pos_filename)
      self._validate_pos_daily_filename_extension(pos_file,pos_filename)
  
  def _validate_pos_filename_abbr(self,pos_file,pos_filename,allowed_ac):
    """Validate the pos filename's abbreviation according to the allowed analysis centers.
    
    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The pos file name
    allowed_ac   : list
      The allowed analysis centers' abbreviations in the long file name
    
    Raises
    ------
    ValidationError
      If the abbreviation doesn't conform
    """
    if not pos_filename[:3] in allowed_ac:
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong abbreviation '{pos_filename[:3]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_pos_filename_constant(self,pos_file,pos_filename):
    """Validate the pos filename's constant (must be _).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The pos file name

    Raises
    ------
    ValidationError
      If the constant is an incorrect value
    """
    if not pos_filename[3] == "_":
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong pos file constant '{pos_filename[3]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_pos_filename_9_character_ID(self,pos_file,pos_filename):
    """Validate the pos filename's 9 character ID (must conform to the marker inside of the file).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The filename of the pos file

    Raises
    ------
    ValidationError
      If the 9 character ID doesn't conform to the long marker inside the file's metadata
    """
    try:
      with open(pos_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        metadata_lines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
        for line in metadata_lines:
          match [part.strip() for part in line.split(":",1)]:
            case ["9-character ID",*values]:
              value = " ".join(values)
              if value != pos_filename[4:13]:
                raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Pos file long marker name '{pos_filename[4:13]}' does not match the metadata file long marker name of {value}. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
    except OSError:
      raise ValidationError(f"Cannot read file '{os.path.basename(pos_file)}' with path '{pos_file}'.")
  
  def _validate_pos_filename_sampling_period(self,pos_file,pos_filename):
    """Validate the pos filename's sampling period (must be _01D or _01W).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The pos file name

    Raises
    ------
    ValidationError
      If the sampling period is an incorrect value
    """
    if not (pos_filename[13:17] == "_01D" or pos_filename[13:17] == "_01W"):
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong pos file sampling period '{pos_filename[13:17]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_pos_daily_date(self,pos_file,pos_filename):
    """Validate the pos daily filename's date (yyyymmdd).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The pos file name

    Raises
    ------
    ValidationError
      If the date is an incorrect value
    """
    if not pos_filename[17] == "_" and not self._validate_date(f"{pos_filename[18:22]}/{pos_filename[22:24]}/{pos_filename[24:26]}"):
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong pos file date '{pos_filename[18:26]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_pos_daily_filename_extension(self,pos_file,pos_filename):
    """Validate the pos daily filename's extension (should be .pos).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file
    pos_filename : str
      The pos file name

    Raises
    ------
    ValidationError
      If the extension is incorrect
    """
    if not (pos_filename[26] == "." and pos_filename[27:30].lower() == "pos"):
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong pos file extension - '{pos_filename[27:30]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_pos_filename_extension(self,pos_file,pos_filename):
    """Validate the pos filename's extension (should be .pos).

    Parameters
    ----------
    pos_file     : str
      The full path of the pos file.
    pos_filename : str
      The pos file name.

    Raises
    ------
    ValidationError
      If the extension is incorrect.
    """
    if not (pos_filename[17] == "." and pos_filename[18:21].lower() == "pos"):
      raise ValidationError(f"Wrong filename format for pos file '{pos_filename}' with path '{pos_file}' - Wrong pos file extension - '{pos_filename[18:21]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validate_metadata_line_pos(self,line,file):
    """Validate a specific metadata line from a pos file (according to 20230707UploadGuidelines_v2.6)

    Parameters
    ----------
    line : str
      The specific pos metadata line to validate
    file : str
      The file to which the metadata line belongs to

    Raises
    ------
    ValidationError
      If the metadata line is invalid
    """
    match [part.strip() for part in line.split(":",1)]:
      case ["9-character ID",*values]:
        value = " ".join(values)
        self.marker = value
        if value not in self._get_allowed_9_character_ID_values():
          raise ValidationError(f"Wrong 9-character ID value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        self.ts_metadata_values[0] = value
        if value not in self._get_allowed_analysis_centre_values():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        self.ts_metadata_values[1] = value
        if not value:
          raise ValidationError(f"The software value is empty in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["Method-url",*values]:
        value = " ".join(values)
        self.ts_metadata_values[2] = value
        if self.cfg.config.get("VALIDATION","METHOD_URL_START") not in value:
          raise ValidationError(f"Wrong method-url value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.") 
      case ["DOI",*values]:
        value = " ".join(values)
        self.ts_metadata_values[3] = value
        if not value:
          raise ValidationError(f"Wrong DOI value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["CreationDate",*values]:
        value = " ".join(values)
        if not self._validate_date(value):
          raise ValidationError(f"Wrong CreationDate format '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["ReleaseVersion",*values]:
        value = " ".join(values)
        self.ts_metadata_values[4] = value
        if not value:
          raise ValidationError(f"Wrong ReleaseVersion format '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
        self.version = value
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        self.ts_metadata_values[5] = value
        if value.lower() not in self.cfg.config.get("VALIDATION","SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")

  def _extract_marker_x_y_z_ts(self,non_epos_metadata_lines):
    for line in non_epos_metadata_lines:
      header = line.split(":")[0].strip()
      if header == "XYZ Reference position":
        x = line.split(":")[1].strip().split()[0]
        y = line.split(":")[1].strip().split()[1]
        z = line.split(":")[1].strip().split()[2]
        return x,y,z

  def _validate_reference_coordinates(self,file,marker,x,y,z):
    x_t1,y_t1,z_t1 = self._get_t1_station_coordinates(marker)
    distance = math.sqrt((float(x) - float(x_t1))**2 + (float(y) - float(y_t1))**2 + (float(z) - float(z_t1))**2)
    if distance > 100:
      raise ValidationError(f"Wrong reference coordinates x = {round(float(x),2)}, where x_t1 = {round(float(x_t1))}, y = {round(float(y),2)}, where y_t1 = {round(float(y_t1))} and z = {round(float(z),2)}, where z_t1 = {round(float(z_t1))} ({round(distance,2)}m between the solution and t1 station) for station '{marker}' for file {os.path.basename(file)}.")
    elif distance > 10:
      self.warnings.append(f"The reference coordinates for station '{marker}' for file {os.path.basename(file)} are more than 10m from the t1 station, being x = {round(float(x),2)}, where x_t1 = {round(float(x_t1))}, y = {round(float(y),2)}, where y_t1 = {round(float(y_t1))} and z = {round(float(z),2)}, where z_t1 = {round(float(z_t1))}, meaning there is a distance of ({round(distance,2)}m between the solution and t1 station).")
  
  def _get_t1_station_coordinates(self,marker):
    self.cursor.execute("SELECT x FROM station WHERE marker = %s;",(marker,))
    x = [item[0] for item in self.cursor.fetchall()][0]
    self.cursor.execute("SELECT y FROM station WHERE marker = %s;",(marker,))
    y = [item[0] for item in self.cursor.fetchall()][0]
    self.cursor.execute("SELECT z FROM station WHERE marker = %s;",(marker,))
    z = [item[0] for item in self.cursor.fetchall()][0]
    return x,y,z
  
  def _get_allowed_9_character_ID_values(self):
    """Get all the 9 character ID markers from the EPOS db.

    Returns
    -------
    list
      All the 9 character ID markers available in the EPOS db
    """
    self.cursor.execute("SELECT marker FROM station;")
    return [item[0] for item in self.cursor.fetchall()]
  
  def validate_vel(self,vel_file):
    """Validate a specific vel file.

    Parameters
    ----------
    vel_file : str
      The vel file to validate

    Raises
    ------
    ValidationError
      If there was an error validating the vel file
    """
    self._validate_vel_filename(vel_file)
    try:
      with open(vel_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        if lines[0].split(":")[1].strip() not in self._get_allowed_reference_frame_values():
          raise ValidationError(f"Wrong reference frame value '{lines[0].split(':')[1].strip()}' in file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
        try:
          metadata_lines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
        except Exception:
          raise ValidationError(f"No metadata block '%Begin EPOS metadata'/'%End EPOS metadata' in file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
        mandatory_vel_headers = self.cfg.config.get("VALIDATION","MANDATORY_VEL_HEADERS").split("|")
        count_matching_mandatory_headers = sum([header.split(":")[0].strip() in mandatory_vel_headers for header in metadata_lines])
        if count_matching_mandatory_headers != len(mandatory_vel_headers):
          raise ValidationError(f"Missing mandatory metadata parameters or duplicated metadata parameters in file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
        for line in metadata_lines:
          self._validate_metadata_line_vel(line,vel_file)
        self._validate_station(vel_file,lines[self._find_index(lines,"*Dot#") + 1:],lines[:self._find_index(lines,"*Dot#") + 1])
    except ValidationError as err:
      raise ValidationError(str(err))
    except ValidationStationsDividedError as err:
      raise ValidationStationsDividedError(str(err))
    except OSError:
      raise ValidationError(f"Cannot read file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
    except Exception as err:
      print(err)
      raise ValidationError(f"An unknown error occurred when validating file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
  
  def _find_index(self,lines,start):
    for count,line in enumerate(lines):
      if line.startswith(start):
        return count
    return 0
  
  def _validate_vel_filename(self,vel_file):
    """Validate a vel file's filename according to 20230707UploadGuidelines_v2.6 guidelines.

    Parameters
    ----------
    vel_file : str
      The full path of the vel file

    Raises
    ------
    ValidationError
      If the name doesn't conform to the one specified by the guidelines
    """
    vel_filename = os.path.basename(vel_file)
    self._validate_vel_filename_abbr(vel_file,vel_filename,self.cfg.config.get("VALIDATION","VEL_ACS").split("|"))
    self._validate_vel_filename_version(vel_file,vel_filename)
    self._validate_vel_filename_reference_frame(vel_file,vel_filename)
    self._validate_vel_filename_extension(vel_file,vel_filename)
  
  
  def _validate_vel_filename_abbr(self,vel_file,vel_filename,allowed_ac):
    """Validate the vel filename's abbreviation according to the allowed analysis centers.

    Parameters
    ----------
    vel_file     : str
      The full path of the vel file
    vel_filename : str
      The vel file name
    allowed_ac   : list
      The allowed analysis centers' abbreviations in the long file name

    Raises
    ------
    ValidationError
      If the abbreviation doesn't conform
    """
    try:
      if not vel_filename[:3] in allowed_ac:
        raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong abbreviation '{vel_filename[:3]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
    except IndexError:
      raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong vel file abbreviation for file '{vel_filename}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
  
  def _validate_vel_filename_version(self,vel_file,vel_filename):
    """Validate the vel filename's version (should be the same as the ReleaseVersion).

    Parameters
    ----------
    vel_file     : str
      The full path of the vel file
    vel_filename : str
      The vel file name

    Raises
    ------
    ValidationError
      If the version is not equal to the ReleaseNumber of the file
    """
    try:
      with open(vel_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        metadata_lines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
        for line in metadata_lines:
          match [part.strip() for part in line.split(":",1)]:
            case ["ReleaseVersion",*values]:
              value = " ".join(values)
              if value != vel_filename.split("_")[1]:
                raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Vel file version '{vel_filename.split('_')[1]}' does not match the metadata file ReleaseVersion of {value}. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
    except OSError:
      raise ValidationError(f"Cannot read file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
    except IndexError:
      raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong vel file version for file '{vel_filename}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
  
  def _validate_vel_filename_reference_frame(self,vel_file,vel_filename):
    """Validate the vel filename's reference frame (should bt the same as the reference frame of the file).

    Parameters
    ----------
    vel_file     : str
      The full path of the vel file
    vel_filename : str
      The vel file name

    Raises
    ------
    ValidationError
      If the reference frame is not equal to the reference frame of the file
    """
    try:
      with open(vel_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        if lines[0].split(":")[1].strip() != vel_filename.split("_")[2].split(".")[0]:
          raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Vel file reference frame '{vel_filename.split('_')[2].split('.')[0]}' does not match the metadata file reference frame of {lines[0].split(':')[1].strip()}. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
    except OSError:
      raise ValidationError(f"Cannot read file '{os.path.basename(vel_file)}' with path '{vel_file}'.")
    except IndexError:
      raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong vel file reference frame for file '{vel_filename}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
  
  def _validate_vel_filename_extension(self,vel_file,vel_filename):
    """Validate the vel filename's extension (should be .vel).

    Parameters
    ----------
    vel_file     : str
      The full path of the vel file
    vel_filename : str
      The vel file name

    Raises
    ------
    ValidationError
      If the extension is incorrect
    """
    try:
      if not (vel_filename[-4] == "." and vel_filename[-3:].lower() == "vel"):
        raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong vel file extension - '{vel_filename[-4:]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
    except IndexError:
      raise ValidationError(f"Wrong filename format for vel file '{vel_filename}' with path '{vel_file}' - Wrong vel file extension for file '{vel_filename}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_VEL}")
  
  def _get_allowed_reference_frame_values(self):
    """Get the allowed reference frame values from the database.
    
    Returns
    -------
    list
      The allowed reference frame values
    """
    self.cursor.execute("SELECT name FROM reference_frame;")
    return [item[0] for item in self.cursor.fetchall()]
  
  def _validate_metadata_line_vel(self,line,file):
    """Validate a specific metadata line from a vel file (according to 20230707UploadGuidelines_v2.6)

    Parameters
    ----------
    line : str
      The specific vel metadata line to validate
    file : str
      The file to which the metadata line belongs to

    Raises
    ------
    ValidationError
      If the metadata line is invalid
    """
    match [part.strip() for part in line.split(":",1)]:
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        self.vel_metadata_values[0] = value
        if value not in self._get_allowed_analysis_centre_values():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        self.vel_metadata_values[1] = value
        if not value:
          raise ValidationError(f"The software value is empty in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["Method-url",*values]:
        value = " ".join(values)
        self.vel_metadata_values[2] = value
        if self.cfg.config.get("VALIDATION","METHOD_URL_START") not in value:
          raise ValidationError(f"Wrong method-url value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["DOI",*values]:
        value = " ".join(values)
        self.vel_metadata_values[3] = value
        if not value:
          raise ValidationError(f"Wrong DOI value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
      case ["ReleaseVersion",*values]:
        value = " ".join(values)
        self.vel_metadata_values[4] = value
        if not value:
          raise ValidationError(f"Wrong ReleaseVersion format '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
        self.version = value
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        self.vel_metadata_values[5] = value
        if value.lower() not in self.cfg.config.get("VALIDATION","SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{os.path.basename(file)}', with path: '{file}'.")
  
  def _validate_station(self,vel_file,lines,metadata_lines_and_header):
    not_existing_stations          = []
    not_existing_stations_line     = []
    duplicate_stations             = []
    duplicate_stations_line        = []
    wrong_coordinates_station      = []
    wrong_coordinates_station_line = []
    correct_stations               = []
    correct_stations_line          = []
    for line in lines:
      station = line.split(" ")[1]
      if not self._is_station_in_db(station):
        not_existing_stations.append(station)
        not_existing_stations_line.append(line)
      else:
        if station not in correct_stations:
          try:
            self._validate_reference_coordinates(vel_file,line.split()[1],line.split()[4],line.split()[5],line.split()[6])
            correct_stations.append(station)
            correct_stations_line.append(line) 
          except ValidationError as err:
            wrong_coordinates_station.append(str(err))
            wrong_coordinates_station_line.append(line)   
        else:
          duplicate_stations.append(station)
          duplicate_stations_line.append(station)        
    wrong_stations      = set(not_existing_stations + duplicate_stations + wrong_coordinates_station)
    wrong_stations_line = set(not_existing_stations_line + duplicate_stations_line + wrong_coordinates_station_line)
    new_line_char           = "\n"
    comma_and_new_line_char = ", \n"
    not_existing_stations_error = f"The following stations of file '{os.path.basename(vel_file)}' with path '{vel_file}' are not in the database: {new_line_char}{comma_and_new_line_char.join(not_existing_stations)}.{new_line_char}" if not_existing_stations != [] else ""
    duplicate_stations_error    = f"The following stations of file '{os.path.basename(vel_file)}' with path '{vel_file}' are duplicated: {new_line_char}{comma_and_new_line_char.join(duplicate_stations)}." if duplicate_stations != [] else ""
    wrong_coordinates_station_error = f"The following stations have wrong reference coordinates: {new_line_char}{comma_and_new_line_char.join(wrong_coordinates_station)}." if wrong_coordinates_station != [] else ""
    if wrong_stations and correct_stations:
      self._divide_good_and_wrong_stations_into_files(vel_file,wrong_stations_line,correct_stations_line,metadata_lines_and_header)
      raise ValidationStationsDividedError(f"{not_existing_stations_error}{duplicate_stations_error}{wrong_coordinates_station_error}")
    elif wrong_stations:
      raise ValidationError(f"{not_existing_stations_error}{duplicate_stations_error}{wrong_coordinates_station_error}")
  
  def _is_station_in_db(self,station):
    self.cursor.execute("SELECT marker FROM station WHERE marker = %s;",(station,))
    return self.cursor.fetchone() is not None
  
  def _divide_good_and_wrong_stations_into_files(self,vel_file,wrong_stations_line,correct_stations_line,metadata_lines_and_header):
    os.remove(vel_file)
    with open(vel_file,"w") as f:
      for line in metadata_lines_and_header:
        f.write(line)
        f.write("\n")
      for line in correct_stations_line:
        f.write(line)
        f.write("\n")
    self.file_handler.move_pbo_file_to_bucket(vel_file,self.bucket_dir,"Vel",self.vel_metadata_values[4])
    with open(vel_file,"w") as g:
      for line in metadata_lines_and_header:
        g.write(line)
        g.write("\n")
      for line in wrong_stations_line:
        g.write(line)
        g.write("\n")