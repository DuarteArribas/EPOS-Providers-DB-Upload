import psycopg2

class DBConnection:
  """A database connection."""
  
  # == Methods ==
  def __init__(self,host,port,databaseName,username,password):
    """Init needed database parameters
    """
    self.host         = host
    self.port         = port
    self.databaseName = databaseName
    self.username     = username
    self.password     = password
    self.conn         = None
    self.cursor       = None
  
  def connect(self):
    self.conn = psycopg2.connect(
      host     = self.host,
      port     = self.port,
      database = self.databaseName,
      user     = self.username,
      password = self.password
    )
    self.cursor = self.conn.cursor()
  