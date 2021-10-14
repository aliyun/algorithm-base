import sys
import time

from ab.utils import logger


def request(client, input):
    resp = client.post_data('/api/data_source/10000506/table/e_annual_performance/algorithm', input)
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
        if times > 10:
            raise TimeoutError('async task timeout')
        time.sleep(0.5)


def test_pool(client):
    input = {
        "algorithm": "async_example",
        "mode": "async_pool",    # 异步进程池执行
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "name": "fangliu"
        }
    }
    request(client, input)


def test_unlimited(client):
    input = {
        "algorithm": "async_example",
        "mode": "async_unlimited",    # 异步进程池执行
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "name": "fangliu"
        }
    }
    request(client, input)
