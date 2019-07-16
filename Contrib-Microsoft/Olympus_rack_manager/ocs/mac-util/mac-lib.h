// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define LIB_VERSION_MAJOR               1
#define LIB_VERSION_MINOR               0
#define LIB_VERSION_REVISION            0
#define LIB_VERSION_BUILD               0

#define MAX_RECORDS			2   // number of fields [MAC_ADDRESS]

#define PACK( __Declaration__ ) __Declaration__ __attribute__((__packed__))

/* mac eeprom record format */
PACK(typedef struct mac_address
{
	uint8_t       byte1;
	uint8_t       byte2;
	uint8_t       byte3;
	uint8_t       byte4;
	uint8_t       byte5;
	uint8_t       byte6;
}) mac_address_t;

/* mac eeprom record format */
PACK(typedef struct mac_header
{
	uint8_t       area_size;
	uint8_t       reserved;
}) mac_header_t;

/* Exposed methods */
int read_from_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* num_macdata, mac_address_t** macdata_array);
int read_file_write_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* filename);
