"""
pytest测试用例。其要求测试用例必须都放在tests文件夹下，需要启动的函数及所在的文件都必须以'test'开头
"""


def test_cache(client):
    req = {
        'args': {
            'val': 'the val',
        }
    }
    resp = client.post_data(
        '/api/algorithm/save',
        data=req,
    )
    '''
    resp例子
    {
        # 0代表请求成功，负数代表失败
        'code': 0,
        'data': {
            # sample开头的字段是采样用的，本demo没用到，忽略即可
            'sample_count': None,
            'sample_rate': None,
            # 返回值自动塞到result里
            'result': 'result:a434fc677e844fa5802041c499ab8f00'
        }
    }
    '''
    assert resp['code'] == 0
    key = resp['data']['result']

    resp2 = client.post_data(
        '/api/algorithm/load',
        data={
            'args': {
                'key': key
            }
        },
    )
    assert resp2 == {
        # 0代表请求成功，负数代表失败
        'code': 0,
        'data': {
            # sample开头的字段是采样用的，本demo没用到，忽略即可
            'sample_count': None,
            'sample_rate': None,
            # 返回值自动塞到result里
            'result': 'the val'
        }
    }
