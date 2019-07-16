// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <time.h>
#include <string.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <syslog.h>

#undef PC_DEBUG
#include "ocslog.h"
#include "ocslog-shm.h"

/* 
 * Global variable to indicate log level 
 * Set by caller of init() method
 * Used by every log_*() invocation
 */
int log_level = 0;

/* 
 * Return 1 is STDOUT is attached to the process 
 */
static int can_output (void)
{
	return (getpgrp() == tcgetpgrp(STDOUT_FILENO));
}

/*
 * Get timestamp string in microseconds  
 * Returns 0 for SUCCESS, -1 for failure
 */
static int gettimestring (char *str)
{
    struct timeval now;
    struct tm *tmp;
    char timestr[32];
    int rc;

    rc = gettimeofday(&now, 0);
    if (rc != 0) {
        syslog(LOG_INFO, "OCS log: gettimeofday failed with error(%s).\n", strerror(rc));
        return -1;
    }

    tmp = localtime(&now.tv_sec);
    if (tmp == 0) {
        syslog(LOG_INFO, "OCS log: localtime failed\n");
        return -1;
    }

    rc = strftime(timestr, sizeof(timestr), "%Y-%m-%d %H:%M:%S", tmp);
    if (rc == 0) {
        syslog(LOG_INFO, "OCS log: strftime failed with error(%s).\n", strerror(rc));
        return -1;
    }
    sprintf(str, "%s.%06ld", timestr, now.tv_usec);
    return 0;
}

/*
 * Get header string 
 * Take a string pointer, returns the same pointer with header data 
 */
static char* getheaderstring (char* str)
{
    char *undefined = "undefined";
    char timestr[32];

    if (gettimestring((char*)timestr) != 0) {
        syslog(LOG_INFO, "OCS log: get timestamp string failed\n");
        strcpy(timestr, undefined);
    }
    sprintf(str, "Time: %s Thread: 0x%x Process: %u", timestr, (int)pthread_self(), getpid());
    return str;
}

/*
 * Format a log message
 */
static void log_formatted_message (const char *message, const char *header, int header_len,
	int syslog_pri, va_list args)
{
	char fmt_message[LOG_ENTRY_SIZE];
	int msg_len;
	char *log_message;


	msg_len = vsnprintf (fmt_message, LOG_ENTRY_SIZE, message, args);

	log_message = malloc (header_len + msg_len + 2);
	if (log_message == NULL) {
		fmt_message[sizeof (fmt_message) - 1] = '\0';
		syslog (syslog_pri, fmt_message);
		return;
	}

	strcpy (log_message, header);
	log_message[header_len] = ' ';

	if (msg_len < LOG_ENTRY_SIZE) {
		strcpy (log_message + header_len + 1, fmt_message);
	}
	else {
		vsnprintf (log_message + header_len + 1, msg_len + 1, message, args);
	}

	if (shm_enqueue (log_message) == FAILURE) {
		syslog (syslog_pri, log_message);
	}
	free (log_message);
}

/*
 * Initialize logging
 */
void log_init (loglevel_t level)
{
	log_level = level;
	if(shm_init()!=SUCCESS)
		syslog(LOG_WARNING, "OCS Log: log init failed for Pid(%d)\n", getpid());
}

void log_exception (const char *message)
{
	char str[128];
	char header[LOG_HEADER_SIZE];
	char *new_message;
	int msg_len;

	if (log_level < ERROR_LEVEL) {
		return;
	}

	msg_len = snprintf (header, LOG_HEADER_SIZE, "Level: ERROR %s", getheaderstring (str));
	msg_len += strlen (message) + 1;
	new_message = malloc (msg_len);
	if ((new_message == NULL)){
		syslog (LOG_ERR, message);
		return;
	}

	snprintf (new_message, msg_len, "%s %s", header, message);
	if (shm_enqueue (new_message) == FAILURE) {
		syslog (LOG_ERR, new_message);
	}
}

void log_err (int err, const char *message, ...)
{
	va_list args;
	char str[128];
	char header[LOG_HEADER_SIZE];
	int len;

	if (log_level < ERROR_LEVEL) {
		return;
	}

	va_start (args, message);
	len = snprintf (header, LOG_HEADER_SIZE, "Level: ERROR %s %s:", getheaderstring (str),
		strerror (err));
	log_formatted_message (message, header, len, LOG_ERR, args);
	va_end (args);
}

void log_err_with_location (int err, const char *src, const char *func, int line,
	const char *message, ...)
{
	va_list args;
	char str[128];
	char header[LOG_HEADER_SIZE];
	int len;

	if (log_level < ERROR_LEVEL) {
		return;
	}

	va_start (args, message);
	len = snprintf (header, LOG_HEADER_SIZE, "Level: ERROR %s %s Location:(%s:%s:%d) \n",
		getheaderstring (str), strerror (err), src, func, line);
	log_formatted_message (message, header, len, LOG_ERR, args);
	va_end (args);
}

void log_info (const char *message, ...)
{
	va_list args;
	char str[128];
	char header[LOG_HEADER_SIZE];
	int len;

	if (log_level < INFO_LEVEL) {
		return;
	}

	va_start (args, message);
	len = snprintf (header, LOG_HEADER_SIZE, "Level: INFO %s", getheaderstring (str));
	log_formatted_message (message, header, len, LOG_INFO, args);
	va_end (args);
}

void log_out (const char *message, ...)
{
    va_list args;
    va_start (args, message);
    vprintf (message, args);
    printf ("\n");
    va_end (args);
}
