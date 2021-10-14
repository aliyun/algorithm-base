from ab.utils import logger
from ab.utils.algorithm import algorithm
from ab import app


# 可以使用这种方式载入配置里的数据，然后执行载入模型之类的操作
model_path = app.config.MODEL_PATH
logger.info('model path is', model_path)


# 被@algorithm装饰的函数会自动暴露为/api/{func.__name__}接口
@algorithm()
def demo(the_uploaded_file, more_args, default_true=True):
    # 接口请求里的args字段会被自动展开为实参，支持文件上传
    # 没有传递的参数可以使用默认值
    assert default_true is True
    return {
        'more_args': more_args,
        'file_content': the_uploaded_file.read().decode('utf-8'),
        'filename': the_uploaded_file.filename
    }
