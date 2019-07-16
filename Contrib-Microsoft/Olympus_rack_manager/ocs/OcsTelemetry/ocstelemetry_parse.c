// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#include "ocslock.h"
#include "ocstelemetry.h"

//
// Parse line into log_entry struct
//

int TelemetryParseLine(char* line, log_entry* entry)
{
	struct tm time_info;
	int day, month, year, second, minute, hour;

	if(line == NULL || entry == NULL)
	{
		return STATUS_FAILURE;
	}

	// Parse id
	char* substring = strchr(line, '|');

	if(substring != NULL)
	{
		sscanf(line, "%x |", &entry->message_id);

		line = substring + 1;
	}
	else
	{
		return STATUS_FAILURE;
	}

	// Parse date
	substring = strchr(line, '|');

	if(substring != NULL)
	{
		sscanf(line, "%2d/%2d/%4d", &month, &day, &year);

		line = substring + 1;
	}
	else
	{
		return STATUS_FAILURE;
	}

	// Parse time
	substring = strchr(line, '|');

	if(substring != NULL)
	{
		sscanf(line, "%2d:%2d:%2d", &hour, &minute, &second);

		time_info.tm_year = year - 1900;
		time_info.tm_mon = month - 1;
		time_info.tm_mday = day;
		time_info.tm_hour = hour;
		time_info.tm_min = minute;
		time_info.tm_sec = second;

		entry->time = mktime(&time_info);

		if(entry->time == -1)
		{
			return STATUS_FAILURE;
		}

		line = substring + 1;
	}
	else
	{
		return STATUS_FAILURE;
	}

	// Parse component, log level, id
	substring = strchr(line, '|');

	if(substring != NULL)
	{
		//Parse component 
		if(strstr(line, "Rack Manager") != NULL)
		{
			entry->component = RACK;
		}
		else if(strstr(line, "Power Readings") != NULL)
		{
			entry->component = SERVER_POWER;
		}
		else if(strstr(line, "Fans") != NULL)
		{
			entry->component = SERVER_FAN;

			// Parse id 
			sscanf(line, "%*s%d", &(entry->bladeid));
		}
		else if(strstr(line, "Servers") != NULL)
		{
			entry->component = SERVER;
		}
		else if(strstr(line, "Port") != NULL)
		{
			entry->component = SWITCH_PORT;

			// Parse id 
			sscanf(line, " Switch Port %d", &(entry->portid));
		}
		else if(strstr(line, "Switch") != NULL)
		{
			entry->component = SWITCH;
		}

		//Parse log level
		if(strstr(line, "Info") != NULL)
		{
			entry->level = INFO;
		}
		else if(strstr(line, "Warning") != NULL)
		{
			entry->level = WARNING;
		}
		else if(strstr(line, "Error") != NULL)
		{
			entry->level = ERROR;
		}

		line = substring + 1;
	}
	else
	{
		return STATUS_FAILURE;
	}

	// Parse sensor type and message
	substring = strchr(line, '|');
	char * start = substring + 1;
	
	if(start == NULL)
	{
		return STATUS_FAILURE;
	}

	substring = strchr(start, '|');

	strncpy(entry->sensortype, start, substring - start);

	start = substring + 1;

	if(start == NULL)
	{
		return STATUS_FAILURE;
	}

	strcpy(entry->message, start);

	return STATUS_SUCCESS;
}


//
// Retrieve manager telemtry log entries
//

int TelemetryGetLog(time_t start_time, time_t end_time, int start_id, int end_id, int log_level, int component, int bladeid, int portid, const char* filename)
{
	FILE* LogFile;
	log_entry entry = {0};
	char line[MAX_LINE_LEN];
	int result = STATUS_FAILURE;

	// Check inputs
	if(filename == NULL)
	{
		return STATUS_FAILURE;
	}

	// Check if file being logged to now
	if(ocs_lock(TELEMETRY_DAEMON) != 0)
	{
	 	return STATUS_FAILURE;
	}

	// Open file to read
	LogFile = fopen(filename, "r");

	if(LogFile == NULL)
	{
		ocs_unlock(TELEMETRY_DAEMON);

		return STATUS_FAILURE;
	}

	// Read file line by line
	while(fgets(line, sizeof(line), LogFile))
	{
		memset(&entry, 0, sizeof(entry));

		result = TelemetryParseLine(line, &entry);

		if((result == STATUS_SUCCESS))
		{
			if(start_time != -1 && entry.time < start_time)
			{
				continue;
			}
			
			if(end_time != -1 && entry.time > end_time)
			{
				continue;	
			}

			if(start_id != -1 && entry.message_id < start_id)
			{
				continue;
			}
			
			if(end_id != -1 && entry.message_id > end_id)
			{
				continue;	
			}

			if(log_level != -1 && entry.level != log_level)
			{
				continue;
			}

			if(component != -1 && entry.component != component)
			{
				continue;
			}

			if(bladeid != -1 && entry.bladeid != bladeid)
			{
				continue;
			}

			if(portid != -1 && entry.portid != portid)
			{
				continue;
			}

			printf("%s", line);
		}
	}

	printf("\n");

	fclose(LogFile);
	ocs_unlock(TELEMETRY_DAEMON);

	return STATUS_SUCCESS;
}

//
// Delete manager telemetry log file
//

int TelemetryClearLog(const char* filename)
{
	FILE* LogFile;

	// Check inputs
	if (filename == NULL)
	{
		return STATUS_FAILURE;
	}

	// Check if file being logged to now
	if(ocs_lock(TELEMETRY_DAEMON) != 0)
	{
	 	return STATUS_FAILURE;
	}

	// Open file to write, which erases file contents
	LogFile = fopen(filename, "w");

	if(LogFile != NULL)
	{
		fclose(LogFile);
		ocs_unlock(TELEMETRY_DAEMON);

		return STATUS_SUCCESS;
	}

	ocs_unlock(TELEMETRY_DAEMON);

	return STATUS_FAILURE;
}
