class UploadError(Exception):
  """Raised whenever upload fails.

  Parameters
  ----------
  Exception : Exception
    An Exception object
  """
  @staticmethod
  def format_error(error : str) -> str:
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