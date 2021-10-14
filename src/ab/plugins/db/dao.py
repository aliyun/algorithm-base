"""
mappers for db
"""
from functools import partial

import sqlalchemy
from ab.utils.prometheus import func_metrics
from sqlalchemy.sql import Select, Insert

from ab.plugins.db import db_conn_pool
from sqlalchemy import *
from ab.utils import serializer, logger
from ab.utils.exceptions import AlgorithmException, DuplicatedKeyException


class Mapper:
    def __init__(self, table_name, db: str=None, json_columns=[], primary_key='id', global_filter: str=None,
                 default_order_by: str=None, default_page_size=10, print_sql=False, *args, **kwargs):
        self.table_name = table_name
        self.db = db
        self.print_sql = print_sql
        self.engine_name = self.engine.name
        self.meta = MetaData()
        self.table = Table(table_name, self.meta,
                           # for oracle
                           # Column('id', Integer, Sequence(table_name + '_id'), primary_key=True),
                           autoload=True, autoload_with=self.engine)

        assert set(json_columns).issubset(self.column_names),\
            'unknown column(s) in json_columns: ' + str(set(json_columns) - set(self.column_names))
        self.json_columns = json_columns

        assert primary_key in self.column_names, 'unknown column: primary key {pk}'.format(pk=primary_key)
        self.primary_key = primary_key
        self.global_filter = global_filter
        self.default_order_by = default_order_by or (primary_key + ' DESC')
        self.default_page_size = default_page_size

    @property
    def engine(self):
        """
        这里有个神奇的bug：如果使用self.engine属性而不是property的话，multiprocessing.Pool里的任务会无法执行
        原因是Pool使用queue.Queue来传输task参数，但在尝试入队的时候在multiprocessing/pool.py的425行报了个
        can't pickle _thread.RLock objects 异常，导致任务根本没有入队，也就没有执行了。为什么报这个异常没有研究，以后有空再说
        """
        if self.db:
            return db_conn_pool.get_engine(self.db, self.print_sql)
        else:
            return db_conn_pool.get_default_engine()

    @property
    def tables(self):
        return self.meta.tables.keys()

    @property
    def column_names(self):
        return [c.name for c in self.table.columns]

    # FIXME: this in-progress matrics will increase infinitely in async unlimited mode
    @func_metrics(name=lambda self, query, *args, **kwargs: self.engine_name + '_execute')
    def execute(self, query, *args, **kwargs):
        # only for debug
        self.last_query = str(query)

        # TODO save conn for transaction, like RDS
        with self.engine.connect() as conn:
            try:
                result = conn.execute(query, *args, **kwargs)
            except sqlalchemy.exc.IntegrityError as e:
                raise DuplicatedKeyException() from e
            else:
                if isinstance(query, Select):
                    return [dict(r) for r in list(result)]
                else:
                    return result

    def dumps(self, row: dict):
        """return a new copy"""
        if not row:
            return row
        return {k: (serializer.dumps(v) if k in self.json_columns else v) for k, v in row.items()}

    def loads(self, row: dict):
        """return a new copy"""
        if not row:
            return row
        return {k: (serializer.loads(v) if (k in self.json_columns and v is not None) else v) for k, v in row.items()}

    def gen_where(self, conditions):
        # conditions = and_(*[self.table.c[key] == val for key, val in conditions.items()])
        where = []
        for key_operator, val in conditions.items():
            if ':' in key_operator:
                key, operator = key_operator.split(':')
            else:
                key = key_operator
                operator = 'eq'

            if operator == 'eq':
                where.append(self.table.c[key] == val)
            elif operator == 'ne':
                where.append(self.table.c[key] != val)
            elif operator == 'gte':
                where.append(self.table.c[key] >= val)
            elif operator == 'lte':
                where.append(self.table.c[key] <= val)
            elif operator == 'gt':
                where.append(self.table.c[key] > val)
            elif operator == 'lt':
                where.append(self.table.c[key] < val)
            elif operator == 'contains':
                where.append(self.table.c[key].like('%{val}%'.format(val=val)))
            elif operator == 'startswith':
                where.append(self.table.c[key].like('{val}%'.format(val=val)))
            elif operator == 'is':
                if val == 'null':
                    where.append(self.table.c[key].is_(None))
                else:
                    raise AlgorithmException(data='unknown is operand: ' + val)
            elif operator == 'isnot':
                if val == 'null':
                    where.append(self.table.c[key].isnot(None))
                else:
                    raise AlgorithmException(data='unknown isnot operand: ' + val)
            else:
                raise AlgorithmException(data='unknown operator: ' + operator)
        if self.global_filter:
            where.append(text(self.global_filter))
        return and_(*where)

    def select(self, fields='*', conditions=None, order_by=None, start=0, num=None, raw=False):
        if fields == '*':
            fields = [self.table]
        elif isinstance(fields, str):
            # f1,f2,f3
            fields = [self.table.c[field.strip()] for field in fields.split(',')]
        elif isinstance(fields, list) and all([isinstance(field, str) for field in fields]):
            # [f1, f2, f3]
            fields = [self.table.c[field.strip()] for field in fields]
        # else keep fields as-is

        query = select(fields).select_from(self.table)

        if conditions:
            where = self.gen_where(conditions)
            query = query.where(where)

        order_by = order_by or self.default_order_by
        if order_by:
            criterion = []
            order_by_list = order_by.split(',')
            for order_by_item in order_by_list:
                order_by_item = order_by_item.strip()
                if ' ' in order_by_item:
                    order_key, order = order_by_item.split(' ')
                    if order.upper() == 'DESC':
                        order_by_item = desc(order_key)
                    else:
                        order_by_item = asc(order_key)
                criterion.append(order_by_item)
            query = query.order_by(*criterion)

        if num:
            query = query.limit(num)
            if start != 0:
                query = query.offset(start)

        result = self.execute(query)
        if not raw:
            result = [self.loads(r) for r in result]
        # result.close()
        return result

    def select_page(self, fields='*', conditions=None, order_by=None, page=1, size=None) -> list:
        size = size or self.default_page_size
        start = (page - 1) * size
        return self.select(fields=fields, conditions=conditions, order_by=order_by, start=start, num=size)

    def select_one(self, fields='*', conditions=None, order_by=None) -> dict:
        rows = self.select(fields=fields, conditions=conditions, order_by=order_by, num=1)
        return rows[0] if rows else None

    def select_one_by_id(self, id, fields='*') -> dict:
        return self.select_one(fields=fields, conditions={self.primary_key: id})

    def select_one_by_id_raw(self, id):
        """returns the raw row. only for test"""
        rows = self.select(conditions={self.primary_key: id}, raw=True)
        return rows[0] if rows else None

    def count(self, conditions=None, distinct_field: str=None):
        """
        :param conditions:
            same as select
        :param distinct_field:
            SELECT COUNT(DISTINCT(distinct_field)) FROM xxx
        :return:
        """
        if not distinct_field:
            fields = [func.count().label('count')]
        else:
            fields = [func.count(distinct(self.table.c[distinct_field])).label('count')]
        rows = self.select(fields=fields, conditions=conditions)
        return rows[0]['count']

    def insert(self, row: dict):
        query = self.table.insert().values(**self.dumps(row))
        result = self.execute(query)
        ret = result.inserted_primary_key[0]
        # result.close()
        # oracle returns a float id
        return int(ret)

    def insert_many(self, rows: list):
        if not rows:
            return 0
        rows = [self.dumps(row) for row in rows]
        query = self.table.insert()
        result = self.execute(query, rows)
        return result.rowcount
        # result.close()
        # oracle returns a float id

    def insert_on_dup_update(self, row):
        """
        mysql-specific func
        """
        assert self.engine.name == 'mysql'

        row = self.dumps(row)
        from sqlalchemy.dialects.mysql import insert
        query = insert(self.table).values(**row).on_duplicate_key_update(**row)
        result = self.execute(query)
        ret = result.inserted_primary_key[0]
        # result.close()
        return ret

    def update(self, row, conditions):
        query = self.table.update().values(**self.dumps(row)).where(self.gen_where(conditions))
        result = self.execute(query)
        # result.close()
        return result.rowcount

    def update_one_by_id(self, id, row):
        return self.update(row, {self.primary_key: id})

    def delete(self, conditions):
        query = self.table.delete().where(self.gen_where(conditions))
        result = self.execute(query)
        # result.close()
        return None

    def delete_one_by_id(self, id):
        return self.delete({self.primary_key: id})
