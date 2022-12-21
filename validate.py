import os
from os import listdir
import datetime

def validateProviderDir(providerDir):
  """Check if the provider dir is valid. Checks if its coordinates, time series and velocities dir are valid.

  Parameters
  ----------
  providerDir : str
    The providers directory

  Returns
  -------
  bool
    True if the providers dir is valid and False otherwise
  """
  isValidCoor = True
  isValidTS   = True
  errors = ""
  dirsInProviderDir = os.listdir(providerDir)
  if "Coor" in dirsInProviderDir:
    errTemp = ""
    isValidCoor,errTemp = validateCoor(f"{providerDir}/Coor")
    if not isValidCoor:
      errors += errTemp
  if "TS" in dirsInProviderDir:
    errTemp = ""
    isValidTS,errTemp = validateTS(f"{providerDir}/TS")
    if not isValidTS:
      errors += " and " + errTemp
  return isValidCoor and isValidTS,errors
  
def validateCoor(coorDir):
  """Check if the coordinates dir is valid. Checks if all files are snx files.

  Parameters
  ----------
  coorFiles : list
    All files from the coordinates dir

  Returns
  -------
  bool
    True if the coordinates dir is valid and False otherwise
  """
  allFilesAreSnx = all([file.split(".")[-1] == "snx" for file in os.listdir(coorDir)])
  if not allFilesAreSnx:
    return False,"Not all files are snx"
  for file in os.listdir(coorDir):
    validate,validationError = validateSnx(os.path.join(coorDir,file))
    if not validate:
      return validate,validationError
  return True,"No problem"

def validateSnx(snxFile):
  with open(snxFile,"r") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
      validate,validationError = validateMetadataLine(line,snxFile)
      if not validate:
        return validate,validationError
    return True,"No problem"

def validateMetadataLine(line,file):
  line = " ".join(line.split())
  header   = line.split(" ")[0]
  value    = " ".join(line.split(" ")[1:])
  if header == "ReferenceFrame":
    if value not in ["IGS08","IGS14","free-network","IGb08","INGV_EU"]:
      return False,f"Wrong ReferenceFrame - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "EpochOfFrame":
    if not validateDate(value):
      return False,f"Wrong EpochOfFrame format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "CovarianceMatrix":
    if value not in ["full","block-diagonal","diagonal"]:
      return False,f"Wrong CovarianceMatrix - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "AnalysisCentre" or header == "CombinationCentre":
    if value not in ["UGA","INGV","WUT-EUREF","BFHK","ROB-EUREF"]:
      return False,f"Wrong AnalysisCentre/CombinationCentre - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "Software":
    if value not in ["Bernese GNSS Software 5.2","GIPSY-OASIS","CATREF"]:
      return False,f"Wrong Software - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "SINEX_version":
    if not isFloat(value):
      return False,f"Wrong SINEX_version format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "CutOffAngle":
    if not value.isdigit():
      return False,f"Wrong CutOffAngle format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "OTLModel":
    if value not in ["FES2004","GOT4.10c","FES2014b"]:
      return False,f"Wrong OTLModel - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "AntennaModel" or header == "Antennamodel":
    if value not in ["epn_14_1958.atx","igs08_wwww.atx","epn_14.atx"]:
      return False,f"Wrong AntennaModel - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "DOI":
    if not value:
      return False,f"Wrong DOI format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "CreationDate":
    if not validateDate(value):
      return False,f"Wrong CreationDate format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "ReleaseNumber":
    if not value.isdigit():
      return False,f"Wrong ReleaseNumber format - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  elif header == "SamplingPeriod":
    if value not in ["daily","weekly"]:
      return False,f"Wrong SamplingPeriod - '{value}' in file {file.split('/')[-1]}, with path: {file}."
  else:
    return False,f"Wrong metadata paremeter - '{header}' of value '{value}' in file {file.split('/')[-1]}, with path: {file}."
  return True,"No problem"
  
def isFloat(num):
  try:
    float(num)
    return True
  except ValueError:
    return False

def validateDate(date):
  try:
    datetime.datetime.strptime(date,"%d/%m/%Y %H:%M:%S")
    return True
  except ValueError:
    return False  
  
def validateTS(tsDir):
  """Check if the time series dir is valid. Checks if all files are pos files.

  Parameters
  ----------
  tsFiles : list
    All files from the time series dir

  Returns
  -------
  bool
    True if the time series dir is valid and False otherwise
  """
  allFilesAreTs = all([file.split(".")[-1] == "pos" for file in os.listdir(tsDir)])
  if not allFilesAreTs:
    return False,"Not all files are pos"
  for file in os.listdir(tsDir):
    validate,validationError = validatePos(os.path.join(tsDir,file))
    if not validate:
      return validate,validationError
  return True,"No problem"

def validatePos(posFile):
  with open(posFile,"r") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    for line in lines[lines.index("Start Field Description") + 1:lines.index("End Field Description")]:
      validate,validationError = validateMetadataLine(line)
      if not validate:
        return validate,validationError
    return True,"No problem"