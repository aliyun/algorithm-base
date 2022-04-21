# ! python3
import random
import re

import sqlite3
from ab.utils.prometheus import func_metrics

from ab import app
from ab.utils import logger
from ab.plugins.db.base import DataBase
from ab.utils.exceptions import DataAPIException
from ab.utils.logger import Logger

varchar_regex = re.compile(r'varchar\((\d+)\)')


class Sqlite(DataBase):

    def __init__(self, db, autocommit=True):
        self.sampler_class = Sampler
        self.db = db
        self.autocommit = autocommit
        self.connect(db, autocommit)

    def connect(self, db, autocommit, charset='utf8'):
        self.connection = sqlite3.connect(self.db)

    def reconnect(self):
        self.connection.ping(reconnect=True)

    @property
    def jdbc_url(self):
        pass

    def inner_execute(self, sql, args=None):
        try:
            action = sql.strip().split()[0].upper()
            cursor = self.connection.cursor()
            # logger.debug(sql)
            # logger.debug(args)

            if args:
                num = cursor.execute(sql, args)
            else:
                num = cursor.execute(sql)

            # todo: other operation
            if action.lower() in ('select', 'show', 'pragma'):
                return cursor.fetchall()
            else:
                return num

        finally:
            self.connection.commit()
            # self.connection.close()

    @func_metrics('rds_execute')
    def execute(self, sql, args=None):
        """
        WARNING: this func has no sql injection prevention. don't use this unless you know what you're doing
        """
        return self.inner_execute(sql, args)

    @staticmethod
    def gen_where(conditions):
        """
        :param conditions:
                {
                    'key': val                  ->      key = val
                    'key:contains': val             ->      key LIKE %val%
                    #TODO 'a:le|a:ge': 'val1,val2'    ->      a <= val1 OR a >= val2
                }
        :return:
        """
        where = []
        values = []
        for key_operator, value in conditions.items():
            if ':' not in key_operator:
                key = key_operator
                operator = 'eq'
            else:
                key, operator = key_operator.split(':')

            key = Sqlite.escape(key)
            m = {
                'eq': lambda k, v: ('{0} = %s'.format(k), v),
                'gt': lambda k, v: ('{0} > %s'.format(k), v),
                'gte': lambda k, v: ('{0} >= %s'.format(k), v),
                'lt': lambda k, v: ('{0} < %s'.format(k), v),
                'lte': lambda k, v: ('{0} <= %s'.format(k), v),
                'contains': lambda k, v: ('{0} LIKE %s'.format(k), '%{v}%'.format(v=v))
            }
            condition, value = m[operator](key, value)
            where.append(condition)
            values.append(value)
        return ' where ' + ' and '.join(where), values

    @staticmethod
    def gen_fields_str(fields):
        if fields == '*':
            return '*'
        if isinstance(fields, str):
            fields = fields.split(',')
        return ', '.join([Sqlite.escape(f) for f in fields])

    def select(self, table, fields='*', conditions=None, order_by=None, start=0, num=None):
        fields_str = self.gen_fields_str(fields)
        sql = 'SELECT {fields_str} FROM {table}'.format(fields_str=fields_str, table=Sqlite.escape(table))
        values = []

        if conditions:
            where, values = self.gen_where(conditions)
            sql += where
        if order_by:
            if ' ' in order_by:
                order_by, order = order_by.split(' ')
                order = order.upper()
                assert order in ('ASC', 'DESC')
            else:
                order = ''
            sql += ' ORDER BY ' + Sqlite.escape(order_by)
            if order:
                sql += ' ' + order
        if num is not None:
            sql += ' LIMIT ? offset ?'
            values.extend([num, start])
        return self.execute(sql, values)

    def select_one(self, table, conditions=None, order_by=None):
        ret = self.select(table, conditions=conditions, order_by=order_by, num=1)
        if ret and len(ret) > 0:
            return ret[0]
        else:
            return None

    def select_one_by_id(self, table, id):
        return self.select_one(table, {'id': id})

    def count(self, table, conditions=None):
        if not table:
            raise DataAPIException("you have to specify a table name, but can't be None")

        sql = 'SELECT *  FROM {0}'.format(Sqlite.escape(table))
        if not conditions:
            result = self.execute(sql)
        else:
            where, values = self.gen_where(conditions)
            result = self.execute(sql + where, values)
        return len(result)

    def insert(self, table, kwargs):
        """
        :return: last row id
        """
        sql = 'INSERT INTO {table} ({columns}) VALUES ({values})'.format(
            table=Sqlite.escape(table),
            columns=', '.join(map(Sqlite.escape, kwargs.keys())),
            values=', '.join(['%s'] * len(kwargs))
        )
        # keys() and values() hold the same order
        return self.execute(sql, list(kwargs.values()))

    def update(self, table, kwargs, conditions):
        where, where_values = self.gen_where(conditions)
        sql = 'UPDATE {table} SET {columns} {where}'.format(
            table=Sqlite.escape(table),
            columns=', '.join(['{0} = %s'.format(Sqlite.escape(key)) for key in kwargs.keys()]),
            where=where
        )
        # keys() and values() hold the same order
        args = list(kwargs.values())
        args.extend(where_values)
        return self.execute(sql, args)

    def update_one_by_id(self, table, kwargs, id):
        return self.update(table, kwargs, {'id': id})

    def insert_on_dup_update(self, table, kwargs):
        sql = 'INSERT INTO {table} ({columns}) VALUES ({values}) ON DUPLICATE KEY UPDATE {kv}'.format(
            table=Sqlite.escape(table),
            columns=', '.join(map(Sqlite.escape, kwargs.keys())),
            values=', '.join(['%s'] * len(kwargs)),
            kv=', '.join([(Sqlite.escape(k) + ' = %s') for k in kwargs])
        )
        # keys() and values() hold the same order
        return self.execute(sql, list(kwargs.values()) * 2)

    def delete(self, table, conditions):
        where, values = self.gen_where(conditions)
        sql = 'DELETE FROM {table} {where}'.format(table=table, where=where)
        return self.execute(sql, values)

    def delete_one_by_id(self, table, id):
        return self.delete(table, {'id': id})

    # multi-row insert or replace
    def execute_many(self, sql, args):
        logger.debug(sql)
        logger.debug(args)
        with self.connection.cursor() as cursor:
            return cursor.executemany(sql, args)

    def insert_many(self, table: str, args: list, columns: list = None) -> int:
        if not args or len(args) == 0:
            return 0

        if not columns:
            # args is a list of kv dict
            columns = args[0].keys()
            # not sure of values order in different dict
            # get them manually
            values = [[item[c] for c in columns] for item in args]
        else:
            # args is a list of values
            values = args

        sql = 'INSERT INTO {table} ({columns}) VALUES ({values})'.format(
            table=Sqlite.escape(table),
            columns=', '.join(map(Sqlite.escape, columns)),
            values=', '.join(['%s'] * len(columns))
        )
        return self.execute_many(sql, values)

    def get_column_meta(self, table_name: str) -> list:
        return self.execute('pragma table_info({table_name})'.format(table_name=table_name))
        # return self.execute('select * from {table_name}'.format(table_name=table_name))

    def get_table_size_in_KB(self, table_name: str) -> int:
        # todo
        return 0

    @staticmethod
    def rds_to_xlab_type(_type: str):
        ''' 把rds的类型转换成xlab的类型表示'''
        _type = _type.lower()
        if any(string_type in _type for string_type in ['char', 'text', 'json', 'enum']):
            return 'String'
        elif 'tinyint(1)' in _type:
            return 'Boolean'
        elif 'int' in _type:
            return 'Long'
        elif any(float_type in _type for float_type in ['float', 'double', 'decimal']):
            return 'Double'
        elif any(date_type in _type for date_type in ['date', 'time', 'year']):
            return 'Date'
        else:
            raise TypeError('不支持的rds数据类型: {_type}'.format(_type=_type))

    def table_info(self, table_name, with_row_count=False):
        '''
        returns table info in db
        returns: {
            'type': data source type,
            'size': table size in KB,
            'row_count': row count in db, optional,
            'columns': [
                    {'field': 'name', 'type': 'varchar(100)', 'xlabType': 'String', 'comment': '公司名称'},
                    {'field': 'f1', 'type': 'double', 'xlabType': 'Double', comment': '年总销售额'}
                ]
        '''
        sqlite_columns = self.get_column_meta(table_name)

        columns = []
        for item in sqlite_columns:
            c = dict()
            c["field"] = item[1]
            c["type"] = item[2]
            c["comment"] = ""
            columns.append(c)

        for column in columns:
            column['xlabType'] = self.rds_to_xlab_type(column['type'])
        table_size = self.get_table_size_in_KB(table_name)
        ret = {
            'type': 'mysql',
            'size': table_size,
            'columns': columns
        }
        if with_row_count:
            ret['row_count'] = self.count(table_name)
        return ret

    def sample(self, table_name, *args, **kwargs):
        '''
        sample max_pt(table_name)
        args:
            self.max_count: rows to be returned at most

        returns:
            sample_rate, sample_count, sample_data
        '''
        total_count = self.count(table_name)

        if total_count <= self.sampler.max_count:
            logger.debug('total_count: {total_count}, max_count: {self.sampler.max_count}'.format(
                total_count=total_count, self=self))
            logger.debug('no need to sample, run sql: select * from {table_name}'.format(table_name=table_name))
            sql = 'SELECT * FROM {table_name}'.format(table_name=self.escape(table_name))
            return 100, total_count, self.table_sql(sql, table_name)

        return self.sampler.sample(table_name, total_count)

    def table_sql(self, sql, table_name, column_names: list = None):
        """
        return sql result over table
        """
        rows = self.execute(sql)
        return rows

    def close(self):
        return self.connection.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass


class Sampler:
    @staticmethod
    def get_instance(db: Sqlite, config: dict):
        '''
        args:
            config: {
                'type': random,
                'count': max sample size
                }
        '''
        config = app.config.FORCE_SAMPLER or config or app.config.SAMPLER

        assert isinstance(config.get('count'), int) and config['count'] > 0, \
            'sampler.count must be positive interger, not string'

        if not hasattr(config, 'type'):
            return RandomSampler(db, config)

        if config['type'] == 'random':
            return RandomSampler(db, config)
        elif config['type'] == 'head':
            return HeadSampler(db, config)
        else:
            raise ValueError('unknown sampler type:', config['type'])

    @property
    def key(self):
        return '{self._type}.{self.max_count}'.format(self=self)

    def __init__(self, db: Sqlite, config: dict):
        self.db = db
        self._type = config.get('type') or ""
        self.max_count = config.get('count') or 0


class RandomSampler(Sampler):
    def sample(self, table_name: str, total_count: int):
        '''
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_rate, sample_count, sample_data
        '''
        assert total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        table_name = Sqlite.escape(table_name)

        # step 1: try to get random self.max_count rows
        # 可以近似推导出当尝试取(2 * self.max_count + 16)行的时候取出来的行数有99.99%的概率(4个标准差)大于self.max_count行
        # 大概推导过程：
        #   假设要从n行的表中取m行。m乘以一个系数k，使得尽可能保证取出来的行数大于m行
        #   每行是否参与采样的概率p = km / n，每行执行一次，共n次，这是个B(km/n, n)的二项分布。
        #   二项分布重复n次，根据中央极限定理，结果总和服从正态分布，期望=km，方差=km * (1 - km / n)
        #   且99.993666%的概率在平均数左右四个标准差的范围内
        #   即k要满足公式：km - 4 * sqrt(km * (1 - km / n)) >= m
        #   当 n -> ∞，可得解：k >= (2 + 16 / m)，即 mk >= 2m + 16
        mk = 2 * self.max_count + 16
        rand = (total_count - mk) / total_count  # rand < 0 is ok
        sql = 'SELECT * FROM {table_name} WHERE random() > {rand}'.format(table_name=table_name, rand=rand)
        sample = self.db.table_sql(sql, table_name)
        logger.debug('try to sample {mk} rows'.format(mk=mk))
        logger.debug('run sql:', sql)
        logger.debug('get sample count:', len(sample))

        # step 2: sample self.max_count rows
        if len(sample) > self.max_count:
            sample = random.sample(sample, self.max_count)
        row_count = len(sample)
        return 100.0 * row_count / total_count, row_count, sample


class HeadSampler(Sampler):
    def sample(self, table_name: str, total_count: int):
        '''
        args:
            total_count: total row count of target partitions or whole table
        returns:
            sample_rate, sample_count, sample_data
        '''
        assert total_count > self.max_count, 'system error, total_count must be greater than sampler max_count'

        sample = self.db.select(table_name, num=self.max_count)

        row_count = len(sample)
        return 100.0 * row_count / total_count, row_count, sample
