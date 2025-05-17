import requests
import json
import cv2
import traceback

# 获取Token
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

    headers = {'Content-Type': 'application/json'}
    try:
        rep = requests.post(url, data=json.dumps(body), headers=headers)
        rep.raise_for_status()  # Check if request was successful
        token = rep.headers["X-Subject-Token"]
        return token
    except Exception as e:
        print(f"Error getting token: {str(e)}")
        return None

# 处理视频帧并显示结果
def process_frame_with_api(frame, token, api_url):
    # 临时保存当前帧
    temp_file = "temp_frame.jpg"
    cv2.imwrite(temp_file, frame)

    # 准备上传文件
    files = {'input_video': open(temp_file, 'rb')}
    headers = {'X-Auth-Token': token}

    try:
        # 调用API进行推理
        response = requests.post(api_url, headers=headers, files=files)
        response.raise_for_status()  # 检查请求是否成功
        result = response.json()  # 获取API返回的结果
        category = result["result"]["category"]

        # 根据category值显示相应的信息
        if category == 1:
            cv2.putText(frame, 'Fatigue Detected: Closed Eyes', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif category == 2:
            cv2.putText(frame, 'Fatigue Detected: Yawning', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif category == 3:
            cv2.putText(frame, 'Fatigue Detected: Using Phone', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif category == 4:
            cv2.putText(frame, 'Fatigue Detected: Looking Away', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        traceback.print_exc()

    return frame

# 主函数，用于读取摄像头并显示结果
def run_camera_detection():
    token = getToken()
    if not token:
        print("Error: Could not get token. Exiting.")
        return

    api_url = "https://015c2ea02afc4cf0afbd3935a760adab.apig.cn-north-4.huaweicloudapis.com/v1/infers/d8700113-5c4a-4ee7-b987-18e87ea6062b"

    # 打开摄像头
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while cap.isOpened():
        # 读取视频帧
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from camera.")
            break

        # 调用API检测并显示结果
        frame = process_frame_with_api(frame, token, api_url)

        # 显示结果帧
        cv2.imshow('Fatigue Detection', frame)

        # 按'q'或'ESC'键退出
        if cv2.waitKey(1) in [ord('q'), 27]:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_camera_detection()
