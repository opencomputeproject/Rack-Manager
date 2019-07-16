// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "cl-helper.h"
#include "hsc-util.h"
#include "hsc-lib.h"
#include "ocslog.h"

#define NUM_USER_COMMANDS       5

// Define minor and major version which will be overridden in the I2C device header files
const int version_major = 1;
const int version_minor = 3;
const int version_revision = 0;
const int version_build = 0;

#define VERSION_INFO \
		log_out("version: %d.%d \n", version_major, version_minor); \
		log_out("build:   %d.%d \n", version_revision, version_build); \
		log_out("\n"); 

const cmd_config_t cmd_config[NUM_USER_COMMANDS] = 
{
	(cmd_config_t) {0, "GetPower", cmd_get_power},
	(cmd_config_t) {0, "GetInputVoltage", cmd_get_inputvoltage},
	(cmd_config_t) {0, "GetStatus", cmd_get_status},
	(cmd_config_t) {0, "ClearFaults", cmd_clear_faults},
	(cmd_config_t) {0, "-v", cmd_version}
};

/*
 * Method to return utility version information
 */
void cmd_version()
{
	VERSION_INFO
}

/*
 * Method to clear faults
 */
void cmd_clear_faults()
{
	if(hsc_clear_faults()==SUCCESS)
	{    
		log_out("ClearFaults for HSC Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Clear Faults failed for %s\n", DEVICE_NAME);
		
	return;
}

/*
 * Method to get power in Watts
 */
void cmd_get_power()
{
	double power;
	
	if(hsc_get_power(&power)==SUCCESS)
	{    
		log_out("GetPower for HSC Succeeded\n");
		log_out("Power in Watts: %.02f\n", power);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Get Power failed for %s\n", DEVICE_NAME);
		
	return;
}
/*
 * Method to get status
 */
void cmd_get_status()
{
	hsc_status_t hsc_response;
	if(hsc_get_status(&hsc_response)!=SUCCESS)
	{    
		log_fnc_err(UNKNOWN_ERROR, "Get Status failed for %s\n", DEVICE_NAME);
	}
	else
	{
		log_out("Get HSC Status Succeeded\n");

		log_out("Is POWER GOOD?: %s\n", (hsc_response.power_good==1) ? "false" : "true");
		log_out("UNIT OFF?: %s\n", (hsc_response.unit_off==0) ? "false" : "true");
		log_out("Temperaturefault?: %s\n", (hsc_response.temperature_fault==0) ? "false" : "true");
		log_out("INPUT fault?: %s\n", (hsc_response.input_fault==0) ? "false" : "true");
		log_out("VIN UV fault?: %s\n", (hsc_response.vin_uv_fault==0) ? "false" : "true");
		log_out("VOUT fault?: %s\n", (hsc_response.vout_fault==0) ? "false" : "true");
		log_out("CML fault?: %s\n", (hsc_response.cml_fault==0) ? "false" : "true");
		log_out("MFR fault?: %s\n", (hsc_response.mfr_fault==0) ? "false" : "true");
		log_out("Other faults?: %s\n", (hsc_response.noFaults==0) ? "false" : "true");
	}
	return;
}

/*
 * Method to get input voltage in V
 */
void cmd_get_inputvoltage()
{
	double inputvoltage;
	if(hsc_get_inputvoltage(&inputvoltage)==SUCCESS)
	{    
		log_out("GetInputVoltage for HSC Succeeded\n");
		log_out("Input Voltage in Volts: %.02f\n", inputvoltage);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Get Input Voltage failed for %s\n", DEVICE_NAME);
		
	return;
}

/*
 * Main HSC method
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
