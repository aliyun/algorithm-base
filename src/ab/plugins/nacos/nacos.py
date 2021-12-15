from ab.utils import logger
from ab.utils.prometheus import time_metrics
from ab.plugins.base_plugin import BasePlugin
from ab.utils.network import get_instance_ip
from ab.utils.exceptions import AlgorithmException

import nacos
import time
from threading import Timer


class NacosPlugin(BasePlugin):

    def __init__(self):
        BasePlugin.__init__(self)

        # the nacos heart beat timer
        self.__timer = None

        # the IP will be registed in nacos
        self.instance_ip = None

        self.platform = None
        self.client = None
        self.config = None

    def set_platform(self, platform):
        self.platform = platform

    def start(self, config):
        logger.info("[plugin] NacosPlugin start")

        self.config = config

        # no auth mode
        if "NACOS_SERVER" not in config:
            raise AlgorithmException(data="you have to config `NACOS_SERVER` in config.py")

        self.client = nacos.NacosClient(config.NACOS_SERVER)
        # auth mode
        # client = nacos.NacosClient(config.NACOS_SERVER,username="nacos", password="nacos")

        # regist service
        self.instance_ip = config.INSTANCE_IP if config.INSTANCE_IP != "" else get_instance_ip(config.NACOS_SERVER)
        self.client.add_naming_instance(config.APP_NAME, self.instance_ip, config.PORT)

        self.__timer = Timer(self.config.NACOS_DEFAULT_HEART_BEAT_INTERVAL_SECONDS, self.__heartbeat)
        self.__timer.daemon = True
        self.__timer.start()
        logger.info("start nacos server... ")

    def stop(self):
        logger.info("[plugin] NacosPlugin stop")
        self.__timer.cancel()

    def __heartbeat(self):
        while True:
            # logger.debug("send heart beat to nacos server... ")
            self.client.send_heartbeat(self.config.APP_NAME, self.instance_ip, self.config.PORT)

            time.sleep(self.config.NACOS_DEFAULT_HEART_BEAT_INTERVAL_SECONDS)

    def get_nacos_client(self):
        return self.client


nacos_plugin = NacosPlugin()
