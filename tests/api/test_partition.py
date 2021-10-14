from ab.utils.abt_config import config as ac

request = {
    "data_source": {
        "type": "ODPS",
        "project": ac.get_value("test_odps_project_test"),
        "access_id": ac.get_value("test_odps_ak"),
        "access_key": ac.get_value("test_odps_sk"),
        "endpoint": ac.get_value("test_odps_endpoint")
    },
    "sampler": {
        "type": "random",
        "count": 1
    },
    "algorithm": "async_example",
    "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
    "args": {
        "table_name": "customer_min",
        "name": "fangliu"
    }
}


def test_odps_default_partition(client):
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


def test_odps_manual_partition(client):
    request2 = request.copy()
    request2['args']['table_name'] = 'test_partition'
    request2['args']['partitions'] = ['p1=1/p2=1', 'p1=2/p2=2', 'p1=2,p2=3']
    resp = client.post_data('/api/algorithm', request2)
    assert resp['code'] == 0
