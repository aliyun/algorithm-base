import logging
import random
from collections import OrderedDict
from datetime import datetime, timedelta

import pytest
from sqlalchemy.sql.functions import concat

from ab.utils import logger, serializer
from ab.utils.dao import Mapper
from sqlalchemy import *

from ab.utils.exceptions import DuplicatedKeyException
from ab.utils.mixes import chunk_string


def check_task_row(row):
    assert row
    if 'data' in row:
        assert not isinstance(row['data'], str)
    if 'status' in row:
        assert not isinstance(row['status'], str)


def insert_new_task():
    from ab.utils.task import Task
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])
    new = {'app_name': 'algorithm_example',
           'algorithm_name': 'test_model',
           'task_id': Task.get_next_id(),
           'status': ['hello', 'world'],
           'data': {'foo': 'bar'}
           }
    new_id = task_mapper.insert(new)
    logger.debug('inserted new id:', new_id)
    return new_id, new


def test_mapper(client):
    from ab.utils.task import Task
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])

    # table may be empty, must insert at first
    # insert & select_one_by_id
    new_id, new = insert_new_task()
    inserted_new = task_mapper.select_one_by_id(new_id)
    check_task_row(inserted_new)
    for k in new:
        assert new[k] == inserted_new[k]
    for k, v in inserted_new.items():
        logger.debug(k + ': ' + str(type(v)))

    # insert dup key
    with pytest.raises(DuplicatedKeyException):
        task_mapper.insert(inserted_new)

    # dump & load
    inserted_new_raw = task_mapper.select_one_by_id_raw(new_id)
    assert inserted_new['data'] == serializer.loads(inserted_new_raw['data'])
    assert inserted_new_raw['status'] == serializer.dumps(inserted_new['status'])

    # update_one_by_id
    result = task_mapper.update_one_by_id(new_id, {'code': 2})
    logger.debug('update result:', result)
    updated_new = task_mapper.select_one_by_id(new_id)
    assert updated_new['code'] == 2

    # delete_one_by_id
    result = task_mapper.delete_one_by_id(new_id)
    logger.debug('delete result:', result)
    deleted_new = task_mapper.select_one_by_id(new_id)
    assert deleted_new is None

    # insert_many & count
    new_many = [
        {'app_name': 'algorithm_example',
         'algorithm_name': 'insert_many',
         'task_id': Task.get_next_id(),
         'status': ['hello', 'world'],
         'data': {'foo': 'bar'}
         } for i in range(3)
    ]
    rowcount = task_mapper.insert_many(new_many)
    assert rowcount == len(new_many)
    # TODO: sqlite only support "%Y-%m-%d %H:%M:%S" as string, which oracle will raise 'ORA-01843: 无效的月份'
    # now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # assert task_mapper.count({'algorithm_name': 'insert_many', 'gmt_create:gte': now}) == rowcount

    # select_page
    rows = task_mapper.select_page(fields='id,app_name,code,status',
                                   conditions={'app_name:contains': 'thm_ex'},
                                   page=1, size=10)
    assert rows
    assert all(['data' not in row for row in rows])
    assert rows[0]['id'] > rows[1]['id']

    # order by
    rows = task_mapper.select_page(fields='id,app_name,status', order_by='app_name desc,id asc, code', page=1, size=2)
    assert 'ORDER BY task.app_name DESC, task.id ASC, task.code' in task_mapper.last_query
    assert rows[0]['app_name'] == rows[1]['app_name']
    assert rows[0]['id'] < rows[1]['id']

    # select one
    one = task_mapper.select_one(order_by='id DESC')
    assert isinstance(one, dict)


def test_count_distinct(client):
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])
    distinct_count = task_mapper.count(distinct_field='app_name')
    assert 0 <= distinct_count <= task_mapper.count()


def test_concat_long(client):
    """only for oracle"""
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])
    if task_mapper.engine.name != 'oracle':
        return
    if not task_mapper.count():
        insert_new_task()
    task = task_mapper.select_one()
    text = '啊' * 10000
    for t in chunk_string(text, 1000):
        task_mapper.update_one_by_id(task['id'], row={'log': concat(task_mapper.table.c.log, t)})


def test_execute_sql(client):
    # from sqlalchemy import *
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])
    # count(distinct id)
    fields = [func.count(distinct(task_mapper.table.c['id'])).label('count')]
    # select
    rows = task_mapper.select(fields=fields)
    logger.info(rows[0]['count'])


def test_gen_where(client):
    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'])

    conditions = OrderedDict()
    conditions['id'] = 1
    conditions['algorithm_name:contains'] = 'abc'
    conditions['id:gte'] = 2
    conditions['id:ne'] = 3
    conditions['id:lte'] = 4
    conditions['code:gt'] = 5
    conditions['code:lt'] = 6
    conditions['app_name:is'] = 'null'
    conditions['args:isnot'] = 'null'

    where = task_mapper.gen_where(conditions)
    assert str(where) == 'task.id = :id_1 AND task.algorithm_name LIKE :algorithm_name_1 ' + \
                         'AND task.id >= :id_2 AND task.id != :id_3 AND task.id <= :id_4 ' + \
                         'AND task.code > :code_1 AND task.code < :code_2 ' + \
                         'AND task.app_name IS NULL AND task.args IS NOT NULL'

    task_mapper = Mapper('task', json_columns=['args', 'status', 'data'], global_filter='id > 0')

    where = task_mapper.gen_where({})
    assert str(where) == 'id > 0'

    conditions = OrderedDict()
    conditions['id'] = 1
    conditions['algorithm_name:contains'] = 'abc'
    conditions['id:gte'] = 2
    conditions['id:ne'] = 3
    conditions['id:lte'] = 4
    conditions['code:gt'] = 5
    conditions['code:lt'] = 6
    conditions['app_name:is'] = 'null'
    conditions['args:isnot'] = 'null'

    where = task_mapper.gen_where(conditions)
    assert str(where) == 'task.id = :id_1 AND task.algorithm_name LIKE :algorithm_name_1 ' + \
           'AND task.id >= :id_2 AND task.id != :id_3 AND task.id <= :id_4 ' + \
           'AND task.code > :code_1 AND task.code < :code_2 ' + \
           'AND task.app_name IS NULL AND task.args IS NOT NULL AND id > 0'
