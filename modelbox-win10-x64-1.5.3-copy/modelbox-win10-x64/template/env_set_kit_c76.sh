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
set_to_develop_model(){
    check_is_root
    rm -rf /etc/usr/sftp_disable
    sed -i "s|Subsystem sftp internal-sftp|Subsystem sftp /usr/libexec/openssh/sftp-server|g" /etc/ssh/sshd_config
    sed -i "s/#PermitRootLogin yes/PermitRootLogin yes/g" /etc/ssh/sshd_config
    sed -i "s/#AllowTcpForwarding yes/AllowTcpForwarding yes/g" /etc/ssh/sshd_config
    sed -i  "s/export TMOUT=300/export TMOUT=0/g"  /etc/profile
    systemctl restart sshd
}

reset_to_default(){
    check_is_root
    touch /etc/usr/sftp_disable
    sed -i "s|Subsystem sftp /usr/libexec/openssh/sftp-server|Subsystem sftp internal-sftp|g" /etc/ssh/sshd_config
    sed -i "s/PermitRootLogin yes/#PermitRootLogin yes/g" /etc/ssh/sshd_config
    sed -i "s/AllowTcpForwarding yes/#AllowTcpForwarding yes/g" /etc/ssh/sshd_config
    sed -i  "s/export TMOUT=0/export TMOUT=300/g"  /etc/profile
    systemctl restart sshd
}

printUsage() {
    echo "Usage:"
    echo "env_set.sh [-i] [-u]"
    echo "Description:"
    echo "-i, install hilens framework c76 driver, change kit config to develop mode"
    echo "-u, reset kit config to default"
}

if [ $# -eq 0 ];then
    printUsage
fi

while getopts :dfhiw opts;do
    case "$opts" in
        i)
            set_to_develop_model
            ;;
        u)
            reset_to_default
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