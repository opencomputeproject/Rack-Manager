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
#include <termios.h>
#include "mgmt-switch.h"
#include "ocslog.h"


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
static const char *OPTIONS = "d:b:f:t:l:careiupsXh";

/**
 * Usage details for the command line options.
 */
static const char *USAGE = "-c|a|r|i|u|p|s [-d <port>] [-b <baud>] [-f <path>] [-t <address>]"
	"[-l <log level>] [-eXh]";

enum {
	NONE,
	CONFIGURE,
	APPEND,
	RELOAD,
	INACTIVE_IMAGE,
	UPGRADE_IMAGE,
	PASSIVE,
	INTERACTIVE,
};

/**
 * Parse an integer and get the baud rate value.
 *
 * @param baud The baud rate to parse.
 *
 * @return The port baud rate setting.
 */
static int parse_baud_rate (int baud)
{
	switch (baud) {
		case 0:
			return B0;
		case 50:
			return B50;
		case 75:
			return B75;
		case 110:
			return B110;
		case 134:
			return B134;
		case 150:
			return B150;
		case 200:
			return B200;
		case 300:
			return B300;
		case 600:
			return B600;
		case 1200:
			return B1200;
		case 1800:
			return B1800;
		case 2400:
			return B2400;
		case 4800:
			return B4800;
		case 9600:
			return B9600;
		case 19200:
			return B19200;
		case 38400:
			return B38400;
		case 57600:
			return B57600;
		case 115200:
			return B115200;
		case 230400:
			return B230400;
		default:
			return -1;
	}
}

int main (int argc, char *argv[])
{
	char *dev = "/dev/ttyUSB0";
	char *path = "Configuration.txt";
	char *address = "";
	int baud = B115200;
	int echo = 0;
	int action = NONE;
	int level = ERROR_LEVEL;
	int catch_sigint = 1;
	int status;
	char *error;
	struct sigaction handler;
	int line;
	int opt;

	while ((opt = getopt (argc, argv, OPTIONS)) != -1) {
		switch (opt) {
			case 'd':
				dev = optarg;
				break;

			case 'b':
				baud = parse_baud_rate (atoi (optarg));
				break;

			case 'f':
				path = optarg;
				break;

			case 't':
				address = optarg;
				break;

			case 'l':
				level = atoi (optarg);
				break;

			case 'e':
				echo = 1;
				setbuf (stdout, NULL);
				break;

			case 'c':
				action = CONFIGURE;
				break;

			case 'a':
				action = APPEND;
				break;

			case 'r':
				action = RELOAD;
				break;

			case 'i':
				action = INACTIVE_IMAGE;
				break;

			case 'u':
				action = UPGRADE_IMAGE;
				break;

			case 'p':
				action = PASSIVE;
				echo = 1;
				setbuf (stdout, NULL);
				break;

			case 's':
				action = INTERACTIVE;
				echo = 1;
				setbuf (stdout, NULL);
				break;

			case 'X':
				catch_sigint = 0;
				break;

			case 'h':
				printf ("%s %s\n", argv[0], USAGE);
				return 0;

			default:
				fprintf (stderr, "%s %s\n", argv[0], USAGE);
				return 1;
		}
	}

	if (baud < 0) {
		fprintf (stderr, "Invalid baud rate specified.\n");
		return 1;
	}
	if (action == NONE) {
		fprintf (stderr, "No control action specified.\n");
	}

	log_init (level);

	memset (&handler, 0, sizeof (handler));
	handler.sa_handler = close_program;
	if (sigaction (SIGINT, &handler, NULL) != 0) {
		log_out ("Failed to register INT signal handler: %s", strerror (errno));
		return 1;
	}
	if (sigaction (SIGTERM, &handler, NULL) != 0) {
		log_out ("Failed to register TERM signal handler: %s", strerror (errno));
		return 1;
	}

	status = mgmt_switch_connect_console (dev, echo, baud);
	if (status != 0) {
		log_out ("Failed to connect to switch console using %s: %s", dev, strerror (status));
		return status;
	}

	switch (action) {
		case CONFIGURE:
			if (access (path, F_OK) != 0) {
				status = errno;
				log_out ("Can't find configuration file %s", path);
				break;
			}

			status = mgmt_switch_clear_startup_config (1);
			if (status != 0) {
				log_out ("Failed to clear startup configuration: %s", strerror (status));
				break;
			}

			status = mgmt_switch_reboot (1);
			if (status != 0) {
				log_out ("Failed to reboot switch: %s", strerror (status));
				break;
			}

		case APPEND:
			status = mgmt_switch_apply_config_file (path, &line, &error);
			if (status != 0) {
				if ((status == EBADE) && (error != NULL)) {
					log_out ("Error executing configuration command on line %d: %s", line, error);
					free (error);
				}
				else {
					log_out ("Failed to apply configuration file %s: %s", path,
						strerror (status));
				}
				break;
			}

			status = mgmt_switch_save_startup_config (0);
			if (status != 0) {
				log_out ("Failed to save startup configuration: %s", strerror (status));
			}
			break;

		case RELOAD:
			status = mgmt_switch_reboot (0);
			if (status != 0) {
				log_out ("Failed to reload switch firmware: %s", strerror (status));
			}
			break;

		case INACTIVE_IMAGE:
			status = mgmt_switch_activate_inactive_image ();
			if (status != 0) {
				log_out ("Failed to activate inactive firmware image: %s", strerror (status));
				break;
			}

			status = mgmt_switch_reboot (0);
			if (status != 0) {
				log_out ("Failed to reload switch firmware: %s", strerror (status));
			}
			break;

		case UPGRADE_IMAGE:
			status = mgmt_switch_upload_firmware (address, path);
			if (status != 0) {
				log_out ("Failed to upload new firmware image: %s", strerror (status));
				break;
			}

			status = mgmt_switch_reboot (0);
			if (status != 0) {
				log_out ("Failed to reload switch firmware: %s", strerror(status));
			}
			break;

		case PASSIVE:
			mgmt_switch_dump_console ();
			break;

		case INTERACTIVE:
			status = mgmt_switch_interactive_console (catch_sigint);
			if (status != 0) {
				log_out ("Failed to start interactive shell: %s", strerror(status));
			}
			break;
	}

	if ((action != PASSIVE) && (action != INTERACTIVE)) {
		mgmt_switch_console_logout ();
	}

	mgmt_switch_disconnect_console ();
	return status;
}
