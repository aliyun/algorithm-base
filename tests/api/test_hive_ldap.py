from ab.utils.abt_config import config as ac

hive = {
    "type": "hive",
    "host": ac.get_value("test_docker_hive_host"),
    "port": ac.get_value("test_docker_hive_port"),
    "username": ac.get_value("test_docker_hive_username"),
    "password": ac.get_value("test_docker_hive_password"),
    "db": ac.get_value("test_docker_hive_db_testdb")
}

def test_hive_ldap(client):
    input = {
        'data_source': hive,
        'cacheable': False,
        'args': {
            'table_name': 'student'
        }
    }
    resp = client.post_data('/api/algorithm/args?qs_arg=123', input)
    assert resp['code'] == 0
    assert resp['data']['result']
