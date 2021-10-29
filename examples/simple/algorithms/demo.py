from ab.utils import logger
from ab.utils.algorithm import algorithm
from ab import app

# 可以使用这种方式载入配置里的数据，然后执行载入模型之类的操作
model_path = app.config.MODEL_PATH
logger.info('model path is:', model_path)


# 会自动暴露为/api/algorithm/add接口
@algorithm()
def add(a: int, b: int) -> int:
    """
    一个简单的加法算法示例
    :param a: 第一个参数
    :param b: 第二个参数
    :return:
    """
    logger.info("enter algorithm {}, {} ".format(a, b))
    return a + b


@algorithm()
def crypto():
    """
    读取加密文件
    :return:
    """
    from ab.keys.data import read_text, read_pickle, open_binary

    # with open_binary("hanhao.pkl") as buffer:
    #    print(1)
    # return "aa"
    return read_text("resource/mydata")
    # return str(read_pickle("resource/hanhao"))[:20]


@algorithm()
def compress() -> int:
    """
    :return:
    """
    return "this is a hello world text file, glad to meet you, bye ~this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye this is a hello world text file, glad to meet you, bye "

