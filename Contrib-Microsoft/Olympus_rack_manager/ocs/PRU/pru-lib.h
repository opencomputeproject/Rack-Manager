// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "util.h"

#define DEVICE_NAME 		"PRU RPMSG Device"

typedef enum
{
	TYPE_CURRENT = 0,
	TYPE_VOLTAGE = 1,
	TYPE_POWER = 2,
}measurement_t;

typedef enum 
{
	STATUS_SUCCESS = 0,
	STATUS_INVALID_CMD = 1,
	STATUS_RESOURCE = 2,
	STATUS_UNKNOWN	= 3
}status_t;

PACK(typedef struct  
{
	double 	phase1_val;
	double 	phase2_val;
	double 	phase3_val;
})phase_val_t;

PACK(typedef struct
{
	byte_t	power_negated 		:1;
	byte_t	oc_throttle_limit 	:1;
	byte_t	logic_error 		:1;
	byte_t	unknown_fault 		:1;		
	byte_t	phase1_V_OV_fault 	:1;
	byte_t	phase1_V_UV_fault 	:1;
	byte_t	phase1_I_OC_fault 	:1;
	byte_t	phase2_V_OV_fault 	:1;
	byte_t	phase2_V_UV_fault 	:1;
	byte_t	phase2_I_OC_fault 	:1;		
	byte_t	phase3_V_OV_fault 	:1;
	byte_t	phase3_V_UV_fault 	:1;
	byte_t	phase3_I_OC_fault 	:1;
	byte_t	reserved 	:3;		
})feed_power_status_t;

PACK(typedef struct
{
	double 	pwr;
	
	double 	feed1_phase1_amps;
	double 	feed1_phase2_amps;
	double 	feed1_phase3_amps;
	
	double 	feed2_phase1_amps;
	double 	feed2_phase2_amps;
	double 	feed2_phase3_amps;
	
	double 	feed1_phase1_volts;
	double 	feed1_phase2_volts;
	double 	feed1_phase3_volts;
	
	double 	feed2_phase1_volts;
	double 	feed2_phase2_volts;
	double 	feed2_phase3_volts;
})max_power_stat_t;

/*
 * Param1 (output): major version - Integer between 0 to 255?  (8 bit wide)
 * Param2 (output): minor version - Integer between 0 to 15? (4 bit wide)
 * Return command success (0) or failure (!0)
 */
int get_pru_fw_version(int*, int*);

/*
 * Param1 (output): power in watts 
 * Return command success (0) or failure (!0)
 */
int get_power(double*);

/*
 * Param1 (output): Max power in watts, max amps, volts since last clear
 * Return command success (0) or failure (!0)
 */
int get_max_power(max_power_stat_t*);

/*
 * Clear max power recording - initiate fresh collection
 * Return command success (0) or failure (!0)
 */
int clear_max_power();

/*
 * Param1 (output): get throttle limit
 * Return command success (0) or failure (!0)
 */
int get_throttle_limit(double*);

/*
 * Param1 (input): set throttle limit in watts 
 * Return command success (0) or failure (!0)
 */
int set_throttle_limit(double);

/*
 * Param1 (output): powerlimit throttle enabled (1) or disabled (0)
 * Param2 (output): powerlimit throttle active (1) or inactive (0)
 * Param3 (output): dcthrottle enabled (1) or disabled (0)
 * Param4 (output): dcthrottle active (1) or inactive (0)
 * Return command success (0) or failure (!0)
 */
int get_throttle_status(int*, int*, int*, int*);

/*
 * Param1 (input): enable powerlimit throttle  (1) or disable powerlimit throttle (0)
 * Param2 (input): enable dcthrottle  (1) or disable dcthrottle (0)
 * Return command success (0) or failure (!0)
 */
int set_throttle_enable(int, int);

/*
 * Param1 (input): set throttle to active (1) or set to inactive (0)
 * Return command success (0) or failure (!0)
 */
int set_throttle_active(int);

/*
 * Param1 (input): feed1 (0) or feed2 (1)
 * Param2 (output): status - 0 for fault, 1 for good/healthy
 * Return command success (0) or failure (!0)
 */
int get_phase_status(int, feed_power_status_t*);

/*
 * Param1 (input): feed1 (0) or feed2 (1)
 * Return command success (0) or failure (!0)
 */
int clear_phase_status(int);

/*
 * Set calibration offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: offset value
 */
int set_offset(int, int, int);

/*
 * Set calibration gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: gain value
 */
int set_gain(int, int, int);

/*
 * Get calibration offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): offset value
 */
int get_offset(int, int, int*);

/*
 * Get calibration gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): gain value
 */
int get_gain(int, int, int*);

/*
 * Get phase power reading for given feed
 * Param1: feed 0 or 1
 * Param2 (output): value for all 3 phases
 * Return command success (0) or failure (!0)
 */
int get_phase_power(int, phase_val_t*);

/*
 * Get phase voltage reading for given feed
 * Param1: feed 0 or 1
 * Param2 (output): value for all 3 phases
 * Return command success (0) or failure (!0)
 */
int get_phase_voltage(int, phase_val_t*);

/*
 * Get phase current reading for given feed
 * Param1: feed 0 or 1
 * Param2 (output): value for all 3 phases
 * Return command success (0) or failure (!0)
 */
int get_phase_current(int, phase_val_t*);

/*
* Replay of persistent PRU configs
* Typically done at boot time 
*/
int replay_persist_config();
