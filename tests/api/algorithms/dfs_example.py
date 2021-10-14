import time

from ab.utils import logger
from ab.utils.algorithm import algorithm


def gen_random_bin(size_in_MB):
    with open('/dev/urandom', 'rb') as reader:
        return reader.read(size_in_MB * 1024 * 1024)


@algorithm()
def dfs_example(dfs_client):

    init = time.time()
    bin_10mb = gen_random_bin(10)

    # test read & write
    begin = time.time()
    with dfs_client.open('10mb.bin', 'w', overwrite=True) as writer:
        writer.write(bin_10mb)
    write = time.time()
    with dfs_client.open('10mb.bin', 'r') as reader:
        assert reader.read() == bin_10mb
    read = time.time()

    # test upload and download
    # bin => local temp file => remote file => local down file
    tempfile_path = '/tmp/10mb.bin'
    download_path = '/tmp/10mb_2.bin'
    with open(tempfile_path, 'wb') as fp:
        fp.write(bin_10mb)
    dfs_client.upload(tempfile_path, '10mb_upload.bin', overwrite=True)
    dfs_client.download('10mb_upload.bin', download_path, overwrite=True)
    with open(download_path, 'rb') as reader:
        assert reader.read() == bin_10mb

    # test mkdir
    dfs_client.mkdirs('test_new_dir/dir2')
    dfs_client.makedirs('test_new_dir/dir2/dir3')

    # test list
    files = dfs_client.list('')

    # test status & exists
    status = dfs_client.status('10mb.bin')
    exists = dfs_client.exists('10mb.bin')
    assert exists
    not_exists = dfs_client.exists('404.bin')
    assert not not_exists

    # test delete
    assert dfs_client.delete('10mb.bin')
    assert dfs_client.delete('10mb_upload.bin')
    assert dfs_client.delete('test_new_dir')
    assert not dfs_client.delete('404.bin')

    return {
        'init time': begin - init,
        'write time': write - begin,
        'read time': read - write,
        'files': files,
        'status': status
    }
