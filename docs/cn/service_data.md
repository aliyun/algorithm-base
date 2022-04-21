
# 数据与API

很多情况下，`算法`是建立在`数据`之上的。`数据`可能存储在rds/sqlite/hive等各种持久化软件中。为了快速实现`算法`,我们将API抽象为`数据`->`算法`


# 使用方法

```
@algorithm()
def your-algorithm(data, table_info, sample_count, sample_rate):
    pass
```

按照如上方式定义算法签名，在`传入数据源`后，会根据`参数名称`自动注入如下信息

- data: 表中数据的DataFrame(pandas或spark，根据engine而不同)，根据输入的data_source_id和table_name、partitions生成
    如果是引擎是python则强制采样，默认返回最多10w条。可以简单理解为相当于`select * from table_name limit 100000`
- table_info: 输入表的建表语句和表数据量大小、表内容行数等信息，格式参考utils/data_source.py中的get_table_info函数说明 
- table_name: 表名
- sample_count：采样数量
- sample_rate: 采样率


# 获取数据的优先级

优先级由高到低排序， 下面分别举例

- request传入的数据源
- 算法装饰器定义的数据源
- config中配置的数据源


## request传入数据源

详见 `examples/data_source` 中的例子。步骤如下

- 启动服务
```
pyab
```

- 使用如下语句测试,在request时动态传入数据源（通常，这一步由后端工程传入）
```
curl --location --request POST 'http://localhost:8000/api/algorithm/head' \
--header 'Content-Type: application/json' \
--data '{
    "data_source": {
        "host": "",
        "type": "sqlite",
        "port": 3306,
        "username": "",
        "password": "",
        "db": "data.db"
    },
    "args": {
        "table_name": "USER"
    }
}'
```


## 算法装饰器定义的数据源

详见 `examples/data_source` 中的例子。步骤如下

- 将数据源绑定算法签名

```
@algorithm( db="data.db", type="sqlite")
def dec_datasource(data, table_info, sample_count, sample_rate):
    return data.head(10)

```

- 启动服务
```
pyab
```

- 使用如下语句测试

```
curl --location --request POST 'http://localhost:8000/api/algorithm/dec_datasource' \
--header 'Content-Type: application/json' \
--data '{
    "args": {
        "table_name": "USER"
    }
}'
```


## config中配置的数据源

详见 `examples/data_source` 中的例子。步骤如下

- 在config中指定data_source
```python
DATA_SOURCE = {
    "host": "",
    "type": "sqlite",  # 支持mysql，odps，hive等
    "port": 3306,
    "username": "",
    "password": "",
    "db": "data.db",
}
```

- 启动服务
```
pyab daily
```

- 使用如下语句测试
```
curl --location --request POST "http://localhost:8000/api/algorithm/head" --header "Content-Type: application/json" --data '{
    "table_name": "USER"
  }'
```


# 使用自定义的sql进行查询

- 定义算法签名

- 请求时，传入`sql`字段，则会将查询结果以DataFrame的形式注入签名的data字段
```
curl --location --request POST 'http://localhost:8000/api/algorithm/head' \
--header 'Content-Type: application/json' \
--data '{
    "data_source": {
        "host": "",
        "type": "sqlite",
        "port": 3306,
        "username": "",
        "password": "",
        "db": "data.db",
        "sql": "select age from USER where age > 90"
    }
}'
```


# 数据源定义的格式

以request传入模式为例：

```
    "data_source": {
        主机地址。如果是sqlite，则保持空字符串
        "host": "",
        
        默认mysql，支持mysql，sqlite，odps，hive
        "type": "sqlite", 
        "port": 3306,
        
        "username": "",
        "password": "",
        
        数据库的名字
        "db": "data.db"
    },
    "args": {
        要查询的表名
        "table_name": "USER"
    }
```


