import psycopg2
import sys
from src.utils.constants import *
from src.utils.logs      import *

class DBConnection:
  """A database connection."""
  
  # == Methods ==
  def __init__(self,host,port,databaseName,username,password,logger):
    """Init needed database parameters.

    Parameters
    ----------
    host         : str
      The host to connect to
    port         : str
      The port of the host
    databaseName : str
      The database to connect to
    username     : str
      The username of the user connecting to the database
    password     : str
      The password of the user
    logger       : Logs
      A logging object to which logs can be written
    """
    self.host         = host
    self.port         = port
    self.databaseName = databaseName
    self.username     = username
    self.password     = password
    self.logger       = logger
    self.conn         = None
    self.cursor       = None
  
  def connect(self):
    """Connect to the database."""
    try:
      self.conn = psycopg2.connect(
        host     = self.host,
        port     = self.port,
        database = self.databaseName,
        user     = self.username,
        password = self.password
      )
      self.conn.autocommit = False
      self.cursor = self.conn.cursor()
    except Exception as err:
      self.logger.writeRegularLog(Logs.SEVERITY.ERROR,dbConnectionError.format(errMsg = str(err).replace("\n","---")))
      sys.exit(-1)