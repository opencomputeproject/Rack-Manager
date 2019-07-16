// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef USER_CMD_HELPER_H_
#define USER_CMD_HELPER_H_

#include "util.h" 

PACK(typedef struct
{
        byte_t num_inputs;
        char* name;
        void (*cmd_func)(void);
})cmd_config_t;

/* 
 * Helper methods
 */
int get_cmd_index(const cmd_config_t*, int, char*);
void display_cmd_help(const cmd_config_t*, int, char*);
int call_cmd_method(const cmd_config_t*, int, char*, int);

#endif // USER_CMD_HELPER_H_

