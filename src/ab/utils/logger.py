import sys
import logging
from pprint import pformat


class Logger:
    _LOG_LEVEL_ = "INFO"

    def __init__(self, name='ab', level=None):
        self.name = name
        self.level = level or Logger._LOG_LEVEL_
        self.logger = self.get_logger(self.name, self.level)

    @staticmethod
    def set_default_level(level):
        lv = level.upper()
        _logger_ = Logger("Logger", "INFO")
        _logger_.info("global log level set to %s" % lv)
        Logger._LOG_LEVEL_ = lv

    @staticmethod
    def get_handler():
        handler = logging.StreamHandler(sys.__stdout__)
        handler.setFormatter(Logger.get_formatter())
        return handler

    @staticmethod
    def get_logger(name, level):
        logger = logging.getLogger(name)
        # Why are there two setLevel() methods?
        # The level set in the logger determines which severity of messages it will pass to its handlers.
        # The level set in each handler determines which messages that handler will send on.
        logger.setLevel(level)
        logger.addHandler(Logger.get_handler())
        return logger

    @staticmethod
    def get_formatter():
        return logging.Formatter(fmt='[%(asctime)s] [%(process)d] [%(levelname)-4s] %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _format(args):
        """list of args to pretty string"""
        ret = []
        for arg in args:
            if isinstance(arg, (list, tuple, dict)):
                ret.append(pformat(arg))
            else:
                ret.append(str(arg))
        return ' '.join(ret)

    def set_level(self, level):
        self.level = level
        self.logger.setLevel(level)

    def debug(self, *args, **kwargs):
        """
        :param args:  ["string1", dict2, list3.....]
        :param kwargs: exc_info & stack_info
        """
        args = self._format(args)
        self.logger.debug(args, **kwargs)

    def info(self, *args, **kwargs):
        args = self._format(args)
        self.logger.info(args, **kwargs)

    def warning(self, *args, **kwargs):
        args = self._format(args)
        # yellow
        args = '\033[33m {args}  \033[0m'.format(args=args)
        self.logger.warning(args, **kwargs)

    def error(self, *args, **kwargs):
        args = self._format(args)
        # red
        args = '\033[31m {args} \033[0m'.format(args=args)
        self.logger.error(args, **kwargs)

    def critical(self, *args, **kwargs):
        args = self._format(args)
        self.logger.critical(args, **kwargs)

    def exception(self, *args, **kwargs):
        args = self._format(args)
        self.logger.exception(args, **kwargs)


default_logger = Logger()
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception
set_level = default_logger.set_level
