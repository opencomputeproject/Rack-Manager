// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef __ocslog_h
#define __ocslog_h

#include <string.h>
#include <stdio.h>

#define LOG_ENTRY_SIZE 		1024
#define LOG_HEADER_SIZE		256
#define UNKNOWN_ERROR	-1
#define FAILURE			-2
#define SUCCESS			0

typedef enum LOG_LEVEL
{
	SILENT_LEVEL = 0,
	ERROR_LEVEL = 1,
	INFO_LEVEL = 2,
}loglevel_t;

#ifdef PC_DEBUG
#define	log_out(...)	printf (__VA_ARGS__); printf ("\n")
#define	log_info		log_out
#define	log_err(x, ...)	\
	do { \
		char message[LOG_ENTRY_SIZE]; \
		snprintf (message, sizeof (message), __VA_ARGS__); \
		log_out ("ERROR: %s -> %s", strerror (x), message); \
	} while (0)
#define log_err_with_location(e, f, func, l, ...) \
	do { \
		char message[LOG_ENTRY_SIZE]; \
		snprintf (message, sizeof (message), __VA_ARGS__); \
		log_out ("Location:(%s:%s:%d) \nERROR: %s -> %s", f, func, l, strerror (e), message); \
	} while (0)
#define log_exception	log_out
#define	log_init(x)
#else
void log_out(const char*, ...);
void log_info(const char*, ...);
void log_err(int, const char*, ...);
void log_err_with_location(int, const char*, const char*, int, const char*, ...);
void log_exception (const char*);
void log_init(loglevel_t);
#endif


/* 
 * LOG_ERR macro
 * Note: Macro is required for getting error location information 
 */
#define log_fnc_err(err, ...) \
	do {	\
		const char* file = __FILE__;	\
		const char* func = __FUNCTION__;	\
		int line = __LINE__;	\
		log_err_with_location (err, file, func, line, __VA_ARGS__); \
	} while(0)

#endif //__ocslog_h
