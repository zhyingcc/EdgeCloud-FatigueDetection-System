:: Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

:: if HILENS_APP_NAME not set, it will be treated as mock

@echo off
set BASE_PATH=%~dp0
set BASE_PATH_LINUX=%BASE_PATH:\=/%
if "%HILENS_APP_NAME%" == "" (
  set HILENS_APP_ROOT=%BASE_PATH_LINUX%..
  set IVA_SVC_CONFIG={"algorithm":{"multiTask":"no","algType":"mock"},"mockFile":"%BASE_PATH_LINUX%../bin/mock_task.toml","svcInstanceId":"modelbox-instance-mock","isv":{"auth":{"id":"test"}}}
  set HILENS_DATA_DIR=%BASE_PATH_LINUX%../hilens_data_dir
  set HILENS_IS_SIMULATE=YES
  set HILENS_MB_SDK_PATH=%BASE_PATH_LINUX%../../../SDKNAME
  set HILENS_EMBED_PYTHON_PATH=%BASE_PATH_LINUX%../../../python-embed
) else (
  set HILENS_MB_SDK_PATH=%HILENS_MB_SDK_ROOT%/sdk_SDKNAME
  if "%HILENS_EMBED_PYTHON_PATH%" == "" (
    set HILENS_EMBED_PYTHON_PATH=%HILENS_APP_ROOT%/python-embed
  )
)

set PYTHONHOME=
set PYTHONPATH=%HILENS_APP_ROOT%/dependence/python

:: install python if needed
if "%HILENS_IS_SIMULATE%" == "YES" (
  set GITBASH_PATH=
  if exist %HILENS_APP_ROOT%/../../git_bash_path.txt (
    set /P GITBASH_PATH=<%HILENS_APP_ROOT%/../../git_bash_path.txt
  )
)

if "%HILENS_IS_SIMULATE%" == "YES" (
  fc "%BASE_PATH%\..\dependence\modelbox_requirements.txt" "%BASE_PATH%\..\dependence\python\installed_modelbox_requirements.txt" > nul 
  if errorlevel 1 (
    if "%GITBASH_PATH%" == "" (
      %HILENS_APP_ROOT%/build_project.sh
    ) else (
      "%GITBASH_PATH%" %HILENS_APP_ROOT%/build_project.sh
    )
  )
)

@echo on
set PATH=%HILENS_EMBED_PYTHON_PATH%;%HILENS_MB_SDK_PATH%/bin;%HILENS_APP_ROOT%/dependence/lib;%PATH%

@echo off
if "%1" == "default" (
  set HILENS_MB_GRAPH_TYPE=
) else if "%1" == "" (
  set HILENS_MB_GRAPH_TYPE=
) else (
  set HILENS_MB_GRAPH_TYPE=_%1
)

if "%2" == "" (
  set HILENS_MB_LOG_LEVEL=WARN
) else (
  set HILENS_MB_LOG_LEVEL=%2
)

@echo on

modelbox-tool.exe -verbose -log-level %HILENS_MB_LOG_LEVEL% flow -run %HILENS_APP_ROOT%/graph/MODULENAME%HILENS_MB_GRAPH_TYPE%.toml

@echo off
if "%HILENS_IS_SIMULATE%" == "YES" (
  pause
)
@echo on
