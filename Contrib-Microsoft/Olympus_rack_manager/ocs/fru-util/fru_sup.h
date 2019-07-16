// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include "fru.h"

#define VERSION_MAJOR               1
#define VERSION_MINOR               2
#define VERSION_REVISION            0
#define VERSION_BUILD               0

#define arr_size(x) (sizeof(x)/sizeof(x[0]))

/* date time offsets */
#define NEW_LINE			0xA
#define UNIX_TSEC_1970_1996	820454400

uint8_t *array_to_time(uint8_t *mfgtime);
uint32_t str_time_to_array(char *time_str);
int current_time();

int validate_fru_address(uint8_t channel, uint8_t slave_addr);
int calculate_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos);
int verify_chksum(uint8_t *buffer, uint16_t offset, uint8_t end_pos);
int fru_oversize(int idx, int length);
int remove_char(uint8_t* buffer, uint8_t remove);
void print_msg(uint8_t* message, uint32_t* code);
void usage();
