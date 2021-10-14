import threading


class BasePlugin(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(BasePlugin, "_instance"):
            with BasePlugin._instance_lock:
                if not hasattr(BasePlugin, "_instance"):
                    BasePlugin._instance = object.__new__(cls)
        return BasePlugin._instance
