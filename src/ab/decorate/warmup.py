warmups = {}


class WarmUpFunction:

    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func()


def warmup(name=None):
    """
    register func for model warmup
    the 'warm up' function must be a function without parameters
    """

    def register_func(func):
        register_warmup(name, func)
        return func

    return register_func


def register_warmup(name, func):
    name = name or func.__name__

    warmups[name] = WarmUpFunction(name, func)


def do_warmup(worker):
    for k, v in warmups.items():
        v()
