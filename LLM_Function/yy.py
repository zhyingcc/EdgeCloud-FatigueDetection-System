# # coding: utf-8

# import os
# import base64
# import pygame  # 用于播放MP3
# from huaweicloudsdkcore.auth.credentials import BasicCredentials
# from huaweicloudsdksis.v1.region.sis_region import SisRegion
# from huaweicloudsdkcore.exceptions import exceptions
# from huaweicloudsdksis.v1 import *
# from playsound import playsound

# def base64_to_file(base64_string, file_path):
#     # 将base64字符串解码为字节流
#     decoded_bytes = base64.b64decode(base64_string)
#     # 将字节流写入文件
#     with open(file_path, 'wb') as file:
#         file.write(decoded_bytes)

# def play_mp3(file_path):
#     # 初始化pygame的音频模块
#     pygame.mixer.init()
#     # 加载MP3文件
#     pygame.mixer.music.load(file_path)
#     # 播放MP3文件
#     pygame.mixer.music.play()
#     # 保持程序运行直到播放结束
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)

# def getaud(str):
#     # 初始化pygame音频模块
#     pygame.mixer.init()
#     # 加载MP3文件

#     # 使用环境变量或其他安全方式存储AK和SK
#     ak = "P7TLTHMIJ3PRHGHI6S2I"
#     sk = "5W9C0NaUaYWp0YzA5TDCXj0tm8LrSclwMQfuwGpU"

#     credentials = BasicCredentials(ak, sk)

#     client = SisClient.new_builder() \
#         .with_credentials(credentials) \
#         .with_region(SisRegion.value_of("cn-east-3")) \
#         .build()

#     try:
#         request = RunTtsRequest()
#         configbody = TtsConfig(
#             audio_format="wav",
#         )
#         request.body = PostCustomTTSReq(
#             text=str, # 替换为你想要的文本
#             config = configbody
#         )
#         response = client.run_tts(request)
#         print(response)
#         mp3_file = "temp.wav"
#         base64_to_file(response.result.data, mp3_file)
#         playsound("temp.wav")
#         # 播放生成的MP3文件
#         # play_mp3(mp3_file)
#         # pygame.mixer.music.load('./temp.mp3')
#         # 播放MP3文件
#         # pygame.mixer.music.play()

#     except exceptions.ClientRequestException as e:
#         print(e.status_code)
#         print(e.request_id)
#         print(e.error_code)
#         print(e.error_msg)


# # coding: utf-8

# import os
# import base64
# import pygame  # 用于播放MP3
# from huaweicloudsdkcore.auth.credentials import BasicCredentials
# from huaweicloudsdksis.v1.region.sis_region import SisRegion
# from huaweicloudsdkcore.exceptions import exceptions
# from huaweicloudsdksis.v1 import *

# def base64_to_file(base64_string, file_path):
#     # 将base64字符串解码为字节流
#     decoded_bytes = base64.b64decode(base64_string)
#     # 将字节流写入文件
#     with open(file_path, 'wb') as file:
#         file.write(decoded_bytes)

# def play_mp3(file_path):
#     # 初始化pygame的音频模块
#     pygame.mixer.init()
#     # 加载音频文件
#     pygame.mixer.music.load(file_path)
#     # 播放音频文件
#     pygame.mixer.music.play()
#     # 保持程序运行直到播放结束
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)

# def getaud(str):
#     # 使用环境变量或其他安全方式存储AK和SK
#     ak = "P7TLTHMIJ3PRHGHI6S2I"
#     sk = "5W9C0NaUaYWp0YzA5TDCXj0tm8LrSclwMQfuwGpU"

#     credentials = BasicCredentials(ak, sk)

#     client = SisClient.new_builder() \
#         .with_credentials(credentials) \
#         .with_region(SisRegion.value_of("cn-east-3")) \
#         .build()

#     try:
#         request = RunTtsRequest()
#         configbody = TtsConfig(
#             audio_format="wav",
#         )
#         request.body = PostCustomTTSReq(
#             text=str,  # 替换为你想要的文本
#             configfile(response.result.data, wav_file)
#         # 使用 pygame 播放生成的音频
#         play_mp3(wav_file)

#     except exceptions.ClientRequestException as e:
#         print(e.status_code)
#         print(e.request_id)
#         print(e.error_code)
#         print(e.error_msg)=configbody
#         )
#         response = client.run_tts(request)
#         print(response)
#         wav_file = "temp.wav"
#         base64_to_

# coding: utf-8
import os
import base64
import pygame
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdksis.v1.region.sis_region import SisRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdksis.v1 import *

# 初始化全局计数器
counter = 0

def base64_to_file(base64_string, file_path):
    decoded_bytes = base64.b64decode(base64_string)
    with open(file_path, 'wb') as file:
        file.write(decoded_bytes)

def play_mp3(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def getaud(str):
    global counter
    ak = "P7TLTHMIJ3PRHGHI6S2I"
    sk = "5W9C0NaUaYWp0YzA5TDCXj0tm8LrSclwMQfuwGpU"

    credentials = BasicCredentials(ak, sk)
    client = SisClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(SisRegion.value_of("cn-east-3")) \
        .build()

    try:
        request = RunTtsRequest()
        configbody = TtsConfig(audio_format="wav")
        request.body = PostCustomTTSReq(text=str, config=configbody)
        response = client.run_tts(request)
        print(response)

        # 生成带序号的文件名
        counter += 1
        wav_file = f"response_{counter}.wav"
        
        base64_to_file(response.result.data, wav_file)
        print(f"Audio saved as: {wav_file}")
        play_mp3(wav_file)

    except exceptions.ClientRequestException as e:
        print(e.status_code, e.request_id, e.error_code, e.error_msg)



