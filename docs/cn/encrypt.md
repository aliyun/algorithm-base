# 加密代码

## 自动加密
自动加密发生在构建镜像时，需要在项目根目录的`.ab`中配置加密选项。  
默认加密所有python文件，如果有不需要加密的源码，需要添加`不加密`的文件列表，支持正则表达式。

```
#!/bin/bash

app_name=simple
app_version=0.0.1

# [选填] 加密的python文件，从include的文件中排除掉exclude的文件。
enable_encrypt_python=true
encrypt_python_include[0]=.*
encrypt_python_exclude[0]=config/config.*.py
encrypt_python_exclude[1]=setup
```


## 手动加密
- 加密执行目录下的所有python文件
```
abt encrypt
```

- 加密执行目录下的所有python文件,但排除某些文件，排除匹配模式符合正则表达式标准(注意：只有python包（具有__init__.py)下的文件会被加密)
```
abt encrypt --include=".*" --exclude="config/config.py,__init__"
```

- 加密执行目录下的所有python文件,并删除python和c源文件(注意：只有python包（具有__init__.py)下的文件会被加密)
```
abt encrypt --clear=True
```

## 注意事项
- 只有符合python模块规范的模块下的文件（具有__init__.py)会被正确加密
- 使用AB框架模板，默认使用自动加密



