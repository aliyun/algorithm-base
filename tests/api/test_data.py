

hive_ldap = {
    "type": "hive",
    "host": "sw2",
    "port": 10000,
    "username": "hive",
    "password": "hive0308",
    "db": "bank_visual"
}


def test_hive_ldap(client):
    input = {
        'data_source': hive_ldap,
        'cacheable': False,
        'args': {
            'table_name': 'device'
        }
    }
    resp = client.post_data('/api/algorithm/args?qs_arg=123', input)
    assert resp['code'] == 0
    assert resp['data']['result']['data']
