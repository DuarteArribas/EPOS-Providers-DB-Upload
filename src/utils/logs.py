import datetime
import logging
import re
from enum import Enum

class Logs:
  """A logging system, that formats logs according to their severity.

  Attributes
  ----------
  SEVERITY       : enum
    The logs severity in an easier to write way
  MIN_NUM_LOGS   : int
    The minimum number of logs allowed
  MAX_NUM_LOGS   : int
    The maximum number of logs allowed 
  LOG_TYPE       : enum
    The type of log. ROUTINE_START and ROUTINE_END mean that the log delimits the start and end
    of a routine. SUBROUTINE_START and SUBROUTINE_END mean that the log delimits the start and end
    of a subroutine. OTHER means it's a regular log
  ROUTINE_STATUS : enum
    START means the start of a routine (or subroutine) and END means the end of a routine (or subroutine)
  """
  # == Class variables ==
  SEVERITY       = Enum(
    "SEVERITY","DEBUG INFO WARNING ERROR CRITICAL"
  )
  MIN_NUM_LOGS   = 100
  MAX_NUM_LOGS   = 100000
  LOG_TYPE       = Enum(
    "LOG_TYPE","ROUTINE_START ROUTINE_END SUBROUTINE_START SUBROUTINE_END SUBSUBROUTINE_START SUBSUBROUTINE_END OTHER"
  )
  ROUTINE_STATUS = Enum(
    "ROUTINE_STATUS","START END"
  )
  # == Methods ==
  def __init__(self,loggingFile,maxLogs):
    """Set the default configuration of the logging tool to write to a specific file with a specific format.
    
    Parameters
    ----------
    loggingFile : str
      The file to log to
    maxLogs     : int
      The max quantity of allowed logs. Older logs will be deleted if this number is surpassed, so 
      that the number of logs will not be more than maxLogs
    """
    maxLogs = int(maxLogs)
    self.loggingFile = loggingFile
    if maxLogs > Logs.MAX_NUM_LOGS:
      self.maxLogs = Logs.MAX_NUM_LOGS
    elif maxLogs < Logs.MIN_NUM_LOGS:
      self.maxLogs = Logs.MIN_NUM_LOGS
    else:
      self.maxLogs = maxLogs
    logging.basicConfig(level = logging.INFO,filename = loggingFile,format = "%(message)s")

  def writeRoutineLog(self,message,routineStatus):
    """Write a routine log to a file, according to its routine status.

    Parameters
    ----------
    message       : str
      The log message
    routineStatus : enum
      START means the start of a routine and END means the end of a routine
    """
    if routineStatus == Logs.ROUTINE_STATUS.START:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.ROUTINE_START,message))
    else:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.ROUTINE_END,message))

  def writeSubroutineLog(self,message,routineStatus):
    """Write a subroutine log to a file, according to its routine status.

    Parameters
    ----------
    message       : str
      The log message
    routineStatus : enum
      START means the start of a subroutine and END means the end of a subroutine
    """
    if routineStatus == Logs.ROUTINE_STATUS.START:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.SUBROUTINE_START,message))
    else:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.SUBROUTINE_END,message))

  def writeSubsubroutineLog(self,message,routineStatus):
    """Write a subsubroutine log to a file, according to its routine status.

    Parameters
    ----------
    message       : str
      The log message
    routineStatus : enum
      START means the start of a subroutine and END means the end of a subroutine
    """
    if routineStatus == Logs.ROUTINE_STATUS.START:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.SUBSUBROUTINE_START,message))
    else:
      self._writeLog(Logs.SEVERITY.INFO,Logs._getLogMsg(Logs.LOG_TYPE.SUBSUBROUTINE_END,message))

  def writeRegularLog(self,severity,message):
    """Write a regular log to a file, according to its severity.

    Parameters
    ----------
    severity : enum
      The severity of the log
    message  : str
      The log message
    """
    self._writeLog(severity,Logs._getLogMsg(Logs.LOG_TYPE.OTHER,message))

  def writeNewRunLog(self,message):
    """Write a log, which is a new run of the file.

    Parameters
    ----------
    message  : str
      The log message
    """
    logging.critical("\n"+message)

  def _writeLog(self,severity,message):
    """Write a log to a file, according to its severity. Debug logs are not 
    written, but are the default if the parameter is misspelled.

    Parameters
    ----------
    severity : enum
      The severity of the log
    message  : str
      The log message
    """
    formattedMessage = Logs._setLogMsg(severity,message)
    if severity   == Logs.SEVERITY.DEBUG:
      logging.debug(formattedMessage)
    elif severity == Logs.SEVERITY.INFO:
      logging.info(formattedMessage)
    elif severity == Logs.SEVERITY.WARNING:
      logging.warning(formattedMessage)
    elif severity == Logs.SEVERITY.ERROR:
      logging.error(formattedMessage)
    elif severity == Logs.SEVERITY.CRITICAL:
      logging.critical(formattedMessage)
    else:
      logging.debug(formattedMessage)

  @staticmethod
  def _setLogMsg(severity,message):
    """Format the logging message, so that it stays aligned. The date, severity and message are logged.

    Parameters
    ----------
    severity : enum
      The severity of the log
    message  : str
      The log message
    """
    severityString = str(severity).split(".")[1]
    return f"{datetime.datetime.now()} ({severityString}){' '*(8-len(severityString))} | {message}"

  @staticmethod
  def _getLogMsg(logType,message):
    """Get the log message, according to its type.

    Parameters
    ----------
    logType  : enum
      The type of the log
    message  : str
      The log message
    
    Returns
    ----------
    str
      The formatted log message, according to its type
    """
    if logType == Logs.LOG_TYPE.ROUTINE_START:
      return "=== " + message + " (START) ==="
    elif logType == Logs.LOG_TYPE.ROUTINE_END:
      return "=== " + message + " (END) ==="
    elif logType == Logs.LOG_TYPE.SUBROUTINE_START:
      return "== " + message + " (START) =="
    elif logType == Logs.LOG_TYPE.SUBROUTINE_END:
      return "== " + message + " (END) =="
    elif logType == Logs.LOG_TYPE.SUBSUBROUTINE_START:
      return "= " + message + " (START) ="
    elif logType == Logs.LOG_TYPE.SUBSUBROUTINE_END:
      return "= " + message + " (END) ="
    else:
      return message + "."