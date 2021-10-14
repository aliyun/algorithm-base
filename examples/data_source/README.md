## 适用范围
本demo适用于一次请求要读取rds/odps/hive中的全表的需求。

如果需要定制化执行各种sql，简单的可以看看[mapper](mapper/)的例子，复杂的需要自行实现。

如果表很大，建议去看看[spark](spark/)的demo。

## 要求
内容有点长，建议先去看代码。

1. ab >= 2.6.4

2. 传递连接串。

    格式：
    
    ```
    RDS:
        {
            "host": "YOUR_HOST",
            "port": 3306,
            "username": "YOUR_USERNAME",
            "password": "YOUR_PASSWORD",
            "db": "YOUR_DB"
        }
    ```
    ```
    ODPS:
        {
            "type": "ODPS",
            "project": "YOUR_DB",
            "access_id": "YOUR_USERNAME",
            "access_key": "YOUR_PASSWORD",
            "endpoint": "http://service.odps.aliyun.com/api"
        } 
    ```
    ```
    HIVE(通过keytab的鉴权，需要配合config.KEYTAB使用):
    KERBEROS = {
    'principal': 'YOUR_PRINCIPAL',
    'keytab': 'PATH_TO_YOUR_KEYTAB_FILE',
    'refresh_interval_in_seconds': 60
    }
    DATA_SOURCE = {
        "type": "hive",
        "host": "YOUR_HOST",
        "port": 10000,
        "username": "YOUR_USERNAME",
        "db": "YOUR_DB"
    }
    ```
    ```
    HIVE(用户名密码方式）:
    {
        "type": "hive",
        "host": "YOUR_HOST",
        "port": 10000,
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD",
        "db": "YOUR_DB"
    }
    ```
    传递方式：
    ```
    1. config.FORCE_DATA_SOURCE
    2. request body里的data_source字段
    3. config.DATA_SOURCE字段

    优先级 1 > 2 > 3
    ```

3. （可选）指定采样方式。实践中发现表可能会过大导致内存不足/读取超时之类的问题，因此需要对数据大小设置上限。ab框架使用强制采样的方式实现
    
    格式：
    ```
    {
       # 采样方式。head就是select * from {table} limit {count}
       'type': 'head', 
       # 采样行数
       'count': 100000
    }
    ```
    设置位置：
    ```
    1. config.FORCE_SAMPLER
    2. request body里的sampler字段
    3. config.SAMPLER

    优先级 1 > 2 > 3
    ```
    如果以上都没有设置，则默认head采样100000行

4. (可选)缓存
    
    配置了config.REDIS之后就可以使用缓存存取数据了，多实例可以共享一份缓存，超时时间可以使用`config.CACHE_TIMEOUT`（单位秒）设置。
    
    如果某次请求不想用缓存的话，可以在request body里指定`cacheable=false`
    
    如果没有配置config.REDIS，则默认每次都去读数据库

5. 在请求里使用`args.table_name`字段指定要读取的表，就能得到data, table_info, sampler_count, sampler_rate这四个需要的字段了。字段详细说明见demo的接口文档


## curl调用例子
```
curl --location --request POST 'http://127.0.0.1:2333/api/algorithm/head' \
--header 'Content-Type: application/json' \
--data-raw '{
	"sampler": {"type": "head", "count": 10},
	"args": {
		"table_name": "task"
	}
}'
```


## 工程相关的说明，没遇到问题可以不看
Q: 为什么不使用和config.DB同样的sqlalchemy连接串格式？
    
A: 因为sqlalchemy不支持odps