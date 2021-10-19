# 加密数据文件

支持加密二进制文件和文本文件

# 使用流程
整个加密，解密流程，对用户是无感的，只要你正确使用了框架提供的文件读写api，是不需要关心加密，解密的。  

## 例子
比如，文本文件`resource/mydata`, 内容如下

```
hello crypto!
```

`如果你希望该文件在镜像中被加密`，则需要在项目的描述文件`.ab`中定义需要加密的文件列表。如
```
#!/bin/bash

app_name=simple
app_version=0.0.1

# [选填] 需要加密的数据文件列表,支持正则表达式
enable_crypto=true
crypto[0]=xxxx
crypto[1]=resource/.*data

enable_encrypt_python=true

```

[这篇文档](https://yuque.antfin.com/hs938q/ew0q9f/bush0g)里有详细描述。**值得注意的是，如果不启用加密数据文件,即`enable_crypto=false`,框架会在打包时，自动将algorithms/__init__.py置为空值**
**注意，如果希望启用数据加密，务必设置enable_crypto=true 和 enable_encrypt_python=true**


在python中，使用如下方式读取该文件。打包后，镜像中的文件会被自动加密，并删除明文文件。同时，`read_text` 将把密文解密到内存中。

```
from ab.keys.data import read_text

@algorithm()
def crypto():
    """
    读取加密文件
    :return:
    """
    return read_text("resource/mydata")

```

## 支持的方法
- read_text：一次性读取文本全部内容,并以字符串形式返回，默认使用utf-8的编码
- read_json：一次性读取二进制文件全部内容，并解析为json格式
- read_pickle: 一次性读取二进制文件全部内容，并解析为pickle格式
- open_text: 读取文本文件，以StringIO的形式返回
- open_binary: 读取二进制文件，以bytearray的形式返回

## 更多的例子
[看这里](tests/api/test_encrypt_file.py)

- 在pytorch中使用加密的模型
```
with open_binary(model_dir+"/torchscript/traced_bert.pt") as f:
    buffer = io.BytesIO(bytes(f))

model_diagnose = torch.jit.load(buffer)
```

## 其他格式如何处理
假如框架没有提供read_json方法，你希望对json格式加密读取，只需要将json文件看成是纯文本文件，使用read_text方法读取，然后自行用json.load即可。其他格式文件不赘述


# 手动加密流程
**不是吃饱了撑的，不用看这一节，框架开发者除外**

## 加密
根据`.ab`文件中的配置，使用如下命令即可。-i后面是正则表达式。加密时需要传入密钥，由于加密环境是安全的，所以选择用环境变量你的方式传入密钥。详见crypto.sh中的使用方式

```
abt crypto -i "resource.*"
```


## 解密
在每一个基于ab框架的项目中，`algorithm/__init__.py` 定义了密钥，并覆盖了上述环境变量。详见`支持的方法`和 `simple`项目的例子
