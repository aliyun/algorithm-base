from ab.utils.algorithm import algorithm
from ab.utils.exceptions import Message


@algorithm('exception')
def exception():
    return 1 / 0


@algorithm('msg')
def msg():
    raise Message('hello world')
