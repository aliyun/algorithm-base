import copy
import time
from multiprocessing import Process
import pytest

from ab.utils import logger
from ab.plugins.db.db_master import get_mapper

from ab.utils.abt_config import config as ac

def request_async(client, input):
    resp = client.post_data('/api/algorithm', input)
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
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_test")
        },
        "algorithm": "spark_example",
        "mode": "async_pool",    # 异步进程池执行
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "world_university_rank",
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
