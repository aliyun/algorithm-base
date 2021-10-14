# http 压缩

## response压缩

如果API返回长文本，你希望对响应体进行压缩，框架会自动帮你实现。


### 实现API
先实现一个普通的接口
```
@algorithm()
def compress() -> int:
    return "long text"
```

该接口的未压缩API是
```
/api/algorithm/compress
```

该接口的压缩API是
```
/api/algorithm/compress.zip
```

### 访问API

如果不想自己解压缩，请使用框架里安装好的python Requests API
```
import requests

r = requests.get('http://your-host:your-port/api/algorithm/compress.zip')
print(r.status_code) ## 200 
print(r.text) 
```

返回：
```
{"code":0,"data":{"sample_rate":null,"sample_count":null,"result":"long text"}}
```

### 原理
压缩返回 `Content-Encoding: gzip` 格式，其他客户端可自行解压缩

## request压缩
todo
