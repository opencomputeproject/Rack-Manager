// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef LOG_H
#define LOG_H

#include <ocslog.h>

/* Enable DEBUG_TRACE to include trace prints */
//#define DEBUG_TRACE 1

#define LOG_ERR(err, msg, ...) do { log_err(err, msg, ##__VA_ARGS__); } while(0)
#define LOG_INFO(msg, ...) do { log_out(msg, ##__VA_ARGS__); } while(0)

#ifdef DEBUG_TRACE
#define LOG_TRACE(msg, ...) do { log_out(msg, ##__VA_ARGS__); } while(0)
#else
#define LOG_TRACE(msg, ...)
#endif

#define UNKNOWN_ERROR   -1
#define FAILED          -1
#define SUCCESS         0

#endif
