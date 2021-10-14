import pytest
from ab import app
from ab.plugins.db.db_master import get_mapper
from ab.utils.abt_config import config as ac

@pytest.mark.spark
def test_spark_sync(client):
    request = {
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_sync",
            "name": "fangliu"
        }
    }
    for i in range(2):
        resp = client.post_data('/api/data_source/10000506/table/e_annual_performance/algorithm/spark_example', request)
        assert resp['code'] == 0
        mapper = get_mapper('_task')
        task_id = resp['data']['result']
        task = mapper.select_one_by_id(task_id)
        if app.config.SAVE_SPARK_LOG:
            assert task_id in task['log']


@pytest.mark.spark
def test_spark_udf(client):
    request = {
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_udf",
            "name": "fangliu"
        }
    }
    resp = client.post_data('/api/data_source/10000506/table/e_annual_performance/algorithm/spark_udf_example', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_rds_data_types(client):
    request = {
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_test")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "test_data_type",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    # spark handles all null columns differently, test it
    request['args']['table_name'] = 'test_data_type_all_null'
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_rds_zero_count(client):
    request = {
        "data_source": {
            "host": ac.get_value("test_rds_host"),
            "port": int(ac.get_value("test_rds_port")),
            "username": ac.get_value("test_rds_username"),
            "password": ac.get_value("test_rds_password"),
            "db": ac.get_value("test_rds_db_test")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "zero_count",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_odps(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_test"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps",
            "table_name": "e_annual_performance",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_odps_partition_table_no_partition(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps_no_partition",
            "table_name": "test_partition",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0




@pytest.mark.spark
def test_spark_read_odps_partition_table_with_partition(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps_partition",
            "table_name": "test_partition",
            "partitions": ["p1=1,p2=1"],
        }
    }
    # mock non-local mode
    sm = app.config.SPARK['spark.master']
    app.config.SPARK['spark.master'] = ''
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0
    app.config.SPARK['spark.master'] = sm


@pytest.mark.spark
def test_spark_read_odps_partition_table_with_multiple_partitions(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False, # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps_multi_partition",
            "table_name": "test_partition",
            "partitions": ["p1=1,p2=1", "p1=2,p2=2"],
        }
    }
    # mock non-local mode
    sm = app.config.SPARK['spark.master']
    app.config.SPARK['spark.master'] = ''
    with pytest.raises(AssertionError):
        resp = client.post_data('/api/algorithm', request)
    app.config.SPARK['spark.master'] = sm


@pytest.mark.spark
def test_spark_read_odps_data_types(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps_data_types",
            "table_name": "test_data_type3",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    # spark handles all null columns differently, test it
    request['args']['table_name'] = 'test_data_type_all_null'
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_odps_zero_count(client):
    request = {
        "data_source": {
            "type": "ODPS",
            "project": ac.get_value("test_odps_project_disuite_match"),
            "access_id": ac.get_value("test_odps_ak"),
            "access_key": ac.get_value("test_odps_sk"),
            "endpoint": ac.get_value("test_odps_endpoint"),
            "tunnel_endpoint": ac.get_value("test_odps_tunnel_endpoint")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "test": "test_spark_read_odps_data_types",
            "table_name": "zero_count",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_hive_no_partition(client):
    request = {
        "data_source": {
            "type": "hive",
            "host": ac.get_value("test_hive_host"),
            "port": ac.get_value("test_hive_port"),
            "username": ac.get_value("test_hive_username"),
            "db": ac.get_value("test_hive_db_zyq")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "test_hive",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    request['args']['table_name'] = 'test_partition'
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_hive_partition(client):
    request = {
        "data_source": {
            "type": "hive",
            "host": ac.get_value("test_hive_host"),
            "port": ac.get_value("test_hive_port"),
            "username": ac.get_value("test_hive_username"),
            "db": ac.get_value("test_hive_db_zyq")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "test_hive",
        }
    }

    request['args']['table_name'] = 'test_partition'
    request['args']['partitions'] = ['pt=1', 'pt=2']
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    request['args']['table_name'] = 'test_l2_partition'
    request['args']['partitions'] = ['pt1=1/pt2=1', 'pt1=2']
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_hive_data_types(client):
    request = {
        "data_source": {
            "type": "hive",
            "host": ac.get_value("test_hive_host"),
            "port": ac.get_value("test_hive_port"),
            "username": ac.get_value("test_hive_username"),
            "db": ac.get_value("test_hive_db_zyq")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "test_data_type",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0

    # spark handles all null columns differently, test it
    request['args']['table_name'] = 'test_data_type_all_null'
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0


@pytest.mark.spark
def test_spark_read_hive_zero_count(client):
    request = {
        "data_source": {
            "type": "hive",
            "host": ac.get_value("test_hive_host"),
            "port": ac.get_value("test_hive_port"),
            "username": ac.get_value("test_hive_username"),
            "db": ac.get_value("test_hive_db_zyq")
        },
        "algorithm": "spark_example",
        "engine": {
            "type": "spark"
        },
        "cacheable": False,  # 即使配置了redis缓存也不从缓存中读取，debug用
        "args": {
            "table_name": "zero_count",
        }
    }
    resp = client.post_data('/api/algorithm', request)
    assert resp['code'] == 0
