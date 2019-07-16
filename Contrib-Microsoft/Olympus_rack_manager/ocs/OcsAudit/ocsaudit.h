// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef _OCSAUDIT_H
#define _OCSAUDIT_H

//
// Audit definitions and return types
//

#define LOCKFILE  "/tmp/ocsaudit_zlog.lock"
#define LOGFILE0  "/usr/srvroot/ocsaudit.log"
#define LOGFILE1  "/usr/srvroot/ocsaudit.log.0"
#define LOGFILE2  "/usr/srvroot/ocsaudit.log.1"
#define ZLOG_CONF "/var/local/ocsaudit_zlog.conf"

#define STATUS_SUCCESS     	 0
#define STATUS_FAILURE    	-1

enum cmd_types
{
	TYPE_GET = 0,
	TYPE_PATCH,
	TYPE_POST,
	TYPE_SHOW,
	TYPE_SET,
	TYPE_SHELL,
	TYPE_START,
	TYPE_STOP,
	TYPE_DELETE,
	TYPE_UNKNOWN,
	NUM_TYPES
};

const char* cmd_types_str[] = {
	"Get",
	"Patch",
	"Post",
	"Show",
	"Set",
	"Shell",
	"Start",
	"Stop",
	"Delete",
	"Unknown"
};

enum cmd_interfaces
{
	INTERFACE_OCSCLI = 0,
	INTEFACE_WCSCLI,
	INTERFACE_REST,
	NUM_INTERFACES
};

const char* cmd_interfaces_str[] = {
	"OcsCli",
	"WcsCli",
	"Rest"
};

//
// Audit function prototypes
//

int OcsAudit_LogCommand(const char* username, int type, int interface, 
						const char* command, const char* args);
int OcsAudit_Init(void);

#endif
