// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <stdbool.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

#include "cl-helper.h"
#include "ocslog.h"
#include "util.h"
#include "pmic.h"

#define DEVICE_NAME             "Power Management IC (TPS65218)"
#define I2C_ADAPTER             0
#define I2C_SLAVE_ADDR          0x24    
#define NUM_I2C_COMMANDS 	4
#define NUM_USER_COMMANDS 	4

PACK(typedef struct
{
        byte_t    coincell_state :2;
        byte_t    statemachine_state :2;
        byte_t    pushbutton_state :1;
        byte_t    ac_state :1;
        byte_t    eeprom_state :1;
        byte_t    fseal_state :1;
})status_t;

PACK(typedef struct
{
        byte_t reg;
        byte_t num_bytes_request;
        byte_t num_bytes_response;
        char* name;
        byte_t delay_ms;
})i2c_config_t;

// Define minor and major version which will be overridden in the I2C device header files
const int version_major = 1;
const int version_minor = 2;
const int version_revision = 0;
const int version_build = 0;

#define VERSION_INFO \
		log_out("version: %d.%d \n", version_major, version_minor); \
		log_out("build:   %d.%d \n", version_revision, version_build); \
		log_out("\n"); 

// NOTE: The enum order should MATCH the i2c_config array for indexing
typedef enum I2cCommands
{
        GET_STATUS,
        PASSWORD,
        GET_CONTROL,
        SET_CONTROL,
}i2c_cmd_t;

const i2c_config_t i2c_config[NUM_I2C_COMMANDS] =
{
	(i2c_config_t) {0x05, 1, 1, "GetStatus", 0},
	(i2c_config_t) {0x10, 2, 0, "SetPassword", 0},
	(i2c_config_t) {0x06, 1, 1, "GetControl", 0},
	(i2c_config_t) {0x06, 2, 0, "SetControl", 0},
};

const cmd_config_t cmd_config[NUM_USER_COMMANDS] = 
{
	(cmd_config_t) {0, "GetStatus", cmd_get_status},
	(cmd_config_t) {0, "SetFseal", cmd_set_fseal},
	(cmd_config_t) {0, "Initialize", cmd_initialize},
	(cmd_config_t) {0, "-v", cmd_version},
};

/*
 * Method to return utility version information
 */
void cmd_version()
{
	VERSION_INFO
}

/*
 * Initialize to read coin cell status
 */
void cmd_initialize()
{
	i2c_cmd_t index = GET_CONTROL;
	char get_request[1]; 
	get_request[0] = (char)i2c_config[index].reg;
	char response;
    if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, get_request,
            i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, &response)<0)
    {
            log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
            return UNKNOWN_ERROR;
    }
    
    index = SET_CONTROL;
	char set_request[2]; 
	set_request[0] = (char)i2c_config[index].reg;
    
    set_request[1] = response | 0x1;
    if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, set_request,
            i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, NULL)<0)
    {
            log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
            return UNKNOWN_ERROR;
    }
    
    log_out("%s Initialized.\n", DEVICE_NAME);	
}

/*
 * Internal method for set password - to set fseal to 1
 */
int set_password()
{
	i2c_cmd_t index = PASSWORD;
	char request[2]; 
	request[0] = (char)i2c_config[index].reg;
	
	request[1] = 0xB1;
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, NULL)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}

	request[1] = 0xFE;
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, NULL)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}
	
	request[1] = 0xA3;
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, NULL)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}
	return SUCCESS;
}

/*
 * Initialize PMIC by writing password sequence 3 times
 * This will be performed once and only during MTE
 */
void cmd_set_fseal()
{
	if(set_password()!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Initialization Failed for %s.\n", DEVICE_NAME);
		return;
	}
	
	if(set_password()!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Initialization Failed for %s.\n", DEVICE_NAME);
		return;
	}
	
	if(set_password()!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Initialization Failed for %s.\n", DEVICE_NAME);
		return;
	}
	log_out("%s FSEAL set to 1.\n", DEVICE_NAME);
}

/*
 * Get status of PMIC
 */
void cmd_get_status()
{
	i2c_cmd_t index = GET_STATUS;
    char request[1] =  {(char)i2c_config[index].reg};
	status_t response_packet;
	status_t* pmic_response = &response_packet;
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, (char*)pmic_response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return;
	}

	log_out("GetStatus Succeeded for %s\n", DEVICE_NAME);

	log_out("FRESH SEAL: %s\n", (pmic_response->fseal_state==0) ? "FSEAL is fresh" : "FSEAL is broken");
	log_out("EEPROM: %s\n", (pmic_response->eeprom_state==0) ? "EEPROM is factory default" : "EEPROM has changed");
	log_out("AC: %s\n", (pmic_response->ac_state==0) ? "AC_DET input is inactive" : "AC_DET input is active");
	log_out("Push Button: %s\n", (pmic_response->pushbutton_state==0) ? "Push Button input is inactive" : "Push Button input is active");
	char* str;
	if(pmic_response->statemachine_state== 0)
			str = "PMIC is in transitional state";
	else if(pmic_response->statemachine_state== 1)
			str = "PMIC is in WAIT_PWR_EN state";
	else if(pmic_response->statemachine_state== 2)
			str = "PMIC is in ACTIVE state";
	else 
			str = "PMIC is in SUSPEND state";
	log_out("State Machine: %s\n", str);

	if(pmic_response->coincell_state== 0)
			str = "Coin cell is not present or approaching end-of-life (EOL)";
	else if(pmic_response->coincell_state== 1)
			str = "Coin cell voltage is LOW";
	else if(pmic_response->coincell_state== 2)
			str = "Coin cell voltage is GOOD";
	else
			str = "Coin cell voltage is IDEAL";
	log_out("Coin Cell: %s\n", str);

	return;
}

/*
 * Main method for PMIC
 */
int main(int argc, char *argv[])
{
	log_init (INFO_LEVEL);

	if(argc<2)
	{
		log_out("Expected arguments, Mandatory:'cmd-name'\n");
		display_cmd_help(cmd_config, NUM_USER_COMMANDS, NULL);
		return UNKNOWN_ERROR;
	}

	// populate global user command and list pointers	
	call_cmd_method(cmd_config, NUM_USER_COMMANDS, argv[1], argc-2);	
	return 0;
}
