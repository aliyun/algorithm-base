## 要求
如果需要部署多个实例做HA，则需要配置`config.DB`以存储任务状态，格式参考[sqlalchemy连接串格式](https://docs.sqlalchemy.org/en/13/core/engines.html)。
理论上sqlalchemy支持的数据库应该都支持，不过只测试过mysql和sqlite。

ab框架会自动创建名为`task`的表。

如果只需要部署一个实例则不用配置config.DB。

## 使用方法
1. 新建异步任务

    和新建同步任务参数基本一致，唯一的区别是加上`"mode": "async_unlimited"`参数指定请求为异步请求。
    
    异步任务调用会立即返回，接口里会包含task_id作为本次异步任务的唯一id。
    
    PS：所以有一个技巧就是测试用例写成同步的，方便debug
    
2. 获取任务状态

    调用`/api/task/{task_id}`接口可以获取任务当前的状态。具体格式看测试用例
    
## curl调用例子
1. 新建异步任务
    ```
    curl --location --request POST 'http://127.0.0.1:2333/api/algorithm/async_work' \
    --header 'Content-Type: application/json' \
    --data-raw '{
            "mode": "async_unlimited",
            "args": {
                "run_seconds": 20
            }
    }'
    ```

2. 获取任务状态
    ```
    curl --location --request GET 'http://127.0.0.1:2333/api/task/04ad7d0c2a854cf3b3d7c95dd5b9a238'
    ```
    
## TODO
自动callback

timeout


## 工程相关说明，没有遇到问题不用看
异步执行是通过fork新进程来实现的。

mode有两个可取的值：
* async_unlimited：每次请求都新建一个进程执行
* async_pool：使用一个进程池来处理请求，每个gunicorn worker一个进程池。
              进程池大小使用`config.ASYNC_POOL_SIZE`来控制，默认为2。

注意：有些库是不支持fork的，使用异步模式就会出现segment fault之类的错误，有两个解决办法：
1. 在请求达到`@algorithm`之后再初始化
2. 设置config.preload_app = False

不支持fork就无法共享内存，每个worker都需要单独申请内存，要注意启动后的内存占用情况。

如果只部署一个实例，任务状态是通过sqlite保存的，可以通过`sqlite3 /tmp/ab.db`连接。

