from ab.plugins.cache import cache_plugin


def b2s(b):
    return b.decode('utf-8')


def test_delete_cache(client):
    # bugfix: use result:random.43786 to avoid cache key dup
    random_count = 43786
    table_key = 'rds://rm-bp16x64jxbdz9tw4aro.mysql.rds.aliyuncs.com:3306/expert_modeling.result.pickle'
    cache_key = 'rds://rm-bp16x64jxbdz9tw4aro.mysql.rds.aliyuncs.com:3306/expert_modeling.result:' \
                'random.{count}.pickle'.format(count=random_count)

    resp = client.post_data('/api/data_source/10000506/table/result/algorithm/args',
                            data={'sampler': {'type': 'random', 'count': random_count}})
    assert resp['code'] == 0
    cache_client = cache_plugin.get_cache_client()
    keys = cache_client._keys()
    assert table_key in keys and cache_key in keys
    cache_keys = cache_client.smembers(table_key)
    assert cache_key in map(b2s, cache_keys)

    resp = client.delete_data('/api/data_source/10000506/table/result/cache')
    assert resp['code'] == 0
    keys = cache_client._keys()
    assert table_key not in keys
    cache_keys = cache_client.smembers(table_key)
    assert cache_key not in map(b2s, cache_keys)
