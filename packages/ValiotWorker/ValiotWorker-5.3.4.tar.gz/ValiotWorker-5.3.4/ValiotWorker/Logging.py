# terminal styles for better logging
import os
import sys
import logging
import useful.logs
from enum import Enum
from colorama import Fore, Back, Style, init as init_term, AnsiToWin32
from termcolor import colored
# colorful terminal initializacion
init_term(wrap=True, autoreset=True)
stream = AnsiToWin32(sys.stderr).stream


def logging_level_setup():
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "SUCCESS": logging.INFO,
        "WARNING": logging.ERROR,
        "ERROR": logging.ERROR,
    }
    current_env = os.environ.get('ENV')
    sys_log_lvl = os.environ.get('LOG_LEVEL')
    if current_env == 'dev':
        default_log_lvl = levels[sys_log_lvl] if sys_log_lvl else logging.DEBUG
        useful.logs.setup(log_level=default_log_lvl)
    else:
        default_log_lvl = levels[sys_log_lvl] if sys_log_lvl else logging.INFO
        useful.logs.setup(log_level=default_log_lvl)


logging_level_setup()

# avoid logging unneeded "requests" library logs (messing around with app logs)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# if the above error (unneeded logs) happen again, these lines will print the possible culprits:
# from pprint import pprint
# loggers = [logging.getLogger(name).name for name in logging.root.manager.loggerDict]
# pprint(loggers)


class LogLevel(Enum):
    DEBUG = 'DEBUG'  # Blue
    ERROR = 'ERROR'  # Red
    INFO = 'INFO'   # White
    WARNING = 'WARNING'  # Yellow
    SUCCESS = 'SUCCESS'  # ! Green, Non-standard with Eliot (might not care)


class LogStyle(Enum):
    PREFIX_FIRST_LINE = 'PREFIX_FIRST_LINE'
    PREFIX_ALL_LINES = 'PREFIX_ALL_LINES'
    JSON = 'JSON'

# print wrappers


def get_str_logger(color):
    """
      builds a logger function and binds the font color to it

      Parameters
      ----------
      color: str
        a string representation of the color to bind ("red", "blue", etc)
    """
    def logger(message):
        """
        color-binded logging function

        Parameters
        ----------
        message: str
            the message to send to stdout
        """
        print(colored(message, color))
    return logger


str_loggers = {
    LogLevel.INFO: get_str_logger('white'),
    LogLevel.SUCCESS: get_str_logger('green'),
    LogLevel.WARNING: get_str_logger('yellow'),
    LogLevel.ERROR: get_str_logger('red'),
    LogLevel.DEBUG: get_str_logger('blue')
}


def log(level: LogLevel, message: str, extra: dict = {}):
    """Logs formatted messages to stdout

    Parameters
    ----------
    level : LogLevel
        Message Level and color related to it (DEBUG, ERROR, etc, see LogLevel type)
    message : Any
        Message to log
    """
    str_loggers[level](message)


# json formatted in the worker setup
json_logger = logging.getLogger(__name__)

json_loggers = {
    LogLevel.INFO: json_logger.info,
    LogLevel.SUCCESS: json_logger.info,
    LogLevel.WARNING: json_logger.warning,
    LogLevel.ERROR: json_logger.error,
    LogLevel.DEBUG: json_logger.debug,
}


def json_log(level: LogLevel, message: str, extra: dict = {}):
    """Logs formatted messages to stdout

    Parameters
    ----------
    level : LogLevel
        Message Level(DEBUG, ERROR, etc, see LogLevel type)
    message : Any
        Message to log
    extra: dict
        Extra json fields to send in the JSON object
    """
    json_loggers[level](message, extra={"status": level.value, **extra})
