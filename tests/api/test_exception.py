import time


def test_divide_zero(client):
    input = {'mode': 'async_pool'}
    resp = client.post_data('/api/algorithm/exception', input)
    assert resp['code'] == 0
    print(resp)


    task_id = resp['data']

    # task_id = algorithm.run_algorithm(input)

    times = 0
    last_ret = None
    while True:
        ret = client.get_data('/api/task/{task_id}'.format(task_id=task_id))
        code = ret['code']
        if ret != last_ret:
            print('get task status: {ret}\n'.format(ret=ret))
            last_ret = ret
        if code == -1:
            break

        times += 1
        if times > 10:
            raise TimeoutError('async task timeout')
        time.sleep(0.5)


def test_msg(client):
    resp = client.post_data('/api/algorithm/msg')
    assert resp['code'] == -100
    assert resp['data'] == 'hello world'
