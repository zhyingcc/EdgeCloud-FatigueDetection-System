set BASE_PATH=%~dp0

cd %BASE_PATH%/../../modelbox-win10-x64/bin

ffmpeg.exe -list_devices true -f dshow -i dummy > %BASE_PATH%/tmp.txt 2>&1
