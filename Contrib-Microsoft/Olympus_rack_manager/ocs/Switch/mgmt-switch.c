// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <sys/file.h>
#include "mgmt-switch.h"
#include "ocslog.h"
#include "blade-id-ip-map.h"

/**
 * Delimiters for terminating both on a new line and a command prompt.
 */
static const char *NEWLINE_OR_PROMPT = "#:\n";

/**
 * Delimiters for terminating only on a new line.
 */
static const char *NEWLINE = "\n";

/**
 * Delimiters for terminating only on a prompt.
 */
static const char *PROMPT = "#:";


/**
 * State information for the connection to the management switch.
 */
static struct mgmt_switch
{
	int dev;	/**< The file descriptor for the serial port. */
	int connected;	/**< Flag indicating if the connection has been established. */
	int echo;	/**< Flag indicating if console reads should be sent to stdout. */
} connection;


/**
 * Initialize the connection to the console of the management switch.
 *
 * @param dev The path of the device to use for the connection.
 * @param echo Flag indicating that all lines read from the console should be echoed to stdout.
 * @param baud The baud rate to use for the connection.
 *
 * @return 0 if the connection was established successfully or an error code.
 */
int mgmt_switch_connect_console (const char *dev, int echo, speed_t baud)
{
	struct termios attr;
	int error;

	if (connection.connected) {
		return EISCONN;
	}

	connection.dev = open (dev, O_RDWR | O_NOCTTY);
	if (connection.dev < 0) {
		return errno;
	}

	error = flock (connection.dev, LOCK_EX | LOCK_NB);
	if (error != 0) {
		error = errno;
		close (connection.dev);
		return error;
	}

	if (tcgetattr (connection.dev, &attr) != 0) {
		goto error_unlock;
	}

	cfmakeraw (&attr);
	if (cfsetspeed (&attr, baud) != 0) {
		goto error_unlock;
	}

	if (tcsetattr (connection.dev, TCSANOW, &attr) != 0) {
		goto error_unlock;
	}

	if (tcflush (connection.dev, TCIFLUSH) != 0) {
		goto error_unlock;
	}

	log_info ("Connected to console using %s", dev);
	connection.connected = 1;
	connection.echo = echo;
	return 0;

error_unlock:
	error = errno;
	flock (connection.dev, LOCK_UN);
	close (connection.dev);
	return error;
}

/**
 * Teardown the connection to the console of the management switch.
 */
void mgmt_switch_disconnect_console ()
{
	if (connection.connected) {
		flock (connection.dev, LOCK_UN);
		close (connection.dev);
		connection.connected = 0;
	}
}

/**
 * Write to the serial port connected to the management switch console.
 *
 * @param data The data to send.
 * @param length The length of the data.
 *
 * @return The number of bytes written to the port or a negative error code.
 */
static int mgmt_switch_write_data (const char *data, int length)
{
	int bytes;
	int sent = 0;

	bytes = write (connection.dev, data, length);
	while ((bytes > 0) && ((length - bytes) > 0)) {
		sent += bytes;
		length -= bytes;
		bytes = write (connection.dev, data + sent, length);
	}

	if (bytes >= 0) {
		sent += bytes;
	}
	else {
		sent = -errno;
	}
	return sent;
}

/**
 * Write a string to the serial port to send data to the management switch console.
 *
 * @param data The null-terminated data string to send to the console.
 *
 * @return The number of bytes written to the port or a negative error code.
 */
static int mgmt_switch_send_data (const char *data)
{
	int length = strlen (data);
	if (length > 0) {
		return mgmt_switch_write_data (data, length);
	}
	else {
		return 0;
	}
}

/**
 * Read the serial port to get the data from the management switch console.  The port will be read
 * until a newline or a prompt is encountered.
 *
 * @param data The buffer to hold the data.  This will be null terminated upon return.
 * @param length The size of the data buffer.
 * @param blanks Flag to indicate if blank lines should be read and returned.  If this flag is
 * false, then blank lines will be skipped.
 * @param print Flag to indicate if the line that has been read should be printed to stdout.
 * @param delim The list of delimiter characters to use to indicate when to stop reading.
 *
 * @return The number of bytes read from the port or a negative error code.
 */
static int mgmt_switch_read_data (char *data, int length, int blanks, int print, const char *delim)
{
	int error;
	int total = 0;
	char byte;
	int done = 0;

	length -= 1;
	while ((total < length) && !done) {
		error = read (connection.dev, &byte, 1);
		if (error == 1) {
			if (blanks || (total > 0) || (byte > 0x20)) {
				data[total++] = byte;

				if ((strchr (delim, byte) != NULL)) {
					done = 1;
				}
			}
		}
		else {
			done = 1;
			if (error < 0) {
				total = -errno;
			}
		}
	}

	if (total >= 0) {
		data[total] = '\0';

		if (print) {
			printf ("%s", data);
		}
		else {
			log_info ("%s", data);
		}
	}
	return total;
}

/**
 * Read data from the management switch console until the expected message has been received.
 *
 * @param match The message to match from the console.
 * @param print Flag indicating if all read lines should be printed to stdout.
 * @param delim The list of delimiter characters to use to single the end of a line.
 *
 * @return 0 if the expected message was received or an error code.
 */
static int mgmt_switch_read_until (const char *match, int print, const char *delim)
{
	int status = 0;
	char line[512];

	do {
		status = mgmt_switch_read_data (line, sizeof (line), 0, print, delim);
	} while ((status > 0) && (strcmp (match, line) != 0));

	if (status == 0) {
		status = -ENOLINK;
	}
	return (status > 0) ? 0 : -status;
}

/**
 * Send a command to the management switch console.
 *
 * @param command The command to send.  No carriage return is necessary.
 * @param login Flag indicating if the console should automatically be logged in before sending the
 * command.
 *
 * @return 0 if the command was successfully sent, -1 if the no command data was provided, or an
 * error code.
 */
static int mgmt_switch_send_command (const char *command, int login)
{
	int status;
	const int cmdlen = strlen (command);
	char tmp[cmdlen + 1];
	const char *send = command;
	int newline;

	if (login) {
		status = mgmt_switch_console_login ();
		if (status != 0) {
			return status;
		}
	}

	// Trim the beginning and end of the command.
	newline = strcspn (command, "\r\n");
	if (newline < cmdlen) {
		strcpy (tmp, command);
		tmp[newline] = '\0';
		send = tmp;
	}
	while ((*send != 0) && (*send <= 0x20)) {
		send++;
	}

	status = mgmt_switch_send_data (send);
	if (status < 0) {
		return -status;
	}

	return (status == 0) ? -1 : mgmt_switch_send_enter ();
}

/**
 * Check a command result and provide the completion status of the command.  In the case of an,
 * read upto the next prompt from the console.
 *
 * @param result The result string to check.
 * @param length The length of the result string, excluding the null terminator.
 * @param error If this is not null and the result is an error, the a copy of the message will be
 * allocated and saved here.
 *
 * @return The completion status for the command.
 */
static int mgmt_switch_check_command_result (const char *result, int length, char **error) {
	if (result[length - 1] == '#') {
		// The next line is the console prompt, so the command was successful.
		return 0;
	}
	else {
		if (error != NULL) {
			char prompt[512];

			*error = strdup (result);
			*error[strcspn (*error, "\r\n")] = '\0';

			mgmt_switch_read_data (prompt, sizeof (prompt), 0, connection.echo, PROMPT);
		}

		if (strstr (result, "% Unrecognized command") == NULL) {
			return EBADE;
		}
		else if (strstr (result, "% Incomplete command") == NULL) {
			return EBADE;
		}
		else if (strstr (result, "% Ambiguous command") == NULL) {
			return EBADE;
		}
		else if (strstr (result, "% missing mandatory parameter") == NULL) {
			return EBADE;
		}
		else if (strstr (result, "% bad parameter value") == NULL) {
			return EBADE;
		}
		else {
			// Also treat any other output as an error.
			return EBADE;
		}
	}
}

/**
 * Execute a command that will be echoed exactly back to the console and will only generate
 * additional output to indicate an error.
 *
 * @param command The command to execute.
 * @param login Flag indicating if the console should be automatically logged in.
 * @param check Flag indicating if the command result should be checked for errors.
 *
 * @return 0 if the command was executed successfully or an error code.
 */
static int mgmt_switch_execute_echoed_command (const char *command, int login, int check)
{
	int status;
	char response[512];

	status = mgmt_switch_send_command (command, login);
	if (status != 0) {
		return (status < 0) ? 0 : status;
	}

	do {
		status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo, NEWLINE);
	} while (check && (status > 0) && (strstr (response, command) == NULL));

	status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo,
		(check) ? NEWLINE_OR_PROMPT : PROMPT);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	if (check) {
		return mgmt_switch_check_command_result (response, status, NULL);
	}
	else {
		return 0;
	}
}

/**
 * Disable sending system logging messages to the console.  The session will not be automatically
 * logged in and must be at the root prompt.
 *
 * @return 0 if console logging was disabled or an error code.
 */
static int mgmt_switch_disable_console_logging ()
{
	int status;

	if (!connection.connected) {
		return ENOTCONN;
	}

	status = mgmt_switch_execute_echoed_command ("config", 0, 0);
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_execute_echoed_command ("no logging console", 0, 0);
	if (status != 0) {
		return status;
	}

	return mgmt_switch_execute_echoed_command ("exit", 0, 0);
}

/**
 * Send the login information to the management switch console.
 *
 * @return 0 if the login information was successfully sent or an error code.
 */
static int mgmt_switch_send_login ()
{
	int status;
	char line[512];
	char username[32];
	char password[32];
	
	status = get_switch_access (username, password);
	if (status != 0) {
		return status;
	}
	
	strcat (username, "\n");
	strcat (password, "\n");
	
	status = mgmt_switch_send_data (username);
	if (status < 0) {
		return -status;
	}

	status = mgmt_switch_read_until ("Password:", connection.echo, NEWLINE_OR_PROMPT);
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_send_data (password);
	if (status < 0) {
		return -status;
	}

	status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, "#:?");
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}
	else if (strstr (line, "Do you want to change the password") != NULL) {
		status = mgmt_switch_send_data ("N");
		if (status < 0) {
			return -status;
		}

		status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);
		if (status <= 0) {
			return (status < 0 ) ? -status : ENOLINK;
		}
	}

	if (line[status - 1] != '#') {
		return ECONNREFUSED;
	}

	mgmt_switch_disable_console_logging ();
	return 0;
}

/**
 * Backup the startup configuration to another location on flash.
 *
 * @return 0 if the startup configuration was successfully backed up or an error code.
 */
static int mgmt_switch_backup_startup_config ()
{
	int status;
	char response[512];

	status = mgmt_switch_send_data ("copy startup-config flash://ocs-config.bak\n");
	if (status < 0) {
		return -status;
	}

	// Read back the echoed command.
	status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo, NEWLINE);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo, "]#");
	if (status < 0) {
		return (status < 0) ? -status: ENOLINK;
	}

	if (strstr (response, "Overwrite file") != NULL) {
		status = mgmt_switch_send_data ("Y");
		if (status < 0) {
			return -status;
		}
	}

	while ((status > 0) && (response[status - 1] != '#')) {
		status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo, "]#");
		if (status <= 0) {
			return (status < 0) ? -status : ENOLINK;
		}
	}

	return 0;
}

/**
 * Send a carriage return to the management switch console.
 *
 * @return 0 if the carriage return was sent or an error code.
 */
int mgmt_switch_send_enter ()
{
	int status;

	if (!connection.connected) {
		return ENOTCONN;
	}

	status = mgmt_switch_send_data ("\n");
	return (status > 0) ? 0 : -status;
}

/**
 * Login to the console of the management switch.
 *
 * @return 0 if the connection has successfully logged into the console or an error code.
 */
int mgmt_switch_console_login ()
{
	int status;
	char line[512];
	int done = 0;

	status = mgmt_switch_send_enter ();
	if (status != 0) {
		return status;
	}

	do {
		status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, NEWLINE_OR_PROMPT);
		if (status < 0) {
			return -status;
		}

		if (strstr (line, "User Name:") != NULL) {
			return mgmt_switch_send_login ();
		}
		if (strstr (line, "Password:") != NULL) {
			status = mgmt_switch_send_enter ();
			if (status != 0) {
				return status;
			}
		}
		else if (strstr (line, "authentication failed") != NULL) {
			// There was an error starting authentication.  We just need to try again.
			status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, NEWLINE);
			if (status < 0) {
				return -status;
			}

			return mgmt_switch_console_login ();
		}
		else if (line[status - 1] == '#') {
			// We are already at the command prompt.
			done = 1;
		}
	} while (!done);

	return 0;
}

/**
 * Logout from the console of the management switch.
 *
 * @return 0 if the connection has successfully logged out or an error code.
 */
int mgmt_switch_console_logout ()
{
	int status;
	char line[512];

	if (!connection.connected) {
		return ENOTCONN;
	}

	status = mgmt_switch_send_enter ();
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);
	while ((status > 0) && (strstr (line, "User Name:") == NULL)) {
		status = mgmt_switch_send_data ("exit\n");
		if (status > 0) {
			status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);
		}
	}

	if (status == 0) {
		status = -ENOLINK;
	}
	return (status > 0) ? 0 : -status;
}

/**
 * Exit out of any active sub-menus and return the console to the root prompt of the system.  The
 * connection will be logged into the console if it is not already logged in.
 *
 * @return 0 if the console is not active at the root prompt or an error code.
 */
int mgmt_switch_goto_root_prompt ()
{
	int status;
	char line[512];

	status = mgmt_switch_console_login ();
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_send_enter ();
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);
	while ((status > 0) && (line[status - 2] ==')')) {
		status = mgmt_switch_send_data ("exit\n");
		if (status > 0) {
			status = mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);
		}
	}

	if (status == 0) {
		status = -ENOLINK;
	}
	return (status > 0) ? 0 : -status;
}

/**
 * Reboot the management switch.  This function will not return until the reboot has completed or an
 * error occurs.
 *
 * @param login Flag indicating if the connection should be logged in after the reboot.
 *
 * @return 0 if the reboot was completed successfully or an error code.
 */
int mgmt_switch_reboot (int login)
{
	int status;

	status = mgmt_switch_console_login ();
	if (status != 0) {
		return status;
	}

	status = mgmt_switch_send_data ("reload\nYYY");
	if (status < 0) {
		return -status;
	}

	status = mgmt_switch_read_until ("User Name:", connection.echo, ":\n");
	if (status != 0) {
		return status;
	}

	if (login) {
		return mgmt_switch_send_login ();
	}

	return 0;
}

/**
 * Issue a configuration command to the management switch using the console connection.  The command
 * being sent should expect no output from the console unless there is an error.
 *
 * @param command The command string to send.  Any newline present in the command will be removed.
 * @param login Flag to indicate if the connection needs to be logged in prior to issuing the
 * command.  Disabling the login check will improve performance when issuing many sequential
 * commands.
 * @param error If not null, this will allocate and return the string error message from the
 * console.
 *
 * @return 0 if the command was successfully executed by the switch or an error code.
 */
int mgmt_switch_execute_config_command (const char *command, int login, char **error)
{
	int status;
	char response[512];

	if (command == NULL) {
		return EINVAL;
	}

	if (!connection.connected) {
		return ENOTCONN;
	}

	status = mgmt_switch_send_command (command, login);
	if (status != 0) {
		return (status < 0) ? 0 : status;
	}

	// First read back the echoed command, which may not exactly match the sent command.
	status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo, NEWLINE);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	// Then get the response line.
	status = mgmt_switch_read_data (response, sizeof (response), 0, connection.echo,
		NEWLINE_OR_PROMPT);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	return mgmt_switch_check_command_result (response, status, error);
}

/**
 * Apply all lines from a specified switch configuration file.  The process will stop at the first
 * error.
 *
 * @param path The path to the configuration file to apply.
 * @param line If not null, this will return with the last line number that was sent to the switch.
 * @param error If not null, this will allocate and return the string error message from the
 * console for the line that failed.
 *
 * @return 0 if all configuration parameters completed successfully or an error code.
 */
int mgmt_switch_apply_config_file (const char *path, int *line, char **error)
{
	FILE *config;
	int status;
	char command[512];
	int num = 0;

	config = fopen (path, "r");
	if (config == NULL) {
		return errno;
	}

	status = mgmt_switch_goto_root_prompt ();
	if (status != 0) {
		goto config_exit;
	}

	while ((status == 0) && (fgets (command, sizeof (command), config) != NULL)) {
		status = mgmt_switch_execute_config_command (command, 0, error);
		num++;
	}

	if (line != NULL) {
		*line = num;
	}

config_exit:
	fclose (config);
	return status;
}

/**
 * Clear the startup configuration for the management switch.  This change will not be applied until
 * the switch has been rebooted.
 *
 * @param backup Flag indicating if a backup of the startup configuration should be kept prior to
 * deleting it.
 *
 * @return 0 if the configuration was cleared or an error code.
 */
int mgmt_switch_clear_startup_config (int backup)
{
	int status;
	char line[512];

	status = mgmt_switch_console_login ();
	if (status != 0) {
		return status;
	}

	if (backup) {
		status = mgmt_switch_backup_startup_config ();
		if (status != 0) {
			return status;
		}
	}

	status = mgmt_switch_send_data ("no boot config\nY");
	if (status < 0) {
		return -status;
	}

	// Wait for the next prompt to indicate the operation has completed.
	mgmt_switch_read_data (line, sizeof (line), 0, connection.echo, PROMPT);

	return 0;
}

/**
 * Save a configuration as the startup configuration for the management switch.
 *
 * @param restore Flag indicating that the startup configuration should be restored from the last
 * backup.  If this is false, the running configuration will be saved as the startup configuration.
 *
 * @return 0 if the configuration was saved or an error code.
 */
int mgmt_switch_save_startup_config (int restore)
{
	int status;
	char result[512];

	status = mgmt_switch_console_login ();
	if (status != 0) {
		return status;
	}

	if (restore) {
		status = mgmt_switch_send_data ("boot config flash://ocs-config.bak\n");
	}
	else {
		status = mgmt_switch_send_data ("boot config running-config\n");
	}
	if (status < 0) {
		return -status;
	}

	// Read back the echoed command.
	status = mgmt_switch_read_data (result, sizeof (result), 0, connection.echo, NEWLINE);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	// Get the next line to figure out what to do.
	status = mgmt_switch_read_data (result, sizeof (result), 0, connection.echo, "?\n");
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	if (strstr (result, "The source file does not exist") != NULL) {
		return ENOENT;
	}
	else {
		status = mgmt_switch_send_data ("Y");
		if (status < 0) {
			return -status;
		}
	}

	if (restore) {
		do {
			status = mgmt_switch_read_data (result, sizeof (result), 0, connection.echo, "]#");
			if (status <= 0) {
				return (status < 0) ? -status : ENOLINK;
			}
		} while ((status > 0) && (result[status - 1] != '#'));
	}
	else {
		status = mgmt_switch_read_data (result, sizeof (result), 0, connection.echo, "#");
		if ((status > 0) && (strstr (result, "Copy succeeded") == NULL)) {
			return EBADE;
		}
	}

	if (status == 0) {
		status = -ENOLINK;
	}
	return (status > 0) ? 0: -status;
}

/**
 * Set the inactive firmware image stored on the management switch to be used as the active image
 * on the next reboot.
 *
 * @return 0 if the inactive was switch to be active or an error code.
 */
int mgmt_switch_activate_inactive_image ()
{
	int status;

	status = mgmt_switch_goto_root_prompt ();
	if (status != 0) {
		return status;
	}

	return mgmt_switch_execute_echoed_command ("boot system inactive-image", 0, 1);
}

/**
 * Upload new firmware to the management switch that will be loaded as the active image on the next
 * reboot.
 *
 * @param server The IP address of the TFTP server that is hosting the new firmware image.
 * @param path The path of the firmware image on the TFTP server.
 *
 * @return 0 if the firmware was successfully uploaded or an error code.
 */
int mgmt_switch_upload_firmware (const char *server, const char *path)
{
	int status;
	char command[512];

	if ((server == NULL) || (*server == '\0') || (path == NULL) || (*path == '\0')) {
		return EINVAL;
	}

	status = mgmt_switch_goto_root_prompt ();
	if (status != 0) {
		return status;
	}

	snprintf (command, sizeof (command), "boot system tftp://%s/%s\n", server, path);
	status = mgmt_switch_send_data (command);
	if (status < 0) {
		return -status;
	}

	status = mgmt_switch_read_data (command, sizeof (command), 0, connection.echo, NEWLINE);
	if (status <= 0) {
		return (status < 0) ? -status : ENOLINK;
	}

	do {
		status = mgmt_switch_read_data (command, sizeof (command), 0, connection.echo, "#]");
	} while ((status > 0) && (command[status - 1] != '#'));

	if (status == 0) {
		status = -ENOLINK;
	}

	if (status > 0) {
		if (strstr (command, "TFTP server unreachable") != NULL) {
			status = -EHOSTUNREACH;
		}
		else if (strstr (command, "Abort from tftp server") != NULL) {
			if (strstr (command, "file not found") != NULL) {
				status = -ENOENT;
			}
			else {
				status = -ECONNABORTED;
			}
		}
		else if (strstr (command, "Error occurred when writing file") != NULL) {
			status = -EREMOTE;
		}
		else if (strstr (command, "Can't open TFTP client") != NULL) {
			status = -EFAULT;
		}
	}
	return (status > 0) ? 0 : -status;
}

/**
 * Echo all console messages received from the management switch.  This will loop until there is a
 * read error.
 *
 * @return The error that caused the function to terminate.
 */
int mgmt_switch_dump_console ()
{
	int status;
	char line[512];

	if (!connection.connected) {
		return ENOTCONN;
	}

	do {
		status = mgmt_switch_read_data (line, sizeof (line), 1, 1, NEWLINE_OR_PROMPT);
	} while (status > 0);

	if (status == 0) {
		status = -ENOLINK;
	}
	return -status;
}

/**
 * Thread function to read data from the switch console and send it to stdout.
 */
static void* mgmt_switch_shell_read (void *unused)
{
	char data[50];
	int bytes;

	bytes = read (connection.dev, data, sizeof (data) - 1);
	while (bytes >= 0) {
		data[bytes] = '\0';
		printf ("%s", data);

		bytes = read (connection.dev, data, sizeof (data) - 1);
	}

	log_info ("%s: Exit (%d)", __func__, bytes);
	return NULL;
}

/**
 * Determine if the shell session was signaled to be terminated by the user.
 *
 * @param input The data input read from the user.
 * @param length The length of the data that was read.
 * @param catch_sigint Use Ctrl-C and Ctrl-D locally to terminate the session.
 *
 * @return 0 if the shell should remain active or 1 if it should terminate.
 */
static int mgmt_switch_shell_terminate (const char *input, int length, int catch_sigint)
{
	int i;
	for (i = 0; i < length; i++) {
		if (input[i] == 0x18) {
			return 1;
		}
		if (catch_sigint && ((input[i] == 0x03) || (input[i] == 0x04))) {
			return 1;
		}
	}

	return 0;
}

/**
 * Thread function to read data from stdin and send it to the switch console.
 *
 * @param int_action The action to take for Ctrl-C and Ctrl-D signals.
 */
static void* mgmt_switch_shell_write (void *int_action)
{
	char data[50];
	int bytes;
	int catch_sigint = (int) int_action;

	bytes = read (0, data, sizeof (data) - 1);
	while (bytes >= 0) {
		if (!mgmt_switch_shell_terminate (data, bytes, catch_sigint)) {
			bytes = mgmt_switch_write_data (data, bytes);

			if (bytes >= 0) {
				bytes = read (0, data, sizeof (data) - 1);
			}
		}
		else {
			bytes = -1;
			kill (getpid (), SIGINT);
		}
	}

	log_info ("%s: Exit (%d)", __func__, bytes);
	return NULL;
}

/**
 * Establish an interactive console with the management switch using stdin and stdout.  THis
 * function will not return until the interactive session has been interrupted.
 *
 * @param catch_sigint Flag indicating that Ctrl-C and Ctrl-D signal should be locally processed to
 * cause the interactive shell to close.
 *
 * @return 0 if console session was started and terminated normally or an error code.
 */
int mgmt_switch_interactive_console (int catch_sigint)
{
	pthread_t shell_in;
	pthread_t shell_out;
	struct termios attr;
	struct termios org;
	int status;

	if (tcgetattr (0, &org) != 0) {
		return errno;
	}

	attr = org;
	cfmakeraw (&attr);

	if (tcsetattr (0, TCSANOW, &attr) != 0) {
		return errno;
	}

	status = pthread_create (&shell_out, NULL, mgmt_switch_shell_read, NULL);
	if (status != 0) {
		log_out ("Failed to create shell read thread.");
		return status;
	}

	status = pthread_create (&shell_in, NULL, mgmt_switch_shell_write, (void*) catch_sigint);
	if (status != 0) {
		log_out ("Failed to create shell write thread.");
		return status;
	}

	pause ();
	tcsetattr (0, TCSANOW, &org);

	/*
	 * NOTE:  The threads spawned by this function are not guaranteed to be completely terminated
	 * upon returning (no pthread_join has been called).  It is assumed that the calling process
	 * is going to exit after returning from this function, which will cause the threads to be
	 * released.  If this ever changes, additions will be required to ensure the threads get
	 * properly stopped and released.
	 */
	return 0;
}
