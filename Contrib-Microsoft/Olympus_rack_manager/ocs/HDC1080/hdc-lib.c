// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <math.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

#include "hdc-lib.h"
#include "ocslog.h"
#include "i2c-lib.h"
#include "util.h"

#define I2C_ADAPTER             0
#define I2C_SLAVE_ADDR          0x40
#define NUM_I2C_COMMANDS        4

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
	GET_TEMPERATURE,
	GET_HUMIDITY,
	GET_CONFIGURATION,
	SET_CONFIGURATION,
}i2c_cmd_t;

const i2c_config_t i2c_config[NUM_I2C_COMMANDS] = 
{
	(i2c_config_t) {0x00, 1, 2, "GetTemperature", 20},
	(i2c_config_t) {0x01, 1, 2, "GetHumidity", 20},
	(i2c_config_t) {0x02, 1, 2, "GetConfiguration", 0},
	(i2c_config_t) {0x02, 3, 0, "SetConfiguration", 0},
};

/* Convert 2 bytes of temperature data to celcius */
double get_temperature_in_celcius(byte_t* temperature_bytes)
{
	// 14-bit resolution set during initialization (2 bits LSB ignored)
	// Convert 2 bytes to integer
	int temperature = (int) (temperature_bytes[0] << 8 | temperature_bytes[1]);
	return (double)((temperature / pow(2, 16)) * 165 - 40);
}

/* Convert 2 bytes of humidty data to %RH */
double get_humidity_in_rh(byte_t* humidity_bytes)
{
	// 14-bit resolution set during initialization (2 bits LSB ignored)
	// Convert 2 bytes to integer
	int humidity = (int) (humidity_bytes[0] << 8 | humidity_bytes[1]);
	return (double)((humidity / pow(2, 16)) * 100);
}

/*
 * Initialize configuration register for HDC sensor
 * Enable reading humidity and temperature\
 * Return status code
 */
int hdc_initialize() 
{
	i2c_cmd_t index = GET_CONFIGURATION;
	
	// Read Config register value
	char request[1] =  {(char)i2c_config[index].reg};
	char response[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}

	// Humidity/temperature resolution, aquisition mode and heater activate setting
	index = SET_CONFIGURATION;
	char setRequest[3];
	setRequest[0]=(char)i2c_config[index].reg;
	memcpy(setRequest+1, response, 2);
	setRequest[2] = (byte_t) ((setRequest[2] & 0xE8) | 0x10);
	
	// Write Config register value
	char setResponse[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, setRequest,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, setResponse)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}

	return SUCCESS;
}

/*
 * Get temperature 
 * Return status code
 */ 
int hdc_get_temperature(double* temperature) 
{
	i2c_cmd_t index = GET_TEMPERATURE;
	char request[1] =  {(char)i2c_config[index].reg};
	char response[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}

	*temperature = get_temperature_in_celcius((byte_t*)response);
	return SUCCESS;
}

/*
 * Get humidity
 * Return status code
 */
int hdc_get_humidity(double* humidity) 
{
	i2c_cmd_t index = GET_HUMIDITY;
	char request[1] =  {(char)i2c_config[index].reg};
	char response[i2c_config[index].num_bytes_response];
	if(i2c_read_after_write(I2C_ADAPTER, I2C_SLAVE_ADDR, i2c_config[index].num_bytes_request, request,
			i2c_config[index].delay_ms, i2c_config[index].num_bytes_response, response)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C ReadAfterWrite Failed for %s.\n", DEVICE_NAME);
			return UNKNOWN_ERROR;
	}

	*humidity = get_humidity_in_rh((byte_t*)response);
	return SUCCESS;
}
