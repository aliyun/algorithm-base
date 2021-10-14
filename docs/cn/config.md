# 多环境配置
配置统一放在项目根目录的config目录下。

## 配置加载优先级（从高到低）
- 从环境变量中，加载键值对覆盖配置
- 从config目录的config_xxx.py中加载指定xxx环境的配置
- 从config目录的config.py中加载配置
- 加载ab框架的默认配置。


### 例子  
- 使用默认的配置启动服务

```
pyab
```

- 使用test环境的配置启动服务，即使用test环境的配置继承默认配置

```
pyab test
```

- 使用daily环境的配置继承默认配置启动服务，并设置workers的数量为4

```
workers=4 pyab daily
```

- 使用local和daily的配置启动服务，local（靠左侧）的优先级更高，同时继承默认配置

```
pyab local daily
```

*请注意，`debug`是框架预留的关键字，不可以作为配置的环境名，比如config_debug.py是不会生效的*
   
### 在容器中使用配置
- 容器启动，默认使用prod环境的配置（即优先使用config_prod.py中的配置）

```
docker run your-image
```   

- 容器启动，使用指定环境（local）的配置（默认支持local,daily,prod三个环境)

```
docker run your-image local
```


   
## 读取配置项  
配置项注入了flask的config，推荐的读取方法如下：

```python
from ab import app

app.config['YOUR_CONFIG_KEY']
# or
app.config.YOUR_CONFIG_KEY
```
