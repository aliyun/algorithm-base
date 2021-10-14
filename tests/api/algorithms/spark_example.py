import os

from ab.utils import logger
from ab.utils.algorithm import algorithm


@algorithm(name='spark_example', engine='spark')
def _(data, spark, task_id, recorder):
    """
    如果定义了algorithm装饰器里的name字段，函数自己的名称就不起作用了
    """
    recorder.update_status('begin')
    sc = spark.sparkContext
    log4jLogger = sc._jvm.org.apache.log4j
    LOGGER = log4jLogger.LogManager.getLogger(__name__)
    LOGGER.warn("task for this app is " + task_id)
    LOGGER.warn('测试spark中文')

    print('current pid: {pid}'.format(pid=os.getpid()))
    print('测试python中文')
    data.show(20)

    logger.debug('debug')
    logger.info('info')

    recorder.update_status('finish')
    return task_id


# known-issue: yarn ImportError
# TODO auto zip and addPyFiles
def squared(s):
    return s * s


@algorithm(engine='spark')
def spark_udf_example(data, spark):
    if spark.version >= '2.2.0':
        squared_udf = spark.udf.register("squaredWithPython", squared)
        data.select("f1", squared_udf("f1").alias("id_squared")).show()
    else:
        from pyspark.sql import functions
        squared_udf = functions.udf(squared)
        data.select("f1", squared_udf('f1')).show()


@algorithm(engine='python')
def spark_example(data):
    """
    这是python版的算法
    因为algorithm装饰器的name没有定义，因此算法名就会使用函数名"spark_example"。
    """
    return 'runs on the default engine'
