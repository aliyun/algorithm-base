import pytest

from ab.utils import logger, db_master
from ab.utils.db.rds import RDS
from tests.utils.test_dao import insert_new_task


def test_min_dbm_config(client):
    from ab.utils.task import Task

    # table may be empty, must insert at first
    # add & get
    new = {'app_name': 'algorithm_example',
           'algorithm_name': 'test_model',
           'task_id': Task.get_next_id(),
           'status': ['hello', 'world'],
           'data': {'foo': 'bar'}
           }
    resp = client.post_data('/api/table/task/', new)
    assert resp['code'] == 0, resp
    new_id = resp['data']
    assert new_id
    resp = client.get_data('/api/table/task/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data']['id'] == new_id

    # update & get
    new['code'] = 2
    resp = client.put_data('/api/table/task/{id}'.format(id=new_id), new)
    assert resp['code'] == 0
    resp = client.get_data('/api/table/task/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data']['code'] == 2

    # list
    resp = client.get_data('/api/table/task?page=1&size=7&app_name:contains=algorithm_example')
    assert resp['code'] == 0
    assert resp['count']
    if resp['count'] == 1:
        insert_new_task()
        resp = client.get_data('/api/table/task?page=1&size=7&app_name:contains=algorithm_example')
    assert resp['data']
    assert resp['data'][0]['id'] > resp['data'][1]['id'], resp['data']

    # order_by
    resp = client.get_data('/api/table/task?order_by=id')
    assert resp['code'] == 0
    assert resp['count']
    assert resp['data']
    assert resp['data'][0]['id'] < resp['data'][1]['id']

    # delete & get
    resp = client.delete_data('/api/table/task/{id}'.format(id=new_id))
    assert resp['code'] == 0
    resp = client.get_data('/api/table/task/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data'] is None


def test_max_page_size(client):
    with pytest.raises(AssertionError):
        resp = client.get_data('/api/table/one_by_one?page=1&size=2')


def test_full_dbm_config(client):
    from ab.utils.task import Task

    # table may be empty, must insert at first
    # add & get
    new = {'name': Task.get_next_id(), 'is_deleted': 0}
    resp = client.post_data('/api/table/model/', new)
    assert resp['code'] == 0, resp
    new_id = resp['data']
    assert new_id
    resp = client.get_data('/api/table/model/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data']['id'] == new_id

    # update & get
    new['remark'] = 'fangliu_test'
    resp = client.put_data('/api/table/model/{id}'.format(id=new_id), new)
    assert resp['code'] == 0
    resp = client.get_data('/api/table/model/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data']['remark'] == 'fangliu_test'

    # list
    resp = client.get_data('/api/table/model?page=1&size=7')
    assert resp['code'] == 0
    assert resp['count']
    assert resp['data']
    assert resp['data'][0]['id'] > resp['data'][1]['id']
    # assert len(resp['data']) == 7

    # order_by
    resp = client.get_data('/api/table/model?order_by=id')
    assert resp['code'] == 0
    assert resp['count']
    assert resp['data']
    assert resp['data'][0]['id'] < resp['data'][1]['id']

    # default order_by
    resp = client.get_data('/api/table/model')
    model_mapper = db_master.get_mapper('model')
    assert 'ORDER BY model.id DESC, model.create_user_id ASC' in model_mapper.last_query

    # delete & get
    resp = client.delete_data('/api/table/model/{id}'.format(id=new_id))
    assert resp['code'] == 0
    resp = client.get_data('/api/table/model/{id}'.format(id=new_id))
    assert resp['code'] == 0
    assert resp['data'] is None
