// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <stdbool.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "zlog.h"
#include "ocslog.h"
#include "ocsaudit.h"

static bool isInitialized = false;

static int get_entry_header(char* str) 
{
    struct timeval now;
    struct tm *temp;
    char timestr[32];
    int result;

    result = gettimeofday(&now, 0);

    if (result != STATUS_SUCCESS) 
    {
        log_info("OcsAudit: gettimeofday failed with error (%s)\n", strerror(result));

        return STATUS_FAILURE;
    }

    temp = localtime(&now.tv_sec);

    if (temp == 0) 
    {
        log_info("OcsAudit: localtime failed\n");

        return STATUS_FAILURE;
    }

    result = strftime(timestr, sizeof(timestr), "%m/%d/%Y | %H:%M:%S |", temp);

    if (result == STATUS_SUCCESS) 
    {
        log_info("OcsAudit: strftime failed with error (%s)\n", strerror(result));

        return STATUS_FAILURE;
    }

    sprintf(str, "%s", timestr);

    return STATUS_SUCCESS;
}

static int audit_info(char* log_msg)
{
	char log_entry[512];

	int result;

	if(log_msg == NULL)
	{
 		log_err(UNKNOWN_ERROR, "OcsAudit: Null string passed to log_info!\n");

		return STATUS_FAILURE;
	}

	result = get_entry_header(log_entry);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsAudit: Unable to create entry header\n");

		return result;
	}

	strcat(log_entry, log_msg);

	dzlog_info(log_entry);
	
	return STATUS_SUCCESS;
}

//
// Log information
//

int OcsAudit_LogCommand(const char* username, int type, int interface, 
						const char* command, const char* args)
{
	char log_msg[512];	

	// Check if initialized
	if (!isInitialized)
	{
		OcsAudit_Init();
	}
	
	// Check inputs
	if (type < TYPE_GET || type > NUM_TYPES)
	{
		log_err(UNKNOWN_ERROR, "OcsAudit: Invalid command type passed to OcsAudit_LogCommand, type: %i\n", type);
		
		return STATUS_FAILURE;
	}

	if (interface < INTERFACE_OCSCLI || interface > NUM_INTERFACES)
	{
		log_err(UNKNOWN_ERROR, "OcsAudit: Invalid interface passed to OcsAudit_LogCommand, interface: %i\n", interface);

		return STATUS_FAILURE;
	}

	if(username == NULL || command == NULL || args == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsAudit: Null arguments passed to OcsAudit_LogCommand!\n");

		return STATUS_FAILURE;
	}

	sprintf(log_msg, " %s | %s | %s | %s | %s ", username, cmd_types_str[type], cmd_interfaces_str[interface],
												 command, args);
	audit_info(log_msg);
	
	return STATUS_SUCCESS;
}

//
// Audit log initialization function
//

int OcsAudit_Init(void)
{
	FILE *fp;
    struct stat st;
	char permissions[] = "0666";
    mode_t mode = strtol(permissions, 0, 8);
    bool lockexist = (stat(LOCKFILE, &st) == 0);
    bool log0exist = (stat(LOGFILE0, &st) == 0);
    bool log1exist = (stat(LOGFILE1, &st) == 0);
    bool log2exist = (stat(LOGFILE2, &st) == 0);
	
	if(isInitialized)
	{
		return STATUS_SUCCESS;
	}

	// Initialize zlog with the audit config file and create internal audit category
	int result = dzlog_init(ZLOG_CONF, "audit");

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsAudit: Failed to initialize zlog, check file indicated by ZLOG_PROFILE_ERROR to find details\n");

		// Release zlog memory and close open files 
		zlog_fini();

		return result;
	}

	// If this process created lock file, attempt to set permissions
	if(!lockexist)
	{
		// Ensure all users have RW permission to rotate lock file 
		if(chmod(LOCKFILE, mode) < 0)
		{
			log_err(UNKNOWN_ERROR, "OcsAudit: Failed to set permissions for the rotate lock file\n");
		}
	}
	
	// If this process created log file, attempt to set permissions
	if(!log0exist)
	{
		// Ensure all users have RW permission to log file 
		if(chmod(LOGFILE0, mode) < 0)
		{
			log_err(UNKNOWN_ERROR, "OcsAudit: Failed to set permissions for log file 0\n");
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
			log_err(UNKNOWN_ERROR, "OcsAudit: Failed to set permissions for log file 1\n");
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
			log_err(UNKNOWN_ERROR, "OcsAudit: Failed to set permissions for log file 2\n");
		}
	}
	
	isInitialized = true;

	return STATUS_SUCCESS;
}