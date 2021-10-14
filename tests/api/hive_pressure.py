from ab.utils.data_source import DataSource

hive = {
    "type": "hive",
    "host": "sw2",
    "port": 10000,
    "username": "hive",
    "db": "bank_visual"
}


def test_hive_pressure(client):
    # 650k rows
    ds = DataSource.get_instance(hive, {'table_name': 'account'}, cacheable=False,
                                 sampler={'type': 'head', 'count': 100000})
    ds.sample()
