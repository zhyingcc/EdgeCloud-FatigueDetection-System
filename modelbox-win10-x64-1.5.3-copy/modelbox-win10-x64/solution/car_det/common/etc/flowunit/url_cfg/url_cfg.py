# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import sys

class url_cfgFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        self.count = 0
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        in_1 = data_context.input("in_1")
        out_1 = data_context.output("out_1")
        for item in in_1:
            out_1.push_back(item)      
        # Process the data
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        # Close the flowunit
        return modelbox.Status()

    def data_pre(self, data_context):
        # Before streaming data starts
        input_meta = data_context.get_input_meta("in_1")
        url_str = str(self.count) + input_meta.get_private_string("source_url") 
        self.count += 1
        data_context.get_session_context().set_private_string("multi_source_url", url_str)
        data_context.set_output_meta("out_1", input_meta)

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