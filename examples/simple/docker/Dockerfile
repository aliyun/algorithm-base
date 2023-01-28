FROM cactusgame/ab-base:py37

WORKDIR /root/app

# 安装算法依赖包
COPY ./setup/base.txt setup/base.txt
RUN pip3 install  --no-cache-dir -r setup/base.txt

COPY ./setup/requirements.txt setup/requirements.txt
RUN pip3 install  --no-cache-dir -r setup/requirements.txt

# 源代码等
COPY ./ ./

# 必须创建日志目录
RUN mkdir -p logs

# 加密python代码
RUN bash ./encrypt.sh

# 加密数据文件
RUN bash ./crypto.sh
# 加密结束后，删除加密密钥
RUN rm -rf ./crypto.sh

# 启动服务。本地调试时，可以覆盖启动命令
ENTRYPOINT ["/root/launch.sh"]
CMD ["prod"]

