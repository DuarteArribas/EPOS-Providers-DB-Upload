from email.mime.text import MIMEText
import checksumdir
import smtplib
import shutil
import glob
import os

class FileHandler:
  """Handle provider files."""
  
  # == Methods ==
  def __init__(self,con,providersDir,fromEmail,toEmail,pwdPath):
    """Get default parameters.

    Parameters
    ----------
    con          : Connection
      A connection object to the local database
    providersDir : str
      The default directory for the providers
    fromEmail    : str
      The email address to send the email from
    toEmail      : str
      The email address to send the email to
    pwdPath      : str
      The file containing the password of the from email
    """
    self.con         = con
    self.providerDir = {
      "INGV" : f"{providersDir}/providers_ingv/uploads",
      "ROB"  : f"{providersDir}/providers_rob/uploads",
      "SGO"  : f"{providersDir}/providers_sgo/uploads",
      "UGA"  : f"{providersDir}/providers_uga/uploads",
      "WUT"  : f"{providersDir}/providers_wut/uploads"
    }
    self.fromEmail   = fromEmail
    self.toEmail     = toEmail
    self.pwdPath     = pwdPath
  
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
  
  def sendEmail(self,subject,body):
    """Email errors to providers.

    Parameters
    ----------
    subject : str
      The email subject
    body    : str
      The email body
    """
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.connect("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.ehlo()    
    server.login(self.fromEmail,self._getPwdFromFile())
    msg = MIMEText(body)
    msg["Subject"] = subject
    server.sendmail(self.fromEmail,self.toEmail,msg.as_string())
    server.quit()
  
  def _getPwdFromFile(self):
    """Read the password from a file.

    Returns
    -------
    str
      The read password from the file
    """
    with open(self.pwdPath,"r") as pPath:
      lines = pPath.readlines()
      pwd   = lines[0]
      return pwd
      
  def moveToPublic(self,providerDir,publicDir):
    """TODO: FIX

    Parameters
    ----------
    providerDir : _type_
        _description_
    publicDir : _type_
        _description_
    """
    files    = [file for file in glob.glob(f"{providerDir}/**/*",recursive = True) if not os.path.isdir(file)]
    version  = ""
    coorOrTs = ""
    for file in files:
      with open(file,"r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
          if line.split(" ")[0] == "ReleaseNumber":
            version = "".join(line.split(" ")[1:])
            break
      coorOrTs = "TS" if "TS" in file else "Coor" 
      if not os.path.exists(f"{publicDir}/{version}/{coorOrTs}"):
        os.makedirs(f"{publicDir}/{version}/{coorOrTs}")
      shutil.move(file,f"{publicDir}/{version}/{coorOrTs}")