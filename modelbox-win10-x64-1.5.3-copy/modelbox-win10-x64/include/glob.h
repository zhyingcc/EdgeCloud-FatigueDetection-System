/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef _WIN32_PORT_GLOB_H_
#define _WIN32_PORT_GLOB_H_

#include <vector>
#include <string>

struct glob_t {
  unsigned int gl_pathc;  /* Count of total paths so far. */
  unsigned int gl_matchc; /* Count of paths matching pattern. */
  unsigned int gl_offs;   /* Reserved at beginning of gl_pathv. */
  int gl_flags;           /* Copy of flags parameter to glob. */
  char ** gl_pathv;        /* List of paths matching pattern. */
  std::vector<std::string> std_pathv;
  ~glob_t() {
    if (gl_pathv) {
      delete[] gl_pathv;
    }
  }
};

#define GLOB_SUCCESS 0 /* ok.  */
#define GLOB_NOSPACE 1 /* Ran out of memory.  */
#define GLOB_ABORTED 2 /* Read error.  */
#define GLOB_NOMATCH 3 /* No matches found.  */
#define GLOB_NOSYS 4   /* Not implemented.  */

#define GLOB_TILDE 0x0800 /* Expand tilde names from the passwd file. */

int glob(const char *pattern, int, int (*)(const char *, int), glob_t *result);
void globfree(glob_t *p_glob);

#endif /* !_WIN32_PORT_GLOB_H_ */
