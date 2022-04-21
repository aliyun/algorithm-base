from ab.utils import logger
from ab.utils.algorithm import algorithm
from ab import jsonify

from ab.utils.abt_config import config as ac


# test table

@algorithm(db="tests/resources/data.db", type="sqlite", sql="select age from USER where age > 90")
def datasource(table_name=None, data=None):
    return data


# In fact, you can write the fix part of the `DATA_SOURCE` in config.py
@algorithm(type="sql", host=ac.get_value("test_rds_host"), port=3306, username=ac.get_value("test_rds_username"),
           password=ac.get_value("test_rds_password"), db=ac.get_value("test_rds_db_test"),
           sql="select * from world_university_rank limit 10;")
def datasource_rds(table_name=None, data=None):
    return data
