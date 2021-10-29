import os
import glob
import shutil
import tempfile
import threading
import time
from subprocess import Popen, PIPE, STDOUT

from sqlalchemy.sql.functions import concat

from ab.utils import logger
from ab.plugins.db.db_master import get_mapper
from ab.utils.mixes import chunk_string
from ab.utils.prometheus import time_metrics
from ab.utils.reflection import hook_module

pid = None


def _checkpid():
    global pid
    if pid is None:
        pid = os.getpid()
        return

    if pid != os.getpid():
        raise RuntimeError('spark get_or_create same session from different process: {pid1} {pid2}'.format(
            pid1=pid, pid2=os.getpid()))


def get_spark_driver_version():
    import pyspark
    return pyspark.__version__


spark_builder = None


@time_metrics('spark')
def init_spark_builder(config):
    if not config.SPARK:
        logger.info('no config.SPARK found, spark uninitialized')
        return
    try:
        import pyspark
        logger.info('spark driver version:', get_spark_driver_version())
    except ImportError:
        logger.warning('pyspark not found, spark uninitialized')
        return

    root = os.path.join(os.path.dirname(__file__), os.path.pardir)
    if config.get('TESTING'):
        try:
            os.symlink(os.path.join(os.getcwd(), 'spark_jars'), os.path.join(root, 'spark_jars'))
        except Exception as e:
            pass
    spark_jars_dir = os.path.join(root, 'spark_jars', '*.jar')
    spark_jars = glob.glob(spark_jars_dir)
    spark_jars_str = ','.join(spark_jars)
    if 'spark.jars' in config.SPARK:
        config.SPARK['spark.jars'] += ',' + spark_jars_str
    else:
        config.SPARK['spark.jars'] = spark_jars_str

    global spark_builder
    spark_builder = pyspark.sql.SparkSession.builder.appName(config.APP_NAME)
    # namely: self.config("spark.sql.catalogImplementation", "hive")
    spark_builder.enableHiveSupport()
    for k, v in config.SPARK.items():
        spark_builder.config(k, v)


gateway_proc = None
current_app_id = None


class HookedPopen(Popen):
    """
    hook the Popen call to get process stdout & stderr log
    """

    def __init__(self, args, env=None, *more_args, **kwargs):
        logger.info('try to start spark process:', ' '.join(args))
        try:
            super(HookedPopen, self).__init__(args, env=env, *more_args, **kwargs,
                                              stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        except Exception as e:
            logger.error('start fail:', self.stdout.read())
            raise
        else:
            logger.info('start success, pid = {pid}'.format(pid=self.pid))
        # logger.info('env:', env)
        self.save_proc()
        # 当没有存活的非守护线程时，整个Python程序才会退出
        threading.Thread(target=self.save_log, daemon=True).start()

    def save_proc(self):
        global gateway_proc
        if gateway_proc:
            logger.exception('spark gateway process re-opened. old pid: {opid}, new pid: {npid}'.format(
                opid=gateway_proc.pid, npid=self.pid))
        gateway_proc = self

    def save_log(self):
        task_mapper = get_mapper('_task')

        # wait until app created & spark_app_id recorded
        # todo wait & notify
        while not current_app_id:
            time.sleep(0.1)
        while task_mapper.count(conditions={'spark_app_id': current_app_id}) == 0:
            time.sleep(0.1)

        while True:
            line = self.stdout.readline()
            if line.strip():
                # log as soon as possible, for debug
                logger.debug(line.strip())

            if '[Stage' in line:
                continue

            app_id = current_app_id
            if app_id is not None and line:
                for t in chunk_string(line, 1000):
                    task_mapper.update(row={'log': concat(task_mapper.table.c.log, t)},
                                       conditions={'spark_app_id': app_id})

            # proc.poll() returns the retcode of subprocess
            # A None value indicates that the process hasn’t terminated yet
            rc = self.poll()
            if line == '' and rc is not None:
                logger.error('spark gateway exited with return code: {rc}'.format(rc=rc))
                return


# process-isolated derby home
derby_home = None


def get_derby_home():
    global derby_home
    if not derby_home:
        derby_home = tempfile.mkdtemp()
    return derby_home


@time_metrics('spark_lazy')
def get_or_create():
    """
    when spark build got inited, it has a underlying spark session singleton named _instantiatedSession,
    which is set to None as default. Only after getOrCreate() will it be set.
    So if we don't call this algorithm before fork, the return spark session should be process-isolated

    thread-safe and process-safe
    """
    # check pid before potential errors
    _checkpid()

    if not spark_builder:
        raise AttributeError('spark not initialized')

    if get_spark_driver_version() < '2.2.0':
        # workaround for https://issues.apache.org/jira/browse/SPARK-10872
        # step 1: create unique derby home dir for each process
        spark_builder.config('spark.driver.extraJavaOptions',
                             '-Dderby.system.home={derby_home}'.format(derby_home=get_derby_home()))

    import pyspark
    from ab import app
    if app.config.SAVE_SPARK_LOG:
        # TODO: got jammed while creating session on spark 2.4.0
        with hook_module(pyspark.java_gateway, 'Popen', HookedPopen):
            return get_or_create_inner()
    else:
        spark = get_or_create_inner()
        spark.sparkContext.setLogLevel('ERROR')
        return spark


def get_or_create_inner():
    spark = spark_builder.getOrCreate()
    # logger.debug('spark version:', spark.version)
    # logger.debug('get spark session:', spark, 'with app id:', spark.sparkContext.applicationId)
    global current_app_id
    current_app_id = spark.sparkContext.applicationId
    return spark


def stop():
    """stop current app"""
    spark = get_or_create()
    spark.stop()
    if get_spark_driver_version() < '2.2.0':
        spark._jvm.SparkSession.clearDefaultSession()
        # workaround for https://issues.apache.org/jira/browse/SPARK-10872
        # step 2: clear derby_home after each execution
        try:
            shutil.rmtree(get_derby_home())
        except FileNotFoundError:
            pass
    global current_app_id
    current_app_id = None
