// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <time.h>
#include "fru_sup.h"
#include "ocslog.h"

int remove_char(uint8_t *buffer, uint8_t remove) {
	uint8_t rem_count = 0;

	uint8_t *head = (uint8_t *)buffer;
	uint8_t *tail = (uint8_t *)buffer;

	while (*head) {
		*tail = *head;
		if (*tail != remove)tail++;
		else
			rem_count++;

		head++;
	}

	*tail = NULL;

	return rem_count;
}


uint32_t str_time_to_array(char *time_str) {
	struct tm mfgtime;
	memset(&mfgtime, 0, sizeof(struct tm));
	time_t time_int;

	strptime(time_str, "%Y-%m-%d %H:%M:%S", &mfgtime);
	mfgtime.tm_isdst = -1;

	time_int = mktime(&mfgtime);

	time_int -= UNIX_TSEC_1970_1996;
	time_int = (time_int / 60);

	return (uint32_t)time_int;
}

/*
returns pointer to charactor representation of unix
date time from int array.
*/
uint8_t *array_to_time(uint8_t *mfgtime) {
	time_t data_long = 0;
	/* unpack ms bytes to seconds number */
	data_long = ((mfgtime[2] << 16) + (mfgtime[1] << 8) + mfgtime[0]) * 60;
	/* add unix offset */
	data_long += UNIX_TSEC_1970_1996;

	uint8_t *time_str;
	time_str = asctime(localtime(&data_long));

	/* remove new line charactors */
	size_t i;
	for (i = 0; i < strlen(time_str); i++)
		time_str[i] = time_str[i] == NEW_LINE ? 0 : time_str[i];

	return time_str;
}

/*
returns int of seconds offset from unix time.
*/
int current_time() {

	time_t date_time;

	/* get current time. */
	date_time = time(NULL);

	if (date_time == ((time_t)-1))
	{
		log_fnc_err(UNKNOWN_ERROR, "Failed to get current date time.\n");
		return FAILURE;
	}

	date_time -= UNIX_TSEC_1970_1996;
	return (int)(date_time / 60);
}

/* validates fru address on rack manager */
int validate_fru_address(uint8_t channel, uint8_t slave_addr)
{
	if (channel = 0)
		return slave_addr == EEPROM_PMDU_ADDRESS ||
		slave_addr == EEPROM_ROW_ADDRESS ||
		slave_addr == EEPROM_AUX_ADDRESS ? SUCCESS : FAILURE;

	if (channel = 1)
		return slave_addr == EEPROM_RMB_ADDRESS ? SUCCESS : FAILURE;

	return FAILURE;
}

/*
calculates ones complement checksum
*/
int calculate_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos) {

	uint8_t chksum = 0;

	for (; offset < end_pos; offset++)
		chksum += buffer[offset];

	return ~(chksum)+1;
}

int verify_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos) {
	return (calculate_chksum(buffer, offset, end_pos) == buffer[end_pos]) ? SUCCESS : FAILURE;
}

/*
function to protect against fru field length overflow
*/
int fru_oversize(int idx, int length)
{
	return idx + length < MAX_EEPROM_SZ ? 1 : 0;
}

/* help usage */
void usage()
{
	log_out("\n");
	log_out("Usage:\n");
	log_out("		-c	{0,1}		i2c channel for eeprom: 0 = local, 1 = add-on pcba\n");
	log_out("		-s	{50,51,52}	i2c slave address: \n");
	log_out("                                   50 = board\n");
	log_out("                                   51 = pmdu\n");
	log_out("                                   52 = row\n");
	log_out("		-r				Read operation.\n");
	log_out("		-w	{file}		write operation, requires file name\n");
	log_out("\n");
	log_out("Write Example:\n");
	log_out("		ocs-fru -c 0 -s 50 -w filename\n");
	log_out("\n");
	log_out("Read Example:\n");
	log_out("		ocs-fru  -c 0 -s 50 -r\n");
	log_out("\n");
	log_out("version: %d.%d \n", VERSION_MAJOR, VERSION_MINOR);
	log_out("build:   %d.%d \n", VERSION_REVISION, VERSION_BUILD);
	log_out("\n");
}

/* print action message */
void print_msg(uint8_t* message, uint32_t* code) {
	log_out("\n");
	log_out("==============================\n");
	if (code != NULL)
		log_out("%s completion code: %d\n", message, (uint32_t)*code);
	else
		log_out("%s\n", message);
	log_out("==============================\n");
	log_out("\n");
}
