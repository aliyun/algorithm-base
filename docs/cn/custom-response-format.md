# 定制响应结构

有时，你需要定制请求返回值的数据结构，目前已支持返回自定义的json格式，示例如下

```
from ab import jsonify


@algorithm()
def custom_response():
    return jsonify({"res": 1})
```
