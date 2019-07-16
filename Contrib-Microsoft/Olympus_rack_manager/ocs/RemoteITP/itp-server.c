// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>
#include <poll.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "itp-server.h"
#include "ocslog.h"
#include "blade-id-ip-map.h"


/**
 * The length of the receive buffers.
 */
#define BUFFER_LENGTH	1024

/**
 * Remote ITP server instance.
 */
struct itp_server {
	int id;	/**< The ITP server instance ID. */
	int socket;	/**< The socket the server is using to listen for connections. */
	struct sockaddr_in address;	/**< The socket address for the server. */
	pthread_t thread;	/**< Thread to run when listening for connections. */
	pthread_mutex_t lock;	/**< Synchronization lock for the server. */
	int listening;	/**< Flag indicating if the server was started. */
	int run;	/**< Thread control flag. */
	int dal;	/**< The DAL client socket connected to the server. */
	struct sockaddr_in dal_addr;	/**< The address of the connected DAL client. */
	uint8_t dal_buffer[BUFFER_LENGTH]; /**< The buffer for receiving external messages. */
	int jtag;	/**< The socket to the internal JTAG server. */
	struct sockaddr_in jtag_addr;	/**< The address of the internal JTAG server. */
	char jtag_ip[INET_ADDRSTRLEN];	/**< The IP address string for the JTAG server. */
	uint8_t jtag_buffer[BUFFER_LENGTH];	/**< The buffer for receiving internal messages. */
};


/**
 * Log information for a change in the DAL client connected state.
 *
 * @param server The server to log the connection change for.
 * @param connected Flag indicating if the connection is up or down.
 */
static void itp_server_log_dal_connection (struct itp_server *server, int connected)
{
	char dal_addr[INET_ADDRSTRLEN];

	inet_ntop (AF_INET, &server->dal_addr.sin_addr, dal_addr, sizeof (dal_addr));
	log_info ("DAL client %s server %d from %s:%d.",
		(connected) ? "connected to" : "disconnected from", server->id, dal_addr,
		ntohs (server->dal_addr.sin_port));
}

/**
 * Log information for a change in the JTAG connected state.
 *
 * @param server The server to log the connection change for.
 * @param connected Flag indicating if the connection is up or down.
 */
static void itp_server_log_jtag_connection (struct itp_server *server, int connected)
{
	char jtag_addr[INET_ADDRSTRLEN];

	inet_ntop (AF_INET, &server->jtag_addr.sin_addr, jtag_addr, sizeof (jtag_addr));
	log_info ("ITP server %d %s JTAG server at %s:%d.", server->id,
		(connected) ? "connected to" : "disconnected from", jtag_addr,
		ntohs (server->jtag_addr.sin_port));
}

/**
 * Send an IPMI command to the target blade to start or stop the JTAG server.
 *
 * @param server The ITP server instance paired with the debug target system.
 * @param start Flag indicating if the JTAG server should be started or stopped.
 *
 * @return 0 if the command was successful or an error code.
 */
static int itp_server_send_ipmi_command (struct itp_server *server, int start)
{
	char user[32];
	char passwd[32];
	int status;
	char command[256];
	char result[256];
	FILE *shell;

	status = get_server_command_access (user, passwd);
	if (status != 0) {
		log_err (status, "Failed to IPMI login credentials for ITP %d.", server->id);
		return status;
	}

	if (snprintf (command, sizeof (command),
		"/usr/bin/ipmitool -I lan -H %s -U %s -P %s ocsoem service cpudbg %s 2>&1", server->jtag_ip,
		user, passwd, (start) ? "start" : "stop") >= sizeof (command))
	{
		status = ENAMETOOLONG;
		log_err (status, "Failed to build IPMI command string for ITP %d.", server->id);
		return status;
	}

	shell = popen (command, "r");
	if (shell == NULL) {
		status = errno;
		log_err (status, "Failed to start IPMI command for ITP %d.", server->id);
		return status;
	}

	while (fgets (result, sizeof (result), shell) != NULL) {
		log_info (result);
	}

	status = pclose (shell);
	if (status != 0) {
		if (status == -1) {
			status = errno;
		}
		log_err (status, "Failed to start JTAG server for ITP %d.", server->id);
		return status;
	}

	return 0;
}

/**
 * Start the JTAG server on the debug target system.
 *
 * @param server The ITP server instance paired with the debug target system.
 *
 * @return 0 if the JTAG server was successfully started or an error code.
 */
static int itp_server_start_jtag_server (struct itp_server *server)
{
	int status = itp_server_send_ipmi_command (server, 1);
	if (status == 0) {
		usleep (200000);
	}

	return status;
}

/**
 * Stop the JTAG server on the debug target system.
 *
 * @param server The ITP server instance paired with the debug target system.
 *
 * @return 0 if the JTAG server was successfully stopped or an error code.
 */
static int itp_server_stop_jtag_server (struct itp_server *server)
{
	return itp_server_send_ipmi_command (server, 0);
}

/**
 * Connect to the JTAG server running on the debug target.
 *
 * @param server The ITP server instance to connect to the JTAG target.
 *
 * @return 0 if connection to the JTAG server was successful or an error code.
 */
static int itp_server_connect_to_jtag (struct itp_server *server)
{
	int status;

	status = itp_server_start_jtag_server (server);
	if (status != 0) {
		return status;
	}

	pthread_mutex_lock (&server->lock);
	server->jtag = socket (PF_INET, SOCK_STREAM, 0);
	if (server->jtag < 0) {
		status = errno;
		log_fnc_err (status, "Failed to get socket for JTAG connection for ITP %d.", server->id);
		pthread_mutex_unlock (&server->lock);
		return status;
	}
	pthread_mutex_unlock (&server->lock);

	status = connect (server->jtag, (struct sockaddr*) &server->jtag_addr,
		sizeof (server->jtag_addr));
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to connect to debug JTAG server for ITP %d.", server->id);
		goto jtag_error;
	}

	itp_server_log_jtag_connection (server, 1);
	return 0;

jtag_error:
	pthread_mutex_lock (&server->lock);
	close (server->jtag);
	server->jtag = -1;
	pthread_mutex_unlock (&server->lock);
	return status;
}

/**
 * Close the connection to the JTAG server running the debug target.
 *
 * @param server The ITP server instance to disconnect from the JTAG target.
 *
 * @return 0 if the connection to the JTAG was disconnected or an error code.
 */
static int itp_server_close_jtag_connection (struct itp_server *server)
{
	int status = 0;

	itp_server_stop_jtag_server (server);

	pthread_mutex_lock (&server->lock);
	if (server->jtag > 0) {
		if (close (server->jtag) == 0) {
			server->jtag = -1;
			itp_server_log_jtag_connection (server, 0);
		}
		else {
			status = errno;
			log_fnc_err (status, "Failed to close JTAG server connection for ITP %d.", server->id);
		}
	}
	pthread_mutex_unlock (&server->lock);

	return status;
}

/**
 * Close the connection to the DAL client.
 *
 * @param server The ITP server instance to disconnect from the DAL.
 *
 * @return 0 if the connection to the DAL was disconnected or an error code.
 */
static int itp_server_close_dal_connection (struct itp_server *server)
{
	int status = 0;

	pthread_mutex_lock (&server->lock);
	if (server->dal > 0) {
		if (close (server->dal) == 0) {
			server->dal = -1;
			itp_server_log_dal_connection (server, 0);
		}
		else {
			status = errno;
			log_fnc_err (status, "Failed to close DAL client connection for ITP %d.", server->id);
		}
	}
	pthread_mutex_unlock (&server->lock);

	return status;
}

/**
 * Read data from one socket and forward it to another.
 *
 * @param from The socket to read from.
 * @param to The socket to send to.
 * @param buffer The buffer to use for reading.
 * @param length The length of the buffer.
 *
 * @return The number of bytes read from the source socket and were forwarded or a negative error
 * code.
 */
static int itp_server_forward_data (int from, int to, uint8_t *buffer, size_t length)
{
	int bytes = read (from, buffer, length);
	int remaining = bytes;
	while (remaining > 0) {
		int written = write (to, buffer, bytes);
		if (written < 0) {
			remaining = -1;
			bytes = -1;
		}
		else {
			remaining -= written;
		}
	}

	if (bytes < 0) {
		bytes = -errno;
	}
	return bytes;
}

/**
 * Forward all received data from the ITP client to the internal JTAG server.
 *
 * @param server The server that has a client actively connected.
 */
static void itp_server_forward_client (struct itp_server *server)
{
	struct pollfd read_check[2];
	int conn_active = 1;

	memset (read_check, 0, sizeof (read_check));
	read_check[0].fd = server->dal;
	read_check[0].events = POLLIN | POLLPRI;
	read_check[1].fd = server->jtag;
	read_check[1].events = read_check[0].events;

	while (conn_active && server->run) {
		int status = poll (read_check, 2, -1);
		if (status > 0) {
			if ((read_check[0].revents & (POLLIN | POLLPRI)) != 0) {
				status = itp_server_forward_data (server->dal, server->jtag, server->dal_buffer,
					BUFFER_LENGTH);
			}

			if ((status > 0) && (read_check[0].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0) {
				status = 0;
			}
			if (status <= 0) {
				conn_active = 0;
				if ((status == 0) || (status == -ECONNRESET)) {
					log_info ("DAL client %d closed connection.", server->id);
				}
				else {
					log_fnc_err (-status, "Failed to forward data to JTAG server %d.",
						server->id);
				}
			}

			if (conn_active) {
				if ((read_check[1].revents & (POLLIN | POLLPRI)) != 0) {
					status = itp_server_forward_data (server->jtag, server->dal, server->jtag_buffer,
						BUFFER_LENGTH);
				}

				if ((status > 0) && (read_check[1].revents & (POLLERR | POLLHUP | POLLNVAL)) != 0) {
					status = 0;
				}
				if (status <= 0) {
					conn_active = 0;
					if ((status == 0) || (status == -ECONNRESET)) {
						log_info ("JTAG client %d closed connection.", server->id);
					}
					else {
						log_fnc_err (-status, "Failed to forward data to DAL client %d.",
							server->id);
					}
				}
			}
		}
		else {
			log_fnc_err (errno, "Poll failure.");
		}
	}
}

/**
 * Listener thread for servers.
 *
 * @param arg The server instance being run.
 */
static void* itp_server_listen_thread (void *arg)
{
	struct itp_server *server = arg;

	pthread_mutex_lock (&server->lock);
	while (server->run) {
		socklen_t addr_len = sizeof (server->dal_addr);
		int dal;

		pthread_mutex_unlock (&server->lock);
		dal = accept (server->socket, (struct sockaddr*) &server->dal_addr, &addr_len);

		pthread_mutex_lock (&server->lock);
		if (server->run) {
			if (dal >= 0) {
				server->dal = dal;
				pthread_mutex_unlock (&server->lock);

				itp_server_log_dal_connection (server, 1);
				if (itp_server_connect_to_jtag (server) == 0) {
					itp_server_forward_client (server);
					itp_server_close_jtag_connection (server);
				}

				itp_server_close_dal_connection (server);
				pthread_mutex_lock (&server->lock);
			}
			else {
				log_fnc_err (errno, "Failed to accept client connection for ITP %d.", server->id);
			}
		}
		else if (dal >= 0) {
			close (dal);
		}
	}
	pthread_mutex_unlock (&server->lock);

	return NULL;
}

/**
 * Create a new remote ITP server.  The new server will not yet be listening for connections.
 *
 * @param id An identifier for this ITP server instance.
 * @param port The port the server should be listening on.
 * @param jtag_ip The IP address of the JTAG server to communicate with.
 * @param jtag_port The port of the JTAG server.
 * @param server A pointer for the new server instance.  This is only changed upon successful
 * return.
 *
 * @return 0 if the server was initialized or an error code.
 */
int itp_server_initialize (int id, uint16_t port, const char *jtag_ip, uint16_t jtag_port,
	struct itp_server **server)
{
	struct itp_server *itp;
	int status;

	if ((port == 0) || (jtag_port == 0)) {
		log_fnc_err (EINVAL, "Invalid port number specified: itp=%d, jtag=%d.", port, jtag_port);
		return EINVAL;
	}

	itp = malloc (sizeof (struct itp_server));
	if (itp == NULL) {
		log_fnc_err (ENOMEM, "Failed to allocate server instance for port %d.", port);
		return ENOMEM;
	}

	memset (itp, 0, sizeof (struct itp_server));
	itp->id = id;
	itp->socket = -1;
	itp->dal = -1;
	itp->jtag = -1;

	status = pthread_mutex_init (&itp->lock, NULL);
	if (status != 0) {
		log_fnc_err (status, "Failed to initialize server mutex.");
		goto itp_error;
	}

	itp->jtag_addr.sin_family = AF_INET;
	itp->jtag_addr.sin_port = htons (jtag_port);
	if (inet_pton (AF_INET, jtag_ip, &itp->jtag_addr.sin_addr) != 1) {
		log_fnc_err (EINVAL, "Invalid JTAG server IP address specified: %s.", jtag_ip);
		status = EINVAL;
		goto itp_error;
	}
	strcpy (itp->jtag_ip, jtag_ip);

	itp->socket = socket (PF_INET, SOCK_STREAM, 0);
	if (itp->socket == -1) {
		status = errno;
		log_fnc_err (status, "Failed to get server socket for port %d.", port);
		goto itp_error;
	}

	itp->address.sin_family = AF_INET;
	itp->address.sin_addr.s_addr = htonl (INADDR_ANY);
	itp->address.sin_port = htons (port);

	if (bind (itp->socket, (struct sockaddr*) &itp->address, sizeof (itp->address)) != 0) {
		status = errno;
		log_fnc_err (status, "Failed to bind to port %d.", port);
		goto itp_error;
	}

	log_info ("Initialized ITP %d on port %d for JTAG server %s:%d.", itp->id, port,
		itp->jtag_ip, jtag_port);
	*server = itp;
	return 0;

itp_error:
	close (itp->socket);
	free (itp);
	return status;
}


/**
 * Start listening for connections to a remote ITP server.
 *
 * @param server The server to start listening.
 *
 * @return 0 if the server is listening for connections or an error code.
 */
int itp_server_listen (struct itp_server *server)
{
	int status;

	if (server == NULL) {
		log_fnc_err (EINVAL, "No server specified to start.");
		return EINVAL;
	}

	status = listen (server->socket, 1);
	if (status != 0) {
		status = errno;
		log_fnc_err (status, "Failed to set socket for listening.");
		return status;
	}

	server->run = 1;
	status = pthread_create (&server->thread, NULL, itp_server_listen_thread, server);
	if (status != 0) {
		log_fnc_err (status, "Failed to start listening thread.");
		server->run = 0;
		return status;
	}

	server->listening = 1;
	return 0;
}


/**
 * Stop running a remote ITP server and release the resources.
 *
 * @param server The server to stop.
 *
 * @return 0 if the server was stopped or an error code.
 */
int itp_server_release (struct itp_server *server)
{
	if (server != NULL) {
		if (server->listening) {
			pthread_mutex_lock (&server->lock);
			server->run = 0;
			shutdown (server->socket, SHUT_RDWR);
			shutdown (server->dal, SHUT_RDWR);
			shutdown (server->jtag, SHUT_RDWR);
			pthread_mutex_unlock (&server->lock);

			pthread_join (server->thread, NULL);
		}

		close (server->socket);
		free (server);
	}

	return 0;
}
