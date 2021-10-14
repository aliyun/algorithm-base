# Redis

## 配置
- 在配置中加入如下配置，可以启用redis功能

```
REDIS = {
    'host': 'your-host',
    'port': 'your-password',
    'password': 'your-pwd'
}
```

- 使用异步任务时，必须先开启redis功能

## 使用

- 在代码中，通过获得redis单例，可以对redis进行读写操作

```
import 
from ab.plugins.cache.redis import cache_plugin

cache_client = cache_plugin.get_cache_client()
cache_client.get(xxx)
cache_client.set(xxx)

```
