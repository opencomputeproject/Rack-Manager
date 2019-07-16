// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "cl-helper.h"
#include "pru-util.h"
#include "pru-lib.h"
#include "ocslog.h"

#define NUM_USER_COMMANDS 21

/* Global pointer to array of strings to hold user parameters */
char** args;

// Define minor and major version which will be overridden in the I2C device header files
const int version_major = 1;
const int version_minor = 5;
const int version_revision = 0;
const int version_build = 0;

#define VERSION_INFO \
		log_out("version: %d.%d \n", version_major, version_minor); \
		log_out("build:   %d.%d \n", version_revision, version_build); \
		log_out("\n"); 

const cmd_config_t cmd_config[NUM_USER_COMMANDS] = 
{
	(cmd_config_t) {0, "GetPruVersion", cmd_get_pru_version},
	(cmd_config_t) {0, "clearmaxpower", cmd_clear_max_power},
	(cmd_config_t) {0, "getmaxpower", cmd_get_max_power},	
	(cmd_config_t) {1, "clearphasestatus", cmd_clear_phase_status},
	(cmd_config_t) {1, "getphasestatus", cmd_get_phase_status},
	(cmd_config_t) {1, "getphasecurrent", cmd_get_phase_current},
	(cmd_config_t) {1, "getphasevoltage", cmd_get_phase_voltage},
	(cmd_config_t) {1, "getphasepower", cmd_get_phase_power},
	(cmd_config_t) {2, "getgain", cmd_get_gain},
	(cmd_config_t) {3, "setgain", cmd_set_gain},
	(cmd_config_t) {2, "getoffset", cmd_get_offset},
	(cmd_config_t) {3, "setoffset", cmd_set_offset},
	(cmd_config_t) {1, "setthrottleactive", cmd_set_throttle_active},
	(cmd_config_t) {0, "getthrottlestatus", cmd_get_throttle_status},
	(cmd_config_t) {2, "setthrottleenable", cmd_set_throttle_enable},
	(cmd_config_t) {0, "getpower", cmd_get_power},
	(cmd_config_t) {1, "setthrottlelimit", cmd_set_throttle_limit},
	(cmd_config_t) {0, "getthrottlelimit", cmd_get_throttle_limit},
	(cmd_config_t) {0, "-v", cmd_version},
	(cmd_config_t) {3, "getadcrawdata", cmd_adc_raw},
	(cmd_config_t) {0, "replaypersistconfig", cmd_replay_persist_config},
};

/*
* Replay persistent config
*/
void cmd_replay_persist_config()
{
	if(replay_persist_config()==SUCCESS)
	{    
		log_out("ReplayPersistConfig Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Replay persistent config settings failed for %s\n", DEVICE_NAME);	
		
	return;
}

/*
 * Get ADC RAW Data
 */
void cmd_adc_raw()
{
	log_out("GetAdcRawData command not implemented\n");
	return; 
}

/*
 * Method to return utility version information
 */
void cmd_version()
{
	VERSION_INFO
	return;
}

/*
 * Get throttle limit in watts
 */
void cmd_get_throttle_limit()
{
	double throttle_limit;
	if(get_throttle_limit(&throttle_limit)==SUCCESS)
	{    
		log_out("GetThrottleLimit Succeeded\n");
		log_out("ThrottleLimit in Watts: %.02f\n", throttle_limit);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Get Throttle Limit failed for %s\n", DEVICE_NAME);	
		
	return;
}

/*
 * Set throttle limit in watts
 */
void cmd_set_throttle_limit()
{
	double throttle_limit = atoi(args[0]);
	if(set_throttle_limit(throttle_limit)==SUCCESS)
	{    
		log_out("SetThrottleLimit Succeeded\n");
		log_out("Set ThrottleLimit in Watts: %.02f\n", throttle_limit);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Set Throttle Limit failed for %s\n", DEVICE_NAME);	
		
	return;
}

/*
 * Get Power in watts
 */
void cmd_get_power()
{
	double power;
	if(get_power(&power)==SUCCESS)
	{    
		log_out("GetPower Succeeded\n");
		log_out("Power in Watts: %.02f\n", power);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Get Power failed for %s\n", DEVICE_NAME);	
		
	return;
}

/*
 * Set throttle enable
 */
void cmd_set_throttle_enable()
{
	int toenablepowerlimit = atoi(args[0]);
	int toenabledcthrottle = atoi(args[1]);
	if(set_throttle_enable(toenablepowerlimit, toenabledcthrottle)==SUCCESS)
	{    
		log_out("SetThrottleEnable Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Set Throttle Enable failed for %s\n", DEVICE_NAME);	

	return;
}

/*
 * Get throttle status
 * 		poweerlimit enabled?
 * 		poweerlimit active?
 * 		dcthrottle enabled?
 * 		dcthrottle active?
 */
void cmd_get_throttle_status()
{
	int isenabled; 
	int isactive;
	int isdcthrottleenabled; 
	int isdcthrottleactive;
	if(get_throttle_status(&isenabled, &isactive, &isdcthrottleenabled, &isdcthrottleactive)==SUCCESS)
	{    
		log_out("GetThrottleStatus Succeeded\n");
		const char* isThrottleEnabled = (isenabled==1)?"Enabled" :"Disabled";
		log_out("Is Powerlimit Throttle Enabled: %s\n", isThrottleEnabled);
		
		const char* currentThrottleState = (isactive==1)?"High. Asserted." :"Low. De-asserted.";
		log_out("Current Powerlimit Throttle State: %s\n", currentThrottleState);

		isThrottleEnabled = (isdcthrottleenabled==1)?"Enabled" :"Disabled";
		log_out("Is DC Throttle Enabled: %s\n", isThrottleEnabled);
		
		currentThrottleState = (isdcthrottleactive==1)?"High. Asserted." :"Low. De-asserted.";
		log_out("Current DC Throttle State: %s\n", currentThrottleState);
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Get Throttle Status failed for %s\n", DEVICE_NAME);	
	
	return;
}

/*
 * Set throttle active
 */
void cmd_set_throttle_active()
{
	int toassert = atoi(args[0]);
	if(set_throttle_active(toassert)==SUCCESS)
	{    
		log_out("SetThrottleAssert Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Set Throttle Assert failed for %s\n", DEVICE_NAME);	
}

/*
 * Set offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: offset value
 */
void cmd_set_offset()
{
	int phase = atoi(args[0]);
	int currentorvoltage = atoi(args[1]);
	int value = atoi(args[2]);
	if(set_offset(phase, currentorvoltage, value)==SUCCESS)
	{    
		log_out("SetOffset Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Set Offset failed for %s\n", DEVICE_NAME);	
		
	return;
}

/*
 * Set gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: gain value
 */
void cmd_set_gain()
{
	int phase = atoi(args[0]);
	int currentorvoltage = atoi(args[1]);
	int value = atoi(args[2]);
	if(set_gain(phase, currentorvoltage, value)==SUCCESS)
	{    
		log_out("SetGain Succeeded\n");
	}
	else
		log_fnc_err(UNKNOWN_ERROR, "Set Gain failed for %s\n", DEVICE_NAME);	
		
	return;
	
}

/*
 * Get calibration offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): offset value
 */
void cmd_get_offset()
{
	int phase = atoi(args[0]);
	int currentorvoltage = atoi(args[1]);
	int value;
	if(get_offset(phase, currentorvoltage, &value)==SUCCESS)
	{    
		log_out("GetOffset Succeeded\n");
		log_out("Feed %d phase %d %s OFFSET (Q14: %d)\n", (phase <= 3)?1:2, (phase<=3)?phase:phase-3, (currentorvoltage==0)?"Current":"Voltage", value);
	}
	else
		log_out("GetOffset Failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Get calibration gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): gain value
 */
void cmd_get_gain()
{
	int phase = atoi(args[0]);
	int currentorvoltage = atoi(args[1]);
	int value;
	if(get_gain(phase, currentorvoltage, &value)==SUCCESS)
	{    
		log_out("GetGain Succeeded\n");
		log_out("Feed %d phase %d %s GAIN (Q14: %d)\n", (phase <= 3)?1:2, (phase<=3)?phase:phase-3, (currentorvoltage==0)?"Current":"Voltage", value);
	}
	else
		log_out("GetGain Failed for %s\n", DEVICE_NAME);
		
	return;	
}

/*
 * Get power for all phases for a given feed
 */
void cmd_get_phase_power()
{
	int feed = atoi(args[0]);
	phase_val_t phase_val;
	if(get_phase_power(feed, &phase_val)==SUCCESS)
	{    
		log_out("GetPhasePower Succeeded\n");
		log_out("Feed %d Phase 1 Power Reading in Watts is %f.\n", feed, phase_val.phase1_val);
		log_out("Feed %d Phase 2 Power Reading in Watts is %f.\n", feed, phase_val.phase2_val);
		log_out("Feed %d Phase 3 Power Reading in Watts is %f.\n", feed, phase_val.phase3_val);
	}
	else
		log_out("GetPhasePower Failed for %s\n", DEVICE_NAME);
	
	return;
}

/*
 * Get voltage for all phases for a given feed
 */
void cmd_get_phase_voltage()
{
	int feed = atoi(args[0]);
	phase_val_t phase_val;
	if(get_phase_voltage(feed, &phase_val)==SUCCESS)
	{    
		log_out("GetPhasevoltage Succeeded\n");
		
		log_out("Feed %d Phase 1 Voltage Reading in Volts is %f.\n", feed, phase_val.phase1_val);
		log_out("Feed %d Phase 2 Voltage Reading in Volts is %f.\n", feed, phase_val.phase2_val);
		log_out("Feed %d Phase 3 Voltage Reading in Volts is %f.\n", feed, phase_val.phase3_val);
		
	}
	else
		log_out("GetPhasevoltage Failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Get current for all phases for a given feed
 */
void cmd_get_phase_current()
{
	int feed = atoi(args[0]);
	phase_val_t phase_val;
	if(get_phase_current(feed, &phase_val)==SUCCESS)
	{    
		log_out("GetPhasecurrent Succeeded\n");
		
		log_out("Feed %d Phase 1 Current Reading in Amps is %f.\n", feed, phase_val.phase1_val);
		log_out("Feed %d Phase 2 Current Reading in Amps is %f.\n", feed, phase_val.phase2_val);
		log_out("Feed %d Phase 3 Current Reading in Amps is %f.\n", feed, phase_val.phase3_val);
		
	}
	else
		log_out("GetPhasecurrent Failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Get status for all phases for a given feed
 */
void cmd_get_phase_status()
{
	int feed = atoi(args[0]);
	feed_power_status_t responsepacket;
	feed_power_status_t* response = &responsepacket;
	if(get_phase_status(feed, response)==SUCCESS)
	{    		
		log_out("Fault status:\n");
		log_out("Is POWER GOOD?:%s\n", (response->power_negated ==1)?"True":"False");
		log_out("OC_THROTTLE_LIMIT:%s\n", (response->oc_throttle_limit ==1)?"True":"False");
		log_out("LOGIC_ERROR:%s\n", (response->logic_error ==1)?"True":"False");
		log_out("UNKOWN_FAULT:%s\n", (response->unknown_fault ==1)?"True":"False");
		log_out("phase1_V_OV_fault:%s\n", (response->phase1_V_OV_fault ==1)?"True":"False");
		log_out("phase1_V_UV_fault:%s\n", (response->phase1_V_UV_fault ==1)?"True":"False");
		log_out("phase1_I_OC_fault:%s\n", (response->phase1_I_OC_fault ==1)?"True":"False");
		
		log_out("phase2_V_OV_fault:%s\n", (response->phase2_V_OV_fault==1)?"True":"False");
		log_out("phase2_V_UV_fault:%s\n", (response->phase2_V_UV_fault ==1)?"True":"False");
		log_out("phase2_I_OC_fault:%s\n", (response->phase2_I_OC_fault ==1)?"True":"False");
		
		log_out("phase3_V_OV_fault:%s\n", (response->phase3_V_OV_fault ==1)?"True":"False");
		log_out("phase3_V_UV_fault:%s\n", (response->phase3_V_UV_fault ==1)?"True":"False");
		log_out("phase3_I_OC_fault:%s\n", (response->phase3_I_OC_fault ==1)?"True":"False");
		
	}
	else
		log_out("Get Phase Status failed for %s\n", DEVICE_NAME);
		
	return;
}

/*
 * Get status for all phases for a given feed
 */
void cmd_clear_phase_status()
{
	int feed = atoi(args[0]);
	if(clear_phase_status(feed)==SUCCESS)
	{
			log_out("Clear Phase Status Succeeded.\n");
	}
	else
			log_out("Clear Phase Status failed for %s\n", DEVICE_NAME);
		
	return;
}

/*
 * Get max power statistics
 */
void cmd_get_max_power()
{
	max_power_stat_t responsepacket;
	max_power_stat_t* response = &responsepacket;
	if(get_max_power(response)==SUCCESS)
	{
		log_out("Get Max Power Statistics Succeeded.\n");    			
		log_out("Max Power in Watts: %f\n", response->pwr);
		
		log_out("Feed 1 Max Current in Amps: Phase1(%f) Phase2(%f) Phase3(%f)\n", response->feed1_phase1_amps, 
			response->feed1_phase2_amps, response->feed1_phase3_amps);

		log_out("Feed 2 Max Current in Amps: Phase1(%f) Phase2(%f) Phase3(%f)\n", response->feed2_phase1_amps,
			response->feed2_phase2_amps, response->feed2_phase3_amps);

		log_out("Feed 1 Max Voltage in Volts: Phase1(%f) Phase2(%f) Phase3(%f)\n", response->feed1_phase1_volts,
			response->feed1_phase2_volts, response->feed1_phase3_volts);
			
		log_out("Feed 2 Max Voltage in Volts: Phase1(%f) Phase2(%f) Phase3(%f)\n", response->feed2_phase1_volts,
			response->feed2_phase2_volts, response->feed2_phase3_volts);
	}
	else
		log_out("Get Max Power Statistics failed for %s\n", DEVICE_NAME);
		
	return;
}

/*
 * Clear max power statistics
 */
void cmd_clear_max_power()
{
	if(clear_max_power()==SUCCESS)
	{
		log_out("Clear Max Power Statistics Succeeded.\n");    			
	}
	else
		log_out("Clear Max Power Statistics failed for %s\n", DEVICE_NAME);

	return;
}

/*
 * Get PRU Firmware verison
 */
void cmd_get_pru_version()
{
	int major_version;
	int minor_version;
	if(get_pru_fw_version(&major_version, &minor_version)==SUCCESS)
	{
		log_out("Get Firmware version succeeded.\n");
		log_out("Firmware version: %d.%d\n", major_version, minor_version);
	}
	else
		log_out("Get Firmware version failed for %s\n", DEVICE_NAME);
		
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

	args = &argv[2];
	/* populate global user command and list pointers */
	call_cmd_method(cmd_config, NUM_USER_COMMANDS, argv[1], argc-2);
		
	return 0;
}


