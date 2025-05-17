import cv2
import time
import pyttsx3
import requests
import json
import collections
import threading
import queue

# 初始化TTS引擎
engine = pyttsx3.init()

# 创建一个队列来保存要朗读的文本
speech_queue = queue.Queue()

def speak_warning():
    """从队列中取出文本并朗读"""
    while True:
        text = speech_queue.get()  # 阻塞，直到有文本进入队列
        engine.say(text)
        engine.runAndWait()
        speech_queue.task_done()

# 启动一个后台线程运行 speak_warning 函数，专门负责处理 TTS 任务
speech_thread = threading.Thread(target=speak_warning, daemon=True)
speech_thread.start()

def getToken():
    url = "https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens"
    body = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "domain": {"name": "hid_eb2gnxs55yqdnn_"},
                        "name": "Czq",
                        "password": "darling.czq2002"
                    }
                }
            },
            "scope": {"project": {"name": "cn-north-4"}}
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    token = response.headers["X-Subject-Token"]
    print(token)
    return token

def save_video_from_frames(frames, output_file="temp_video.mp4"):
    if not frames:
        return None

    height, width, layers = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

    for frame in frames:
        out.write(frame)
    out.release()
    return output_file


def upload_video_and_get_result(file_path):
    url = "https://015c2ea02afc4cf0afbd3935a760adab.apig.cn-north-4.huaweicloudapis.com/v1/infers/d8700113-5c4a-4ee7-b987-18e87ea6062b"
    token = getToken()
    headers = {
        'X-Auth-Token': token
    }
    files = {
        'input_video': open(file_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    print(response.json())
    return response.json()


# 异步处理视频保存和分析
def async_save_and_analyze(frames, warning_flag):
    output_file = save_video_from_frames(frames)
    result = upload_video_and_get_result(output_file)
    category = result.get("result", {}).get("category", None)

    if category == 4:  # 转头
        warning_flag[4] = True  # 设置标志位表示需要显示警告
    else:
        warning_flag[4] = False  # 如果没有检测到违规行为，清除警告
    if category == 3:
        warning_flag[3] = True  # 设置标志位表示需要显示警告
    else:
        warning_flag[3] = False  # 如果没有检测到违规行为，清除警告
    if category == 2:  # 哈欠
        warning_flag[2] = True  # 设置标志位表示需要显示警告
    else:
        warning_flag[2] = False  # 如果没有检测到违规行为，清除警告
    if category == 1:  # 闭眼
        warning_flag[1] = True  # 设置标志位表示需要显示警告
    else:
        warning_flag[1] = False  # 如果没有检测到违规行为，清除警告

def main():
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    frame_queue = collections.deque(maxlen=150)  # 存储最近5秒的帧，假设帧率是30fps (5秒 * 30 = 150帧)
    warning_flag = [False, False, False, False, False, False]  # 用于指示是否显示警告
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if ret:
            if warning_flag[4]:
                cv2.putText(frame, "Warning: do not turn your head", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                speech_queue.put("Warning: do not turn your head")  # 将文本放入队列中
            if warning_flag[3]:
                cv2.putText(frame, "Warning: do not use phone", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                speech_queue.put("Warning: do not use phone")
            if warning_flag[2]:
                cv2.putText(frame, "Warning: do not yawn", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                speech_queue.put("Warning: do not ha yawn")
            if warning_flag[1]:
                cv2.putText(frame, "Warning: do not close your eyes", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                speech_queue.put("Warning: do not close your eyes")

            cv2.imshow('Live Stream', frame)
            frame_queue.append(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        current_time = time.time()
        elapsed_time = current_time - start_time

        # 每秒进行一次分析
        if elapsed_time >= 1:
            if len(frame_queue) == 150:
                threading.Thread(target=async_save_and_analyze, args=(list(frame_queue), warning_flag)).start()
            start_time = current_time  # 重置时间

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
