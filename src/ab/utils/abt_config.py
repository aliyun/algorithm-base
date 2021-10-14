import os
import configparser


class AbtConfig(object):
    def __init__(self):
        self.abt_config = {}
        config_parser = configparser.RawConfigParser()
        config_parser.read(os.environ["HOME"] + os.sep + ".abt" + os.sep + "config", "utf-8")
        secs = config_parser.sections()
        for sec in secs:
            items = config_parser.items(sec)
            for item in items:
                if len(item) == 2:
                    self.abt_config[item[0]] = item[1]

    def get_value(self, key):
        return self.abt_config.get(key)


config = AbtConfig()
