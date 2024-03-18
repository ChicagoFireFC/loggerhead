"""
Logging module
"""

# Needed to ignore "Undefined name `dbutils`"
# ruff: noqa: F821

import logging

import rollbar
from databricks.sdk.runtime import dbutils
from rollbar.logger import RollbarHandler

LOGGERS = ["", "core"]


class _CustomFormatter(logging.Formatter):
    """
    Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    """

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"

    COLORS = {
        "WARNING": YELLOW,
        "INFO": GREEN,
        "DEBUG": BLUE,
        "CRITICAL": MAGENTA,
        "ERROR": RED,
    }

    # 23 miniumum spaces needed for CRITICAL messages (with color characters)
    DATE_FMT = "%Y-%m-%d | %H:%M:%S"

    def __init__(self, env):
        if env == "development":
            FMT = """{asctime} | {levelname:>23} | {message} | ({filename}:{lineno})"""
        else:
            FMT = """{asctime} | {levelname:>11} | {message} | ({filename}:{lineno})"""

        logging.Formatter.__init__(self, fmt=FMT, datefmt=self.DATE_FMT, style="{")
        self.use_color = env == "development"
        # print(f"use_color: {self.use_color}")

    def format(self, record):
        """
        Format Function
        """

        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            levelname_color = (
                self.BOLD_SEQ
                + self.COLOR_SEQ % (30 + self.COLORS[levelname])
                + levelname
                + self.RESET_SEQ
            )
            record.levelname = levelname_color

        return logging.Formatter.format(self, record)


class LoggerHead:
    """
    Custom class to set sane defaults for python logging
    """

    def _print_data_frame(self, data_frame):
        """
        print data frame in a more visually digestable way
        """
        logging.info("\n" + data_frame.to_string())

    def __init__(self, env="development"):
        if env == "production":
            rollbar.init(
                dbutils.secrets.get(scope="analytics", key="rollbar_access_token"),
                env,
            )

        # Add custom print_data_frame function
        logging.print_data_frame = self._print_data_frame

        # Create custom logger logging all five levels
        log_level = logging.DEBUG if env == "development" else logging.INFO

        # Define format for logs
        log_handler = logging.StreamHandler()
        log_handler.setLevel(log_level)
        log_handler.setFormatter(_CustomFormatter(env))

        rollbar_handler = RollbarHandler()
        rollbar_handler.setLevel(logging.ERROR)

        for logger_name in LOGGERS:
            logger = logging.getLogger(logger_name)

            # https://stackoverflow.com/questions/7173033/duplicate-log-output-when-using-python-logging-module
            if logger.hasHandlers():
                logger.handlers.clear()

            logger.setLevel(log_level)
            logger.addHandler(log_handler)
            logger.propagate = False

            if env == "production":
                logger.addHandler(rollbar_handler)
