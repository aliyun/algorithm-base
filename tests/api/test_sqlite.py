import pytest

from ab.utils.abt_config import config as ac


# test custom sql


def test_sqlite_request_sql(client):
    req = {
        "data_source": {
            "type": "sqlite",
            "db": "tests/resources/data.db"
        },
        "algorithm": "async_example",
        "mode": "sync",
        "args": {
            "sql": "select age from USER where age > 90"
        }
    }

    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result)


def test_sqlite_decorator_sql(client):
    req = {
        "algorithm": "datasource",
        "mode": "sync",
    }

    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result)


# test sampler


req = {
    "data_source": {
        "type": "sqlite",
        "db": "tests/resources/data.db"
    },
    "algorithm": "async_example",
    "mode": "sync",
    # "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
    "args": {
        "table_name": "USER",
        "print_data": False
    }
}


def test_sqlite_head(client):
    req["sampler"] = {
        "type": "head",
        "count": 1
    }

    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_sqlite_tail(client):
    req["sampler"] = {
        "type": "tail",
        "count": 1
    }
    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_sqlite_random(client):
    req["sampler"] = {
        "type": "random",
        "count": 1
    }

    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])


def test_sqlite_none(client):
    req['sampler'] = None
    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result['sample_rate'], result['sample_count'])
