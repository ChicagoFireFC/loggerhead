"""
Logging module
"""

import logging

LOGGERS = [
    "",
    "core",
    "botocore",
    "boto3",
]


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

    def __init__(self, msg, env):
        logging.Formatter.__init__(self, msg)
        self.use_color = bool(env == "development")

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

    def __init__(self, env="development"):
        # Create custom logger logging all five levels
        log_level = logging.DEBUG if env == "development" else logging.INFO
        logger = logging.getLogger()
        logger.setLevel(log_level)

        # Define format for logs
        fmt = "%(levelname)8s:     %(message)s | (%(filename)s:%(lineno)d)"

        # Create stdout handler for logging to the console (logs all five levels)
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(log_level)
        stdout_handler.setFormatter(_CustomFormatter(fmt, env))

        for logger_name in LOGGERS:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            logger.propagate = False

            log_handler = logging.StreamHandler()
            log_handler.setLevel(log_level)
            log_handler.setFormatter(_CustomFormatter(fmt, env))
            logger.addHandler(log_handler)
