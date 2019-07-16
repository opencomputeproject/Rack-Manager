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
#define LIB_VERSION_MINOR               2
#define LIB_VERSION_REVISION            0
#define LIB_VERSION_BUILD               0

#define arr_size(x) (sizeof(x)/sizeof(x[0]))

#define I2C_BUS_0			0x00
#define I2C_BUS_1			0x01
#define MAX_PAGE_SIZE		32	/* 32 byte page when 2 byte address is added */

/* eeprom addresses (7-bit) */
#define	EEPROM_RMB_ADDRESS	0x50
#define	EEPROM_PMDU_ADDRESS	0x51
#define	EEPROM_ROW_ADDRESS	0x52
#define	EEPROM_AUX_ADDRESS	0x50
#define MAX_PAYLOAD_LEN     16   // maximum i2c payload length


/* adc record limits */
#define MAX_RECORDS			64   // number of fields [ADC_OFFSET]
#define MAX_DESCRIPTOR		2	 // Heading descriptors
#define MAX_RECORD_SZ		4    // size of field data
#define MAX_RECORD_LEN		12	 // length of field name
#define MAX_LINE_BUF_SZ		30	 // line buffer size 

/* eeprom area */
#define EEPROM_OFFSET		1312 // offset into eeprom
#define MAX_ADC_AREA_SZ		288   // reserved area size
#define ADC_AREA_SZ			256   // reserved area size

#define PACK( __Declaration__ ) __Declaration__ __attribute__((__packed__))
/*#define PACK( __Declaration__ ) __pragma( pack(push, 1) ) __Declaration__ __pragma( pack(pop) )*/

/* adc eeprom record format */
PACK(typedef struct adc_offset
{
	uint16_t       offset;
	uint16_t       gain;
}) ADC_OFFSET;

/* adc eeprom record format */
PACK(typedef struct adc_header
{
	uint16_t       area_size;
	uint16_t       reserved;
}) ADC_HEADER;

/* Exposed methods */
int read_from_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* num_adcdata, ADC_OFFSET** adcdata_array);
int read_file_write_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* filename);
