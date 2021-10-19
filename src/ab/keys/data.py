import os
import io
import contextlib

from ab.utils.exceptions import AlgorithmException
from ab.keys.crypto import decrypt_to_memory

# 加密文件扩展名
SEC_FILE_POSTFIX = ".sec"


def read_text(infile, encode="UTF-8"):
    """
    纯文本解密工具
    :param infile:
    :param passw_fun():
    :param encode:
    :return:
    """
    frags = []
    with open_text(infile, encode) as text:
        for t in text:
            frags.append(t)
    return "".join(frags)


def read_json(infile, encode="UTF-8"):
    """
    json解密工具
    :param infile:
    :param passw_fun():
    :param encode:
    :return:
    """
    text = read_text(infile, encode)
    import json
    return json.loads(text)


def read_pickle(infile):
    """
    pickle解密工具
    :param infile:
    :param passw_fun():
    :param encode:
    :return:
    """
    import pickle
    with open_binary(infile) as buffer:
        obj = pickle.loads(buffer)
        return obj


@contextlib.contextmanager
def open_text(infile, encode="utf-8"):
    """
    返回解压后的文本流
    :param infile:
    :param passw_fun():
    :param encode:
    :return:
    """

    if os.path.exists(infile):
        f = open(infile, "r", encoding=encode)
        yield f
        f.close()
    else:
        sec_file_path = infile + SEC_FILE_POSTFIX
        if os.path.exists(sec_file_path):
            byte_io = decrypt_to_memory(sec_file_path)
            text_obj = byte_io.getvalue().decode(encode)
            string_io = io.StringIO(text_obj)
            yield string_io
            byte_io.close()
            string_io.close()
        else:
            raise AlgorithmException(data="file doesn't exist {}".format(sec_file_path))


@contextlib.contextmanager
def open_binary(infile):
    """
    返回解压后的二进制流
    :param infile:
    :param passw_fun():
    :param encode:
    :return:
    """
    if os.path.exists(infile):
        f = open(infile, "rb")
        max_bytes = 2 ** 31 - 1
        bytes_in = bytearray(0)
        input_size = os.path.getsize(infile)
        if input_size > max_bytes:
            raise AlgorithmException(data="the file is too large! {}".format(infile))
        with open(infile, 'rb') as f_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += f_in.read(max_bytes)
        yield bytes_in
        f.close()
    else:
        sec_file_path = infile + SEC_FILE_POSTFIX
        if os.path.exists(sec_file_path):
            byte_io = decrypt_to_memory(sec_file_path)
            yield byte_io.getvalue()
            byte_io.close()
        else:
            raise AlgorithmException(data="file doesn't exist {}".format(sec_file_path))
