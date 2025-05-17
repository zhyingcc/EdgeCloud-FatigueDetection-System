import os
import numpy as np
import onnxruntime as ort
import itertools
import pyaudio
from omegaconf import OmegaConf
from python_speech_features import mfcc

# 设置音频流参数
RATE = 16000  # 采样率，16kHz
CHUNK_DURATION = 3  # 每次读取的音频时长（秒）
CHUNK = int(RATE * CHUNK_DURATION)  # 每次读取的数据量（帧数）

# 设置 ONNX 模型路径
onnx_model_path = "F:\\model_export.onnx"  # 请将此路径修改为您的 ONNX 模型路径

# 加载模型和配置
def load_infer_config():
    cfg = OmegaConf.create({
        'common_eval': {
            'path': onnx_model_path,
            'results_path': 'F:\\',
            'quiet': False
        }
    })
    return cfg

def load_model(cfg):
    print("加载 ONNX ASR 模型...")
    onnx_model_path = cfg.common_eval.path
    session = ort.InferenceSession(onnx_model_path)
    return session

# 使用 python_speech_features 提取 MFCC 特征
def extract_mfcc(audio_data, sr):
    # audio_data 需要是 1D 的 NumPy 数组，数据类型为 float32
    # 计算 MFCC 特征
    mfcc_features = mfcc(
        signal=audio_data,
        samplerate=sr,
        numcep=40,  # 返回的倒谱系数数量
        nfilt=40,  # 滤波器组的数量
        winlen=0.025,  # 窗口长度，25ms
        winstep=0.01,  # 窗口移位，10ms
        nfft=512,  # FFT 的大小
        appendEnergy=False  # 是否添加能量项
    )

    # 确保返回的特征是 float32 类型
    return mfcc_features.astype(np.float32)

# 实时音频推理
def infer_realtime(session, id2char):
    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    # 开始录音
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始实时音频推理...")

    try:
        while True:
            # 读取音频流
            data = stream.read(CHUNK)
            # 将数据转换为 numpy 数组
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            #audio_data = audio_data / 32768.0  # 将数据归一化到 [-1.0, 1.0]

            # 使用 python_speech_features 提取 MFCC 特征
            mfcc_features = extract_mfcc(audio_data, RATE)

            if mfcc_features.shape[0] == 0:
                continue  # 如果未能提取到特征，继续下一次循环
            print(mfcc_features)
            # 准备输入数据
            # 假设模型期望的输入形状为 (batch_size, sequence_length, feature_dim)
            input_data = mfcc_features[np.newaxis, :, :]  # 添加 batch 维度

            # 确保 input_data 是 float32 类型
            input_data = input_data.astype(np.float32)

            # 获取模型的输入和输出名称
            input_name = session.get_inputs()[0].name
            output_name = session.get_outputs()[0].name

            # 运行推理
            outputs = session.run([output_name], {input_name: input_data})

            # 处理输出
            # 假设模型输出的是 logits，需要进行后处理，例如 CTC 解码
            logits = outputs[0]  # 输出的 logits，形状为 (1, time_steps, num_classes)
            if logits.shape[0] == 1:
                logits = np.squeeze(logits, axis=0)  # 仅当 batch 维度为 1 时才进行 squeeze

            # 执行 CTC 解码
            predicted_ids = np.argmax(logits, axis=-1)  # 获得每个时间步的最大概率类别
            # 去除重复的预测和空白符号（索引为 0），得到最终的预测序列
            predicted_ids = [k for k, _ in itertools.groupby(predicted_ids) if k != 0]
            predicted_text = ''.join([id2char.get(id, '') for id in predicted_ids])

            print(f"推理结果: {predicted_text}")

    except KeyboardInterrupt:
        print("结束推理。")

    # 关闭流
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    cfg = load_infer_config()
    session = load_model(cfg)

    # 加载 id2char 映射表
    id2char = {}
    vocab_path = 'F:\\vocab.json'  # 修改为您的词汇表路径
    with open(vocab_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            char = line.strip()
            id2char[idx] = char

    infer_realtime(session, id2char)


# import os
# import sys
# import pyaudio
# import numpy as np
# import onnxruntime as ort
# import itertools
# import time
# from omegaconf import OmegaConf
# import librosa
#
# # 设置音频流参数
# RATE = 16000  # 采样率，16kHz
# CHUNK_DURATION = 0.5  # 每次读取的音频时长（秒）
# CHUNK = int(RATE * CHUNK_DURATION)  # 每次读取的数据量（帧数）
#
# # 设置 ONNX 模型路径
# onnx_model_path = "F:\\model_export.onnx"  # 请将此路径修改为您的 ONNX 模型路径
#
#
# # 加载模型和配置
# def load_infer_config():
#     cfg = OmegaConf.create({
#         'common_eval': {
#             'path': onnx_model_path,
#             'results_path': 'F:\\',
#             'quiet': False
#         }
#     })
#     return cfg
#
#
# def load_model(cfg):
#     print("加载 ONNX ASR 模型...")
#     onnx_model_path = cfg.common_eval.path
#     session = ort.InferenceSession(onnx_model_path)
#     return session
#
#
# # 实时音频推理
# def infer_realtime(session, id2char):
#     # 初始化 PyAudio
#     p = pyaudio.PyAudio()
#
#     # 开始录音
#     stream = p.open(format=pyaudio.paInt16,
#                     channels=1,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)
#
#     print("开始实时音频推理...")
#
#     try:
#         while True:
#             # 读取音频流
#             data = stream.read(CHUNK)
#             # 将数据转换为 numpy 数组
#             audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
#             audio_data = audio_data / 32768.0  # 将数据归一化到 [-1.0, 1.0]
#
#             # 提取 MFCC 特征
#             # 参数需要根据您的模型训练时的配置进行调整
#             mfcc_features = librosa.feature.mfcc(
#                 y=audio_data,
#                 sr=RATE,
#                 n_mfcc=40,  # MFCC 特征的维度
#                 n_fft=int(0.025 * RATE),  # 窗口长度，25ms
#                 hop_length=int(0.01 * RATE),  # 窗口移位，10ms
#                 win_length=int(0.025 * RATE),  # 窗口长度，25ms
#                 window='hamming',
#                 center=False,
#                 htk=True,
#             ).T  # 转置以获得形状 (time_steps, feature_dim)
#
#             if mfcc_features.shape[0] == 0:
#                 continue  # 如果未能提取到特征，继续下一次循环
#
#             # 准备输入数据
#             # 假设模型期望的输入形状为 (batch_size, sequence_length, feature_dim)
#             input_data = mfcc_features[np.newaxis, :, :]  # 添加 batch 维度
#
#             # 获取模型的输入和输出名称
#             input_name = session.get_inputs()[0].name
#             output_name = session.get_outputs()[0].name
#
#             # 运行推理
#             outputs = session.run([output_name], {input_name: input_data})
#
#             # 处理输出
#             # 假设模型输出的是 logits，需要进行后处理，例如 CTC 解码
#             logits = outputs[0]  # 输出的 logits，形状为 (1, time_steps, num_classes)
#             if logits.shape[0] == 1:
#                 logits = np.squeeze(logits, axis=0)  # 仅当 batch 维度为 1 时才进行 squeeze
#             #logits = np.squeeze(logits, axis=0)  # 去除 batch 维度
#
#             # 执行 CTC 解码
#             predicted_ids = np.argmax(logits, axis=-1)  # 获得每个时间步的最大概率类别
#             # 去除重复的预测和空白符号（索引为 0），得到最终的预测序列
#             predicted_ids = [k for k, _ in itertools.groupby(predicted_ids) if k != 0]
#             predicted_text = ''.join([id2char.get(id, '') for id in predicted_ids])
#
#             print(f"推理结果: {predicted_text}")
#
#     except KeyboardInterrupt:
#         print("结束推理。")
#
#     # 关闭流
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#
#
# if __name__ == "__main__":
#     cfg = load_infer_config()
#     session = load_model(cfg)
#
#     # 加载 id2char 映射表
#     # 需要根据您的模型实际的词汇表进行加载
#     # 假设我们有一个名为 'vocab.txt' 的文件，每行是一个字符
#     id2char = {}
#     vocab_path = 'F:\\vocab.json'  # 修改为您的词汇表路径
#     with open(vocab_path, 'r', encoding='utf-8') as f:
#         for idx, line in enumerate(f):
#             char = line.strip()
#             id2char[idx] = char
#
#     infer_realtime(session, id2char)

import socket
import pyaudio
from sshtunnel import SSHTunnelForwarder

def stream_audio_to_server_through_ssh():
    # SSH 连接信息
    jump_host = '222.204.6.193'
    jump_user = 'YZH'
    jump_password = 'YZH@good114'  # 使用密码认证
    jump_port = 8087

    # 远程服务器的 SSH 连接信息
    remote_server_ip = '192.168.1.72'
    remote_port = 22  # 远程服务器的端口


    # 音频流信息
    chunk = 1024  # 每次读取的数据块大小
    format = pyaudio.paInt16  # 16-bit int
    channels = 1
    rate = 16000  # 16kHz

    # 使用 sshtunnel 创建 SSH 隧道
    with SSHTunnelForwarder(
        (jump_host, jump_port),
        ssh_username=jump_user,
        ssh_password=jump_password,
        remote_bind_address=(remote_server_ip, remote_port),
        local_bind_address=('0.0.0.0', 4000)  # 本地绑定端口
    ) as tunnel:
        print("SSH 隧道已建立，开始连接服务器...")

        # 连接到本地转发的端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', tunnel.local_bind_port))

        # 打开麦克风流
        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print("开始传输音频数据到远程服务器...")

        try:
            while True:
                data = stream.read(chunk)
                sock.sendall(data)  # 通过隧道传输音频数据
        except KeyboardInterrupt:
            print("结束传输")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            sock.close()

if __name__ == "__main__":
    stream_audio_to_server_through_ssh()


#
# import paramiko
# import socket
# import pyaudio
#
# def stream_audio_to_server_through_ssh():
#     # SSH 连接信息
#     jump_host = '222.204.6.193'
#     jump_user = 'YZH'
#     jump_password = 'YZH@good114'  # 使用密码认证
#     jump_port = 8087
#
#     # 远程服务器的 SSH 连接信息
#     remote_server_ip = '192.168.1.72'
#     remote_user = 'ZZQ'
#     remote_password = 'ZZQ@good114'
#     remote_port = 4000  # 远程服务器的端口
#
#     # 音频流信息
#     chunk = 1  # 更小的数据块
#     format = pyaudio.paInt16  # 16-bit int
#     channels = 1
#     rate = 16000  # 16kHz
#
#     # 连接跳板机并转发端口
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     # 使用密码验证连接跳板机
#     ssh.connect(jump_host, port=jump_port, username=jump_user, password=jump_password)
#
#     # 启用 keepalive，防止连接超时
#     ssh.get_transport().set_keepalive(30)
#
#     # 创建 SSH 隧道，将本地端口映射到远程服务器
#     transport = ssh.get_transport()
#     local_addr = ('localhost', 4000)  # 本地端口，用于音频传输
#     remote_addr = (remote_server_ip, remote_port)  # 远程服务器 IP 和端口
#
#     try:
#         tunnel = transport.open_channel('direct-tcpip', remote_addr, local_addr)
#         if tunnel is None or not tunnel.active:
#             print("隧道创建失败")
#             return
#     except paramiko.SSHException as e:
#         print(f"隧道创建失败: {e}")
#         return
#
#     # 打开麦克风流
#     p = pyaudio.PyAudio()
#     stream = p.open(format=format,
#                     channels=channels,
#                     rate=rate,
#                     input=True,
#                     frames_per_buffer=chunk)
#
#     print("开始传输音频数据到远程服务器...")
#
#     try:
#         while True:
#             data = stream.read(chunk)
#             try:
#                 tunnel.send(data)  # 通过隧道传输音频数据
#             except (socket.error, EOFError) as e:
#                 print(f"数据发送失败，连接已中断: {e}")
#                 break
#     except KeyboardInterrupt:
#         print("结束传输")
#     finally:
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
#         if tunnel is not None:
#             tunnel.close()
#         ssh.close()
#
#
# if __name__ == "__main__":
#     stream_audio_to_server_through_ssh()
#
#
