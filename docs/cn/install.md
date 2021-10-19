
# 安装

## 安装之前

强烈建议国内用户更改pip源，以加速安装速度 `~/.pip/pip.conf`

```
[global]
timeout = 6000
index-url = http://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
```


## 使用源代码安装(推荐)
- 先clone AB框架源代码

gitlab用户（内部）
```
git clone git@gitlab.alibaba-inc.com:medical-care/algorithm-base.git
```

github用户

```
git clone https://github.com/aliyun/algorithm-base.git
```

- 进入项目根目录，按照如下命令安装

```
pip install . 
```

- 对于ab框架开发者，进入ab框架根目录，调试安装

```
pip install -e .
```


## 离线安装

- 某些情况下，服务器无法连接到网络，可以先从能联网的机器上，下载指定tag的zip压缩包，然后通过pip离线安装

```
pip install ab-xxxx.tar.gz
```

如果需要在dockerfile中离线安装，需要将ab框架的tar.gz包先copy到docker内部再执行安装，比如

```
COPY ./setup/ab-xxxx.tar.gz ./ab-xxxx.tar.gz
```

## 依赖

- 使用abt的file,logs命令，需要单独安装ossutil，请根据[oss文档](https://help.aliyun.com/document_detail/120075.html) 进行安装


## 关于版本号
ab框架版本号使用major.middle.minor.bugfix模式

* major版本号变更代表代码完全不兼容，需要修改代码才能完成升级
* middle代表需要**修改配置**即可升级。算法同学需要注意下
* minor代表新特性，但无需修改代码即可直接升级
* bugfix就是修复bug
