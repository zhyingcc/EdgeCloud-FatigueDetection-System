#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Huawei Technologies Co., Ltd. All rights reserved.

import _flowunit as modelbox
import cv2
import json
import numpy as np
import queue

# two video_decoder(image resize to 640 360)  -- fill to 1280 720


class draw_car_bbox_multiFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        self.image_cache = []
        self.image_cache.append(queue.Queue())
        self.image_cache.append(queue.Queue())
        self.last_img = []
        self.last_img.append(np.zeros((360,640,3), np.uint8))
        self.last_img.append(np.zeros((360,640,3), np.uint8))        
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    # hold image and draw all to self.image, if two images has filled , output it, all buffer full, output too.
    def process(self, data_context):
        url = data_context.get_session_context().get_private_string("multi_source_url")
        image_index = int(url[0])

        in_image = data_context.input("in_image")
        in_bbox = data_context.input("in_bbox")
        out_image = data_context.output("out_image")

        for buffer_img, buffer_bbox in zip(in_image, in_bbox):
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            bbox_str = buffer_bbox.as_object()
            bboxes = self.decode_car_bboxes(bbox_str, (height, width))
            img_out = self.draw_bboxes(img_data, bboxes)

            self.image_cache[image_index].put_nowait(img_out)

        # 2帧放满了，或者只有一帧， 但是缓存了2个,  就可以开始输出了
        while True:
            if ((not self.image_cache[0].empty() and not self.image_cache[1].empty()) or (self.image_cache[0].qsize() > 1) or (self.image_cache[0].qsize() > 1)):
                concat_list = []
                for idx, q in enumerate(self.image_cache):
                    if not q.empty():
                        self.last_img[idx] = q.get_nowait()
                    concat_list.append(self.last_img[idx])
                
                img_cat=cv2.hconcat(concat_list)
                out_buffer = modelbox.Buffer(self.get_bind_device(), img_cat)
                out_buffer.copy_meta(buffer_img)
                out_buffer.set('width', width*2)
                out_image.push_back(out_buffer)
            else:
                break
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def decode_car_bboxes(self, bbox_str, input_shape):
        try:
            coco_car_labels = [2, 5, 7]  # car, bus, truck
            det_result = json.loads(bbox_str)['det_result']
            if (det_result == "None"):
                return []
            bboxes = json.loads(det_result)
            car_bboxes = list(
                filter(lambda x: int(x[5]) in coco_car_labels, bboxes))
        except Exception as ex:
            modelbox.error(str(ex))
            return []
        else:
            for bbox in car_bboxes:
                bbox[0] = int(bbox[0] * input_shape[1])
                bbox[1] = int(bbox[1] * input_shape[0])
                bbox[2] = int(bbox[2] * input_shape[1])
                bbox[3] = int(bbox[3] * input_shape[0])
            return car_bboxes

    def draw_bboxes(self, img_data, bboxes):
        for bbox in bboxes:
            x1, y1, x2, y2, _, _ = bbox
            color = (0, 0, 255)
            cv2.rectangle(img_data, (x1, y1), (x2, y2), color, 2)
        return img_data

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
