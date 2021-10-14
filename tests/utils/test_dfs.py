import random
import string

import pytest

from ab.utils import dfs


def run_once(dfs_client):
    # test text files
    text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
    with dfs_client.open('test.txt', 'w', encoding='utf-8', overwrite=True) as writer:
        writer.write(text)
    with dfs_client.open('test.txt', 'r', encoding='utf-8') as reader:
        assert text == reader.read()

    dfs_client.download('test.txt', '/tmp/test.txt.bak', overwrite=True)
    with open('/tmp/test.txt.bak', 'r', encoding='utf-8') as reader:
        assert text == reader.read()

    dfs_client.upload('/tmp/test.txt.bak', 'test.txt.bak', overwrite=True)
    with dfs_client.open('test.txt.bak', 'r', encoding='utf-8') as reader:
        assert text == reader.read()

    # test binary files
    binary = bytearray(random.getrandbits(8) for _ in range(64))
    with dfs_client.open('test.bin', 'w', overwrite=True) as writer:
        writer.write(binary)
    with dfs_client.open('test.bin', 'r') as reader:
        assert binary == reader.read()

    # FIXME occasionally fail
    dfs_client.download('test.bin', '/tmp/test.bin.bak', overwrite=True)
    with open('/tmp/test.bin.bak', 'rb') as reader:
        assert binary == reader.read()

    dfs_client.upload('/tmp/test.bin.bak', 'test.bin.bak', overwrite=True)
    with dfs_client.open('test.bin.bak', 'rb') as reader:
        assert binary == reader.read()

    # test dir op
    dfs_client.makedirs('test_dir')
    assert 'test_dir' in dfs_client.list('')
    assert dfs_client.exists('test_dir')
    assert [] == dfs_client.list('test_dir')
    dfs_client.delete('test_dir')
    assert not dfs_client.exists('test_dir')
    assert 'test_dir' not in dfs_client.list('')

    # test file op
    dfs_client.status('test.bin')
    assert dfs_client.exists('test.bin')
    dfs_client.delete('test.bin')
    assert not dfs_client.exists('test.bin')
    try:
        dfs_client.status('test.bin')
    except:
        pass
    else:
        raise Exception('should raise exception')


def is_accessable(ip, port, timeout):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def run(dfs_client):
    # remove root dir
    dfs_client.delete('')
    # recreate root dir
    dfs_client.makedirs('')
    # run with empty root dir
    run_once(dfs_client)
    # run again with existing root dir and files
    run_once(dfs_client)


@pytest.mark.dfs
def test_hdfs():
    if not is_accessable('116.62.179.22', 50070, 3):
        return

    hdfs_config = {
        # 'type': 'hdfs',
        'sub_type': 'insecure',
        'url': 'http://116.62.179.22:50070',
        'user': 'root',
        # must use a different dir. otherwise it may break test_dfs_example.py test case
        'root': '/user/root/algorithm_example2'
    }
    dfs_client = dfs.HDFSClient(**hdfs_config)
    run(dfs_client)


def test_local_fs():
    local_fs_config = {
        # 'type': 'local',
        'root': '/tmp/test_fs'
    }
    dfs_client = dfs.LocalFSClient(**local_fs_config)
    run(dfs_client)

    # test local fs up/down same file/dir
    text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
    with dfs_client.open('test.txt', 'w', encoding='utf-8', overwrite=True) as writer:
        writer.write(text)
    dfs_client.download('test.txt', '/tmp/test_fs/test.txt', overwrite=True)
    dfs_client.upload('/tmp/test_fs/test.txt', 'test.txt', overwrite=True)
    dfs_client.download('/tmp', '/tmp', overwrite=True)
    dfs_client.upload('/tmp', '/tmp', overwrite=True)
