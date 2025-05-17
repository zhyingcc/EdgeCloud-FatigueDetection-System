#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

BASE_PATH=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
export PATH=${PATH}:${BASE_PATH}/SDKNAME/bin
export LD_LIBRARY_PATH=${BASE_PATH}/SDKNAME/lib

check_is_root()
{
    if [ $UID -ne 0 ];then
        echo "Please switch to root, the following op needs root user"
        exit -1
    fi
}

# 检查有没有库
check_env(){
    check_is_root
    enable_wifi

    if [ -f ~/.pip/pip.conf ]; then
        python3 -m pip install opencv-python
    else
        python3 -m pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    fi

    apt-get update && \
    apt-get install -y libatomic1 && \
    apt-get install -y build-essential && \
    apt-get install -y gdb && \
    apt-get install -y libcurl4 && \
    apt-get install -y libgl1 && \
    apt-get install -y curl && \
    apt-get install -y tofrodos && \
    apt-get install -y netplan.io
    
    ln -s /usr/bin/todos /usr/bin/unix2dos
    ln -s /usr/bin/fromdos /usr/bin/dos2unix

    # rk1808 cp npu_transfer_proxy, must in the last , it will return
    BASE_PATH=$(cd $(dirname $0);pwd)
    if [ ! -e /proc/device-tree/compatible ];then
        return
    fi
    IS_RK3399=`grep -c rk3399 /proc/device-tree/compatible 2> /dev/null`
    if [ "${IS_RK3399}" = "0" ];then
        # not rk3399
        return
    fi

    if [ -f ${BASE_PATH}/npu_transfer_proxy -a ! -f /usr/rk_bins/npu_transfer_proxy ];then
        mkdir /usr/rk_bins
        cp -rf ${BASE_PATH}/npu_transfer_proxy /usr/rk_bins/
        echo -n "cp npu_transfer_proxy, need reboot now (y/n)?"
        read answer
        if echo "$answer" | grep -iq "^y" ;then
            reboot
        fi
    fi
}

# 转为静态ip
fix_ip(){
    check_is_root
    rm -rf /etc/netplan/*
    echo "network:
            version: 2
            renderer: networkd
            ethernets:
              eth0:
                dhcp4: false
                addresses: [192.168.2.111/23]
                gateway4: 192.168.2.1
                optional: true
                nameservers:
                  addresses: [114.114.114.114,8.8.8.8]" >> /etc/netplan/config.yaml

    systemctl restart systemd-networkd
    netplan apply && \
    echo "to fixed ip successfully"
}

# 转为动态ip
dyn_ip(){
    check_is_root
    rm -rf /etc/netplan/*
    systemctl restart systemd-networkd
    netplan apply && \
    echo "to dynamic ip successfully"
}

# 删除默认路由
enable_wifi(){
    check_is_root
    def_route=$((route -n)| grep '0.0.0.0' | awk '{print $2}' | sed -n '1p')
    is_static=$((ip route)| grep 'default' | awk '{print $7}' | sed -n '1p')
    if [ "$is_static" = "dhcp" ];then
      ip route del default via ${def_route} dev eth0
    fi
}

printUsage() {
    echo "Usage:"
    echo "env_set.sh [-i] [-f] [-d] [-w]"
    echo "Description:"
    echo "-i,install necessary dependencies, if it is your first use, please run this option"
    echo "-f,turn to fix ip"
    echo "-d,turn to dynamic ip(dhcp)"
    echo "-w,if there is problem with wifi network, try this option"
}

if [ $# -eq 0 ];then
    printUsage
fi

while getopts :dfhiw opts;do
    case "$opts" in
        f)
            fix_ip
            ;;
        d)
            dyn_ip
            ;;
        i)
            check_env
            ;;
        w)
            enable_wifi
            ;;
        h)
            printUsage
            ;;
        ?)
            echo "invalid option -$OPTARG ignored!"
            printUsage
            ;;
    esac
done