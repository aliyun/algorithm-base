# 健康检查

## 原理
当服务启动initialDelaySeconds秒后，每隔periodSeconds秒进行一次健康检查，如果连续failureThreshold次不能在timeoutSeconds秒内返回，则认为服务已经失去响应，遂杀掉服务主进程，依赖docker的restart=always机制重启服务。  
这是默认的存活检查配置，你可以选择关闭健康检查，也可以调整健康检查的频率.  

如果健康检查持续失败，会导致主进程被杀掉。依赖docker的restart=always机制，达到服务重启的目的。  

额外，健康检查也可以在某种程度上达到预热服务的作用，尤其是在高内存消耗的服务中，合理配置 initialDelaySeconds 等参数，可以达到上述目标。

## 配置
```
ENABLE_LIVENESS_PROB = True
LIVENESS_PROB = {
    # 容器启动后要等待多少秒后存活和就绪探测器才被初始化，最小值是 0。
    "initialDelaySeconds": 180,
    # 执行探测的时间间隔（单位是秒）。最小值是 1。
    "periodSeconds": 60,
    # 探测的超时后等待多少秒。最小值是 1。
    "timeoutSeconds": 1,
    # 当连续失败N次后，重启容器
    "failureThreshold": 5,
}
```

## 其他
todo: 待重构为插件
