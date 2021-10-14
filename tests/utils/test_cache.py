from ab.plugins.cache.redis import cache_plugin

from tests import config

cache_plugin.start(config)


def b2s(b):
    return b.decode('utf-8')


def test_redis_cache():
    tk = 'the_table_key'
    ck1, ck2, ck3 = 'the_cache_key_one', 'the_cache_key_two', 'the_cache_key_three'

    client = cache_plugin.get_cache_client()
    client.delete(tk, ck1, ck2, ck3)

    client.get_set_cache(ck1, lambda: 'the value', expire=60, table_key=tk)
    client.get_set_cache(ck2, lambda: 'the value', expire=60, table_key=tk)

    keys = set(client._keys())
    # super set of
    assert keys >= {tk, ck1, ck2}

    ttls = [client.ttl(tk), client.ttl(ck1), client.ttl(ck2)]
    assert all([ttl == 60 for ttl in ttls])

    cache_keys = client.smembers(tk)
    assert set(map(b2s, cache_keys)) == {ck1, ck2}

    client.sadd(tk, ck3)
    cache_keys = client.smembers(tk)
    assert set(map(b2s, cache_keys)) == {ck1, ck2, ck3}

    client.delete_table_cache(tk)
    assert not any([client.exists(ck1), client.exists(ck2), client.smembers(tk)])


def test_redis_bin_cache():
    cases = {'string': '123', 'dict': {'a': 123}, 'none': None}
    client = cache_plugin.get_cache_client()
    for k, v in cases.items():
        client.bset(k, v, ex=86400)
        assert client.bget(k) == v

    assert client.bget('a_key_that_never_exists') is None

    client.delete(*cases.keys())
