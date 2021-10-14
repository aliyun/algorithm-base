from flask import request, Response

from ab import app
from ab.utils import logger
from ab.utils.exceptions import AlgorithmException
from ab.plugins.cache.redis import cache_plugin

# 不限制call次数
CALL_UNTRALIMIT = -1


def get_limit_key(key):
    return "limit:{}".format(key)


def legal(ak, sk):
    """
    验证ak和sk是否合法
    :param ak:
    :param sk:
    :return:
    """
    if ak is None or sk is None:
        return False

    cache_client = cache_plugin.get_cache_client()
    if str(cache_client.get(ak).strip(), 'UTF-8') == sk.strip():
        return True
    return False


def get_call_count(key):
    """
    获得调用次数
    :param key:
    :return:
    """
    cache_client = cache_plugin.get_cache_client()
    ret = cache_client.iget(key)

    return 0 if not ret else ret


def get_call_limit(key):
    """
    获得调用限制次数
    :param key:
    :return: -1 不允许调用
    """
    cache_client = cache_plugin.get_cache_client()
    ret = cache_client.iget(get_limit_key(key))

    return CALL_UNTRALIMIT if not ret else ret


def inc_call_count(key):
    """
    增加调用次数
    :param key:
    :return:
    """
    current_count = get_call_count(key)
    current_count = current_count + 1
    cache_client = cache_plugin.get_cache_client()
    cache_client.set(key, current_count)


@app.before_request
def before_call():
    path = request.path

    request.limit = False
    if request.path.startswith("/api/algorithm"):
        ak = request.args.get("ak")
        if legal(ak, request.args.get("sk")):
            request.ak = ak
            key = "{}:{}".format(ak, path)
            current_count = get_call_count(key)

            call_limit = get_call_limit(key)
            if call_limit != CALL_UNTRALIMIT:
                request.limit = True
                if not current_count < get_call_limit(key):
                    raise AlgorithmException(data="the API exceed the call limit : {}".format(key))
        else:
            raise AlgorithmException(data="wrong ak or sk")


@app.after_request
def post_call(response):
    path = request.path
    if request.limit:
        key = "{}:{}".format(request.ak, path)
        inc_call_count(key)
    request.ak = None
    return response


class CallLimit:

    def __init__(self):
        self.platform = None

    def set_platform(self, platform):
        self.platform = platform

    def start(self, config):
        logger.info("[plugin] CallLimit start")

    def stop(self):
        logger.info("[plugin] CallLimit stop")
