// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef I2C_READAFTERWRITE_H_
#define I2C_READAFTERWRITE_H_

/*
 * Method for performing atomic i2c read write 
 * Param1: i2c_adapter_num
 * Param2: i2c_address 
 * Param3: num_write (bytes)
 * Param4: write_buf
 * Param5: delay in millisecs
 * Param6: num_read (bytes)
 * Param7: read_buf
 */
int i2c_read_after_write(int, int, int, void*, int, int, void*);

#endif // I2C_READAFTERWRITE_H_
