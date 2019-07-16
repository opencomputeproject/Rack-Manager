// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "cl-helper.h"
#include "hdc-util.h"
#include "hdc-lib.h"
#include "ocslog.h"

#define NUM_USER_COMMANDS       4

// Define minor and major version which will be overridden in the I2C device header files
const int version_major = 1;
const int version_minor = 2;
const int version_revision = 0;
const int version_build = 0;

#define VERSION_INFO \
		log_out("version: %d.%d \n", version_major, version_minor); \
		log_out("build:   %d.%d \n", version_revision, version_build); \
		log_out("\n"); 

const cmd_config_t cmd_config[NUM_USER_COMMANDS] =
{
	(cmd_config_t) {0, "GetTemperature", cmd_get_temperature},
	(cmd_config_t) {0, "GetHumidity", cmd_get_humidity},
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
 * Method to initialize HDC sensor - typically called once after system boot
 */
void cmd_initialize()
{
	if(hdc_initialize()==SUCCESS)
		log_out("Initialization Succeeded for %s\n", DEVICE_NAME);
	else
		log_fnc_err(UNKNOWN_ERROR, "Initialization failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Method to get temperature in C
 */
void cmd_get_temperature()
{
	double temperature;
	if(hdc_get_temperature(&temperature)==SUCCESS)
	{
        	log_out("GetTemperature Succeeded for %s\n", DEVICE_NAME);
        	log_out("Temperature in C (%f)\n", temperature);
	}
	else 
		log_fnc_err(UNKNOWN_ERROR, "Get Temperature failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Method to return humidity in RH
 */
void cmd_get_humidity()
{
        double humidity;
        if(hdc_get_humidity(&humidity)==SUCCESS)
        {
        	log_out("Get Humidity Succeeded for %s\n", DEVICE_NAME);
        	log_out("Humidity in RH (%f)\n", humidity);
        }
        else
                log_fnc_err(UNKNOWN_ERROR, "Get Temperature failed for %s\n", DEVICE_NAME);

		return;
}

/*
 * Main method
 * Get user input and respond
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

	/* populate global user command and list pointers */
	call_cmd_method(cmd_config, NUM_USER_COMMANDS, argv[1], argc-2);
		
	return 0;
}

