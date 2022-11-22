import sqlite3
import checksumdir

# Global variables
DATABASE      = "db/detectFiles.db"
PROVIDERS_DIR = "in/providers_sftp/"
PROVIDER_DIR  = {
  "INGV" : f"{PROVIDERS_DIR}/providers_ingv",
  "ROB"  : f"{PROVIDERS_DIR}/providers_rob",
  "SGO"  : f"{PROVIDERS_DIR}/providers_sgo",
  "UGA"  : f"{PROVIDERS_DIR}/providers_uga",
  "WUT"  : f"{PROVIDERS_DIR}/providers_wut"
}

#Functions
def getHashOfDir(dir):
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

def getListOfFilesChanged(con,newHashes):
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
  cur = con.cursor()
  hashesChanged = [False,False,False,False,False]
  for i in range(len(list(PROVIDER_DIR.keys()))):
    res      = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{list(PROVIDER_DIR.keys())[i]}'")
    fileHash = res.fetchall()
    if newHashes[i] != fileHash[0][0]:
      hashesChanged[i] = True
      cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE '{list(PROVIDER_DIR.keys())[i]}'",(newHashes[i],))
      con.commit()
  return hashesChanged

# Main function
def main():
  # Open database connection
  con = sqlite3.connect(DATABASE)
  # Check which hashes changed
  hashesChanged = getListOfFilesChanged(con,[getHashOfDir(providerDir) for provider,providerDir in PROVIDER_DIR.items()])
  print(hashesChanged)
  
if __name__ == '__main__':
  main()