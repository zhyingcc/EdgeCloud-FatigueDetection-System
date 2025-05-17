#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.


import os
import sys
import datetime
import platform
import glob


def get_sdk_path(base_path: str) -> str:
    for filename in os.listdir(base_path):
        file_path = os.path.join(base_path, filename)
        if (os.path.isdir(file_path) and filename.startswith("modelbox")):
            return file_path
    print("can not find sdk, exit")
    sys.exit(1)

__pythoncmd = 'python3'
__curpath = os.path.split(os.path.realpath(__file__))[0]
__sdk_path = get_sdk_path(os.path.dirname(
    os.path.dirname(os.path.dirname(__curpath))))
__python_install_path = os.path.join(__sdk_path, "python-install")
if not os.path.exists(__python_install_path):
    os.makedirs(__python_install_path)
sys.path.append(__python_install_path)

if platform.system().lower() == 'windows':
    __pythoncmd = 'python.exe'
    os.add_dll_directory(os.path.join(__sdk_path, "bin"))
try:
    import modelbox
except Exception as e:
    print(e)
    whl_path = glob.glob(__sdk_path + '/*.whl')[0]
    os.system(__pythoncmd + ' -m pip install pydevd --target=' + __python_install_path + ' --timeout=3 --retries=1')
    os.system(__pythoncmd + ' -m pip install ' + whl_path + ' --target=' + __python_install_path +
               ' --timeout=3 --retries=1')
    print('\n\nauto install modelbox and pydevd finish, please re-run it')
    sys.exit(0)

__log = modelbox.Log()

def log_level_str_to_level(level: str) -> modelbox.Log.Level:
    '''
    log level str to enum level
    '''
    if level == 'DEBUG':
        return modelbox.Log.Level.DEBUG
    elif level == 'INFO':
        return modelbox.Log.Level.INFO
    elif level == 'NOTICE':
        return modelbox.Log.Level.NOTICE
    elif level == 'WARN':
        return modelbox.Log.Level.WARN
    elif level == 'ERROR':
        return modelbox.Log.Level.ERROR
    elif level == 'FATAL':
        return modelbox.Log.Level.FATAL

    return modelbox.Log.Level.OFF


def log_level_to_str(level: modelbox.Log.Level) -> str:
    '''
    log level str to enum level
    '''
    if level == modelbox.Log.Level.DEBUG:
        return 'DEBUG'
    elif level == modelbox.Log.Level.INFO:
        return 'INFO'
    elif level == modelbox.Log.Level.NOTICE:
        return 'NOTICE'
    elif level == modelbox.Log.Level.WARN:
        return 'WARN'
    elif level == modelbox.Log.Level.ERROR:
        return 'ERROR'
    elif level == modelbox.Log.Level.FATAL:
        return 'FATAL'

    return "NONE"


def log_callback(level: modelbox.Log.Level, file: str, lineno: int, func: str, msg: str):
    '''
    Log callback function
    '''
    print("[{time}][{level:>5}][{file:>20}:{lineno:>4}] {msg}".format(
        time=datetime.datetime.now(), level=log_level_to_str(level),
        file=file, lineno=lineno, msg=msg
    ))


def reg_log():
    '''
    Register log function
    '''
    __log.reg(log_callback)
    __log.set_log_level(modelbox.Log.Level.INFO)


def set_log_level(level: modelbox.Log.Level):
    '''
    Set log level
    '''
    __log.set_log_level(level)


def run_flow(flow_file: str):
    '''
    Run modelbox flow
    '''
    try:
        with open(flow_file) as f:
            pass
    except IOError as e:
        print("Open file {} failed, {}".format(
            flow_file, os.strerror(e.errno)), file=sys.stderr)
        return 1

    # initialize flow
    flow = modelbox.Flow()
    ret = flow.init(flow_file)
    if ret == False:
        modelbox.error(ret)
        return 1

    # build graph
    ret = flow.build()
    if ret == False:
        modelbox.error(ret)
        return 1

    # run flow async
    ret = flow.run_async()
    if ret == False:
        modelbox.error(ret)
        return 1

    # get flow result
    retval = modelbox.Status()
    ret = flow.wait(0, retval)
    if ret == False:
        modelbox.error(ret)
        return 1
    modelbox.info("Running result: " + str(retval))
    return 0


if __name__ == '__main__':
    arg_len = len(sys.argv)
    if (arg_len < 2):
        print("need flow path")
        sys.exit(1)

    reg_log()
    set_log_level(log_level_str_to_level('INFO'))

    ret = run_flow(str(sys.argv[1]))
    sys.exit(ret)
