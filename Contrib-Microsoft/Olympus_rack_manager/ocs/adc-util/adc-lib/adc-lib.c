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
#include "adc-lib.h"
#include "i2clib.h"

/*
	Required FRU fields.  These tags must appear in the FRU file.
*/
static const char ADC_FIELDS[MAX_DESCRIPTOR][MAX_RECORD_LEN] = {
	"rms_offset:",
	"rms_gain:",
};

/* Function prototype declaration */
int write_to_eeprom(uint8_t channel, uint8_t slave_addr, uint16_t fru_offset, uint16_t write_length, uint8_t* buffer);

/*
calculates ones complement checksum
*/
//static int calculate_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos){

	//uint8_t chksum = 0;

	//for (; offset < end_pos; offset++)
		//chksum += buffer[offset];

	//return ~(chksum)+1;
//}

//static int verify_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos){
	//return (calculate_chksum(buffer, offset, end_pos) == buffer[end_pos]) ? SUCCESS : FAILURE;
//}

/*
	function to protect against fru field length overflow
*/
//static int fru_oversize(int idx, int length)
//{	return idx + length < MAX_ADC_AREA_SZ ? 1 : 0;
//}

/*
	reads adc numeric data from file into array
*/
static int read_fru_from_file(uint8_t channel, uint8_t slave_addr, FILE *input)
{
	/* return code */
	int rc = 0;

	/* file line lengths */
	char line[MAX_LINE_BUF_SZ];
	memset(&line, 0, MAX_LINE_BUF_SZ);

	/* used for line tag compare */
	char tag[MAX_RECORD_LEN];
	
	uint8_t tag_length = 0;

	uint16_t offset_gain = 0;
	uint64_t numeric_value;

	uint16_t idx = 0;

	char adc_data[MAX_RECORDS * sizeof(ADC_OFFSET)];

	uint8_t str_order = 0;
	while(fgets(line, MAX_LINE_BUF_SZ, input) != NULL)
	{
		if (strstr(line, ADC_FIELDS[str_order]) != NULL) {

			tag_length = strlen(ADC_FIELDS[str_order]);

			memset(tag, 0, MAX_RECORD_LEN);			
			strncpy(tag, ADC_FIELDS[str_order], tag_length);

			/* check adc file tag format */
			if (strcmp(tag, ADC_FIELDS[str_order]) != 0)
			{
				log_fnc_err(UNKNOWN_ERROR, "header mismatch line beginging: %s\n", (char*)line);
				rc = UNKNOWN_ERROR;
				break;
			}

			numeric_value = strtoul(&line[tag_length], NULL, 10);
			offset_gain = (uint16_t)numeric_value;
			memcpy(&adc_data[idx], &offset_gain, sizeof(uint16_t));

			idx += sizeof(uint16_t);
			offset_gain = 0;
			tag_length = 0;
		}
		else {
			log_fnc_err(UNKNOWN_ERROR, "file not in correct format. could not read line header: %s\n", (char*)line);
			rc = UNKNOWN_ERROR;
		}

		// rotate order
		str_order = str_order == 0 ? 1 : 0;
	}

	if (strcmp(tag, ADC_FIELDS[1]) != 0) {
		log_fnc_err(UNKNOWN_ERROR, "file not in correct format. must end with gain: %s\n", (char*)line);
		rc = UNKNOWN_ERROR;
	}

	//* write the eeprom content to eeprom */
	if (rc == SUCCESS)
		rc = write_to_eeprom(channel, slave_addr, EEPROM_OFFSET, idx, (uint8_t*)adc_data);

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
	uint16_t adc_idx = 0;
	uint16_t boundary = 0;
	uint16_t read_length = 0;
	uint8_t write_buffer[sizeof(uint16_t)];

	ADC_HEADER header;
	memset(&header, 0, sizeof(ADC_HEADER));

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	if (response == SUCCESS) {

		// copy the start offset to the write buffer
		memset(&write_buffer, 0, sizeof(uint16_t));
		memcpy(write_buffer, fru_offset, sizeof(uint16_t));

		if ((response = i2c_write_read(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, sizeof(ADC_HEADER), &buffer[*buf_idx])) != 0)
			log_fnc_err(UNKNOWN_ERROR, "read_fru_area() i2c_write_read failed.");

		memcpy(&header, &buffer[*buf_idx], sizeof(ADC_HEADER));

		*fru_offset += sizeof(ADC_HEADER);
		*buf_idx += sizeof(ADC_HEADER);
	}

	if (header.area_size > 0  && header.area_size <= MAX_ADC_AREA_SZ) {
		*area_length = header.area_size;
	}
	else {
		log_fnc_err(UNKNOWN_ERROR, "invalid adc area header size");
		response = FAILURE;
	}
		

	if (response == SUCCESS)
	{
		while (adc_idx < *area_length)
		{
			// copy the start offset to the write buffer
			memset(&write_buffer, 0, sizeof(uint16_t));
			memcpy(write_buffer, fru_offset, sizeof(uint16_t));

			if ((adc_idx + MAX_PAYLOAD_LEN) < *area_length)
				read_length = MAX_PAYLOAD_LEN;
			else
				read_length = (*area_length - adc_idx);

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

			adc_idx += read_length;
			*fru_offset += read_length;
			*buf_idx += read_length;
		}
	}

	close_i2c_channel(handle);

	return response;
}

/* reads raw fru data from eeprom */
int read_from_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* num_adcdata, ADC_OFFSET** adcdata_array) 
{
	uint8_t buffer[MAX_ADC_AREA_SZ];
	uint16_t fru_offset = EEPROM_OFFSET;
	uint16_t buf_idx = 0;
	uint8_t  write_buffer[sizeof(uint16_t)];
	/* gets resized inside read_fru_area */
	uint16_t area_length = ADC_AREA_SZ;
	
	// initialize return values
	int response = UNKNOWN_ERROR;
	*num_adcdata = 0;
	
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
		if (area_length <= (sizeof(ADC_OFFSET) * MAX_RECORDS))
		{
			*num_adcdata = (int)(area_length / sizeof(ADC_OFFSET));
			memcpy(adcdata_array, buffer+sizeof(ADC_HEADER), area_length);
			response = SUCCESS;
		}
		else 
		{
			log_fnc_err(UNKNOWN_ERROR, "area_length does not support area size\n");
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
	
	if (write_length > MAX_ADC_AREA_SZ){
		log_fnc_err(UNKNOWN_ERROR, "fru data length cannot exceed maximum write length: %d.", MAX_ADC_AREA_SZ);
		return FAILURE;
	}

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	if (response == SUCCESS) {

		 ADC_HEADER header;
		memset(&header, 0, sizeof(ADC_HEADER));

		header.area_size = write_length;

		// copy the start offset to the write buffer
		memset(&write_buf, 0, sizeof(uint16_t));
		memcpy(write_buf, &fru_offset, sizeof(uint16_t));

		/* package header in temp buffer */
		uint8_t buf[sizeof(ADC_HEADER)];
		memset(buf, 0, sizeof(ADC_HEADER));
		memcpy(buf, &header, sizeof(ADC_HEADER));

		if ((response = i2c_write(handle, slave_addr, sizeof(uint16_t), write_buf, sizeof(ADC_HEADER), buf) != SUCCESS)){
			log_fnc_err(UNKNOWN_ERROR, "unable to write adc header to eeprom");
		}

		fru_offset += sizeof(ADC_HEADER);
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
