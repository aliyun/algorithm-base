from ab import app
from ab.utils import logger


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
