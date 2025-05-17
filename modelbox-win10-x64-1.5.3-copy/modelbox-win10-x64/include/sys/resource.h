/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */
// liyuming: add rlimit mkdir support for windows

#ifndef _SYS_WINPORT_RESOURCE_H_
#define _SYS_WINPORT_RESOURCE_H_

#include <sys/time.h>

#ifdef __cplusplus
extern "C" {
#endif

struct rlimit {
  unsigned long rlim_cur;
  unsigned long rlim_max;
};

#define WINPORT_RUSAGE_SELF 0
#define WINPORT_RLIMIT_NOFILE 5

#define RUSAGE_SELF WINPORT_RUSAGE_SELF
#define RLIMIT_NOFILE	WINPORT_RLIMIT_NOFILE
#define mkdir(a, b) mkdir(a)

int getrlimit(int __resource, struct rlimit *__rlp) { return 0; }
int setrlimit(int __resource, const struct rlimit *__rlp) { return 0; }

#ifdef __cplusplus
}
#endif

#endif
