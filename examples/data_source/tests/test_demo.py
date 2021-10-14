"""
pytest测试用例。其要求测试用例必须都放在tests文件夹下，需要启动的函数及所在的文件都必须以'test'开头
"""

rds = {
    "host": "YOUR_HOST",
    "port": 3306,
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "db": "YOUR_DB"
}


odps = {
    "access_id": "your id",
    "access_key": "your key",
    "project": "shuiniu",
    "endpoint": "http://service.cn-hangzhou.maxcompute.aliyun.com/api",
    "log_view_host": None,
    "type":"odps"    # 默认是mysql
}


def test_show(client):
    req = {
        # 指定数据源
        'data_source': rds,
        # 指定采样方式
        'sampler': {'type': 'head', 'count': 10},  # mysql 支持random和head， odps支持random，head，tail等
        # 指定不读取缓存
        'cacheable': False,
        # 指定读取哪张表
        'args': {
            'table_name': 'task'
        }
    }
    resp = client.post_data(
        '/api/algorithm/head',
        data=req,
    )
    assert resp['code'] == 0
    """
    resp示例：
    {'code': 0,
     'data': {
        'result': [
                    table line 1,
                    table line 2,
                    ...
                 ],
        'sample_count': 685,
        'sample_rate': 100.0
        }
    }
    """
