# 许可证服务

该服务可以先定容器只能运行在指定的物理机/虚拟机上

## 使用方法

### 预检

在客户的目标宿主机上，运行 `sudo sh pre.sh`. 同目录下会生成一个名为`pre.output`的文件，将`pre.output` 带回公司，用于生成许可证.

### 生成许可证

执行如下命令，许可证文件将会被打印到控制台，同时该目录下生成一个名为`license.ab`的许可证。理论上，这个许可证属于哪个客户，哪台服务器应该被正确记录到文档上。
```
python license.py <pre.output的路径> <许可证有效天数>
```

### 在核心算法中嵌入许可代码
将下列代码粘贴到项目根目录的`algorithms`目录下的任意一个文件中(最好是最核心的代码中)，且该文件在打包时务必启用python加密。当然，你可以把这段代码粘贴到所有算法文件中，可以提高安全性.

```
from ab.decorate.warmup import warmup
@warmup()
def start():
    """
    将这段代码注入到核心算法接口中，以便实现license检查
    :return:
    """
    from ab.utils import logger
    from ab.keys.crypto import license_verify
    from ab.plugins.prob import restart_handler
    try:
        license_verify("license.ab")
    except Exception as e:
        logger.error(e)
        logger.set_level('FATAL')
        restart_handler()
```

### 构建算法镜像
省略

### 启动服务,验证许可证

启动容器时，将上述license.ab文件挂载到容器的/root/app目录下，并将宿主机的`/etc`目录挂载到`/mnt`目录，服务将在启动时验证许可证授权信息.  
验证如果未通过，error.log中会出现`invalid license`字样。

```
docker run -v /etc:/mnt -v `pwd`/license.ab:/root/app/license.ab <your-image>
```


例如，以下命令是我在本机调试框架和许可证功能时的启动命令,值得注意的是，在OSX系统中，/etc目录其实是/private/etc的链接
```
docker run -p 8000:8000 -v /private/etc:/mnt:ro -v `pwd`:/root/app/  -v /Users/peng/Documents/project/algorithm-base/src/ab:/usr/local/lib/python3.7/site-packages/ab registry.cn-hangzhou.aliyuncs.com/medical-care/simple:0.0.2
```

## 其他
### 本地调试怎么办？
of course，你可以用上面的办法，为自己的调试环境颁发许可证。为了减少被破解的风险，框架就不提供后门了。

### 更新许可证

按照上面步骤，重新创建一遍即可

### 手动验证许可证 

是否验证通过, 未打印异常即代表通过

```
abt license -v license.ab
```
