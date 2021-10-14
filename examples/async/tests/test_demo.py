"""
pytest测试用例。其要求测试用例必须都放在tests文件夹下，需要启动的函数及所在的文件都必须以'test'开头
"""
import time
from pprint import pprint


def test_async(client):
    # 1. 新建异步任务
    run_seconds = 4
    req = {
        # 指定模式为异步执行
        "mode": "async_unlimited",
        'args': {
            'run_seconds': run_seconds
        }
    }
    resp = client.post_data(
        '/api/algorithm/async_work',
        data=req,
    )
    assert resp['code'] == 0
    # 获得异步任务的id。这是个uuid，全局唯一
    task_id = resp['data']

    # 2. 任务初始化了，code为0
    ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
    '''
    此时刚新建任务，ret大概是这样：
    {   'algorithm_name': 'async_work',
        'app_name': '',
        'args': {'run_seconds': 4},
        'code': 0,
        'data': None,
        'gmt_create': '2020-03-27 11:44:50.000',
        'gmt_modified': None,
        'id': 52,
        'log': '',
        'spark_app_id': None,
        'status': None,
        'task_id': '051c8d9b53684c37b263c8ef0da6df5b'
    }
    '''
    assert ret['code'] == 0

    time.sleep(run_seconds / 2)

    # 3. 任务开始执行了，code为1。注意如果没有调用 update_status 则code仍为0
    ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
    '''
    任务执行中，此时ret大概是这样：
    {   'algorithm_name': 'async_work',
        'app_name': '',
        'args': {'run_seconds': 4},
        'code': 1,
        'data': None,
        'gmt_create': '2020-03-27 11:39:11.000',
        'gmt_modified': None,
        'id': 49,
        'log': '',
        'spark_app_id': None,
        'status': {'progress': 0},
        'task_id': '4b83af635fe9409a887052574387b424'
    }
    '''
    assert ret['code'] == 1

    time.sleep(run_seconds / 2 + 1)

    # 4. 任务执行结束，code为2
    ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
    '''
    任务执行完成，此时ret大概是这样：
    {
        'algorithm_name': 'async_work',
        'app_name': '',
        'args': {'run_seconds': 4},
        'code': 2,
        'data': {'result': 'successfully sleep for 4 seconds',
                 'sample_count': None,
                 'sample_rate': None},
        'gmt_create': '2020-03-27 11:39:11.000',
        'gmt_modified': None,
        'id': 49,
        'log': '',
        'spark_app_id': None,
        'status': {'progress': 99},
        'task_id': '4b83af635fe9409a887052574387b424'
    }
    '''
    assert ret['code'] == 2
    assert ret['data']['result'] == 'successfully sleep for {run_seconds} seconds'.format(run_seconds=run_seconds)
