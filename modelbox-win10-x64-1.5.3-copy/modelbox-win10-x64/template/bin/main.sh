#!/bin/sh
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

# if HILENS_APP_NAME not set, it will be treated as mock

if [ "${HILENS_APP_NAME}" = "" ];then
  BASE_PATH=$(cd $(dirname $0);pwd)
  export HILENS_APP_ROOT=${BASE_PATH}/..
  export HILENS_DATA_DIR=${HILENS_APP_ROOT}/hilens_data_dir
  export HILENS_IS_SIMULATE="YES"
  export HILENS_MB_SDK_PATH=${HILENS_APP_ROOT}/../../SDKNAME
  if ! cmp -s ${HILENS_APP_ROOT}/dependence/modelbox_requirements.txt ${HILENS_APP_ROOT}/dependence/python/installed_modelbox_requirements.txt
  then
    sh ${HILENS_APP_ROOT}/build_project.sh
  fi
else
  export HILENS_MB_SDK_PATH=${HILENS_MB_SDK_ROOT}/sdk_SDKNAME
fi

export PATH=${HILENS_EMBED_PYTHON_PATH}:${HILENS_MB_SDK_PATH}/bin:${HILENS_APP_ROOT}/dependence/lib:${PATH}
export LD_LIBRARY_PATH=${HILENS_EMBED_PYTHON_PATH}:${HILENS_MB_SDK_PATH}/lib:${HILENS_APP_ROOT}/dependence/lib
export PYTHONHOME=
export PYTHONPATH=${HILENS_APP_ROOT}/dependence/python
export DISPLAY=:0.0

if [ -e /etc/os-release ]; then
  IS_DEBAIN=$(cat /etc/os-release | grep debian | awk '{print $1}')
  if [ ! -z "${IS_DEBAIN}" ]; then
    echo "debain os need load libgomp"
    preload_lib=/lib/aarch64-linux-gnu/libgomp.so.1
    if [ -e /lib/aarch64-linux-gnu/libmali-wayland.so.1 ];then
      preload_lib=/lib/aarch64-linux-gnu/libmali-wayland.so.1:${preload_lib}
    fi
    if [ -e /lib/aarch64-linux-gnu/libGLdispatch.so.0 ];then
      preload_lib=/lib/aarch64-linux-gnu/libGLdispatch.so.0:${preload_lib}
    fi
    export LD_PRELOAD=${preload_lib}:${LD_PRELOAD}
  fi
fi

if [ "$1" = "default" -o "$1" = "" ]; then
  export HILENS_GRAPH_TYPE=
else
  export HILENS_GRAPH_TYPE=_$1
fi

if [ "$2" = "" ]; then
  export HILENS_MB_LOG_LEVEL=WARN
else
  export HILENS_MB_LOG_LEVEL=$2
fi

modelbox-tool -verbose -log-level ${HILENS_MB_LOG_LEVEL} flow -run ${HILENS_APP_ROOT}/graph/MODULENAME${HILENS_MB_GRAPH_TYPE}.toml

if [ "${HILENS_IS_SIMULATE}" = "YES" ];then
  # delete cache when local-run, avoid cache not refresh
  rm -rf ${HILENS_APP_ROOT}/bin/modelbox-driver-info
  rm -rf ${HILENS_APP_ROOT}/modelbox-driver-info
fi
