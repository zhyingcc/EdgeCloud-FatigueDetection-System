:: Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

set BASE_PATH=%~dp0
set PATH=%BASE_PATH%\python-embed;%PATH%
set PYTHONPATH=
set PYTHONHOME=

python.exe -u %BASE_PATH%\create.py %1 %2 %3 %4 %5 %6 %7 %8 %9