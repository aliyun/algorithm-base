# 说明
这是一个AB框架的项目模板，除hadoop，hive，spark功能之外，都已在模板中启用。
  
# 项目目录结构
```
├── algorithms
├── config
│   └── config.py
│   └── config_dev.py
├── tests
│   ├── test_xxx.py
├── docker
│   ├── Dockerfile
├── setup
│   ├── requirements.txt
```

- `algorithms`: 算法入口放在此目录下，框架可以自动发现并导入。**注意：ab框架都会尝试import本文件夹下的所有一级文件，用不到的文件最好移动到其他文件夹或者二级目录下**
- `config`目录放项目配置
- `tests`放置测试用例
- `docker`放docker打包脚本
- `setup`放项目依赖相关脚本

# 构建镜像
```
sh build.sh
```

# 启动容器
```
docker run -it -v $PWD/logs:/root/app/logs -p <your-host-port>:80 --restart=always simple
```
