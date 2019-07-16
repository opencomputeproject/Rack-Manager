// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <stdbool.h>
#include <linux/i2c-dev-user.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>

#include "i2c-lib.h"
#include "ocslock.h"
#include "ocslog.h"
#define I2C_DEV_FILE            "/dev/i2c-%d"

/* 
 * IOCTL I2C Read Or Write 
 */
int ioctl_read_or_write(int file, int slave_addr, bool is_read, int num_bytes, char* buffer)
{
	struct i2c_rdwr_ioctl_data rdwr_data;
	struct i2c_msg rdwr_messages;

	/* Read */
	rdwr_messages.addr = slave_addr;
	rdwr_messages.flags = (is_read == true) ? I2C_M_RD : 0;
	rdwr_messages.len = num_bytes;
	rdwr_messages.buf = (void*)buffer;

	/* I2C ioctl kernel call metadata */
	rdwr_data.msgs = &rdwr_messages;
	rdwr_data.nmsgs = 1;

	/* Perform the IOCTL I2C Read after Write */
	if(ioctl(file,I2C_RDWR,&rdwr_data)<0)
	{
		log_fnc_err(UNKNOWN_ERROR, "i2c_ioctl (%s) failed: %s \n", (is_read == true) ? "READ" : "WRITE", strerror(errno));
		return UNKNOWN_ERROR;
	}

	return SUCCESS;
}

/* 
 * IOCTL I2C Read and Write 
 */
int ioctl_read_and_write(int file, int slave_addr, int num_write, char* write_buf, int num_read, char* read_buf)
{
	struct i2c_rdwr_ioctl_data rdwr_data;
	struct i2c_msg rdwr_messages[2];

	/* Read */
	rdwr_messages[0].addr = slave_addr;
	rdwr_messages[0].flags = 0;
	rdwr_messages[0].len = num_write;
	rdwr_messages[0].buf = (void*)write_buf;

	/* Read */
	rdwr_messages[1].addr = slave_addr;
	rdwr_messages[1].flags = I2C_M_RD;
	rdwr_messages[1].len = num_read;
	rdwr_messages[1].buf = (void*)read_buf;

	/* I2C ioctl kernel call metadata */
	rdwr_data.msgs = &rdwr_messages[0];
	rdwr_data.nmsgs = 2;

	/* Perform the IOCTL I2C Read after Write */
	if(ioctl(file,I2C_RDWR,&rdwr_data)<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "i2c_ioctl failed: %s \n", strerror(errno));
			return UNKNOWN_ERROR;
	}

	return SUCCESS;
}

/*
 * EXPOSED METHOD: Generic I2C Read after Write Method
*/
int i2c_read_after_write(int adapter_num, int i2c_addr, int num_write, void* write_buf, 
	int delay_ms, int num_read, void* read_buf)
{
	int file;
	int ret;
	char filename[20];
	ocslock_t lock = (adapter_num==0)?I2C0_CHARDEV:I2C1_CHARDEV;

	if(num_write > 0 && write_buf == NULL)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C write buffer is NULL (expected buffer of %d bytes).\n", num_write);
			return UNKNOWN_ERROR;
	}

	if(num_read > 0 && read_buf == NULL)
	{
			log_fnc_err(UNKNOWN_ERROR, "I2C read buffer is NULL (expected buffer of %d bytes).\n", num_read);
			return UNKNOWN_ERROR;
	}

	sprintf(filename, I2C_DEV_FILE, adapter_num);
	file = open(filename, O_RDWR);
	if(file<0)
	{
			log_fnc_err(UNKNOWN_ERROR, "Cannot open I2C device file (%s).\n", filename);
			return UNKNOWN_ERROR;
	}

	/* lock */
	ret = ocs_lock(lock);
	if(ret!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Cannot lock device file for I2C access (%s).\n", strerror(ret));
        return UNKNOWN_ERROR;
	}

	log_info("I2C: Addr (%02x) numWr (%d) numRd (%d) delay (%d)\n", i2c_addr, num_write, num_read, delay_ms);
	
	if(i2c_addr == 0x10 && num_read>0) /* HSC required single read after write TODO: Refactor as part of i2c library merge */ 
	{
		ret = ioctl_read_and_write(file, i2c_addr, num_write, write_buf, num_read, read_buf);
		
		if(ret!=SUCCESS)
		{
			log_fnc_err(UNKNOWN_ERROR, "Cannot perform I2C write (%s).\n", strerror(ret));
			ocs_unlock(lock);
			close(file);
			return UNKNOWN_ERROR;
		}
	}
	else
	{
		if(num_write > 0)
		{
			ret = ioctl_read_or_write(file, i2c_addr, false, num_write, write_buf);
			if(ret!=SUCCESS)
			{
				log_fnc_err(UNKNOWN_ERROR, "Cannot perform I2C write (%s).\n", strerror(ret));
				ocs_unlock(lock);
				close(file);
				return UNKNOWN_ERROR;
			}
		}

		usleep(delay_ms*1000);

		if(num_read > 0)
		{
			ret = ioctl_read_or_write(file, i2c_addr, true, num_read, read_buf);
			if(ret!=SUCCESS)
			{
				log_fnc_err(UNKNOWN_ERROR, "Cannot perform I2C read (%s).\n", strerror(ret));
				ocs_unlock(lock);
				close(file);
				return UNKNOWN_ERROR;
			}
		}
	}
    // unlock
	ret = ocs_unlock(lock);
	if(ret!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Cannot unlock device file for I2C access (%s).\n", strerror(ret));
	}

	close(file);
	return ret;
}
