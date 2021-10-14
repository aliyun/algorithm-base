FROM registry.cn-hangzhou.aliyuncs.com/medical-care/python:3.7.10-buster
# FROM registry.cn-hangzhou.aliyuncs.com/medical-care/python:3.6.12-buster

ENV LANG C.UTF-8

WORKDIR /root/app

COPY ./sources.list /etc/apt/sources.list

# 安装系统包
RUN apt-get update \
    && apt-get install -y \
    curl \
    vim \
    iputils-ping \
    git \
    locales \
    logrotate \
    default-jdk \
    nginx \
    cron \
    && apt-get clean

# 设置系统时区为东8区
RUN set -eux; \
	sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen; \
	sed -i -e 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen; \
	locale-gen; \
	update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_MESSAGES=POSIX; \
	dpkg-reconfigure -f noninteractive locales; \
	\
	ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
	dpkg-reconfigure -f noninteractive tzdata;

# 设置pip使用阿里云镜像
COPY ./.pip.conf /root/.pip/pip.conf

# 设置lograte的配置
COPY ./gunicorn /etc/logrotate.d/gunicorn

# 启用lograte的定时任务
COPY ./gunicorn.cron /etc/cron.d/gunicorn.cron
COPY ./crond /etc/pam.d/crond

RUN echo "abcdefghi"

# 启动命令
COPY ./launch.sh /root/launch.sh

# python文件加密脚本
COPY ./encrypt.sh ./encrypt.sh

# 数据文件加密脚本
COPY ./crypto.sh ./crypto.sh

RUN chmod 0644 /etc/cron.d/gunicorn.cron
RUN chmod 777 /root/launch.sh
RUN crontab /etc/cron.d/gunicorn.cron
RUN touch /var/log/cron.log

# 拷贝nginx配置
COPY ./nginx_default.conf /etc/nginx/sites-available/default
COPY ./nginx.conf /etc/nginx/nginx.conf


