// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <stdlib.h>
#include "cl-helper.h"
#include "ocslog.h"

/*
 * Return Index in to the command config structure
 */
int get_cmd_index(const cmd_config_t* cmd_config, int count, char* cmd_name)
{
	if(cmd_config == NULL)
		return UNKNOWN_ERROR;
	
	int i;
	for(i = 0; i<count; i++)
	{
			if(strcasecmp(cmd_config[i].name, cmd_name)==0)
					return i;
	}
	return UNKNOWN_ERROR;
}

/*
 * Help test for command
 */
void display_cmd_help(const cmd_config_t* cmd_config, int count, char* cmd_name)
{		
        if(cmd_name == NULL)
                log_out("Available Commands\n");

        int i;
        for(i = 0; i<count; i++)
        {
                if((cmd_name==NULL) || (cmd_name != NULL && (strcasecmp(cmd_config[i].name, cmd_name)==0)))    
					log_out("(Name, ExpectedNumInputs): (%s, %d)\n", cmd_config[i].name, cmd_config[i].num_inputs);
        }
}

/*
 * Allocate memory for request response structure and perform respective command I2C readafterwrite
 * Return -1 when error is encountered.
 */
int call_cmd_method(const cmd_config_t* cmd_config, int num_cmd, char* cmd_name, int arg_count)
{
        // Get the required number of inputs for the command
        // Just for checking valid user command name
        int index=get_cmd_index(cmd_config, num_cmd, cmd_name);
        if(index<0)
        {
                log_fnc_err(UNKNOWN_ERROR, "Error: Invalid command (%s)\n", cmd_name);
                display_cmd_help(cmd_config, num_cmd, cmd_name);
                return UNKNOWN_ERROR;
        }

		if(arg_count < cmd_config[index].num_inputs)
        {
                log_fnc_err(UNKNOWN_ERROR, "Error: Invalid command parameters (%s)\n", cmd_name);
                display_cmd_help(cmd_config, num_cmd, cmd_name);
                return UNKNOWN_ERROR;
        }

        // call command specific function
        cmd_config[index].cmd_func();

        return SUCCESS;
}
