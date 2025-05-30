#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2020-2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# edited by ZGB
################################################################################

import time
import ctypes
import numpy as np
import cv2
import os
import pathlib
import sys
import io
from queue import Queue
import threading
from loguru import logger

from cloudinfer import cloud_infer

sys.path.append("../")
import gi

gi.require_version("Gst", "1.0")
from gi.repository import GObject, Gst
import platform
import sys
video_writer = None

def is_aarch64():
    return platform.uname()[4] == 'aarch64'


import gi
import sys

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

# 创建一个帧队列
frame_queue = []

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True


sys.path.append('/opt/nvidia/deepstream/deepstream/lib')

import pyds

CLASS_NB = 7
ACCURACY_ALL_CLASS = 0.5
UNTRACKED_OBJECT_ID = 0xffffffffffffffff
IMAGE_HEIGHT = 720
IMAGE_WIDTH = 1280
OUTPUT_VIDEO_NAME = "./out.mp4"

np.set_printoptions(threshold=np.inf)

INPUT_HEIGHT = 640
INPUT_WIDTH = 640


class BoundingBox:
    def __init__(self, classID, confidence, x1, x2, y1, y2, image_width, image_height):
        self.classID = classID
        self.confidence = confidence
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.u1 = x1 / image_width
        self.u2 = x2 / image_width
        self.v1 = y1 / image_height
        self.v2 = y2 / image_height

    def box(self):
        return self.x1, self.y1, self.x2, self.y2

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def center_absolute(self):
        return 0.5 * (self.x1 + self.x2), 0.5 * (self.y1 + self.y2)

    def center_normalized(self):
        return 0.5 * (self.u1 + self.u2), 0.5 * (self.v1 + self.v2)

    def size_absolute(self):
        return self.x2 - self.x1, self.y2 - self.y1

    def size_normalized(self):
        return self.u2 - self.u1, self.v2 - self.v1


def nms(boxes, box_confidences, nms_threshold=0.5):
    x_coord = boxes[:, 0]
    y_coord = boxes[:, 1]
    width = boxes[:, 2]
    height = boxes[:, 3]

    areas = width * height
    ordered = box_confidences.argsort()[::-1]

    keep = list()
    while ordered.size > 0:
        i = ordered[0]
        keep.append(i)
        xx1 = np.maximum(x_coord[i], x_coord[ordered[1:]])
        yy1 = np.maximum(y_coord[i], y_coord[ordered[1:]])
        xx2 = np.minimum(x_coord[i] + width[i], x_coord[ordered[1:]] + width[ordered[1:]])
        yy2 = np.minimum(y_coord[i] + height[i], y_coord[ordered[1:]] + height[ordered[1:]])

        width1 = np.maximum(0.0, xx2 - xx1 + 1)
        height1 = np.maximum(0.0, yy2 - yy1 + 1)
        intersection = width1 * height1
        union = (areas[i] + areas[ordered[1:]] - intersection)

        iou = intersection / union

        indexes = np.where(iou <= nms_threshold)[0]
        ordered = ordered[indexes + 1]
    keep = np.array(keep).astype(int)
    return keep


def postprocess(buffer, image_width, image_height, conf_threshold=0.4, nms_threshold=0.5):
    detected_objects = []
    img_scale = [image_width / INPUT_WIDTH, image_height / INPUT_HEIGHT, image_width / INPUT_WIDTH,
                 image_height / INPUT_HEIGHT]
    num_bboxes = int(buffer[0, 0, 0, 0])

    if num_bboxes:
        bboxes = buffer[0, 1: (num_bboxes * 6 + 1), 0, 0].reshape(-1, 6)
        labels = set(bboxes[:, 5].astype(int))

        for label in labels:
            selected_bboxes = bboxes[np.where((bboxes[:, 5] == label) & (bboxes[:, 4] >= conf_threshold))]
            selected_bboxes_keep = selected_bboxes[nms(selected_bboxes[:, :4], selected_bboxes[:, 4], nms_threshold)]
            for idx in range(selected_bboxes_keep.shape[0]):
                box_xy = selected_bboxes_keep[idx, :2]
                box_wh = selected_bboxes_keep[idx, 2:4]
                score = selected_bboxes_keep[idx, 4]

                box_x1y1 = box_xy - (box_wh / 2)
                box_x2y2 = np.minimum(box_xy + (box_wh / 2), [INPUT_WIDTH, INPUT_HEIGHT])
                box = np.concatenate([box_x1y1, box_x2y2])
                box *= img_scale

                if box[0] == box[2]:
                    continue
                if box[1] == box[3]:
                    continue
                detected_objects.append(
                    BoundingBox(label, float(score), box[0], box[2], box[1], box[3], image_height, image_width))

    return detected_objects


def get_label_names_from_file(filepath="./labels.txt"):
    """
        从文件中读取标签名称。
    """
    f = io.open(filepath, "r")
    labels = f.readlines()
    labels = [elm[:-1] for elm in labels]
    f.close()
    return labels


def make_elm_or_print_err(factoryname, name, printedname, detail=""):
    """
        利用一种流媒体处理框架的对象工厂创建对象。
        factoryname: 对象工厂名称
        name: 对象名称 （在管道中唯一标识的名称）
        Creates an element with Gst Element Factory make.
        Return the element  if successfully created, otherwise print
        to stderr and return None.
    """
    print("Creating", printedname)
    elm = Gst.ElementFactory.make(factoryname, name)
    if not elm:
        sys.stderr.write("Unable to create " + printedname + " \n")
        if detail:
            sys.stderr.write(detail)
    return elm


def add_obj_meta_to_frame(bbox, score, label, batch_meta, frame_meta):
    """
    Inserts an object into the metadata
    """
    untracked_obj_id = 0xffffffffffffffff
    # this is a good place to insert objects into the metadata.
    # Here's an example of inserting a single object.
    obj_meta = pyds.nvds_acquire_obj_meta_from_pool(batch_meta)
    # Set bbox properties. These are in input resolution.
    rect_params = obj_meta.rect_params
    rect_params.left = int(bbox[0])
    rect_params.top = int(bbox[1])
    rect_params.width = int((bbox[2] - bbox[0]))
    rect_params.height = int(bbox[3] - bbox[1])
    # logger.info(f"rect_params.left: {rect_params.height}")

    # Semi-transparent yellow backgroud
    rect_params.has_bg_color = 0
    rect_params.bg_color.set(1, 1, 0, 0.4)

    # Red border of width 3
    rect_params.border_width = 3
    rect_params.border_color.set(1, 0, 0, 1)

    # Set object info including class, detection confidence, etc.
    obj_meta.confidence = score
    # obj_meta.class_id = int(label)

    # There is no tracking ID upon detection. The tracker will
    # assign an ID.
    obj_meta.object_id = untracked_obj_id

    # lbl_id = int(label)
    # if lbl_id >= len(label_names):
    #    lbl_id = 0

    # Set the object classification label.
    obj_meta.obj_label = label

    # Set display text for the object.
    txt_params = obj_meta.text_params
    if txt_params.display_text:
        pyds.free_buffer(txt_params.display_text)

    txt_params.x_offset = int(rect_params.left)
    txt_params.y_offset = max(0, int(rect_params.top) - 10)
    txt_params.display_text = (
            label + " " + "{:04.3f}".format(score)
    )
    # Font , font-color and font-size
    txt_params.font_params.font_name = "Serif"
    txt_params.font_params.font_size = 10
    # set(red, green, blue, alpha); set to White
    txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

    # Text background color
    txt_params.set_bg_clr = 1
    # set(red, green, blue, alpha); set to Black
    txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

    # Inser the object into current frame meta
    # This object has no parent
    pyds.nvds_add_obj_meta_to_frame(frame_meta, obj_meta, None)



def tiler_sink_pad_buffer_probe(pad, info, u_data):
    """
    Get tensor_metadata from triton inference output
    Convert tensor metadata to numpy array
    Postprocessing
    """
    global frame_queue
    global video_writer
    image_width = 1280
    image_height = 720
    conf_thresh = 0.5
    nms_thresh = 0.5
    label = get_label_names_from_file()
    print(label)
    is_save_output = False
    # get the buffer of info argument
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))

    l_frame = batch_meta.frame_meta_list

    print(time.time())
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            # logger.info("frame_meta: {}".format(frame_meta))
        except StopIteration:
            break
        iter_obj = frame_meta.obj_meta_list
        print("number_of_counts:", frame_meta.num_obj_meta)
        n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
        # convert python array into numpy array format in the copy mode.
        frame_copy = np.array(n_frame, copy=True, order='C')
        # convert the array into cv2 default color format
        pic = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGRA)
        pic = cv2.cvtColor(pic, cv2.COLOR_BGRA2BGR)
        # cv2.imwrite(f"test_{time.time()}.jpg", pic)
        # filename = 'tmp.npy'

        # np.save(filename, pic)
        # video_writer.write(pic)
        # frame_queue.append(pic)
        # frame_queue.put(pic)
        # cv2.imwrite(f"test_{time.time()}.jpg", pic)
        # cv2.waitKey(1000)
        # cv2.destroyAllWindows()
        while iter_obj is not None:
            # 从GList对象中获取当前节点的数据
            obj_meta = pyds.NvDsObjectMeta.cast(iter_obj.data)

            # 读取对象元数据的属性
            object_id = obj_meta.object_id
            class_id = obj_meta.class_id
            left = obj_meta.rect_params.left
            top = obj_meta.rect_params.top
            width = obj_meta.rect_params.width
            height = obj_meta.rect_params.height
            confidence = obj_meta.confidence
            # 用cropped_image = pic[int(top):int(top + height), int(left):int(left + width)] 裁剪
            if class_id == 2 or class_id == 6:
                # 2: face, 6: side_face
                cropped_image = pic[int(top):int(top + height), int(left):int(left + width)]
                tmp_name = f"{label[class_id]}_{confidence}.jpg"
                cv2.imwrite(tmp_name, cropped_image)
                # res = cloud_infer(tmp_name) # 云端推理这里可以用confidence联合推理
                # if res == "OK":
                #     pass
#---------------------!!!!!!!!!!!!!!!!!补充端云协同!!!!!!!!!!!!!!!!!!!!!!---------------------------------
            # print("class_id: ", class_id)
            # print("top: ", top)
            # print("left: ", left)
            # print("width: ", width)
            # print("height: ", height)
            # cropped_image = pic[int(top):int(top + height), int(left):int(left + width)]
            # cv2.imwrite(f"{class_id}_{time.time()}_{confidence}.jpg", cropped_image)
            try:
                iter_obj = iter_obj.next
            except StopIteration:
                break

        try:
            l_frame = l_frame.next
        except StopIteration:
            break
    return Gst.PadProbeReturn.OK

def queueToMP4():
    global frame_queue
    queue = frame_queue
    while queue.empty():
        continue
    print("queue now not empty")
    frame = frame_queue.get()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    output_file = "tmp.mp4"
    fps = 30
    height, width, _ = frame.shape
    if(os.path.exists(output_file)):
        os.remove(output_file)

    # 设置视频编解码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 创建输出视频对象
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # 写入第一帧
    video_writer.write(frame)
    print("now queue!")
    # 将队列中的每一帧写入输出视频
    q_siz = queue.qsize()
    for i in range(q_siz):
        frame = queue.get()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        video_writer.write(frame)
    print("queue ended")

    # 释放资源
    video_writer.release()
    return output_file

EOS_MESSAGE = False

def cloud_inference():
    cnt_for_cloud = 0
    file_name = "tmp.mp4"
    while not EOS_MESSAGE:
        # time.sleep(1)
        # continue
        file_name = queueToMP4()
        cnt_for_cloud += 1
        print("cnt_for_cloud:", cnt_for_cloud)
        cloud_inference_result = cloud_infer(file_name)
        print("cloud_inference_result:", cloud_inference_result)

def cb_newpad(decodebin, decoder_src_pad, data):
    logger.info("In cb_newpad\n")
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    logger.info("gstname= %s" % gstname)
    if gstname.find("video") != -1:
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        logger.info("features= %s" % features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                logger.opt(colors=True).warning("WARNING: Failed to link decoder src pad to source bin ghost pad\n")
        else:
            logger.error("ERROR: Decodebin did not pick nvidia decoder plugin.\n")

def decodebin_child_added(child_proxy, Object, name, user_data):
    logger.info(f"Decodebin child added: {name} \n")
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)


def create_source_bin(idx, uri):
    """
    Decode file video local and URI video input
    """
    logger.info("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name = "source-bin-%02d" % idx
    #logger.info(f"source_name: {bin_name}")
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        logger.opt(colors=True).warning("WARNING: Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        logger.opt(colors=True).warning("WARNING: Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri", uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        logger.opt(colors=True).warning("WARNING: Failed to add ghost pad in source bin \n")
        return None
    return nbin



def main(args):
    global EOS_MESSAGE
    # 不进行保存
    is_save_output = False
    # Check input arguments
    # 第二个参数是媒体文件或者uri
    # if len(args) != 2:
    #     sys.stderr.write("usage: %s <media file or uri>\n" % args[0])
    #     sys.exit(1)

    # test_video_file = ["file:///home/jetson/DeepStream-Yolo/night_woman_087_40_5.mp4"]

    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Create gstreamer elements
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")


    # Source element for reading from the file
    print("Creating Source \n ")
    source = Gst.ElementFactory.make("nvarguscamerasrc", "src-elem")
    if not source:
        sys.stderr.write(" Unable to create Source \n")

    # Converter to scale the image
    nvvidconv_src = Gst.ElementFactory.make("nvvideoconvert", "convertor_src")
    if not nvvidconv_src:
        sys.stderr.write(" Unable to create nvvidconv_src \n")

    # Caps for NVMM and resolution scaling
    caps_nvvidconv_src = Gst.ElementFactory.make("capsfilter", "nvmm_caps")
    if not caps_nvvidconv_src:
        sys.stderr.write(" Unable to create capsfilter \n")

    streammux = make_elm_or_print_err("nvstreammux", "Stream-muxer", "NvStreamMux")

    # Use nvinferserver to run inferencing on decoder's output,
    # behaviour of inferencing is set through config file
    pgie = make_elm_or_print_err("nvinfer", "primary-inference", "Nvinferserver")

    #################################################
    tee = make_elm_or_print_err("tee", "tee", "Tee")
    queue1 = make_elm_or_print_err("queue", "queue1", "Queue1")
    queue2 = make_elm_or_print_err("queue", "queue2", "Queue2")

    print("Creating nvvidconv1 \n ")
    nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
    if not nvvidconv1:
        sys.stderr.write(" Unable to create nvvidconv1 \n")
    print("Creating filter1 \n ")
    caps1 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
    filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
    if not filter1:
        sys.stderr.write(" Unable to get the caps filter1 \n")
    filter1.set_property("caps", caps1)
    print("Creating tiler \n ")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    # fakesink 用来接收前面的数据，作为最后的link，不做任何处理，不能删掉
    fakesink = Gst.ElementFactory.make("fakesink")

    #################################################

    # Use convertor to convert from NV12 to RGBA as required by nvosd
    nvvidconv = make_elm_or_print_err("nvvideoconvert", "convertor", "Nvvidconv")

    # Create OSD to draw on the converted RGBA buffer
    nvosd = make_elm_or_print_err("nvdsosd", "onscreendisplay", "OSD (nvosd)")

    # Finally encode and save the osd output
    queue = make_elm_or_print_err("queue", "queue", "Queue")

    nvvidconv2 = make_elm_or_print_err("nvvideoconvert", "convertor2", "Converter 2 (nvvidconv2)")

    capsfilter = make_elm_or_print_err("capsfilter", "capsfilter", "capsfilter")

    caps = Gst.Caps.from_string("video/x-raw, format=I420")
    capsfilter.set_property("caps", caps)

    # On Jetson, there is a problem with the encoder failing to initialize
    # due to limitation on TLS usage. To work around this, preload libgomp.
    # Add a reminder here in case the user forgets.
    preload_reminder = "If the following error is encountered:\n" + \
                        "/usr/lib/aarch64-linux-gnu/libgomp.so.1: cannot allocate memory in static TLS block\n" + \
                        "Preload the offending library:\n" + \
                        "export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1\n"
    encoder = make_elm_or_print_err("avenc_mpeg4", "encoder", "Encoder", preload_reminder)

    encoder.set_property("bitrate", 2000000)

    codeparser = make_elm_or_print_err("mpeg4videoparse", "mpeg4-parser", 'Code Parser')

    container = make_elm_or_print_err("qtmux", "qtmux", "Container")

    output_video_name = "./output.mp4"

    if is_save_output:
        sink = make_elm_or_print_err("filesink", "filesink", "Sink")

        sink.set_property("location", output_video_name)
        sink.set_property("sync", 0)
        sink.set_property("async", 0)
    else:
        sink = make_elm_or_print_err("fakesink", "fake-sink", "FakeSink")
    source.set_property('bufapi-version', True)

    # Add elemnts to pipeline

    pipeline.add(source)
    pipeline.add(nvvidconv_src)
    pipeline.add(caps_nvvidconv_src)

    pipeline.add(streammux)

    batch_size = 1
    image_height = 720
    image_width = 1280

    caps_nvvidconv_src.set_property('caps', Gst.Caps.from_string('video/x-raw(memory:NVMM), width=1280, height=720'))

    streammux.set_property("width", image_width)
    streammux.set_property("height", image_height)
    streammux.set_property("batch-size", batch_size)
    streammux.set_property("batched-push-timeout", 4000000)

    logger.info("DeepStream Triton yolov5 tensorRT inference")
    pgie.set_property("config-file-path", "config_infer_primary_yoloV5.txt")

    logger.info("Adding elements to Pipeline \n")

    pipeline.add(pgie)
    pipeline.add(tee)
    pipeline.add(queue1)
    if is_save_output:
        pipeline.add(nvvidconv)
        pipeline.add(nvosd)
        pipeline.add(queue)
        pipeline.add(nvvidconv2)
        pipeline.add(capsfilter)
        pipeline.add(encoder)
        pipeline.add(codeparser)
        pipeline.add(container)
    pipeline.add(sink)
    pipeline.add(queue2)
    pipeline.add(nvvidconv1)
    pipeline.add(filter1)
    pipeline.add(tiler)
    pipeline.add(fakesink)

    # we link the elements together
    # uri -> uridecode bin ->
    # nvinfer -> nvvidconv -> nvosd -> video-renderer
    logger.info("Linking elements in the Pipeline \n")
    source.link(nvvidconv_src)
    nvvidconv_src.link(caps_nvvidconv_src)

    sinkpad = streammux.get_request_pad("sink_0")
    if not sinkpad:
        sys.stderr.write(" Unable to get the sink pad of streammux \n")
    srcpad = caps_nvvidconv_src.get_static_pad("src")
    if not srcpad:
        sys.stderr.write(" Unable to get source pad of caps_nvvidconv_src \n")
    srcpad.link(sinkpad)

    streammux.link(pgie)
    pgie.link(tee)
    tee.link(queue1)
    tee.link(queue2)
    if is_save_output:
        queue1.link(nvvidconv)
        nvvidconv.link(nvosd)
        nvosd.link(queue)
        queue.link(nvvidconv2)
        nvvidconv2.link(capsfilter)
        capsfilter.link(encoder)
        encoder.link(codeparser)
        codeparser.link(container)
        container.link(sink)
    else:
        queue1.link(sink)

    queue2.link(nvvidconv1)
    nvvidconv1.link(filter1)
    filter1.link(tiler)
    tiler.link(fakesink)

    tiler_sink_pad = tiler.get_static_pad("sink")
    if not tiler_sink_pad:
        sys.stderr.write(" Unable to get src pad \n")
    else:
        tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe, 0)

    # start play back and listen to events
    # 开启pipeline
    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    # video_thread = threading.Thread(target=cloud_inference)

    # 启动视频文件线程
    # video_thread.start()

    # create an event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()  # 创建主循环
    bus = pipeline.get_bus()  # 获取总线
    bus.add_signal_watch()  # 添加信号监视器
    bus.connect("message", bus_call, loop)  # 连接信号处理函数

    try:
        loop.run()
    except:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)
    EOS_MESSAGE = True
    print("Waiting for video thread to finish...")
    # video_thread.join()
    print("Video thread finished.")
    # video_writer.release()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
