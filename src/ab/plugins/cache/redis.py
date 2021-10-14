import redis
import time

from ab.utils import logger
from ab.utils.prometheus import time_metrics
from ab.plugins.base_plugin import BasePlugin
from prometheus_client import Counter

from ab.utils import logger, serializer
from ab.utils.exceptions import AlgorithmException
from ab.utils.prometheus import func_metrics

c_cache_hits = Counter("cache_hits_total", "cache hits")
c_cache_wait_timeout_count = Counter("cache_wait_timeout_count_total", "count of wait for cache ready until timeout")


class CachePlugin(BasePlugin):

    def __init__(self):
        BasePlugin.__init__(self)
        self.platform = None
        self.redis_pool = None

    def set_platform(self, platform):
        self.platform = platform

    def start(self, config):
        logger.info("[plugin] CachePlugin start")

        self.init_redis_pool(config)

    def stop(self):
        logger.info("[plugin] CachePlugin stop")

    @time_metrics('redis')
    def init_redis_pool(self, config):
        # process-safe && thread-safe
        self.redis_pool = redis.BlockingConnectionPool(**config.REDIS)

        conn = redis.StrictRedis(connection_pool=self.redis_pool)
        # check password. raise on fail: redis.exceptions.ResponseError
        conn.ping()

    def get_connection(self):
        if not self.redis_pool:
            raise AttributeError('redis not initialized')
        return redis.StrictRedis(connection_pool=self.redis_pool)

    @staticmethod
    def get_cache_client():
        if cache_plugin.redis_pool:
            return RedisCache()
        return NoCache()


class NoCache():
    def get_set_cache(self, key, value_generator, *args, **kwargs):
        return value_generator()


class RedisCache():
    def __init__(self):
        self.conn = cache_plugin.get_connection()
        super().__init__()

    def flushall(self):
        logger.warning('you are using redis.flushall, which is very dangerous')
        return self.conn.flushall()

    def _keys(self, pattern='*') -> list:
        """
        WARNING: pause redis。never use this in prod env
        """

        bin_keys = self.conn.keys(pattern)
        return [k.decode('utf-8') for k in bin_keys]

    '''common'''

    @func_metrics('redis')
    def ttl(self, key: str):
        return self.conn.ttl(key)

    @func_metrics('redis')
    def expire(self, key: str, ttl):
        return self.conn.expire(key, ttl)

    @func_metrics('redis')
    def delete(self, *keys):
        return self.conn.delete(*keys)

    @func_metrics('redis')
    def exists(self, *keys):
        return self.conn.exists(*keys)

    '''any type. may be slow'''

    @func_metrics('redis')
    def bget(self, key):
        """
        :return: None if key not exists
        """
        bval = self.conn.get(key)
        if bval is None:
            return None
        return serializer.loads_bin(bval)

    @func_metrics('redis')
    def bset(self, key, value, ex, px=None, nx=False, xx=False):
        if value is None:
            logger.warning("value for key '{key}' is None, identical to 'key not exist'".format(key=key))
        bval = serializer.dumps_bin(value)
        return self.conn.set(key, bval, ex, px, nx, xx)

    '''string'''

    @func_metrics('redis')
    def get(self, key: str):
        """
        :return: None if key not exists
        """
        return self.conn.get(key)

    '''int'''

    @func_metrics('redis')
    def iget(self, key: str):
        """
        :return: None if key not exists
        """
        ret = self.conn.get(key)
        return int(ret) if ret else ret

    @func_metrics('redis')
    def set(self, key: str, value, ex=None, px=None, nx=False, xx=False):
        return self.conn.set(key, value, ex, px, nx, xx)

    '''hash'''

    @func_metrics('redis')
    def hgetall(self, key: str) -> dict:
        """
        :return: {} if key not exists
        """
        h = self.conn.hgetall(key)
        return {k.decode('utf-8'): v for k, v in h.items()}

    @func_metrics('redis')
    def hmset(self, key: str, mapping: dict, ex=None):
        # TODO pipeline
        ret = self.conn.hmset(key, mapping)
        if ex:
            self.expire(key, ex)
        return ret

    '''set'''

    @func_metrics('redis')
    def smembers(self, key: str) -> set:
        return self.conn.smembers(key)

    @func_metrics('redis')
    def sadd(self, key: str, *values):
        return self.conn.sadd(key, *values)

    @func_metrics('redis')
    def srem(self, *keys):
        return self.conn.srem(*keys)

    '''cache'''

    def delete_table_cache(self, table_key):
        """
        delete all cache in table set
        TODO lua script
        """
        cache_keys = self.smembers(table_key)
        if cache_keys:
            self.delete(*cache_keys)
            self.srem(table_key, *cache_keys)

    def get_set_cache(self, key, value_generator, redis_type='string', expire=None, table_key=None):
        """
        try to get cache from redis.
        if no cache found, generate one, save it then return.

        :param key: key to store cache
        :param value_generator: function for generate value
        :param redis_type:  string/hash
        :param expire: expire time
        :param table_key:  the table that this cache belongs to
        :return: cached value
        """
        try:
            value = self.get_set_cache_inner(key, value_generator, redis_type, expire)
            # TODO move to another place
            if table_key:
                # save cache in table set
                self.sadd(table_key, key)
                self.expire(table_key, expire)
            return value
        except Exception as e:
            mutex_key = 'mutex:' + key
            self.delete(key, mutex_key)
            raise e

    @func_metrics('get_set_cache')
    def get_set_cache_inner(self, key, value_generator, redis_type='string', expire=None):
        '''
        尝试获取缓存。如果没有缓存就加锁然后更新

        注意：如果redis_type=='hash'，value_generator必须生成一个dict，
             且此函数返回的dict的value类型都是bytes，需要手动转换
        '''
        from ab.utils import logger

        if redis_type == 'string':
            getter = self.get
            setter = self.set
        elif redis_type == 'hash':
            getter = self.hgetall
            setter = self.hmset

        value = getter(key)
        if (redis_type == 'string' and value is not None) or \
                (redis_type == 'hash' and value):
            logger.debug('{key} get cache'.format(key=key))
            c_cache_hits.inc()
            return value

        logger.debug('{key} not cached'.format(key=key))
        mutex_key = 'mutex:' + key
        # 锁固定超时时间10分钟
        if self.set(mutex_key, 1, ex=600, nx=True):
            # 获取锁
            logger.debug('get lock, loading data from db')
            if value_generator is None:
                raise AlgorithmException('value_generator is None, cannot generate cache value')
            # 生成value，扔到redis里
            value = value_generator()
            setter(key, value, ex=expire)
            self.delete(mutex_key)
        else:
            # 没有获取锁
            logger.debug('unable to get lock, wait until get cache')
            # 轮询，直到缓存已经准备好
            for _ in range(600):
                time.sleep(1)
                if self.exists(key):
                    break
            logger.debug('get cache')
            value = getter(key)
            if value in ({}, None):
                c_cache_wait_timeout_count.inc()
        return value

    @func_metrics('bget_set_cache')
    def bget_set_cache(self, key, value_generator, expire):
        '''
        二进制存取缓存
        '''
        from ab.utils import logger

        value = self.bget(key)
        if value is not None:
            logger.debug('{key} get cache'.format(key=key))
            c_cache_hits.inc()
            return value

        logger.debug('{key} not cached'.format(key=key))
        mutex_key = 'mutex:' + key
        # 锁固定超时时间10分钟
        if self.set(mutex_key, 1, ex=600, nx=True):
            # 获取锁
            logger.debug('get lock, loading data from db')
            if value_generator is None:
                raise AlgorithmException('value_generator is None, cannot generate cache value')
            # 生成value，扔到redis里
            value = value_generator()
            self.bset(key, value, ex=expire)
            self.delete(mutex_key)
        else:
            # 没有获取锁
            logger.debug('unable to get lock, wait until get cache')
            # 轮询，直到缓存已经准备好
            for _ in range(600):
                time.sleep(1)
                if self.exists(key):
                    break
            logger.debug('get cache')
            value = self.bget(key)
            if value in ({}, None):
                c_cache_wait_timeout_count.inc()
        return value


cache_plugin = CachePlugin()
