// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <syslog.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <sys/stat.h>
#include "ocslog-shm.h"

#include "zlog.h"

#define ZLOG_CONF "/var/local/ocslog.conf"
#define LOCKFILE "/tmp/zlog.lock"
#define LOGFILE0 "/usr/srvroot/ocsevent.log"
#define LOGFILE1 "/usr/srvroot/ocsevent.log.0"
#define LOGFILE2 "/usr/srvroot/ocsevent.log.1"

int main()
{
	FILE *fp;
	zlog_category_t *zc; 
	int status;
	struct stat st;
	char permissions[] = "0666";
    mode_t mode = strtol(permissions, 0, 8);
    bool lockexist = (stat(LOCKFILE, &st) == 0);
    bool log0exist = (stat(LOGFILE0, &st) == 0);
    bool log1exist = (stat(LOGFILE1, &st) == 0);
    bool log2exist = (stat(LOGFILE2, &st) == 0);
	
	zlog_init(ZLOG_CONF);

	// If this process created lock file, attempt to set permissions
	if(!lockexist)
	{
		// Ensure all users have RW permission to rotate lock file 
		if(chmod(LOCKFILE, mode) < 0)
		{
			syslog(LOG_ERR, "OCS log Daemon: Failed to set permissions for the rotate lock file\n");
		}
	}
	
	// If this process created log file, attempt to set permissions
	if(!log0exist)
	{
		// Ensure all users have RW permission to log file 
		if(chmod(LOGFILE0, mode) < 0)
		{
			syslog(LOG_ERR, "OCS log Daemon: Failed to set permissions for log file 0\n");
		}
	}

	// If this process created log file, attempt to set permissions
	if(!log1exist)
	{
		// Create file if doesnt exist
		fp = fopen(LOGFILE1, "ab+");

		// Ensure all users have RW permission to log file 
		if(chmod(LOGFILE1, mode) < 0)
		{
			syslog(LOG_ERR, "OCS log Daemon: Failed to set permissions for log file 1\n");
		}
	}

	// If this process created log file, attempt to set permissions
	if(!log2exist)
	{
		// Create file if doesnt exist
		fp = fopen(LOGFILE2, "ab+");

		// Ensure all users have RW permission to log file 
		if(chmod(LOGFILE2, mode) < 0)
		{
			syslog(LOG_ERR, "OCS log Daemon: Failed to set permissions for log file 2\n");
		}
	}

	zc = zlog_get_category("event");			

	status = shm_init();
	if (status != 0) {
		syslog (LOG_ERR, "OCS log Daemon: Failed to initialize shared memory: %d\n", status);
		return 1;
	}

	char* log_entry;
	
	while(1)
	{
		if(shm_dequeue(&log_entry)!=SUCCESS)
		{
 			syslog(LOG_WARNING, "OCS log Daemon: Get log entry failed\n");
			continue;
		}

		zlog_info(zc, "%s", log_entry);
		free (log_entry);
	}
	
	return 0;
}

