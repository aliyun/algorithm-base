SPARK = {
    'spark.master': 'local[*]',
    'spark.executor.memory': '4g',
    'spark.executor.cores': 4,
    #'spark.cores.max': '12',
    'spark.dynamicAllocation.initialExecutors': 10,
    'spark.driver.memory': '2g',
    'spark.driver.maxResultSize': '2g',
    'spark.port.maxRetries': 1000,
    'spark.executorEnv.PYTHON_EGG_CACHE': "/tmp/.cache/",
    'spark.executorEnv.PYTHON_EGG_DIR': "/tmp/.cache/",
    'spark.driverEnv.PYTHON_EGG_CACHE': "/tmp/.cache/",
    'spark.driverEnv.PYTHON_EGG_DIR': "/tmp/.cache/",
    # 'spark.dynamicAllocation.initialExecutors': 6,

    # Logs the effective SparkConf as INFO when a SparkContext is started
    'spark.logConf': "true",
    'odps.numPartitions': 10,
}

ENVAR = {
    # a bug in spark 2.1.x, must clear hadoop config, otherwise spark will try to connect to hive
    'HADOOP_CONF_DIR': '',
    # 'SPARK_HOME': '/usr/local/Caskroom/miniconda/base/envs/cpy35/lib/python3.5/site-packages/pyspark',
}
