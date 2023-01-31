import os
import datetime

class Validator:
  """Validate provider files before insertion to database."""
  
  # == Class variables ==
  FILENAME_CONVENTION_ERROR_MSG = "\n\n Please Make sure that the filename conforms to the long filename specification of {{XXX}}{{v}}OPSSNX_{{yyyy}}{{ddd}}0000_{{pp}}D_{{pp}}D_SOL.SNX.gz, where XXX is the provider abbreviation, and v is the version (0-9), yyyy is the year, ddd is the day of the year, and pp is the sample period (01 for daily, 07 for weekly)."
  
  # == Methods ==
  def __init__(self,providerDir):
    """Get default parameters.

    Parameters
    ----------
    providerDir : str
      The default directory for the provider
    """
    self.providerDir = providerDir

  def validateProviderDir(self):
    """Check if the provider dir is valid. Checks if its coordinates and time series dirs (if it has them) are valid.

    Returns
    -------
    bool,str
      True if the providers dir is valid and False otherwise
      Any errors that occurred formatted as a string
    """
    isValidCoor       = True
    isValidTS         = True
    errors            = ""
    dirsInProviderDir = os.listdir(self.providerDir)
    # Validate Coors
    if "Coor" in dirsInProviderDir:
      errTemp = ""
      isValidCoor,errTemp = self._validateCoor(f"{self.providerDir}/Coor")
      if not isValidCoor:
        errors += errTemp + "\n"
    # Validate TS
    if "TS" in dirsInProviderDir:
      errTemp = ""
      isValidTS,errTemp = self._validateTS(f"{self.providerDir}/TS")
      if not isValidTS:
        errors += errTemp + "\n"
    return isValidCoor and isValidTS,errors
    
  def _validateCoor(self,coorDir):
    """Check if the coordinates dir is valid. Checks if all files are snx files and validate each snx file.

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
    allFilesAreSnx = all([file.split(".")[-1] == "snx" for file in os.listdir(coorDir)])
    if not allFilesAreSnx:
      return False,"Not all files are snx."
    for file in os.listdir(coorDir):
      validate,validationError = self._validateSnx(os.path.join(coorDir,file))
      if not validate:
        return validate,validationError
    return True,"No problem."

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
    validate,validationError = self._validateSnxLongFilename(snxFile)
    if not validate:
      return validate,validationError
    with open(snxFile,"r") as f:
      lines = f.readlines()
      lines = [line.strip() for line in lines]
      for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
        validate,validationError = self._validateMetadataLineSnx(line,snxFile)
        if not validate:
          return validate,validationError
      return True,"No problem."
  
  def _validateSnxLongFilename(self,snxFile):
    snxFilename    = snxFile.split("/")[-1]
    if len(snxFilename) != 41:
      return False,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Incorrect length {len(snxFilename)}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    isValidAbbr,errorMsg              = self._validateSnxFilenameAbbr(snxFile,snxFilename)
    if not isValidAbbr:
      return isValidAbbr,errorMsg
    isValidVersion,errorMsg           = self._validateSnxFilenameVersion(snxFile,snxFilename)
    if not isValidVersion:
      return isValidVersion,errorMsg
    isValidConstant,errorMsg          = self._validateSnxFilenameConstant(snxFile,snxFilename)
    if not isValidConstant:
      return isValidConstant,errorMsg
    isValidYear,errorMsg              = self._validateSnxFilenameYear(snxFile,snxFilename)
    if not isValidYear:
      return isValidYear,errorMsg
    isValidDay,errorMsg               = self._validateSnxFilenameDayOfYear(snxFile,snxFilename)
    if not isValidDay:
      return isValidDay,errorMsg
    isValidConstant2,errorMsg         = self._validateSnxFilenameConstant2(snxFile,snxFilename)
    if not isValidConstant2:
      return isValidConstant2,errorMsg
    isValidSamplePeriod,errorMsg      = self._validateSnxFilenameSamplePeriod(snxFile,snxFilename)
    if not isValidSamplePeriod:
      return isValidSamplePeriod,errorMsg
    isValidConstant3,errorMsg         = self._validateSnxFilenameConstant3(snxFile,snxFilename)
    if not isValidConstant3:
      return isValidConstant3,errorMsg
    isValidSamplePeriod2,errorMsg     = self._validateSnxFilenameSamplePeriod2(snxFile,snxFilename)
    if not isValidSamplePeriod2:
      return isValidSamplePeriod2,errorMsg
    isValidConstant4,errorMsg         = self._validateSnxFilenameConstant4(snxFile,snxFilename)
    if not isValidConstant4:
      return isValidConstant4,errorMsg
    isValidExtension,errorMsg         = self._validateSnxFilenameExtension(snxFile,snxFilename)
    if not isValidExtension:
      return isValidExtension,errorMsg
    isValidCompressExtension,errorMsg = self._validateSnxFilenameCompressExtension(snxFile,snxFilename)
    if not isValidCompressExtension:
      return isValidCompressExtension,errorMsg
    return True,"No problem"
  
  def _validateSnxFilenameAbbr(self,snxFile,snxFilename):
    validation = snxFilename[:3] in ["EPO","ING","UGA","EUR","EPN"]
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong abbreviation {snxFilename[:3]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameVersion(self,snxFile,snxFilename):
    validation = snxFilename[3:4] in [str(i) for i in range(10)]
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong version {snxFilename[3:4]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameConstant(self,snxFile,snxFilename):
    validation = snxFilename[4:11] == "OPSSNX_"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant {snxFilename[4:11]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
      
  def _validateSnxFilenameYear(self,snxFile,snxFilename):
    validation = snxFilename[11:15] in [str(i) for i in range(1994,datetime.now().year + 1)]
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file year {snxFilename[11:15]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
      
  def _validateSnxFilenameDayOfYear(self,snxFile,snxFilename):
    numOfDaysInYear = 366 if self._isLeapYear(datetime.now().year) else 365
    validation = snxFilename[15:18] in [str(i) for i in range(1,numOfDaysInYear + 1)]
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx day of the year {snxFilename[15:18]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _isLeapYear(self,year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
  
  def _validateSnxFilenameConstant2(self,snxFile,snxFilename):
    validation = snxFilename[18:23] == "0000_"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 2 - {snxFilename[4:11]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameSamplePeriod(self,snxFile,snxFilename):
    validation = snxFilename[23:25] == "01" or snxFilename[23:25] == "07"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file sample period - {snxFilename[23:25]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameConstant3(self,snxFile,snxFilename):
    validation = snxFilename[25:27] == "D_"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 3 - {snxFilename[25:27]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameSamplePeriod2(self,snxFile,snxFilename):
    validation = snxFilename[27:29] == "01" or snxFilename[27:29] == "07"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file sample period 2 - {snxFilename[27:29]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameConstant4(self,snxFile,snxFilename):
    validation = snxFilename[29:34] == "D_SOL"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file constant 4 - {snxFilename[29:34]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameExtension(self,snxFile,snxFilename):
    validation = snxFilename[34] == "." and snxFilename[35:38].lower() == "snx"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file extension - {snxFilename[34:38]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
  def _validateSnxFilenameCompressExtension(self,snxFile,snxFilename):
    validation = snxFilename[38] == "." and snxFilename[39:41].lower() == "gz"
    if not validation:
      return validation,f"Wrong filename format for snx file {snxFilename} with path {snxFile} - Wrong snx file compress extension - {snxFilename[38:41]}. {Validator.FILENAME_CONVENTION_ERROR_MSG}"
    return validation,"No problem"
  
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
    line   = " ".join(line.split())
    header = line.split(" ")[0]
    value  = " ".join(line.split(" ")[1:])
    if header == "ReferenceFrame":
      if value not in ["IGS08","IGS14","free-network","IGb08","INGV_EU","IGS20"]:
        return False,f"Wrong ReferenceFrame - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "EpochOfFrame":
      if not self._validateDate(value):
        return False,f"Wrong EpochOfFrame format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "CovarianceMatrix":
      if value not in ["full","block-diagonal","diagonal"]:
        return False,f"Wrong CovarianceMatrix - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "AnalysisCentre" or header == "CombinationCentre":
      if value not in ["UGA","INGV","WUT-EUREF","BFHK","ROB-EUREF"]:
        return False,f"Wrong AnalysisCentre/CombinationCentre - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "Software":
      if value not in ["Bernese GNSS Software 5.2","GIPSY-OASIS","CATREF"]:
        return False,f"Wrong Software - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "SINEX_version":
      if not self._isFloat(value):
        return False,f"Wrong SINEX_version format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "CutOffAngle":
      if not value.isdigit():
        return False,f"Wrong CutOffAngle format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "OTLmodel":
      if value not in ["FES2004","GOT4.10c","FES2014b"]:
        return False,f"Wrong OTLmodel - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "AntennaModel" or header == "Antennamodel":
      if value not in ["epn_14_1958.atx","igs08_wwww.atx","epn_14.atx","epn_20.atx","igs20.atx"]:
        return False,f"Wrong AntennaModel - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "DOI":
      if not value:
        return False,f"Wrong DOI format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "CreationDate":
      if not self._validateDate(value):
        return False,f"Wrong CreationDate format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "ReleaseNumber":
      if not self._isFloat(value):
        return False,f"Wrong ReleaseNumber format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "SamplingPeriod":
      if value not in ["daily","weekly"]:
        return False,f"Wrong SamplingPeriod - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    else:
      return False,f"Wrong metadata paremeter - '{header}' of value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    return True,"No problem."
    
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
      datetime.datetime.strptime(date,"%d/%m/%Y %H:%M:%S")
      return True
    except ValueError:
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
    allFilesArePbo = all([file.split(".")[-1] == "pos" for file in os.listdir(tsDir)])
    if not allFilesArePbo:
      return False,"Not all files are PBO."
    for file in os.listdir(tsDir):
      validate,validationError = self._validatePbo(os.path.join(tsDir,file))
      if not validate:
        return validate,validationError
    return True,"No problem."

  def _validatePbo(self,pboFile):
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
    with open(pboFile,"r") as f:
      lines = f.readlines()
      lines = [line.strip() for line in lines]
      for line in lines[lines.index("%Begin EPOS metadata") + 1:lines.index("%End EPOS metadata")]:
        validate,validationError = self._validateMetadataLinePbo(line,pboFile)
        if not validate:
          return validate,validationError
      return True,"No problem"
  
  def _validateMetadataLinePbo(self,line,file):
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
    line   = " ".join(line.split())
    header = line.split(" ")[0]
    value  = " ".join(line.split(" ")[1:])
    if header == "ReferenceFrame":
      if value not in ["IGS08","IGS14","free-network","IGb08","INGV_EU","IGS20"]:
        return False,f"Wrong ReferenceFrame - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "AnalysisCentre" or header == "CombinationCentre":
      if value not in ["UGA","INGV","WUT-EUREF","BFHK","ROB-EUREF"]:
        return False,f"Wrong AnalysisCentre/CombinationCentre - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "Software":
      if value not in ["Bernese GNSS Software 5.2","GIPSY-OASIS","CATREF"]:
        return False,f"Wrong Software - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "Method_url":
      if not value:
        return False,f"Wrong Method url format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "DOI":
      if not value:
        return False,f"Wrong DOI format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "ReleaseNumber":
      if not self._isFloat(value):
        return False,f"Wrong ReleaseNumber format - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    elif header == "SamplingPeriod":
      if value not in ["daily","weekly"]:
        return False,f"Wrong SamplingPeriod - '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    else:
      return False,f"Wrong metadata paremeter - '{header}' of value '{value}' in file '{file.split('/')[-1]}', with path: '{file}'."
    return True,"No problem."