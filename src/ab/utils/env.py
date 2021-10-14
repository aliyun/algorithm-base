import os

from ab.utils import logger


def init_env(config):
    if not config.ENVAR:
        return

    for k, v in config.ENVAR.items():
        os.environ[k] = v
        logger.info('export {k}={v}'.format(k=k, v=v))