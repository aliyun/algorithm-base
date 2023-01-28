#!/bin/bash

set -x

check_result()
{
  echo input params:$1
  if [ $1 != 0 ]; then
     exit $1
  fi
}


abt_build()
{
  # 更新基础镜像
  docker pull cactusgame/ab-base:py37

  # 编译并指定docker的上下文
  if [ $use_cache = "false" ]; then
    docker build --no-cache -t $docker_full_name:$docker_version -f docker/Dockerfile ./
  else
    docker build -t $docker_full_name:$docker_version -f docker/Dockerfile ./
  fi
  if [ $? -ne 0 ]; then
    echo "Abt build failed"
    echo "1" > "/tmp/abt-slim.log"
    exit 1
  fi


  # 上传docker
  docker login --username=$docker_username $acr_address -p $docker_password
  docker tag $docker_full_name:$docker_version $docker_full_name:$docker_version
  docker push $docker_full_name:$docker_version
  if [ $? -ne 0 ]; then
    echo "push failed"
    echo "Please check whether the namespace exists in your ACR (note that the personal version of ACR can only have up to 3 namespaces"
    echo "1" > "/tmp/abt-slim.log"
    exit 1;
  fi

}


# 全局配置
if test -f ~/.abt/config ; then
  . ~/.abt/config

  if [ -n "$docker_registry_username" ]; then
    docker_username=$docker_registry_username
  fi

  if [ -n "$docker_registry_password" ]; then
    docker_password=$docker_registry_password
  fi

else
  echo " ~/.abt/config is necessary. Not found"
  exit 1
fi


# 项目配置
if test -f ./.ab ; then
  . ./.ab

  if [ -n "$app_name" ]; then
    docker_name=$app_name
  fi

  if [ -n "$app_version" ]; then
    docker_version=$app_version
  fi

  if [ -n "$acr_namespace" ]; then
    acr_namespace=$acr_namespace
  fi

  if [ -n "$acr_address" ]; then
      acr_address=$acr_address
  fi
else
  echo " ./ab is necessary. NOT found"

  exit 1
fi


if [ ! $docker_name ]; then
  echo "The app_name is None."
  exit 1
fi

if [ ! $docker_version ]; then
  echo "The app_version is None."
fi


# 获取命令行参数
use_cache=false
while getopts "c:" opt; do
    case "$opt" in
    c)  use_cache=$OPTARG
        ;;
    esac
done


docker_full_name=$acr_address/$acr_namespace/$docker_name
abt_build
