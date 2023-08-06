import logging
import logging.config

__doc__ = """
Logger
======

Based on:
https://docs.python.org/3/howto/logging-cookbook.html#formatting-times-using-utc-gmt-via-configuration

https://realpython.com/lessons/logger-dictionary/

The Galaxy Project has the same base:
https://docs.galaxyproject.org/en/release_20.05/admin/config_logging.html

Collected logger for this repo and to abstract out the config for logger

https://docs.python.org/3/library/logging.html#logrecord-attributes
"""


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class UTCFormatter(logging.Formatter):
    """Force UTC time in log messages"""

    converter = logging.time.gmtime


class UTCColorFormatter(logging.Formatter):
    """Force UTC time in log messages and add color to log level"""

    converter = logging.time.gmtime
    # debug
    cyan = "\033[36m"
    # info
    green = "\033[32m"
    # warning
    yellow = "\033[33m"
    # error
    red = "\033[31m"
    # critical
    bold_red = "\033[91m"
    reset = "\033[0m"

    start_str = "[%(asctime)s.%(msecs)03dZ]"

    end_str = ": %(name)s : %(message)s"

    datefmt = "%Y-%m-%dT%H:%M:%S"

    FORMATS = {
        logging.DEBUG: f"{start_str} {cyan}%(levelname)s{reset} {end_str} ",
        logging.INFO: f"{start_str} {green}%(levelname)s{reset} {end_str}",
        logging.WARNING: f"{start_str} {yellow}%(levelname)s{reset} {end_str}",
        logging.ERROR: f"{start_str} {red}%(levelname)s{reset} {end_str}",
        logging.CRITICAL: f"{start_str} {bold_red}%(levelname)s{reset} {end_str}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


class HideMessageStartswith(logging.Filter):
    """Filter out the schema from the log

    from: https://stackoverflow.com/a/879937
    """

    def __init__(self, text):
        self.text = text

    def filter(self, record):
        return not record.getMessage().startswith(self.text)
