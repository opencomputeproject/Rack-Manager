// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <netinet/in.h>
#include "itp-server.h"
#include "ocslog.h"
#include "blade-id-ip-map.h"
#include "pre-checks.h"
#include "ocsgpioaccess.h"


/**
 * Signal handler for the application.
 *
 * @param signum The signal that was received.
 */
static void close_program (int signum)
{
//	printf ("Received signal %d.\n", signum);
}

/**
 * List of supported command line options.
 */
static const char *OPTIONS = "p:l:m:c:h";

/**
 * Usage details for the command line options.
 */
static const char *USAGE = "[-p <start port>] [-l <log level>] [-m <mode>] [-c <count>] [-h]";

/**
 * The maximum number of ITP forwarding servers that can be run.
 */
#define MAX_ITP_SERVERS		48

int main (int argc, char *argv[])
{
	int port = 5125;
	int level = INFO_LEVEL;
	int mode = -1;
	int count = -1;
	int status;
	int opt;
	struct sigaction handler;
	struct itp_server *server[MAX_ITP_SERVERS] = {0};
	int i;
	char address[INET_ADDRSTRLEN];
	unsigned long long presence;
	int use_presence = 1;
	int initialized;

	while ((opt = getopt (argc, argv, OPTIONS)) != -1) {
		switch (opt) {
			case 'p':
				port = atoi (optarg);
				break;

			case 'l':
				level = atoi (optarg);
				break;

			case 'm':
				mode = atoi (optarg);
				break;

			case 'c':
				count = atoi (optarg);
				use_presence = 0;
				break;

			case 'h':
				printf ("%s %s\n", argv[0], USAGE);
				return 0;

			default:
				fprintf (stderr, "%s %s\n", argv[0], USAGE);
				return 1;
		}
	}

	log_init (level);

	if (mode < 0) {
		status = get_rm_mode (&mode);
		if (status != 0) {
			log_err (status, "Failed to determine RM mode (%d), using default.", status);
			mode = PMDU_RACKMANAGER;
		}
	}
	else if (mode > TFB_DEV_BENCHTOP) {
		fprintf (stderr, "Invalid mode specified: %d\n", mode);
		return 1;
	}

	if (count < 0) {
		switch (mode) {
			case PMDU_RACKMANAGER:
			case TFB_DEV_BENCHTOP:
				count = 48;
				break;

			case STANDALONE_RACKMANAGER:
				count = 24;
				break;

			default:
				count = 0;
				break;
		}
	}
	else if (count > MAX_ITP_SERVERS) {
		fprintf (stderr, "Too many servers specified: %d, max=%d\n", count, MAX_ITP_SERVERS);
		return 1;
	}

	if (count == 0) {
		log_info ("Not running any ITP forwarding servers.");
		return 0;
	}

	if (use_presence) {
		use_presence = ocs_port_present (0, &presence);
		if (status != 0) {
			log_err (status, "Failed to determine port presence.  Running maximum server count.");
		}
	}
	else {
		use_presence = -1;
	}

	memset (&handler, 0, sizeof (handler));
	handler.sa_handler = close_program;
	if (sigaction (SIGINT, &handler, NULL) != 0) {
		log_err (errno, "Failed to register INT signal handler.");
		return 1;
	}
	if (sigaction (SIGTERM, &handler, NULL) != 0) {
		log_err (errno, "Failed to register TERM signal handler.");
		return 1;
	}

	initialized = 0;
	for (i = 1; i <= count; i++) {
		if ((use_presence != 0) || (presence & 0x1)) {
			int itp_port = port + (i - 1);

			status = get_server_address (i, &address);
			if (status != 0) {
				log_err (status, "Failed to get JTAG target address %d.", i);
				goto init_fail;
			}

			status = itp_server_initialize (i, itp_port, address, 5125, &server[i - 1]);
			if (status != 0) {
				log_err (status, "Failed to initialize ITP server %d.", i);
				goto init_fail;
			}

			initialized++;
		}

		presence >>= 1;
	}

	for (i = 0; i < count; i++) {
		if (server[i] != NULL) {
			status = itp_server_listen (server[i]);
			if (status != 0) {
				log_err (status, "Failed to start listening for connections on server %d.", i + 1);
				goto init_fail;
			}
		}
	}

	if (initialized != 0) {
		pause ();
	}
	else {
		log_info ("No servers present.  Stopping ITP forwarding server.\n");
	}

	for (i = 0; i < count; i++) {
		status = itp_server_release (server[i]);
		if (status != 0) {
			log_err (status, "Failed to release ITP server %d.", i + 1);
		}
	}

	return status;

init_fail:
	for (i = 0; i < count; i++) {
		itp_server_release (server[i]);
	}
	return status;
}
