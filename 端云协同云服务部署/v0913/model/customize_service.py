import json
import os
import queue
import traceback
import threading
import sys
import argparse

from onnx_detect import ONNX_engine
import our_tool
from our_videoReader import VideoReader

from model_service.pytorch_model_service import PTServingBaseService # 提交
class fatigue_driving_detection(PTServingBaseService): # 提交
# class fatigue_driving_detection():  # 本地
    def __init__(self, model_name, model_path):
        self.onnx_model = ONNX_engine(weights_path='/home/mind/model/v4_c7_320.onnx', size=320)   # 提交！！！！看清楚权重
        # self.onnx_model = ONNX_engine(weights_path='v4_c7_320.onnx', size=320)
        self.model_name = model_name
        self.model_path = model_path
        self.capture = '/home/mind/model/test.mp4'

        self.width = 1920
        self.height = 1080
        self.fps = 30
        self.video_count = 0

    # 前处理：接收byteIO对象并存成mp4文件
    def _preprocess(self, data):
        # data: {'input_video': OrderedDict([('day_man_101_41_6.mp4', <_io.BytesIO object at 0x7fd95e91c770>)])}
        self.video_count += 1
        for k, v in data.items():
            for file_name, bytesIO_object in v.items():
                print('file_name:', file_name,
                      'jhj video count:', self.video_count)
                self.file_name = file_name
                try:
                    with open(self.capture, 'wb') as f:
                        file_content_bytes = bytesIO_object.read()
                        f.write(file_content_bytes)
                except Exception:
                    traceback.print_exc()
                    return {"message": "There was an error read or write file"}
        
        self.model1_face = False
        return 'ok'


    # 推理部分
    def _inference(self, data):
        print(data)
        self.result = {"result": []}
        result_bbox_list = []

        self.reader = VideoReader(self.capture)         
        if self.reader.ret == False:
            return result_bbox_list
        self.height, self.width, self.fps, self.video_totalFrameNum = self.reader.get_capInfo()   # 初始化，获取视频信息
        
        # 读取第一帧
        ret, frame = self.reader.grab_forword_read(1)
        self.nowFrameIdx = 1
        self.skip_step = 1

        self.frame_queue = queue.Queue(maxsize=10)
        io_thread = threading.Thread(target=self.read_frame_worker, args=(self.skip_step, ))    # 初始化，创建一个子线程用于取帧，异步IO
        io_thread.start()
        
        # 3. 主线程处理检测的需求，设置一个 检测结束的flag_infer_end
        while frame is not None:
            # 检测
            bbox = self.infer_one_frame(frame)
            result_bbox_list.append(bbox)
            # 取下一帧
            frame = self.frame_queue.get()
            self.nowFrameIdx += self.skip_step
        
        io_thread.join()
        self.reader.release()  # 释放cap对象
        print(result_bbox_list)

        self.result = {"result": result_bbox_list}

        return self.result

    def _postprocess(self, data):
        return data

    
    def infer_one_frame(self, frame):
        # 主驾驶位剪裁
        sub_frame = frame[:, int(self.width * 0.33): int(self.width), :]
        # bbox->[class ,[center-x, center-y, width, height],] ，bbox是清洗过的数据
        bbox = self.onnx_model.preprocess(sub_frame)
        if len(bbox) > 0:           # 根据清洗后的bbox，得到驾驶员的行为和位置
            for box in bbox:
                box[0] = int(box[0]) # 
                box[1][0] = int(box[1][0] + self.width * 0.33)
                box[1][1] = int(box[1][1])
                box[1][2] = int(box[1][2])
                box[1][3] = int(box[1][3])
                box[2] = 0

        return bbox

    # IO异步取帧
    def read_frame_worker(self, step: int):
        while True:
            ret, frame = self.reader.grab_forword_read(step)      # 取帧
            if ret:
                self.frame_queue.put(frame)
            else:
                self.frame_queue.put(None)          # 读出来的一帧为空，意为视频结束
                break
        return

                


def run(opt):
    if opt.savetxt:
        if not os.path.exists('run'):               # 路径不存在则新建
            os.makedirs('run')
        save_stdout = sys.stdout                    # 保存标准输出流
        info_output = open(os.path.join('run', opt.output_txtname), "w")
        sys.stdout = info_output

    detection = fatigue_driving_detection("model name", 1)
    detection.onnx_model = ONNX_engine(weights_path=opt.weights, size=opt.img_size)

    filenames = os.listdir(opt.test_video)          # 将文件夹转换成一个列表，元素为文件名
    filenames.sort()                                # 对列表进行排序, 元素是字符串时，默认按照首字母排序
    video_num = len(filenames)  # 视频段数

    all_deal_frame = 0
    all_time = 0
    all_detect_time = 0
    Total_time_score = 0
    count = 0

    for filename in filenames:
        file_path = os.path.join(opt.test_video, filename)  # 拼接文件路径
        detection.capture = file_path
        result = detection._inference(1)
        return
        # category = result.get('result').get('category')
        infer_duration = result.get('result').get('duration')

        # 计算推理时长得分
        one_video_time = round(our_tool.get_video_time(file_path))  # 计算单个视频的视频时长（单位为ms）
        time_score = our_tool.sigmoid(one_video_time / infer_duration)
        Total_time_score += time_score

        all_deal_frame += detection.detected_frames
        all_time += infer_duration
        all_detect_time += detection.onnx_infer_time
        count += 1

        print(count, '/', video_num, filename, result, '; video_time(ms)', one_video_time, '; time_score', round(time_score, 3))
        print('\n\n')

        # 打印到终端
        if opt.savetxt and opt.print2terminal:
            sys.stdout = save_stdout  # 恢复标准输出流
            print(count, '/', video_num, filename, result, '; video_time(ms)', one_video_time, '; time_score', round(time_score, 3))
            print('\n\n')
            sys.stdout = info_output

        result = detection._postprocess(result)
        info_output.flush()  # 立刻写入文件，不等缓存

    # 计算各个分类的加权F1_score
    # 视频的时间得分，乘权重0.3。（* 100 / video_num这个操作是为了不是100段视频时，总得分不为100）
    Total_time_score = Total_time_score / video_num * 0.3

    # 总得分
    # Total_socre = F1_score + Total_time_score
    print('\n', opt.test_video)

    # 打印到终端
    if opt.savetxt and opt.print2terminal:
        sys.stdout = save_stdout  # 恢复标准输出流
        print('\n', opt.test_video)
        print('all_deal_frame', all_deal_frame)
        print('all_time', all_time)
        print('all_detect_time', all_detect_time)

        sys.stdout = info_output

    print('all_deal_frame', all_deal_frame)
    print('all_time', all_time)
    print('all_detect_time', all_detect_time)

    if opt.savetxt:
        sys.stdout = save_stdout  # 恢复标准输出流
        info_output.close()


if __name__ == "__main__":
    # 使用argparse打包参数，便于从命令行修改参数或者使用shell脚本进行测试
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str,default='v4_c7_320.onnx', help='onnx权重路径')
    parser.add_argument('--test-video', type=str,default='videoone', help='测试视频路径')
    parser.add_argument('--savetxt', type=bool, default=True, help='是否保存输出txt')
    parser.add_argument('--output-txtname', type=str,default='output0912.txt', help='输出日志文件路径')
    parser.add_argument('--img-size', type=int, default=320, help='推理时使用的图片大小')
    parser.add_argument('--print2terminal', type=bool,default=False, help='是否将中间过程打印到终端')
    opt = parser.parse_args()

    # 测试
    run(opt)
