/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef __WIN_TERMIOS__
#define __WIN_TERMIOS__

#define WEXITSTATUS(x) x

struct termios
{
  unsigned int c_lflag;
};

#define WINPORT_TCSANOW 0
#define WINPORT_ECHO 0x1
#define WINPORT_ICANON 0x10
#define WINPORT_ISIG 0x40

#define TCSANOW WINPORT_TCSANOW
#define ECHO WINPORT_ECHO
#define ICANON WINPORT_ICANON
#define ISIG WINPORT_ISIG

static int tcgetattr (int fd, struct termios *buf) { return 0;}
static int tcsetattr (int fd, int actions, const struct termios *buf) { return 0;}
static int tcdrain (int fd) { return 0;}
static int tcflow (int fd, int action) { return 0;}

#endif