# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import io
import json
import queue
import sys
import threading
import time
import traceback

import cv2
import requests
import _flowunit as modelbox
from etc.flowunit.dy.our_videoReader import VideoReader
from onnx_detect import ONNX_engine

api_url = "https://015c2ea02afc4cf0afbd3935a760adab.apig.cn-north-4.huaweicloudapis.com/v1/infers/d8700113-5c4a-4ee7-b987-18e87ea6062b"
token = "MIIN2QYJKoZIhvcNAQcCoIINyjCCDcYCAQExDTALBglghkgBZQMEAgEwggvrBgkqhkiG9w0BBwGgggvcBIIL2HsidG9rZW4iOnsiZXhwaXJlc19hdCI6IjIwMjQtMTItMDNUMDc6MTA6MzAuMTcwMDAwWiIsIm1ldGhvZHMiOlsicGFzc3dvcmQiXSwiY2F0YWxvZyI6W10sInJvbGVzIjpbeyJuYW1lIjoidGVfYWRtaW4iLCJpZCI6IjAifSx7Im5hbWUiOiJ0ZV9hZ2VuY3kiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3JlcF9hY2NlbGVyYXRpb24iLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lY3NfZGlza0FjYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rzc19tb250aCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWVwX2FyY2hpdmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLXNvdXRoLTRjIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZGVjX21vbnRoX3VzZXIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jYnJfc2VsbG91dCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vbGRfcmVvdXJjZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Bhbmd1IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfd2VsaW5rYnJpZGdlX2VuZHBvaW50X2J1eSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nicl9maWxlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZG1zLXJvY2tldG1xNS1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Rtcy1rYWZrYTMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lZGdlc2VjX29idCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29ic19kZWNfbW9udGgiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF91bmlidXkiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9pZG1lX21ibV9mb3VuZGF0aW9uIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2M2YSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX211bHRpX2JpbmQiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9zbW5fY2FsbG5vdGlmeSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTNkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfY3Nic19wcm9ncmVzc2JhciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Nlc19yZXNvdXJjZWdyb3VwX3RhZyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2FjNyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19yZXR5cGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9rb29tYXAiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9ldnNfZXNzZDIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9kbXMtYW1xcC1iYXNpYyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2V2c19wb29sX2NhIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1zb3V0aHdlc3QtMmIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9od2NwaCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19vZmZsaW5lX2Rpc2tfNCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h3ZGV2IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfc21uX3dlbGlua3JlZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2h2X3ZlbmRvciIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfY24tbm9ydGgtNGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2NuLW5vcnRoLTRkIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfZWNzX2hlY3NfeCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19hYzciLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9lcHMiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9jc2JzX3Jlc3RvcmVfYWxsIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9jbi1ub3J0aC00ZiIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX29wX2dhdGVkX3JvdW5kdGFibGUiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9ldnNfZXh0IiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfcGZzX2RlZXBfYXJjaGl2ZSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfYXAtc291dGhlYXN0LTFlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9ydS1tb3Njb3ctMWIiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9hX2FwLXNvdXRoZWFzdC0xZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FwcHN0YWdlIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfYV9hcC1zb3V0aGVhc3QtMWYiLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9zbW5fYXBwbGljYXRpb24iLCJpZCI6IjAifSx7Im5hbWUiOiJvcF9nYXRlZF9ldnNfY29sZCIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX3Jkc19jYSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19ncHVfZzVyIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfb3BfZ2F0ZWRfbWVzc2FnZW92ZXI1ZyIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2Vjc19yaSIsImlkIjoiMCJ9LHsibmFtZSI6Im9wX2dhdGVkX2FfcnUtbm9ydGh3ZXN0LTJjIiwiaWQiOiIwIn0seyJuYW1lIjoib3BfZ2F0ZWRfaWVmX3BsYXRpbnVtIiwiaWQiOiIwIn1dLCJwcm9qZWN0Ijp7ImRvbWFpbiI6eyJuYW1lIjoiaGlkX2ViMmdueHM1NXlxZG5uXyIsImlkIjoiNzg0MzkyMmFlMTJiNGFmYWExMTM1NmE1YzJkY2YwNGUifSwibmFtZSI6ImNuLW5vcnRoLTQiLCJpZCI6Ijg3YjFiNjIwN2IyOTQ1MTNhYWE2YTYwNzE4YzZkNjY4In0sImlzc3VlZF9hdCI6IjIwMjQtMTItMDJUMDc6MTA6MzAuMTcwMDAwWiIsInVzZXIiOnsiZG9tYWluIjp7Im5hbWUiOiJoaWRfZWIyZ254czU1eXFkbm5fIiwiaWQiOiI3ODQzOTIyYWUxMmI0YWZhYTExMzU2YTVjMmRjZjA0ZSJ9LCJuYW1lIjoiQ3pxIiwicGFzc3dvcmRfZXhwaXJlc19hdCI6IiIsImlkIjoiYjdmOTVkNWE4Y2VkNGFhOGE1YTliYWUyODgwYTFmNDIifX19MYIBwTCCAb0CAQEwgZcwgYkxCzAJBgNVBAYTAkNOMRIwEAYDVQQIDAlHdWFuZ0RvbmcxETAPBgNVBAcMCFNoZW5aaGVuMS4wLAYDVQQKDCVIdWF3ZWkgU29mdHdhcmUgVGVjaG5vbG9naWVzIENvLiwgTHRkMQ4wDAYDVQQLDAVDbG91ZDETMBEGA1UEAwwKY2EuaWFtLnBraQIJANyzK10QYWoQMAsGCWCGSAFlAwQCATANBgkqhkiG9w0BAQEFAASCAQBEuR-hWE-JjKet28B0FPKi25n7Ta1YgSVgdjyQxBUuOhI61WmAynYI8erzZH35tgszTmyPoBXv94q4WjxtRpmXpG3NdSpeUAUbqrFGkbd8A8sDET+gB7TwhsQp2WmFNjuPUjbOHiNBkB2yWViPNLk9FLDdFzLjQoIsJ8pFQvgkfRMHQ19WMIUC9R8jmRnZShDwFuxm0OK1RXbngdUFWUF8VSy4ulUbYPhXC+xzHaMBWQv6nJ56s8vY-Id59HWBTOYi6nJds8PWeQ7zuTtENpyY+2393g2PyRPSAc9s3bTeZMc843Nk7FCyIr9xgnMtyMBcS0TE9EKCplhpjUUfYxzD"

class dyFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        self.onnx_model = ONNX_engine(weights_path='etc/flowunit/dy/v4_c7_320.onnx', size=320)
        self.capture='data/video/night_man_001_5.mp4'
        

        self.reader = VideoReader(self.capture)   
        print(self.reader.ret)
        if self.reader.ret == False:
            return self.result
        self.height, self.width, self.fps, self.video_totalFrameNum = self.reader.get_capInfo()   # 初始化，获取视频信息
        self.frameNum_3s = int(self.fps * 3)                    # 3s的帧数
        self.chushai_skip_step = int(self.fps)                                      # 固定帧数间隔

        
        self.readall_frame_queue = queue.Queue()
        readall_thread = threading.Thread(target=self.readall_frame_worker, args=(1, ))    # 初始化，创建一个子线程用于取帧，异步IO
        readall_thread.daemon = True     # 守护线程, 随进程结束而结束
        readall_thread.start()

        self.frame_list = []
        self.frame_list.append([])
        frame = self.readall_frame_queue.get()
        while frame is not None:
            self.frame_list.append(frame)
            frame = self.readall_frame_queue.get()
        print(len(self.frame_list))
        readall_thread.join()

        self.reset_CountValue_between_videos()
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        
        # Process the data
        in_data = data_context.input("in_1")
        out_data = data_context.output("out_1")

        # 保存bbox的dict
        self.bbox_dict = {}
        self.detect_frame_set = set()
        self.chushai_frame_set = set()

        self.infer_time_start = time.time()

        # 初筛
        chushai_maybe_list = self.chushai_infer()
        self.skip_step = 1
        detect_step = 3

        # 创建一个显示线程
        self.show_frame_queue = queue.Queue()
        show_thread = threading.Thread(target=self.show_frame_worker, args=(self.fps, ))    # 初始化，创建一个子线程用于取帧，异步IO
        show_thread.start()
        
        
        for now_frame_id in range(1, len(self.frame_list)):
            self.nowFrameIdx = now_frame_id
            self.reset_CountValue_between_frames()
            # 判断这一帧是否在初筛后的列表中
            is_maybe_start, maybe_start, maybe_end = self.frameid_is_maybe_start(now_frame_id, chushai_maybe_list)
            # 在可能列表里面
            if is_maybe_start:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用MP4V编解码器
                video = cv2.VideoWriter("temp.mp4", fourcc, self.fps, (int(self.width), int(self.height)))
                for data_id in range(maybe_start, maybe_end + 1, detect_step):
                    video.write(self.frame_list[data_id]) 
                video.release()

                # Send request.
                headers = {'X-Auth-Token': token}
                with open('temp.mp4', 'rb') as f:
                    files = {'input_video':  f}
                    start = time.time()
                    print('\nSend request')
                    resp = requests.post(api_url, headers=headers, files=files)
                print(f'status_code: {resp.status_code}')
                print(maybe_start, maybe_end, maybe_end - maybe_start, 'frame')
                print(f'time cost: {round(time.time()-start, 2)} s')
                result_dict = json.loads(resp.text) 
                print('head', result_dict['result'][0],'\n')
                i = 0
                for data_id in range(maybe_start, maybe_end + 1, detect_step):
                    self.bbox_dict[data_id] = result_dict['result'][i]
                    self.detect_frame_set.add(data_id)
                    i += 1

                is_maybe_start = False
            
            # 检查当前帧在集合中
            if now_frame_id in self.detect_frame_set:
                if self.frameidx_in_maybe_list(now_frame_id,chushai_maybe_list):
                    self.skip_step = detect_step
                else:
                    self.skip_step = 1
                    
                bbox = self.bbox_dict[now_frame_id]
                
                # 本地蓝色
                if now_frame_id in self.chushai_frame_set:
                    tempframe = self.deal_bbox_beidi_blue(bbox,self.frame_list[now_frame_id])
                # 云端绿色
                else:
                    tempframe = self.deal_bbox(bbox,self.frame_list[now_frame_id])
                self.judge_action()
                tempframe = self.deal_action_count(tempframe)
                self.show_frame_queue.put(tempframe)
            else:
                self.show_frame_queue.put(self.frame_list[now_frame_id])

            
        # 所有都入队后，put None
        self.show_frame_queue.put(None)
        duration = int((time.time() - self.infer_time_start) * 1000)
        self.result['result']['duration'] = duration
        self.result["result"]["drowsy"] = self.temp_list
        print(self.result,'\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        show_thread.join()

        for buffer in in_data:
            result = 'Done'
            add_buffer = modelbox.Buffer(self.get_bind_device(), result)
            out_data.push_back(add_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        # Close the flowunit
        return modelbox.Status()

    def data_pre(self, data_context):
        # Before streaming data starts
        return modelbox.Status()

    def data_post(self, data_context):
        # After streaming data ends
        return modelbox.Status()

    def data_group_pre(self, data_context):
        # Before all streaming data starts
        return modelbox.Status()

    def data_group_post(self, data_context):
        # After all streaming data ends
        return modelbox.Status()
    
    def show_frame_worker(self,fps):
        i = 1
        frame = self.show_frame_queue.get()
        # time.sleep(10)
        # 实时显示
        while frame is not None:
            cv2.imshow('Video Frame', frame)
            # if cv2.waitKey(int(1000.0 * 1/fps)) & 0xFF == 27 :
            if cv2.waitKey(1) & 0xFF == 27 :
                print('waitkey')
            time.sleep(1/fps)
            # print(f'show image {i}')
            i += 1 
            frame = self.show_frame_queue.get()
        # 结束
        cv2.destroyAllWindows()

        # 保存成视频
        # video_out_path = 'output.mp4'
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # writer = cv2.VideoWriter(video_out_path, fourcc, 24, (int(self.width),int(self.height)),True)
        # while frame is not None:
        #     writer.write(frame)	# 读取图片后一帧帧写入到视频中
        #     print(f'write image {i}')
        #     i += 1 
        #     frame = self.show_frame_queue.get()
        # writer.release()


        # # 读取刚刚保存的视频
        # # 打开视频文件
        # cap = cv2.VideoCapture(video_out_path)

        # # 检查视频是否成功打开
        # if not cap.isOpened():
        #     print("无法打开视频文件")
        #     exit()

        # # 获取视频的帧率
        # fps = int(cap.get(cv2.CAP_PROP_FPS))

        # # 创建一个窗口来显示视频
        # cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

        # while True:
        #     # 从视频中读取一帧
        #     ret, frame = cap.read()

        #     # 如果视频读取结束，退出循环
        #     if not ret:
        #         break

        #     # 显示当前帧
        #     cv2.imshow('Video', frame)

        #     # 按照视频的帧率等待一定时间，以模拟正常速率播放
        #     key = cv2.waitKey(1000 // fps)

        #     # 如果按下 'q' 键，退出循环
        #     if key == ord('q'):
        #         break

        # # 释放视频对象和关闭窗口
        # cap.release()
        # cv2.destroyAllWindows()
        return 
    
    def chushai_infer(self):
        normal_start_pos = 1
        chushai_maybe_list = []
        # 2. 检测
        for now_frame_id in range(1, len(self.frame_list), int(self.fps)):
            self.reset_CountValue_between_frames()
            tempframe = self.frame_list[now_frame_id][:, int(self.width * 0.33): int(self.width), :]
            # 2.1 检测
            temp_bbox =  self.chushai_detect(tempframe)      
            self.bbox_dict[now_frame_id] = temp_bbox   
            self.detect_frame_set.add(now_frame_id)
            self.chushai_frame_set.add(now_frame_id)

            # 2.2 判断这一帧是否是正常行为
            self.judge_action()
            now_frame_is_normal = self.chushai_judge_action_is_normal()

            # 2.3 正常: 找到上一个正常的位置，看一下够不够三秒，够三秒把起止的位置记录下来 maybe_list[[start pos,end pos]]
            if now_frame_is_normal:
                # 超过三秒需要记录, 符合要求的start和end放入到list中[[start1, end1], [start2, end2]]
                if now_frame_id - normal_start_pos >= int(self.fps) * 3 :
                    chushai_maybe_list.append([normal_start_pos, now_frame_id])
                    # chushai_maybe_list.append([self.getTimestamp_idx(normal_start_pos), self.getTimestamp_idx(self.nowFrameIdx)])
                # 更新start
                normal_start_pos = now_frame_id
        
        return chushai_maybe_list
    
    # 模型1，图像检测，检测出现的行为
    def chushai_detect(self, frame):
        # bbox是清洗过的数据    # bbox->[class ,[center-x, center-y, width, height]]
        bbox = self.onnx_model.preprocess(frame)

        if len(bbox) > 0:
            for box in bbox:
                box[1][0] = round(box[1][0] + self.width * 0.33,1)
                if box[0] == 0:                     # 人脸
                    self.model1_face = True         # 这个值只会在不同视频切换重置为False。相当于一个视频检测到一次主驾驶员，就一直为true
                    # print('face', end='')
                elif box[0] == 1:                   # 手机
                    self.model1_usePhone = True
                    # print('use phone', end='')
                elif box[0] == 2:                   # openeye
                    self.model1_openEye += 1
                    self.model1_eyeNum += 1
                    # print('open eye', end='')
                elif box[0] == 3:                   # closedeye
                    self.model1_closeEye += 1
                    self.model1_eyeNum += 1
                    # print('close eye', end='')
                elif box[0] == 4:                   # yawn打哈欠
                    self.model1_openMouth = True
                    self.model1_mouthNum += 1
                    # print('open mouth', end='')
                elif box[0] == 5:                   # noyawn 不打哈欠、闭嘴
                    self.model1_closeMouth = True
                    self.model1_mouthNum += 1
                    # print('close mouth', end='')
                elif box[0] == 6:                   # 转头
                    self.model1_face = True
                    self.model1_turned = True
                    # print('turn', end='')
                elif box[0] == 7:                   # 低头，不识别低头的模型也不影响，不会出现7，该条件判断不成立
                    self.model1_face = True
                    self.model1_turnedDown = True
                    # print('down', end='')
                
                # print(box)
        else:                                       # 没有人脸
            self.model1_turned = True
            self.model1_turnedDown = True
            print('Model 1 No Face')
        return bbox
    

    def deal_bbox(self, bbox, frame):
        if len(bbox) > 0:           # 根据清洗后的bbox，得到驾驶员的行为和位置
            for box in bbox:
                cx = box[1][0]
                cy = box[1][1]
                w = box[1][2]
                h = box[1][3]
                x = cx - w/2
                y = cy - h/2

                # 点的坐标要是整数
                pt1 = (int(x), int(y))
                pt2 = (int(x + w), int(y + h))

                # OpenCV中通道顺序是蓝色、绿色、红色（BGR）
                green = (0, 255, 0)
                red = (0, 0, 255)
                thickness = 2

                # print(box)
                if box[0] == 0:                     # 人脸
                    self.model1_face = True         # 这个值只会在不同视频切换重置为False。相当于一个视频检测到一次主驾驶员，就一直为true
                    # print('人脸')
                    cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)

                elif box[0] == 1:                   # 手机
                    self.model1_usePhone = True
                    # print('手机')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 2:                   # openeye
                    self.model1_openEye += 1
                    self.model1_eyeNum += 1
                    # print('睁眼')
                    cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 3:                   # closedeye
                    self.model1_closeEye += 1
                    self.model1_eyeNum += 1
                    # print('闭眼')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 4:                   # yawn打哈欠
                    self.model1_openMouth = True
                    self.model1_mouthNum += 1
                    # print('打哈欠')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 5:                   # noyawn 不打哈欠、闭嘴
                    self.model1_closeMouth = True
                    self.model1_mouthNum += 1
                    # print('闭嘴')
                    cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 6:                   # 转头
                    self.model1_face = True
                    self.model1_turned = True
                    # print('转头')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 7:                   # 低头，不识别低头的模型也不影响，不会出现7，该条件判断不成立
                    self.model1_face = True
                    self.model1_turnedDown = True
                    # print('低头')
        else:                                       # 没有人脸
            self.model1_turned = True
            self.model1_turnedDown = True
            print('Model 1 No Face')

        return frame

    def deal_bbox_beidi_blue(self, bbox, frame):
        if len(bbox) > 0:           # 根据清洗后的bbox，得到驾驶员的行为和位置
            for box in bbox:
                cx = box[1][0]
                cy = box[1][1]
                w = box[1][2]
                h = box[1][3]
                x = cx - w/2
                y = cy - h/2

                # 点的坐标要是整数
                pt1 = (int(x), int(y))
                pt2 = (int(x + w), int(y + h))

                # OpenCV中通道顺序是蓝色、绿色、红色（BGR）
                blue = (255, 0, 0)
                red = (0, 0, 255)
                thickness = 2

                # print(box)
                if box[0] == 0:                     # 人脸
                    self.model1_face = True         # 这个值只会在不同视频切换重置为False。相当于一个视频检测到一次主驾驶员，就一直为true
                    # print('人脸')
                    cv2.rectangle(frame, pt1, pt2, blue, thickness,lineType=cv2.LINE_AA)

                elif box[0] == 1:                   # 手机
                    self.model1_usePhone = True
                    # print('手机')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 2:                   # openeye
                    self.model1_openEye += 1
                    self.model1_eyeNum += 1
                    # print('睁眼')
                    cv2.rectangle(frame, pt1, pt2, blue, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 3:                   # closedeye
                    self.model1_closeEye += 1
                    self.model1_eyeNum += 1
                    # print('闭眼')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 4:                   # yawn打哈欠
                    self.model1_openMouth = True
                    self.model1_mouthNum += 1
                    # print('打哈欠')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 5:                   # noyawn 不打哈欠、闭嘴
                    self.model1_closeMouth = True
                    self.model1_mouthNum += 1
                    # print('闭嘴')
                    cv2.rectangle(frame, pt1, pt2, blue, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 6:                   # 转头
                    self.model1_face = True
                    self.model1_turned = True
                    # print('转头')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 7:                   # 低头，不识别低头的模型也不影响，不会出现7，该条件判断不成立
                    self.model1_face = True
                    self.model1_turnedDown = True
                    # print('低头')
        else:                                       # 没有人脸
            self.model1_turned = True
            self.model1_turnedDown = True
            print('Model 1 No Face')

        return frame
     
    
    def infer_one_frame(self, frame):
        # 主驾驶位剪裁
        sub_frame = frame[:, int(self.width * 0.33): int(self.width), :]
        # bbox->[class ,[center-x, center-y, width, height]] ，bbox是清洗过的数据
        bbox = self.onnx_model.preprocess(sub_frame)
        if len(bbox) > 0:           # 根据清洗后的bbox，得到驾驶员的行为和位置
            for box in bbox:

                original_cx, original_cy, original_w, original_h = self.sub2original(box[1][0], box[1][1], box[1][2], box[1][3], self.width)
                x = original_cx - original_w/2
                y = original_cy - original_h/2

                # 点的坐标要是整数
                pt1 = (int(x), int(y))
                pt2 = (int(x + original_w), int(y + original_h))

                # OpenCV中通道顺序是蓝色、绿色、红色（BGR）
                green = (0, 255, 0)
                red = (0, 0, 255)
                thickness = 2

                # print(box)
                if box[0] == 0:                     # 人脸
                    self.model1_face = True         # 这个值只会在不同视频切换重置为False。相当于一个视频检测到一次主驾驶员，就一直为true
                    # print('人脸')
                    cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)

                elif box[0] == 1:                   # 手机
                    self.model1_usePhone = True
                    # print('手机')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 2:                   # openeye
                    self.model1_openEye += 1
                    self.model1_eyeNum += 1
                    # print('睁眼')
                    # cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 3:                   # closedeye
                    self.model1_closeEye += 1
                    self.model1_eyeNum += 1
                    # print('闭眼')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 4:                   # yawn打哈欠
                    self.model1_openMouth = True
                    self.model1_mouthNum += 1
                    # print('打哈欠')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 5:                   # noyawn 不打哈欠、闭嘴
                    self.model1_closeMouth = True
                    self.model1_mouthNum += 1
                    # print('闭嘴')
                    # cv2.rectangle(frame, pt1, pt2, green, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 6:                   # 转头
                    self.model1_face = True
                    self.model1_turned = True
                    # print('转头')
                    cv2.rectangle(frame, pt1, pt2, red, thickness,lineType=cv2.LINE_AA)
                elif box[0] == 7:                   # 低头，不识别低头的模型也不影响，不会出现7，该条件判断不成立
                    self.model1_face = True
                    self.model1_turnedDown = True
                    # print('低头')
        else:                                       # 没有人脸
            self.model1_turned = True
            self.model1_turnedDown = True
            print('Model 1 No Face')

        # 业务处理：增加画位置框的相关操作
        return frame
    
    def sub2original(self,sub_cx,sub_cy,sub_w,sub_h,original_width):
        original_cx = round(sub_cx + original_width * 0.33,1)
        original_cy = sub_cy
        original_w = sub_w
        original_h = sub_h
        return original_cx, original_cy, original_w, original_h

    def judge_action(self):         # 0602 ，1111，在v7的基础上修改为有一只闭眼就是闭眼

        if self.model1_closeEye > 0:                                # 闭眼，在v7的基础上，修改为有一只闭眼就是闭眼
            self.is_closeEye = True
        else:
            self.is_closeEye = False

        if self.model1_closeMouth or self.model1_mouthNum == 0:     # 张嘴，m1检测到闭嘴，票否
            self.is_openMouth = False
        else:
            self.is_openMouth = True
        

        if self.model1_usePhone:                                    # 手机
            self.is_usePhone = True

        if self.model1_turned or self.model1_turnedDown:            # 转头
            self.is_turned = True
        
        return
    
    def chushai_judge_action_is_normal(self):
        # 1. 初始化，表示当前帧正常
        normal = True
        # 2. 如果存在危险驾驶的行为，标记当前帧不正常
        if self.is_turned or self.is_usePhone or self.is_openMouth or self.is_closeEye:
            normal = False
        return normal

    # IO异步取帧
    def readall_frame_worker(self, step: int):
        while True:
            ret, frame = self.reader.grab_forword_read(step)      # 取帧
            if ret:
                self.readall_frame_queue.put(frame)
            else:
                self.readall_frame_queue.put(None)          # 读出来的一帧为空，意为视频结束
                break
        return

    def frameidx_in_maybe_list(self, frameidx, maybe_list:list):
        if len(maybe_list) > 0:
            for sublist in maybe_list:
                start = sublist[0]
                end = sublist[1]
                if frameidx >= start and frameidx <= end:
                    return True
        return False
    
    def frameid_is_maybe_start(self, frameidx, maybe_list:list):
        if len(maybe_list) > 0:
            for sublist in maybe_list:
                start = sublist[0]
                end = sublist[1]
                if frameidx == start:
                    return True, start, end
        
        start = 0
        end = 0
        return False, start, end

    def getTimestamp(self):             # 获取以ms为单位的时间戳
        # 第几帧/fps*1000 即为时间戳，单位ms
        return int(1000.0 * self.nowFrameIdx / self.fps)

    def deal_action_count(self, frame):
        # print(f"self.skip_step: {self.skip_step}")


        nowTimestamp = self.getTimestamp()                  # 获取当前时间戳
        half_step_timestamp = int(1000.0 * self.skip_step / 2 / self.fps)
        self.videoWillEnd = False           # 下一帧视频将会结束
        # if self.nowFrameIdx + self.skip_step >= self.video_totalFrameNum:       # 下次跳帧超出总帧数，代表视频结尾
        #     self.videoWillEnd = True

        # 手机
        if self.is_usePhone:            # 检测到手机
            # print(f'((3) {self.use_phone_frame} 当前第几帧{self.nowFrameIdx})')
            self.use_phone_frame += self.skip_step
            if self.use_phone_frame == self.skip_step:              # 动作刚开始，记录 开始时间
                self.timestamp_start_usePhone = nowTimestamp - half_step_timestamp
            elif self.use_phone_frame >= self.frameNum_3s:          # 判断某个行为是否超过3s，若超过置标志位为True
                self.usePhone_MoreThan3s = True
            
            if self.videoWillEnd and self.usePhone_MoreThan3s:              # 视频结束 and 行为超过3s
                self.timestamp_end_usePhone = nowTimestamp - half_step_timestamp  # 记录 结束时间
                self.temp_action["periods"][0] = self.timestamp_start_usePhone
                self.temp_action["periods"][1] = self.timestamp_end_usePhone
                self.temp_action["category"] = 3
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()                
        else:                           # 没检测到手机
            self.use_phone_frame = 0
            if self.usePhone_MoreThan3s:              # 这个行为结束的时候超过3s
                self.timestamp_end_usePhone = nowTimestamp - half_step_timestamp # 记录 结束时间
                self.temp_action["periods"][0] = self.timestamp_start_usePhone
                self.temp_action["periods"][1] = self.timestamp_end_usePhone
                self.temp_action["category"] = 3
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()



        # 转头
        if not self.is_turned or (self.is_turned and self.is_usePhone):
            self.look_around_frame = 0
            if self.lookAround_MoreThan3s:        # 这个行为结束的时候超过3s
                self.timestamp_end_lookAround = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_lookAround
                self.temp_action["periods"][1] = self.timestamp_end_lookAround
                self.temp_action["category"] = 4
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()

        elif self.is_turned:
            # print(f'((4) {self.look_around_frame} 当前第几帧{self.nowFrameIdx})')
            self.look_around_frame += self.skip_step
            if self.look_around_frame == self.skip_step:  # 初次出现某个危险行为，计数值 = 一个跳帧间隔
                self.timestamp_start_lookAround = nowTimestamp - half_step_timestamp
            elif self.look_around_frame >= self.frameNum_3s:
                self.lookAround_MoreThan3s = True
            
            if self.videoWillEnd and self.lookAround_MoreThan3s:        # 这个行为结束的时候超过3s
                self.timestamp_end_lookAround = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_lookAround
                self.temp_action["periods"][1] = self.timestamp_end_lookAround
                self.temp_action["category"] = 4
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()

        # 张嘴
        if self.is_openMouth:
            # print(f'((2) {self.mouth_open_frame}当前第几帧{self.nowFrameIdx})')
            self.mouth_open_frame += self.skip_step
            if self.mouth_open_frame == self.skip_step:
                self.timestamp_start_openMouth = nowTimestamp - half_step_timestamp
            elif self.mouth_open_frame >= self.frameNum_3s:
                self.openMouth_MoreThan3s = True
            
            if self.videoWillEnd and self.openMouth_MoreThan3s:         # 这个行为结束的时候超过3s
                self.timestamp_end_openMouth = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_openMouth
                self.temp_action["periods"][1] = self.timestamp_end_openMouth
                self.temp_action["category"] = 2
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()
        elif not self.is_openMouth:
            self.mouth_open_frame = 0
            if self.openMouth_MoreThan3s:         # 这个行为结束的时候超过3s
                self.timestamp_end_openMouth = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_openMouth
                self.temp_action["periods"][1] = self.timestamp_end_openMouth
                self.temp_action["category"] = 2
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()

        # 闭眼
        # 后续需要替换，缩小优先级范围，将转头影响计时改为低头影响计时
        if not self.is_closeEye or (self.is_closeEye and self.is_openMouth) or (self.is_closeEye and self.is_turned):
            self.eyes_closed_frame = 0
            if self.closeEye_MoreThan3s:         # 这个行为结束的时候超过3s
                self.timestamp_end_closeEye = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_closeEye 
                self.temp_action["periods"][1] = self.timestamp_end_closeEye 
                self.temp_action["category"] = 1
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()
        elif self.is_closeEye:
            # print(f'((1) {self.eyes_closed_frame} 当前第几帧{self.nowFrameIdx})')
            self.eyes_closed_frame += self.skip_step
            if self.eyes_closed_frame == self.skip_step:
                self.timestamp_start_closeEye = nowTimestamp - half_step_timestamp
            elif self.eyes_closed_frame >= self.frameNum_3s:
                self.closeEye_MoreThan3s = True
            
            if self.videoWillEnd and self.closeEye_MoreThan3s:         # 这个行为结束的时候超过3s
                self.timestamp_end_closeEye = nowTimestamp - half_step_timestamp
                self.temp_action["periods"][0] = self.timestamp_start_closeEye
                self.temp_action["periods"][1] = self.timestamp_end_closeEye
                self.temp_action["category"] = 1
                self.temp_list.append(copy.deepcopy(self.temp_action))
                self.clear_between_action()

        # 有超过三秒的行为，在图片上输出危险
        if self.usePhone_MoreThan3s or self.lookAround_MoreThan3s or self.openMouth_MoreThan3s or self.closeEye_MoreThan3s:
            org = (300, 300)  # 文本左下角位置坐标

            # 定义文本属性
            fontFace = cv2.FONT_HERSHEY_SIMPLEX  # 字体类型
            fontScale = 2.0  # 字体缩放比例
            color = (0, 0, 255)  # 文本颜色 (绿色)
            thickness = 2  # 文本线宽
            lineType = cv2.LINE_AA  # 线的类型

            # 在图像上绘制文本
            cv2.putText(frame, "Danger!!!", org, fontFace, fontScale, color, thickness, lineType)
        return frame    


    def reset_CountValue_between_videos(self):
        self.result = {"result": {"duration": 6000, "drowsy": []}}
        self.temp_list = []
        self.temp_action = {"periods": [3, 7], "category": 1}

        self.timestamp_start_lookAround = 0         # 初始化记录时间戳（起、止时间）的变量
        self.timestamp_start_closeEye = 0
        self.timestamp_start_openMouth = 0
        self.timestamp_start_usePhone = 0

        self.timestamp_end_lookAround = 0
        self.timestamp_end_closeEye = 0
        self.timestamp_end_openMouth = 0
        self.timestamp_end_usePhone = 0

        self.lookAround_MoreThan3s = False
        self.closeEye_MoreThan3s = False
        self.openMouth_MoreThan3s = False
        self.usePhone_MoreThan3s = False

        self.failures = 0    # 失败计数值
        
        self.look_around_frame = 0  # 重置四种行为连续计数值
        self.eyes_closed_frame = 0
        self.mouth_open_frame = 0
        self.use_phone_frame = 0

        self.cv2_setpos_time = 0  # 统计各部分占的时间
        self.cv2_read_time = 0
        self.onnx_infer_time = 0
        self.tracker_time = 0

        self.detected_frames = 0   # 统计处理的帧的数量，第几帧结束判断的
        self.model1_face = False  # 模型1是否检测到人脸
        self.io_thread_end = False
        return
    
    def reset_CountValue_between_frames(self):
        self.is_normal = False  # 一共5种行为, bool类型,表示某种行为有没有出现
        self.is_closeEye = False
        self.is_openMouth = False
        self.is_usePhone = False
        self.is_turned = False

        self.model1_openEye = 0
        self.model1_closeEye = 0
        self.model1_eyeNum = 0

        self.model1_mouthNum = 0
        self.model1_openMouth = False
        self.model1_closeMouth = False
        self.model1_usePhone = False
        self.model1_turned = False
        self.model1_turnedDown = False
        return

    def clear_between_action(self):
        self.timestamp_start_lookAround = 0         # 重置时间戳（起、止时间）的变量
        self.timestamp_start_closeEye = 0
        self.timestamp_start_openMouth = 0
        self.timestamp_start_usePhone = 0

        self.timestamp_end_lookAround = 0
        self.timestamp_end_closeEye = 0
        self.timestamp_end_openMouth = 0
        self.timestamp_end_usePhone = 0

        self.lookAround_MoreThan3s = False        # 超过3s的标记
        self.closeEye_MoreThan3s = False
        self.openMouth_MoreThan3s = False
        self.usePhone_MoreThan3s = False

        self.look_around_frame = 0                      # 每个行为检测出来以后，重置连续帧数计数值
        self.eyes_closed_frame = 0
        self.mouth_open_frame = 0
        self.use_phone_frame = 0

        return
