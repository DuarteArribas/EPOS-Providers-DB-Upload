import os
from os import listdir

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
  isValidVel  = True
  dirsInProviderDir = os.listdir(providerDir)
  if "Coor" in dirsInProviderDir:
    isValidCoor = validateCoor(os.listdir(f"{providerDir}/Coor"))
  if "TS" in dirsInProviderDir:
    isValidTS = validateTS(os.listdir(f"{providerDir}/TS"))
  if "Vel" in dirsInProviderDir:
    isValidVel = validateVel(os.listdir(f"{providerDir}/Vel"))
  return isValidCoor and isValidTS and isValidVel
  
def validateCoor(coorFiles):
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
  allFilesAreSnx = all([file.split(".")[-1] == "snx" for file in coorFiles])
  return allFilesAreSnx
  
def validateTS(tsFiles):
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
  allFilesAreTs = all([file.split(".")[-1] == "pos" for file in tsFiles])
  return allFilesAreTs
  
def validateVel(velFiles):
  """Check if the velocities dir is valid. Checks if all files are vel files.

  Parameters
  ----------
  velFiles : list
    All files from the velocities dir

  Returns
  -------
  bool
    True if the velocities dir is valid and False otherwise
  """
  allFilesAreVel = all([file.split(".")[-1] == "vel" for file in velFiles])
  return allFilesAreVel