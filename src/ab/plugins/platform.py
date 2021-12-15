import os
import importlib

from ab.utils import logger

plugin_alias = {}
plugin_alias["cache"] = "REDIS"
plugin_alias["nacos"] = "NACOS_SERVER"


class Platform:
    def __init__(self, config):
        self.config = config

    def load_plugins(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))

        for filename in os.listdir(dirname):
            if os.path.isdir(os.path.join(dirname, filename)):
                self.run_plugin(dirname, filename)

    def run_plugin(self, dirname, filename):

        def load_plugin():
            logger.warning("prepare to run plugin at {}".format(os.path.join(dirname, filename)))
            plugin = self.get_plugin(filename, "ab.plugins")
            if plugin is not None:
                plugin.set_platform(self)
                plugin.start(self.config)

        if filename in plugin_alias.keys() and plugin_alias[filename] in self.config.keys():
            load_plugin()
        elif bool(getattr(self.config, "enable_{}".format(filename))) is True:
            load_plugin()
        else:
            return

    def get_plugin(self, module_name, package_name):
        plugin_path = package_name + "." + module_name
        module = importlib.import_module(plugin_path)

        if not hasattr(module, "plugin_instance"):
            logger.warning("it's NOT a plugin: {}".format(module_name))
            return None
        logger.warning("loading plugin {}".format(plugin_path))

        plugin_instance = getattr(module, "plugin_instance")
        return plugin_instance
