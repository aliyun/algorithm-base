# 滚动日志

## 打印日志

日志要求统一使用logger，使用方法如下：
```python
from ab.utils import logger

# https://docs.python.org/3/library/logging.html#module-logging
logger.debug/info/warning/error/exception/critical('hello', 'world')
```
日志是分级别的，最低是debug，数量多但不太重要。最高是critical，数量很少但会非常重要。

配置里的`LOG_LEVEL`设置为某个等级后，低于这个等级的log就不会打印出来。

默认的日志等级为`INFO`。

**不要直接调用print打log。调用print打印的内容默认不会显示出来。框架不保证会保存print输出的内容到本地日志，出了问题查都没法查。**



## 日志文件
由于在docker中安装了cron服务，日志文件可以按天被分割开，并最多保留30日内的日志。  

- 根据config_prod.py中的默认配置，日志会被记录到如下文件中。默认情况下，日志文件会以服务启动的时间戳区分。
```
accesslog='logs/access.log'
errorlog='logs/error.log'
```

- 某些情况下，你可能希望日志文件的文件名称固定不变，可以在文件名中加入`fix`字符串，这样，日志文件名就不会以时间戳结尾了。
```
accesslog='logs/fixaccess.log'
errorlog='logs/fixerror.log'
```
