import os

from ab.utils import logger
from ab.config import Config, default_config

PROJECT_DEFAULT_CONFIG_PATH = 'config.py'


def read_local_config_files(config_str=None, root='config'):
    """
    # UPPER CASE for flask and ab
    # lower case for gunicorn
    """
    config = Config()
    # 1. load framework default config
    config.from_object(default_config)

    # 2. load project default config
    pdc = os.path.join(root, PROJECT_DEFAULT_CONFIG_PATH)
    if os.path.isfile(pdc):
        config.from_pyfile(pdc)
    else:
        logger.warning("\n{pdc} doesn't exist, please make sure you are running from the app root."
                       " Read the doc for more information".format(pdc=pdc))
        input("Press ENTER to continue anyway")

    if not config_str:
        config.from_mapping(os.environ)

        config.check()
        return config
    else:
        # 3. load cmd line config
        for c in config_str.split(','):
            if os.path.isfile(c):
                config.from_pyfile(c)
            else:
                path1 = os.path.join(root, 'config_{c}.py'.format(c=c))
                path2 = os.path.join(root, '{c}.py'.format(c=c))
                if os.path.isfile(path1):
                    config.from_pyfile(path1)
                elif os.path.isfile(path2):
                    config.from_pyfile(path2)
                else:
                    raise FileNotFoundError("neither {path1} nor {path2} exists".format(path1=path1, path2=path2))

    # 4. load from env
    config.from_mapping(os.environ)

    config.check()
    return config
