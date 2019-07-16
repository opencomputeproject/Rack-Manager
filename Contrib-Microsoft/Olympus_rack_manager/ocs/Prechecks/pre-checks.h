// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#define PRECHECK_ERROR_STRING_LENGTH 64

/* 
 * Enum with all command categories
 */
typedef enum COMMAND_NAME
{
	  GET_RM_STATE = 0, /* All Get RM commands including port power/present (user) */
	  SET_RM_STATE = 1, /* All Set RM commands including port power/present (operator) */
	  SET_RM_CONFIG = 2, /* firmware update, networking, rack power cap etc. (admin) */
					
	  GET_BLADE_STATE = 3, /* All Get blade IPMI commands (user) */
	  SET_BLADE_STATE = 4, /* All Set blade IPMI commands (operator) */
	  SET_BLADE_CONFIG = 5, /* firmware update of blade components, blade power cap, serial session etc., (admin?) */

	  NUM_COMMANDS = 6,
}cmd_name_t;

/* 
 * Enum with all Rack/Row Manager modes/roles 
 */
typedef enum RM_MODE
{
	  PMDU_RACKMANAGER = 0, 
	  STANDALONE_RACKMANAGER = 1, 
	  ROWMANAGER = 2,
	  UNKNOWN_RM_MODE = 3,
	  TFB_DEV_BENCHTOP = 4,
}rm_mode_t;

/*
* Does pre checks 
	* api-level authorization,  
	* blade-present, 
	* blade-on, 
	* blade-fwload-delay
* Parameters:
	* param1: unt unix user group id
    * param2: enum cmd_name_t command name id
    * param3: integer device id
    * param4: rm mode 
* Returns
	* 0 on success
	* >0 for system errors
	* <0 for app specific errors
*/
int pre_check(int, cmd_name_t, int, rm_mode_t);

/*
* Pre check blade availability
	* blade-present,
	* blade-on,
	* blade-fwload-delay
* Parameters:
    * param2: enum cmd_name_t command name id
    * param3: integer device id
    * param4: rm mode
* Returns
	* 0 on success
	* >0 for system errors
	* <0 for app specific errors
*/
int blade_check(cmd_name_t, int, rm_mode_t);

/*
* Check if the user is authorized to execute a command
	* api-level authorization
* Parameters:
	* param1: unt unix user group id
    * param2: enum cmd_name_t command name id
* Returns
	* 0 on success
	* >0 for system errors
	* <0 for app specific errors
*/
int api_authorization_check(int, cmd_name_t);

/*
 * Get Rack manager mode
 * Paramters:
  	  * param1: integer pointer with the value of enum role
  	  	  * Value 0: PMDU Rack Manager
  	  	  * Value 1: Standalone Rack Manager
  	  	  * Value 2: Row Manager
 * Return
 	 * 0 on success
 	 * >0 for system errors
 	 * <0 for app specific errors
 */
int get_rm_mode(int*);

/*
* Get application specific error string
* Called only on error or non-zero response from pre_check()
* Parameters:
	* param1: error_no returned by the pre_check() API
    * param2: error_str is error string passed by reference, the caller allocates it for PRECHECK_ERROR_STRING_LENGTH bytes 
*/
int get_app_error(int, char*);

/*
* Get firmware decompression delay for blade/server
* Parameters:
	* param1: integer device id
	* param2: return parameter with firmware decompression delay remaining time 
*/
int get_server_fwready_delay(int, int*);
