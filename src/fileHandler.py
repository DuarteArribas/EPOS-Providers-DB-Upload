import checksumdir
import smtplib
import shutil
import gzip
import os
from email.mime.text import MIMEText

class FileHandler:
  """Handle provider files."""
  
  # == Methods ==
  def __init__(self,con,providersDir,fromEmail,fromEmailPassword):
    """Get default parameters.

    Parameters
    ----------
    con               : Connection
      A connection object to the local database
    providersDir      : str
      The default directory for the providers
    fromEmail         : str
      The email address to send the email from
    fromEmailPassword : str
      The password of the , which is sending the email
    """
    self.con               = con
    self.providerDir       = {
      "INGV" : f"{providersDir}/providers_ingv/uploads",
      "ROB"  : f"{providersDir}/providers_rob/uploads",
      "SGO"  : f"{providersDir}/providers_ltk/uploads",
      "UGA"  : f"{providersDir}/providers_uga-cnrs/uploads",
      "WUT"  : f"{providersDir}/providers_wut/uploads"
    }
    self.fromEmail         = fromEmail
    self.fromEmailPassword = fromEmailPassword
  
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
      server.quit()
    except Exception as err:
      pass
  
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