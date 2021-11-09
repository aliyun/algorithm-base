from ab import app
from ab.utils import logger


def test_custom_response(client):
    input = {
        "mode": "sync",
        "algorithm": "custom_response",
    }
    resp = client.post_data('/api/algorithm', input)
    print("xxxx")


def test_task_list(client):
    resp = client.get_data('/api/task?page=1&size=10000')
    assert resp['code'] == 0, resp
    tasks = resp['data']
    assert tasks, resp
    # assert any([isinstance(task['status'], (list, dict)) for task in tasks])
    assert all(['data' not in task for task in tasks])
    assert all([task['app_name'] == app.config.APP_NAME for task in tasks])

    # no need to test here. already fully tested in async example
    # task = client.get_data('/api/task/{task_id}'.format(task_id=tasks[0]['task_id']))
    # assert task
    # assert 'data' in task


def test_sync_task(client):
    input = {
        "mode": "sync",
        "algorithm": "sync",
    }
    resp = client.post_data('/api/algorithm', input)
    assert resp['code'] == 0, resp
    assert resp['data']['result'] == "hello-sync-task"


def do_async(client, mode, algorithm, result):
    import time

    input = {
        "mode": mode,
        "algorithm": algorithm,
    }
    resp = client.post_data('/api/algorithm', input)

    assert resp['code'] == 0, resp
    assert resp['data'] is not None

    times = 0
    task_id = resp['data']

    # status code
    # ERROR = -1
    # INIT = 0
    # RUNNING = 1
    # DONE = 2

    while True:
        ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
        code = ret['code']
        logger.info('{task_id}, code={code}'.format(task_id=task_id, code=code))
        if code < 0:
            logger.error(ret['data'])
            break
        if code == 0:
            assert ret['task_id'] == task_id
        # fixme: the status `1` is not occur
        # if code == 1:
        #     assert ret['data']['result'] == "hello-async-unlimit-task"
        if code == 2:
            assert ret['data']['result'] == result
            break

        times += 1
        if times > 100:
            logger.error('task {task_id} timeout'.format(task_id=task_id))
            return
        time.sleep(0.1)


def test_async_unlimit_task(client):
    do_async(client, "async_unlimited", "async_unlimit", "hello-async-unlimit-task")


def test_async_pool_task(client):
    do_async(client, "async", "async_pool", "hello-async-pool-task")
