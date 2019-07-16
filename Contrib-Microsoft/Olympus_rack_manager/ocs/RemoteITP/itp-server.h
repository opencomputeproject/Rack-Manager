// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef ITP_SERVER_H_
#define ITP_SERVER_H_

#include <stdint.h>


struct itp_server;

int itp_server_initialize (int id, uint16_t port, const char *jtag_ip, uint16_t jtag_port,
	struct itp_server **server);
int itp_server_listen (struct itp_server *server);
int itp_server_release (struct itp_server *server);


#endif /* ITP_SERVER_H_ */
