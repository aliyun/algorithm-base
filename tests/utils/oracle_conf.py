import os

from ab.utils.db import db_conn_pool


def test(client):
    assert db_conn_pool.get_default_engine().name == 'oracle'
