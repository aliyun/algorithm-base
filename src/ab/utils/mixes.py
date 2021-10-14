import functools
from functools import update_wrapper

from ab.utils import logger
from ab.utils.exceptions import AlgorithmException


def lazy_property(func):
    attr_name = "_lazy__property" + func.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return _lazy_property


# see also: flask.helpers.locked_cached_property


def run_once(raise_error=False, msg=None):
    def outer(f):
        @functools.wraps(f)
        def wrapper_func(self, *args, **kwargs):
            attr_name = "run_once_" + f.__name__
            if hasattr(self, attr_name):
                info = msg or 'func {name} should run only once'.format(name=f.__name__)
                if raise_error:
                    raise AlgorithmException(data=info)
                else:
                    logger.info(info)
            else:
                setattr(self, attr_name, True)
                return f(self, *args, **kwargs)
        return wrapper_func
    return outer


def chunk_string(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


def first_char_lower(s: str):
    return s[:1].lower() + s[1:] if s else ''
