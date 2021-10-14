import os
import sys

from flask import current_app, Flask, send_from_directory, redirect
from flask.app import setupmethod

from ab.plugins.spring import eureka
from ab.utils import logger, reflection, algorithm, fixture, env, \
    serializer
from ab.plugins import kerberos
from ab.plugins.storage import dfs
from ab.plugins.db import db_master
from ab.plugins.calculate import spark
from ab.plugins.db import db_conn_pool
from ab.utils.mixes import run_once
from ab.utils.exceptions import ConfigException
from ab.config import Config, default_config


def jsonify(*args, **kwargs):
    """
    copy from flask.jsonify and patch jsonify dumps
    """
    indent = None
    separators = (',', ':')

    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
        indent = 2
        separators = (', ', ': ')

    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    return current_app.response_class(
        serializer.dumps(data, indent=indent, separators=separators) + '\n',
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )


class FlaskApp(Flask):
    """
    the simple flask server
    the wsgi logic is in __call__

    1. load and check flask config
    2. and config hooks
    """
    config_class = Config

    def __init__(self, name, root_path=os.getcwd(), *args, **kwargs):
        """
        :param config: the config module
        """
        # disable default static mapping
        super(FlaskApp, self).__init__(name, static_folder=None, root_path=root_path, *args, **kwargs)

        # /api/algorithm & /api/algorithm/
        self.url_map.strict_slashes = False

        # load framework default config
        self.config.from_object(default_config)

    @setupmethod
    @run_once(raise_error=True, msg='load_config should run only once, please remove tests/conftest.py since ab v2.4.7')
    def load_config(self, *config_list):
        if not config_list:
            return

        for config in config_list:
            if isinstance(config, dict):
                self.config.from_mapping(config)
            else:
                self.config.from_object(config)

        self.check_config()

    def check_config(self):
        if not self.config.APP_NAME and self.config.REGISTER_AT_EUREKA:
            raise ConfigException(
                'please set unique APP_NAME for eureka register\nAPP_NAME会影响到线上服务，如果不知道是什么请看文档')

        if self.config.DEBUG and self.config.get('HOST', '').strip() not in ('127.0.0.1', 'localhost', '[::]') \
                and sys.platform == 'linux':
            raise ConfigException('服务器上只允许在绑定localhost/127.0.0.1的情况下打开debug模式，请返回修改后重新启动')

        if self.config.PORT != 8000:
            logger.warning("在生产环境，gunicorn端口默认应该是8000。如果你修改了默认端口，务必要修改nginx的代理设置")

    @setupmethod
    @run_once(raise_error=True)
    def add_ab_static_url(self, config):
        """
        HTTP GET /$STATIC_URL_PATH/{filename} -> FILE $PWD/$STATIC_FOLDER/[filename}
        """
        if config.STATIC_URL_PATH is not None and config.STATIC_FOLDER is not None:
            def send_static_file(filename=None):
                if not filename:
                    return redirect(config.STATIC_URL_PATH + '/index.html')
                # copy from flask
                cache_timeout = self.get_send_file_max_age(filename)
                return send_from_directory(
                    config.STATIC_FOLDER, filename, cache_timeout=cache_timeout
                )

            self.add_url_rule(config.STATIC_URL_PATH,
                              endpoint="ab_static_root", view_func=send_static_file, )
            self.add_url_rule(config.STATIC_URL_PATH + "/<path:filename>",
                              endpoint="ab_static", view_func=send_static_file, )

    @setupmethod
    @run_once(msg='submodules already loaded, ignore')
    def load_submodules(self):
        # init logger
        if self.config.LOG_LEVEL:
            default_log_level = self.config.LOG_LEVEL
        else:
            default_log_level = 'DEBUG' if self.config.DEBUG else 'INFO'
        logger.Logger.set_default_level(default_log_level)
        # TODO
        logger.set_level(default_log_level)

        # env must be the first
        env.init_env(self.config)
        eureka.init_eureka_registry_client(self.config)
        kerberos.init_kerberos(self.config)
        spark.init_spark_builder(self.config)
        dfs.init_dfs_client(self.config)
        algorithm.register_all_algorithms(self.config)
        fixture.register_all_fixtures(self.config)
        db_conn_pool.init_db(self.config)
        db_master.init_dbm(self.config)
        self.add_ab_static_url(self.config)

        if self.config.TESTING:
            eureka.init_eureka_discovery_client(self.config)

        from ab.plugins.platform import Platform
        platform = Platform(self.config)
        platform.load_plugins()

        # DO NOT REMOVE: import all submodules after config loading
        import ab.controllers

    def run(self, host=None, port=None, debug=None, load_dotenv=None, config=[], **options):
        """
        load config and run
        just for debug
        """
        self.load_config(*config)
        self.load_submodules()

        if host is None:
            host = self.config.HOST
        if port is None:
            port = self.config.PORT
        if debug is None:
            debug = self.config.DEBUG
        if load_dotenv is None:
            if self.config.LOAD_DOTENV is not None:
                load_dotenv = self.config.LOAD_DOTENV
            else:
                load_dotenv = True

        super(FlaskApp, self).run(host, port, debug, load_dotenv, **options)
