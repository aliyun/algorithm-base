import sqlalchemy

from sqlalchemy import MetaData, Table
from sqlalchemy.exc import NoSuchTableError

import thrift.transport.TSocket

from ab import app
from ab.utils import logger
from ab.plugins.db import db_conn_pool
from ab.plugins.db.base import DataBase
from ab.plugins.db.odps_helper import ODPS
from ab.utils.exceptions import AlgorithmException


def get_thrift_transport(host=None, port=None, username=None, auth=None, kerberos_service_name=None, password=None,
                         kerberos_host=None, socket_timeout_in_ms=None):
    """copy from pyhive/hive.py and patch"""
    if port is None:
        port = 10000
    if auth is None:
        auth = 'NONE'
    socket = thrift.transport.TSocket.TSocket(host, port)

    #################################################
    #             1. set socket timeout             #
    #################################################
    if socket_timeout_in_ms is not None:
        socket.setTimeout(socket_timeout_in_ms)  # in ms

    if auth == 'NOSASL':
        # NOSASL corresponds to hive.server2.authentication=NOSASL in hive-site.xml
        return thrift.transport.TTransport.TBufferedTransport(socket)
    elif auth in ('LDAP', 'KERBEROS', 'NONE', 'CUSTOM'):
        # Defer import so package dependency is optional
        import sasl
        import thrift_sasl

        if auth == 'KERBEROS':
            # KERBEROS mode in hive.server2.authentication is GSSAPI in sasl library
            sasl_auth = 'GSSAPI'
        else:
            sasl_auth = 'PLAIN'
            if password is None:
                # Password doesn't matter in NONE mode, just needs to be nonempty.
                password = 'x'

        def sasl_factory():
            sasl_client = sasl.Client()
            sasl_client.setAttr('host', host)
            if sasl_auth == 'GSSAPI':
                #################################################
                #          2. adapt for huawei hadoop           #
                #################################################
                if kerberos_host is not None:
                    sasl_client.setAttr('host', kerberos_host)

                sasl_client.setAttr('service', kerberos_service_name)
            elif sasl_auth == 'PLAIN':
                sasl_client.setAttr('username', username)
                sasl_client.setAttr('password', password)
            else:
                raise AssertionError

            #################################################
            #         3. copy from huawei just in case      #
            #################################################
            sasl_client.setAttr("maxbufsize", 16777215)

            sasl_client.init()
            return sasl_client

        return thrift_sasl.TSaslClientTransport(sasl_factory, sasl_auth, socket)
    else:
        # All HS2 config options:
        # https://cwiki.apache.org/confluence/display/Hive/Setting+Up+HiveServer2#SettingUpHiveServer2-Configuration
        # PAM currently left to end user via thrift_transport option.
        raise NotImplementedError(
            "Only NONE, NOSASL, LDAP, KERBEROS, CUSTOM "
            "authentication are supported, got {}".format(auth))


class Hive(DataBase):
    def __init__(self, host, port, db, username, password=None):
        self.sampler_class = Sampler
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password

        if password is not None:
            auth = 'LDAP'
            kerberos_service_name = None
        else:
            auth = 'KERBEROS'
            kerberos_service_name = 'hive'
        thrift_transport = get_thrift_transport(host=host, port=port,
                                                username=username,
                                                auth=auth,
                                                password=password,
                                                kerberos_service_name=kerberos_service_name,
                                                kerberos_host=app.config.get('HUAWEI_KERBEROS_HOST'),
                                                socket_timeout_in_ms=app.config.HIVE_TIMEOUT * 1000,
                                                )
        self.connect_args = {'port': None, 'database': db, 'thrift_transport': thrift_transport}
        self.engine = db_conn_pool.get_engine("hive://", connect_args=self.connect_args)


    def execute(self, query, *args, **kwargs):
        # only for debug
        self.last_query = str(query)

        with self.engine.connect() as conn:
            result = conn.execute(query, *args, **kwargs)

            action = query.strip().split()[0].upper()
            if action in ('SELECT', 'SHOW', 'DESC'):
                return [dict(r) for r in list(result)]
            else:
                return result

    def table(self, table_name):
        try:
            table = Table(table_name, MetaData(bind=self.engine), autoload=True)
        except NoSuchTableError:
            raise AlgorithmException(data="no such table '{}' in hive".format(table_name))
        except Exception as e:

            raise AlgorithmException(data="hive error")
        return table

    def column_names(self, table_name):
        table = self.table(table_name)
        return table.columns.keys()

    def get_table_size_in_KB(self, table_name):
        # only works for non-partitioned table
        result = self.execute('SHOW TBLPROPERTIES {table_name}("rawDataSize")'.format(table_name=table_name))
        try:
            return int(result[0]['prpt_name']) / 1024
        except:
            return None

    @staticmethod
    def hive_to_xlab_type(data_type):
        """
        https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Types#LanguageManualTypes-decimal
        """
        data_type = str(data_type).lower()
        if data_type in ('tinyint', 'smallint', 'int', 'integer', 'bigint'):
            return 'Long'
        elif data_type in ('float', 'double', 'numeric') or 'decimal' in data_type:
            return 'Double'
        elif data_type in ('string', 'char', 'varchar'):
            return 'String'
        elif data_type == 'boolean':
            return 'Boolean'
        elif data_type in ('date', 'timestamp', 'interval'):
            return 'Date'
        else:
            raise TypeError('不支持的hive数据类型: {data_type}'.format(data_type=data_type))

    def table_info(self, table_name, with_row_count=False):
        '''
        returns table info in db
        returns: {
            'type': data source type,
            'size': table size in KB,
            'row_count': row count in db, optional,
            'columns': [
                {'field': 'name', 'type': 'varchar', 'xlabType': 'String', 'comment': '公司名称'},
                {'field': 'f1', 'type': 'double', 'xlabType': 'Double', comment': '年总销售额'}
                ],
            'partitions': ['p1=v1/p2=v2']
        '''
        table = self.table(table_name)
        columns = [{'field': c.name, 'type': str(c.type).lower(), 'xlabType': self.hive_to_xlab_type(c.type),
                    'comment': c.comment or ''} for _, c in table.columns.items()]
        partitions = self.partitions(table_name)

        ret = {
            'type': 'hive',
            'size': self.get_table_size_in_KB(table_name),
            'columns': columns,
            'partitions': partitions,
        }
        if with_row_count:
            pass
        return ret

    def partitions(self, table_name):
        """
        return all partitions string
        returns:
            None: not a partitioned table
            []: no data
            ['p1=v1/p2=v2', 'p1=v3/p2=v4']
        """
        try:
            result = self.execute('SHOW PARTITIONS {table_name}'.format(table_name=table_name))
            return [r['partition'] for r in result]
        except sqlalchemy.exc.OperationalError as e:
            if 'is not a partitioned table' in str(e):
                return None

    def sample(self, table_name, partitions=None):
        column_names = self.column_names(table_name)
        sample = self.sampler.sample(table_name, column_names=column_names, partitions=partitions)
        sample_count = len(sample)
        return None, sample_count, sample


class Sampler:
    @staticmethod
    def get_instance(db: Hive, config: dict):
        '''
        args:
            config: {
                'type': random,
                'count': max sample size
                }
        '''
        config = app.config.FORCE_SAMPLER or config or app.config.SAMPLER

        assert config['type'] == 'head'
        assert isinstance(config.get('count'), int) and config['count'] > 0, \
            'sampler.count must be positive interger, not string'
        return HeadSampler(db, config)

    @property
    def key(self):
        return '{self._type}.{self.max_count}'.format(self=self)

    def __init__(self, db: Hive, config: dict):
        self.db = db
        self._type = config['type']
        self.max_count = config['count']


class HeadSampler(Sampler):
    """
    return head rows
    """

    def sample(self, table_name: str, column_names: list, partitions: list):
        """
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_data
        """
        condition = ODPS.join_partitions(partitions)
        if condition:
            where = ' where {condition}'.format(condition=condition)
        else:
            where = ''

        fields = ', '.join(column_names)
        sql = 'select {fields} from {table_name}{where} limit {self.max_count}'.format(
            fields=fields, table_name=table_name, where=where, self=self)

        logger.debug('sample sql:', sql)
        return self.db.table_sql(sql, table_name, column_names)



