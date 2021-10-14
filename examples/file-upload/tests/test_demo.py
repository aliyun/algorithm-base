"""
pytest测试用例。其要求测试用例必须都放在tests文件夹下，需要启动的函数及所在的文件都必须以'test'开头
"""

import io


def test_demo(client):
    # 模拟一个上传的文件
    req = {
        'the_uploaded_file': (io.BytesIO(b'hello world'), 'filename.mp3'),
        'more_args': 'xxxx'
    }
    resp = client.post_form(
        '/api/algorithm/demo',
        data=req,
        content_type='multipart/form-data'
    )
    assert resp == {
        # 0代表请求成功，负数代表失败
        'code': 0,
        'data': {
            # sample开头的字段是采样用的，本demo没用到，忽略即可
            'sample_count': None,
            'sample_rate': None,
            # 返回值自动塞到result里
            'result': {
                'more_args': 'xxxx',
                'file_content': 'hello world',
                'filename': 'filename.mp3'
            }
        }
    }
