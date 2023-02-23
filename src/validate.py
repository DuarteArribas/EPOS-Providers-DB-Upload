import os
import doi
import gzip
import requests
from datetime            import datetime
from src.utils.config    import *
from src.validationError import *

class Validator:
  """Validate provider files before insertion to database."""
  
  # == Class variables ==
  FILENAME_CONVENTION_ERROR_MSG  = "\n\n Please make sure that the filename conforms to the long filename specification of {{XXX}}{{v}}OPSSNX_{{yyyy}}{{ddd}}0000_{{pp}}D_{{pp}}D_SOL.SNX.gz, where XXX is the provider abbreviation, and v is the version (0-9), yyyy is the year, ddd is the day of the year, and pp is the sample period (01 for daily, 07 for weekly)."
  FILENAME_CONVENTION_ERROR_MSG2 = "\n\n Please make sure that the filename conforms to the long filename specification of {{XXXX}}{{00}}{{CCC}}.pos.gz, where XXXX00CCC is the Station Long Marker."
  
  # == Methods ==
  def __init__(self,providerDir,cfg,conn,cursor):
    """Get default parameters.

    Parameters
    ----------
    providerDir : str
      The default directory for the provider
    """
    self.providerDir = providerDir
    self.cfg         = cfg
    self.conn        = conn
    self.cursor      = cursor

  def validateProviderDir(self):
    """Check if the provider dir is valid. Checks if its coordinates and time series dirs (if it has them) are valid.

    Returns
    -------
    bool,str
      True if the providers dir is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    dirsInProviderDir = os.listdir(self.providerDir)
    # Validate Coors
    if "Coor" in dirsInProviderDir:
      self._validateCoor(f"{self.providerDir}/Coor")
    # Validate TS
    if "TS" in dirsInProviderDir:
      self._validateTS(f"{self.providerDir}/TS")
    
  def _validateCoor(self,coorDir):
    """Check if the coordinates dir is valid. Check if all files are snx files and validate each snx file.

    Parameters
    ----------
    coorDir : str
      The coordinates dir to validate.

    Returns
    -------
    bool,str
      True if the coordinates dir is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    coorFiles = os.listdir(coorDir)
    allFilesAreSnx = all([self._getNExtension(file,2) == "snx" for file in coorFiles])
    if not allFilesAreSnx:
      raise ValidationError("Not all files are snx.")
    for file in coorFiles:
      self._validateSnx(os.path.join(coorDir,file))
  
  def _getNExtension(self,filename,n):
    return filename.split(".")[-n].lower()

  def _validateSnx(self,snxFile):
    """Validate a specific snx file.

    Parameters
    ----------
    snxFile : str
      The snx file to validate

    Returns
    -------
    bool,str
      True if the snx file is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    self._validateSnxLongFilename(snxFile)
    try:
      with gzip.open(snxFile,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        try:
          metadataLines = lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]
        except Exception:
          raise ValidationError(f"No metadata block +FILE/COMMENT/-FILE/COMMENT in file {snxFile.split('/')[-1]} with path {snxFile}.")
        if len(metadataLines) != 13:
          raise ValidationError(f"Wrong number of metadata parameters in file {snxFile.split('/')[-1]} with path {snxFile}.")
        for line in metadataLines:
          self._validateMetadataLineSnx(line,snxFile)
    except(OSError,ValueError):
      raise ValidationError(f"File {snxFile.split('/')[-1]} with path {snxFile} is not a valid gzipped file.")
  
  def _validateSnxLongFilename(self,snxFile):
    snxFilename = snxFile.split("/")[-1]
    if len(snxFilename) != 41:
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Incorrect length {len(snxFilename)}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
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
    if not snxFilename[:3] in allowedAC:
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong abbreviation {snxFilename[:3]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameVersion(self,snxFile,snxFilename):
    if not snxFilename[3:4] in [str(i) for i in range(10)]:
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong version {snxFilename[3:4]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameConstant(self,snxFile,snxFilename):
    if not snxFilename[4:11] == "OPSSNX_":
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant {snxFilename[4:11]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
      
  def _validateSnxFilenameYear(self,snxFile,snxFilename):
    if not snxFilename[11:15] in [str(i) for i in range(1994,datetime.now().year + 1)]:
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file year {snxFilename[11:15]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
      
  def _validateSnxFilenameDayOfYear(self,snxFile,snxFilename):
    numOfDaysInYear = 366 if self._isLeapYear(int(snxFilename[11:15])) else 365
    if not snxFilename[15:18] in [str(i).zfill(3) for i in range(1,numOfDaysInYear + 1)]:
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx day of the year {snxFilename[15:18]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _isLeapYear(self,year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
  
  def _validateSnxFilenameConstant2(self,snxFile,snxFilename):
    if not snxFilename[18:23] == "0000_":
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 2 - {snxFilename[4:11]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameSamplePeriod(self,snxFile,snxFilename):
    if not (snxFilename[23:25] == "01" or snxFilename[23:25] == "07"):
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file sample period - {snxFilename[23:25]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameConstant3(self,snxFile,snxFilename):
    if not snxFilename[25:27] == "D_":
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 3 - {snxFilename[25:27]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameSamplePeriod2(self,snxFile,snxFilename):
    if not (snxFilename[27:29] == "01" or snxFilename[27:29] == "07"):
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file sample period 2 - {snxFilename[27:29]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameConstant4(self,snxFile,snxFilename):
    if not snxFilename[29:34] == "D_SOL":
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 4 - {snxFilename[29:34]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameExtension(self,snxFile,snxFilename):
    if not (snxFilename[34] == "." and snxFilename[35:38].lower() == "snx"):
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file extension - {snxFilename[34:38]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
  def _validateSnxFilenameCompressExtension(self,snxFile,snxFilename):
    if not (snxFilename[38] == "." and snxFilename[39:41].lower() == "gz"):
      raise ValidationError(f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file compress extension - {snxFilename[38:41]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}")
  
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
    match line.split():
      case ["ReferenceFrame",*values]:
        value = " ".join(values)
        if value not in self._getAllowedReferenceFrameValues():
          raise ValidationError(f"Wrong ReferenceFrame value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["EpochOfFrame",*values]:
        value = " ".join(values)
        if not self._validateDate(value):
          raise ValidationError(f"Wrong EpochOfFrame format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["CovarianceMatrix",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("COV_MATRIX_VALUES").split("|"):
          raise ValidationError(f"Wrong CovarianceMatrix value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["AnalysisCentre",*values]:
        value = " ".join(values)
        if value not in self._getAllowedAnalysisCentreValues():
          raise ValidationError(f"Wrong AnalysisCentre value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["Software",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("SOFTWARE_VALUES").split("|"):
          raise ValidationError(f"Wrong Software value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["SINEX_version",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"Wrong SINEX_version '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["CutOffAngle",*values]:
        value = " ".join(values)
        if not value.isdigit():
          raise ValidationError(f"Wrong CutOffAngle format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["OTLmodel",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("OTLMODEL_VALUES").split("|"):
          raise ValidationError(f"Wrong OTLmodel value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["AntennaModel",*values]:
        value = " ".join(values)
        if value not in self.cfg.getValidationConfig("ANTENNAMODEL_VALUES").split("|"):
          raise ValidationError(f"Wrong AntennaModel value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["DOI",*values]:
        value = " ".join(values)
        if value != "unknown" and not self._validateDoi(value):
          raise ValidationError(f"Wrong DOI value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["CreationDate",*values]:
        value = " ".join(values)
        if not self._validateDate(value):
          raise ValidationError(f"Wrong CreationDate format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["ReleaseNumber",*values]:
        value = " ".join(values)
        if not value:
          raise ValidationError(f"Wrong ReleaseNumber format '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case ["SamplingPeriod",*values]:
        value = " ".join(values)
        if value.lower() not in self.cfg.getValidationConfig("SAMPLINGPERIOD_VALUES").split("|"):
          raise ValidationError(f"Wrong SamplingPeriod value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
      case [header,*values]:
        value = " ".join(values)
        raise ValidationError(f"Wrong metadata paremeter '{header}' of value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'.")
  
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
    
  def _validateTS(self,tsDir):
    """Check if the time series dir is valid. Checks if all files are pos files and validate each pos file.

    Parameters
    ----------
    tsDir : str
      The time series dir to validate.

    Returns
    -------
    bool,str
      True if the time series dir is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    tsFiles = os.listdir(tsDir)
    allFilesArePos = all([self._getNExtension(file,1) == "pos" for file in tsFiles])
    if not allFilesArePos:
      raise ValidationError("Not all files are pos.")
    for file in tsFiles:
      self._validatePos(os.path.join(tsDir,file))

  def _validatePos(self,posFile):
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
      raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Incorrect length {len(posFilename)}. {Validator.FILENAME_CONVENTION_ERROR_MSG2}")
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
                raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Pos file long marker name - {posFilename[:9]} does not match the metadata file long marker name. {Validator.FILENAME_CONVENTION_ERROR_MSG2}")
    except OSError:
      raise ValidationError(f"Cannot read file {posFile.split('/')[-1]} with path {posFile}.")

  def _validatePosFilenameExtension(self,posFile,posFilename):
    if not (posFilename[9] == "." and posFilename[10:13].lower() == "pos"):
      raise ValidationError(f"Wrong filename format for pos file {posFilename} with path {posFile} - Wrong pos file extension - {posFilename[10:13]}. {Validator.FILENAME_CONVENTION_ERROR_MSG2}")
  
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
    self.cursor.execute("SELECT markerlongname FROM station;")
    return [item[0] for item in self.cursor.fetchall()]