// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef _TELEMETRY_H
#define _TELEMETRY_H

//
// Telemetry definitions and return types
//

#define LOCKFILE  "/tmp/ocstelemetry_zlog.lock"
#define LOGFILE0  "/usr/srvroot/ocstelemetry.log"
#define LOGFILE1  "/usr/srvroot/ocstelemetry.log.0"
#define LOGFILE2  "/usr/srvroot/ocstelemetry.log.1"
#define ZLOG_CONF "/var/local/ocstelemetry_zlog.conf"

#define STATUS_SUCCESS     	 0
#define STATUS_FAILURE    	-1

#define MIN_SERVER_ID 	   	 1
#define NUM_SERVERS 	  	48
#define MIN_FAN_ID			 0
#define NUM_FANS			12
#define MIN_PORT_ID		   	 1
#define NUM_PORTS   	  	48
#define MAX_FAN_SPEED_LEN	8
#define MAX_FAN_SPEEDS_LEN  (MAX_FAN_SPEED_LEN * NUM_FANS)
#define MAX_SERVER_PWR_LEN	8
#define MAX_SERVER_PWRS_LEN (MAX_SERVER_PWR_LEN * NUM_SERVERS)

#define MAX_RACK_TEMP 	  	50
#define MAX_RACK_HUMIDITY 	80
#define MIN_RACK_HUMIDITY 	25

#define MAX_FILENAME_SIZE   255 	//max linux filename size
#define MAX_LINE_LEN 		512 	//arbitrary limit on characters per log file line

#define VALID_PATTERN		0xAC

//
// Telemetry types
//

enum components
{
	RACK = 0,
	SWITCH,
	SWITCH_PORT,
	SERVER,
	SERVER_POWER,
	SERVER_FAN,
	NUM_COMPONENTS
};

enum levels
{
	INFO = 0,
	WARNING,
	ERROR,
	NUM_LEVELS
};

enum ipmi_cmds
{
	IPMI_FAN_INFO = 0,
	IPMI_POWER_INFO,
	NUM_IPMI_COMMANDS
};

enum python_cmds
{
	PYTHON_SWITCH_INFO = 0,
	PYTHON_SWITCH_PORT_INFO,
	NUM_PYTHON_COMMANDS
};

typedef struct _entry
{
	time_t time;
	int component;
	int level;
	int bladeid;
	int fanid;
	int portid;
	int message_id;
	char message[512];
	char sensortype[32];
} log_entry;


typedef struct _rack_info
{ 
	double  temp_celsius;
	double  humidity_rh;
	double  power_watts;
	double  power_limit_watts;
	bool 	power_limit_enabled;
	bool 	power_limit_asserted;
	bool 	dcthrottle_enabled;
	bool 	dcthrottle_asserted;
	double	voltage_volts;
} rack_info;

typedef struct _server_info
{
	unsigned long long presence;
	unsigned long long power_enabled;
	int valid;
} server_info;

typedef struct _server_fan_info
{
	bool healthy;
	int  speed_rpm;
	int valid;
} server_fan_info;

typedef struct _server_power_info
{
	uint16_t power_reading;
	int valid;
} server_power_info;

typedef struct _switch_info
{
	int temp_celsius;
	float uptime;
	char redundant_power_state[32];
	char temp_sensor_state[32];
	char power_state[32];
	int valid;
} switch_info;

typedef struct _switch_port_info
{
	char port_state[20];
	int valid;
} switch_port_info;


//
// Telemetry function prototypes
//

int telemetry_init (void);
int TelemetryClearLog(const char* filename);
int TelemetryGetLog(time_t start_time, time_t end_time, int start_id, int end_id, int log_level, int component, int bladeid, int portid, const char* filename);
int TelemetryParseLine(char* line, log_entry* entry);

#endif
