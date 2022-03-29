# 如何创建新项目

## 自动创建

- 使用abt命令创建新项目
备注(fixme)： 
安装在site-pacakge下的ab框架，其实是不包含examples代码的

如果你需要创建基于ab框架的项目，目前的方式有些繁琐，如下

1. 先git clone AB框架的代码到某个目录
2. 进入上面的目录，使用pip install -e . 安装源码
3. 使用如下命令创建项目

```
abt project create -n your-project-name
```

- 启动服务
```
cd your-project-name
pyab
```


## 手动创建
新项目以examples/simple项目为模板，请在AB框架根目录执行以下命令，详细步骤如下

- 新建名称为`hello-world`的项目，复制`examples/simple`项目到指定位置（这里以`tmp`目录为例）

```
cp -r examples/simple /tmp/hello-world
```

- 把字符串`simple`替换为`hello-world`.(以下命名可以在MAC运行)

```
find /tmp/hello-world/ -name \*.py -o -name \*.sh -o -name \*.md | xargs grep -l "simple" | xargs sed -i '' 's/simple/hello-world/g'
```

- 启动服务
```
cd /tmp/hello-world

pyab
```






