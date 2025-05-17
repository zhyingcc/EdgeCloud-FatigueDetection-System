/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

/* later will use libbacktrace*/
#ifndef _WIN32_PORT_EXECINFO_H_
#define _WIN32_PORT_EXECINFO_H_

static int backtrace(void **buffer, int size)
{
  return -1;
}

#endif