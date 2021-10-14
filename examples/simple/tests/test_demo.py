"""
pytest测试用例。其要求测试用例必须都放在tests文件夹下，需要启动的函数及所在的文件都必须以'test'开头
"""


def test_add(client):
    req = {
        'args': {
            'a': 1,
            'b': 2,
        }
    }
    resp = client.post_data(
        '/api/algorithm/add',
        data=req,
    )
    assert resp == {
        # 0代表请求成功，负数代表失败。负数的时候data会显示异常栈，方便debug
        'code': 0,
        'data': {
            # sample开头的字段是采样用的，本demo没用到，忽略即可
            'sample_count': None,
            'sample_rate': None,
            # 返回值自动塞到result里
            'result': 3
        }
    }


def test_add2(client):
    req = {
        'args': {
            'a': 1,
            'b': 2,
        }
    }
    resp = client.post_data(
        '/api/algorithm/add',
        data=req,
    )
    assert resp == {
        # 0代表请求成功，负数代表失败。负数的时候data会显示异常栈，方便debug
        'code': 0,
        'data': {
            # sample开头的字段是采样用的，本demo没用到，忽略即可
            'sample_count': None,
            'sample_rate': None,
            # 返回值自动塞到result里
            'result': 3
        }
    }
