import os
import time
from typing import Any, Optional

from akerbp.mlops.core.logger_config import LOGGING_CONFIG

base_name = "main"


class CDFLogger:
    """
    Create a logger that mocks logging.Logger with only print statements.
    """

    def __init__(self, name: str = base_name):
        self.name = name

    def _log(self, level: str, msg: str, args):
        """
        A helper method that prints the log message with the appropriate log level.
        """
        print(
            f"{time.strftime(LOGGING_CONFIG['formatters']['standard']['datefmt'])}"
            f" - {self.name} - {level} - {msg % args}"
        )

    def info(self, msg: str, *args, **kwargs):
        self._log("INFO", msg, args)

    def debug(self, msg: str, *args, **kwargs):
        self._log("DEBUG", msg, args)

    def warning(self, msg: str, *args, **kwargs):
        self._log("WARNING", msg, args)

    def error(self, msg: str, *args, **kwargs):
        self._log("ERROR", msg, args)

    def critical(self, msg: str, *args, **kwargs):
        self._log("CRITICAL", msg, args)

    def exception(self, msg: str, *args, **kwargs):
        self._log("EXCEPTION", msg, args)

    def log(self, level: str, msg: str, *args, **kwargs):
        self._log(level, msg, args)

    def __repr__(self):
        return f"CDFLogger(name={self.name})"

    def __str__(self):
        return self.name


def get_logger(
    name: str = base_name,
    platform: Optional[str] = os.getenv("DEPLOYMENT_PLATFORM"),
) -> Any:  # Returns CDFLogger or logging.Logger but can't put import at top of module due to CDF issues
    """
    Set up a stream logger based on a global logging config.

    Args:
        name (str): name of the logger. Defaults to the global base_name variable

    Returns:
        (Logger): logger object
    """
    # can't use config module for this one or there would be circular imports
    if platform == "cdf":
        return CDFLogger(name)

    import logging
    from logging import config as logging_config

    logging_config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    logging.captureWarnings(True)

    return logger
