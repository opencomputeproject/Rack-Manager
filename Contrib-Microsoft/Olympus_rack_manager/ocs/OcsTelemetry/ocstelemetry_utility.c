// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>

#include "ocstelemetry.h"

#define GET_OPTIONS "b:e:s:f:l:c:i:"
#define CLEAR_OPTIONS "h:"

//
// Shell help prompt
//

void Usage(void)
{
	printf("\nOcsTelemetry Log File Access Utility\n");
	printf("Format: ocstelemetry_utility <command> <options>\n\n");
	printf("Commands: \n");
	printf("1) GetLog  -- Retrieve log contents\n");
	printf("options: -b <start_time> -- start time in seconds since Epoch (optional)\n");
	printf("         -e <end_time>   -- end time in seconds since Epoch (optional)\n");
	printf("         -s <start_id>   -- start message id in decimal (optional)\n");
	printf("         -f <end_id>     -- end message id in decimal (optional)\n");
	printf("         -l <log_level>  -- 0:Info, 1:Warning, 2:Error (optional)\n");
	printf("         -c <component>  -- 0:RackManager, 1:Switch, 2:SwitchPort, 3:Server, 4:ServerPower, 5:ServerFan (optional)\n");
	printf("         -i <server_id or port_id> (optional)\n");
	printf("\n\n 2) ClearLog -- Clear log contents\n");
}

//
// Main shell application
//

int main(int argc, char** argv)
{
	int result;
	int opt;
	char* command = argv[1];
	char filename[MAX_FILENAME_SIZE];
	char filename0[MAX_FILENAME_SIZE];
	char filename1[MAX_FILENAME_SIZE];

	if(argc < 2 || argc > 16)
	{
		printf("\nIncorrect number of parameters!\n");

		Usage();

		return STATUS_FAILURE;
	}

	if(strcmp(command, "GetLog") == 0)
	{
		time_t start_time = -1;
		time_t end_time = -1;
		int log_level = -1;
		int component = -1;
		int bladeid = -1;
		int portid = -1;
		int start_id = -1;
		int end_id = -1;

		while((opt = getopt(argc, argv, GET_OPTIONS)) != -1)
		{
			switch(opt)
			{
				case 'b':
				{
					start_time = atol(optarg);

					break;
				}

				case 'e':
				{
					end_time = atol(optarg);

					break;
				}

				case 's':
				{
					start_id = atol(optarg);

					break;
				}

				case 'f':
				{
					end_id = atol(optarg);

					break;
				}

				case 'l':
				{
					log_level = atoi(optarg);

					if(log_level < INFO || log_level >= NUM_LEVELS)
					{
						fprintf(stderr, "\nIncorrect log_level: %i\n", log_level);

						Usage();

						return STATUS_FAILURE;
					}

					break;
				}

				case 'c':
				{
					component = atoi(optarg);

					if(component < RACK || component >= NUM_COMPONENTS)
					{
						fprintf(stderr, "\nIncorrect component: %i\n", component);

						Usage();

						return STATUS_FAILURE;
					}

					break;
				}

				case 'i':
				{
					if(component == SERVER_FAN)
					{
						bladeid = atoi(optarg);
					}
					else if(component == SWITCH_PORT)
					{
						portid = atoi(optarg);
					}
					else if(component != -1)
					{
						fprintf(stderr, "\nCannot pass id for this component: %i \n", component);

						return STATUS_FAILURE;
					}
					else
					{
						bladeid = atoi(optarg);
						portid = atoi(optarg);
					}

					break;
				}

				default:
				{
					fprintf(stderr, "\nUnknown parameter: %c\n", opt);

					Usage();

					return STATUS_FAILURE;
				}
			}
		}

		strcpy(filename,"/usr/srvroot/ocstelemetry");
		strcat(filename, ".log");

		result = TelemetryGetLog(start_time, end_time, start_id, end_id, log_level, component, bladeid, portid, filename);

		if(result != STATUS_SUCCESS)
		{
			fprintf(stderr, "\nUnable to read log!\n");

			return STATUS_FAILURE;
		}

		strcpy(filename0,"/usr/srvroot/ocstelemetry");
		strcat(filename0, ".log");
		strcat(filename0, ".0");
		TelemetryGetLog(start_time, end_time, start_id, end_id, log_level, component, bladeid, portid, filename0);

		strcpy(filename1,"/usr/srvroot/ocstelemetry");
		strcat(filename1, ".log");
		strcat(filename1, ".1");
		TelemetryGetLog(start_time, end_time, start_id, end_id, log_level, component, bladeid, portid, filename1);
	}

	else if (strcmp(command, "ClearLog") == 0)
	{
		while((opt = getopt(argc, argv, CLEAR_OPTIONS)) != -1)
		{
			switch(opt)
			{
				default:
				{
					fprintf(stderr, "\nUnknown parameter: %c\n", opt);

					Usage();

					return STATUS_FAILURE;
				}
			}
		}

		strcpy(filename,"/usr/srvroot/ocstelemetry");
		strcat(filename, ".log");

		result = TelemetryClearLog(filename);

		if(result != STATUS_SUCCESS)
		{
			fprintf(stderr, "\nUnable to clear log!\n");

			return STATUS_FAILURE;
		}

		strcat(filename, ".0");
		result = TelemetryClearLog(filename);

		strcpy(filename1,"/usr/srvroot/ocstelemetry");
		strcat(filename1, ".log");
		strcat(filename1, ".1");
		result = TelemetryClearLog(filename1);
	}

	else
	{
		fprintf(stderr, "\nIncorrect command! %s\n", command);

		Usage();

		return STATUS_FAILURE;
	}

	return STATUS_SUCCESS;
}
