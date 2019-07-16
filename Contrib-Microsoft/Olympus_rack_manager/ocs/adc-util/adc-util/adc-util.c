// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ocslog.h"
#include "adc-lib.h"
#include "pru-lib.h"

#define UTIL_VERSION_MAJOR               1
#define UTIL_VERSION_MINOR               2
#define UTIL_VERSION_REVISION            0
#define UTIL_VERSION_BUILD               0



/* print action message */
static void print_msg(uint8_t* message, uint32_t* code) {
	log_out("\n");
	log_out("==============================\n");
	if (code != NULL)
		log_out("%s completion code: %d\n", message, (uint32_t)*code);
	else
		log_out("%s\n", message);
	log_out("==============================\n");
	log_out("\n");
}

/* help usage */
static void usage()
{
	log_out("\n");
	log_out("Usage:\n");
	log_out("		-r				Read operation.\n");
	log_out("		-w	{file}		write operation, requires file name\n");
	log_out("		-c				perform adc calibration (read from EEPROM and program it via PRU) \n");
	log_out("\n");
	log_out("Write Example:\n");
	log_out("		ocs-adccalibration -w filename\n");
	log_out("\n");
	log_out("Read Example:\n");
	log_out("		ocs-adccalibration -r\n");
	log_out("Calibration (via PRU) Example:\n");
		log_out("		ocs-adccalibration -c\n");
	log_out("\n");
	log_out("utility version: %d.%d \n", UTIL_VERSION_MAJOR, UTIL_VERSION_MINOR);
	log_out("utility build:   %d.%d \n", UTIL_VERSION_REVISION, UTIL_VERSION_BUILD);
	log_out("\n");
	log_out("library version: %d.%d \n", LIB_VERSION_MAJOR, LIB_VERSION_MINOR);
	log_out("library build:   %d.%d \n", LIB_VERSION_REVISION, LIB_VERSION_BUILD);
	log_out("\n");
}

int main(int argc, char **argv)
{\
	if (argc <= 1) {
		usage();
		return FAILURE;
	}

	int response = UNKNOWN_ERROR;
	uint8_t operation = 0;
	uint8_t *filename = NULL;

	// This utility is intended for only one EEPROM - in the PMDU 
	uint8_t channel = 1;
	uint8_t slave_addr = 0x51;
	
	int i;
	for (i = 0; i < argc; i++) {

		if (strcmp(argv[i], "-c") == SUCCESS)
			operation = 2;
			
		if (strcmp(argv[i], "-r") == SUCCESS)
			operation = 0;

		if (strcmp(argv[i], "-w") == SUCCESS) {
			operation = 1;

			if (argc >= (i + 1)) {
				filename = argv[i + 1];
			}
			else {
				usage();
				response = UNKNOWN_ERROR;
				goto main_end;
			}
		}
	}

	log_init (INFO_LEVEL);
	log_out("i2c target: %d %x\n", channel, slave_addr);

	if (operation == 0 || operation == 2) 
	{
		uint8_t length;
		ADC_OFFSET adc_offset[MAX_RECORDS];

		for (i = 0; i < MAX_RECORDS; i+=sizeof(ADC_OFFSET))
			memset(&adc_offset[i], 0, sizeof(ADC_OFFSET));

		response = read_from_eeprom(channel, slave_addr, &length, &adc_offset);

		if(response!=SUCCESS)
		{
			log_fnc_err(UNKNOWN_ERROR, "ADC Calibration read failed. Make sure to 'write' ADC calibration data in EEPROM before reading.\n");
			response = UNKNOWN_ERROR;
			goto main_end;
		}
		
		if(operation==0)
		{
			print_msg("reading from eeprom", NULL);
			log_out("\n");
			for (i = 0; i < length; i++)
			{
				log_out("q14 offset[%d]: %d\n", (i + 1), adc_offset[i].offset);
				log_out("q14 gain  [%d]: %d\n", (i + 1), adc_offset[i].gain);
				log_out("\n");
			}
			print_msg("eeprom read", &response);
		}
		else /* operation = 2 */
		{
			if(length != 12)
			{
				log_fnc_err(UNKNOWN_ERROR, "Required 12 pair of gain/offsets (available: %d)\n", length);
				response = UNKNOWN_ERROR;
				goto main_end;
			}
			
			int phase =0;
			int currentorvoltage =0;
			int value=0;

			for (i = 0; i < length; i++)
			{
				int feed = 1 + i/6; /* first 6 (i = 0 to 5) pairs are for feed 1, next 6 is for feed 2 */
				phase = 1 + i%3;
				if(feed==2)
					phase+=3; /* feed 1 has phase values 1,2,3 and feed 2 has phase values 4,5,6 */

				currentorvoltage = (1+i/3)%2;
				
				value = adc_offset[i].gain;
				if(set_gain(phase, currentorvoltage, value)!=SUCCESS)
					log_fnc_err(UNKNOWN_ERROR, "Could not calibrate %s gain for Phase:%d\n", (currentorvoltage==1)?"Voltage":"Current", phase);
				
				value = adc_offset[i].offset;
				if(set_offset(phase, currentorvoltage, value)!=SUCCESS)
					log_fnc_err(UNKNOWN_ERROR, "Could not calibrate %s offset for Phase:%d\n", (currentorvoltage==1)?"Voltage":"Current", phase);
			}
		}
	}
	else 
	{
		if (filename != NULL) {
			/* read input file and write it to the eeprom */
			response = read_file_write_eeprom(channel, slave_addr, filename);
			if(response == SUCCESS)
				log_out("Write Succeeded\n");
		}
		else 
		{
			log_fnc_err(UNKNOWN_ERROR, "File not found.");
			response = UNKNOWN_ERROR;
		}
	}
	
main_end:
		
	return response;
}
