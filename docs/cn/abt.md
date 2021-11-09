# ABT 使用示例

## 简易部署脚本使用方法(不支持license)

使用前提：按照`ABT 参考`章节，完成配置`全局配置`与`项目配置`。不用怕，事实上你需要改写的配置非常少。

在项目根目录下，执行如下命令，可以将项目打包，推送到镜像仓库。  

```
sh build.sh
```

如果希望提速docker构建，可以开启docker构建缓存。

```
sh build.sh -c=true
```


## abt工具命令展示
在运行以下示例命令前，请完成`ABT 参考`中的全局配置和项目配置,命令详见见下方参考

- 执行项目下的全部测试用例

```
abt test
```

- 执行项目下的全部测试用例, 并构建镜像

```
abt build
```

- 执行项目下的全部测试用例, 构建镜像，并把镜像推送到镜像仓库 

```
abt push
```

- 仅构建镜像

```
abt build -o=true
```

- 一键构建，部署应用到SAE

```
abt deploy
```

- 获得项目部署信息

```
abt get deploy
```

- 获得项目日志

```
abt get logs
```

- 根据项目配置，将本地文件批量同步到oss

```
abt file upload
```

- 根据项目配置，将oss文件批量下载到本地

```
abt file download
```

- 加密项目目录下的python文件

```
abt encrypt -i ".*" -e "config.*"
```

- 加密项目目录下的数据文件

```
abt crypto -i ".*" -e "config.*"
```


# ABT 参考

## 依赖

- 使用abt的file,logs命令，需要单独安装ossutil，请根据[oss文档](https://help.aliyun.com/document_detail/120075.html) 进行安装


## 全局配置文件（config）

- 放在~/.abt/config

```
[abt_config]
# [必填] 个人名称（内部用户使用域账号名），主要用于区分用户名
user=域账号名，需要区分用户

# [必填] 阿里云的ak，sk
ak=xxx
sk=xxx

# [必填] 镜像仓库的用户名，密码
docker_registry_username=xxx
docker_registry_password=xxx

# [必填] ossutil安装路径
ossutil=xxx

```

## 项目配置文件（meta）

- 放在项目的根目录下，命名为`.ab`

```
# [必填] 项目名称，镜像名称。
app_name=xxx

# [必填] 镜像版本，版本号的格式为 X.Y.Z(又称 Major.Minor.Patch)，X 表示主版本号，当 API 的兼容性变化时，X 需递增。Y 表示次版本号，当增加功能时(不影响 API 的兼容性)，Y 需递增。Z 表示修订号，当做 Bug 修复时(不影响 API 的兼容性)，Z 需递增。
app_version=0.0.1

# [必填] 你的镜像仓库endpoint
acr_address=registry.xxx.aliyuncs.com

# [必填] 你的镜像仓库namespace
acr_namespace=your-namespace

# [必填] 你的远端oss bukect名称。上传下载命令，会自动把指定的文件同步到这个bucket下。部署时，也会从这个bucket下自动挂载文件。
oss_bucket=xxx

# [必填] 部署serverless时用要用到的命名空间。输入不存在的命名空间，abt会帮你自动创建
sl_namespace=Default

# [必填] 在容器内部，应用的日志绝对路径
log_path=/root/app/logs

# [必填] 部署到SAE时的vpc，交换机，slb，安全组信息的id
vpc=vpc-xxxx
vsw=vsw-xxxx
slb=lb-xxxx
sg=sg-xxxx
slb_ip=your-slb-ip

# ================================================
# ================================================
# ============= 以下为选填内容 ======================
# ================================================
# ================================================

# 为什么没有配置oss的endpoint？因为我们用ossutil对oss操作，oss的endpoint需要配置到ossutil的config中。

# [选填] 你的应用所在的地域（region），这个值对应阿里云SAE服务的region，默认值: cn-hangzhou
sl_region_id=cn-hangzhou

# [选填] 部署的实例数。默认值：1, 最大10
sl_replicas=1

# [选填] 每个实例所需的CPU，单位为毫核，不能为0，默认值2000。目前仅支持以下固定规格：500，1000，2000，4000，8000
cpu=2000
# [选填]每个实例所需的内存，单位为MB，不能为0。与CPU为一一对应关系，目前仅支持以下固定规格：
# 1024：对应CPU为500毫核。
# 2048：对应CPU为500和1000毫核。
# 4096：对应CPU为1000和2000毫核。
# 8192：对应CPU为2000和4000毫核。
# 16384：对应CPU为4000和8000毫核。
memory=4096

# [选填] 容器和OSS文件挂载配置。使用该功能前，需要通过file命令将文件上传到oss上。
#  mountPath:容器内的绝对路径
#  bucketPath:OSS路径，(不包含bucket名称)
#  例：/root/app/config:abt/abtdemo/config/(最后的这个斜杠不能少) 将OSS中 abt/abtdemo/config 文件夹挂载到容器中的 /root/app/config
data[1]=/root/app/resource/mydata:simple/resource/mydata
data[2]=/root/app/resource/mydata2:simple/resource/mydata2

# [选填] 需要加密的数据文件列表,支持正则表达式
enable_crypto=false
crypto[0]=resource
crypto[1]=resource/.*data

# [选填] 需要加密的python文件, 你可以指定include和exclude的文件，支持正则表达式
enable_encrypt_python=true
encrypt_python_include[0]=.*
encrypt_python_exclude[0]=config/config.*.py
encrypt_python_exclude[1]=setup

# [选填]是否启用license功能
enable_license=false
```

---

## 命令

### ABT

```
abt [OPTIONS] COMMAND [ARGS]...
```

### 原则

- 配置优先级： abt命令传入的参数 > 项目配置文件 > 默认值（如果有的话），否则报错
- 支持类似maven的生命周期，即一个命令对应一个流水线，一个流水线内包含N个（N>=0)阶段，每个阶段按照顺序执行

## 子命令

### 清理

```
abt clean [OPTIONS]
```

#### clean

- 在本地环境中，停止并删除meta中配置的容器实例
- 删除操作：
- 删除项目目录下所有扩展名为.c, .o的所有文件
- 删除项目根目录下名为 `build`的目录及以下所有文件
- 删除项目根目录下名为setup.py的文件（仅删除这一个文件，不会递归删除）


### 部署（流水线）

```
abt test|build|push|deploy [OPTIONS]
```

**公共参数**

- -n, --name <NAME> 指定镜像的名字，默认从meta中获取
- -v, --version <VALUE> 指定镜像的版本号，默认从meta中获取
- -ns, --namespace <NAME> 指定部署时的命名空间（注意，不是镜像的命名空间）,默认从meta中获取
- -s, --skiptest <false|true> 默认false，是否跳过测试用例。
- -o, --only<false|true>默认false，是否只执行当前步骤。
- -c, --use-cache <false|true> 默认true。此参数决定docker build时是否使用docker cache机制。
- -f, --force <false|true> 默认false。如果设置为true，直接覆盖原有deploy，不进行提示

#### test

- 执行test目录下的全部测试用例

#### build

- 根据项目meta文件和dockerfile，构建docker镜像
- 目前根目录下的build.sh已经实现了相关功能

#### push

- 推送镜像至镜像仓库
- 目前根目录下的build.sh已经实现了相关功能

#### deploy

- 部署到serverless服务

### 获取信息

```
abt get [OPTIONS] COMMAND [ARGS]...
```

**公共参数**

- -n, --name <NAME> 指定镜像的名字，默认从meta中获取
- -ns, --namespace <NAME> 指定部署时SAE的命名空间,默认从meta中获取

#### deploy

- 从serverless服务中，获得相关部署的信息

#### logs

- 获得日志信息

参数：

- -f, --file-name <NAME> 查看指定oss文件的内容

### 文件

```
abt file [OPTIONS] COMMAND [ARGS]...
```

**公共参数**

#### upload

- 将meta中定义的全部文件上传至oss

#### download

- 同”部署“中的download，将meta中定义的全部文件从oss下载到本地

### python文件加密

```
abt encrypt [OPTIONS]
```

**公共参数**

- -i ,--include 支持正则表达式，包含需要加密的文件，默认值为所有python文件(.*)
- -e, --exclude 支持正则表达式，需要排除的文件。
- -c, --clear 是否删除源文件，默认为false

注意：

- 使用本命令时，需要在项目的根目录使用，项目的根目录必须是普通目录，而不能是python module(即不能包含__init___.py)


### 数据文件加密

```
abt crypto [OPTIONS]
```

**公共参数**

- -i ,--include 支持正则表达式，包含需要加密的文件，默认值为所有python文件(.*)
- -c, --clear 是否删除源文件，默认为false

注意：

- 本命令只支持加密，不支持解密，为了防止客户现场的攻击者使用解密命令。
