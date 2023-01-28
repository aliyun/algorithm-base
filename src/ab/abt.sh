#!/bin/bash
#set -x

abt_skiptest="false"
rm -rf "/tmp/abt.log_tmp"
abt_clean()
{
  container_id=$(docker ps -a -f "ancestor=$docker_full_name:$docker_version" -q)
  if [ -n "$container_id" ]; then
    echo "The container "$container_id" will be remove"
    docker rm -f $container_id
    if [ $? -ne 0 ]; then
      echo "Failed to delete the container"
      echo "Abt clean failed"
      exit 1
    else
      echo "The container "$container_id" has been remove"
    fi
  else
    echo "No container need to clean"
  fi

  rm -rf $(find . -name '*.o' -or -name '*.c') ./build ./setup.py
  echo "Abt clean succeeded"
}

abt_test()
{
  if [ $abt_command = "test" ] || [ $abt_skiptest = "false" ]; then
    pytest ./tests `pwd`
  fi
}

abt_build()
{
  if [ $abt_only_current_step = "false" ]; then
    abt_test
  fi

  # 更新基础镜像
  docker pull cactusgame/ab-base:py37
  rm -rf ./algorithms_tmp

  cp -r ./algorithms ./algorithms_tmp
  if [ $enable_license = "true" ]; then
    folder_name=./algorithms_tmp
    for file in ${folder_name}/*.py;
      do
        if [ $file = "./algorithms_tmp/__init__.py" ]; then
          continue
        fi
        echo "
from ab.decorate.warmup import warmup
from ab.decorate import when_ready_hooks


@warmup()
def start():
    from ab.utils import logger
    from ab.keys.crypto import license_verify
    from ab.plugins.prob import restart_handler
    try:
        license_verify(\"license.ab\")
    except Exception as e:
        logger.error(e)
        logger.set_level('FATAL')
        restart_handler()


@when_ready_hooks.when_ready()
def when_ready():
    from ab.keys.crypto import add_task
    add_task()

" >> $file
    break
    done
  fi

  # 编译并指定docker的上下文
  if [ $use_cache = "false" ]; then
    docker build --no-cache -t $docker_full_name:$docker_version -f docker/Dockerfile ./
  else
    docker build -t $docker_full_name:$docker_version -f docker/Dockerfile ./
  fi
  rm -rf ./algorithms_tmp
  if [ $? -ne 0 ]; then
    echo "Abt build failed"
    echo "1" > "/tmp/abt.log_tmp"
    exit 1
  fi
}

abt_push()
{
  if [ $abt_only_current_step = "false" ]; then
    abt_build
  fi

  # 上传docker
  docker login --username=$docker_username $acr_address -p $docker_password
  docker tag $docker_full_name:$docker_version $docker_full_name:$docker_version
  docker push $docker_full_name:$docker_version
  if [ $? -ne 0 ]; then
    echo "Abt push failed"
    echo "Please check whether the namespace exists in your ACR (note that the personal version of ACR can only have up to 3 namespaces"
    echo "1" > "/tmp/abt.log_tmp"
    exit 1;
  fi
}

# 从配置中读取设置信息
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
  echo "The .ab file was not found in the current directory."
  exit 1
fi


# 获取命令行参数
while getopts "n:v:s:c:o:u:p:i:l:" opt; do
    case "$opt" in
    n)  docker_name=$OPTARG
        ;;
    v)  docker_version=$OPTARG
        ;;
    s)  abt_skiptest=$OPTARG
        ;;
    i)  abt_command=$OPTARG
        ;;
    o)  abt_only_current_step=$OPTARG
        ;;
    u)  docker_username=$OPTARG
        ;;
    p)  docker_password=$OPTARG
        ;;
    c)  use_cache=$OPTARG
        ;;
    l)  enable_license=$OPTARG
        ;;
    esac
done

if [ ! $docker_name ]; then
  echo "The app_name is None."
  exit 1
fi

if [ ! $docker_version ]; then
  echo "The app_version is None."
fi

docker_full_name=$acr_address/$acr_namespace/$docker_name
abt_${abt_command}
