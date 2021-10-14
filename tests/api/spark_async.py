import copy
import time
from multiprocessing import Process

import pytest

from ab.utils import logger
from ab.utils.db_master import get_mapper


def request_async(client, input):
    resp = client.post_data('/api/data_source/10000506/table/e_annual_performance/algorithm', input)
    assert resp['code'] == 0
    task_id = resp['data']

    # task_id = algorithm.run_algorithm(input)

    times = 0
    mapper = get_mapper('_task')
    while True:
        ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
        code = ret['code']
        if code < 0:
            logger.error(ret['data'])
            break
        if code == 2:
            assert ret['data']['result'] == task_id
            task = mapper.select_one_by_id(task_id)
            assert task_id in task['log']
            break
        logger.info('{task_id} type {mode} code {code}'.format(
            task_id=task_id, mode=input['args']['mode'], code=code))

        times += 1
        if times > 90:
            logger.error('task {task_id} timeout'.format(task_id=task_id))
            return
        time.sleep(2)


@pytest.mark.spark
def test_spark_async(client):
    input = {
        "algorithm": "spark_example",
        "mode": "async_pool",    # 异步进程池执行
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_async",
            "mode": "async_pool",    # 异步进程池执行
            "name": "fangliu"
        }
    }
    workers = []
    for i in range(4):
        # prometheus don't support hybrid of multi-thread and multiprocess, use multiprocess only
        workers.append(Process(target=request_async, args=(client, input)))
    input = copy.deepcopy(input)
    input['mode'] = 'async_unlimited'
    input['args']['mode'] = 'async_unlimited'
    for i in range(4):
        workers.append(Process(target=request_async, args=(client, input)))

    for w in workers:
        w.start()

    for w in workers:
        w.join()
        logger.info('worker {w} joined'.format(w=str(w)))
