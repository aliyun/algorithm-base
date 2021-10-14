# API调用限次

注意，这是一个极简的解决方案，需要满足如下条件时可以使用：
- redis和算法服务均部署在公网
- 用户对安全性要求不高

## 启用方式
启用calllimit插件,在config中加入`enable_calllimit=True`即可。该插件依赖redis，所以，config中也应该加入redis的连接信息，比如

```
REDIS = {
    'host': 'localhost',
    'port': 6379,
}
```

# 使用方法

## 分配ak，sk
这里的ak，sk相当于用户调用api的用户名和密码，这样才能限制用户的调用次数。  
随机生成两个字符串分别为ak和sk（最好只包含字母和数字），然后在redis中执行

```
set your-ak your-sk
```

## 编写调用限次API
限制api只能被调用N次, 即在redis添加以下格式的值。  
调用限制规则：`limit:<ak>:<api>`

比如，限制`/api/algorithm/limit`只能被用户`your-ak`调用2次，则redis中命令为
```
set limit:your-ak:/api/algorithm/limit 2
```

## 用户调用
调用时记得把ak和sk放到url中。  
todo： 这样做不安全，待优化

```
curl --location --request POST 'localhost:8000/api/algorithm/limit?ak=your-aksk=your-sk' \
--header 'Content-Type: application/json' \
--data-raw '{
        "args": {"a": 1, "b": 2} 
}'
```


# 其他

如需手动修改调用次数和限制，可以到redis中直接修改。格式如下
- 调用限制：limit:<ak>:<api>
- 当前调用次数: <ak>:<api>

```
"limit:your-ak:/api/algorithm/limit"
"your-ak:/api/algorithm/limit"
```
