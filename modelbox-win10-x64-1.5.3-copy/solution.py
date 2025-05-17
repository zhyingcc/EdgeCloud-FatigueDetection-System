#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import os
import json
import argparse
import zipfile
import shutil
import platform
import sys
import glob
import pathlib


def create_pip_conf():
    cfg_ext = 'conf'
    cfg_path = os.path.expanduser('~') + "/.pip/"
    if platform.system().lower() == 'windows':
        cfg_ext = 'ini'
        cfg_path = os.path.expanduser('~') + "/pip/"
    cfg_file = "pip." + cfg_ext
    if os.path.exists(cfg_path + cfg_file):
        return
    # 如果没有新建pip配置文件，如果有， 就用原来的
    pathlib.Path(cfg_path).mkdir(parents=True, exist_ok=True)
    with open(cfg_path + cfg_file, 'w') as f:
        f.write('[global]\n')
        f.write('index-url=https://pypi.tuna.tsinghua.edu.cn/simple\n')
        f.write('[install]\n')
        f.write('trusted-host=pypi.tuna.tsinghua.edu.cn\n')


def get_sdk_path(base_path: str) -> str:
    for filename in os.listdir(base_path):
        file_path = os.path.join(base_path, filename)
        if (os.path.isdir(file_path) and filename.startswith("modelbox")):
            return file_path
    print("can not find sdk, exit")
    sys.exit(1)


create_pip_conf()
g_curpath = os.path.split(os.path.realpath(__file__))[0]
g_sdk_path = get_sdk_path(g_curpath)
g_python_install_path = os.path.join(g_sdk_path, "python-install")
if not os.path.exists(g_python_install_path):
    os.makedirs(g_python_install_path)
sys.path.append(g_python_install_path)

g_pythoncmd = 'python3'
if platform.system().lower() == 'windows':
    g_pythoncmd = 'python.exe'

unzip_path = g_curpath + '/huaweicloud-obs-sdk-python/'
try:
    try:
        shutil.rmtree(unzip_path)
    except:
        pass
    from obs import ObsClient
except Exception as e:
    print(e)
    os.system(g_pythoncmd + ' -m pip install pycryptodome==3.10.1 --target=' +
              g_python_install_path + ' --timeout=3 --retries=1')
    zFile = zipfile.ZipFile(
        g_curpath + '/huaweicloud-obs-sdk-python_3.22.2.zip', "r")
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)
    zFile.extractall(unzip_path)

    os.chdir(unzip_path + '/src')
    os.system(g_pythoncmd + " setup.py install --prefix=" +
              g_python_install_path)
    try:
        obs_dirs = glob.glob(g_python_install_path +
                             "/lib/python*/site-packages/esdk_obs_python*/obs")
        if (len(obs_dirs) == 0):
            obs_dirs = glob.glob(g_python_install_path +
                                 "/lib/site-packages/esdk_obs_python*/obs")
        if (len(obs_dirs) == 0):
            obs_dirs = glob.glob(g_python_install_path +
                                 "/local/lib/python*/dist-packages/esdk_obs_python*/obs")
        shutil.move(obs_dirs[0], g_python_install_path)
    except Exception as e:
        print(e)
        # 如果上面失败了，那么就直接安装在系统python环境中，我的想法是尽可能减少对系统的影响
        os.system(g_pythoncmd + " setup.py install")
        pass
    try:
        shutil.rmtree(unzip_path)
    except:
        pass
    print('\n\nauto install obs finish, please re-run it')
    sys.exit(0)


class OBSUtils(object):
    def __init__(self):
        """初始化"""
        server = 'https://obs.cn-north-4.myhuaweicloud.com'
        # 如果需要用代理，使用这个方法, 切记，proxy_host不能有http开头 self.obsClient = ObsClient(server=server, proxy_host="xxx.xxx.com", proxy_port=8080, proxy_username="xxx", proxy_password="xxx")
        self.obsClient = ObsClient(server=server)

    def callback(self, transferredAmount, totalAmount, totalSeconds):
        # 获取下载平均速率(KB/S) , 获取下载进度百分比
        print('\r', "%.2fKB/S, percent=%.2f%%" % (transferredAmount * 1.0 /
              totalSeconds / 1024, transferredAmount * 100.0 / totalAmount), end='', flush=True)

    def download_obs_bucket_dir_to_local(self, bucket_name, object_path_list, target_dir):
        """下载obs上的文件/文件夹到本地"""
        if not bucket_name or not object_path_list:
            return None
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        objectKey = ''
        objectName = ''
        for i, obj_path in enumerate(object_path_list):
            objectKey += obj_path
            if (i != len(object_path_list) - 1):
                objectKey += '/'
            else:
                objectName = obj_path
        try:
            print('start download ' + objectKey)
            self.obsClient.getObject(
                bucket_name, objectKey, downloadPath=target_dir + '/' + objectName, progressCallback=self.callback)
            print('')
        except Exception as e:
            print("cannot download data from obs")
            print(e)
            sys.exit(0)


class Pipline:
    def __init__(self):
        self.solution_path = ""
        self.device_name = ""
        self.json_path = g_curpath + "/desc.json"
        self.solutions_list = None
        self.obs_utils = None
        self.sdk_name = ""

    def get_version(self, curpath=""):
        if not curpath:
            curpath = os.path.split(os.path.realpath(__file__))[0]
        vs_count = 0
        sdk_name = ""
        for filename in os.listdir(curpath):
            file_path = os.path.join(curpath, filename)
            if os.path.isdir(file_path) and filename.startswith("modelbox"):
                sdk_name = filename
                vs_count = vs_count + 1

        if vs_count == 1:
            ver_num = "1.0.0"
            try:
                with open(curpath + "/" + sdk_name + "/version") as f:
                    ver_num = f.readline().rstrip()
            except:
                pass
        elif vs_count == 0:
            print("err: there is no sdk")
        else:
            sdk_name = ""
            print(
                "err: too many sdk, please just leave one sdk (folder with modelbox*) here")
        self.sdk_name = sdk_name
        return sdk_name, curpath

    def get_solution_arch(self, sdk_name, curpath):
        self.solution_path = os.path.join(curpath, sdk_name, "solution")
        if not os.path.isdir(self.solution_path):
            os.makedirs(self.solution_path)
        device_name = ""
        sdk_name_list = sdk_name.split('-')
        if sdk_name == 'modelbox-rk-aarch64' or sdk_name == 'modelbox-rk3588-aarch64':
            is_rknn_device = False
            is_rk3588_device = False
            with open('/proc/device-tree/compatible', 'r') as f:
                for line in f:
                    if ("rk3399" in line):
                        is_rknn_device = True
                        break
                    if ("rk3588" in line):
                        is_rk3588_device = True
                        break
            if is_rk3588_device:
                device_name = "rk3588"
            elif (os.path.isfile("/usr/rk_bins/npu_transfer_proxy") or is_rknn_device):
                device_name = "rknpu"
            else:
                device_name = "rknpu2"
        elif len(sdk_name_list) >= 2:
            device_name = sdk_name_list[1]

        if device_name == "":
            print("error: current device not support " + device_name + " exit!")
            self.device_name = ""
            return None
        self.device_name = device_name

    def init_download_json_from_obs(self, object_key):
        self.obs_utils = OBSUtils()
        self.obs_utils.download_obs_bucket_dir_to_local(
            "modelbox-solutions", [object_key], g_curpath)

    def json_load(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            solution_list = data["solution_list"]
            self.solutions_list = []
            for d in solution_list:
                device_list = d["platform"]
                if self.device_name in device_list:
                    self.solutions_list.append(d["name"])

    def get_device_name(self):
        sdk_name, curpath = self.get_version()
        self.get_solution_arch(sdk_name, curpath)
        return None

    def unzip_package(self, package_path, solution_name):
        unzip_path_ = os.path.join(self.solution_path, solution_name)
        zFile = zipfile.ZipFile(package_path, "r")
        if not os.path.exists(unzip_path_):
            os.makedirs(unzip_path_)
        for fileM in zFile.namelist():
            zFile.extract(fileM, unzip_path_)
        zFile.close()

    def download_device_zips(self, solution_name):
        ls_ = [None, "desc.toml", "common.zip"]
        ls_[0] = self.device_name + ".zip"
        for i in ls_:
            self.obs_utils.download_obs_bucket_dir_to_local(
                "modelbox-solutions", [solution_name, i], self.solution_path)
        sys_zip_path_ = os.path.join(self.solution_path, ls_[0])
        self.unzip_package(sys_zip_path_, solution_name)
        self.unzip_package(os.path.join(
            self.solution_path, "common.zip"), solution_name)
        shutil.move(os.path.join(self.solution_path, "desc.toml"),
                    os.path.join(self.solution_path, solution_name, "desc.toml"))
        try:
            os.remove(sys_zip_path_)
            os.remove(os.path.join(self.solution_path, "common.zip"))
        except PermissionError:
            pass


def run():
    description = """
    Usage: Download ModelBox AI Solution zip.  (in windows, suggest using solution.bat)
NOTE : you must firstly use bellow command to enumerate all available AI solutions 
    `python solution.py -l`  or `solution.bat -l` in win10
secondly, specify a solution name after -s, for example 
    `python solution.py -s mask_det_yolo3` or `solution.bat -s mask_det_yolo3` in win10
NOTE: the first run will automatically install obs, please use root in the first run in linux 
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-s", "--solution-name", type=str,
                        help="specify a solution, do not set -l")
    parser.add_argument("-l", "--list", nargs="?", const=True,
                        type=bool, help="print all the solutions")
    args = parser.parse_args()
    if (not args.list and not args.solution_name):
        print(description)
        return None

    if platform.system().lower() == 'linux':
        # 解决wifi连接问题
        os.system(g_curpath + '/env_set.sh -w >/dev/null 2>&1')

    pipline = Pipline()
    pipline.get_device_name()
    pipline.init_download_json_from_obs('desc.json')
    pipline.json_load()
    if args.list:
        print("Solutions name:")
        for i in pipline.solutions_list:
            print(i, flush=True)
        return None
    if not args.solution_name:
        return None
    solution_name = args.solution_name

    find_sn = False
    for sn in pipline.solutions_list:
        if sn == solution_name:
            find_sn = True
            break

    if not find_sn:
        print("solution name invalid, valid solutions name:\n")
        for i in pipline.solutions_list:
            print(i, flush=True)
        return None
    pipline.download_device_zips(solution_name)
    print('success to download ' + solution_name)


if __name__ == '__main__':
    run()
