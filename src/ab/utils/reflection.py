import sys
from importlib import util

from ab.utils import logger


def get_module_vars(module) -> dict:
    """
    get all vars from module
    """
    d = vars(module)
    return {k: v for k, v in d.items() if not k.startswith('_')}


def load_module_by_path(module_name, file_path):
    spec = util.spec_from_file_location(module_name, file_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Optional; only necessary if you want to be able to import the module
    # by name later.
    sys.modules[module_name] = module
    return module


class hook_module:
    def __init__(self, module, key: str, new_val):
        self.module = module
        self.key = key
        self.new_val = new_val

    def __enter__(self):
        self.old_val = getattr(self.module, self.key)
        setattr(self.module, self.key, self.new_val)
        return self

    def __exit__(self, exctype, excinst, exctb):
        setattr(self.module, self.key, self.old_val)


class PrintHook:
    warned = False

    def __init__(self):
        self.stdout = sys.__stdout__

    def write(self, text):
        if not PrintHook.warned:
            logger.warning(
                'print is hooked by ab.utils.logger.debug. set LOG_LEVEL to "DEBUG" to see logs')
            PrintHook.warned = True
        logger.debug(text)

    def __getattr__(self, name):
        # pass all other methods to self.stdout so that we don't have to override them
        return getattr(self.stdout, name)


def hook_print():
    """
    hook print to show warn info
    """
    sys.stdout = PrintHook()


if __name__ == '__main__':
    c = load_module_by_path('config', 'tests/config.py')
    print(get_module_vars(c))

    print('123')
    hook_print()
    print('456')
