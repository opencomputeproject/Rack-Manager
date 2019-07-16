// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "ocslog.h"
#include "hsc-lib.h"
#include "i2c-lib.h"

#define I2C_ADAPTER		0
#define I2C_SLAVE_ADDR		0x10	
#define NUM_I2C_COMMANDS 	4

PACK(typedef struct
{
        byte_t reg;
        byte_t num_bytes_request;
        byte_t num_bytes_response;
        char* name;
        byte_t delay_ms;
})i2c_config_t;

/*
 * NOTE: The enum order should MATCH the i2c_config array for indexing 
 */
typedef enum I2cCommands
{
	GET_POWER,
	GET_INPUTVOLTAGE,
	GET_STATUS,
	CLEAR_FAULTS,
}i2c_cmd_t;

const i2c_config_t i2c_config[NUM_I2C_COMMANDS] =
{
	(i2c_config_t) {0xD2, 1, 2, "GetPower", 0},
	(i2c_config_t) {0x88, 1, 2, "GetInputVoltage", 0},
	(i2c_config_t) {0x79, 1, 2, "GetStatus", 0},
	(i2c_config_t) {0x03, 1, 0, "ClearFaults", 0},
};

/*
 * Clear faults
 */
int hsc_clear_faults()
{
	i2c_cmd_t index = CLEAR_FAULTS;
	char request[1] =  {(char)i2c_config[index].reg};
	
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request, 
		i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, NULL)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return FAILURE;
	}
	
	return SUCCESS;
}

/*
 * Get power status
 */
int hsc_get_status(hsc_status_t* hsc_response)
{
	i2c_cmd_t index = GET_STATUS;
	char request[1] =  {(char)i2c_config[index].reg};
	hsc_status_t responsepacket; 
	
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request, 
		i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, &responsepacket)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return FAILURE;
	}
	
	*hsc_response = responsepacket; 
	
	return SUCCESS;
}

/* 
 * Convert power
 * Return 1/m * (y * 10^-r -b), where y is the read value
 * 		 all values are in 2's compliment
 */
double convert_power(byte_t low_byte, byte_t high_byte)
{
	// Looks like CL is connected to VDD, therefore using appropriate coefficients
	int Rs = 5;
	int m = 369*Rs; // 736 if CL=VDD, 369 if CL=GND
	int b = -1900; // -3300 if CL=VDD, -1900 if CL=GND
	int r = -2;
	
	int y = low_byte | high_byte << 8;
	return ((y * pow(10,-r))-b)/m;
}

/*
 * Read Power 
 */
int hsc_get_power(double* power)
{
	i2c_cmd_t index = GET_POWER;
	char request[1] =  {(char)i2c_config[index].reg};
	char response[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return FAILURE;
	}

	*power = convert_power(response[0], response[1]);

	return SUCCESS;
}

/* 
 * Convert voltage
 * Return 1/m * (y * 10^-r -b), where y is the read value
 * 		all values are in 2's compliment
 */
double convert_voltage(byte_t low_byte, byte_t high_byte)
{
	int m = 22070;
	int b = -1800;
	int r = -2;
		
	int y = low_byte | high_byte << 8;
	return ((y * pow(10,-r))-b)/m;
}

/*
 * Get input voltage
 */
int hsc_get_inputvoltage(double* voltage)
{
	i2c_cmd_t index = GET_INPUTVOLTAGE;
	char request[1] =  {(char)i2c_config[index].reg};
	char response[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return FAILURE;
	}
	
	*voltage = convert_voltage(response[0], response[1]);

	return SUCCESS;
}
