callbacks = {}


class CallbackFunction:

    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func()


def on_starting(name=None):
    """
    the 'callback' function must be a function without parameters
    """

    def register_func(func):
        register_callback(name, func)
        return func

    return register_func


def register_callback(name, func):
    name = name or func.__name__

    callbacks[name] = CallbackFunction(name, func)


def do_callback(server):
    for k, v in callbacks.items():
        v()
