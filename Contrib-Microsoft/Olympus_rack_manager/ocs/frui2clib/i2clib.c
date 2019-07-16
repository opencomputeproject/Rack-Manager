// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include "i2clib.h"
#include <fcntl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <unistd.h>
#include "ocslog.h"

int open_i2c_channel(uint8_t channel, int32_t *handle) {

	char filename[20];
	sprintf(filename, I2C_DEV_FILE, channel);

	*handle = open(filename, O_RDWR);
	if (*handle < SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "cannot open i2c device file (%s).\n", filename);
		return FAILURE;
	}

	ioctl(*handle, I2C_TIMEOUT, 3);
	ioctl(*handle, I2C_RETRIES, 3);

	return SUCCESS;
}

int close_i2c_channel(int32_t handle) {
	if(close(handle) != SUCCESS){
		log_fnc_err(UNKNOWN_ERROR, "error closing i2c file handle");
		return FAILURE;
	}

	return SUCCESS;
}

int i2c_block_write(int32_t handle, uint8_t dev_addr, uint16_t write_length, uint8_t *write_buf, uint16_t length, uint8_t *buffer) {

	struct i2c_msg msg;
	struct i2c_rdwr_ioctl_data msgst;


	if (length + 2 > MAX_PAGE_SIZE || length > MAX_PAYLOAD_LEN) {
		log_fnc_err(UNKNOWN_ERROR, "error: block too large");
			return FAILURE;
	}

	/* page limit of 32 bytes including address */
	uint8_t write_buffer[MAX_PAYLOAD_LEN + 2];

	memset(&write_buffer, 0, MAX_PAYLOAD_LEN+2);
	memcpy(&write_buffer, write_buf, write_length);
	memcpy(&write_buffer[write_length], buffer, length);

	int i;
	for(i=0;i<MAX_PAYLOAD_LEN+2;i++)
		log_info("%02x ", write_buffer[i]);
	log_info("\n");

	msg.addr = dev_addr;
	msg.flags = 0;
	msg.len = (length + write_length);
	msg.buf = write_buffer;

	msgst.nmsgs = 1;
	msgst.msgs = &msg;

	if (ioctl(handle, I2C_RDWR, &msgst) < SUCCESS) {
		log_info("transaction failed");
		return FAILURE;
	}

	usleep(5000);

	return SUCCESS;

}

int i2c_block_read(int32_t handle, uint8_t dev_addr, uint8_t write_len, uint8_t *write_buf, uint16_t length, uint8_t *buffer) {

	struct i2c_msg msg[2];
	struct i2c_rdwr_ioctl_data msgst;

	msg[0].addr = dev_addr;
	msg[0].flags = 0;
	msg[0].len = write_len;
	msg[0].buf = write_buf;

	msg[1].addr = dev_addr;
	msg[1].flags = 1;
	msg[1].len = length;
	msg[1].buf = buffer;

	msgst.msgs = msg;
	msgst.nmsgs = 2;

	if (ioctl(handle, I2C_RDWR, &msgst) < SUCCESS) {
		log_info("i2c_block_read - write/read offset failed.");
		return FAILURE;
	}

	return SUCCESS;
}
