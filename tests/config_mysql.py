'''test create mysql task table'''
import time
from ab.plugins.db.rds import RDS
from ab.utils.abt_config import config as ac

r = RDS(host=ac.get_value("test_rds_host"), port=3306, db=None, username=ac.get_value("test_rds_host"),
        password=ac.get_value("test_rds_password"))
r.execute('drop database if exists ab_task')
r.execute('create database ab_task')
r.close()

DB = ac.get_value("test_rds_ab_task_connection")
# PRINT_SQL = True
