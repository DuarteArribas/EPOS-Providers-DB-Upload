import os
import doi
import gzip
import requests
from datetime            import datetime
from src.utils.config    import *
from src.validationError import *

class Validator:
  """Validate provider files before handling them."""
  
  # == Class variables ==
  DEFAULT_SNX_FILENAME_LENGTH = 41
  
  FILENAME_CONVENTION_ERROR_MSG_SNX     = """\n\n Please make sure that the filename conforms to the long filename specification 
  of {{XXX}}{{v}}OPSSNX_{{yyyy}}{{ddd}}0000_{{pp}}D_{{pp}}D_SOL.SNX.gz, where XXX is the provider abbreviation, and v is the 
  version (0-9), yyyy is the year, ddd is the day of the year, and pp is the sample period (01 for daily, 07 for weekly)."""
  
  FILENAME_CONVENTION_ERROR_MSG_POS     = """\n\n Please make sure that the filename conforms to the long filename specification 
  of {{XXXX}}{{00}}{{CCC}}.pos.gz, where XXXX00CCC is the Station Long Marker."""
  
  # == Methods ==
  def __init__(self,cfg,conn,cursor):
    """Get default parameters.

    Parameters
    ----------
    cfg    : Config
      A config object
    conn   : psycopg2.extensions.connection
      A connection object to the EPOS db
    cursor : psycopg2.extensions.cursor
      A cursor object to the EPOS db
    """
    self.cfg    = cfg
    self.conn   = conn
    self.cursor = cursor

  def validateSnx(self,snxFile):
    """Validate a specific snx file.
    
    Parameters
    ----------
    snxFile : str
      The snx file to validate
      
    Raises
    ------
    ValidationError
      If there was an error validating the snx file
    """
    self._validateSnxLongFilename(snxFile)
    try:
      with gzip.open(snxFile,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        try:
          metadataLines = lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]
        except Exception:
          raise ValidationError(f"No metadata block '+FILE/COMMENT'/'-FILE/COMMENT' in file '{os.path.basename(snxFile)}' with path '{snxFile}'.")
        mandatorySnxHeaders = self.cfg.getValidationConfig("MANDATORY_SNX_HEADERS").split("|")
        countMatchingMandatoryHeaders = sum([header.split(" ")[0] in mandatorySnxHeaders for header in metadataLines])
        if countMatchingMandatoryHeaders != len(mandatorySnxHeaders):
          raise ValidationError(f"Missing mandatory metadata parameters or duplicated metadata parameters in file '{os.path.basename(snxFile)}' with path '{snxFile}'.")
        for line in metadataLines:
          self._validateMetadataLineSnx(line,snxFile)
    except(OSError,ValueError):
      raise ValidationError(f"File '{os.path.basename(snxFile)}' with path '{snxFile}' is not a valid gzipped file.")
    except Exception:
      raise ValidationError(f"An unknown error occurred when validating file '{os.path.basename(snxFile)}' with path '{snxFile}'.")
  
  def _validateSnxLongFilename(self,snxFile):
    """Validate an snx file's long filename according to 20220906UploadGuidelines_v2.5 guidelines.

    Parameters
    ----------
    snxFile : str
      The full path of the snx file

    Raises
    ------
    ValidationError
      If the name doesn't conform to that specified by the guidelines
    """
    snxFilename = os.path.basename(snxFile)
    if len(snxFilename) != Validator.DEFAULT_SNX_FILENAME_LENGTH:
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Incorrect length '{len(snxFilename)}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
    self._validateSnxFilenameAbbr(snxFile,snxFilename,self.cfg.getValidationConfig("COOR_ACS").split("|"))
    self._validateSnxFilenameVersion(snxFile,snxFilename)
    self._validateSnxFilenameConstant(snxFile,snxFilename)
    self._validateSnxFilenameYear(snxFile,snxFilename)
    self._validateSnxFilenameDayOfYear(snxFile,snxFilename)
    self._validateSnxFilenameConstant2(snxFile,snxFilename)
    self._validateSnxFilenameSamplePeriod(snxFile,snxFilename)
    self._validateSnxFilenameConstant3(snxFile,snxFilename)
    self._validateSnxFilenameSamplePeriod2(snxFile,snxFilename)
    self._validateSnxFilenameConstant4(snxFile,snxFilename)
    self._validateSnxFilenameExtension(snxFile,snxFilename)
    self._validateSnxFilenameCompressExtension(snxFile,snxFilename)
  
  def _validateSnxFilenameAbbr(self,snxFile,snxFilename,allowedAC):
    """Validate the snx filename's abbreviation according to the allowed analysis centers.

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name
    allowedAC   : list
      The allowed analysis centers' abbreviations in the long file name

    Raises
    ------
    ValidationError
      If the abbreviation doesn't conform
    """
    if not snxFilename[:3] in allowedAC:
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong abbreviation '{snxFilename[:3]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameVersion(self,snxFile,snxFilename):
    """Validate the snx filename's version (0-9).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the version is an incorrect value
    """
    if not snxFilename[3:4] in [str(i) for i in range(10)]:
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong version '{snxFilename[3:4]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameConstant(self,snxFile,snxFilename):
    """Validate the snx filename's constant (must be OPSSNX_).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant is an incorrect value
    """
    if not snxFilename[4:11] == "OPSSNX_":
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file constant '{snxFilename[4:11]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
      
  def _validateSnxFilenameYear(self,snxFile,snxFilename):
    """Validate the snx filename's year (four digits).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the year is not a four digit value
    """
    if not snxFilename[11:15] in [str(i) for i in range(1994,datetime.now().year + 1)]:
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file year '{snxFilename[11:15]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
      
  def _validateSnxFilenameDayOfYear(self,snxFile,snxFilename):
    """Validate the snx filename's day of year (1-365/366).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the day of year is incorrect
    """
    numOfDaysInYear = 366 if self._isLeapYear(int(snxFilename[11:15])) else 365
    if not snxFilename[15:18] in [str(i).zfill(3) for i in range(1,numOfDaysInYear + 1)]:
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx day of the year '{snxFilename[15:18]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _isLeapYear(self,year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
  
  def _validateSnxFilenameConstant2(self,snxFile,snxFilename):
    """Validate the snx filename's second constant value (must be 0000_).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not snxFilename[18:23] == "0000_":
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file constant 2 - '{snxFilename[18:23]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameSamplePeriod(self,snxFile,snxFilename):
    """Validate the snx filename's sample period (01 or 07).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the sample period is incorrect
    """
    if not (snxFilename[23:25] == "01" or snxFilename[23:25] == "07"):
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file sample period - '{snxFilename[23:25]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameConstant3(self,snxFile,snxFilename):
    """Validate the snx filename's third constant value (must be D_).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not snxFilename[25:27] == "D_":
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file constant 3 - '{snxFilename[25:27]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameSamplePeriod2(self,snxFile,snxFilename):
    """Validate the snx filename's second sample period (01 or 07).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the sample period is incorrect
    """
    if not (snxFilename[27:29] == "01" or snxFilename[27:29] == "07"):
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file sample period 2 - '{snxFilename[27:29]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameConstant4(self,snxFile,snxFilename):
    """Validate the snx filename's fourth constant value (must be D_SOL).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file
    snxFilename : str
      The snx file name

    Raises
    ------
    ValidationError
      If the constant value is incorrect
    """
    if not snxFilename[29:34] == "D_SOL":
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file constant 4 - '{snxFilename[29:34]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameExtension(self,snxFile,snxFilename):
    """Validate the snx filename's extension (should be .snx).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file.
    snxFilename : str
      The snx file name.

    Raises
    ------
    ValidationError
      If the extension is incorrect.
    """
    if not (snxFilename[34] == "." and snxFilename[35:38].lower() == "snx"):
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file extension - '{snxFilename[34:38]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateSnxFilenameCompressExtension(self,snxFile,snxFilename):
    """Validate the snx filename's compressed extension (should be .gz).

    Parameters
    ----------
    snxFile     : str
      The full path of the snx file.
    snxFilename : str
      The snx file name.

    Raises
    ------
    ValidationError
      If the extension is incorrect.
    """
    if not (snxFilename[38] == "." and snxFilename[39:41].lower() == "gz"):
      raise ValidationError(f"Wrong filename format for snx file '{snxFilename}' with path '{snxFile}' - Wrong snx file compress extension - '{snxFilename[38:41]}'. {Validator.FILENAME_CONVENTION_ERROR_MSG_SNX}")
  
  def _validateMetadataLineSnx(self,line,file):
    """Validate a specific metadata line from an snx file (according to 20220906UploadGuidelines_v2.5)

    Parameters
    ----------
    line : str
      The specific snx metadata line to validate
    file : str
      The file to which the metadata line belongs to

    Returns
    -------
    bool,str
      True if the snx metadata line is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    match line.split(":"):
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        if value not in self._getAllowedAnalysisCentreValues():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("SOFTWARE_VALUES").split("|"):
          raise ValidationError(f"Wrong Software value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["Method-url",*values]:
        value = " ".join(values)
        if requests.get(value).status_code != 200:
          raise ValidationError(f"Wrong method-url value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["DOI",*values]:
        value = " ".join(values)
        if value != "unknown" and not self._validateDoi(value):
          raise ValidationError(f"Wrong DOI value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["CreationDate",*values]:
        value = " ".join(values)
        if not self._validateDate(value):
          raise ValidationError(f"Wrong CreationDate format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["ReleaseVersion",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"Wrong ReleaseVersion format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        if value.lower() not in self.cfg.getValidationConfig("SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
  
  def _getAllowedReferenceFrameValues(self):
    self.cursor.execute("SELECT name FROM reference_frame;")
    return [item[0] for item in self.cursor.fetchall()]
  
  def _getAllowedAnalysisCentreValues(self):
    self.cursor.execute("SELECT acronym FROM analysis_centers;")
    return [item[0] for item in self.cursor.fetchall()]
  
  def _isFloat(self,num):
    """Check if a string is a float.

    Parameters
    ----------
    num : str
      The string to check

    Returns
    -------
    bool
      True if the string is a float or False if not
    """
    try:
      float(num)
      return True
    except ValueError:
      return False

  def _validateDate(self,date):
    """Validate a data according to the format `dd/mm/yyyy hh:mm:ss`.

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
      comparison = datetime.strptime(date,"%Y/%m/%d %H:%M:%S") < datetime.today()
      return comparison
    except ValueError:
      return False
    
  def _validateDoi(self,doiValue):
    try:
      return doi.validate_doi(doiValue)
    except Exception:
      return False

  def validatePos(self,posFile):
    """Validate a specific pbo file.

    Parameters
    ----------
    pboFile : str
      The pbo file to validate

    Returns
    -------
    bool,str
      True if the pbo file is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    self._validatePosFilename(posFile)
    try:
      with open(posFile,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        try:
          metadataLines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
        except Exception as err:
          raise ValidationError(f"No metadata block %Begin EPOS metadata/%End EPOS metadata in file {posFile.split('/')[-1]} with path {posFile}.")
        if len(metadataLines) != 9:
          raise ValidationError(f"Wrong number of metadata parameters in file {posFile.split('/')[-1]} with path {posFile}.")
        for line in metadataLines:
          self._validateMetadataLinePos(line,posFile)
    except OSError:
      raise ValidationError(f"Cannot read file {posFile.split('/')[-1]} with path {posFile}.")
  
  def _validatePosFilename(self,posFile):
    posFilename = posFile.split("/")[-1]
    if len(posFilename) != 13:
      raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Incorrect length {len(posFilename)}. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
    self._validatePosFilename9characterID(posFile,posFilename)
    self._validatePosFilenameExtension(posFile,posFilename)

  def _validatePosFilename9characterID(self,posFile,posFilename):
    try:
      with open(posFile,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        metadataLines = lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]
        for line in metadataLines:
          match line.split(":"):
            case ["9-character ID",*values]:
              value = " ".join(values)
              if value != posFilename[:9]:
                raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Pos file long marker name - {posFilename[:9]} does not match the metadata file long marker name. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
    except OSError:
      raise ValidationError(f"Cannot read file {posFile.split('/')[-1]} with path {posFile}.")

  def _validatePosFilenameExtension(self,posFile,posFilename):
    if not (posFilename[9] == "." and posFilename[10:13].lower() == "pos"):
      raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Wrong pos file extension - {posFilename[10:13]}. {Validator.FILENAME_CONVENTION_ERROR_MSG_POS}")
  
  def _validateMetadataLinePos(self,line,file):
    """Validate a specific metadata line from a pbo file (according to 20220906UploadGuidelines_v2.5)

    Parameters
    ----------
    line : str
      The specific pbo metadata line to validate
    file : str
      The file to which the metadata line belongs to

    Returns
    -------
    bool,str
      True if the pbo metadata line is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    match line.split(":"):
      case ["9-character ID",*values]:
        value = " ".join(values)
        if value not in self._getAllowed9characterIDValues():
          raise ValidationError(f"Wrong 9-character ID value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["ReferenceFrame",*values]:
        value = " ".join(values)
        if value not in self._getAllowedReferenceFrameValues():
          raise ValidationError(f"Wrong ReferenceFrame value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        if value not in self._getAllowedAnalysisCentreValues():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("SOFTWARE_VALUES").split("|"):
          raise ValidationError(f"Wrong Software value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["Method-url",*values]:
        value = " ".join(values)
        if requests.get(value).status_code != 200:
          raise ValidationError(f"Wrong method-url value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["DOI",*values]:
        value = " ".join(values)
        if value != "unknown" and not self._validateDoi(value):
          raise ValidationError(f"Wrong DOI value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["CreationDate",*values]:
        value = " ".join(values)
        if not self._validateDate(value):
          raise ValidationError(f"Wrong CreationDate format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["ReleaseVersion",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"Wrong ReleaseVersion format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        if value.lower() not in self.cfg.getValidationConfig("SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case [header,*values]:
        value = " ".join(values)
        raise ValidationError(f"Wrong metadata paremeter '{header}' of value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")

  def _getAllowed9characterIDValues(self):
    self.cursor.execute("SELECT marker FROM station;")
    return [item[0] for item in self.cursor.fetchall()]