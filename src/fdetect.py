import checksumdir

class FileDetect:
  """Detect file changes since the last time."""
  
  # == Methods ==
  def __init__(self,con,providersDir):
    """Get default parameters.

    Parameters
    ----------
    con          : Connection
      A connection object to the local database
    providersDir : str
      The default directory for the providers
    """
    self.con         = con
    self.providerDir = {
      "INGV" : f"{providersDir}/providers_ingv/uploads",
      "ROB"  : f"{providersDir}/providers_rob/uploads",
      "SGO"  : f"{providersDir}/providers_sgo/uploads",
      "UGA"  : f"{providersDir}/providers_uga/uploads",
      "WUT"  : f"{providersDir}/providers_wut/uploads"
    }
  
  def getListOfFilesChanged(self):
    """Get the list of files changed.

    Returns
    -------
    list
      A list containing a boolean for each provider, indicating if their hash was changed (True) or not (False)
    """
    cur            = self.con.cursor()
    providerList   = list(self.providerDir.keys())
    providerHashes = [self._getHashOfDir(providerDir) for provider,providerDir in self.providerDir.items()]
    hashesChanged  = [False,False,False,False,False]
    for i in range(len(providerList)):
      res          = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{providerList[i]}'")
      previousHash = res.fetchall()
      if providerHashes[i] != previousHash[0][0]:
        hashesChanged[i] = True
        cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE '{providerList[i]}'",(providerHashes[i],))
        self.con.commit()
    return hashesChanged
  
  def _getHashOfDir(self,dir):
    """Get checksum hash from a directory recursively.

    Parameters
    ----------
    dir : str
      The directory from which to get the hash

    Returns
    -------
    str
      The hash of the directory
    """
    return checksumdir.dirhash(dir)