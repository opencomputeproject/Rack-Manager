// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include "blade-id-ip-map.h"
#include "ocslog.h"

void __attribute__((constructor)) init(void);

static char address_buffer[16];
static char switch_buffer[16];

void init() {
	load_base_address();
}


int load_base_address() {
	int handle;
	int response = SUCCESS;
	struct ifreq ifr;
	int last_octet_idx;
	char address[16];
	char last_octet[4];
	int octet;
	char *addptr;
	addptr = address;

	handle = socket(AF_INET, SOCK_DGRAM, 0);

	if (handle == -1) {
		log_fnc_err(FAILURE, "error creating socket: %d\n", errno);
		response = FAILURE;
		goto clean_up;
	}

	ifr.ifr_addr.sa_family = AF_INET;

	/* eth1 always switch connection */
	strncpy(ifr.ifr_name, "eth1", IFNAMSIZ - 1);

	ioctl(handle, SIOCGIFADDR, &ifr);

	if (ioctl == -1) {
		log_fnc_err(FAILURE, "ioctl error getting ip address: %d\n", errno);
		response = FAILURE;
		goto clean_up;
	}

	stpcpy(address, inet_ntoa(((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr));

	/* pointer subtraction */
	last_octet_idx = (strrchr(address, '.') - addptr) + 1;

	memset(address_buffer, 0, sizeof(address_buffer));

	strncpy(address_buffer, address, last_octet_idx);
	strcat(address_buffer, "\%d");

	strcpy(last_octet, &address[last_octet_idx]);
	sscanf(last_octet, "%d", &octet);

	sprintf(switch_buffer, address_buffer, (octet -1));

clean_up:
	close(handle);

	return response;
}

int get_server_address(uint8_t slot_id, char *address) {

	if (address == NULL)
		return 1;

	if (strchr(address_buffer, '.') == NULL) {
		if (load_base_address() != SUCCESS) {
			return FAILURE;
		}
	}

	if (slot_id > 0 && slot_id <= 48) {
		sprintf(address, address_buffer, ((slot_id * 4) - 3));
		return SUCCESS;
	}
	else
		return FAILURE;
}

int get_switch_address(char *address) {

	if (address == NULL)
		return FAILURE;

	if (strchr(switch_buffer, '.') == NULL) {
		if (load_base_address() != SUCCESS) {
			return FAILURE;
		}
	}

	strcpy(address, switch_buffer);

	return SUCCESS;
}

int get_server_console_access(char *username, char *password) {
	strcpy(username, "xxxxx");
	strcpy(password, "xxxxx");
	return SUCCESS;
}

int get_server_command_access(char *username, char *password) {
	strcpy(username, "xxxxx");
	strcpy(password, "xxxxx");
	return SUCCESS;
}

int get_server_rest_access(char *username, char *password) {
	strcpy(username, "xxxxxx");
	strcpy(password, "xxxxxx");
	return SUCCESS;
}

int get_switch_access(char *username, char *password) {
	strcpy(username, "xxxxx");
	strcpy(password, "xxxxx");
	return SUCCESS;
}
