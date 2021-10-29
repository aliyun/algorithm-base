import sys

from ab.plugins.cache.redis import cache_plugin
from ab.utils.abt_config import config as ac


def test_decimal(client):
    '''
    用含有decimal的表测试对decimal字段的处理
    '''
    if not cache_plugin.redis_pool:
        print('未配置redis，跳过测试')
        sys.exit(0)

    c = cache_plugin.get_cache_client()
    c.delete(ac.get_value('test_odps_bin_file1'),
             ac.get_value("test_rds_bin_file1"))

    request = {
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_expert_modeling")
        },
        "algorithm": "async_example",
        "args": {
            "table_name": "expert_model"
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint")
        },
        "algorithm": "async_example",
        "args": {
            "table_name": "demo_heartdisease_1k",
            "column_name": "chest_pain_type"
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0
