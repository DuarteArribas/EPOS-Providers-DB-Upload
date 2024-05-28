class UploadError(Exception):
  """Raised whenever upload fails.

  Parameters
  ----------
  Exception : Exception
    An Exception object
  """
  @staticmethod
  def formatError(error):
    """Formats the error message.
    
    Parameters
    ----------
    error : str
      The error message
    
    Returns
    -------
    str
      The formatted error message
    """
    return error.replace("\n", "| ")