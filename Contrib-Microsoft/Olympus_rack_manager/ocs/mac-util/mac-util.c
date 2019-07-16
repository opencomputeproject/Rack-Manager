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
#include "mac-lib.h"

#define UTIL_VERSION_MAJOR               1
#define UTIL_VERSION_MINOR               0
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
	log_out("\n");
	log_out("Write Example:\n");
	log_out("		ocs-mac -w filename\n");
	log_out("\n");
	log_out("Read Example:\n");
	log_out("		ocs-mac -r\n");
	log_out("\n");
	log_out("utility version: %d.%d \n", UTIL_VERSION_MAJOR, UTIL_VERSION_MINOR);
	log_out("utility build:   %d.%d \n", UTIL_VERSION_REVISION, UTIL_VERSION_BUILD);
	log_out("\n");
	log_out("library version: %d.%d \n", LIB_VERSION_MAJOR, LIB_VERSION_MINOR);
	log_out("library build:   %d.%d \n", LIB_VERSION_REVISION, LIB_VERSION_BUILD);
	log_out("\n");
}

int main(int argc, char **argv)
{
	if (argc <= 1) {
		usage();
		return FAILURE;
	}

	int response = UNKNOWN_ERROR;
	uint8_t operation = 0;
	uint8_t *filename = NULL;

	// This utility is intended for only one EEPROM - in the PMDU 
	uint8_t channel = 0;
	uint8_t slave_addr = 0x50;
	
	int i;
	for (i = 0; i < argc; i++) {

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
			
	log_out("i2c target: %d %x\n", channel, slave_addr);

	if (operation == 0) 
	{
		uint8_t length;
		mac_address_t mac_addr[MAX_RECORDS];

		for (i = 0; i < MAX_RECORDS; i+=sizeof(mac_address_t))
			memset(&mac_addr[i], 0, sizeof(mac_address_t));

		response = read_from_eeprom(channel, slave_addr, &length, &mac_addr);
		
		if(response == SUCCESS)
		{
			print_msg("reading from eeprom", NULL);
			log_out("\n");
			for (i = 0; i < length; i++)
			{
				log_out("MAC[%d]: %x:", (i + 1), mac_addr[i].byte1);
				log_out("%x:", mac_addr[i].byte2);
				log_out("%x:", mac_addr[i].byte3);
				log_out("%x:", mac_addr[i].byte4);
				log_out("%x:", mac_addr[i].byte5);
				log_out("%x\n", mac_addr[i].byte6);
				log_out("\n");
			}
			print_msg("eeprom read", &response);
		}
		else
		{
			log_fnc_err(UNKNOWN_ERROR, "EEPROM MAC addresses read failed. Make sure to 'write' valid MAC addresses in EEPROM before reading.\n");
			response = UNKNOWN_ERROR;
			goto main_end;
		}

	}
	else 
	{
		if (filename != NULL) 
		{
			/* read input file and write it to the eeprom */
			response = read_file_write_eeprom(channel, slave_addr, filename);
			if(response == SUCCESS)
				log_out("Write Succeeded\n");
		}
		else 
		{
			log_fnc_err(UNKNOWN_ERROR, "File not found.");
			response = UNKNOWN_ERROR;
			goto main_end;
		}
	}
	
main_end:

	return response;
}
