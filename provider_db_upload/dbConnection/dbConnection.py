import sys
import logging
import psycopg2

class DBConnection:
  """A database connection."""
  
  # == Methods ==
  def __init__(self : "DBConnection",host : str,port : int,db_name : str,username : str,password : str) -> None:
    """Init needed database parameters.

    Parameters
    ----------
    host         : str
      The host to connect to
    port         : str
      The port of the host
    db_name      : str
      The database to connect to
    username     : str
      The username of the user connecting to the database
    password     : str
      The password of the user
    """
    self.host         = host
    self.port         = port
    self.db_name      = db_name
    self.username     = username
    self.password     = password
    self.conn         = None
    self.cursor       = None
  
  def connect(self : "DBConnection") -> None:
    """Connect to the database."""
    try:
      self.conn = psycopg2.connect(
        host     = self.host,
        port     = self.port,
        database = self.db_name,
        user     = self.username,
        password = self.password
      )
      self.conn.autocommit = False
      self.cursor = self.conn.cursor()
    except Exception as err:
      logging.exception(err)
      sys.exit(-1)