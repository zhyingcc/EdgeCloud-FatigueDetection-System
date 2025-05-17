/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef MODELBOX_COMMON_UTILS_H_
#define MODELBOX_COMMON_UTILS_H_

#include <signal.h>

#include <functional>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>

namespace modelbox {

constexpr const char *MODELBOX_ROOT_VAR = "${MODELBOX_ROOT}";

/**
 * @brief Get current modelbox standalone directory
 * @return standalone root dir
 */
const std::string &modelbox_root_dir(void);


/**
 * @brief Get modelbox full path
 *
 * @param path
 * @return std::string
 */
std::string modelbox_full_path(const std::string &path);

/**
 * @brief Create pid file of current process
 * @param pid_file path of pid file
 * @return create result
 */
int modelbox_create_pid(const char *pid_file);

/**
 * @brief Handle process signal
 * @param sig_list signal list to handle
 * @param sig_num sig_list count
 * @param action signal handler
 * @return register result.
 */
int modelbox_sig_register(const int sig_list[], int sig_num,
                          void (*action)(int));

/**
 * @brief Custom stream
 */
class OutStream {
 protected:
  using OStream = std::ostringstream;
  using Buffer_p = std::unique_ptr<OStream, std::function<void(OStream *)>>;
  virtual void ProcessStream(OStream *st) = 0;

 public:
  /**
   * @brief return stream
   */
  Buffer_p Stream() {
    return Buffer_p(new OStream, [=](OStream *st) {
      ProcessStream(st);
      delete st;
    });
  }
};

}  // namespace modelbox

#endif  // MODELBOX_COMMON_UTILS_H_