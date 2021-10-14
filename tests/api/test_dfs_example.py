import pytest


@pytest.mark.dfs
def test(client):
    input = {
        "algorithm": "dfs_example",
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
    }
    resp = client.post_data('/api/algorithm', input)
    assert resp['code'] == 0
    print(resp['data'])
