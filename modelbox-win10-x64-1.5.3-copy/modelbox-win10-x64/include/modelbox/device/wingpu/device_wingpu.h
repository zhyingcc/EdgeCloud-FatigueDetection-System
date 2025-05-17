/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef MODELBOX_DEVICE_WINGPU_H_
#define MODELBOX_DEVICE_WINGPU_H_

#include <modelbox/base/device.h>
#include <modelbox/data_context.h>
#include <modelbox/device/wingpu/wingpu_memory.h>
#include <modelbox/flow.h>

namespace modelbox {

constexpr const char *DEVICE_TYPE = "gpu";
constexpr const char *DEVICE_DRIVER_NAME = "device-win10-gpu";
constexpr const char *DEVICE_DRIVER_DESCRIPTION = "A win10 gpu device driver";

class WinGpu : public Device {
 public:
  WinGpu(const std::shared_ptr<DeviceMemoryManager> &mem_mgr);
  virtual ~WinGpu();
  std::string GetType() const override;

  Status DeviceExecute(const DevExecuteCallBack &fun, int32_t priority,
                       size_t dev_count) override;
  bool NeedResourceNice() override;
};

class WinGpuFactory : public DeviceFactory {
 public:
  WinGpuFactory();
  virtual ~WinGpuFactory();

  std::map<std::string, std::shared_ptr<DeviceDesc>> DeviceProbe();
  std::string GetDeviceFactoryType();
  std::shared_ptr<Device> CreateDevice(const std::string &device_id);

 private:
  size_t GetMemSize();
};

class WinGpuDesc : public DeviceDesc {
 public:
  WinGpuDesc() = default;
  virtual ~WinGpuDesc() = default;
};

}  // namespace modelbox

#endif  // MODELBOX_DEVICE_WINGPU_H_