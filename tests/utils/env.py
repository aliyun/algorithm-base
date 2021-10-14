import os


def test_env(client):
    oracle_home = os.getenv('ORACLE_HOME')
    assert oracle_home == '/usr/local/oracle/instant_client'
    dyld_library_path = os.getenv('DYLD_LIBRARY_PATH')
    assert dyld_library_path == '/usr/local/oracle/instant_client'

