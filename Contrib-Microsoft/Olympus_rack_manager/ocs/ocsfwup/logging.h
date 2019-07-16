// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef LOG_H
#define LOG_H

#include <stdio.h>
#include <string.h>

/* Enable DEBUG_TRACE to include trace prints */
// #define DEBUG_TRACE 1

#define LOG_FNC_ERR(err) if((err) != 0) { fprintf(stderr, "ERROR: %s %s :%d Error-->%d %s \n",  __FILE__, __FUNCTION__, __LINE__ ,errno,strerror(errno));}

#define LOG_ERR(err, msg, ...) do { fprintf(stderr, "ERROR: " msg ": %s \n",  ##__VA_ARGS__, strerror(err));} while(0)

#define LOG_INFO(msg, ...) do {fprintf(stdout, msg, ##__VA_ARGS__);} while(0)

#ifdef DEBUG_TRACE
#define LOG_TRACE(msg, ...) do {fprintf(stdout, msg, ##__VA_ARGS__);} while(0)
#else
#define LOG_TRACE(msg, ...)
#endif

#define UNKNOWN_ERROR   -1
#define FAILED          -1
#define SUCCESS         0

#endif
