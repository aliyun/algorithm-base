
## 如何实现一个插件

- 在ab.plugins目录下新建python包，比如`calllimit`目录

- 在上述目录下新建`__init__.py`, 其中要做两件事
  - import需要用到的python文件
  - 指定`plugin_instance`. `plugin_instance` 是插件启动类

```
from ab.plugins.calllimit.core import *

plugin_class = CallLimit()

```


### 插件启动类
一个插件启动类形如, 在flask加载app时，会自动调用start方法。
todo:卸载时应调用stop方法。

```
class CallLimit:

    def __init__(self):
        self.platform = None

    def set_platform(self, platform):
        self.platform = platform

    def start(self):
        logger.info("[plugin] CallLimit start")

    def stop(self):
        logger.info("[plugin] CallLimit stop")
```

### 启用插件

#### 方法一
比如插件的包名为xxx，只需在config中指定enable_xxx = True , 即可启用插件

#### 方法二
某些需要额外配置的插件，比如redis，不是通过enable_xxx 的形式启动插件，而是通过自己的配置 `REDIS` 启动插件。
这种情况，需要在`platform.py`中定义插件文件夹和插件配置的关联，

```
plugin_alias["cache"] = "REDIS"
```


### todo:

- 支持自定义插件启动顺序
