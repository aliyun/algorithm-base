# 请求类型

## 同步请求

同步请求，请求后会一直阻塞等待返回结果，用于请求耗时较短的请求。

在请求参数中，加入如下参数即可, mode参数的默认值就是sync。
```
"mode"="sync"
```

## 异步请求

异步请求，请求发出后，会立刻返回`taskId`, 随后根据`taskId` 查询请求状态，最终获得请求返回值。用于请求耗时长，非实时的任务，比如Hive，ODPS，Spark等。

在请求参数中，加入如下参数即可
```
"mode"="async"
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
获取异步算法任务状态。比上述算法列表多了data/log字段。状态返回值`code`

```
"code": 2,  // 0：新建， 1：执行中，2：运行结束，-1：异常
```

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

## 已知问题
- 通过/api/task可以查看所有结束的任务, 没有被删除掉
