# 模型预热
某些CPU消耗性的模型，在首次加载运行时非常耗时，可能会触发timeout。框架支持@warmup标签，在服务初始化时对特定的业务逻辑进行预热。
```
@warmup()
def some_function():
    print("you can do warmup here")
```

注意，warmup方法，发生在gunicorn的post_worker_init阶段。
