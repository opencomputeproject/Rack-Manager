// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include "util.h"

#define MAX_ADC_RAW_BYTES 				64

PACK(typedef struct  
{
	byte_t 	cmd 		:8;
	byte_t 	seq 		:6; 
	byte_t	status_code :2;
	byte_t 	byte3		:8;
	byte_t 	byte4		:8; 
})generic_t;

PACK(typedef struct  
{
	byte_t 	cmd 		:8;
	byte_t 	seq 		:6; 
	byte_t	status_code :2;
	byte_t 	powerlimit_enable :8;
	byte_t 	powerlimit_active :8; 
	byte_t 	dcthrottle_enable :8;
	byte_t 	dcthrottle_active :8; 
})throttle_t;

PACK(typedef struct  
{
	byte_t 				cmd			:8;
	byte_t			 	seq 		:6;
	byte_t				status_code :2;
	unsigned int		power 		:16;	
})power_t;

PACK(typedef struct  
{
	byte_t 			cmd 		:8;
	byte_t 			seq 		:6; 
	byte_t			status_code :2;
	unsigned int 	phase1_pwr 	:16;
	unsigned int 	phase2_pwr 	:16;
	unsigned int 	phase3_pwr 	:16;
})power_phase_t;

PACK(typedef struct
{
	byte_t 			cmd 				:8;
	byte_t 			seq 				:6;
	byte_t			status_code 		:2;
	byte_t			feed 				:8;
	byte_t	 							:8;
	unsigned int 	phase1			 	:16;
	unsigned int 	phase2			 	:16;
	unsigned int 	phase3			 	:16;
})curr_volt_t;

PACK(typedef struct
{
	byte_t 			cmd 				:8;
	byte_t		 	seq 				:6;
	byte_t			status_code 		:2;
	byte_t			phase 				:8;
	byte_t			currentorvoltage 	:2;
	byte_t								:6;
	unsigned int 	value	 			:16;
})calibration_t;

PACK(typedef struct
{
	byte_t 			cmd 							:8;
	byte_t 			seq 							:6; 
	byte_t 			status_code 					:2;
	unsigned int 	pwr 							:16;
	
	unsigned int 	feed1_phase1_amps			 	:16;
	unsigned int 	feed1_phase2_amps				:16;
	unsigned int 	feed1_phase3_amps			 	:16;
	
	unsigned int 	feed2_phase1_amps			 	:16;
	unsigned int 	feed2_phase2_amps			 	:16;
	unsigned int 	feed2_phase3_amps			 	:16;
	
	unsigned int 	feed1_phase1_volts			 	:16;
	unsigned int 	feed1_phase2_volts			 	:16;
	unsigned int 	feed1_phase3_volts			 	:16;
	
	unsigned int 	feed2_phase1_volts			 	:16;
	unsigned int 	feed2_phase2_volts			 	:16;
	unsigned int 	feed2_phase3_volts			 	:16;
})max_power_t;

PACK(typedef struct
{
	byte_t 	cmd 		:8;
	byte_t 	seq 		:6; 
	byte_t 	status_code :2;
	byte_t	adcnumber 	:2;
	byte_t 	numsamples 	:6;
	byte_t	channel		:8;
})adc_request_t;

PACK(typedef struct
{
	byte_t 	cmd 					:8;
	byte_t 	seq 					:6;
	byte_t 	status_code 			:2;
	byte_t	relevantbitspersample 	:5;
	byte_t							:3;
	byte_t	bytecount 				:8;
	byte_t	rawbuffer[MAX_ADC_RAW_BYTES]	;
})adc_response_t;

PACK(typedef struct
{
	byte_t 	cmd 				:8;
	byte_t 	seq 				:6; 
	byte_t	status_code 		:2;
	
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
	
})feed_status_t;
