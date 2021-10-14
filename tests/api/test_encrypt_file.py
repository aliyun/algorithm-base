import pickle

# from ab.utils.os_util import resource_file_path
from ab.keys.crypto import open_text, open_binary, read_text, read_pickle, ab_encryptFile

input_pickle = "resources/pickle_example"
input_text_common = "resources/text_common"
input_text_common_json = "resources/text_common_json"
input_text_contains_chinese = "resources/text_contains_chinese"
input_text_path_contains_chinese = "resources/子目录/text_path_contains_chinese"
input_text_common_without_crypto = "resources/text_common_without_crypto"


def resource_file_path(file_path):
    return "tests/" + file_path


def setup_module():
    """
    to test decrypt, we need prepare some encrypt files first.
    :return:
    """

    def return_pwd():
        return "this is the secret"

    source_files = [input_text_common, input_text_common_json, input_text_contains_chinese,
                    input_text_path_contains_chinese]
    for f in source_files:
        source_path = resource_file_path(f)
        ab_encryptFile(source_path, source_path + ".sec")

    obj = {}
    obj["hello"] = "world"
    obj["你"] = "好"
    input_pickle_path = "tests/resources/pickle_example"
    with open(input_pickle_path, 'wb') as f:
        pickle.dump(obj, f)
    ab_encryptFile(input_pickle_path, input_pickle_path + ".sec")


# ==============================================================================
# 二进制类型文件
# ==============================================================================

def test_decrypt_bin():
    source_path = resource_file_path(input_pickle)
    with open_binary(source_path) as buffer:
        obj = pickle.loads(buffer)
        assert "world" == obj["hello"]
        assert "好" == obj["你"]


def test_decrypt_pickle():
    source_path = resource_file_path(input_pickle)
    obj = read_pickle(source_path)
    assert "world" == obj["hello"]
    assert "好" == obj["你"]


# 这个用例必须在 test_decrypt_pickle 之后
def test_decrypt_pickle_after_remove_source():
    import os
    os.remove("tests/resources/pickle_example")

    obj = read_pickle("tests/resources/pickle_example")
    assert "world" == obj["hello"]
    assert "好" == obj["你"]


# # ==============================================================================
# # 文本类文件
# # ==============================================================================
#
def test_decrypt_text_common():
    source_path = resource_file_path(input_text_common)
    with open_text(source_path) as text:
        for t in text:
            assert t == "hello world\n"
            break


def test_decrypt_text_with_sec():
    import subprocess
    subprocess.run("cp {} {}".format("tests/" + input_text_common + ".sec", "tests/" + input_text_common + "2.sec"),
                   shell=True,
                   stdout=subprocess.PIPE, encoding="utf-8").stdout

    source_path = "tests/" + input_text_common + "2"
    with open_text(source_path) as text:
        for t in text:
            assert t == "hello world\n"
            break


def test_decrypt_text_common_json():
    source_path = resource_file_path(input_text_common_json)
    json_string = read_text(source_path)

    import json
    json_object = json.loads(json_string)
    assert json_object["key1"] == "你好啊"
    assert json_object["key2"] == "value2"


def test_decrypt_text_common_json_with_sec():
    source_path = resource_file_path(input_text_common_json)

    import subprocess
    subprocess.run("cp {} {}".format(source_path + ".sec", source_path + "2.sec"),
                   shell=True,
                   stdout=subprocess.PIPE, encoding="utf-8").stdout

    json_string = read_text(source_path + "2")

    import json
    json_object = json.loads(json_string)
    assert json_object["key1"] == "你好啊"
    assert json_object["key2"] == "value2"


def test_decrypt_text_contains_chinese():
    source_path = resource_file_path(input_text_contains_chinese)
    with open_text(source_path) as text:
        for t in text:
            assert t == "你好，\n"
            break


def test_decrpyt_text_path_contains_chinese():
    source_path = resource_file_path(input_text_path_contains_chinese)
    with open_text(source_path) as text:
        for t in text:
            assert t == "你好，\n"
            break


def test_decrpyt_text_common_without_crypto():
    source_path = resource_file_path(input_text_common_without_crypto)
    with open_text(source_path) as text:
        for t in text:
            assert t == "hello world raw text,\n"
            break



