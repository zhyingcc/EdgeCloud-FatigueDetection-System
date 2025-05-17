/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef __WIN_SETENV__
#define __WIN_SETENV__

#include <stdlib.h>
#include <string>

static int setenv(const char *name, const char *value, int overwrite)
{
    if(!overwrite) {
        char *v = getenv(name);
        if(v) return 0;
    }
	std::string combilestr(name);
	combilestr.append("=").append(value);
	
    return putenv(combilestr.c_str());
}

#endif