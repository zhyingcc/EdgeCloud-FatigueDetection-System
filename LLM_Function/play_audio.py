import os
from playsound import playsound

def play_audio(file_path):
    """播放音频文件。"""
    try:
        print(f"正在播放音频: {file_path}")
        playsound(file_path)
    except Exception as e:
        print(f"播放音频时出错: {e}")

if __name__ == "__main__":
    audio_file = "response_audio.wav"
    if os.path.exists(audio_file):
        play_audio(audio_file)
    else:
        print("未找到音频文件。")
