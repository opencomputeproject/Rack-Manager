// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* i2c file location */
#define I2C_DEV_FILE		"/dev/i2c-%d"
#define MAX_PAGE_SIZE		32	/* 32 byte page when 2 byte address is added */
#define MAX_PAYLOAD_LEN		16  /* FRU read/write chunk size */

int open_i2c_channel(uint8_t channel, int32_t *handle);
int close_i2c_channel(int32_t handle);
int i2c_block_write(int32_t handle, uint8_t dev_addr, uint16_t write_length, uint8_t *write_buf, uint16_t length, uint8_t *buffer);
int i2c_block_read(int32_t handle, uint8_t dev_addr, uint8_t write_len, uint8_t *write_buf, uint16_t length, uint8_t *buffer);
