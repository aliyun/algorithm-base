# 文档

在项目的根目录下，编写`doc.yaml`可以实现支持嵌套层级的文档

一个示例,注意
- 下面所有的字段都是必填
- request有且仅有5个字段，分别代表参数名，参数类型，描述，示例值，是否为必须。空值请用空格表示
- response有且仅有4个字段，分别代表参数名，参数类型，描述，示例值。空值请用空格表示
- 填写完成后，务必启动服务，访问/doc接口查看是否报错。如果有报错，请根据提示修复。

```
---
apiName: 8个字以内的中文描述
apiUrl: /api/algorithm/add
method: GET|POST
desc: 测试请求参数中含有2个基本类型
tag:
  - demo
visible: false
request:
  - a||int||第一个参数（必填）||1.0||true
  - b||int||第二个参数 || 2||false
response:
  - sum||int||两个数之和||1.0
sampleCode: >-
  curl --location --request POST ''http://{ip}:{port}/api/algorithm/add'' --header ''Content-Type: application/json'' --data ''{sampleRequestCode}''
sampleRequestCode: >-
  {
    "args": {"a": 1, "b": 2}
  }
sampleResponseCode: >-
  {"code":0,"data":{"sample_rate":null,"sample_count":null,"result":3}}


```

访问接口
```
curl http://host:port/doc
```


# 路由表

获得算法名称和算法服务名称的对应关系

访问接口
```
curl http://host:port/routing
```
