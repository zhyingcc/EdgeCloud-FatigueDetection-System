import cv2
import time
import pyttsx3
import requests
import json
import collections
import threading
import queue
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 初始化TTS引擎
engine = pyttsx3.init()

# 创建一个队列来保存要朗读的文本
speech_queue = queue.Queue()

# 用于追踪每种警告的播放次数，初始值为0
warning_played_count = [0, 0, 0, 0, 0]

# 新增：用于存储最新的人脸坐标和更新时间，并确保线程安全
latest_face = None
latest_face_time = 0
face_lock = threading.Lock()

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
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "domain": {
                            "name": "hw074922794"
                        },
                        "name": "nanqipro",
                        "password": "8729512929abc"
                    }
                }
            },
            "scope": {
                "project": {
                    "name": "cn-north-4"
                }
            }
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(body), headers=headers)
    token = response.headers.get("X-Subject-Token", "")
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
    url = "https://26c1aa8fc1714f8cbbb4d054f6fa4acc.apig.cn-north-4.huaweicloudapis.com/v1/infers/10ad4dc2-b6fc-44c0-affe-dee8c4da6c52"
    token = getToken()
    headers = {
        'X-Auth-Token': token
    }
    files = {
        'input_video': open(file_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    try:
        result = response.json()
    except json.JSONDecodeError:
        result = {}
    print(result)
    return result

# 异步处理视频保存和分析
def async_save_and_analyze(frames, warning_flag):
    global latest_face, latest_face_time
    output_file = save_video_from_frames(frames)
    if output_file is None:
        return
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

    # 新增：提取最后一个人脸坐标并更新最新人脸和时间
    faces = result.get("result", {}).get("faces", [])
    if faces:
        last_face = faces[-1]
        top_left = last_face.get("top_left", [0, 0])
        bottom_right = last_face.get("bottom_right", [0, 0])
        with face_lock:
            latest_face = (tuple(top_left), tuple(bottom_right))
            latest_face_time = time.time()

def put_chinese_text_v1(image, text, position, font_size=30, bold_factor=2):
    # 将 OpenCV 图片转换为 Pillow 图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # 设置字体，可以指定路径使用合适的字体文件
    font = ImageFont.truetype("C:/Users/86188/AppData/Local/Microsoft/Windows/Fonts/msyh.ttf", font_size)

    # 获取文本的尺寸
    text_width, text_height = draw.textsize(text, font=font)

    # 计算水平方向的居中位置
    image_width, image_height = image_pil.size
    position_x = (image_width - text_width) // 2

    # 计算垂直方向上靠上方的显示位置
    position_y = int(image_height * 0.1)  # 设置为画面高度的10%左右

    # 计算文本的起始位置
    position = (position_x, position_y)

    # 模拟加粗效果，通过多次绘制文本
    for i in range(bold_factor):
        offset = i - (bold_factor // 2)  # 偏移量
        draw.text((position[0] + offset, position[1] + offset), text, font=font, fill=(255, 0, 0))  # 红色

    # 将 Pillow 图像转换回 OpenCV 图像
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def put_chinese_text_v2(image, text, font_size=30, bold_factor=2):
    # 将 OpenCV 图片转换为 Pillow 图像
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # 设置字体
    font = ImageFont.truetype("C:/Users/86188/AppData/Local/Microsoft/Windows/Fonts/msyh.ttf", font_size)
    
    # 获取文本的边界框 (bounding box)
    bbox = draw.textbbox((0, 0), text, font=font)  # (left, top, right, bottom)
    text_width = bbox[2] - bbox[0]  # 右边界 - 左边界
    text_height = bbox[3] - bbox[1]  # 底边界 - 上边界
    
    # 计算水平方向的居中位置
    image_width, image_height = image_pil.size
    position_x = (image_width - text_width) // 2
    
    # 计算垂直方向上靠上方的显示位置
    position_y = int(image_height * 0.1)  # 设置为画面高度的10%左右
    
    # 计算文本的起始位置
    position = (position_x, position_y)

    # 模拟加粗效果，通过多次绘制文本
    for i in range(bold_factor):
        offset = i - (bold_factor // 2)  # 偏移量
        draw.text((position[0] + offset, position[1] + offset), text, font=font, fill=(255, 0, 0))  # 红色

    # 将 Pillow 图像转换回 OpenCV 图像
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def main():
    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    frame_queue = collections.deque(maxlen=150)
    warning_flag = [False, False, False, False, False, False]  # 用于指示是否显示警告
    start_time = time.time()

    # 创建一个窗口并设置其大小
    cv2.namedWindow('Live Stream', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Live Stream', 800, 600)  # 设置窗口的大小，例如 800x600

    while True:
        ret, frame = cap.read()
        if ret:
            # 新增：在绘制警告前绘制人脸矩形框
            with face_lock:
                current_time = time.time()
                # 仅在最新人脸数据在1秒内时绘制
                if latest_face and (current_time - latest_face_time <= 1):
                    top_left, bottom_right = latest_face
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)  # 绿色矩形框

            # 处理警告文字
            if warning_flag[4]:
                frame = put_chinese_text_v1(frame, "警告! 请不要左顾右盼!", (50, 50), 30)
                if warning_played_count[4] < 1:  
                    speech_queue.put("警告! 请不要左顾右盼!")
                    warning_played_count[4] += 1  

            if warning_flag[3]:
                frame = put_chinese_text_v1(frame, "警告! 开车不能打电话!", (50, 50), 30)
                if warning_played_count[3] < 1:
                    speech_queue.put("警告! 开车不能打电话!")
                    warning_played_count[3] += 1

            if warning_flag[2]:
                frame = put_chinese_text_v1(frame, "警告! 你在打哈欠!", (50, 50), 30)
                if warning_played_count[2] < 1:
                    speech_queue.put("警告! 你在打哈欠!")
                    warning_played_count[2] += 1

            if warning_flag[1]:
                frame = put_chinese_text_v1(frame, "警告! 请不要闭眼睛!", (50, 50), 30)
                if warning_played_count[1] < 1:
                    speech_queue.put("警告! 请不要闭眼睛!")
                    warning_played_count[1] += 1

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

        # 重置播放次数标志位，当警告解除时
        if not warning_flag[4]:
            warning_played_count[4] = 0
        if not warning_flag[3]:
            warning_played_count[3] = 0
        if not warning_flag[2]:
            warning_played_count[2] = 0
        if not warning_flag[1]:
            warning_played_count[1] = 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
