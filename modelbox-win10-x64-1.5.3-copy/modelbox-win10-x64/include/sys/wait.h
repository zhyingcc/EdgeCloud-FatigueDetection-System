/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

// wait_pid for windows

#ifndef __SYS_WAIT_H_WINDOWS_PORT__
#define __SYS_WAIT_H_WINDOWS_PORT__

#ifndef _WIN32

#pragma message("this sys/wait.h is only for Windows!")

#else /* _WIN32 */

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#ifdef __GNUC__
#include <sys/time.h> /* for timeval */
#endif /* __GNUC__  */

#include <errno.h>
#include <string.h>

#ifndef _INC_WINDOWS

typedef unsigned long DWORD;
typedef DWORD * LPDWORD;

#ifdef _WIN64

typedef long long LONG_PTR;
typedef unsigned long long ULONG_PTR;

#else /* _WIN64 */

typedef long LONG_PTR;
typedef unsigned long ULONG_PTR;

#endif

typedef long LONG;
typedef wchar_t WCHAR;
typedef int BOOL;
typedef void * HANDLE;

#ifndef MAX_PATH
#define MAX_PATH 260
#endif /* MAX_PATH */

#ifndef WINAPI
#define WINAPI __stdcall
#endif /* WINAPI */

#ifndef DECLSPEC_DLLIMPORT
#ifdef _MSC_VER
#define DECLSPEC_DLLIMPORT __declspec(dllimport)
#else /* _MSC_VER */
#define DECLSPEC_DLLIMPORT
#endif /* _MSC_VER */
#endif /* DECLSPEC_DLLIMPORT */

#ifndef WINBASEAPI
#define WINBASEAPI DECLSPEC_DLLIMPORT
#endif /* WINBASEAPI */

#ifndef INVALID_HANDLE_VALUE
#define INVALID_HANDLE_VALUE ((HANDLE)(LONG_PTR)-1)
#endif /* INVALID_HANDLE_VALUE */

#ifndef SYNCHRONIZE
#define SYNCHRONIZE (0x00100000L)
#endif /* SYNCHRONIZE */

#ifndef PROCESS_QUERY_INFORMATION
#define PROCESS_QUERY_INFORMATION (0x0400)
#endif /* PROCESS_QUERY_INFORMATION */

#ifndef INFINITE
#define INFINITE 0xFFFFFFFF
#endif /* INFINITE */

#ifndef WAIT_OBJECT_0
#define WAIT_OBJECT_0 0
#endif /* WAIT_OBJECT_0 */

#ifndef WAIT_TIMEOUT
#define WAIT_TIMEOUT 258L
#endif /* WAIT_TIMEOUT */

WINBASEAPI DWORD WINAPI GetCurrentProcessId(void);
WINBASEAPI BOOL WINAPI CloseHandle(HANDLE hObject);
WINBASEAPI HANDLE WINAPI OpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId);
WINBASEAPI DWORD WINAPI WaitForSingleObject(HANDLE hHandle, DWORD dwMilliseconds);
WINBASEAPI BOOL WINAPI GetExitCodeProcess(HANDLE hProcess, LPDWORD lpExitCode);

#endif /* _INC_WINDOWS */

#ifndef _WINSOCKAPI_

struct private_timeval {
    long    tv_sec;
    long    tv_usec;
};

#define timeval private_timeval

#endif /* _WINSOCKAPI_ */

#ifndef _INC_TOOLHELP32

typedef struct tagPROCESSENTRY32W
{
    DWORD   mydwSize;
    DWORD   mycntUsage;
    DWORD   myth32ProcessID;
    ULONG_PTR myth32DefaultHeapID;
    DWORD   myth32ModuleID;
    DWORD   mycntThreads;
    DWORD   myth32ParentProcessID;
    LONG    mypcPriClassBase;
    DWORD   mydwFlags;
    WCHAR   myszExeFile[MAX_PATH];
} PROCESSENTRY32W;
typedef PROCESSENTRY32W *  PPROCESSENTRY32W;
typedef PROCESSENTRY32W *  LPPROCESSENTRY32W;

#ifndef TH32CS_SNAPPROCESS
#define TH32CS_SNAPPROCESS 2
#endif /* TH32CS_SNAPPROCESS */

HANDLE WINAPI CreateToolhelp32Snapshot(DWORD mydwFlags, DWORD myth32ProcessID);
BOOL WINAPI Process32FirstW(HANDLE hSnapshot, LPPROCESSENTRY32W lppe);
BOOL WINAPI Process32NextW(HANDLE hSnapshot, LPPROCESSENTRY32W lppe);

#endif /* _INC_TOOLHELP32 */

#ifndef WNOHANG
#define WNOHANG 1
#endif /* WNOHANG */

#ifndef WUNTRACED
#define WUNTRACED 2
#endif /* WUNTRACED */

#ifndef __WEXITSTATUS
#define __WEXITSTATUS(status) (((status) & 0xFF00) >> 8)
#endif /* __WEXITSTATUS */

#ifndef __WIFEXITED
#define __WIFEXITED(status) (__WTERMSIG(status) == 0)
#endif /* __WIFEXITED */

#ifndef __WTERMSIG
#define __WTERMSIG(status) ((status) & 0x7F)
#endif /* __WTERMSIG */

#ifndef __WIFSIGNALED
#define __WIFSIGNALED(status) (((signed char)(__WTERMSIG(status) + 1) >> 1) > 0)
#endif /* __WIFSIGNALED */

#ifndef __WIFSTOPPED
#define __WIFSTOPPED(status) (((status) & 0xFF) == 0x7F)
#endif /* __WIFSTOPPED */

#ifndef __WSTOPSIG
#define __WSTOPSIG(status) __WEXITSTATUS(status)
#endif /* __WSTOPSIG */

#ifndef __WCONTINUED
#define __WCONTINUED 8
#endif /* __WCONTINUED */

#ifndef __WNOWAIT
#define __WNOWAIT 0x01000000
#endif /* __WNOWAIT */

#ifndef WEXITSTATUS
#define WEXITSTATUS(status) __WEXITSTATUS(status)
#endif /* WEXITSTATUS */

#ifndef WIFEXITED
#define WIFEXITED(status) __WIFEXITED(status)
#endif /* WIFEXITED */

#ifndef WIFSIGNALED
#define WIFSIGNALED(status) __WIFSIGNALED(status)
#endif /* WIFSIGNALED */

#ifndef WTERMSIG
#define WTERMSIG(status) __WTERMSIG(status)
#endif /* WTERMSIG */

#ifndef WIFSTOPPED
#define WIFSTOPPED(status) __WIFSTOPPED(status)
#endif /* WIFSTOPPED */

#ifndef WSTOPSIG
#define WSTOPSIG(status) __WSTOPSIG(status)
#endif /* WSTOPSIG */

#if !defined(__pid_t_defined) && !defined(_PID_T_) && !defined(pid_t)
#define __pid_t_defined 1
#define _PID_T_
typedef int __pid_t;
typedef __pid_t pid_t;
#endif /* !defined(__pid_t_defined) && !defined(_PID_T_) && !defined(pid_t) */

#ifndef __id_t_defined
#define __id_t_defined 1
typedef unsigned __id_t;
typedef __id_t id_t;
#endif /* __id_t_defined */

#ifndef __uid_t_defined
#define __uid_t_defined 1
typedef unsigned __uid_t;
typedef __uid_t uid_t;
#endif /* __uid_t_defined */

#ifndef __siginfo_t_defined
#define __siginfo_t_defined 1
typedef struct
{
    int si_signo; 
    int si_code; 
    int si_errno; 
    pid_t si_pid; 
    uid_t si_uid;
    void * si_addr;
    int si_status; 
    long si_band;
}
siginfo_t;
#endif /* __siginfo_t_defined */

struct rusage
{
    struct timeval ru_utime; /* user time used */
    struct timeval ru_stime; /* system time used */
};

#define WAIT_PID_ERR_RETURN \
do {                        \
    CloseHandle(hSnapshot); \
    errno = ECHILD;         \
    return -1;              \
}while(0);

static int __filter_anychild(PROCESSENTRY32W * pe, DWORD pid)
{
    return pe->myth32ParentProcessID == GetCurrentProcessId();
}

static int __filter_pid(PROCESSENTRY32W * pe, DWORD pid)
{
    return pe->myth32ProcessID == pid;
}

static int __waitpid_wait(HANDLE hSnapshot, HANDLE hProcess, 
    int * status, int nohang, int ret)
{
    int saved_status = 0;
    DWORD wait_status = 0, exit_code = 0;
    wait_status = WaitForSingleObject(hProcess, nohang ? 0 : INFINITE);

    if (WAIT_OBJECT_0 == wait_status) {
        if (GetExitCodeProcess(hProcess, &exit_code))
            saved_status |= (exit_code & 0xFF) << 8;
    }
    else if (WAIT_TIMEOUT == wait_status && nohang) {
        return 0;
    }
    else {
        CloseHandle(hProcess);
        WAIT_PID_ERR_RETURN
    }

    CloseHandle(hProcess);
    CloseHandle(hSnapshot);

    if (status) {
        *status = saved_status;
    }
    return ret;
}

static int __waitpid_internal(pid_t pid, int * status, int options, siginfo_t * infop, struct rusage * rusage)
{
    HANDLE hProcess = INVALID_HANDLE_VALUE, hSnapshot = INVALID_HANDLE_VALUE;
    int (*filter)(PROCESSENTRY32W*, DWORD);
    PROCESSENTRY32W pe;
    int nohang = WNOHANG == (WNOHANG & options);
    options &= ~(WUNTRACED | __WNOWAIT | __WCONTINUED | WNOHANG);
    if (options) {
        errno = -EINVAL;
        return -1;
    }

    if (pid == -1) {
        /* wait for any child */
        filter = __filter_anychild;
    }
    else if (pid == 0 || pid < -1) {
        /* wait for any process from the group */
        /* wait for any process from the current group */
        return -1; /* not implemented */
    }
    else {
        /* wait for process with given pid */
        filter = __filter_pid;
    }

    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (INVALID_HANDLE_VALUE == hSnapshot) {
        errno = ECHILD;
        return -1;
    }
    pe.mydwSize = sizeof(pe);
    if (!Process32FirstW(hSnapshot, &pe)) {
        WAIT_PID_ERR_RETURN
    }
    do {
        if (filter(&pe, pid)) {    
            hProcess = OpenProcess(SYNCHRONIZE | PROCESS_QUERY_INFORMATION, 0, pe.myth32ProcessID);
            if (INVALID_HANDLE_VALUE == hProcess) {
                WAIT_PID_ERR_RETURN
            }
            break;
        }
    } while (Process32NextW(hSnapshot, &pe));
    if (INVALID_HANDLE_VALUE == hProcess) {
        WAIT_PID_ERR_RETURN
    }

    return __waitpid_wait(hSnapshot, hProcess, status, nohang, pe.myth32ParentProcessID);
}

static int waitpid(pid_t pid, int * status, int options)
{
    return __waitpid_internal(pid, status, options, NULL, NULL);
}

static int wait(int *status)
{
    return __waitpid_internal(-1, status, 0, NULL, NULL);
}

// liyuming add for fork fake
static int fork()
{
    return -1;
}

static int vfork()
{
    return -1;
}

#ifndef _INC_WINDOWS

#undef WAIT_OBJECT_0

#undef FILETIME
#undef PFILETIME
#undef LPFILETIME

#endif /* _INC_WINDOWS */

#ifndef _WINSOCKAPI_

#undef timeval

#endif /* _WINSOCKAPI_ */

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* _WIN32 */

#endif /* __SYS_WAIT_H_WINDOWS_PORT__ */
