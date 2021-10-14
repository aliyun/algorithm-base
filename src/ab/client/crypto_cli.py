import subprocess

from ab.utils import logger
from ab.keys.crypto import ab_encryptFile

# 加密文件扩展名
SEC_FILE_POSTFIX = ".sec"


def list_dir(file_pattern):
    """
    列出需要加密的文件
    :file_pattern: 匹配文件的正则表达式
    :return:
    """
    import os
    import re

    def include_name(oname):
        if file_pattern is not None:
            match = re.search(file_pattern, oname)
            if match:
                return True
        return False

    dir = os.getcwd()
    target_files = []
    for root, dirs, files in os.walk(dir, topdown=True):
        for name in files:
            if include_name(os.path.join(root, name)):
                if name[-4:] != SEC_FILE_POSTFIX:
                    target_files.append(os.path.join(root, name))

    l = len(dir)
    target_files = [x[l + 1:] for x in target_files]
    return dir, target_files


def gen_crypto_files(root_dir, files, clear=False):
    """
    加密root_dir文件夹下的files模块组
    :return:
    """
    for f in files:
        infile = root_dir + "/" + f
        logger.info("crypto file {}".format(infile))
        # python to c
        ab_encryptFile(infile, infile + SEC_FILE_POSTFIX)

        if clear:
            command = "rm -rf {}".format(f)
            subprocess.run(command, shell=True)


def crypto_impl(args):
    dir, target_files = list_dir(args.include)

    gen_crypto_files(dir, target_files, args.clear)
