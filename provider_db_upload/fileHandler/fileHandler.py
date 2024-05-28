import checksumdir
import smtplib
import shutil
import gzip
import os
from email.mime.text import MIMEText
from src.utils.config import *

class FileHandler:
  """Handle provider files."""
  
  # Attributes
  CONFIG_FILE = "config/appconf.cfg"
  
  # == Methods ==
  def __init__(self,providersDir,fromEmail,fromEmailPassword,con = None):
    """Get default parameters.

    Parameters
    ----------
    providersDir      : str
      The default directory for the providers
    fromEmail         : str
      The email address to send the email from
    fromEmailPassword : str
      The password of the , which is sending the email
    con               : Connection
      A connection object to the local database
    """
    self.providerDir       = {
      "INGV" : f"{providersDir}/providers_ingv/uploads",
      "ROB"  : f"{providersDir}/providers_rob/uploads",
      "SGO"  : f"{providersDir}/providers_sgo/uploads", #TODO hardcoded?
      "UGA"  : f"{providersDir}/providers_uga-cnrs/uploads",
      "WUT"  : f"{providersDir}/providers_wut/uploads"
    }
    self.fromEmail         = fromEmail
    self.fromEmailPassword = fromEmailPassword
    self.con               = con
    self.cfg = Config(FileHandler.CONFIG_FILE)
  
  def getListOfHashesChanged(self):
    """Get the list of hashes changed.

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

  def updateHashes(self):
    """Update the hashes in the database."""
    cur = self.con.cursor()
    for provider,providerDir in self.providerDir.items():
      newFileHash = self._getHashOfDir(providerDir)
      cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE ?",(newFileHash,provider))
      self.con.commit()
  
  def sendEmail(self,subject,body,toEmail):
    """Email errors to providers.

    Parameters
    ----------
    subject : str
      The email subject
    body    : str
      The email body
    toEmail : str
      The provider's email address
    """
    try:
      server = smtplib.SMTP("smtp.gmail.com",587)
      server.connect("smtp.gmail.com",587)
      server.ehlo()
      server.starttls()
      server.ehlo()    
      server.login(self.fromEmail,self.fromEmailPassword)
      msg = MIMEText(body)
      msg["Subject"] = subject
      server.sendmail(self.fromEmail,toEmail,msg.as_string())
      server.sendmail(self.fromEmail,self.cfg.getEmailConfig('SEGAL_EMAIL'),msg.as_string())
      server.quit()
    except Exception as err:
      print(err)
  
  def sendEmailToSegal(self,subject,body):
    """Email errors to Segal.

    Parameters
    ----------
    subject : str
      The email subject
    body    : str
      The email body
    """
    try:
      server = smtplib.SMTP("smtp.gmail.com",587)
      server.connect("smtp.gmail.com",587)
      server.ehlo()
      server.starttls()
      server.ehlo()    
      server.login(self.fromEmail,self.fromEmailPassword)
      msg = MIMEText(body)
      msg["Subject"] = subject
      server.sendmail(self.fromEmail,self.cfg.getEmailConfig('SEGAL_EMAIL'),msg.as_string())
      server.quit()
    except Exception as err:
      print(err)
  
  def moveSnxFileToPublic(self,snxFile,publicDir):
    """Move an snx file to the public directory, according to {publicDir}/Coor/{version}/{snxFile}

    Parameters
    ----------
    snxFile   : str
      The snx file to move
    publicDir : str
      The public directory of the correspondent provider
    """
    try:
      with gzip.open(snxFile,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
          if line.split(":")[0].strip() == "ReleaseVersion":
            version    = "".join(line.split(":")[1:])
            pathToMove = f"{publicDir}/Coor/{version}"
            if not os.path.exists(pathToMove):
              os.makedirs(pathToMove)
            shutil.move(snxFile,pathToMove)
            break
    except Exception as err:
      print(err)
    
  
  def movePboFileToBucket(self,pboFile,bucketDir,filetype,version):
    """Move a pbo file to the bucket directory, according to {bucketDir}/TS/{version}/{pboFile}

    Parameters
    ----------
    pboFile   : str
      The pbo file to move
    bucketDir : str
      The bucket directory of the correspondent provider
    fileType  : str
      The type of the file (TS or VEL)
    version   : str
      The release number
    """
    try:
      pathToMove = f"{bucketDir}/{filetype}/{version}"
      if not os.path.exists(pathToMove):
        os.makedirs(pathToMove)
      shutil.copy(pboFile,pathToMove)
      os.remove(pboFile)
    except Exception as err:
      print(err)
  
  def moveSolutionToPublic(self,solutionDir,publicDir,filetype):
    """Move a solution directory to the public directory, according to {publicDir}/{filetype}/{solutionDir}.
    
    Parameters
    ----------
    solutionDir : str
      The solution directory to move
    publicDir   : str
      The public directory of the correspondent provider
    fileType    : str
      The type of the file (TS or VEL)
    """
    try: #TODO
      pathToMove = f"{publicDir}/{filetype}"
      if not os.path.exists(pathToMove):
        os.makedirs(pathToMove)
      if not os.path.exists(os.path.join(pathToMove,solutionDir.split("/")[-1])):
        os.makedirs(os.path.join(pathToMove,solutionDir.split("/")[-1]))
      for file in os.listdir(solutionDir):
        shutil.copy(os.path.join(solutionDir,file),os.path.join(pathToMove,solutionDir.split("/")[-1]))
        os.remove(os.path.join(solutionDir,file))
    except Exception as err:
      print('arropz')
      print(err)