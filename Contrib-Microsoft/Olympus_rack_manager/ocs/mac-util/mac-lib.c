// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "ocslog.h"
#include "mac-lib.h"
#include "i2clib.h"

#define MAX_PAGE_SIZE		32	/* 32 byte page when 2 byte address is added */

#define MAX_PAYLOAD_LEN     16   // maximum i2c payload length

/* mac record limits */

#define MAX_RECORD_LEN		6	 // length of field name
#define MAX_RECORD_SZ		4    // size of field data
#define MAX_LINE_BUF_SZ		30	 // line buffer size 

/* eeprom area */
#define EEPROM_OFFSET		1280 // offset into eeprom
#define MAX_MAC_AREA_SZ		32   // reserved area size
#define MAC_AREA_SZ			12   // reserved area size

/*
	Required FRU fields.  These tags must appear in the FRU file.
*/
static const char* MAC_STRING = "mac:";

/* Function prototype declaration */
int write_to_eeprom(uint8_t channel, uint8_t slave_addr, uint16_t fru_offset, uint16_t write_length, uint8_t* buffer);

/*
	reads mac numeric data from file into array
*/
static int read_fru_from_file(uint8_t channel, uint8_t slave_addr, FILE *input)
{
	int rc = 0; 					/* return code */
	char line[MAX_LINE_BUF_SZ]; 	/* file line lengths */
	char mac_data[MAX_RECORDS * sizeof(mac_address_t)];
	char* mac_start;
	int ln;
	mac_address_t mac_addresses[MAX_RECORDS];
	
	for(ln = 0;ln<2;ln++) /*Parse just 2 lines - MAC1 and MAC2*/
	{
		memset(&line, 0, MAX_LINE_BUF_SZ);
		if(fgets(line, MAX_LINE_BUF_SZ, input) != NULL)
		{
			mac_start = strstr(line, MAC_STRING);
			if (mac_start != NULL) 
			{				
				mac_start+=strlen(MAC_STRING);
				
				int i  = 0;
				char* mac_byte = strtok (mac_start,":");
				if(mac_byte!=NULL)
					mac_addresses[ln].byte1 = strtoul(mac_byte, NULL, 16);
					
				for(i=1;i<6;i++) /* Parse six integer values delimited by :*/
				{
					mac_byte = strtok (NULL,":");
					if(mac_byte!=NULL)
					{
						if(i==1)
							mac_addresses[ln].byte2 = strtoul(mac_byte, NULL, 16);
						if(i==2)
							mac_addresses[ln].byte3 = strtoul(mac_byte, NULL, 16);
						if(i==3)
							mac_addresses[ln].byte4 = strtoul(mac_byte, NULL, 16);
						if(i==4)
							mac_addresses[ln].byte5 = strtoul(mac_byte, NULL, 16);
						if(i==5)
							mac_addresses[ln].byte6 = strtoul(mac_byte, NULL, 16);
					}
					else
						break;
				}
				
				if(i<6)
				{
					log_fnc_err(UNKNOWN_ERROR, "file not in correct format. could not read full mac address: %s\n", (char*)line);
					rc = UNKNOWN_ERROR;
					return rc;
				}
				
				memcpy(&mac_data[ln*sizeof(mac_address_t)], &mac_addresses[ln], sizeof(mac_address_t));
			}
			else 
			{
				log_fnc_err(UNKNOWN_ERROR, "file not in correct format. could not read line header: %s\n", (char*)line);
				rc = UNKNOWN_ERROR;
			}
		}
		else
		{
				log_fnc_err(UNKNOWN_ERROR, "file not in correct format. could not read all mac address (Required: 2, Available: %d)\n", ln);
				rc = UNKNOWN_ERROR;
		}
	}

	//* write the eeprom content to eeprom */
	if (rc == SUCCESS)
		rc = write_to_eeprom(channel, slave_addr, EEPROM_OFFSET, MAX_RECORDS * sizeof(mac_address_t), (uint8_t*)mac_data);

	return rc;
}

/* write read from i2c device */
int i2c_write_read(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t* write_data, uint8_t read_length, uint8_t* buffer)
{
	// switch msb->lsb
	uint16_t offset = (uint16_t)(write_data[0] << 8 | write_data[1]);
	memcpy(write_data, &offset, sizeof(uint16_t));

	if (i2c_block_read(handle, slave_addr, write_length, write_data, read_length, buffer) != SUCCESS) {
		log_fnc_err(UNKNOWN_ERROR, "i2c read_after_write failed for eeprom: (%02x).\n", slave_addr);
		return FAILURE;
	}

	return SUCCESS;
}

/* write to i2c device */
int i2c_write(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t* write_data, uint8_t data_length, uint8_t* buffer)
{
	uint16_t offset = (uint16_t)(write_data[0] << 8 | write_data[1]);
	memcpy(write_data, &offset, sizeof(uint16_t));

	if (i2c_block_write(handle, slave_addr, write_length, write_data, data_length, buffer) != SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "i2c write failed for eeprom (%02x).\n", slave_addr);
		return FAILURE;
	}

	return SUCCESS;
}

/* supports fru read, by reading fru area from eeprom */
static int read_fru_area(uint8_t channel, uint8_t slave_addr, uint16_t* fru_offset, 
	uint16_t* buf_idx, uint16_t* area_length, uint8_t* buffer)
{
	int response = SUCCESS;
	uint16_t mac_idx = 0;
	uint16_t boundary = 0;
	uint16_t read_length = 0;
	uint8_t write_buffer[sizeof(uint16_t)];

	mac_header_t header;
	memset(&header, 0, sizeof(mac_header_t));

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	if (response == SUCCESS) {

		// copy the start offset to the write buffer
		memset(&write_buffer, 0, sizeof(uint16_t));
		memcpy(write_buffer, fru_offset, sizeof(uint16_t));

		if ((response = i2c_write_read(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, sizeof(mac_header_t), &buffer[*buf_idx])) != 0)
			log_fnc_err(UNKNOWN_ERROR, "read_fru_area() i2c_write_read failed.");

		memcpy(&header, &buffer[*buf_idx], sizeof(mac_header_t));

		*fru_offset += sizeof(mac_header_t);
		*buf_idx += sizeof(mac_header_t);
	}

	if (header.area_size > 0 && header.area_size <= MAC_AREA_SZ) {
		*area_length = header.area_size;
	}
	else {
		log_fnc_err(UNKNOWN_ERROR, "mac area header contains invalid area size");
		response = FAILURE;
	}
		

	if (response == SUCCESS)
	{
		while (mac_idx < *area_length)
		{
			// copy the start offset to the write buffer
			memset(&write_buffer, 0, sizeof(uint16_t));
			memcpy(write_buffer, fru_offset, sizeof(uint16_t));

			if ((mac_idx + MAX_PAYLOAD_LEN) < *area_length)
				read_length = MAX_PAYLOAD_LEN;
			else
				read_length = (*area_length - mac_idx);

			/* get page boundary */
			boundary = MAX_PAGE_SIZE - (*fru_offset % MAX_PAGE_SIZE);

			if (read_length > boundary)
				read_length = boundary;

			if (read_length > 0)
				if ((response = i2c_write_read(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, read_length, &buffer[*buf_idx])) != 0)
				{
					log_fnc_err(UNKNOWN_ERROR, "read_fru_area() i2c_write_read failed.");
					break;
				}

			mac_idx += read_length;
			*fru_offset += read_length;
			*buf_idx += read_length;
		}
	}

	close_i2c_channel(handle);

	return response;
}

/* reads raw fru data from eeprom */
int read_from_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* num_macdata, mac_address_t** macdata_array) 
{
	uint8_t buffer[MAX_MAC_AREA_SZ];
	uint16_t fru_offset = EEPROM_OFFSET;
	uint16_t buf_idx = 0;
	uint8_t  write_buffer[sizeof(uint16_t)];
	/* gets resized inside read_fru_area */
	uint16_t area_length = MAC_AREA_SZ;
	
	// initialize return values
	int response = UNKNOWN_ERROR;
	*num_macdata = 0;
	
	// copy the start offset to the write buffer
	memset(&write_buffer, 0, sizeof(uint16_t));
	memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

	response = read_fru_area(channel, slave_addr, &fru_offset, &buf_idx, &area_length, buffer);
	
	if (response != SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Fru area board read_fru_area() i2c_write_read failed.");
		response = FAILURE;
	}
	else
	{
		if (area_length <= (sizeof(mac_address_t) * MAX_RECORDS))
		{
			*num_macdata = (int)(area_length / sizeof(mac_address_t));
			memcpy(macdata_array, buffer+sizeof(mac_header_t), area_length);
			response = SUCCESS;
		}
		else 
		{
			log_fnc_err(UNKNOWN_ERROR, "area_length %d exceeds allowed size %d\n", area_length, (sizeof(mac_address_t) * MAX_RECORDS));
			response = FAILURE;
		}
	}	
	return response;
}

/* writes a buffer to eeprom */
int write_to_eeprom(uint8_t channel, uint8_t slave_addr, uint16_t fru_offset, uint16_t write_length, uint8_t* buffer)
{
	int response = SUCCESS;
	uint8_t chunksize = 0;
	uint8_t write_buf[sizeof(uint16_t)];
	uint16_t write_idx = 0;
	uint16_t boundary = 0;
	
	if (write_length > MAX_MAC_AREA_SZ){
		log_fnc_err(UNKNOWN_ERROR, "fru data length cannot exceed maximum write length: %d.", MAX_MAC_AREA_SZ);
		return FAILURE;
	}

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	if (response == SUCCESS) {

		 mac_header_t header;
		memset(&header, 0, sizeof(mac_header_t));

		header.area_size = write_length;

		// copy the start offset to the write buffer
		memset(&write_buf, 0, sizeof(uint16_t));
		memcpy(write_buf, &fru_offset, sizeof(uint16_t));

		/* package header in temp buffer */
		uint8_t buf[sizeof(mac_header_t)];
		memset(buf, 0, sizeof(mac_header_t));
		memcpy(buf, &header, sizeof(mac_header_t));

		if ((response = i2c_write(handle, slave_addr, sizeof(uint16_t), write_buf, sizeof(mac_header_t), buf) != SUCCESS)){
			log_fnc_err(UNKNOWN_ERROR, "unable to write mac header to eeprom");
		}

		fru_offset += sizeof(mac_header_t);
	}

	if (response == SUCCESS) {
		while (write_idx < write_length)
		{
			if ((write_idx + MAX_PAYLOAD_LEN) < write_length)
				chunksize = MAX_PAYLOAD_LEN;
			else
				chunksize = write_length - write_idx;

			/* get page boundary */
			boundary = MAX_PAGE_SIZE - (fru_offset % MAX_PAGE_SIZE);

			if (chunksize > boundary)
				chunksize = boundary;

			// copy the start offset to the write buffer
			memset(&write_buf, 0, sizeof(uint16_t));
			memcpy(write_buf, &fru_offset, sizeof(uint16_t));

			if (chunksize > 0)
				if ((response = i2c_write(handle, slave_addr, sizeof(uint16_t), write_buf, chunksize, &buffer[write_idx])) != SUCCESS)
					break;

			write_idx += chunksize;
			fru_offset += chunksize;
		}
	}

	close_i2c_channel(handle);

	return response;
}

/* opens input file and coordinates the write to eeprom */
int read_file_write_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* filename)
{
	int rc;
	if (filename != NULL) {
		FILE *input_file;
		char *mode = "r";

		input_file = fopen((char*)filename, mode);

		if (input_file == NULL) {
			log_fnc_err(UNKNOWN_ERROR, "can't open input file: %s", filename);
			return FAILURE;
		}

		rc = read_fru_from_file(channel, slave_addr, input_file);

		if (input_file != NULL)
			fclose(input_file);
	}
	else {
		log_fnc_err(UNKNOWN_ERROR, "file not found.");
		rc = UNKNOWN_ERROR;
	}

	return rc;
}
