import psycopg2

class DBConnection:
  """A database connection."""
  
  # == Methods ==
  def __init__(self,host,port,databaseName,username,password):
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
    """
    self.host         = host
    self.port         = port
    self.databaseName = databaseName
    self.username     = username
    self.password     = password
    self.conn         = None
    self.cursor       = None
  
  def connect(self):
    """Connect to the database."""
    self.conn = psycopg2.connect(
      host     = self.host,
      port     = self.port,
      database = self.databaseName,
      user     = self.username,
      password = self.password
    )
    self.cursor = self.conn.cursor()