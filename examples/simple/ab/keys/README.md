
# 这个分支用于快速更新源码包中的.so文件

1. 在ab框架的src目录下编辑crypto.py 
2. 编辑完成，将crypto.py拷贝到本目录  
3. 编译mac环境的.so文件, 将.so 拷贝至src下。并删除生成的.c, setup.py等文件

```
abt encrypt -i crypto.py
```
4. 编译docker linux环境的.so  
4.1 在项目根目录下启动容器
```
docker run -it -v `pwd`:/root/app registry.cn-hangzhou.aliyuncs.com/medical-care/simple:0.0.2
```

4.2 进入容器，进行编译.so  

```
abt encrypt -i crypto.py
```

4.3 在关闭容器前，将so拷贝至框架的src下  

4.4 删除simple下其他生成文件。 
