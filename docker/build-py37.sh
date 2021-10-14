#!/bin/bash
set -x

# 打包docker
docker_name="ab-base"
docker_version="py37"

# ====== 需要定义的变量 =====
# 定义docker的名字，必须是小写英文字母
docker_full_name=registry.cn-hangzhou.aliyuncs.com/medical-pub/$docker_name
# ====== 需要定义的变量 END =====

# 编译并指定docker的上下文
docker build -t $docker_full_name:$docker_version -f ./Dockerfile ./

# 上传docker
docker tag $docker_full_name:$docker_version $docker_full_name:$docker_version
docker push $docker_full_name:$docker_version
