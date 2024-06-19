import os
import gzip
import shutil
import smtplib
import checksumdir
from utils.config    import *
from email.mime.text import MIMEText

class FileHandler:
  """Handle provider files."""
  
  # Attributes
  CONFIG_FILE = "config/appconf.ini"
  
  # == Methods ==
  def __init__(self : "FileHandler",providers_dir : dict,from_email : str,from_email_password : str,con = None) -> None:
    """Get default parameters.

    Parameters
    ----------
    providers_dir       : dict
      A dictionary containing the upload directory for each provider
    from_email          : str
      The email address to send the email from
    from_email_password : str
      The password of the , which is sending the email
    con                 : Connection
      A connection object to the local database
    """
    self.provider_dir       = {
      "INGV" : providers_dir["INGV"],
      "ROB"  : providers_dir["ROB"],
      "SGO"  : providers_dir["SGO"],
      "UGA"  : providers_dir["UGA"],
      "WUT"  : providers_dir["WUT"]
    }
    self.from_email          = from_email
    self.from_email_password = from_email_password
    self.con                 = con
    self.cfg = Config(FileHandler.CONFIG_FILE)
  
  def get_list_of_hashed_changed(self : "FileHandler") -> list:
    """Get the list of hashes changed.

    Returns
    -------
    list
      A list containing a boolean for each provider, indicating if their hash was changed (True) or not (False)
    """
    cur             = self.con.cursor()
    provider_list   = list(self.provider_dir.keys())
    provider_hashed = [self._get_hash_of_dir(provider_dir) for provider,provider_dir in self.provider_dir.items()]
    hashes_changed  = [False,False,False,False,False]
    for i in range(len(provider_list)):
      res          = cur.execute(f"SELECT fileHash FROM previousFiles WHERE fileName LIKE '{provider_list[i]}'")
      previous_hash = res.fetchall()
      if provider_hashed[i] != previous_hash[0][0]:
        hashes_changed[i] = True
    return hashes_changed
  
  def _get_hash_of_dir(self : "FileHandler",dir : str) -> str:
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

  def update_hashes(self : "FileHandler") -> None:
    """Update the hashes in the database."""
    cur = self.con.cursor()
    for provider,provider_dir in self.provider_dir.items():
      new_file_hash = self._get_hash_of_dir(provider_dir)
      cur.execute(f"UPDATE previousFiles SET fileHash = ? WHERE fileName LIKE ?",(new_file_hash,provider))
      self.con.commit()
  
  def send_email(self : "FileHandler",subject : str,body : str,to_email : str) -> None:
    """Email errors to providers.

    Parameters
    ----------
    subject  : str
      The email subject
    body     : str
      The email body
    to_email : str
      The provider's email address
    """
    try:
      server = smtplib.SMTP("smtp.gmail.com",587)
      server.connect("smtp.gmail.com",587)
      server.ehlo()
      server.starttls()
      server.ehlo()
      server.login(self.from_email,self.from_email_password)
      msg = MIMEText(body)
      msg["Subject"] = subject
      server.sendmail(self.from_email,to_email,msg.as_string())
      server.sendmail(self.from_email,self.cfg.config.get("EMAIL","SEGAL_EMAIL"),msg.as_string())
      server.quit()
    except Exception as err:
      logging.exception(err)
  
  def send_email_to_segal(self : "FileHandler",subject : str,body : str) -> None:
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
      server.login(self.from_email,self.from_email_password)
      msg = MIMEText(body)
      msg["Subject"] = subject
      server.sendmail(self.from_email,self.cfg.config.get("EMAIL","SEGAL_EMAIL"),msg.as_string())
      server.quit()
    except Exception as err:
      logging.exception(err)
  
  def move_snx_file_to_public(self : "FileHandler",snx_file : str,public_dir : str) -> None:
    """Move an snx file to the public directory, according to {public_dir}/Coor/{version}/{snx_file}

    Parameters
    ----------
    snx_file   : str
      The snx file to move
    public_dir : str
      The public directory of the correspondent provider
    """
    try:
      with gzip.open(snx_file,"rt") as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines[lines.index("+FILE/COMMENT") + 1:lines.index("-FILE/COMMENT")]:
          if line.split(":")[0].strip() == "ReleaseVersion":
            version    = "".join(line.split(":")[1:])
            path_to_move = f"{public_dir}/Coor/{version}"
            if not os.path.exists(path_to_move):
              os.makedirs(path_to_move)
            shutil.move(snx_file,path_to_move)
            break
    except Exception as err:
      logging.exception(err)
    
  def move_pbo_file_to_bucket(self : "FileHandler",pbo_file : str,bucket_dir : str,file_type : str,version : str) -> None:
    """Move a pbo file to the bucket directory, according to {bucket_dir}/{file_type}/{version}/{pbo_file}

    Parameters
    ----------
    pbo_file   : str
      The pbo file to move
    bucket_dir : str
      The bucket directory of the correspondent provider
    file_type  : str
      The type of the file (TS or VEL)
    version    : str
      The release number
    """
    try:
      path_to_move = f"{bucket_dir}/{file_type}/{version}"
      if not os.path.exists(path_to_move):
        os.makedirs(path_to_move)
      shutil.copy(pbo_file,path_to_move)
      os.remove(pbo_file)
    except Exception as err:
      print(err)
  
  def move_solution_to_public(self : "FileHandler",solution_dir : str,public_dir : str,file_type : str) -> None:
    """Move a solution directory to the public directory, according to {public_dir}/{file_type}/{solution_dir}.
    
    Parameters
    ----------
    solution_dir : str
      The solution directory to move
    public_dir   : str
      The public directory of the correspondent provider
    file_type    : str
      The type of the file (TS or VEL)
    """
    try:
      path_to_move = f"{public_dir}/{file_type}"
      if not os.path.exists(path_to_move):
        os.makedirs(path_to_move)
      if not os.path.exists(os.path.join(path_to_move,solution_dir.split("/")[-1])):
        os.makedirs(os.path.join(path_to_move,solution_dir.split("/")[-1]))
      for file in os.listdir(solution_dir):
        shutil.copy(os.path.join(solution_dir,file),os.path.join(path_to_move,solution_dir.split("/")[-1]))
        os.remove(os.path.join(solution_dir,file))
    except Exception as err:
      logging.exception(err)