import logging
import logging.handlers
import os
import sys
import traceback
from typing import Optional, List

from modelbit.api import MbApi
from modelbit.error import ModelbitException, UserFacingException

from .ux import printTemplate

logger = logging.getLogger(__name__)


def enableFileLogging():
  return os.environ.get("MB_LOG", None) is not None


def initLogging():
  LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
  streamHandler = logging.StreamHandler()
  handlers: List[logging.Handler] = [streamHandler]
  streamHandler.setLevel(LOGLEVEL)
  if enableFileLogging():
    try:
      import appdirs
      logDir = appdirs.user_log_dir("modelbit")
      if not os.path.exists(logDir):
        os.mkdir(logDir)
      fileHandler = logging.handlers.RotatingFileHandler(os.path.join(logDir, "log.txt"),
                                                         maxBytes=10485760,
                                                         backupCount=5)
      fileHandler.setLevel(level="INFO")
      handlers.append(fileHandler)
    except Exception as e:
      print(e)
      logging.info(e)

  logging.basicConfig(level="INFO", handlers=handlers)


def _logErrorToWeb(mbApi: Optional[MbApi], userErrorMsg: str):
  from modelbit.api import MbApi
  mbApi = mbApi or MbApi()
  errStack = traceback.format_exception(*sys.exc_info())[1:]
  errStack.reverse()
  errorMsg = userErrorMsg + "\n" + "".join(errStack)
  try:
    mbApi.getJson("api/cli/v1/error", {"errorMsg": errorMsg})
  except Exception as e:
    logger.info(e)


def eatErrorAndLog(mbApi: Optional[MbApi], genericMsg: str):

  def decorator(func):

    def innerFn(*args, **kwargs):
      error = None  # Stored error so stack trace doesn't contain our internals.
      try:
        return func(*args, **kwargs)
      except UserFacingException as e:
        if e.logToModelbit:
          _logErrorToWeb(mbApi, e.userFacingErrorMessage)
        printTemplate("error", None, errorText=genericMsg + " " + e.userFacingErrorMessage)
        error = e.userFacingErrorMessage
      except Exception as e:
        specificError = getattr(e, "userFacingErrorMessage", None)
        errorMsg = genericMsg + (" " + specificError if specificError is not None else "")
        _logErrorToWeb(mbApi, errorMsg)
        printTemplate("error_details", None, errorText=errorMsg, errorDetails=traceback.format_exc())
        error = errorMsg
      # Convert to generic ModelbitException.
      if error is not None:
        raise ModelbitException(error)

    return innerFn

  return decorator
