# import sounddevice as sd
# from scipy.io.wavfile import write
# import requests
# import os
# from playsound import playsound
#
# def record_audio(filename, duration=5, fs=16000):
#     """录制音频并保存为 WAV 文件。"""
#     print(f"开始录制 {duration} 秒的音频...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()  # 等待录音结束
#     write(filename, fs, recording)  # 保存为 WAV 文件
#     print(f"录音完成，音频已保存为 {filename}")
#
# def upload_audio_to_server(file_path):
#     url = "http://192.168.1.72:8001/process_audio"  # 将此替换为您的服务器 URL
#     files = {'audio': open(file_path, 'rb')}
#     try:
#         response = requests.post(url, files=files)
#         if response.status_code == 200:
#             print("文件上传成功，正在处理...")
#             return response.content  # 接收处理后的音频数据
#         else:
#             print(f"文件上传失败: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"上传文件时出错: {e}")
#         return None
#
# def play_audio(file_path):
#     """播放音频文件。"""
#     try:
#         print(f"正在播放音频: {file_path}")
#         playsound(file_path)
#     except Exception as e:
#         print(f"播放音频时出错: {e}")
#
# if __name__ == "__main__":
#     # 步骤 1：录制音频
#     recorded_audio_file = "recorded_audio.wav"
#     record_audio(recorded_audio_file, duration=5)  # 可根据需要调整持续时间
#
#     # 步骤 2：上传音频并接收处理后的音频
#     response_audio_data = upload_audio_to_server(recorded_audio_file)
#     if response_audio_data:
#         # 保存接收到的音频数据
#         response_audio_file = "response_audio.wav"
#         with open(response_audio_file, 'wb') as f:
#             f.write(response_audio_data)
#         print("已从服务器接收处理后的音频。")
#
#         # 步骤 3：播放接收到的音频
#         play_audio(response_audio_file)
#     else:
#         print("未能接收到处理后的音频。")


# import sounddevice as sd
# from scipy.io.wavfile import write
# import requests
# import os
# from playsound import playsound
# from sshtunnel import SSHTunnelForwarder
#
# def record_audio(filename, duration=5, fs=16000):
#     """录制音频并保存为 WAV 文件。"""
#     print(f"开始录制 {duration} 秒的音频...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()  # 等待录音结束
#     write(filename, fs, recording)  # 保存为 WAV 文件
#     print(f"录音完成，音频已保存为 {filename}")
#
# def upload_audio_to_server_through_ssh(file_path):
#     # SSH 连接信息
#     jump_host = '222.204.6.193'
#     jump_user = 'YZH'
#     jump_password = 'YZH@good114'  # 使用密码认证
#     jump_port = 8087
#
#     # 远程服务器的 SSH 连接信息
#     remote_server_ip = '192.168.1.72'
#     remote_port = 22  # 远程服务器的 SSH 端口
#
#     # 使用 sshtunnel 创建 SSH 隧道
#     with SSHTunnelForwarder(
#         (jump_host, jump_port),
#         ssh_username=jump_user,
#         ssh_password=jump_password,
#         remote_bind_address=(remote_server_ip, 8001),  # 服务器上的 Flask 监听端口
#         local_bind_address=('0.0.0.0', 5000)  # 本地绑定端口
#     ) as tunnel:
#         print("SSH 隧道已建立，开始连接服务器...")
#
#         # 上传音频文件到通过隧道建立的服务器端口
#         url = f"http://127.0.0.1:{tunnel.local_bind_port}/process_audio"
#         files = {'audio': open(file_path, 'rb')}
#
#         try:
#             response = requests.post(url, files=files)
#             if response.status_code == 200:
#                 print("文件上传成功，正在处理...")
#                 return response.content  # 接收处理后的音频数据
#             else:
#                 print(f"文件上传失败: {response.status_code}")
#                 return None
#         except Exception as e:
#             print(f"上传文件时出错: {e}")
#             return None
#
# def play_audio(file_path):
#     """播放音频文件。"""
#     try:
#         print(f"正在播放音频: {file_path}")
#         playsound(file_path)
#     except Exception as e:
#         print(f"播放音频时出错: {e}")
#
# if __name__ == "__main__":
#     # 步骤 1：录制音频
#     recorded_audio_file = "recorded_audio.wav"
#     record_audio(recorded_audio_file, duration=5)  # 可根据需要调整持续时间
#
#     # 步骤 2：通过 SSH 隧道上传音频并接收处理后的音频
#     response_audio_data = upload_audio_to_server_through_ssh(recorded_audio_file)
#     if response_audio_data:
#         # 保存接收到的音频数据
#         response_audio_file = "response_audio.wav"
#         with open(response_audio_file, 'wb') as f:
#             f.write(response_audio_data)
#         print("已从服务器接收处理后的音频。")
#
#         # 步骤 3：播放接收到的音频
#         play_audio(response_audio_file)
#     else:
#         print("未能接收到处理后的音频。")

# # 最终上传音频下载音频
# import speech_recognition as sr
# import wave
# import os
# from datetime import datetime
# import paramiko
# from paramiko import SSHClient, AutoAddPolicy
# from scp import SCPClient
# # 从服务器上下载并且自动播放
# import pygame  # 用于播放音频
# from playsound import playsound
#
# def create_ssh_client(server, port, user, password):
#     """连接到指定的服务器"""
#     client = paramiko.SSHClient()
#     client.load_system_host_keys()
#     client.set_missing_host_key_policy(AutoAddPolicy())
#     client.connect(server, port=port, username=user, password=password)
#     return client
#
#
# def scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
#                           remote_host, remote_port, remote_user, remote_password,
#                           local_file_path, remote_file_path):
#     """通过跳板机把文件传输到目标服务器"""
#     # 连接到跳板机
#     jump_client = create_ssh_client(jump_host, jump_port, jump_user, jump_password)
#
#     # 设置跳板机的转发
#     transport = jump_client.get_transport()
#     remote_channel = transport.open_channel("direct-tcpip", (remote_host, remote_port), ("localhost", 0))
#
#     # 通过跳板机连接目标服务器
#     remote_client = paramiko.SSHClient()
#     remote_client.set_missing_host_key_policy(AutoAddPolicy())
#     remote_client.connect(remote_host, port=remote_port, username=remote_user, password=remote_password,
#                           sock=remote_channel)
#
#     # 使用SCP传输文件到目标服务器
#     with SCPClient(remote_client.get_transport()) as scp:
#         scp.put(local_file_path, remote_file_path)
#
#     # 关闭连接
#     remote_client.close()
#     jump_client.close()
#
# def upload(i):
#     # 配置信息
#     jump_host = '222.204.6.193'  # 跳板机IP地址
#     jump_port = 8087  # 跳板机端口
#     jump_user = 'ZZQ'  # 你的跳板机用户名
#     jump_password = 'ZZQ@good114'  # 你的跳板机密码
#
#     remote_host = '192.168.1.72'  # 目标服务器IP
#     remote_port = 22  # 目标服务器端口
#     remote_user = 'ZZQ'  # 你的目标服务器用户名
#     remote_password = 'ZZQ@good114'  # 你的目标服务器密码
#
#     local_file_path = rf'D:\GitHub_local\24_Huawei_developer\LLM_Function\speech_1.wav'  # 你想上传的本地文件路径
#     remote_file_path = '/app/huaweiyun/sichuan/WAV16k/test/'  # 文件在目标服务器上的存储路径
#     # 调用函数上传文件
#     scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
#                           remote_host, remote_port, remote_user, remote_password,
#                           local_file_path, remote_file_path)
#
# def save_audio_wav(audio_data, output_filename):
#     """保存音频数据到 WAV 文件"""
#     with wave.open(output_filename, "wb") as wf:
#         wf.setnchannels(1)
#         wf.setsampwidth(2)  # 16位音频样本
#         wf.setframerate(16000)  # 设置采样率
#         wf.writeframes(audio_data.get_wav_data())
#
# def listen_and_record():
#     """实时截获说话音频，并保存为 WAV 文件"""
#     recognizer = sr.Recognizer()
#     recognizer.dynamic_energy_threshold = False  # 自动调整能量阈值
#     recognizer.energy_threshold = 50  # 设置静音检测阈值，值越高需要更大音量
#
#     mic = sr.Microphone(sample_rate=16000)
#
#     with mic as source:
#         print("开始监听，请开始说话...")
#         recognizer.adjust_for_ambient_noise(source)  # 自动调整噪声水平
#
#         # while True:
#         i = 1
#         try:
#             print("等待说话中...")
#             audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)  # phrase_time_limit 用于限制单次录音时长
#             if audio:
#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 output_filename = f"speech_{i}.wav"
#                 save_audio_wav(audio, output_filename)
#                 print(f"已保存语音到 {output_filename}")
#                 # playsound("./speech_1.wav")
#                 upload(i)
#                 i += 1
#
#         except sr.WaitTimeoutError:
#             print("没有检测到说话声...")
#         except KeyboardInterrupt:
#             print("录音已结束。")
#         print("结束")
#
#
# # 调用函数开始实时监听并截获说话的语句
#
#
#
#
#
#
# # 创建SSH连接
# def create_ssh_client(server, port, user, password):
#     """连接到指定的服务器"""
#     client = paramiko.SSHClient()
#     client.load_system_host_keys()
#     client.set_missing_host_key_policy(AutoAddPolicy())
#     client.connect(server, port=port, username=user, password=password)
#     return client
#
# # 通过跳板机从服务器下载文件夹中的所有文件到本地
# def scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
#                               remote_host, remote_port, remote_user, remote_password,
#                               local_directory_path, remote_directory_path):
#     """通过跳板机从服务器下载文件夹中的所有文件到本地"""
#     # 连接到跳板机
#     jump_client = create_ssh_client(jump_host, jump_port, jump_user, jump_password)
#
#     # 设置跳板机的转发
#     transport = jump_client.get_transport()
#     remote_channel = transport.open_channel("direct-tcpip", (remote_host, remote_port), ("localhost", 0))
#
#     # 通过跳板机连接目标服务器
#     remote_client = paramiko.SSHClient()
#     remote_client.set_missing_host_key_policy(AutoAddPolicy())
#     remote_client.connect(remote_host, port=remote_port, username=remote_user, password=remote_password,
#                           sock=remote_channel)
#
#     # 使用SCP递归下载整个文件夹
#     with SCPClient(remote_client.get_transport()) as scp:
#         scp.get(remote_directory_path, local_directory_path, recursive=True)
#
#     # 关闭连接
#     remote_client.close()
#     jump_client.close()
#
# # 播放音频文件
# def play_audio(file_path):
#     """播放本地音频文件"""
#     # 初始化pygame的音频模块
#     pygame.mixer.init()
#     # 加载音频文件
#     pygame.mixer.music.load(file_path)
#     # 播放音频文件
#     pygame.mixer.music.play()
#     # 保持程序运行直到播放结束
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)
#
# # 主程序入口
# if __name__ == "__main__":
#     # 配置信息
#     jump_host = '222.204.6.193'  # 跳板机IP地址
#     jump_port = 8087  # 跳板机端口
#     jump_user = 'ZZQ'  # 跳板机用户名
#     jump_password = 'ZZQ@good114'  # 跳板机密码
#
#     remote_host = '192.168.1.72'  # 目标服务器IP
#     remote_port = 22  # 目标服务器端口
#     remote_user = 'ZZQ'  # 目标服务器用户名
#     remote_password = 'ZZQ@good114'  # 目标服务器密码
#
#     local_directory_path = r'./downloaded_audio/'  # 保存文件的本地目录路径
#     remote_directory_path = '/app/huaweiyun/sichuan/WAV16k/output/temp.wav'  # 远程目录路径
#     listen_and_record()
#     # 创建本地目录
#     if not os.path.exists(local_directory_path):
#         os.makedirs(local_directory_path)
#
#     # 从服务器下载文件
#     scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
#                               remote_host, remote_port, remote_user, remote_password,
#                               local_directory_path, remote_directory_path)
#
#     # 获取下载的文件列表
#     audio_files = [f for f in os.listdir(local_directory_path) if f.endswith('.wav')]  # 修改为查找 .mp3 文件
#     print(os.listdir(local_directory_path))
#     print(audio_files)
#     if audio_files:
#         # 播放下载的第一个音频文件
#         # first_audio_file = os.path.join(local_directory_path, audio_files[0])
#         # print()
#         print(f"正在播放文件: {audio_files}")
#         playsound(r'./downloaded_audio/temp.wav')
#     else:
#         print("没有找到音频文件！")

# 上传到服务器上
import speech_recognition as sr
import wave
import os
from datetime import datetime
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
# 从服务器上下载并且自动播放
import paramiko
from paramiko import AutoAddPolicy
from scp import SCPClient
import pygame  # 用于播放音频
import os
from playsound import playsound

def create_ssh_client(server, port, user, password):
    """连接到指定的服务器"""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port=port, username=user, password=password)
    return client


def scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
                          remote_host, remote_port, remote_user, remote_password,
                          local_file_path, remote_file_path):
    """通过跳板机把文件传输到目标服务器"""
    # 连接到跳板机
    jump_client = create_ssh_client(jump_host, jump_port, jump_user, jump_password)

    # 设置跳板机的转发
    transport = jump_client.get_transport()
    remote_channel = transport.open_channel("direct-tcpip", (remote_host, remote_port), ("localhost", 0))

    # 通过跳板机连接目标服务器
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(AutoAddPolicy())
    remote_client.connect(remote_host, port=remote_port, username=remote_user, password=remote_password,
                          sock=remote_channel)

    # 使用SCP传输文件到目标服务器
    with SCPClient(remote_client.get_transport()) as scp:
        scp.put(local_file_path, remote_file_path)

    # 关闭连接
    remote_client.close()
    jump_client.close()

def upload(i):
    # 配置信息
    jump_host = '222.204.6.193'  # 跳板机IP地址
    jump_port = 8087  # 跳板机端口
    jump_user = 'ZZQ'  # 你的跳板机用户名
    jump_password = 'ZZQ@good114'  # 你的跳板机密码

    remote_host = '192.168.1.72'  # 目标服务器IP
    remote_port = 22  # 目标服务器端口
    remote_user = 'ZZQ'  # 你的目标服务器用户名
    remote_password = 'ZZQ@good114'  # 你的目标服务器密码

    local_file_path = rf'./speech_{i}.wav'  # 你想上传的本地文件路径
    remote_file_path = '/app/huaweiyun/sichuan/WAV16k/input/'  # 文件在目标服务器上的存储路径
    # 调用函数上传文件
    scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
                          remote_host, remote_port, remote_user, remote_password,
                          local_file_path, remote_file_path)

def save_audio_wav(audio_data, output_filename):
    """保存音频数据到 WAV 文件"""
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16位音频样本
        wf.setframerate(16000)  # 设置采样率
        wf.writeframes(audio_data.get_wav_data())

def listen_and_record():
    """实时截获说话音频，并保存为 WAV 文件"""
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False  # 自动调整能量阈值
    recognizer.energy_threshold = 50  # 设置静音检测阈值，值越高需要更大音量

    mic = sr.Microphone(sample_rate=16000)

    with mic as source:
        print("开始监听，请开始说话...")
        recognizer.adjust_for_ambient_noise(source)  # 自动调整噪声水平

        while True:
            i = 1
            try:
                print("等待说话中...")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)  # phrase_time_limit 用于限制单次录音时长
                if audio:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"speech_{i}.wav"
                    save_audio_wav(audio, output_filename)
                    print(f"已保存语音到 {output_filename}")
                    # upload(i)
                    i += 1
                    break
            except sr.WaitTimeoutError:
                print("没有检测到说话声...")
            except KeyboardInterrupt:
                print("录音已结束。")
                break






# 创建SSH连接
def create_ssh_client(server, port, user, password):
    """连接到指定的服务器"""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port=port, username=user, password=password)
    return client

# 通过跳板机从服务器下载文件夹中的所有文件到本地
def scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
                              remote_host, remote_port, remote_user, remote_password,
                              local_directory_path, remote_directory_path):
    """通过跳板机从服务器下载文件夹中的所有文件到本地"""
    # 连接到跳板机
    jump_client = create_ssh_client(jump_host, jump_port, jump_user, jump_password)

    # 设置跳板机的转发
    transport = jump_client.get_transport()
    remote_channel = transport.open_channel("direct-tcpip", (remote_host, remote_port), ("localhost", 0))

    # 通过跳板机连接目标服务器
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(AutoAddPolicy())
    remote_client.connect(remote_host, port=remote_port, username=remote_user, password=remote_password,
                          sock=remote_channel)

    # 使用SCP递归下载整个文件夹
    with SCPClient(remote_client.get_transport()) as scp:
        scp.get(remote_directory_path, local_directory_path, recursive=True)

    # 关闭连接
    remote_client.close()
    jump_client.close()

# 播放音频文件
def play_audio(file_path):
    """播放本地音频文件"""
    # 初始化pygame的音频模块
    pygame.mixer.init()
    # 加载音频文件
    pygame.mixer.music.load(file_path)
    # 播放音频文件
    pygame.mixer.music.play()
    # 保持程序运行直到播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# # 主程序入口 一次版
# if __name__ == "__main__":
#     # 调用函数开始实时监听并截获说话的语句
#     listen_and_record()
#     # 配置信息
#     jump_host = '222.204.6.193'  # 跳板机IP地址
#     jump_port = 8087  # 跳板机端口
#     jump_user = 'ZZQ'  # 跳板机用户名
#     jump_password = 'ZZQ@good114'  # 跳板机密码
#
#     remote_host = '192.168.1.72'  # 目标服务器IP
#     remote_port = 22  # 目标服务器端口
#     remote_user = 'ZZQ'  # 目标服务器用户名
#     remote_password = 'ZZQ@good114'  # 目标服务器密码
#
#     local_directory_path = r'./downloaded_audio/'  # 保存文件的本地目录路径
#     remote_directory_path = '/app/huaweiyun/sichuan/WAV16k/output/temp.wav'  # 远程目录路径
#
#     # 创建本地目录
#     if not os.path.exists(local_directory_path):
#         os.makedirs(local_directory_path)
#
#     # 从服务器下载文件
#     scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
#                               remote_host, remote_port, remote_user, remote_password,
#                               local_directory_path, remote_directory_path)
#
#     # 获取下载的文件列表
#     audio_files = [f for f in os.listdir(local_directory_path) if f.endswith('.wav')]  # 修改为查找 .mp3 文件
#     print(os.listdir(local_directory_path))
#     print(audio_files)
#     if audio_files:
#         # 播放下载的第一个音频文件
#         # first_audio_file = os.path.join(local_directory_path, audio_files[0])
#         # print()
#         print(f"正在播放文件: {audio_files}")
#         playsound(r'./downloaded_audio/temp.wav')
#     else:
#         print("没有找到音频文件！")

# 主程序入口
if __name__ == "__main__":
    i = 1
    while True:
        # 调用函数开始实时监听并截获说话的语句
        listen_and_record()
        # 配置信息
        jump_host = '222.204.6.193'  # 跳板机IP地址
        jump_port = 8087  # 跳板机端口
        jump_user = 'ZZQ'  # 跳板机用户名
        jump_password = 'ZZQ@good114'  # 跳板机密码

        remote_host = '192.168.1.72'  # 目标服务器IP
        remote_port = 22  # 目标服务器端口
        remote_user = 'ZZQ'  # 目标服务器用户名
        remote_password = 'ZZQ@good114'  # 目标服务器密码

        local_directory_path = r'./downloaded_audio/'  # 保存文件的本地目录路径
        remote_directory_path = f'/app/huaweiyun/sichuan/WAV16k/output/temp{i}.wav'  # 远程目录路径

        # 创建本地目录
        if not os.path.exists(local_directory_path):
            os.makedirs(local_directory_path)

        # 从服务器下载文件
        scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
                                  remote_host, remote_port, remote_user, remote_password,
                                  local_directory_path, remote_directory_path)

        # 获取下载的文件列表
        audio_files = [f for f in os.listdir(local_directory_path) if f.endswith('.wav')]
        print(os.listdir(local_directory_path))
        print(audio_files)
        if audio_files:
            print(f"正在播放文件: {audio_files}")
            playsound(f'./downloaded_audio/temp{i}.wav')
        else:
            print("没有找到音频文件！")

        i += 1

