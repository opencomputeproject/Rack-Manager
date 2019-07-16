// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "fru_sup.h"
#include "ocslog.h"

/*#define DEBUG*/

/* end move to i2c library */
static int read_from_eeprom(uint8_t channel, uint8_t slave_addr);
static int write_to_eeprom(uint8_t channel, uint8_t slave_addr, uint16_t fru_offset, uint16_t write_length, uint8_t* buffer);

/* debug buffer */
uint8_t *debug_buffer;


/* function pointer for i2c write read */
int(*i2c_write_read)(int32_t handle,
	uint8_t slave_addr,
	uint8_t write_length,
	uint8_t* write_data,
	uint8_t read_length,
	uint8_t* buffer);

/* function pointer for i2c write */
int(*i2c_write)(int32_t handle,
	uint8_t slave_addr,
	uint8_t write_length,
	uint8_t* write_data,
	uint8_t data_length,
	uint8_t* data);


/*
	Required FRU fields.  These tags must appear in the FRU file.
*/
static const uint8_t FRU_FIELDS[MAX_RECORDS][MAX_NAME_LEN] = {
	"Board_MfgTime:",		/* 00 */
	"Board_MfgName:",		/* 01 */
	"Board_Product:",		/* 02 */
	"Board_Serial:",		/* 03 */
	"Board_PartNumber:",	/* 04 */
	"Board_FruId:",			/* 05 */
	"Board_BinaryAdd:",		/* 06 */
	"Board_BinaryAdd:",		/* 07 */
	"Board_Version:",		/* 08 */
	"Board_Build:",			/* 09 */
	"Product_Mfgr:",		/* 10 */
	"Product_Product:",		/* 11 */
	"Product_Model:",		/* 12 */
	"Product_Serial:",		/* 13 */
	"Product_AssetTag:",	/* 14 */
	"Product_FruId:",		/* 15 */
	"Product_SubProd:",		/* 16 */
	"Product_Build:"		/* 17 */
};

/* converts input char buffer to binary data */
static int convert_binary_data(uint8_t* buffer) {

	if (buffer == NULL)
		return FAILURE;

	uint64_t hex = strtoul(buffer, NULL, 16);
	memset(buffer, 0, sizeof(long));

	memcpy(buffer, &hex, sizeof(long));

	return SUCCESS;
}

/*
requited fru fields.  tags must appear in the fru file.
*/
static AREA_FIELD fru_field(uint16_t *idx, uint8_t *buffer)
{
	AREA_FIELD field;

	field.length = &buffer[++(*idx)];
	field.data = &buffer[++(*idx)];

	*idx += *field.length;

	return field;
}

/*
	assigns fru charactor data in buffer to fru structures.
*/
static int read_fru_from_buffer(uint8_t *buffer, uint16_t length)
{
	uint16_t idx;
	uint8_t * mfgtime;

	FRU_HEADER header;
	memset(&header, 0, sizeof(FRU_HEADER));

	FRU_BOARD_INFO board;
	memset(&board, 0, sizeof(FRU_BOARD_INFO));

	FRU_PRODUCT_INFO product;
	memset(&product, 0, sizeof(FRU_PRODUCT_INFO));

	/* populate fru header */
	memcpy(&header, buffer, sizeof(FRU_HEADER));

	/* index into board area */
	idx = (header.board * 8);

	if (idx + sizeof(FRU_HEADER) > length) {
		log_fnc_err(UNKNOWN_ERROR, "FRU buffer lenght does not support board header data");
		return FAILURE;
	}

	/* board header information */
	board.header.version = buffer[idx++];
	board.header.length = buffer[idx++];
	board.header.languagecode = buffer[idx++];

	if (idx + (board.header.length - sizeof(FRU_HEADER)) > length) {
		log_fnc_err(UNKNOWN_ERROR, "FRU buffer lenght does not support board area data");
		return FAILURE;
	}

	// temporary for mftdatetime
	mfgtime = array_to_time(&buffer[idx]);
	log_out("board mfgdatetime: %s \n", mfgtime);
	idx += 2;

	board.manufacture = fru_field(&idx, buffer);
	log_out("board manufacturer: %s \n", board.manufacture.data);

	board.name = fru_field(&idx, buffer);
	log_out("board name: %s \n", board.name.data);

	board.serial = fru_field(&idx, buffer);
	log_out("board serial: %s \n", board.serial.data);

	board.part = fru_field(&idx, buffer);
	log_out("board part: %s \n", board.part.data);

	board.fruid = fru_field(&idx, buffer);
	log_out("board fruId: %s \n", board.fruid.data);

	board.address1 = fru_field(&idx, buffer);
	if (*board.address1.length > 0) {
		log_out("board address1: %s \n", board.address1.data);
	}

	board.address2 = fru_field(&idx, buffer);
	if (*board.address2.length > 0) {
		log_out("board address2: %s \n", board.address2.data);
	}

	board.boardver = fru_field(&idx, buffer);
	log_out("board version: %s \n", board.boardver.data);

	board.build = fru_field(&idx, buffer);
	log_out("board build: %s \n", board.build.data);

	/* index into product area */
	idx = (header.product * 8);

	if (idx + sizeof(FRU_HEADER) > length) {
		log_fnc_err(UNKNOWN_ERROR, "FRU buffer lenght does not support product header data");
		return FAILURE;
	}

	/* product header information */
	product.header.version = buffer[idx++];
	product.header.length = buffer[idx++];
	product.header.languagecode = buffer[idx];

	if (idx + (product.header.length - sizeof(FRU_HEADER)) > length) {
		log_fnc_err(UNKNOWN_ERROR, "FRU buffer lenght does not support product area data");
		return FAILURE;
	}

	product.manufacture = fru_field(&idx, buffer);
	log_out("product manufacture: %s \n", product.manufacture.data);

	product.productname = fru_field(&idx, buffer);
	log_out("product productname: %s \n", product.productname.data);

	product.productversion = fru_field(&idx, buffer);
	log_out("product productversion: %s \n", product.productversion.data);

	product.serial = fru_field(&idx, buffer);
	log_out("product serial: %s \n", product.serial.data);

	product.assettag = fru_field(&idx, buffer);
	log_out("product assettag: %s \n", product.assettag.data);

	product.fruid = fru_field(&idx, buffer);
	log_out("product fruid: %s \n", product.fruid.data);

	product.subproduct = fru_field(&idx, buffer);
	log_out("product subproduct: %s \n", product.subproduct.data);

	product.build = fru_field(&idx, buffer);
	log_out("product build: %s \n", product.build.data);

	return SUCCESS;
}

/*
	reads fru text data from file into array
*/
static int read_fru_from_file(uint8_t channel, uint8_t slave_addr, FILE *input)
{
	/* fru spec rev 1.3: field lenght: 5:0 */
	/* record maximum lenght 63 bytes */
	uint8_t line[80];
	memset(&line, 0, sizeof(line));

	/* used for line tag compare */
	uint8_t tag[MAX_NAME_LEN];
	memset(&tag, 0, MAX_NAME_LEN);

	uint8_t tag_length = 0;
	uint8_t field_length = 0;
	uint16_t area_length = 0;
	uint16_t idx = sizeof(FRU_HEADER);

	FRU_HEADER header;
	memset(&header, 0, sizeof(FRU_HEADER));

	uint8_t *fru_data;
	fru_data = calloc(MAX_EEPROM_SZ, sizeof(uint8_t));

	uint8_t *boardLength;
	uint8_t *prodLength;

	fru_data[idx++] = FRU_VERSION;
	boardLength = &fru_data[idx++];
	fru_data[idx++] = FRU_LANG;
	area_length = 3;
	int rc = 0;

	size_t i;
	for (i = 0; i < MAX_RECORDS; i++)
	{
		if (fgets(line, (MAX_LENGTH + MAX_NAME_LEN), input) != NULL)
		{
			if (strstr(&line, &FRU_FIELDS[i]) != NULL) {

				tag_length = (uint8_t)strlen(&FRU_FIELDS[i]);

				memset(&tag, 0, MAX_NAME_LEN);
				strncpy(&tag, &FRU_FIELDS[i], tag_length);

				/* check fru file tag format */
				if (strcmp(&tag, &FRU_FIELDS[i]) != 0)
				{
					log_fnc_err(UNKNOWN_ERROR, "header mismatch line beginging: %s\n", line);
					rc = UNKNOWN_ERROR;
					break;
				}

				/* length of field or maximum length */
				field_length = (uint8_t)((strlen(line) - tag_length));
				field_length = field_length > MAX_LENGTH ? MAX_LENGTH : field_length;

				/* remove any new line */
				if (field_length > 0) {
					field_length = line[(field_length + tag_length) - 1] == NEW_LINE ?
						field_length - 1 : field_length;
				}

				/* if mfgdate time is not specified, use current time*/
				if (i == 0){

					uint32_t mfg_time = 0;

					/* no date use current */
					if (field_length == 0)
						mfg_time = current_time();
					else{
						if (field_length > 20);
							field_length = 20;

						char date_str[20];
						strncpy(&date_str, &line[tag_length], field_length);
						mfg_time = str_time_to_array(&date_str);
					}

					if (mfg_time > 0) {
						memcpy(&fru_data[idx], &mfg_time, 3);
						idx += 3;
						area_length += 3;
					}
					else {
						log_fnc_err(UNKNOWN_ERROR, "could not get current time.");
						rc = UNKNOWN_ERROR;
						break;
					}
				} /* board_binary */
				//else if (i == 6 || i == 7) {

				//	uint8_t binary_data[20];

				//if (field_length > 0)
				//{
				//	/* typically mac address space */
				//	field_length = (field_length - remove_char(&line[tag_length], '-'));
				//	field_length = (field_length - remove_char(&line[tag_length], ':'));
				//	/* copy data to temp buffer */
				//	strncpy(&binary_data, &line[tag_length], field_length);
				//
				//	/* convert data to binary data */
				//	convert_binary_data(&binary_data);
				//
				//	/*every hex charactor is 2 */
				//	field_length = (field_length / 2);
				////}
				//
				///* copy field data into buffer */
				//fru_data[idx++] = (uint8_t)(field_length & FRU_LENGTH_MASK);
				//strncpy(&fru_data[idx++], &binary_data, field_length);
				//
				///* increment index by the field length */
				//idx += field_length;
				//
				///* increment the area length, by the field lenght and the bytes occupied */
				//area_length += (field_length + 2);
				//
				//}
				/* check current area within designated fru size */
				else if (fru_oversize(idx, field_length + 1)) {

					/* copy field data into buffer */
					fru_data[idx++] = (uint8_t)(field_length & FRU_LENGTH_MASK);
					strncpy(&fru_data[idx++], &line[tag_length], field_length);

					/* increment index by the field length */
					idx += field_length;

					/* increment the area length, by the field lenght and the bytes occupied */
					area_length += (field_length + 2);
				}
				else {
					log_fnc_err(UNKNOWN_ERROR, "content to large for FRU designated EEPROM space: %s", line);
					rc = UNKNOWN_ERROR;
					break;
				}

				tag_length = 0;
				field_length = 0;

				if (i == (9)
					|| i == (MAX_RECORDS - 1)) {

					area_length++; // stop byte
					area_length++; // checksum

					/* area stop byte */
					fru_data[idx++] = FRU_AREA_STOP;

					/* check sum */
					idx++;

					/* pad area length */
					if ((area_length % 8) != 0) {
						idx += (8 - (area_length % 8));
						area_length += (8 - (area_length % 8));
					}

					/* start of board area */
					if (i == 9) {
						header.board = 1;
						*boardLength = (uint8_t)(area_length /8);

						header.product = (uint8_t)(idx / 8);

						fru_data[idx++] = FRU_VERSION;
						prodLength = &fru_data[idx++];
						fru_data[idx++] = FRU_LANG;

						area_length = 3;

						/* zero the area length for next area */
					}
					else {
						*prodLength = (uint8_t)(area_length /8);
					}
				}
			}
			else {
				log_fnc_err(UNKNOWN_ERROR, "could not read line header: %s", line);
				rc = UNKNOWN_ERROR;
				break;
			}

		}
		else {
			log_fnc_err(UNKNOWN_ERROR, "file not in correct format: %s \n", line);
			rc = UNKNOWN_ERROR;
			break;
		}
	}

	if (rc == SUCCESS)
	{

		/* copy the header */
		memcpy(fru_data, &header, sizeof(FRU_HEADER));

#ifdef DEBUG

		print_msg("read input file buffer", NULL);

		/* read file back */
		rc = read_fru_from_buffer(fru_data, idx);

		print_msg("read buffer", &rc);

#endif // DEBUG

		//* write the eeprom content to eeprom */
		if (rc == SUCCESS)
		{
			uint16_t fru_offset = 0;
			print_msg("write to eeprom", NULL);
			rc = write_to_eeprom(channel, slave_addr, fru_offset, idx, fru_data);
			print_msg("write", &rc);
		}
	}
	free(fru_data);
	return rc;
}

/* debug simulating i2c_write_read */
static int i2c_write_read_dbg(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t* write_data, uint8_t read_length, uint8_t* buffer)
{
	if (debug_buffer == NULL){
		log_fnc_err(UNKNOWN_ERROR, "i2c_write_read_dbg - no debug buffer defined");
		return FAILURE;
	}
	else{
		uint16_t offset = 0;
		memcpy(&offset, write_data, sizeof(uint16_t));
		memcpy(buffer, &debug_buffer[offset], read_length);
		return SUCCESS;
	}
}

/* write read from i2c device */
static int i2c_write_read_prod(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t* write_data, uint8_t read_length, uint8_t* buffer)
{
	// switch msb->lsb
	uint16_t offset = (uint16_t)(write_data[0]<<8|write_data[1]);
	memcpy(write_data, &offset, sizeof(uint16_t));

	if(i2c_block_read(handle, slave_addr, write_length, write_data, read_length, buffer)!= SUCCESS){
		log_fnc_err(UNKNOWN_ERROR, "i2c read_after_write failed for eeprom: (%02x).\n", slave_addr);
		return FAILURE;
	}

	return SUCCESS;
}

/* debug simulating i2c_write */
static int i2c_write_dbg(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t* write_data, uint8_t data_length, uint8_t* data)
{
	if (debug_buffer == NULL){
		log_out("i2c_write_read_dbg - no debug buffer defined");
		return FAILURE;
	}
	else{
		uint16_t offset = 0;
		memcpy(&offset, write_data, sizeof(uint16_t));
		memcpy(&debug_buffer[offset], data, data_length);
		return SUCCESS;
	}
}

/* write to i2c device */
static int i2c_write_prod(int32_t handle, uint8_t slave_addr,
	uint8_t write_length, uint8_t *write_data, uint8_t data_length, uint8_t *buffer)
{
		uint16_t offset = (uint16_t)(write_data[0]<<8 | write_data[1]);
		memcpy(write_data, &offset, sizeof(uint16_t));

		if(i2c_block_write(handle, slave_addr, write_length, write_data, data_length, buffer) != SUCCESS)
		{
				log_fnc_err(UNKNOWN_ERROR, "i2c write failed for eeprom (%02x).\n", slave_addr);
				return FAILURE;
		}

		return SUCCESS;
}

/* supports fru read, by reading fru area from eeprom */
static int read_fru_area(int32_t handle, uint8_t slave_addr, uint16_t *fru_offset,
	uint16_t *buf_idx, int16_t *area_length, uint8_t *buffer)
{
	int response = SUCCESS;
	uint16_t length = 0;
	uint16_t boundary = 0;
	uint16_t fru_idx = 0;
	uint8_t read_length = 0;
	uint8_t write_buffer[sizeof(uint16_t)];

	AREA_HEADER area_header;
	memset(&area_header, 0, sizeof(AREA_HEADER));

	// copy the start offset to the write buffer
	memset(&write_buffer, 0, sizeof(uint16_t));
	memcpy(write_buffer, fru_offset, sizeof(uint16_t));

	/* ensure fru header is withn the page, or read across page boundaries */
	if (MAX_PAGE_SIZE - (*fru_offset % MAX_PAGE_SIZE) > sizeof(AREA_HEADER)) {
		response = (*i2c_write_read)(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, sizeof(AREA_HEADER), &buffer[*buf_idx]);
	}
	else{
		uint16_t i = 0;
		uint16_t tmp_idx = *buf_idx;
		uint16_t offset = *fru_offset;

		for (; i < sizeof(area_header); i++) {
			if (response = (*i2c_write_read)(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, sizeof(uint8_t), &buffer[tmp_idx]) != SUCCESS) {
				log_fnc_err(UNKNOWN_ERROR, "area head read error (%d)", response);
				return FAILURE;
			}

			offset++;
			tmp_idx++;

			memcpy(write_buffer, &offset, sizeof(uint16_t));
		}

	}

	if (response == SUCCESS)
	{
		memcpy(&area_header, &buffer[*buf_idx], sizeof(AREA_HEADER));
		*fru_offset += sizeof(AREA_HEADER);
		*buf_idx += sizeof(AREA_HEADER);

		*area_length += (area_header.length * 8);
		if(*area_length > MAX_EEPROM_SZ/2)
		{
			log_fnc_err(UNKNOWN_ERROR, "area length (%d) exceeded %d\n", *area_length, MAX_EEPROM_SZ/2);
			return FAILURE;
		}

		if (area_header.length != 0)
		{
			length = ((area_header.length * 8) - sizeof(AREA_HEADER));

			while (fru_idx < length)
			{
				// copy the start offset to the write buffer
				memset(&write_buffer, 0, sizeof(uint16_t));
				memcpy(write_buffer, fru_offset, sizeof(uint16_t));

				if ((fru_idx + MAX_PAYLOAD_LEN) < length)
					read_length = MAX_PAYLOAD_LEN;
				else
					read_length = (length - fru_idx);

				/* get page boundary */
				boundary = MAX_PAGE_SIZE - (*fru_offset % MAX_PAGE_SIZE);

				if (read_length > boundary)
					read_length = boundary;

				if (read_length > 0)
					if ((*i2c_write_read)(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, read_length, &buffer[*buf_idx]) != SUCCESS)
					{
						log_fnc_err(UNKNOWN_ERROR, "read_fru_area() i2c_write_read failed.");
						return FAILURE;
					}

				fru_idx += read_length;
				*fru_offset += read_length;
				*buf_idx += read_length;
			}
		}
	}

	return response;
}

/* reads raw fru data from eeprom */
static int read_raw_from_eeprom(uint8_t channel, uint8_t slave_addr) {

	print_msg("reading raw from eeprom", NULL);

	uint8_t *buffer;
	buffer = calloc(MAX_EEPROM_SZ, sizeof(uint8_t));

	uint16_t fru_offset = 0;
	uint16_t buf_idx = 0;
	uint8_t  write_buffer[sizeof(uint16_t)];

	int response = 0;
	uint8_t read_length = 0;
	// copy the start offset to the write buffer
	memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	log_out("\n");
	if (response == SUCCESS) {
		while (fru_offset < MAX_EEPROM_SZ)
		{
			// copy the start offset to the write buffer
			memset(write_buffer, 0, sizeof(uint16_t));
			memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

			if ((fru_offset + MAX_PAYLOAD_LEN) < MAX_EEPROM_SZ)
				read_length = MAX_PAYLOAD_LEN;
			else
			{
				read_length = (MAX_EEPROM_SZ - fru_offset);
			}

			if (read_length > 0)
				if (response = (*i2c_write_read)(handle, slave_addr, (uint8_t)sizeof(uint16_t), write_buffer, read_length, &buffer[buf_idx]) != SUCCESS)
				{
					log_fnc_err(UNKNOWN_ERROR, "read_raw_from_eeprom() i2c_write_read failed.");
					break;
				}

				fru_offset += read_length;
				buf_idx += read_length;
		}
	}
	log_out("\n");

	close_i2c_channel(handle);

	free(buffer);

	print_msg("eeprom read", &response);

	return response;
}

/* reads raw fru data from eeprom */
static int read_from_eeprom(uint8_t channel, uint8_t slave_addr) {

	print_msg("reading from eeprom", NULL);

	uint8_t *buffer;
	buffer = calloc(MAX_EEPROM_SZ, sizeof(uint8_t));

	FRU_HEADER header;
	memset(&header, 0, sizeof(FRU_HEADER));

	uint16_t fru_offset = 0;
	uint16_t buf_idx = 0;
	uint8_t  write_buffer[sizeof(uint16_t)];

	int response = 0;
	uint16_t length = 0;
	// copy the start offset to the write buffer
	memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

	int32_t handle = 0;
	// open i2c bus
	if ((response = open_i2c_channel(channel, &handle)) != SUCCESS)
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");

	if (response == SUCCESS) {

		// i2c read fru header
		if ((response = (*i2c_write_read)(handle, slave_addr, sizeof(uint16_t), write_buffer, sizeof(FRU_HEADER), &buffer[buf_idx])) == SUCCESS)
		{
			memcpy(&header, &buffer[buf_idx], sizeof(FRU_HEADER));
			buf_idx += sizeof(FRU_HEADER);

			if (header.board != 0)
			{
				// update the offset
				fru_offset = (header.board * 8);

				// copy the start offset to the write buffer
				memset(&write_buffer, 0, sizeof(uint16_t));
				memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

				if (fru_offset > MAX_EEPROM_SZ)
				{
					log_fnc_err(UNKNOWN_ERROR, "board offset (%d) exceeded %d\n", fru_offset, MAX_EEPROM_SZ);
				}
				else
				{
					if (response = read_fru_area(handle, slave_addr, &fru_offset, &buf_idx, &length, buffer) != SUCCESS)
						log_fnc_err(UNKNOWN_ERROR, "fru area board read_fru_area() i2c_write_read failed.");
				}
			}

			if (response == SUCCESS && header.product != 0)
			{
				// update the offset
				fru_offset = (header.product * 8);

				if (buf_idx > fru_offset)
					buf_idx = fru_offset;

				// copy the start offset to the write buffer
				memset(&write_buffer, 0, sizeof(uint16_t));
				memcpy(write_buffer, &fru_offset, sizeof(uint16_t));

				if (fru_offset > MAX_EEPROM_SZ)
				{
					log_fnc_err(UNKNOWN_ERROR, "product offset (%d) exceeded %d\n", fru_offset, MAX_EEPROM_SZ);
				}
				else
				{
					if ((response = read_fru_area(handle, slave_addr, &fru_offset, &buf_idx, &length, buffer)) != SUCCESS)
					{
						log_fnc_err(UNKNOWN_ERROR, "fru area product read_fru_area() i2c_write_read failed.");
					}
				}
			}

			if (response == SUCCESS)
				response = read_fru_from_buffer(buffer, length);
		}
	}

	close_i2c_channel(handle);

	free(buffer);

	print_msg("eeprom read", &response);

	return response;
}

/* writes a buffer to eeprom */
static int write_to_eeprom(uint8_t channel, uint8_t slave_addr, uint16_t fru_offset, uint16_t write_length, uint8_t* buffer)
{
	int32_t response = SUCCESS;
	uint8_t chunksize = 0;
	uint8_t write_buf[sizeof(uint16_t)];
	uint16_t write_idx = 0;

	if (write_length > MAX_EEPROM_SZ){
		log_fnc_err(UNKNOWN_ERROR, "fru data length cannot exceed maximum write length: %d.", MAX_EEPROM_SZ);
		return FAILURE;
	}

	int32_t handle = 0;
	// open i2c bus
	if (open_i2c_channel(channel, &handle) != SUCCESS) {
		log_fnc_err(UNKNOWN_ERROR, "unable to open i2c bus");
		return FAILURE;
	}

	while (write_idx < write_length)
	{
		log_out(". ");
		if ((write_idx + MAX_PAYLOAD_LEN) < write_length)
			chunksize = MAX_PAYLOAD_LEN;
		else
			chunksize = write_length - write_idx;

		// copy the start offset to the write buffer
		memset(write_buf, 0, sizeof(uint16_t));
		memcpy(write_buf, &fru_offset, sizeof(uint16_t));

		if (chunksize > 0)
			if (response = (*i2c_write)(handle, slave_addr, sizeof(uint16_t), write_buf, chunksize, &buffer[write_idx]) != SUCCESS)
				goto end;

		write_idx += chunksize;
		fru_offset += chunksize;
	}
	log_out("\n");

	end:

	close_i2c_channel(handle);

	return response;
}

/* opens input file and coordinates the write to eeprom */
static int read_file_write_eeprom(uint8_t channel, uint8_t slave_addr, uint8_t* filename)
{
	int rc;
	if (filename != NULL) {
		FILE *input_file;
		char *mode = "r";

		input_file = fopen(filename, mode);

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

int main(int argc, char **argv)
{
	if (argc <= 3){
		usage();
		return 1;
	}

#ifdef DEBUG
	print_msg("warning debug mode", NULL);
	/* assign fn ptr to debug func */
	i2c_write_read = &i2c_write_read_dbg;
	i2c_write = &i2c_write_dbg;
	debug_buffer = calloc(MAX_EEPROM_SZ, sizeof(uint8_t));
#else
	/* assign fn ptr to prod func */
	i2c_write_read = &i2c_write_read_prod;
	i2c_write = &i2c_write_prod;
#endif // DEBUG

	int response = 0;
	uint8_t channel = 0;
	uint8_t slave_addr = 0;
	uint8_t operation = 0;
	uint8_t *filename = NULL;
	uint8_t raw_read = 0;

	int i;
		for (i = 0; i < argc; i++){

			if (strcmp(argv[i], "-c") == SUCCESS)
				channel = strtol(argv[i + 1], NULL, 16);

			if (strcmp(argv[i], "-s") == SUCCESS)
				slave_addr = strtol(argv[i + 1], NULL, 16);

			if (strcmp(argv[i], "-r") == SUCCESS) {
				operation = 0;
				
				if (argc > (i + 1)) {
					if (strcmp(argv[i + 1], "raw") == SUCCESS)
						raw_read = 1;
				}
			}

			if (strcmp(argv[i], "-w") == SUCCESS){
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

		if (validate_fru_address != SUCCESS)
		{

			log_out("i2c target: %d %x\n", channel, slave_addr);

			if (operation == 0) {

				if (raw_read == 0) {
					/* read from the target eeprom */
					response = read_from_eeprom(channel, slave_addr);
				}
				else
				{
					response = read_raw_from_eeprom(channel, slave_addr);
				}
			}
			else{
				if (filename != NULL) {
					/* read input file and write it to the eeprom */
					response = read_file_write_eeprom(channel, slave_addr, filename);
#ifdef DEBUG
					/* in debug mode do read back*/
					response = read_from_eeprom(channel, slave_addr);
#endif // DEBUG
				}
				else {
					log_fnc_err(UNKNOWN_ERROR, "File not found.");
					response = UNKNOWN_ERROR;
				}
			}
		}
		else
		{
			log_fnc_err(UNKNOWN_ERROR, "invalid channel or slave address: channel: %x address %x", channel, slave_addr);
			response = UNKNOWN_ERROR;
		}

	main_end:

#ifdef DEBUG
		free(debug_buffer);
		print_msg("warning debug mode - end", NULL);
#endif // DEBUG

		return response;
}
