import os


class AbConfig(object):
    def __init__(self):
        self.ab_config = {}
        if not os.path.exists("./.ab"):
            return
        with open("./.ab") as file:
            lines = file.readlines()
        for line in lines:
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue
            (key, _, value) = line.partition("=")
            self.ab_config[key] = value.strip()

    def get_value(self, key):
        return self.ab_config.get(key)

    def get_all_values(self):
        return self.ab_config

    def is_load(self):
        if not bool(self.ab_config):
            print("you should run the command under a project root and put the .ab config file under the folder.")
            exit(-1)


config = AbConfig()
