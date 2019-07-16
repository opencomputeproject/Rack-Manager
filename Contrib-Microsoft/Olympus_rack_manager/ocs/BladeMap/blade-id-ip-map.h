// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>

#define SUCCESS 0
#define FAILURE 1

extern int load_base_address();
extern int get_server_address(uint8_t slot_id, char *address);
extern int get_switch_address(char *address);
extern int get_server_console_access(char *username, char *password);
extern int get_server_command_access(char *username, char *password);
extern int get_server_rest_access(char *username, char *password);
extern int get_switch_access(char *username, char *password);
