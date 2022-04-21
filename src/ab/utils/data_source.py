import time

from ab import app
from ab.services import data_source as data_source_service
from ab.utils import logger
from ab.plugins.db.rds import RDS
from ab.plugins.db.sqlite import Sqlite
from ab.plugins.db.odps_helper import ODPS
from ab.utils.prometheus import time_metrics
from ab.plugins.cache.redis import cache_plugin


class DataSource:
    '''
    unique facade for rds/odps data_sources
    '''

    @staticmethod
    @time_metrics('data_source_lazy')
    def get_instance(data_source: dict = None, args: dict = None, cacheable=True, sampler=None, **kwargs):
        '''
        根据数据源配置生成db
        '''
        if not data_source:
            # some api may not use data_source
            return None

        table_name = data_source.get("table_name") or args.get('table_name') or kwargs.get("table_name")
        sql = data_source.get("sql") or args.get('sql') or kwargs.get("sql")
        partitions = data_source.get("partitions") or args.get('partitions') or kwargs.get("partitions")

        if cacheable:
            return CachedDataSource(data_source, table_name, partitions, sampler, sql=sql)
        else:
            return DataSource(data_source, table_name, partitions, sampler, sql=sql)

    @staticmethod
    def get_instance_by_id(data_source_id, table_name, partitions=None, cacheable=True, sampler=None, **kwargs):
        '''
        根据数据源配置生成db
        '''
        if not data_source_id:
            # some api may not use data_source
            return None

        data_source = data_source_service.get_data_source_by_id(data_source_id)

        # TODO args.get('fields')
        if cacheable:
            return CachedDataSource(data_source, table_name, partitions, sampler)
        else:
            return DataSource(data_source, table_name, partitions, sampler)

    @staticmethod
    def retrieve_datasource_object(data_object):
        """
        :param data_object:
        :return: return the data object if it's a datasource object. else return None
        """
        if not data_object:
            return None

        datasource_field = ['host', 'port', 'db', 'username', 'password', 'access_id', 'access_key', 'project',
                            'endpoint', 'tunnel_endpoint']
        for item in datasource_field:
            if hasattr(data_object, item):
                if getattr(data_object, item):
                    return data_object
        return None

    @staticmethod
    def init_db(data_source):
        _type = data_source.get('type', 'mysql').lower()
        if _type in ('mysql', 'ads'):
            return RDS(data_source['host'], data_source['port'], data_source['db'],
                       data_source['username'], data_source['password'])
        elif _type == 'odps':
            return ODPS(data_source['access_id'], data_source['access_key'],
                        data_source['project'], data_source['endpoint'],
                        data_source.get('tunnel_endpoint'))
        elif _type == 'hive':
            from ab.plugins.db.hive import Hive
            return Hive(data_source['host'], data_source['port'], data_source['db'],
                        data_source['username'], data_source.get('password'))
        if _type in ('sqlite'):
            return Sqlite(data_source['db'])
        else:
            raise TypeError('不支持的数据源类型：' + data_source['type'])

    def __init__(self, data_source, table_name, partitions: list = None, sampler_config: dict = None, sql=None):
        self.type_ = data_source.get('type', 'mysql').lower()
        self.db = self.init_db(data_source)
        self.table_name = table_name
        self.partitions = partitions
        self.sql = sql
        self.db.set_sampler(sampler_config)

    def sample(self):
        tic = time.time()
        ret = self.db.sample(self.table_name, partitions=self.partitions)
        toc = time.time()
        logger.debug('sample time:', toc - tic)
        return ret

    def data(self):
        tic = time.time()
        ret = self.db.execute(self.sql)
        toc = time.time()
        logger.debug('sample time:', toc - tic)
        return ret

    def close(self):
        # no close for odps
        try:
            self.db.close()
        except Exception as e:
            pass

    def get_table_info(self, with_row_count=False):
        return self.db.table_info(self.table_name, with_row_count)


class CachedDataSource(DataSource):
    def __init__(self, data_source, table_name, partitions: list = None, sampler_config: dict = None, sql=None):
        super(CachedDataSource, self).__init__(data_source, table_name, partitions, sampler_config, sql)

        db = self.db
        # init keys
        if self.type_ in ('mysql', 'ads'):
            self.table_key = 'rds://{}:{}/{}.{}.pickle'.format(db.host, db.port, db.db, table_name)
            self.cache_key = 'rds://{}:{}/{}.{}:{}.pickle'.format(db.host, db.port, db.db, table_name, db.sampler.key)
        elif self.type_ in ('sqlite'):
            self.table_key = 'sqlite://{}.{}.pickle'.format(db.db, table_name)
            self.cache_key = 'sqlite://{}.{}:{}.pickle'.format(db.db, table_name, db.sampler.key)
        elif self.type_ == 'odps':
            if partitions:
                partitions = '|' + ','.join(partitions)
            else:
                partitions = ''
            self.table_key = 'odps://{}/{}.{}.pickle'.format(db.endpoint, db.project, table_name)
            self.cache_key = 'odps://{}/{}.{}{}:{}.pickle'.format(db.endpoint, db.project, table_name, partitions,
                                                                  db.sampler.key)
        elif self.type_ == 'hive':
            if partitions:
                partitions = '|' + ','.join(partitions)
            else:
                partitions = ''
            self.table_key = 'hive://{}:{}/{}.{}.pickle'.format(db.host, db.port, db.db, table_name)
            self.cache_key = 'hive://{}:{}/{}.{}{}:{}.pickle'.format(db.host, db.port, db.db, table_name, partitions,
                                                                     db.sampler.key)

    def delete_table_cache(self):
        cache_client = cache_plugin.get_cache_client()
        return cache_client.delete_table_cache(self.table_key)

    def sample_to_bytes(self, sample) -> bytes:
        from ab.utils import serializer
        return serializer.dumps_bin(sample)

    def bytes_to_sample(self, binary: bytes):
        from ab.utils import serializer
        return serializer.loads_bin(binary)

    def sample(self):
        '''
        如果配置了redis，会使用redis做缓存

        注意：
        odps里decimal类型的字段会读取为Decimal类型（df里显示为object），
        但to_msgpack无法dump decimal类型，需要手动转成float64，会造成精度丢失。
        如果确实需要精度，需自行实现取数据逻辑
        rds的decimal会自动读取成float64，无需处理，和网上查的不一样，不知道为什么。以防万一依然统一转化下

        TODO 这里没有检查用户名密码是否合法，可能有安全性隐患
        '''

        def value_generator():
            sample_rate, sample_count, sample = super(CachedDataSource, self).sample()
            # redis.exceptions.DataError: Invalid input of type: 'NoneType'. Convert to a byte, string or number first.
            return {'sample_rate': sample_rate if sample_rate is not None else b'',
                    'sample_count': sample_count,
                    'sample_data': self.sample_to_bytes(sample)
                    }

        # invoke cache
        cache_client = cache_plugin.get_cache_client()
        tic = time.time()
        c = cache_client.get_set_cache(self.cache_key, value_generator, redis_type='hash',
                                       expire=app.config.CACHE_TIMEOUT, table_key=self.table_key)
        sample_rate = float(c['sample_rate']) if c['sample_rate'] != b'' else None
        sample_count = int(c['sample_count'])
        sample_data = self.bytes_to_sample(c['sample_data'])
        toc = time.time()
        logger.debug('cache time:', toc - tic)
        return sample_rate, sample_count, sample_data
