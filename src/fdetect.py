class FileDetect:
  def __init__(self,con,providersDir):
    self.con         = con
    self.providerDir = {
      "INGV" : f"{providersDir}/providers_ingv/uploads",
      "ROB"  : f"{providersDir}/providers_rob/uploads",
      "SGO"  : f"{providersDir}/providers_sgo/uploads",
      "UGA"  : f"{providersDir}/providers_uga/uploads",
      "WUT"  : f"{providersDir}/providers_wut/uploads"
    }
  
  def getListOfFilesChanged(self,newHashes):
    """Get the list of files changed.

    Parameters
    ----------
    con : Connection
      An connection to a database
    newHashes: list
      A list of the hashes of the 5 providers

    Returns
    -------
    list
      A list containing a boolean for each provider, indicating if their hash was changed (True) or not (False)
    """
    cur = self.con.cursor()
    hashesChanged = [False,False,False,False,False]
    for i in range(len(list(self.providerDir.keys()))):
      res      = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{list(self.providerDir.keys())[i]}'")
      fileHash = res.fetchall()
      if self._getHashOfDir[i] != fileHash[0][0]:
        hashesChanged[i] = True
        cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE '{list(self.providerDir.keys())[i]}'",(self._getHashOfDir[i],))
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