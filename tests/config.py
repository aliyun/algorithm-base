from ab.utils.abt_config import config as ac


TESTING = True

DEBUG = True

APP_NAME = 'algorithm_example'

HOST = 'localhost'
PORT = 6092

PRINT_RESULT = False
LOG_LEVEL = 'DEBUG'

# 环境变量
ENVAR = {
    'ORACLE_HOME': '/usr/local/oracle/instant_client',
    'NLS_LANG': 'SIMPLIFIED CHINESE_CHINA.UTF8',
    # 特例：下面这俩变量是python解释器启动的时候载入的，在这里配置无效
    # # mac
    # 'DYLD_LIBRARY_PATH': '/usr/local/oracle/instant_client',
    # # linux
    # 'LD_LIBRARY_PATH': '/usr/local/oracle/instant_client',
}

SAMPLER = {
    'type': 'head',
    'count': 1000
}

# daily用这个
EUREKA_SERVER = ac.get_value("test_eureka_server")

REGISTER_AT_EUREKA = False

# 如果不配置redis就无法使用缓存
REDIS = {
    'host': ac.get_value("test_redis_host"),
    'port': ac.get_value("test_redis_port"),
    'password': ac.get_value("test_redis_password")
}
# CACHE_TIMEOUT = 120

DB = ac.get_value("test_rds_connection")


# 打印实际执行的sql，debug用
PRINT_SQL = False

DBM = [
    {
        # 最小配置只需要一个table_name字段
        'table_name': 'task',
        'json_columns': 'status,data'
    },
    {
        # 最全配置。所有的表名、列名必须要小写。
        # 暴露哪张表。必填。
        'table_name': 'model',
        # 哪些字段需要在列表中显示。有些字段比如data或者二进制列比较大，不想在列表中返回。默认为'*'
        'list_columns': 'id,name,remark,gmt_create,gmt_modified',
        # 哪些字段需要在根据id查询详情的时候返回。有些字段如二进制数据是无法显示在json中的，可以用此字段控制。默认为'*'
        'detail_columns': 'id,remark,pk_name',
        # 哪些字段是json格式，增删改查需要自动dump/load。默认为''
        'json_columns': 'table_args',
        ######### 以上是常用字段，下面的没特殊需求可以不看 ##########
        # 指定其他db。默认使用config.DB
        'db': ac.get_value("test_rds_model_connection"),
        # 如果填写了db选项则控制是否打印sql。默认为false
        # 非自定义的db会忽略此参数而使用PRINT_SQL参数(控制DB是否打印sql)
        # 'print_sql': True,
        # 允许哪些操作, C-新建 R-读取列表和详情 U-更新 D-删除。大写，顺序无关。默认为"CRUD"
        'operations': 'CRUD',
        # 有可能出现不同db的同名表的情况，使用key区分url里的路径, 即/api/table/{key}。默认使用table_name作为key
        'key': 'model',
        # 强制所有select请求追加此查询条件到where条件末尾。默认为空
        'global_filter': 'is_deleted = 0',
        # 分页的时候的默认order_by。默认为'id DESC'
        'default_order_by': 'id DESC, create_user_id ASC',
        # 哪个列作为主键。增删改查的时候都使用这个列作为id。默认为'id'
        'primary_key': 'id',
        # 默认一页显示多少条。默认为10条
        'default_page_size': 10,
        # 一页最多显示多少条。默认50条
        'max_page_size': 50,
    },
    {
        # 测试max_page_size用
        'table_name': 'task',
        'key': 'one_by_one',
        'max_page_size': 1,
    }
]



ASYNC_POOL_SIZE = 2

DFS = {}


ALGORITHM_DIR = 'tests/api/algorithms'

FIXTURE_DIR = 'tests/api/fixtures'

STATIC_FOLDER = 'tests/static'
STATIC_URL_PATH = '/tests/static'

accesslog='logs/access.log'
errorlog='logs/error.log'
# Redirect stdout/stderr to specified file in errorlog
capture_output = True
