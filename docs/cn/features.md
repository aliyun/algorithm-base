
# 全部配置

## 配置都包含了什么
- 配置ab框架的插件
- [flask的配置项](http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values) 都是大写，
- [gunicorn的配置项](http://docs.gunicorn.org/en/stable/settings.html) 都是小写，
- 用户自定义的配置


## 详细配置项
ab的config继承自flask和gunicorn并加了些ab自有的配置项。因此可以写在同一个config.py文件里。算法同学一般不用改这些配置。

目前支持配置项：
* APP_NAME: 算法名，用于注册到spring cloud。每个算法保证不和其他算法重复即可。
            since v2.4.2:分隔符要使用'-'，不可使用'_'。
            部署到服务器上必须改掉。必填。
* DB: ab的后台数据库，保存历史任务信息。必填。（Since v2.2.5)
* DBM: 把数据库CRUD操作封装成api暴露给前端，简化后端开发。（Since v2.2.8）
* PORT: 端口号不再支持修改。在docker内，nginx固定使用80端口去访问gunicorn的8000端口
* HOST: 绑定哪个IP。一般本机测试用`localhost`，部署到服务器上用`0.0.0.0`。默认为'localhost'。
        参考：[What is the difference between 0.0.0.0, 127.0.0.1 and localhost?](https://stackoverflow.com/questions/20778771/what-is-the-difference-between-0-0-0-0-127-0-0-1-and-localhost)
* DEBUG: 是否打开flask和gunicorn的debug模式，默认为False。
         DEBUG=True实际上允许执行任意代码，部署到服务器上时禁止HOST=0.0.0.0和DEBUG=True的组合。
* LOG_LEVEL: 全局默认日志级别。底层依赖python的logging模块。
             logging的级别参见：[logging levels](https://docs.python.org/3/library/logging.html#levels)
             不填默认级别为`INFO`。
* EUREKA_SERVER: 注册到哪个eureka。要接入disuite必填。
* REGISTER_AT_EUREKA: 是否将本服务注册为eureka client。要接入disuite必须为True。默认False。
* REDIS: redis配置。使用异步任务就必填。
* SPARK: spark配置。spark的所有配置项见：[spark configuration](https://spark.apache.org/docs/latest/configuration.html)。
         使用spark必填。
* KERBEROS: kerberos配置。支持keytab和password两种方式。使用kerberos必填。
* DFS: 分布式文件系统配置。目前支持用于开发的本地文件系统local模式和分布式hdfs模式。不填默认local模式。
* STATIC_FOLDER: 静态文件在项目里的相对路径。(Since v2.5.3)
* STATIC_URL_PATH: 静态文件映射的url。注意一定要以'/'开头。(Since v2.5.3)
* 插件配置： enable_xxx，详见插件文档
