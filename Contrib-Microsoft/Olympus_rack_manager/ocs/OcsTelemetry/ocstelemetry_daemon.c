// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <time.h>
#include <ctype.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "auth.h"
#include "zlog.h"
#include "ocslog.h"
#include "hdc-lib.h"
#include "hsc-lib.h"
#include "pru-lib.h"
#include "ocslock.h"
#include "pre-checks.h"
#include "ocstelemetry.h"
#include "ocsgpioaccess.h"
#include "blade-id-ip-map.h"

#define IPMI_TOOL_PATH 		"/usr/bin/ipmitool"
#define IPMI_CNXN_SETTINGS  "-I lan -H"

#define MAX_IPMI_CMD_LEN 	512
#define MAX_PYTHON_CMD_LEN  255
#define POLL_INTERVAL_SEC	300

static bool get_precheck_state(int category, int device_id)
{           
	int mode_id;

	/* daemon should be admin */
	int group_id = 0;

	// Get rack manager mode
	int result = get_rm_mode(&mode_id);

	if (result != STATUS_SUCCESS)
	{
		return false;
	}
   
    return (pre_check(group_id, category, device_id, mode_id) == 0);
}

static int get_entry_header(char* str) 
{
    static unsigned long message_id = 1;

    struct timeval now;
    struct tm *temp;
    char timestr[32];
    int result;

    result = gettimeofday(&now, 0);

    if (result != STATUS_SUCCESS) 
    {
        log_info("OcsTelemetry_Daemon: gettimeofday failed with error (%s)\n", strerror(result));

        return STATUS_FAILURE;
    }

    temp = localtime(&now.tv_sec);

    if (temp == 0) 
    {
        log_info("OcsTelemetry_Daemon: localtime failed\n");

        return STATUS_FAILURE;
    }

    result = strftime(timestr, sizeof(timestr), "%m/%d/%Y | %H:%M:%S |", temp);

    if (result == STATUS_SUCCESS) 
    {
        log_info("OcsTelemetry_Daemon: strftime failed with error (%s)\n", strerror(result));

        return STATUS_FAILURE;
    }

    sprintf(str, "%lx | %s", message_id, timestr);

    // Wraps when it overflows
    ++message_id;

    return STATUS_SUCCESS;
}

static int telemetry_info(char* log_msg)
{
	char log_entry[512];

	int result;

	if(log_msg == NULL)
	{
 		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null string passed to log_info!\n");

		return STATUS_FAILURE;
	}

	result = get_entry_header(log_entry);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to create entry header\n");

		return result;
	}

	strcat(log_entry, log_msg);

	dzlog_info(log_entry);

	return STATUS_SUCCESS;
}	

static int telemetry_error(char* log_msg)
{
	char log_entry[512];

	int result;

	if(log_msg == NULL)
	{
 		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null string passed to log_error!\n");

		return STATUS_FAILURE;
	}

	result = get_entry_header(log_entry);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to create entry header\n");

		return result;
	}

	strcat(log_entry, log_msg);

	dzlog_error(log_entry);

	return STATUS_SUCCESS;
}

static int telemetry_warning(char* log_msg)
{
	char log_entry[512];

	int result;

	if(log_msg == NULL)
	{
 		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null string passed to log_warning!\n");

		return STATUS_FAILURE;
	}

	result = get_entry_header(log_entry);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to create entry header\n");

		return result;
	}

	strcat(log_entry, log_msg);

	dzlog_warn(log_entry);

	return STATUS_SUCCESS;
}

static int parse_line_fan_info(char* line, server_fan_info* result)
{
	int id;

	char temp[255];
	char status[255];
	
	bool healthy;

	// Parse fan number
	char* substring = strstr(line, "Fan_");

	if(substring != NULL)
	{
		sscanf(line, "Fan_%s", temp);
	}
	else
	{
		return STATUS_FAILURE;
	}

	id = strtol(temp, NULL, 10);

	if(id < MIN_FAN_ID || id >= NUM_FANS)
	{
		return STATUS_FAILURE;
	}

	// Parse fan id
	substring = strchr(line, '|');

	if(substring == NULL)
	{
		return STATUS_FAILURE;
	}

	// Parse fan status
	line = substring;
	substring = strchr(++line, '|');

	if(substring != NULL)
	{
		sscanf(substring, "| %s", status);

		if(strstr(status, "ok") != NULL)
		{
			healthy = true;
		}
		else
		{
			healthy = false;
		}
	}
	else
	{
		return STATUS_FAILURE;
	}

	// Parse fan number
	line = substring;
	substring = strchr(++line, '|');

	if(substring == NULL)
	{
		return STATUS_FAILURE;
	}

	// Parse fan sensor reading
	line = substring;
	substring = strchr(++line, '|');

	if(substring != NULL)
	{
		sscanf(substring, "| %s RPM", temp);
	}
	else
	{
		return STATUS_FAILURE;
	}

	result[id].healthy = healthy;
	result[id].speed_rpm = strtol(temp, NULL, 10);

	result[id].valid = VALID_PATTERN;

	return STATUS_SUCCESS;
}

static int parse_line_power_info(char* line, server_power_info* result)
{
	char temp[16];

	// Parse power reading
	char* substring = strstr(line, "Instantaneous power reading:");

	if(substring != NULL)
	{
		sscanf(line, "Instantaneous power reading: %s Watts", temp);
	}
	else
	{
		return STATUS_FAILURE;
	}

	result->power_reading = strtol(temp, NULL, 10);
	result->valid = VALID_PATTERN;

	return STATUS_SUCCESS;
}

static int parse_line_switch_info(char* line, switch_info* result)
{
	int status;
	char *pos;

	// Parse redundant power state
	pos = strstr (line, "RedundantPowerState");
	if (pos != NULL) {
		status = sscanf (pos, "RedundantPowerState': %[a-zA-Z]", result->redundant_power_state);
		if (status != 1) {
			return STATUS_FAILURE;
		}
	}
	else {
		return STATUS_FAILURE;
	}

	// Parse temperature sensor state
	pos = strstr (line, "TemperatureSensorState");
	if (pos != NULL) {
		status = sscanf (pos, "TemperatureSensorState': %[a-zA-Z]", result->temp_sensor_state);
		if (status != 1) {
			return STATUS_FAILURE;
		}
	}
	else {
		return STATUS_FAILURE;
	}

	// Parse temperature 
	pos = strstr (line, "ReadingTemp");
	if (pos != NULL)
	{
		status = sscanf (pos, "ReadingTemp': %d", &(result->temp_celsius));
		if (status != 1) {
			return STATUS_FAILURE;
		}
	}
	else {
		return STATUS_FAILURE;
	}

	// Parse uptime
	pos = strstr (line, "Uptime");
	if (pos != NULL) {
		status = sscanf (pos, "Uptime': %f", &(result->uptime));
		if (status != 1) {
			return STATUS_FAILURE;
		}
	}
	else {
		return STATUS_FAILURE;
	}

	// Parse main power state
	pos = strstr (line, "MainPowerState");
	if (pos != NULL) {
		status = sscanf (pos, "MainPowerState': %[a-zA-Z]", result->power_state);
		if (status != 1) {
			return STATUS_FAILURE;
		}
	}
	else {
		return STATUS_FAILURE;
	}
	
	result->valid = VALID_PATTERN;

	return STATUS_SUCCESS;
}

static int call_ipmi_tool(int command_id, int server_id, void* result)
{
	FILE* IpmiTool;

	char hostname[48];
	char command[MAX_IPMI_CMD_LEN];
	char output[MAX_LINE_LEN];
	char username[32];
	char password[32];

	unsigned long long portstate = 0;

	if(server_id < MIN_SERVER_ID || server_id > NUM_SERVERS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid server id, %i, passed to call_ipmi_tool\n", server_id);

		return STATUS_FAILURE;
	}

	if(!get_precheck_state(GET_BLADE_STATE, server_id))
	{
		return STATUS_FAILURE;
	}

	if(ocs_port_present(server_id, &portstate) != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get server presence for server %i\n", server_id);

		return STATUS_FAILURE;
	}

	if(portstate != 1)
	{
	 	log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Server %i not present\n", server_id);

	 	return STATUS_FAILURE;
	}

	if(get_server_address(server_id, &hostname[0]))
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get host address for server %i\n", server_id);

		return STATUS_FAILURE;
	}

	if(get_server_command_access(username, password)!=0)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get username, password for server %i\n", server_id);

		return STATUS_FAILURE;
	}
	
	if(command_id < IPMI_FAN_INFO || command_id >= NUM_IPMI_COMMANDS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid command passed to call_ipmi_tool, %i\n", command_id);

		return STATUS_FAILURE;
	}

	if(result == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to call_ipmi_tool!\n");

		return STATUS_FAILURE;
	}

	// construct command to call using popen
	strcpy(command, IPMI_TOOL_PATH);
	strcat(command, " ");
	strcat(command, IPMI_CNXN_SETTINGS);
	strcat(command, " ");
	strcat(command, hostname);
	strcat(command, " -U ");
	strcat(command, username);
	strcat(command, " -P ");
	strcat(command, password);
	strcat(command, " ");
	strcat(command, "2>/dev/null"); // suppress stderr from being displayed

	switch(command_id)
	{
		case IPMI_FAN_INFO:
		{
			strcat(command, " sdr type fan");
			break;
		}

		case IPMI_POWER_INFO:
		{
			strcat(command, " dcmi power reading");
			break;
		}

		default:
		{
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Command passed to call_ipmi_tool not implemented, %i\n", command_id);

			return STATUS_FAILURE;
		}
	}

	// run command
	IpmiTool = popen(command, "r");

	if (IpmiTool == NULL) 
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to run ipmitool with command: %s\n", command);

		return STATUS_FAILURE;
	}

	// read in tool output
	while (fgets(output, sizeof(output)-1, IpmiTool) != NULL) 
	{
		switch(command_id)
		{
			case IPMI_FAN_INFO:
			{
				if(parse_line_fan_info(output, (server_fan_info*)result) == STATUS_FAILURE)
				{
					continue;
				}

				break;
			}

			case IPMI_POWER_INFO:
			{
				if(parse_line_power_info(output, (server_power_info*)result) == STATUS_FAILURE)
				{
					continue;
				}

				break;
			}

			default:
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Command passed to call_ipmi_tool not implemented, %i\n", command_id);

				return STATUS_FAILURE;
			}
		}
	}

	pclose(IpmiTool);

	return STATUS_SUCCESS;
}

static int call_python_script(int command_id, int arg, void* result)
{
	FILE* PythonScript;
	int status;
	int loop_status;
	int loop_done;
	char command[MAX_PYTHON_CMD_LEN];
	char output[MAX_LINE_LEN];

	if(command_id < PYTHON_SWITCH_INFO || command_id >= NUM_PYTHON_COMMANDS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid command passed to call_python_script, %i\n", command_id);

		return STATUS_FAILURE;
	}

	if(command_id == PYTHON_SWITCH_PORT_INFO && (arg > NUM_PORTS || arg < MIN_PORT_ID))
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid port id passed to call_python_script, %i\n", arg);

		return STATUS_FAILURE;
	}

	if(result == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to call_python_script!\n");

		return STATUS_FAILURE;
	}

	// construct command to call using popen
	switch(command_id)
	{
		case PYTHON_SWITCH_INFO:
		{
			char addr[20];

			if(!get_precheck_state(GET_RM_STATE, 0))
			{
				return STATUS_FAILURE;
			}

			if (get_switch_address(addr) != 0) {
				return STATUS_FAILURE;
			}

			if (snprintf(command, MAX_PYTHON_CMD_LEN, "python -c"
							 " \"import sys;"
							 " sys.path.append('/usr/lib/commonapi');"
							 " from controls.mgmt_switch import *;"
							 " switch=mgmt_switch('%s');"
							 " print switch.get_switch_status();"
							 " switch.logout()\""
							 " 2>/dev/null", addr) >= MAX_PYTHON_CMD_LEN) {
				return STATUS_FAILURE;
			}

			break;
		}

		case PYTHON_SWITCH_PORT_INFO:
		{
			char addr[20];

			if(!get_precheck_state(GET_RM_STATE, 0))
			{
				return STATUS_FAILURE;
			}

			if (get_switch_address (addr) != 0) {
				return STATUS_FAILURE;
			}

			if (snprintf(command, MAX_PYTHON_CMD_LEN, "python -c"
							 " \"import sys;  sys.path.append('/usr/lib/commonapi');" 
							 " from controls.mgmt_switch import *;"
							 " switch=mgmt_switch('%s');"
							 " print switch.get_port_link_state(%d);"
							 " switch.logout()\""
							 " 2>/dev/null", addr, arg) >= MAX_PYTHON_CMD_LEN) {
				return STATUS_FAILURE;
			}

			break;
		}

		default:
		{
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Command passed to call_python_script not implemented, %i\n", command_id);

			return STATUS_FAILURE;
		}
	}

	// run command
	PythonScript = popen(command, "r");

	if (PythonScript == NULL) 
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to run python with command: %s\n", command);

		return STATUS_FAILURE;
	}

	
	// read in tool output
	loop_done = 0;
	while (!loop_done && (fgets(output, sizeof(output), PythonScript) != NULL))
	{
		switch(command_id)
		{
			case PYTHON_SWITCH_INFO:
			{
				loop_status = parse_line_switch_info(output, (switch_info*)result);
				if (loop_status == STATUS_SUCCESS) {
					loop_done = 1;
				}

				break;
			}

			case PYTHON_SWITCH_PORT_INFO:
			{
				strtok(output, "\n");
				strcpy(((switch_port_info*)result)->port_state, output);
				loop_status = STATUS_SUCCESS;
				loop_done = 1;
				break;
			}

			default:
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Command passed to call_python_script not implemented, %i\n", command_id);
				loop_status = STATUS_FAILURE;
				loop_done = 1;
				break;
			}
		}
	}

	status = pclose(PythonScript);

	if (status != STATUS_SUCCESS) {
		return STATUS_FAILURE;
	}

	return loop_status;
}

//
// Get rack manager information
//

static int get_rack_info(rack_info* info)
{
	int throttleenabled    = 0;
	int throttleactive     = 0;
	int dcthrottleenabled  = 0;
	int dcthrottleactive   = 0;
	int result 			   = STATUS_FAILURE;

	double rackpower 	 = 0;
	double throttlelimit = 0;
	double racktemp      = 0;
	double rackhumidity  = 0;
	double rackvoltage   = 0;

	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_rack_info\n");

		return STATUS_FAILURE;
	}

	if(!get_precheck_state(GET_RM_STATE, 0))
	{
		return STATUS_FAILURE;
	}
	
	// Call OCS libraries to get rack manager information
	result = get_power(&rackpower);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager power, error: %i\n", result);
	}
	
	result = get_throttle_limit(&throttlelimit);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager throttle limit, error: %i\n", result);
	}
	
	result = get_throttle_status(&throttleenabled, &throttleactive, &dcthrottleenabled, &dcthrottleactive);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager power, error: %i\n", result);
	}

	result = hdc_get_temperature(&racktemp);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager temperature, error: %i\n", result);
	}

	result = hdc_get_humidity(&rackhumidity);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager humidity, error: %i\n", result);
	}

	result = hsc_get_inputvoltage(&rackvoltage);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get rack manager voltage, error: %i\n", result);
	}

	info->temp_celsius = racktemp;
	info->humidity_rh = rackhumidity;
	info->power_watts = rackpower;
	info->power_limit_watts = throttlelimit;
	info->power_limit_enabled = throttleenabled == 1 ? true: false;
	info->power_limit_asserted = throttleactive == 1 ? true: false;
	info->dcthrottle_enabled = dcthrottleenabled == 1 ? true: false;
	info->dcthrottle_asserted = dcthrottleactive == 1 ? true: false;
	info->voltage_volts = rackvoltage;

	return STATUS_SUCCESS;
}

//
// Get server information
//

static int get_server_info(server_info* info)
{
	int result = STATUS_FAILURE;

	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_server_info\n");

		return STATUS_FAILURE;
	}

	if(!get_precheck_state(GET_RM_STATE, 0))
	{
		return STATUS_FAILURE;
	}

	result = ocs_port_present(0, &(info->presence));

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get server presence, error: %i\n", result);
	}

	result = ocs_port_state(0, &(info->power_enabled));

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to get server power state, error: %i\n", result);
	}

	info->valid = VALID_PATTERN;

	return STATUS_SUCCESS;
}

//
// Get server fan information
//

static int get_server_fan_info(server_fan_info info[], int server_id)
{
	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_server_fan_info\n");

		return STATUS_FAILURE;
	}

	if(server_id < MIN_SERVER_ID || server_id > NUM_SERVERS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid server id passed to get_server_fan_info\n");

		return STATUS_FAILURE;
	}

	return call_ipmi_tool(IPMI_FAN_INFO, server_id, (void*) info);
}

//
// Get server fan information
//

static int get_server_power_info(server_power_info info[], int server_id)
{
	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_server_power_info\n");

		return STATUS_FAILURE;
	}

	if(server_id < MIN_SERVER_ID || server_id > NUM_SERVERS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid server id passed to get_server_power_info\n");

		return STATUS_FAILURE;
	}

	return call_ipmi_tool(IPMI_POWER_INFO, server_id, (void*) info);
}

//
// Get switch information
//

static int get_switch_info(switch_info* info)
{
	int result = STATUS_FAILURE;

	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_switch_info\n");

		return STATUS_FAILURE;
	}

	result = call_python_script(PYTHON_SWITCH_INFO, 0, info);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to call python script\n");

		return result;
	}

	return STATUS_SUCCESS;
}

//
// Get switch port information
//

static int get_switch_port_info(switch_port_info* info, int port_id)
{
	int result = STATUS_FAILURE;

	if(info == NULL)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Null struct passed to get_switch_port_info\n");

		return STATUS_FAILURE;
	}

	result = call_python_script(PYTHON_SWITCH_PORT_INFO, port_id, info);

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to call python script\n");

		return result;
	}

	return STATUS_SUCCESS;
}

//
// Log information
//

static int Telemetry_LogInformation(int component)
{
	int result = STATUS_FAILURE;

	static double sPrevPowerLimitWatts   = -1;
	static int    sPrevPowerLimitEnabled = -1;	

	char log_msg[128];	

	// Check inputs
	if (component < RACK || component > NUM_COMPONENTS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Invalid component passed to Telemetry_LogInformation, component: %i\n", component);

		return STATUS_FAILURE;
	}

	switch(component)
	{
		case RACK:
		{
			rack_info info;
			
			result = get_rack_info(&info);
			
			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get rack manager information\n");

				return result;
			}

			//Wait on file till utility releases lock
			result = ocs_lock(TELEMETRY_DAEMON);
			
			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");

				return result;
			}
			
			if(info.power_watts > info.power_limit_watts && info.power_limit_enabled)
			{
    			sprintf(log_msg, " Rack Manager | Error | Rack Power | Rack Power (%.2f) greater than limit (%.2f)", info.power_watts, info.power_limit_watts);

				telemetry_error(log_msg);
			}

			if(info.temp_celsius > MAX_RACK_TEMP)
			{
				sprintf(log_msg, " Rack Manager | Error | Temperature | Temperature (%.2f) greater than limit (%i)", info.temp_celsius, MAX_RACK_TEMP);

				telemetry_error(log_msg);
			}

			if(info.humidity_rh > MAX_RACK_HUMIDITY)
			{
				sprintf(log_msg, " Rack Manager | Error | Humidity | Humidity (%.2f) greater than limit (%i)", info.humidity_rh, MAX_RACK_HUMIDITY);

				telemetry_error(log_msg);
			}

			if(info.humidity_rh < MIN_RACK_HUMIDITY)
			{
				sprintf(log_msg, " Rack Manager | Error | Humidity | Humidity (%.2f) less than limit (%i)", info.humidity_rh, MIN_RACK_HUMIDITY);

				telemetry_error(log_msg);
			}

			if(info.power_limit_watts != sPrevPowerLimitWatts && sPrevPowerLimitWatts != -1)
			{
				sprintf(log_msg, " Rack Manager | Warning | Rack Power Limit | Changed: Previous (%.2f) - Current (%.2f)", sPrevPowerLimitWatts, info.power_limit_watts);

				telemetry_warning(log_msg);
			}

			if((info.power_limit_enabled ? 1 : 0) != sPrevPowerLimitEnabled && sPrevPowerLimitEnabled != -1)
			{
				sprintf(log_msg, " Rack Manager | Warning | Rack Power Limit Enabled | Changed: Previous (%s) - Current (%s)", sPrevPowerLimitEnabled ? "On" : "Off", 
					info.power_limit_enabled ? "On" : "Off");

				telemetry_warning(log_msg);
			}

			sprintf(log_msg, " Rack Manager | Info | Temperature | %.2f", info.temp_celsius);
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Humidity | %.2f", info.humidity_rh);
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Voltage | %.2f", info.voltage_volts);
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack Power | %.2f", info.power_watts);
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack Power Limit | %.2f", info.power_limit_watts);
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack Power Limit Enabled | %s", info.power_limit_enabled ? "True" : "False");
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack Power Limit Asserted | %s", info.power_limit_asserted ? "True" : "False");
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack DC Throttle Enabled | %s", info.dcthrottle_enabled ? "True" : "False");
			telemetry_info(log_msg);

			sprintf(log_msg, " Rack Manager | Info | Rack DC Throttle Asserted | %s", info.dcthrottle_asserted ? "True" : "False");
			telemetry_info(log_msg);

			sPrevPowerLimitEnabled = (info.power_limit_enabled ? 1 : 0);
			sPrevPowerLimitWatts = info.power_limit_watts;
			
			ocs_unlock(TELEMETRY_DAEMON);
			
			break;
		}

		case SERVER:
		{
			server_info info;

			info.valid = 0;

			result = get_server_info(&info);

			if(result != STATUS_SUCCESS || info.valid != VALID_PATTERN)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get server information\n");

				return result;
			}
	
			//Wait on file till utility releases lock
			result = ocs_lock(TELEMETRY_DAEMON);
	
			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");
	
				return result;
			}

			sprintf(log_msg, " Servers | Info | Presence | 0x%llX", info.presence);
			telemetry_info(log_msg);

			sprintf(log_msg, " Servers | Info | Power States | 0x%llX", info.power_enabled);
			telemetry_info(log_msg);
	
			ocs_unlock(TELEMETRY_DAEMON);

			break;
		}

		case SERVER_FAN:
		{
			int fan_id;
			int server_id = MIN_SERVER_ID;
			char speed[MAX_FAN_SPEED_LEN];
			char speeds[MAX_FAN_SPEEDS_LEN]; 
			server_fan_info info[NUM_FANS];
			
			for(; server_id <= NUM_SERVERS; ++server_id)
			{
				speed[0] = '\0';
				speeds[0] = '\0';

				for(fan_id = MIN_FAN_ID; fan_id < NUM_FANS; ++fan_id)
				{
					info[fan_id].valid = 0;
				}

				result = get_server_fan_info(info, server_id);

				if(result != STATUS_SUCCESS)
				{
					log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get server %i fan information\n", server_id);

					return result;
				}

				for(fan_id = MIN_FAN_ID; fan_id < NUM_FANS; ++fan_id)
				{
					if(info[fan_id].valid != VALID_PATTERN)
					{
						sprintf(speed, "x");
					}
					else
					{
						sprintf(speed, "%d", info[fan_id].speed_rpm);
					}

					if(fan_id > MIN_FAN_ID)
					{
						strcat(speeds, ":");
					}

					strcat(speeds, speed);
				}

				//Wait on file till utility releases lock
				result = ocs_lock(TELEMETRY_DAEMON);

				if(result != STATUS_SUCCESS)
				{
					log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");
		
					return result;
				}

				sprintf(log_msg, " Server %i Fans | Info | Fans Speed | %s", server_id, speeds);
				telemetry_info(log_msg);	
				
				ocs_unlock(TELEMETRY_DAEMON);
			}
			
			break;
		}

		case SERVER_POWER:
		{
			int server_id = MIN_SERVER_ID;
			char reading[MAX_SERVER_PWR_LEN];
			char readings[MAX_SERVER_PWRS_LEN]; 
			server_power_info info;

			for(; server_id <= NUM_SERVERS; ++server_id)
			{
				reading[0] = '\0';

				result = get_server_power_info(&info, server_id);

				if(result != STATUS_SUCCESS)
				{
					log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get server %i power information\n", server_id);

					return result;
				}

				if(info.valid != VALID_PATTERN)
				{
					sprintf(reading, "x");
				}
				else
				{
					sprintf(reading, "%d", info.power_reading);
				}

				if(server_id > MIN_SERVER_ID)
				{
					strcat(readings, ":");
				}

				strcat(readings, reading);	
			}

			//Wait on file till utility releases lock
			result = ocs_lock(TELEMETRY_DAEMON);

			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");
	
				return result;
			}

			sprintf(log_msg, " Servers | Info | Power Readings | %s", readings);
			telemetry_info(log_msg);	
			
			ocs_unlock(TELEMETRY_DAEMON);
			
			break;
		}

		case SWITCH:
		{
			switch_info info;

			result = get_switch_info(&info);

			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get switch information\n");

				return result;
			}
		
			//Wait on file till utility releases lock
			result = ocs_lock(TELEMETRY_DAEMON);

			if(result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");

				return result;
			}

			sprintf(log_msg, " Switch | Info | Temperature | %d ", info.temp_celsius);
			telemetry_info(log_msg);

			sprintf(log_msg, " Switch | Info | Uptime | %.02f ", info.uptime);
			telemetry_info(log_msg);

			sprintf(log_msg, " Switch | Info | Main Power State | %s ", info.power_state);
			telemetry_info(log_msg);

			sprintf(log_msg, " Switch | Info | Redundant Power State | %s ", info.redundant_power_state);
			telemetry_info(log_msg);

			sprintf(log_msg, " Switch | Info | Temperature Sensor State | %s ", info.temp_sensor_state);
			telemetry_info(log_msg);
		
		 	ocs_unlock(TELEMETRY_DAEMON);

			break;
		}

		case SWITCH_PORT:
		{
			switch_port_info info;

			int port_id = MIN_PORT_ID;

			for(; port_id <= NUM_PORTS; ++port_id)
			{
				result = get_switch_port_info(&info, port_id);

				if(result != STATUS_SUCCESS)
				{
					log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Unable to get switch port %i information\n", port_id);

					return result;
				}
		
				//Wait on file till utility releases lock
				result = ocs_lock(TELEMETRY_DAEMON);
	
				if(result != STATUS_SUCCESS)
				{
					log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: OcsTelemetry_Daemon: Unable to acquire lock to telemetry file.\n");
	
					return result;
				}

				sprintf(log_msg, " Switch Port %i | Info | Link State | %s ", port_id, info.port_state);
				telemetry_info(log_msg);

				ocs_unlock(TELEMETRY_DAEMON);

			}

			break;
		}
	}
	
	return STATUS_SUCCESS;
}

//
// Telemetry initialization function
//

static int Telemetry_Init(void)
{
	FILE *fp;
	int result;
	struct stat st;
	char permissions[] = "0666";
    mode_t mode = strtol(permissions, 0, 8);
    bool lockexist = (stat(LOCKFILE, &st) == 0);
    bool log0exist = (stat(LOGFILE0, &st) == 0);
    bool log1exist = (stat(LOGFILE1, &st) == 0);
    bool log2exist = (stat(LOGFILE2, &st) == 0);
	
	// Initialize ocslog 
	log_init(INFO_LEVEL);

	// Initialize zlog with the telemetry config file and create internal telemetry category
	result = dzlog_init (ZLOG_CONF, "telemetry");

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to initialize zlog, check file indicated by ZLOG_PROFILE_ERROR to find details\n");

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
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to set permissions for the rotate lock file\n");
		}
	}
	
	// If this process created log file, attempt to set permissions
	if(!log0exist)
	{
		// Ensure all users have RW permission to log file 
		if(chmod(LOGFILE0, mode) < 0)
		{
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to set permissions for log file 0\n");
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
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to set permissions for log file 1\n");
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
			log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to set permissions for log file 2\n");
		}
	}

	return STATUS_SUCCESS;
}


//
// Main daemon loop
//

int main()
{
	int result = STATUS_FAILURE;
	
	// Initialize telemetry module
	result = Telemetry_Init();

	if(result != STATUS_SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to initialize telemetry module\n");
		
		return result;
	}

	while(1)
	{
		uint i = RACK; 
		
		for(; (i < NUM_COMPONENTS); ++i)
		{
			result = Telemetry_LogInformation(i);

			if (result != STATUS_SUCCESS)
			{
				log_err(UNKNOWN_ERROR, "OcsTelemetry_Daemon: Failed to log information for component %i\n", i);
			}
		}	

		// sleep before another pass
		sleep(POLL_INTERVAL_SEC);
	}

	// Release zlog memory and close open files 
	zlog_fini();

	return STATUS_SUCCESS;
}
