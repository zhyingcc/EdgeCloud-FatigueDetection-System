import requests

def upload_audio_to_server(file_path):
    url = "http://your-server-ip:8000/process_audio"  # 将此替换为您的服务器 URL
    files = {'audio': open(file_path, 'rb')}
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            print("文件上传成功，正在处理...")
            return response.content  # 接收处理后的音频数据
        else:
            print(f"文件上传失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"上传文件时出错: {e}")
        return None

if __name__ == "__main__":
    # 上传 'recorded_audio.wav' 并接收处理后的音频
    audio_response = upload_audio_to_server("recorded_audio.wav")
    if audio_response:
        with open("response_audio.wav", 'wb') as f:
            f.write(audio_response)
        print("已从服务器接收处理后的音频。")
