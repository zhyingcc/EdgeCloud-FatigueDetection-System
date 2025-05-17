/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef __WIN_UTILS_PATH__
#define __WIN_UTILS_PATH__

#include <io.h>
typedef unsigned char u_char;

#ifdef GetCurrentTime
#undef GetCurrentTime
#endif

#ifdef CreateDirectory
#undef CreateDirectory
#endif

static inline int mkdir(const char *p, int mode) { return mkdir(p); }
#endif