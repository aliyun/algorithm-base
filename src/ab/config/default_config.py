import multiprocessing

worker_class = "sync"

preload_app = False

# The maximum number of requests a worker will process before restarting.
max_requests = 0
# avoid all workers restarting at the same time
max_requests_jitter = 200

# 这个获取的是HT虚拟核的数量
cpu_count = multiprocessing.cpu_count()

timeout = 60  # seconds

workers = 2

# 防止压力堆积
backlog = cpu_count * 32

# 日志
capture_output = True

APP_NAME = ''

HOST = 'localhost'

PORT = 8000

DEBUG = False

INSTANCE_HOST = ""
INSTANCE_IP = ""
REGISTER_AT_EUREKA = False

CACHE_TIMEOUT = 1800  # seconds

# TODO: -> SAMPLER_TIMEOUT
HIVE_TIMEOUT = 120  # seconds

SAMPLER = {'type': 'head', 'count': 100000}

STATIC_FOLDER = 'static'
STATIC_URL_PATH = '/static'

# local db file for sqlite, all projects can share the same file
DB = 'sqlite:////tmp/ab.db'

# eureka default register info
INSTANCE_HOST = ""
INSTANCE_IP = ""


NACOS_DEFAULT_HEART_BEAT_INTERVAL_SECONDS = 10


# 是否开启存活检查
ENABLE_LIVENESS_PROB = False
LIVENESS_PROB = {
    # 容器启动后要等待多少秒后存活和就绪探测器才被初始化，最小值是 0。
    "initialDelaySeconds": 600,
    # 执行探测的时间间隔（单位是秒）。最小值是 1。
    "periodSeconds": 60,
    # 探测的超时后等待多少秒。最小值是 1。
    "timeoutSeconds": 1,
    # 当连续失败N次后，重启容器
    "failureThreshold": 5,
}

# the default hooks are process in gunicorn to avoid import problems
# from ab.apps import gunicorn
# child_exit = gunicorn.child_exit
# post_fork = gunicorn.post_fork
