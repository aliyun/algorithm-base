import os
import time
import uuid
from multiprocessing import Process
from multiprocessing.pool import Pool

from flask import Response
from prometheus_client import Gauge

from ab import app
from ab.plugins.calculate import spark
from ab.plugins.cache.redis import cache_plugin
from ab.plugins.spring import eureka
from ab.plugins.storage import dfs
from ab.utils import logger, fixture
from ab.utils.data_source import DataSource
from ab.utils.algorithm import Algorithm
from ab.utils.exceptions import AlgorithmException
from ab.plugins.data.engine import Engine
from ab.utils.prometheus import func_metrics
from ab.task.recorder import TaskRecorder


class Task:
    """
    stateful algorithm runner
    """

    @staticmethod
    def get_next_id():
        """
        docker uses the IPv4 address of the container to generate MAC address
        which may lead to a collision
        just use the random uuid version 4
        """
        return uuid.uuid4().hex

    @staticmethod
    def get_instance(request):
        # run in sync mode as default
        if request.get('mode', 'sync') == 'sync':
            return SyncTask(request)
        # 'async' for backward compatibility
        elif request['mode'] in ('async', 'async_pool'):
            return PoolAsyncTask(request)
        elif request['mode'] == 'async_unlimited':
            return UnlimitedAsyncTask(request)
        else:
            raise AlgorithmException('unknown mode:', request['mode'])

    def __init__(self, request: dict):
        """
        light weight init.
        the whole self object should be dumpable after init since AsyncTask.run depends on pickle.dumps
        """
        self.data_source = None
        self.engine = None
        self.algorithm = None
        self.spark = None
        self.id = Task.get_next_id()
        self.request = request
        if 'args' in self.request:
            self.kwargs = self.request['args'].copy()
        else:
            self.kwargs = {}
        # self.spark: SparkSession = None
        self.recorder = TaskRecorder.get_instance(task=self)
        self.recorder.init(self.kwargs)

    def lazy_init(self):
        """
        heavy weight init
        """
        self.engine = Engine.get_instance(self.request.get('engine'))
        self.algorithm = Algorithm.get_instance(self.request['algorithm'], self.engine._type)

        # update spark app id as early as possible
        if 'spark' in self.algorithm.params:
            try:
                self.spark = self.kwargs['spark'] = spark.get_or_create()
                self.recorder.update_spark_app_id(self.spark.sparkContext.applicationId)
            except AttributeError:
                if 'spark' not in self.algorithm.defaults_map:
                    raise

        self.data_source = DataSource.get_instance(**self.request)

        if 'task_id' in self.algorithm.params:
            self.kwargs['task_id'] = self.id

        # TODO only set when key not exists in kwargs
        if self.data_source:
            # read data
            if 'data' in self.algorithm.params:
                if getattr(self.data_source,"sql"):
                    # read from custom sql
                    d = self.engine.read_data_by_sql(self.data_source)
                    self.kwargs['sample_rate'], self.kwargs['sample_count'], self.kwargs['data'] = \
                        1, len(d), d
                else:
                    # sample from table
                    self.kwargs['sample_rate'], self.kwargs['sample_count'], self.kwargs['data'] = \
                        self.engine.read_data(self.data_source)
            # underlying db
            if 'db' in self.algorithm.params:
                self.kwargs = self.data_source.db
            # get table meta from db
            if 'table_info' in self.algorithm.params:
                self.kwargs['table_info'] = self.data_source.get_table_info()

        if 'cache_client' in self.algorithm.params:
            self.kwargs['cache_client'] = cache_plugin.get_cache_client()

        if 'dfs_client' in self.algorithm.params:
            self.kwargs['dfs_client'] = dfs.get_instance()

        if 'eureka_client' in self.algorithm.params:
            self.kwargs['eureka_client'] = eureka.get_instance()

        if 'recorder' in self.algorithm.params:
            self.kwargs['recorder'] = self.recorder

        used_fixtures = set(self.algorithm.params) & fixture.fixtures.keys()
        for f in used_fixtures:
            ret = fixture.fixtures[f].run(self.request, self.kwargs)
            if ret is not None:
                if f in self.kwargs and not fixture.fixtures[f].overwrite:
                    raise AlgorithmException(data='fixture try to overwrite param {f}'.format(f=f))
                self.kwargs[f] = ret

        # TODO auto type-conversion according to type hint

    def run_algorithm(self):
        result = self.algorithm.run(self.kwargs)
        if isinstance(result, Response):
            return result
        return {'sample_rate': self.kwargs.get('sample_rate', None),
                'sample_count': self.kwargs.get('sample_count', None),
                'result': result
                }

    def after_run(self):
        if self.data_source:
            self.data_source.close()
        self.engine.stop()


class SyncTask(Task):
    def run(self):
        try:
            '''1. init'''
            self.lazy_init()
            '''2. run'''
            ret = self.run_algorithm()
            # fixme: throw errors when return by jsonify
            self.recorder.done(ret)
            return ret
        finally:
            '''3. gc'''
            self.after_run()


g_inprogress_async_tasks = Gauge("inprogress_async_tasks", "async task", labelnames=['mode'],
                                 multiprocess_mode='livesum')


class AsyncTask(Task):

    def inner_run(self):
        """
        lazy init, then run algorithm in another process
        """
        with g_inprogress_async_tasks.labels(mode=self.mode).track_inprogress():
            try:
                '''1. init'''
                logger.debug('async worker pid:', os.getpid())
                tic = time.time()
                self.lazy_init()
                toc = time.time()
                logger.debug('async lazy init time:', toc - tic)

                '''2. run'''
                result = self.run_algorithm()
                self.recorder.done(result)
            except Exception as e:
                self.recorder.error(e)
            finally:
                '''3. gc'''
                self.after_run()


class PoolAsyncTask(AsyncTask):
    """ process pool """
    pool = None
    mode = 'async_pool'

    @staticmethod
    def get_pool():
        """lazy init pool to avoid fork"""
        if PoolAsyncTask.pool:
            return PoolAsyncTask.pool

        pool_size = app.config.get('ASYNC_POOL_SIZE', 2)
        # two processes for each worker
        try:
            # setproctitle requires gcc, best effort
            from setproctitle import setproctitle
            PoolAsyncTask.pool = Pool(processes=pool_size, initializer=lambda: setproctitle(
                'async pool for {ppid} [{app.config.APP_NAME}]'.format(ppid=os.getppid(), app=app)))
        except ImportError as e:
            PoolAsyncTask.pool = Pool(processes=pool_size)
        logger.debug('init async task pool:', PoolAsyncTask.pool, '\n')
        return PoolAsyncTask.pool

    def run(self):
        # When an object is put on a queue, the object is pickled (by pickle.dumps) and
        # a background thread later flushes the pickled data to an underlying pipe.
        # This has some consequences which are a little surprising, but should not cause any practical difficulties
        pool = self.get_pool()
        pool.apply_async(self.inner_run)

        return self.id


class UnlimitedAsyncTask(AsyncTask):
    """create new process for each task"""
    mode = 'async_unlimited'

    def run(self):
        p = Process(target=self.inner_run)
        p.start()

        return self.id
