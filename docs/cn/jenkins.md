# 通过jenkins构建镜像

## 目的

解决本地打包慢，大文件不能上传gitlab等问题。

## 原理

将大文件上传到OSS，解决大文件存储问题。同时，OSS支持版本控制，容器挂载等功能

## 步骤

- 从阿里云官网安装ossutil，并配置abt的[全局配置](abt.md)

- 在abt项目配置中，配置需要同步到OSS的`文件夹`。注意，只支持同步文件夹。详见[项目配置](abt.md)和simple项目下的`.ab`模板

- 使用如下命令同步本地文件到OSS

```
abt file upload
```

- 进入Jenkins（详见语雀文档），找到`ab-project-builder`进行构建。

## 风险

jenkins宿主机硬盘有限，硬盘容易不足。
