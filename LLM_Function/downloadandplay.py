# import os
# import paramiko
# from paramiko import SSHClient, AutoAddPolicy
# from scp import SCPClient
# from playsound import playsound  # 用于播放音频
# import time
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
# def scp_file_from_server(jump_host, jump_port, jump_user, jump_password,
#                          remote_host, remote_port, remote_user, remote_password,
#                          remote_file_path, local_file_path):
#     """通过跳板机从目标服务器下载文件"""
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
#     # 使用SCP从目标服务器下载文件
#     with SCPClient(remote_client.get_transport()) as scp:
#         scp.get(remote_file_path, local_file_path)
#
#     # 关闭连接
#     remote_client.close()
#     jump_client.close()
#
# def download_and_play():
#     # 配置信息
#     jump_host = '222.204.6.193'  # 跳板机IP地址
#     jump_port = 8087  # 跳板机端口
#     jump_user = 'ZJ'  # 跳板机用户名
#     jump_password = 'ZJ@good114'  # 跳板机密码
#
#     remote_host = '192.168.1.72'  # 目标服务器IP
#     remote_port = 22  # 目标服务器端口
#     remote_user = 'ZZQ'  # 目标服务器用户名
#     remote_password = 'ZZQ@good114'  # 目标服务器密码
#
#     remote_audio_folder = '/app/huaweiyun/sichuan/WAV16k/output/'  # 远程音频文件夹路径
#     local_audio_folder = './downloaded_audio/'  # 本地存储音频文件夹路径
#
#     # 确保本地文件夹存在
#     if not os.path.exists(local_audio_folder):
#         os.makedirs(local_audio_folder)
#
#     # 无限循环获取音频并播放
#     while True:
#         # 遍历远程服务器的文件夹
#         try:
#             client = create_ssh_client(remote_host, remote_port, remote_user, remote_password)
#             stdin, stdout, stderr = client.exec_command(f"ls {remote_audio_folder}")
#             remote_files = stdout.readlines()
#             client.close()
#
#             for file in remote_files:
#                 file = file.strip()
#                 if file.endswith('.wav'):
#                     remote_file_path = os.path.join(remote_audio_folder, file)
#                     local_file_path = os.path.join(local_audio_folder, file)
#
#                     # 下载音频文件
#                     scp_file_from_server(jump_host, jump_port, jump_user, jump_password,
#                                          remote_host, remote_port, remote_user, remote_password,
#                                          remote_file_path, local_file_path)
#
#                     # 播放下载的音频文件
#                     print(f"正在播放 {local_file_path}")
#                     playsound(local_file_path)
#                     time.sleep(1)  # 防止频繁下载，可以设置为适合的间隔时间
#         except Exception as e:
#             print(f"下载或播放时出错: {e}")
#
#         # 休眠一段时间后再检查新的文件
#         time.sleep(10)
#
# # 开始下载和播放音频
# download_and_play()




# # 从服务器下载音频
# import paramiko
# from paramiko import SSHClient, AutoAddPolicy
# from scp import SCPClient
#
#
# def create_ssh_client(server, port, user, password):
#     """连接到指定的服务器"""
#     client = paramiko.SSHClient()
#     client.load_system_host_keys()
#     client.set_missing_host_key_policy(AutoAddPolicy())
#     client.connect(server, port=port, username=user, password=password)
#     return client
#
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
# # 配置信息
# jump_host = '222.204.6.193'  # 跳板机IP地址
# jump_port = 8087  # 跳板机端口
# jump_user = 'ZZQ'  # 你的跳板机用户名
# jump_password = 'ZZQ@good114'  # 你的跳板机密码
#
# remote_host = '192.168.1.72'  # 目标服务器IP
# remote_port = 22  # 目标服务器端口
# remote_user = 'ZZQ'  # 你的目标服务器用户名
# remote_password = 'ZZQ@good114'  # 你的目标服务器密码
#
# local_directory_path = r'./'  # 你想保存文件的本地目录路径
# remote_directory_path = '/app/huaweiyun/sichuan/WAV16k/output/'  # 你想下载的远程目录路径
#
# scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
#                           remote_host, remote_port, remote_user, remote_password,
#                           local_directory_path, remote_directory_path)


# 从服务器上下载并且自动播放
import paramiko
from paramiko import AutoAddPolicy
from scp import SCPClient
import pygame  # 用于播放音频
import os
from playsound import playsound

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

# 主程序入口
if __name__ == "__main__":
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
    remote_directory_path = '/app/huaweiyun/sichuan/WAV16k/output/temp.wav'  # 远程目录路径

    # 创建本地目录
    if not os.path.exists(local_directory_path):
        os.makedirs(local_directory_path)

    # 从服务器下载文件
    scp_directory_from_server(jump_host, jump_port, jump_user, jump_password,
                              remote_host, remote_port, remote_user, remote_password,
                              local_directory_path, remote_directory_path)

    # 获取下载的文件列表
    audio_files = [f for f in os.listdir(local_directory_path) if f.endswith('.wav')]  # 修改为查找 .mp3 文件
    print(os.listdir(local_directory_path))
    print(audio_files)
    if audio_files:
        # 播放下载的第一个音频文件
        # first_audio_file = os.path.join(local_directory_path, audio_files[0])
        # print()
        print(f"正在播放文件: {audio_files}")
        playsound(r'./downloaded_audio/temp.wav')
    else:
        print("没有找到音频文件！")
