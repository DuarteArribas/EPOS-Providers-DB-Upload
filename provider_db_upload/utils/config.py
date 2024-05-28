import sys
import configparser
from utils.constants import *

class Config:
  """A config tool, which reads from the given configuration file."""
  
  # == Methods ==
  def __init__(self : "Config",config_file : str) -> None:
    """Set the default configuration of the config reading tool.
    
    Parameters
    ----------
    config_file : str
      The configuration file to read from
    """
    self.config = configparser.RawConfigParser()
    config_list = self.config.read(config_file)
    if len(config_list) == 0:
      print(ERROR_MSG["CONFIG_READ"],file = sys.stderr)
      exit(-1)