/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef MODELBOX_WINGPU_MEMORY_H_
#define MODELBOX_WINGPU_MEMORY_H_

#include <modelbox/base/device.h>
#include <modelbox/base/memory_pool.h>
#include <modelbox/base/status.h>
#include <modelbox/base/timer.h>

#include <queue>
#include <thread>
#include <unordered_map>

namespace modelbox {
Timer *GetTimer();
constexpr uint32_t GPU_MEM_NORMAL = 0;
constexpr uint32_t GPU_MEM_DX2D = 1;

class WinGpuMemory : public DeviceMemory {
 public:
  WinGpuMemory(const std::shared_ptr<Device> &device,
               const std::shared_ptr<DeviceMemoryManager> &mem_mgr,
               void *device_mem_ptr, size_t size);

  WinGpuMemory(const std::shared_ptr<Device> &device,
               const std::shared_ptr<DeviceMemoryManager> &mem_mgr,
               std::shared_ptr<void> device_mem_ptr, size_t size);

  virtual ~WinGpuMemory();
};

class WinGpuMemoryManager;
class WinGpuMemoryPool : public MemoryPoolBase {
 public:
  WinGpuMemoryPool(WinGpuMemoryManager *mem_manager);
  virtual ~WinGpuMemoryPool();
  Status Init();
  virtual void *MemAlloc(size_t size);
  virtual void MemFree(void *ptr);
  virtual void OnTimer();

 private:
  WinGpuMemoryManager *mem_manager_;
  std::shared_ptr<TimerTask> flush_timer_;
};

class WinGpuMemoryManager : public DeviceMemoryManager {
 public:
  WinGpuMemoryManager(const std::string &device_id);
  virtual ~WinGpuMemoryManager();

  Status Init();

  /* *
   * @brief Implement by win10 device, alloc memory
   * @param size Memory size to allocate
   * @return Device memory in shared ptr
   *   */
  std::shared_ptr<void> AllocSharedPtr(size_t size);

  /* *
   * @brief Create a win10 memory container
   * @param device pointer to device
   * @param mem_ptr shared pointer to memory
   * @param size memory size
   * @return Empty memory container
   */
  std::shared_ptr<DeviceMemory> MakeDeviceMemory(
      const std::shared_ptr<Device> &device, std::shared_ptr<void> mem_ptr,
      size_t size) override;

  /* *
   * @brief Implement by win10 device, free memory
   * @param mem_ptr Memory to free
   */
  void Free(void *mem_ptr, uint32_t mem_flags);

  /* *
   * @brief Implement by win10 device, alloc memory
   * @param size Memory size to allocate.
   * @return Device memory.
   */
  void *Malloc(size_t size, uint32_t mem_flags);

  /**
   * @brief Implement by win10 device, copy data from src to dest
   * @param dest dest buffer to write
   * @param dest_size dest buffer size
   * @param src_buffer src buffer to read
   * @param src_size read data size
   * @param kind data copy kind
   * @return Status
   */
  Status Copy(void *dest, size_t dest_size, const void *src_buffer,
                      size_t src_size, DeviceMemoryCopyKind kind) override;

  /* *
   * @brief Copy memory between win10 device and host
   * @param dest_memory Destination memory
   * @param dest_offset Destination memory offset
   * @param src_memory Source memory
   * @param src_offset Source offset
   * @param src_size Source memory size
   * @param copy_kind Memory copy mode
   * @return Status
   */
  Status DeviceMemoryCopy(
      const std::shared_ptr<DeviceMemory> &dest_memory, size_t dest_offset,
      const std::shared_ptr<const DeviceMemory> &src_memory, size_t src_offset,
      size_t src_size,
      DeviceMemoryCopyKind copy_kind = DeviceMemoryCopyKind::FromHost) override;

  /* *
   * @brief Get device memory info
   * @return Status
   */
  Status GetDeviceMemUsage(size_t *free, size_t *total) const override;

 private:

  WinGpuMemoryPool mem_pool_;
};
}  // namespace modelbox

#endif  // MODELBOX_WINGPU_MEMORY_H_
