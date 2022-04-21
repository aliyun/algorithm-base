import sys
import time

from ab.utils import logger
from ab.utils.abt_config import config as ac


def request(client, input):
    resp = client.post_data('/api/algorithm', input)
    assert resp['code'] == 0
    task_id = resp['data']

    # task_id = algorithm.run_algorithm(input)

    times = 0
    last_ret = None
    while True:
        ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
        code = ret['code']
        if code < 0:
            logger.error(ret['data'])
            break
        if ret != last_ret:
            logger.debug('task updated: {ret}\n'.format(ret=ret))
            last_ret = ret
        if code > 0:
            assert ret['status']
        if code == 2:
            assert ret['data']['result'] == ['hello', 'world']
            assert ret['status'] == 'stage2'
            break

        times += 1
        if times > 100:
            raise TimeoutError('async task timeout')
        time.sleep(0.5)




def test_pool(client):
    input = {
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_test")
        },

        "algorithm": "async_example",
        "mode": "async_pool",  # 异步进程池执行
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "world_university_rank",
            "name": "fangliu"
        }
    }
    request(client, input)


def test_unlimited(client):
    input = {
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_test")
        },

        "algorithm": "async_example",
        "mode": "async_unlimited",  # 异步进程池执行
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "world_university_rank",
            "name": "fangliu"
        }
    }
    request(client, input)
