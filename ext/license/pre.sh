#!/bin/bash
set -x

# 免密登录所有服务器，最后处理本机
if test -f ./servers.conf ; then
  . ./servers.conf
else
  echo "no servers.conf found. "
fi






# License 预检工具
if test -f /etc/timezone ; then
  echo "valid /etc/timezone"
else
   echo "Asia/Shanghai" > /etc/timezone
fi

if test -f /etc/hostname; then
  echo "valid /etc/hostname"
else
   echo "abstub" > /etc/hostname
fi

if test -f /etc/locale.conf; then
  echo "valid /etc/locale.conf"
else
   echo "LANG=en_US.UTF-8" > /etc/locale.conf
fi


if test -f /etc/stub0; then
  echo "valid /etc/stub0"
else
   echo "0" > /etc/stub0
fi
if test -f /etc/stub1; then
  echo "valid /etc/stub1"
else
   echo "1" > /etc/stub1
fi
if test -f /etc/stub2; then
  echo "valid /etc/stub2"
else
   echo "2" > /etc/stub2
fi
if test -f /etc/stub3; then
  echo "valid /etc/stub3"
else
   echo "4" > /etc/stub3
fi

chmod 444 /etc/stub0
chmod 444 /etc/stub1
chmod 444 /etc/stub2
chmod 444 /etc/stub3

echo "---" > pre.output
ls -i /etc/stub0 | awk '{print $1}' >> pre.output
ls -i /etc/stub1 | awk '{print $1}' >> pre.output
ls -i /etc/stub2 | awk '{print $1}' >> pre.output
ls -i /etc/stub3 | awk '{print $1}' >> pre.output
ls -i /etc/timezone | awk '{print $1}' >> pre.output
ls -i /etc/hostname | awk '{print $1}' >> pre.output
ls -i /etc/locale.conf | awk '{print $1}' >> pre.output

# get hardware info
echo "---" >> pre.output
lscpu >> pre.output

echo "---" >> pre.output
ifconfig >> pre.output
