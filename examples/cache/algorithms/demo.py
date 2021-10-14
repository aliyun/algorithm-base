from ab.utils import logger
from ab.utils.algorithm import algorithm


"""
要使用缓存必须配置config.REDIS。配置好之后缓存客户端会自动生成cache_client参数
bget/bset接口 Since ab v2.6.3
"""


# 会自动暴露为/api/algorithms/save接口
@algorithm()
def save(task_id, cache_client, val):
    """
    :param task_id: 每次执行algorithm的时候ab框架自动生成的全局唯一的id
    :param cache_client: 缓存客户端，配置config.REDIS即可自动生成
    :param val: 接口传递过来的缓存val
    :return: 缓存key
    """
    # key显然需要是个str
    key = 'result:' + task_id
    # val大小不能太大，要考虑redis缓存的总大小
    # ex是超时时间，单位秒，必填。86400秒=1天
    cache_client.bset(key, val, ex=86400)
    # 写入成功返回key
    return key


# 会自动暴露为/api/algorithms/load接口
@algorithm()
def load(cache_client, key: str):
    val = cache_client.bget(key)
    if val is None:
        # save的时候val不建议为None，会导致和key不存在的情况无法区分
        logger.error('key不存在')
    return val
