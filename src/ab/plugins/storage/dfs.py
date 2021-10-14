"""
Distributed File Storage
"""
import os
import shutil

from ab.utils import logger
from ab.utils.prometheus import time_metrics, func_metrics

dfs_client = None


def init_dfs_client(config: dict):
    """
    return a dfs config according to config
    :param config:
        {
            "type": "hdfs",
            "sub_type": "insecure",
            ...
        }
    :return:
    """
    global dfs_client

    if config.DFS:
        dfs_config = config.DFS.copy()
    else:
        dfs_config = {
            'type': 'local',
            'root': os.path.join('/tmp', config.APP_NAME)
        }

    _type = dfs_config.pop('type')
    if _type == 'local':
        dfs_client = LocalFSClient(**dfs_config)
    elif _type == 'hdfs':
        dfs_client = HDFSClient(**dfs_config)


def get_instance():
    return dfs_client


class LocalFSClient:
    def __init__(self, root, **config):
        self.root = root
        self.makedirs('')

    def abs_path(self, remote_path):
        """
        return remote_path as is if remote_path is abs path
        else return root + remote_path
        """
        if os.path.isabs(remote_path):
            logger.warning('use absolute path as dfs remote path is not recommended, '
                           'which may lead to privilege bugs:', remote_path)
        return os.path.join(self.root, remote_path)

    def upload(self, local_path, remote_path, overwrite=False):
        """
        local_path -> remote_path
        TODO overwrite
        """
        abs_remote_path = self.abs_path(remote_path)
        if self.samefile(local_path, remote_path):
            return abs_remote_path
        # real copy in case src got deleted
        return shutil.copyfile(local_path, abs_remote_path)

    def download(self, remote_path, local_path, overwrite=False):
        """
        remote_path -> local_path
        """
        if self.samefile(local_path, remote_path):
            return local_path

        abs_remote_path = self.abs_path(remote_path)
        if overwrite:
            self.delete(local_path)
        # real copy in case src got deleted
        return shutil.copyfile(abs_remote_path, local_path)

    def open(self, path, mode, encoding=None, overwrite=True, *args, **kwargs):
        """
        TODO overwrite
        """
        # text mode
        if encoding:
            kwargs['encoding'] = encoding
        # binary mode
        elif 'b' not in mode:
            logger.warning('neither encoding nor "b" bit found, treat [{path}] as binary file'.format(path=path))
            mode += 'b'
        abs_path = self.abs_path(path)
        return open(abs_path, mode, *args, **kwargs)

    def samefile(self, local_path, remote_path):
        """
        Return True if both pathname arguments refer to the same file or directory
        """
        # Macintosh, Unix.
        abs_remote_path = self.abs_path(remote_path)
        try:
            return os.path.samefile(abs_remote_path, local_path)
        except OSError:
            return False

    def _isfile(self, abs_path):
        return os.path.isfile(abs_path)

    def _isdir(self, abs_path):
        return os.path.isdir(abs_path)

    def delete(self, path):
        """
        TODO return code
        """
        abs_path = self.abs_path(path)
        if self._isfile(abs_path):
            os.remove(abs_path)
            # os.remove always return None on success
            return True
        elif self._isdir(abs_path):
            shutil.rmtree(abs_path)
            # shutil.rmtree always return None on success
            return True

    def makedirs(self, path, permissions=0o777):
        abs_path = self.abs_path(path)
        return os.makedirs(abs_path, mode=permissions, exist_ok=True)

    mkdirs = makedirs

    def list(self, path, status=False):
        abs_path = self.abs_path(path)
        return os.listdir(abs_path)

    def status(self, path):
        """
        raise exception if not found
        :param path:
        :return: os.stat_result(st_mode=33188, st_ino=12902734940,
                st_dev=16777221, st_nlink=1, st_uid=502, st_gid=0,
                st_size=22, st_atime=1566805542, st_mtime=1566805542,
                st_ctime=1566805542)
        """
        abs_path = self.abs_path(path)
        return os.stat(abs_path)

    def exists(self, path):
        abs_path = self.abs_path(path)
        return os.path.exists(abs_path)


class HDFSClient:
    """
    https://hdfscli.readthedocs.io/en/latest/api.html
    """

    def __init__(self, sub_type='insecure', **config):
        import hdfs

        if sub_type == 'insecure':
            self.client = hdfs.client.InsecureClient(**config)
        elif sub_type == 'secure':
            self.client = hdfs.ext.kerberos.KerberosClient(**config)

        self.mkdirs('')

    @func_metrics('hdfs')
    def download(self, remote_path, local_path, overwrite=False):
        if os.path.isabs(remote_path):
            logger.warning('use absolute path as dfs remote path is not recommended, '
                           'which may lead to privilege bugs:', remote_path)
        return self.client.download(remote_path, local_path, overwrite=overwrite)

    @func_metrics('hdfs')
    def upload(self, local_path, remote_path, overwrite=False):
        if os.path.isabs(remote_path):
            logger.warning('use absolute path as dfs remote path is not recommended, '
                           'which may lead to privilege bugs:', remote_path)
        return self.client.upload(remote_path, local_path, overwrite=overwrite)

    @func_metrics('hdfs')
    def open(self, path, mode, *args, **kwargs):
        if 'r' in mode:
            return self.client.read(path, *args, **kwargs)
        elif 'w' in mode:
            return self.client.write(path, *args, **kwargs)

    @func_metrics('hdfs')
    def delete(self, path):
        """
        :param path:
        :return:    True if the deletion was successful
                    False if no file or directory previously existed at path
        """
        return self.client.delete(path, recursive=True, skip_trash=True)

    @func_metrics('hdfs')
    def makedirs(self, path, permissions=None):
        return self.client.makedirs(path, permissions)

    mkdirs = makedirs

    @func_metrics('hdfs')
    def list(self, path, status=False):
        return self.client.list(path, status)

    @func_metrics('hdfs')
    def status(self, path):
        """
        raise exception if not found
        :param path:
        :return: {
                'accessTime': 1563447269976,
                'blockSize': 134217728,
                'childrenNum': 0,
                'fileId': 17185,
                'group': 'supergroup',
                'length': 10485760,
                'modificationTime': 1563447272757,
                'owner': 'root',
                'pathSuffix': '',
                'permission': '755',
                'replication': 2,
                'storagePolicy': 0,
                'type': 'FILE'
            }
        """
        return self.client.status(path, strict=True)

    @func_metrics('hdfs')
    def exists(self, path):
        return self.client.status(path, strict=False) is not None
