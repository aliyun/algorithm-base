import functools
import os
import re

from sqlalchemy import create_engine, event, exc
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateTable

from ab.utils.exceptions import AlgorithmException


def create_table_multiprocess(engine, table):
    """
    copy from https://github.com/sqlalchemy/sqlalchemy/issues/4936#issuecomment-545557883
    fix multiprocess test case error: "table task already exists" in multiprocess env
    """
    class CreateTableIfNotExists(CreateTable):
        pass

    @compiles(CreateTableIfNotExists)
    def compile_create_table_if_not_exists(element, ddlcompiler, **kw):
        default_create_ddl = ddlcompiler.visit_create_table(element, **kw)
        default_create_ddl = default_create_ddl.lstrip()
        create_if_not_exists = re.sub(
            r"^CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", default_create_ddl, flags=re.IGNORECASE
        )
        return create_if_not_exists

    engine.execute(CreateTableIfNotExists(table))


def create_task_table_and_mapper(engine):
    from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Text, text
    from sqlalchemy.sql import func
    meta = MetaData()

    server_now = func.now()
    text_class = Text
    if engine.name == 'sqlite':
        server_now = text("(DATETIME(CURRENT_TIMESTAMP,'LOCALTIME'))")
    elif engine.name == 'mysql':
        from sqlalchemy.dialects.mysql import LONGTEXT
        text_class = LONGTEXT

    task_table = Table(
        'task', meta,
        # Background on SQLite’s autoincrement is at: http://sqlite.org/autoinc.html
        # if want non-dup pk, use "sqlite_autoincrement=True"
        Column('id', Integer, primary_key=True),
        Column('task_id', String(255), unique=True),
        Column('app_name', String(255)),
        Column('algorithm_name', String(255)),
        Column('code', Integer),
        Column('args', text_class),
        Column('status', text_class),
        Column('data', text_class),
        Column('spark_app_id', String(255)),
        Column('log', text_class),
        Column('gmt_create', DateTime(timezone=True), server_default=server_now),
        Column('gmt_modified', DateTime(timezone=True)),
    )
    # checkfirst=True by default, will skip create the table if already exists
    meta.create_all(engine)

    # TODO: isolate create_mapper
    from ab.plugins.db.dao import Mapper
    from ab.plugins.db import db_master

    mapper = Mapper('task',  json_columns=['args', 'status', 'data'], primary_key='task_id')
    db_master.mappers['_task'] = mapper


def init_db(config):
    if config.DB and not isinstance(config.DB, str):
        raise TypeError('config.DB must be valid sqlalchemy connection str since v2.4.0. '
                        'Please refer to: https://docs.sqlalchemy.org/en/13/core/engines.html')
    engine = get_engine(config.DB, config.get('PRINT_SQL', False))
    create_task_table_and_mapper(engine)
    # MAGIC: fix all db connection related bugs
    engine.dispose()


def get_default_engine():
    from ab import app
    return get_engine(app.config.DB, app.config.get('PRINT_SQL', False))


def hash_dict(func):
    """Transform mutable dictionnary
    Into immutable
    Useful to be compatible with cache
    """
    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HDict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


@hash_dict
@functools.lru_cache(maxsize=128)
def get_engine(db_config: str, echo=False, **kwargs):
    """
    create engine and adapt for multi-process
    # TODO refactor to class, one for each engine
    """
    if not isinstance(db_config, str):
        raise AlgorithmException('config.DB only supports string format since v2.4.0')

    if db_config.startswith('oracle'):
        assert os.getenv('ORACLE_HOME') and (os.getenv('DYLD_LIBRARY_PATH') or os.getenv('LD_LIBRARY_PATH')),\
            'please set ORACLE_HOME and (DY)LD_LIBRARY_PATH to use oracle database'
        # FIXME: use the default QueuePool may cause some strange bugs in async mode
        new_engine = create_engine(db_config, echo=echo, echo_pool=echo,
                                   optimize_limits=True, poolclass=NullPool, **kwargs)
    elif db_config.startswith('sqlite'):
        # TODO: sqlite can't use NullPoll in multi-process mode. perhaps a bug of sqlalchemy read/write lock
        new_engine = create_engine(db_config, echo=echo, echo_pool=echo, **kwargs)
    else:
        # default mysql
        new_engine = create_engine(db_config, echo=echo, echo_pool=echo, pool_use_lifo=True,
                                   pool_recycle=3600, pool_pre_ping=True, pool_size=50, **kwargs)

    @event.listens_for(new_engine, "connect")
    def connect(dbapi_connection, connection_record):
        connection_record.info['pid'] = os.getpid()

    @event.listens_for(new_engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        pid = os.getpid()
        if connection_record.info['pid'] != pid:
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
            )

    return new_engine
