// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <pthread.h>
#include <errno.h>
#include <sys/stat.h>
#include <time.h>
#include "pre-checks.h"
#include "auth.h"
#include "ocslog.h"
#include "util.h"
#include "ocsgpioaccess.h"

#define DEVICE_FW_LOAD_DELAY_SECS 	40

#define SUCCESS 0
#define UNKNOWN_ERROR -1
#define FAILURE -2
#define API_AUTH_FAILURE -3
#define DEVICE_NOT_PRESENT -4
#define DEVICE_NOT_POWERED -5
#define DEVICE_FW_NOT_LOADED -6
#define USERNAME_NOT_RECOGNIZED -7
#define USERGROUP_NOT_RECOGNIZED -8
#define CMDNAME_NOT_RECOGNIZED -9
#define DEVICE_PRESENT_STATE_UNKNOWN -10
#define DEVICE_POWER_STATE_UNKNOWN -11
#define DEVICE_FWLOAD_STATE_UNKNOWN -12
#define GPIO_LIBRARY_LOAD_FAILED -13 
#define UNKNOWN_RM_MODE -14

PACK(typedef struct
{
	cmd_name_t cmd_name;
	int access_group_id; /* Group id with access for the command */
	byte_t is_blade_cmd; /* when 1, check for blade present */
})cmd_config_t;

/*
 * NOTE: Array INDEXING ORDER should match the COMMAND_NAME enum listing in .h file
 */
const cmd_config_t cmd_config[NUM_COMMANDS] =
{
	(cmd_config_t) {GET_RM_STATE, OCS_USER_ID, 0},
	(cmd_config_t) {SET_RM_STATE, OCS_OPERATOR_ID, 0},
	(cmd_config_t) {SET_RM_CONFIG, OCS_ADMIN_ID, 0},

	(cmd_config_t) {GET_BLADE_STATE, OCS_USER_ID, 1},
	(cmd_config_t) {SET_BLADE_STATE, OCS_OPERATOR_ID, 1},
	(cmd_config_t) {SET_BLADE_CONFIG, OCS_ADMIN_ID, 1},
};

/* 
 * Get app-specific error message 
 * Log the error via ocslog
 */
void log_fnc_err_msg(int error_no) {
	char error_str[PRECHECK_ERROR_STRING_LENGTH];
	get_app_error(error_no, error_str);
	log_fnc_err(error_no, "Precheck: %s", error_str);
	return;
}

/* 
 * Check API-level authorization 
 */
int api_authorization_check(int user_group_id, cmd_name_t cmd_name) {	
	/* 
	 * Get groupid with access to command 
	 * Compare lowest access groupid with that of user 
	 */
	if(cmd_config[cmd_name].access_group_id < user_group_id)
		return API_AUTH_FAILURE;
	
	return SUCCESS;
}

/*
 * Check whether device firmware is loaded
 * Return SUCCESS or 0 when firmware load is complete and device is ready for further transactions
 * Return FAILURE or non zero value when firmware load is pending
 */
int check_firmware_load(int device_id) {
	unsigned long blade_uptime;
	
	/* Check for blade present */
	if(ocs_port_uptime (device_id, &blade_uptime)==SUCCESS) {
		if(blade_uptime< DEVICE_FW_LOAD_DELAY_SECS)
			return DEVICE_FW_NOT_LOADED;
	}
	else
		return DEVICE_FWLOAD_STATE_UNKNOWN;
	
	return SUCCESS;
}

/*
* Get firmware decompression delay for blade/server
* Parameters:
	* param1: integer device id
	* param2: return parameter with firmware decompression delay remaining time 
*/
int get_server_fwready_delay(int device_id, int *fwreadydelay) {
	unsigned long blade_uptime;
	
	/* Check for blade present */
	if(ocs_port_uptime(device_id, &blade_uptime)==SUCCESS) {
		if(blade_uptime< DEVICE_FW_LOAD_DELAY_SECS)
			*fwreadydelay = (int)(DEVICE_FW_LOAD_DELAY_SECS - blade_uptime);
		else
			*fwreadydelay = 0;
	}
	else
		return DEVICE_FWLOAD_STATE_UNKNOWN;
	
	return SUCCESS;
}

/*
 * Get Rack manager mode
 * Paramters:
  	  * param1: rm_mode_t (integer) pointer with the value of enum role
  	  	  * Value 0: PMDU Rack Manager
  	  	  * Value 1: Standalone Rack Manager
  	  	  * Value 2: Row Manager
 * Return
 	 * 0 on success
 	 * >0 for system errors
 	 * <0 for app specific errors
 */
int get_rm_mode(int *rm_mode) {
	/* Check for RM mode */
	unsigned int modeval;
	if(ocs_get_mode (0, &modeval)==SUCCESS) {
		if(modeval==0) { /* Checking for WCS PMDU RM */
			*rm_mode = PMDU_RACKMANAGER;
			return SUCCESS;
		}
		else if(modeval == 2) { /* Checking for MTE benchtop dev TFB board RM */
			*rm_mode = TFB_DEV_BENCHTOP;
			return SUCCESS;
		}
		else { /* continue getting port present to determine standalone_rackmanager or rowmanager */
			unsigned long long blade_presentstate;
			
			/* Check for blade present */
			if(ocs_port_present (0, &blade_presentstate)==SUCCESS) {
				if(blade_presentstate <= 0xFFFFFF) {
					*rm_mode = STANDALONE_RACKMANAGER;
					return SUCCESS;
				}
				else if(blade_presentstate > 0xFFFFFF && blade_presentstate <= 0xFFFFFF000000) {
					*rm_mode = ROWMANAGER;
					return SUCCESS;
				}
			}			
		}
	}
	return UNKNOWN_RM_MODE;
}

int blade_check(cmd_name_t cmd_name, int deviceid, rm_mode_t rm_mode) {
	if(cmd_name < 0 || cmd_name >= NUM_COMMANDS) {
		log_fnc_err_msg(CMDNAME_NOT_RECOGNIZED);
		return CMDNAME_NOT_RECOGNIZED;
	}

	/* if blade checks not required, return immediately */
	if(cmd_config[cmd_name].is_blade_cmd !=1)
		return SUCCESS;
	
	/* Check Port Presence/power-state only for PMDU_RACKMANAGER */
	if(rm_mode != PMDU_RACKMANAGER) {
		return SUCCESS;
	}
	
	unsigned long long blade_state;
	unsigned long long blade_presence;

	/* Check for blade present */
	if(ocs_port_present(deviceid, &blade_presence)==SUCCESS) {
		if(blade_presence == 0)
			return DEVICE_NOT_PRESENT;
	}
	else
	{
		log_fnc_err_msg(DEVICE_PRESENT_STATE_UNKNOWN);
		return SUCCESS;
	}
	
	/* check for blade power on */
	if(ocs_port_state(deviceid, &blade_state)==SUCCESS) {
		if(blade_state == 0)
			return DEVICE_NOT_POWERED;
	}
	else
	{
		log_fnc_err_msg(DEVICE_POWER_STATE_UNKNOWN);
		return SUCCESS;
	}

	int ret = DEVICE_NOT_PRESENT;

	if(deviceid == 0)
	{
		for(deviceid = 1; deviceid < 48 && blade_presence > 0 && blade_state > 0;
			++deviceid, blade_presence >>=1, blade_state >>=1)
		{
			if((blade_presence & 0x01) && (blade_state & 0x01))
			{
				/*check for blade firmware load delay*/
				ret = check_firmware_load(deviceid);
				if(ret == DEVICE_FWLOAD_STATE_UNKNOWN || ret == GPIO_LIBRARY_LOAD_FAILED)
				{
					log_fnc_err_msg(ret);
					return SUCCESS;
				}
			}
		}

		return ret;
	}
	else
	{
		/* check for blade firmware load delay */
		ret = check_firmware_load(deviceid);
		if(ret == DEVICE_FWLOAD_STATE_UNKNOWN || ret == GPIO_LIBRARY_LOAD_FAILED)
		{
			log_fnc_err_msg(ret);
			return SUCCESS;
		}
		else 
			return ret; 
	}
}

/*
* Does pre checks 
	* api-level authorization,  
	* blade-present, 
	* blade-on, 
	* blade-fwload-delay
* Parameters:
	* param1: integer unix user_group_id
    * param2: enum cmd_name_t command name id
    * param3: interger device id 
    * param4: rm mode
* Returns
	* 0 on success
	* >0 for system errors
	* <0 for app specific errors
*/
int pre_check(int user_group_id, cmd_name_t cmd_name, int deviceid, rm_mode_t rm_mode) {
	int rc;
			
	if(cmd_name < 0 || cmd_name >= NUM_COMMANDS) {
		log_fnc_err_msg(CMDNAME_NOT_RECOGNIZED);
		return CMDNAME_NOT_RECOGNIZED;
	}

	/* Check API-level authorization */
	if((rc=api_authorization_check(user_group_id, cmd_name))!=SUCCESS) {
		log_fnc_err_msg(rc);
		return rc;
	}
	
	/* Check blade-specific checks */
	if((rc=blade_check(cmd_name, deviceid, rm_mode))!=SUCCESS) {
		log_fnc_err_msg(rc);
		return rc;
	}
	
	return SUCCESS;
}

/*
* Get application specific error string
* Called only on error or non-zero response from pre_check()
* Parameters:
	* param1: error_no returned by the pre_check() API
    * param2: error_str is error string passed by reference, the caller allocates it for PRECHECK_ERROR_STRING_LENGTH bytes 
* Always returns success
*/
int get_app_error(int error_no, char *error_str) {
	switch(error_no) {
		case API_AUTH_FAILURE:
			strcpy(error_str, "API-level authorization failed.");
			break;
		case DEVICE_NOT_PRESENT:
			strcpy(error_str, "Device is not present.");
			break;
		case DEVICE_NOT_POWERED:
			strcpy(error_str, "Device is not powered on.");
			break;
		case DEVICE_FW_NOT_LOADED:
			strcpy(error_str, "Device firmware is loading, retry again.");
			break;
		case USERNAME_NOT_RECOGNIZED:
			strcpy(error_str, "Username not recognized.");
			break;
		case USERGROUP_NOT_RECOGNIZED:
			strcpy(error_str, "Usergroup not a recoginized OCS group.");
			break;	
		case DEVICE_PRESENT_STATE_UNKNOWN:
			strcpy(error_str, "Device presence state is unknown.");
			break;	
		case DEVICE_POWER_STATE_UNKNOWN:
			strcpy(error_str, "Device power state is unknown.");
			break;	
		case DEVICE_FWLOAD_STATE_UNKNOWN:
			strcpy(error_str, "Device firmware load state is unknown.");
			break;	
		case GPIO_LIBRARY_LOAD_FAILED:
			strcpy(error_str, "Cannot open libocsgpio.so.");
			break;
		case UNKNOWN_RM_MODE:
			strcpy(error_str, "Cannot determine device management mode.");
			break;
		default:
			strcpy(error_str, "Unknown fault occurred.");
			break;
	}
	return SUCCESS;
}
