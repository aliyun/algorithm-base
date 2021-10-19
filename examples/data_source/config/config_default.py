

# 默认只取一行数据，可以被request body里的参数覆盖
SAMPLER = {'type': 'head', 'count': 1}

# 默认使用此数据源，可以被request body里的参数覆盖
DATA_SOURCE = {
    "host": "YOUR_HOST",
    "port": 3306,
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "db": "YOUR_DB"
}