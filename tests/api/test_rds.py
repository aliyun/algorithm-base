import pytest

from ab.utils.abt_config import config as ac

# test table

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


def test_rds_table(client):
    resp = client.post_data('/api/algorithm', rds_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result)


# test custom sql


def test_rds_request_sql(client):
    rds_request["args"] = {}
    rds_request["args"]["table_name"] = "world_university_rank"
    rds_request["args"]["sql"] = "select * from world_university_rank limit 5"

    resp = client.post_data('/api/algorithm', rds_request)
    assert resp['code'] == 0
    result = resp['data']
    print(result)


def test_rds_decorator_sql(client):
    req = {
        "algorithm": "datasource_rds",
        "mode": "sync",
    }

    resp = client.post_data('/api/algorithm', req)
    assert resp['code'] == 0
    result = resp['data']
    print(result)
