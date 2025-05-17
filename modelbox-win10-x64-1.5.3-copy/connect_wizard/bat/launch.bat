chcp 65001

set BASE_PATH=%~dp0

cd %BASE_PATH%/../../modelbox-win10-x64/bin
ffmpeg.exe -f dshow -video_size 1280x720 -framerate 30 -vcodec mjpeg -i video=%1 -vcodec h264_mf -b:v 4M -rtsp_transport tcp -f rtsp rtsp://localhost:8554/instream
