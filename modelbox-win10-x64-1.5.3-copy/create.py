#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import sys
import os
import getopt
import shutil
import pathlib
import subprocess
import platform
import json
import glob


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


def is_name_valid(name):
    name = name.replace('_', '')
    ok = name.isalnum()
    if (not ok):
        print(name + " not valid, only 0-9,a-z,A-z and _ is allowed", file=sys.stderr)
    return ok


def safe_rmfile(name):
    try:
        os.remove(name)
    except:
        pass


def safe_rmsome(name):
    try:
        files = glob.glob(name)
        for file in files:
            os.remove(file)
    except:
        pass


def sed_file(src, dst, module_name, sdk_name, editor_ip="127.0.0.1"):
    fin = open(src, 'r', encoding='utf-8')
    fout = open(dst, 'wb')
    ip_port = ""
    port_start = editor_ip.find(":")
    if (port_start >= 0):
        ip_port = editor_ip[port_start + 1::]
        editor_ip = editor_ip[0:port_start:]

    for line in fin:
        line = line.replace('\r', '')
        line = line.replace('MODULENAME', module_name)
        line = line.replace('SDKNAME', sdk_name)
        line = line.replace('EDITOR_IP', editor_ip)
        if (ip_port != "" and line.startswith("port")):
            line = line.replace('1104', ip_port)
        fout.write(line.encode('utf-8'))

    fin.close()
    fout.close()


def add_inout_port(src, json_cfg, device, module_name):
    retstr = ''
    cfg = None
    try:
        cfg = json.loads(json_cfg)
        if (cfg["desc"] == ""):
            cfg["desc"] = "description"

        fin = open(src, 'r', encoding='utf-8')
        for line in fin:
            line = line.replace('\r', '')
            line = line.replace('MODULENAME', module_name)
            line = line.replace('description = "description"',
                                'description = "' + cfg["desc"] + '"')
            if (line.startswith("# Input ports description")):
                break
            retstr += line

        fin.close()
        retstr += "# Input ports description\n[input]\n"
        index = 1
        for input in cfg["input"]:
            retstr += "[input.input" + \
                str(index) + \
                "] # Input port number, the format is input.input[N]\n"
            retstr += 'name = "' + input["name"] + '" # Input port name\n'
            type_str = "uint8"
            if ("type" in input):
                type_str = input["type"]
            retstr += 'type = "' + type_str + '"  # input port data type ,e.g. float or uint8\n'
            real_device = device
            if (input["device"] == "cpu"):
                real_device = "cpu"
            retstr += 'device = "' + \
                str(real_device) + '"  # input buffer type\n'
            index += 1

        if (not "output" in cfg):
            return retstr, cfg
        retstr += "\n# Output ports description\n[output]\n"
        index = 1
        for output in cfg["output"]:
            retstr += "[output.output" + \
                str(index) + \
                "] # Output port number, the format is output.output[N]\n"
            retstr += 'name = "' + output["name"] + '" # Output port name\n'
            type_str = "float"
            if ("type" in output):
                type_str = output["type"]
            retstr += 'type = "' + type_str + \
                '"  # output port data type ,e.g. float or uint8\n'
            index += 1

    except Exception as e:
        print("create flowunit error: ", file=sys.stderr)
        print(e, file=sys.stderr)
        retstr = ''
    return retstr, cfg


def copy_sdk_win(src, dst):
    shutil.copytree(src+"/bin", dst+"/bin", symlinks=True)
    shutil.copytree(src+"/flowunit", dst+"/flowunit", symlinks=True)


def copy_sdk_linux(src, dst):
    shutil.copytree(src+"/bin", dst+"/bin", symlinks=True)
    shutil.copytree(src+"/flowunit", dst+"/flowunit", symlinks=True)
    pathlib.Path(dst + "/lib").mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(src+"/lib"):
        if (not os.path.isdir(os.path.join(src+"/lib", filename))) and ".so" in filename:
            shutil.copyfile(src + "/lib/" + filename, dst +
                            "/lib/" + filename, follow_symlinks=False)


def get_device(sdk_name):
    if sdk_name.startswith('modelbox-rk'):
        return 'rknpu'
    elif sdk_name.startswith('modelbox-sdc'):
        return 'sdc'
    elif sdk_name.startswith('modelbox-kit'):
        return 'kit'
    return 'cpu'


def get_osext(sdk_name):
    if sdk_name.startswith('modelbox-win10'):
        return '.bat'
    return '.sh'


def get_cplus_tool(cfg, linux_proj_path, linux_sdk_path, extstr, toml_path):
    cfg["program"] = linux_sdk_path + "/bin/modelbox-tool" + extstr
    cfg["args"] = ["-verbose", "-log-level", "INFO", "flow", "-run"]
    cfg["args"].append(toml_path.replace('\\', '/'))
    return cfg


def get_cplus_server(cfg, linux_proj_path, linux_sdk_path, extstr, toml_path):
    cfg["program"] = linux_sdk_path + "/bin/modelbox" + extstr
    if platform.system().lower() == 'windows':
        cfg["args"] = ["-c"]
        cfg["args"].append(linux_proj_path + "/graph/modelbox.conf")
    else:
        cfg["args"] = ["-f", "-V", "-c"]
        cfg["args"].append(linux_proj_path + "/graph/modelbox.conf")
        cfg["args"].append("-p")
        cfg["args"].append(linux_proj_path +
                           "/hilens_data_dir/hilens_modelbox_server_debug.pid")
    return cfg


def new_debug_json(proj_path, sdk_path, prj_type):
    if not os.path.exists(proj_path):
        return
    proj_path = proj_path.replace('\\', '/')
    sdk_path = sdk_path.replace('\\', '/')
    if (prj_type == ''):
        if (os.path.exists(proj_path + "/graph/modelbox.conf")):
            prj_type = 'server'
        else:
            prj_type = 'project'
    vscode_path = proj_path + "/.vscode"
    if not os.path.exists(vscode_path):
        os.makedirs(vscode_path)
    linux_proj_path = proj_path.replace('\\', '/')
    linux_sdk_path = sdk_path.replace('\\', '/')
    extstr = ''
    pathstr = "PATH"
    pathsplit = ":"
    if platform.system().lower() == 'windows':
        extstr = '.exe'
        pathstr = "Path"
        pathsplit = ";"
    env_json_fix = {"MODELBOX_DEBUG_PYTHON": "yes",
                    pathstr: linux_sdk_path+"/../python-embed" + pathsplit +
                    linux_sdk_path+"/bin" + pathsplit + linux_sdk_path +
                    "/dependence/lib" + pathsplit + "${env:" + pathstr + "}",
                    "HILENS_APP_ROOT": linux_proj_path,
                    "HILENS_DATA_DIR": linux_proj_path + "/hilens_data_dir",
                    "HILENS_MB_SDK_PATH": linux_sdk_path,
                    "PYTHONPATH": linux_proj_path + "/dependence/python",
                    "HILENS_MB_LOG_LEVEL": "INFO"}
    if platform.system().lower() == 'linux':
        env_json_fix["LD_LIBRARY_PATH"] = linux_sdk_path + \
            "/lib:" + linux_proj_path + "/dependence/lib"
        if ("rk-aarch64" in sdk_path):
            env_json_fix[
                "LD_PRELOAD"] = "/lib/aarch64-linux-gnu/libgomp.so.1:/lib/aarch64-linux-gnu/libGLdispatch.so.0:${env:LD_PRELOAD}"
        if ("rk3588-aarch64" in sdk_path):
            env_json_fix[
                "LD_PRELOAD"] = "/lib/aarch64-linux-gnu/libgomp.so.1:/lib/aarch64-linux-gnu/libmali-wayland.so.1:/lib/aarch64-linux-gnu/libGLdispatch.so.0:${env:LD_PRELOAD}"

    dgj = {"version": "0.2.0", 'configurations': []}
    for tomlname in os.listdir(os.path.join(proj_path, 'graph')):
        if not tomlname.endswith(".toml"):
            continue
        proj_base = os.path.basename(proj_path)
        if not tomlname.startswith(proj_base):
            continue
        env_json = env_json_fix.copy()
        tomlname_0 = tomlname.split(".")[0]
        if (not tomlname_0 == proj_base):
            env_json["HILENS_MB_GRAPH_TYPE"] = tomlname_0[len(proj_base):]
        cfg = {'name': "Python: " + tomlname_0, "type": "python", "request": "launch",
               "program": proj_path + "/bin/python_debug.py", "console": "integratedTerminal",
               "justMyCode": False,
               "cwd": linux_proj_path + "/bin",
               "args": [linux_proj_path + "/graph/" + tomlname],
               "env": env_json
               }
        if platform.system().lower() == 'windows':
            cfg["pythonPath"] = sdk_path + "/../python-embed/python.exe"
        dgj['configurations'].append(cfg)

        env_json_cplus = []
        for key in env_json:
            if (not key == 'MODELBOX_DEBUG_PYTHON'):
                env_json_cplus.append({"name": key, "value": env_json[key]})
        iva_str = "{\"algorithm\":{\"multiTask\":\"no\",\"algType\":\"mock\"},\"mockFile\":\"" + linux_proj_path + \
            "/bin/mock_task.toml\",\"svcInstanceId\":\"modelbox-instance-mock\",\"isv\":{\"auth\":{\"id\":\"test\"}}}"
        env_json_cplus.append({"name": "IVA_SVC_CONFIG", "value": iva_str})

        # windows版本目前c++调试会崩溃，原因不明，或许是符号冲突导致 Status的
        if platform.system().lower() == 'windows':
            continue

        cfg = {'name': "C++: " + tomlname_0, "type": "cppdbg", "request": "launch",
               "justMyCode": False,
               "stopAtEntry": False,
               "externalConsole": False,
               "MIMode": "gdb",
               "miDebuggerPath": "gdb" + extstr,
               "cwd": linux_proj_path + "/bin",
               "setupCommands": [
                   {
                       "description": "为 gdb 启用整齐打印",
                       "text": "-enable-pretty-printing",
                       "ignoreFailures": True
                   }
               ],
               "args": [],
               "environment": env_json_cplus
               }
        if prj_type == 'server':
            cfg = get_cplus_server(
                cfg, linux_proj_path, linux_sdk_path, extstr, proj_path+'/graph/' + tomlname)
        else:
            cfg = get_cplus_tool(
                cfg, linux_proj_path, linux_sdk_path, extstr, proj_path+'/graph/' + tomlname)
        dgj['configurations'].append(cfg)
    # final write file
    with open(vscode_path+"/launch.json", 'w', encoding='utf-8') as fw:
        json.dump(dgj, fw, indent=2, ensure_ascii=False)


def check_path(curpath, proj_name):
    if (proj_name == ""):
        print(
            "error: project name is null", file=sys.stderr)
        return "", ""
    workspace_path = os.path.join(curpath, "workspace")
    proj_path = os.path.join(workspace_path, proj_name)
    if (not os.path.exists(proj_path)):
        print("error: project:" + proj_name + " is not exist", file=sys.stderr)
        return "", ""
    return workspace_path, proj_path


def get_solution_arch(vs_string, solution_name, curpath):
    sdk_solution_path = curpath + "/" + vs_string + "/solution/" + solution_name
    device_name = ""
    vs_string_list = vs_string.split('-')
    if vs_string == 'modelbox-rk-aarch64' or vs_string == 'modelbox-rk3588-aarch64':
        option_name = "rknpu2"
        is_rknn_device = False
        with open('/proc/device-tree/compatible', 'r') as f:
            for line in f:
                if ("rk3399" in line):
                    is_rknn_device = True
                    break
        if (os.path.isfile("/usr/rk_bins/npu_transfer_proxy") or is_rknn_device):
            device_name = "rknpu"
        else:
            device_name = "rknpu2"
            option_name = "rknpu"
        if (not os.path.exists(sdk_solution_path + "/" + device_name)):
            print("warning: please change all infer toml to use " +
                  option_name + ", since solution not match!")
            device_name = option_name
    elif len(vs_string_list) >= 2:
        device_name = vs_string_list[1]

    if device_name == "":
        print("error: current device not support " +
              solution_name + " exit!", file=sys.stderr)
        return ""
    return sdk_solution_path + "/" + device_name


def solution_copy_common(sdk_solution_root, sdk_solution_path, cur_solution_path):
    if not os.path.isdir(sdk_solution_path + "/../common"):
        return
    if platform.system().lower() == 'windows':
        cmd_xcopy = "xcopy " + sdk_solution_path + \
            "/../common/* " + cur_solution_path + "/ "
        os.system(cmd_xcopy.replace('/', '\\') + "/S /E /Y /Q")
    else:
        os.system("cp -rf " + sdk_solution_path +
                  "/../common/* " + cur_solution_path + "/  >/dev/null 2>&1")


def import_solution(curpath, module_name, vs_string, solution_name, workspace_path, prj_type, wk_name):
    sdk_solution_path = get_solution_arch(vs_string, solution_name, curpath)
    proj_path = curpath + "/" + wk_name + "/" + module_name
    if (sdk_solution_path == ""):
        return False
    if (not os.path.exists(sdk_solution_path)):
        print("error: solution:" + solution_name +
              " is not exist", file=sys.stderr)
        shutil.rmtree(proj_path)
        return False
    if platform.system().lower() == 'windows':
        cmd_xcopy = "xcopy " + sdk_solution_path + "/* " + proj_path + "/ "
        cmd_del = "del " + proj_path + "/graph/" + solution_name + "* "
        os.system(cmd_xcopy.replace('/', '\\') + "/S /E /Y /Q")
        os.system(cmd_del.replace('/', '\\') + "/Q")
    else:
        os.system("cp -rf " + sdk_solution_path +
                  "/* " + proj_path + "/  >/dev/null 2>&1")
        os.system("rm -rf " + proj_path + "/graph/" +
                  solution_name + "* >/dev/null 2>&1")
    for graph_file in os.listdir(sdk_solution_path + "/graph"):
        file_ext = os.path.splitext(graph_file)[-1]
        if (file_ext != ".toml"):
            continue
        file_name = os.path.splitext(graph_file)[0]
        file_name_ext = file_name[len(solution_name):len(file_name)]
        dst_name = proj_path + "/graph/" + module_name + file_name_ext + ".toml"
        sed_file(sdk_solution_path + "/graph/" + graph_file,
                 dst_name, module_name, vs_string)

    solution_copy_common(curpath + "/" + vs_string +
                         "/solution/", sdk_solution_path, proj_path)
    return True


def get_git_path(curpath):
    git_bash_path = ''
    try:
        with open(curpath + "/git_bash_path.txt", 'r', encoding='utf-8') as f:
            git_bash_path = f.readline().strip()
        if (os.path.exists(git_bash_path)):
            return os.path.dirname(git_bash_path)
    except:
        pass

    path_strs = os.environ["PATH"].split(';')
    for each in path_strs:
        git_path = os.path.join(each, "git.exe")
        if (not os.path.exists(git_path)):
            continue
        git_bash_path1 = os.path.join(os.path.dirname(each), "git-bash.exe")
        git_bash_path2 = os.path.join(os.path.dirname(
            os.path.dirname(each)), "git-bash.exe")
        if (not os.path.exists(git_bash_path1) and not os.path.exists(git_bash_path2)):
            continue
        if os.path.exists(git_bash_path1):
            git_bash_path = git_bash_path1
        else:
            git_bash_path = git_bash_path2
        with open(curpath + "/git_bash_path.txt", 'wb') as f:
            f.write(git_bash_path.encode('utf-8'))
        return os.path.dirname(git_bash_path)

    return ""


def dos2_unix(root_path, sed_cmd):
    for root, dirs, files in os.walk(root_path):
        for name in files:
            if name.endswith(".toml") or name.endswith(".conf") or name.endswith(".ini"):
                os.system(sed_cmd + os.path.join(root, name))


def create_project(curpath, module_name, vs_string, solution_name, prj_type, wk_name="workspace"):
    if (not is_name_valid(module_name)):
        return False, ""
    workspace_path = os.path.join(curpath, wk_name)
    sdk_path = os.path.join(curpath, vs_string)
    proj_path = os.path.join(workspace_path, module_name)
    if (os.path.exists(proj_path)):
        print(module_name +
              " is exist, can not crate project with the same name", file=sys.stderr)
        return False, ""
    pathlib.Path(workspace_path).mkdir(parents=True, exist_ok=True)
    shutil.copytree(sdk_path+"/template/project", proj_path)
    pathlib.Path(
        proj_path + "/etc/flowunit/cpp").mkdir(parents=True, exist_ok=True)

    os_type = 'linux'
    sed_cmd = 'sed -i "s/\r//g" '
    if platform.system().lower() == 'windows':
        os_type = 'win10'
        cmd_pre = get_git_path(curpath)
        if (cmd_pre == ""):
            print("can not find git-bash.exe", file=sys.stderr)
            return False, proj_path
        sed_cmd = '"' + cmd_pre + '/usr/bin/dos2unix.exe" '

    if (solution_name == ""):
        src_path = sdk_path + "/template/project/graph/example.toml"
        dst_path = proj_path + "/graph/" + module_name + ".toml"
        sed_file(src_path, dst_path, module_name, vs_string)

    sed_file(sdk_path + "/template/project/CMakeLists.txt",
             proj_path + "/CMakeLists.txt", module_name, vs_string)
    if (module_name != "example"):
        safe_rmfile(proj_path + "/graph/example.toml")

    pathlib.Path(proj_path + "/model").mkdir(parents=True, exist_ok=True)
    pathlib.Path(proj_path + "/data").mkdir(parents=True, exist_ok=True)
    # 创建run的脚本
    pathlib.Path(proj_path + "/bin").mkdir(parents=True, exist_ok=True)
    bin_path = ""
    if (prj_type == "server"):
        bin_path = "_server"
        sed_file(sdk_path + "/template/bin_server/modelbox_" + os_type + ".conf",
                 proj_path + "/graph/modelbox.conf", module_name, vs_string)
        sed_file(sdk_path + "/template/bin_server/mock_task.toml",
                 proj_path + "/bin/mock_task.toml", module_name, vs_string)

    sed_file(sdk_path + "/template/bin" + bin_path + "/main" + get_osext(vs_string),
             proj_path + "/bin/main" + get_osext(vs_string), module_name, vs_string)
    shutil.copyfile(sdk_path + "/template/bin" + bin_path + "/python_debug.py", proj_path +
                    "/bin/python_debug.py", follow_symlinks=False)
    # 创建空的python安装rt
    pathlib.Path(proj_path + "/dependence").mkdir(parents=True, exist_ok=True)
    pathlib.Path(
        proj_path + "/dependence/python").mkdir(parents=True, exist_ok=True)
    pathlib.Path(
        proj_path + "/dependence/python/installed_modelbox_requirements.txt").touch()

    ret = True
    if (solution_name != ""):
        ret = import_solution(curpath, module_name, vs_string,
                              solution_name, workspace_path, prj_type, wk_name)
    if (ret):
        new_debug_json(proj_path, sdk_path, prj_type)
        create_pip_conf()
        if platform.system().lower() != 'windows':
            os.system("chmod +x " + proj_path + "/bin/main.sh")
        dos2_unix(proj_path + "/graph", sed_cmd)
        dos2_unix(proj_path + "/etc", sed_cmd)
        dos2_unix(proj_path + "/model", sed_cmd)
        dos2_unix(proj_path + "/bin", sed_cmd)
        files = glob.glob(proj_path + "/dependence/wheel/*.whl")
        if (len(files) > 0):
            with open(proj_path + "/dependence/python/installed_modelbox_requirements.txt", 'wb') as f:
                f.write("initial_wheel_installation".encode('utf-8'))
        print("success: create " + module_name + " in " + workspace_path)

    return ret, proj_path


def create_cplusplus(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    cplusplus_path = proj_path + "/flowunit_cpp/" + module_name
    if (os.path.exists(cplusplus_path)):
        print("error: " + module_name +
              " is exist, can not crate c++ with the same name", file=sys.stderr)
        return False, ""
    pathlib.Path(cplusplus_path).mkdir(parents=True, exist_ok=True)
    sed_file(sdk_path+"/template/flowunit/c++/CMakeLists.txt",
             cplusplus_path+"/CMakeLists.txt", module_name, vs_string)
    sed_file(sdk_path+"/template/flowunit/c++/example.cc",
             cplusplus_path+"/"+module_name+".cc", module_name, vs_string)
    sed_file(sdk_path+"/template/flowunit/c++/example.h",
             cplusplus_path+"/"+module_name+".h", module_name, vs_string)

    print("success: create c++ " + module_name + " in " + cplusplus_path)
    return True, cplusplus_path


def create_python(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    python_path = proj_path + "/etc/flowunit/" + module_name
    if (os.path.exists(python_path)):
        print("error: " + module_name +
              " is exist, can not crate python with the same name", file=sys.stderr)
        return False, ""
    pathlib.Path(python_path).mkdir(parents=True, exist_ok=True)
    src_path = sdk_path + "/template/flowunit/python/"
    sed_file(src_path+"example.py",
             python_path+"/"+module_name+".py", module_name, vs_string)
    if (cfg_json == ""):
        sed_file(src_path+"example.toml",
                 python_path+"/"+module_name+".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(
            src_path+"example.toml", cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, python_path
        retstr = retstr.replace('group_type = "generic"',
                                'group_type = "' + cfg["group-type"] + '"')
        if ("type" in cfg):
            retstr = retstr.replace(
                cfg["type"] + " = false", cfg["type"] + " = true")
        with open(python_path+"/"+module_name+".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create python " + module_name + " in " + python_path)
    return True, python_path


def create_infer(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    infer_path = proj_path + "/model/" + module_name
    if (os.path.exists(infer_path)):
        print("error: " + module_name +
              " is exist, can not crate python with the same name", file=sys.stderr)
        return False, ""
    pathlib.Path(infer_path).mkdir(parents=True, exist_ok=True)
    src_file = sdk_path+"/template/flowunit/infer/example_" + \
        get_device(vs_string) + ".toml"
    if (cfg_json == ""):
        sed_file(src_file, infer_path + "/" + module_name +
                 ".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(
            src_file, cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, infer_path
        if (cfg["model"] != ""):
            retstr = retstr.replace(
                './model', './' + os.path.splitext(cfg["model"])[0])
        with open(infer_path + "/" + module_name + ".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create infer " + module_name + " in " + infer_path)
    return True, infer_path


def create_yolo(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    yolo_path = proj_path + "/etc/flowunit/" + module_name
    if (os.path.exists(yolo_path)):
        print("error: " + module_name +
              " is exist, can not crate yolo with the same name", file=sys.stderr)
        return False, ""
    pathlib.Path(yolo_path).mkdir(parents=True, exist_ok=True)
    src_file = sdk_path+"/template/flowunit/yolo/example.toml"
    if (cfg_json == ""):
        sed_file(src_file, yolo_path+"/"+module_name +
                 ".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(
            src_file, cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, yolo_path
        if ("virtual-type" in cfg):
            retstr = retstr.replace('yolov3_postprocess', cfg["virtual-type"])
        with open(yolo_path+"/"+module_name+".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create yolo " + module_name + " in " + yolo_path)
    return True, yolo_path


def encrypt_model(rpm_path, sdk_path, model_key):
    sdk_path = sdk_path.replace("\\", "/").strip()
    rpm_path = rpm_path.replace("\\", "/").strip()
    encrypt_list = rpm_path + "/../encrypt_list.txt"
    model_list = []
    f_en_list = open(encrypt_list, 'w')

    if (os.path.exists(rpm_path + "/dependence/env_verify.json")):
        f_en_list.write(rpm_path + "/dependence/env_verify.json")

    for model_dir in os.listdir(rpm_path + "/model"):
        toml_file = rpm_path + "/model/" + model_dir + "/" + model_dir + ".toml"
        if (not os.path.exists(toml_file)):
            print("error: " + model_dir + " has no " +
                  model_dir + ".toml", file=sys.stderr)
            return False
        # get modelfile name, do not use toml, for install is needed
        modefile = ''
        with open(toml_file, 'r') as fin, open(toml_file+".tmp", 'wb') as fout:
            for read_line in fin.readlines():
                line = read_line.replace(' ', '')
                if line.startswith('entry='):
                    start_pos = line.find('"')
                    if (start_pos < 0):
                        print("error: " + toml_file +
                              " has no entry", file=sys.stderr)
                        return False
                    start_pos += 1
                    end_pos = line.find('"', start_pos)
                    if (end_pos < 0):
                        print("error: " + toml_file +
                              " has no entry", file=sys.stderr)
                        return False
                    modefile = line[start_pos:end_pos]
                    model_list.append(model_dir)
                    modepath = rpm_path + "/model/" + model_dir + "/" + modefile
                    if (not os.path.exists(modepath)):
                        print("error: " + modepath + " not exist in " +
                              toml_file, file=sys.stderr)
                        return False
                    fout.write(read_line.replace(
                        modefile, modefile + ".en").encode('utf-8'))
                    f_en_list.write(modepath.replace("\\", "/").strip())
                else:
                    fout.write(read_line.encode('utf-8'))
        safe_rmfile(toml_file)
        os.rename(toml_file+".tmp", toml_file)

    # start to call modelbox-tool to encrypt
    f_en_list.close()
    if (len(model_list) == 0):
        print("warning: can not find model, skip model encrypt")
        return True
    output = subprocess.Popen(["modelbox-tool.exe", "key", "-model", encrypt_list, "S-n"], env={
        "LD_LIBRARY_PATH": sdk_path + "/lib", "Path": sdk_path + "/bin", "MODELBOX_PASSWORD": model_key},
        stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, bufsize=-1).communicate()
    output_result = ''
    output_err = ''
    try:
        output_result = output[0].decode('gb2312')
    except:
        output_result = output[0].decode('utf-8')
    try:
        output_err = output[1].decode('gb2312')
    except:
        output_err = output[1].decode('utf-8')

    if not "Key:" in output_result:
        print("error: model encryp failed " + output_err, file=sys.stderr)
        return False
    with open(rpm_path + "/../model_keyfile.txt", 'w') as keyf, open(encrypt_list, 'r') as flist:
        keyf.write(output_result)
        for read_line in flist.readlines():
            safe_rmfile(read_line.strip())
    # modify graph, add modeldecryption=true
    graph_name_list = []
    for graph_name in os.listdir(rpm_path + "/graph"):
        if not ".toml" in graph_name:
            continue
        graph_name_list.append(graph_name)
        gp = rpm_path + "/graph/" + graph_name
        with open(gp, 'r', encoding='utf-8') as gfr, open(gp + ".en", 'wb') as gw:
            for read_line in gfr.readlines():
                line = read_line.replace(" ", "")
                findms = ''
                for ms in model_list:
                    if ("flowunit=" + ms) in line:
                        findms = ms
                        break
                if len(findms) > 0:
                    read_line = read_line.replace(
                        findms, findms + ", modeldecryption=true")
                gw.write(read_line.encode('utf-8'))
        safe_rmfile(gp)
        os.rename(gp + ".en", gp)
    # clean
    safe_rmfile(encrypt_list)
    print("ModelKey has been written in model_keyfile.txt in project path")
    return True


def create_rpm(proj_path, module_name, vs_string, model_key):
    if (not os.path.exists(proj_path)):
        print("error: no " + module_name, file=sys.stderr)
        return
    if (not os.path.exists(proj_path + "/hilens_data_dir")):
        print("error: please firstly call your_prj/build_project.sh", file=sys.stderr)
        return

    try:
        shutil.rmtree(proj_path + "/rpm")
    except:
        pass

    if (os.path.exists(proj_path + "/rpm")):
        print("error: rpm folder in project path delete fail!", file=sys.stderr)
        return
    pathlib.Path(proj_path + "/rpm").mkdir(parents=True, exist_ok=True)
    shutil.copytree(proj_path+"/bin", proj_path + "/rpm/bin", symlinks=True)
    try:
        safe_rmfile(proj_path + "/rpm/bin/modelbox-driver-info")
        safe_rmfile(proj_path + "/rpm/modelbox-driver-info")
        safe_rmsome(proj_path + "/rpm/bin/mock_task*.toml")
        safe_rmfile(proj_path + "/rpm/bin/python_debug.py")
    except:
        pass
    # cp embeded python
    if (os.path.exists(proj_path + "/../../python-embed")):
        shutil.copytree(proj_path+"/../../python-embed",
                        proj_path + "/rpm/python-embed", symlinks=True)
    shutil.copytree(proj_path+"/etc", proj_path + "/rpm/etc", symlinks=True)
    shutil.copytree(proj_path+"/graph", proj_path +
                    "/rpm/graph", symlinks=True)
    shutil.copytree(proj_path+"/dependence", proj_path +
                    "/rpm/dependence", symlinks=True)
    if (os.path.exists(proj_path + "/model")):
        shutil.copytree(proj_path+"/model", proj_path +
                        "/rpm/model", symlinks=True)
    if (os.path.exists(proj_path + "/data")):
        shutil.copytree(proj_path+"/data", proj_path +
                        "/rpm/data", symlinks=True)
    pathlib.Path(proj_path + "/rpm/sdk_" +
                 vs_string).mkdir(parents=True, exist_ok=True)
    try:
        shutil.rmtree(proj_path + "/rpm/dependence/wheel")
    except:
        pass

    # 只打包有用的sdk部分，且当前sdk路径不一致，打包的是放在工程里面， 编译运行的时候sdk是在工程外面，需要改改路径
    cmd = proj_path + "/../../mb-pkg-tool pack  "
    if (get_osext(vs_string) == ".bat"):
        copy_sdk_win(proj_path+"/../../" + vs_string,
                     proj_path + "/rpm/sdk_" + vs_string)
    else:
        copy_sdk_linux(proj_path+"/../../" + vs_string,
                       proj_path + "/rpm/sdk_" + vs_string)

    if (len(model_key) > 0):
        enret = encrypt_model(proj_path + "/rpm", proj_path +
                              "/../../" + vs_string, model_key)
        if (not enret):
            print("error: encrypt error", file=sys.stderr)
            return

    if (os.path.exists(proj_path + "rpm_copyothers.sh")):
        os.system(proj_path + "rpm_copyothers.sh")
    print(
        "call mb-pkg-tool pack [folder] > [rpm file] to building rpm, waiting...")
    os.system(cmd + proj_path + "/rpm > ./workspace/" +
              module_name + "/" + module_name + ".rpm")

    if (os.path.isfile(proj_path+"/"+module_name + ".rpm")):
        print("success: create " + module_name + ".rpm in " + proj_path)
    else:
        print("error: create error", file=sys.stderr)


def create_editor(curpath, module_name, vs_string, editor_ip):
    sdk_path = os.path.join(curpath, vs_string)

    cmd = curpath + "/editor/run_editor" + get_osext(vs_string)
    os_type = 'win10'
    if platform.system().lower() != 'windows':
        cmd = "sh " + cmd
        os_type = 'linux'

    if (editor_ip.find(":") < 0):
        editor_ip += ":1104"

    # editor目录不存在，创建editor，拷贝模板里面的文件
    pathlib.Path(
        curpath + "/editor/task/log").mkdir(parents=True, exist_ok=True)
    sed_file(sdk_path + "/template/editor/run_editor" + get_osext(vs_string), curpath +
             "/editor/run_editor" + get_osext(vs_string), module_name, vs_string)
    sed_file(sdk_path + "/template/editor/editor_config_" + os_type + ".conf", curpath +
             "/editor/editor_config_" + os_type + ".conf", module_name, vs_string, editor_ip)

    print("open http://" + editor_ip + "/editor")
    # start http-server
    try:
        os.system(cmd)
    except:
        pass


def sed_demos(demo_path):
    for graph_file in os.listdir(demo_path + "/graph"):
        lines = []
        with open(demo_path + "/graph/" + graph_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(demo_path + "/graph/" + graph_file, 'wb') as f:
            for line in lines:
                line = line.replace('\r', '')
                line = line.replace("${HILENS_APP_ROOT}", demo_path)
                line = line.replace('\\', '/')
                f.write(line.encode('utf-8'))


def create_demos(curpath, solution_name, vs_string):
    create_pip_conf()
    solution_dir = curpath + "/" + vs_string + "/solution"
    for sn in os.listdir(solution_dir):
        if (sn != solution_name and solution_name != ""):
            continue
        create_project(curpath, sn, vs_string,
                       sn, "server", "demo")
        sed_demos(curpath + "/demo/" + sn)


def print_usage():
    print(
        """
Usage: Create ModelBox project and flowunit (in windows, suggest using create.bat)

NOTE : you must firstly use bellow cmd to create a project in workspace
    create.py -t server -n your_proj_name {option: -s name, create this project from a solution}, support hilens deployment
 or create.py -t project -n your_proj_name {option: -s name, create this project from a solution}, generally not use
AND  : use bellow cmd to create  [c++|python|infer]  flowunit in this project
    create.py -t c++ -n your_flowunit_name -p your_proj_name
AND  : call workspace/your_proj_name/build_project.sh to build your project, call bin/main.sh[bat] to run
FINAL: create.py -t rpm -n your_proj_name [-k modelkey(option)] to package your project (the same folder with create.py) if upload to hilens

NOTE: create.py -t editor {option: -i ip or ip:port to start editor server in your config ip:port}
NOTE: create.py -t demo to create solutions to runnable demo

for ex: create.py -t server -n my_det -s car_det

-h or --help：show help
-t or --template [c++|python|infer|yolo|project|server|rpm|editor|demo|debug]  create a template or package to rpm ...
-n or --name [your template name]
-p or --project  [your project name when create c++|python|infer|yolo]
-s or --solution [the solution name when create project] create a project from solution
-c or --cfg [flowunit configure json, it's used by UI, you can use it too, but too complicated]
-v or --version：show sdk version
"""
    )


def run_cmd():
    try:
        process = subprocess.Popen(
            'cmd.exe /K python ' + os.path.split(os.path.realpath(__file__))[0] + '\create.py -h')
    except Exception as e:
        print(e)
        os.system('pause')
        return


def get_version(curpath):
    vs_count = 0
    vs_string = ""

    for filename in os.listdir(curpath):
        file_path = os.path.join(curpath, filename)
        if (os.path.isdir(file_path) and filename.startswith("modelbox")):
            vs_string = filename
            vs_count = vs_count + 1

    if (vs_count == 1):
        ver_num = "1.0.0"
        try:
            with open(curpath + "/" + vs_string + "/version") as f:
                ver_num = f.readline().rstrip()
        except:
            pass
        print("sdk version is " + vs_string + "-" + ver_num)
    elif (vs_count == 0):
        print("err: there is no sdk", file=sys.stderr)
    else:
        vs_string = ""
        print("err: too many sdk, please just leave one sdk (folder with modelbox*) here", file=sys.stderr)
    return vs_string


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvt:n:p:s:i:c:k:", [
            "help", "version", "template=", "name=", "project=", "solution=", "ip=", "cfg=", "key="])
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print("argv error,please input as:")
        print_usage()
        return

    # 以下部分即根据分析出的结果做相应的处理，并将处理结果返回给用户
    curpath = os.path.split(os.path.realpath(__file__))[0]
    template_type = ""
    module_name = ""
    proj_name = ""
    solution_name = ""
    editor_ip = "127.0.0.1"
    cfg_json = ""
    model_key = ""
    if platform.system().lower() == 'linux':
        editor_ip = "192.168.2.111"
    for cmd, arg in opts:
        if cmd in ("-h", "--help"):
            print_usage()
            return
        elif cmd in ("-v", "--version"):
            get_version(curpath)
            return
        elif cmd in ("-t", "--template"):
            template_type = arg
        elif cmd in ("-n", "--name"):
            module_name = arg
        elif cmd in ("-p", "--project"):
            proj_name = arg
        elif cmd in ("-s", "--solution"):
            solution_name = arg
        elif cmd in ("-i", "--ip"):
            editor_ip = arg
        elif cmd in ("-c", "--cfg"):
            cfg_json = arg
        elif cmd in ("-k", "--key"):
            model_key = arg

    vs_string = get_version(curpath)
    if (vs_string == ""):
        return

    if (template_type == "demo" or template_type == "editor"):
        module_name = "all"

    if (template_type == "" or module_name == ""):
        print("create.py -t *** -n ***, *** can not be null", file=sys.stderr)
        return

    ret = True
    mdpath = ""
    if (template_type == "project" or template_type == "server"):
        ret, mdpath = create_project(curpath, module_name, vs_string,
                                     solution_name, template_type)
    elif (template_type == "c++"):
        ret, mdpath = create_cplusplus(curpath, module_name,
                                       vs_string, proj_name, cfg_json)
    elif (template_type == "python"):
        ret, mdpath = create_python(curpath, module_name,
                                    vs_string, proj_name, cfg_json)
    elif (template_type == "infer"):
        ret, mdpath = create_infer(curpath, module_name,
                                   vs_string, proj_name, cfg_json)
    elif (template_type == "yolo"):
        ret, mdpath = create_yolo(
            curpath, module_name, vs_string, proj_name, cfg_json)
    elif (template_type == "rpm"):
        create_rpm(curpath + "/workspace/" +
                   module_name, module_name, vs_string, model_key)
    elif (template_type == "editor"):
        create_editor(curpath, module_name, vs_string, editor_ip)
    elif (template_type == "demo"):
        create_demos(curpath, solution_name, vs_string)
    elif (template_type == "debug" and not module_name == ''):
        new_debug_json(curpath + "/workspace/" + module_name,
                       curpath + "/" + vs_string, '')
    else:
        print(
            "error: support [c++|python|infer|yolo|project|server|rpm|editor|demo] with -t or --template", file=sys.stderr)
    if (ret == False and mdpath != "" and os.path.exists(mdpath)):
        shutil.rmtree(mdpath)


def run_main():
    if len(sys.argv) == 1:
        if platform.system().lower() == 'windows':
            run_cmd()
        else:
            print_usage()
        return

    if platform.system().lower() == 'linux':
        output = subprocess.Popen(
            ['id -u HwHiLensDriverUser'], stdout=subprocess.PIPE, shell=True, stderr=subprocess.DEVNULL,
            bufsize=-1).communicate()
        if not "HwHiLensDriverUser" in output:
            output = subprocess.Popen(
                ['id'], stdout=subprocess.PIPE, shell=True).communicate()
            output_str = output[0].decode('utf-8')
            if not "HwHiLensDriverUser" in output_str and not "uid=0" in output_str:
                current_user = output_str.split(')')[0].split('(')[-1]
                print(current_user +
                      " not in HwHiLensDriverUser group, enter root passwd to add")
                os.system(
                    "sudo usermod -a -G HwHiLensDriverUser " + current_user)
    main()


if __name__ == "__main__":
    run_main()
