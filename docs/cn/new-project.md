# 如何创建新项目

## 自动创建

- 使用abt命令创建新项目
请注意，如果使用abt命令创建项目，ab框架必须使用"开发者模式"安装，即《安装》文档中的 `pip install -e .` 命令
```
abt project create -n your-project-name
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



# 启动服务

无论你使用`自动创建` 还是 `手动创建` 项目，都需要安装`setup/base.txt`中的依赖，然后便可以启动服务了。 

```
cd /tmp/hello-world

pyab
```






