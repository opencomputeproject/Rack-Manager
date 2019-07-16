// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include "ocslock.h"
#include "ocslog.h"
#include "ocs-persist.h"

#define PERSIST_FILE "/usr/srvroot/ocs-persist.txt"

/*
* Get persist Value from provided Key
* Param1: Input Key 
* Param2: Return Value
*/
int get_persist(char* key, char* value) {
	if(access(PERSIST_FILE,F_OK)!=-1) {
		char read_cmd[100], buffer[100];
		sprintf(read_cmd, "sed -n '/%s/p' %s", key, PERSIST_FILE);
		if(ocs_lock(PRU_PERSIST)!=SUCCESS) {
			log_err(UNKNOWN_ERROR, "get_persist: ocs_lock failed\n");
			return UNKNOWN_ERROR;
		}
		FILE *fp = popen(read_cmd, "r");
		if(ocs_unlock(PRU_PERSIST)!=SUCCESS) {
			log_err(UNKNOWN_ERROR, "get_persist: ocs_unlock failed\n");
		}
		if(fp==NULL) {
			log_err(UNKNOWN_ERROR, "get_persist: persist file(%s) read failed\n", PERSIST_FILE);
			return UNKNOWN_ERROR;
		}
		fgets(buffer, 100, fp);
		char file_cmd[100];
		sscanf(buffer, "%s %s\n", file_cmd, value);
		pclose(fp);
	}
	else {
		log_err(UNKNOWN_ERROR, "get_persist: Persist file (%s) does not exist.\n", PERSIST_FILE);
		return UNKNOWN_ERROR;
	}
	return SUCCESS;
}

/*
* Set persist key/Value 
* Param1: Input Key 
* Param2: Input Value
*/
int set_persist(char* key, char* value) {
	if(access(PERSIST_FILE,F_OK)!=-1) {
		char write_cmd[100];
		FILE *fp = NULL;
		sprintf(write_cmd, "sed -i '/%s /d' %s", key, PERSIST_FILE);
		if(ocs_lock(PRU_PERSIST)!=SUCCESS) {
			log_err(UNKNOWN_ERROR, "set_persist_value: ocs_lock failed\n");
			return UNKNOWN_ERROR;
		}
		fp = popen(write_cmd, "r");
		
		if(fp==NULL) {
			log_err(UNKNOWN_ERROR, "set_persist_value: persist file(%s) write (delete) failed\n", PERSIST_FILE);
			if(ocs_unlock(PRU_PERSIST)!=SUCCESS) {
        		log_err(UNKNOWN_ERROR, "set_persist_value: ocs_unlock failed\n");
        	}
			return UNKNOWN_ERROR;
		}
		pclose(fp);

		char write_str[100];
		sprintf(write_str, "echo %s %s >> %s", key, value, PERSIST_FILE);
		fp = popen(write_str, "r");
		if(ocs_unlock(PRU_PERSIST)!=SUCCESS) {
        	log_err(UNKNOWN_ERROR, "set_persist_value: ocs_unlock failed\n");
		}
		if(fp==NULL) {
			log_err(UNKNOWN_ERROR, "set_persist_value: persist file(%s) write (add) failed\n", PERSIST_FILE);
			return UNKNOWN_ERROR;
		}
		pclose(fp);
	}
	else {
		log_err(UNKNOWN_ERROR, "set_persist_value: Persist file (%s) does not exist.\n", PERSIST_FILE);
		return UNKNOWN_ERROR;
	}
	return SUCCESS;
}
