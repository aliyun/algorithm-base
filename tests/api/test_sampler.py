import pytest

from ab.utils.abt_config import config as ac

rds_request = {
    "data_source": {
        "host": ac.get_value("test_rds_host"),
        "port": int(ac.get_value("test_rds_port")),
        "username": ac.get_value("test_rds_username"),
        "password": ac.get_value("test_rds_password"),
        "db": ac.get_value("test_rds_db_test")
    },
    "algorithm": "async_example",
    "mode": "sync",
    # "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
    "args": {
        "table_name": "world_university_rank",
        "name": "fangliu",
        "print_data": False
    }
}


def test_rds_random(client):
    rds_request["sampler"] = {
        "type": "random",
        "count": 100000
    }
    resp = client.post_data('/api/algorithm', rds_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_rds_none(client):
    rds_request['sampler'] = None
    resp = client.post_data('/api/algorithm', rds_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


odps_request = {
    "data_source": {
        "type": "ODPS",
        "project": ac.get_value("test_odps_project_test"),
        "access_id": ac.get_value("test_odps_ak"),
        "access_key": ac.get_value("test_odps_sk"),
        "endpoint": ac.get_value("test_odps_endpoint")
    },
    "algorithm": "async_example",
    # "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
    "sampler": {  # sampler不想暴露给main函数，就放在外层了
        "column_name": "je",
        "count": 100000
    },
    "args": {
        "table_name": "world_university_rank",
        # "partitions": ['p1=1/p2=1', 'p1=2/p2=2', 'p1=2,p2=3'],
        "name": "fangliu",
        # "print_data": True
    }
}


def test_odps_cvr(client):
    odps_request['sampler']['type'] = 'column_variety_random'
    resp = client.post_data('/api/algorithm', odps_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_odps_head(client):
    odps_request['sampler']['type'] = 'head'
    resp = client.post_data('/api/algorithm', odps_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_odps_tail(client):
    odps_request['sampler']['type'] = 'tail'
    resp = client.post_data('/api/algorithm', odps_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_odps_random(client):
    odps_request['sampler']['type'] = 'random'
    resp = client.post_data('/api/algorithm', odps_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_odps_none(client):
    odps_request['sampler'] = None
    resp = client.post_data('/api/algorithm', odps_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])
