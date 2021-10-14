
# 自定义接口

## quick-start
在项目根目录的`algorithms`目录下，为方法增加 @algorithm注解即可。服务启动后，就可以用 /api/algorithm/add 访问到服务了

```
from ab.utils import logger
from ab.utils.algorithm import algorithm
from ab import app

@algorithm()
def add(a, b):
    logger.warning("enter algorithm {}, {} ".format(a, b))
    return a + b
```

## algorithm装饰器详解
算法使用`@algorithm(name='你的算法名', engine='你算法运行的引擎')`装饰器将算法入口函数注册到框架。原理和flask的app.route类似。

- name: 不填则默认使用函数名。
- engine: 同一个算法名可以注册多种不同引擎。目前支持`python`和`spark`两种。不填默认使用`python`。

框架根据请求的`algorithm`, 和`engine`字段自动调用对应的注册的算法函数。(算法名, 引擎)合起来唯一标志一个算法入口函数。

目前框架自动生成的main函数的参数有以下几个：
* task_id: 当前任务的uuid，每次进入main函数生成一个不重复的。主要用于异步任务的时候手动向数据库塞数据用。
* data_source_id: 云计算资源id(此功能和disuite耦合，待重构)
* table_name: 表名
* data: 表中数据的DataFrame(pandas或spark，根据engine而不同)，根据输入的data_source_id和table_name、partitions生成
    如果是引擎是python则强制采样，默认返回最多10w条。可以简单理解为相当于`select * from table_name limit 100000`
* table_info: 输入表的建表语句和表数据量大小、表内容行数等信息，格式参考utils/data_source.py中的get_table_info函数说明
* recorder: 异步算法需要的记录算法执行状态的handler。调用recorder.update_status可以更新算法执行状态。
    算法同学开发算法的时候可以使用`from ab.utils.recorder import DummyRecorder`作为占位符
* cache_client: 缓存客户端，可直接调用get/set/get_set_cache
* dfs_client: 分布式文件系统客户端，可直接调用open读写文件。可看例子：[dfs_example.py](src/tests/api/algorithms/dfs_example.py)
* eureka_client: eureka客户端 (Since v2.3.1)
* spark: SparkSession实例

更复杂的main函数示例可见[async_example.py](src/tests/api/algorithms/async_example.py)。



# 内置接口
### POST /api/data_source/{data_source_id}/table/{table_name}/algorithms

**接入di suite优先使用此接口，不接入不用看**

执行算法的接口

注意：使用此接口必须要配置config.EUREKA_SERVER才能根据data_source_id获取data_source连接串

path variable:
* data_source_id: 数据源的id
* table_name: 表名

body:
```
{
        // 执行引擎。目前支持type为python/spark。如果不写默认为python
        "engine": {
            "type": "spark"
        },
        "mode": "sync/async_pool/async_unlimited",    # 同步/异步进程池/异步新进程执行。不写默认sync
        "sampler": {   // 采样器，没有默认为随机采样10万行。仅在engine为python时有效
            "type": "random",  // 采样方法。random: 随机采样; head: 头部(最旧）采样; tail: 尾部（最新）采样
            "count": 1001      // 采样条数
        },
        "algorithm": "algorithm名称",
        "cacheable": true/false, # 是否从redis缓存中读取data，debug用。没有则默认为true
        "args": {  // 请求参数，会原样传递给main函数，内容任意即可
            "name": "fangliu"
        }
    }
```
response:
```
同步执行：
{
    "code": 0,
    "data": {
        "sample_rate": 100,  // 采样率
        "sample_count": 50,  // 采样行数
        "result": 算法返回值
    }
}

异步执行：
{
    "code": 0,
    "data": "异步task_id"
}
```


### POST /api/algorithms
**不接入di suite使用此接口即可，需要自己拼连接串**

执行算法的接口

body:
```
{
        // 数据源。因spark目前不支持odps，如果数据源为odps，则engine必须为python
        "data_source": {
            "host" : your-host,
            "port" : your-port,
            "username" : your-username,
            "password" : your-password,
            "db" : "test"
        },
        // 执行引擎。目前支持type为python/spark。如果不写默认为python
        "engine": {
            "type": "spark"
        },
        "mode": "sync/async_pool/async_umlimited",    # 同步/异步进程池/异步新进程执行。不写默认sync
        "sampler": {   // 采样器，没有默认为随机采样10万行。仅在engine为python时有效
            "type": "random",  // 采样方法。random: 随机采样; head: 头部(最旧）采样; tail: 尾部（最新）采样
            "count": 1001      // 采样条数
        },
        "args": {  // 请求参数，会原样传递给main函数，内容任意即可
            "table_name": "e_annual_performance",
            "name": "fangliu"
        }
    }
```
response:
```
同步执行：
{
    "code": 0,
    "data": {
        "sample_rate": 100,  // 采样率
        "sample_count": 50,  // 采样行数
        "result": 算法返回值
    }
}

异步执行：
{
    "code": 0,
    "data": "异步task_id"
}
```

### GET /api/task
获取异步算法任务列表

query string:
* page: 第几页
* size: 每页条数

response:
```
{
    "code": 0,
    "data": [{
            "code": 2,  // 0：新建， 1：执行中，2：运行结束，-1：异常
            "task_id": "d97704ef0b704b54bb777de090531eef",
            "app_name": "algorithm-base-demo-app",
            "algorithm_name": "async_example",
            "status": "begin", // 算法状态
            "gmt_create": "2019-09-02 19:35:52.000",
            "gmt_modified": "2019-09-02 20:23:34.000"
        }
    ]
}
```


### GET /api/task/{task_id}/
获取异步算法任务状态。比上述算法列表多了data/log字段

path variable:
* task_id: 上面接口返回的异步task_id

response:
```
{
    "code": 2,  // 0：新建， 1：执行中，2：运行结束，-1：异常
    "task_id": "d97704ef0b704b54bb777de090531eef",
    "app_name": "algorithm-base-demo-app",
    "algorithm_name": "async_example",
    "status": "begin", // 算法状态
    "data": {
        "sample_rate": 100,  // 采样率
        "sample_count": 50,  // 采样行数
    }, // 算法的返回值
    "spark_app_id": "xxx", // spark application id
    "log": "yyy",  // spark及算法中print的log
    "gmt_create": "2019-09-02 19:35:52.000",
    "gmt_modified": "2019-09-02 20:23:34.000"
}
```

### DELETE /api/data_source/{data_source_id}/table/{table_name}/cache
删除表的所有缓存

response:
```
{
    "code": 0,
    "data": "success"
}
```

   
# 接口格式

## 自定义返回格式
正常情况下，所有的接口默认返回`{"code": 0, "data": xxx}`这样的结构。

如果不想遵循这个格式，可以直接返回flask.Response对象，框架不会做任何处理。

## 返回二进制下载文件

```python
    from flask import make_response
    response = make_response(YOUR_CONTENT)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename={YOUR_FILENAME}'
    return response
```

## 返回异常
1. ab框架有一个默认异常类, 常见用法如下：

```python
from ab.utils.exceptions import AlgorithmException

try:
    1 / 0
except Exception as e:
    # from e必须要加，否则log会丢失异常栈，无法复现问题
    raise AlgorithmException(code=-100, data=YOUR_MSG) from e
```

则前端就会得到如下接口返回值：

```
{
    "code": -100,
    "data": YOUR_MSG
}
```

2. 如果抛出了未被捕获的异常，则前端接口会返回：

```
{
    "code": -1,
    "data": 异常堆栈
}
```

更多信息，详见 [异常与错误处理](error.md)


# 已知问题
- 通过/api/task可以查看所有结束的任务，目前没有删除机制
