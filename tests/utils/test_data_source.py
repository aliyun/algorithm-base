from ab.utils import logger
from ab.utils.data_source import DataSource
from ab.utils.abt_config import config as ac


rds = {
    "host": ac.get_value("test_rds_host"),
    "port": int(ac.get_value("test_rds_port")),
    "username": ac.get_value("test_rds_username"),
    "password": ac.get_value("test_rds_password"),
    "db": ac.get_value("test_rds_db_test")
}


def test_rds_data_source(client):
    """client for init logger"""
    rds_columns = {
        's': 'String',
        'b': 'Boolean',
        'i': 'Long',
        'e': 'Long',
        'd': 'Double',
        'f': 'Double',
        'dt': 'Date',
        'dcm': 'Double'
    }

    ds = DataSource.get_instance(rds, {'table_name': 'test_data_type'})
    ti = ds.get_table_info(True)
    logger.info(ti)
    for column in ti['columns']:
        assert column['xlabType'] == rds_columns[column['field']]
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(rds, {'table_name': 'test_data_type'}, sampler={'type': 'random', 'count': 1})
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(rds, {'table_name': 'test_data_type'}, sampler={'type': 'head', 'count': 1})
    _, _, sample = ds.sample()
    assert len(sample)

    # some engines (spark) handles all null columns differently. put it here just in case
    ds = DataSource.get_instance(rds, {'table_name': 'test_data_type_all_null'})
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(rds, {'table_name': 'zero_count'})
    _, _, sample = ds.sample()
    assert len(sample) == 0


odps = {
    "type": "ODPS",
    "project": ac.get_value("test_odps_project_test"),
    "access_id": ac.get_value("test_odps_ak"),
    "access_key": ac.get_value("test_odps_sk"),
    "endpoint": ac.get_value("test_odps_endpoint")
}


def test_odps_data_source(client):
    """client for init logger"""
    odps_columns = {
        'ti': 'Long',
        'si': 'Long',
        'i': 'Long',
        'b': 'Long',
        'f': 'Double',
        'd': 'Double',
        'dcm': 'Double',
        'vc': 'String',
        's': 'String',
        'dt': 'Date',
        'ts': 'Date',
        'bl': 'Boolean',
    }
    ds = DataSource.get_instance(odps, {'table_name': 'test_data_type3'})
    _, _, sample = ds.sample()

    ti = ds.get_table_info(True)
    logger.info(ti)
    for column in ti['columns']:
        assert column['xlabType'] == odps_columns[column['field']]
        # assert column['pandas_type'] == sample.dtypes[column['field']]
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(odps, {'table_name': 'test_data_type3'}, sampler={'type': 'head', 'count': 1})
    _, _, sample = ds.sample()
    assert len(sample)

    # some engines (spark) handles all null columns differently. put it here just in case
    ds = DataSource.get_instance(odps, {'table_name': 'test_data_type_all_null'})
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(odps, {'table_name': 'zero_count'})
    _, _, sample = ds.sample()
    assert len(sample) == 0

hive = {
    "type": "hive",
    "host": ac.get_value("test_hive_host"),
    "port": ac.get_value("test_hive_port"),
    "username": ac.get_value("test_hive_username"),
    "db": ac.get_value("test_hive_db_zyq")
}


def test_hive_data_source(client):
    """
    hive datasource relies on kerberos, so client is needed

    create table test_data_type(
    ti tinyint,
    si smallint,
    i  int,
    # i2 integer,
    bi bigint,
    f float,
    d double,
    dcm decimal(10,2),
    # n numeric,
    s string,
    # vc varchar,
    # c char,
    ts timestamp,
    dt date,
    # itv interval,
    b boolean
    );

    insert into test_data_type values (1,2,3,4,5.5,6.6,7.7,'8','2019-01-01 00:00:00', '2020-01-01', false);
    """
    hive_columns = {
        'ti': 'Long',
        'si': 'Long',
        'i': 'Long',
        'i2': 'Long',
        'bi': 'Long',
        'f': 'Double',
        'd': 'Double',
        'dcm': 'Double',
        'n': 'Double',
        's': 'String',
        'vc': 'String',
        'c': 'String',
        'ts': 'Date',
        'dt': 'Date',
        # 'itv': 'Date',
        'b': 'Boolean',
    }
    ds = DataSource.get_instance(hive, {'table_name': 'test_l2_partition', 'partitions': ['pt1=1/pt2=1', 'pt1=2']})
    _, _, sample = ds.sample()

    ds = DataSource.get_instance(hive, {'table_name': 'test_data_type'})
    _, _, sample = ds.sample()
    assert len(sample)

    ti = ds.get_table_info(True)
    for column in ti['columns']:
        assert column['xlabType'] == hive_columns[column['field']]
        # assert column['pandas_type'] == sample.dtypes[column['field']]

    ds = DataSource.get_instance(hive, {'table_name': 'test_data_type'}, sampler={'type': 'head', 'count': 1})
    _, _, sample = ds.sample()
    assert len(sample)

    # some engines (spark) handles all null columns differently. put it here just in case
    ds = DataSource.get_instance(hive, {'table_name': 'test_data_type_all_null'})
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(hive, {'table_name': 'zero_count'})
    _, _, sample = ds.sample()
    assert len(sample) == 0


hive_ldap = {
    "type": "hive",
    "host": ac.get_value("test_hive_host"),
    "port": ac.get_value("test_hive_port"),
    "username": ac.get_value("test_hive_username"),
    "password": ac.get_value("test_hive_password"),
    "db": ac.get_value("test_hive_db_zyq")
}


def test_hive_ldap_data_source(client):
    """
    create table test_data_type(
    ti tinyint,
    si smallint,
    i  int,
    # i2 integer,
    bi bigint,
    f float,
    d double,
    dcm decimal(10,2),
    # n numeric,
    s string,
    # vc varchar,
    # c char,
    ts timestamp,
    dt date,
    # itv interval,
    b boolean
    );

    insert into test_data_type values (1,2,3,4,5.5,6.6,7.7,'8','2019-01-01 00:00:00', '2020-01-01', false);
    """
    hive_columns = {
        'ti': 'Long',
        'si': 'Long',
        'i': 'Long',
        'i2': 'Long',
        'bi': 'Long',
        'f': 'Double',
        'd': 'Double',
        'dcm': 'Double',
        'n': 'Double',
        's': 'String',
        'vc': 'String',
        'c': 'String',
        'ts': 'Date',
        'dt': 'Date',
        # 'itv': 'Date',
        'b': 'Boolean',
    }
    ds = DataSource.get_instance(hive_ldap, {'table_name': 'test_l2_partition', 'partitions': ['pt1=1/pt2=1', 'pt1=2']})
    _, _, sample = ds.sample()

    ds = DataSource.get_instance(hive_ldap, {'table_name': 'test_data_type'})
    _, _, sample = ds.sample()
    assert len(sample)

    ti = ds.get_table_info(True)
    for column in ti['columns']:
        assert column['xlabType'] == hive_columns[column['field']]
        # assert column['pandas_type'] == sample.dtypes[column['field']]

    ds = DataSource.get_instance(hive, {'table_name': 'test_data_type'}, sampler={'type': 'head', 'count': 1})
    _, _, sample = ds.sample()
    assert len(sample)

    # some engines (spark) handles all null columns differently. put it here just in case
    ds = DataSource.get_instance(hive, {'table_name': 'test_data_type_all_null'})
    _, _, sample = ds.sample()
    assert len(sample)

    ds = DataSource.get_instance(hive, {'table_name': 'zero_count'})
    _, _, sample = ds.sample()
    assert len(sample) == 0
