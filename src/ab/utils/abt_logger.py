import logging
from ab.utils.logger import Logger
from logging import handlers


class AbtLogger(Logger):
    @staticmethod
    def get_logger(name, level):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        th = handlers.TimedRotatingFileHandler(filename="/tmp/abt.log", when="D", backupCount=5, encoding='utf-8')
        th.setFormatter(AbtLogger.get_formatter())
        logger.addHandler(th)
        return logger


default_logger = AbtLogger()
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception
set_level = default_logger.set_level

