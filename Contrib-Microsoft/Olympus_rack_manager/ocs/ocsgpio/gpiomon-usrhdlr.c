// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsgpio-common.h>
#include <gpiomon-usrhdlr.h>
#include <ocsgpioaccess.h>

#include <signal.h>

#define MAX_PORT_EVENTS					256	/* Keep it power of 2 */

/* Shared data struct between signal handler and the main thread */
struct _port_event_t
{
	volatile int head;
	volatile int tail;
	volatile bool_t endmonitor;
	volatile bool_t status[MAX_PORT_EVENTS];
} portevents;

/******************************************************************************
*   Function Name: gpiomon_processportevent
*   Purpose: Process queued in signals in main thread
*******************************************************************************/
static void gpiomon_processportevent(int portid, bool_t portstate)
{
	int retval;
	char pathname[sizeof(GPIOMON_SDRCACHE_FILE)+1];
	
	/* Data coming from IRQ handler does not include direction. Port presence is inverted logic */
	portstate = portstate?FALSE:TRUE;
	
	/* Put an entry into the log file */
	log_info("%s: Port %d attachment is now %s\n", APPNAME, portid, portstate?"present":"absent");
	
	/* Remove the associated sdr cache file */
	sprintf(pathname, GPIOMON_SDRCACHE_FILE, portid);
	retval = remove(pathname);
	LOG_TRACE("%s: Removing file %s, rc %d\n", APPNAME, pathname, retval);

	if (portstate)
		ocs_port_control(portid, PORT_ONTIME_UPDATE_ID);
}

/******************************************************************************
*   Function Name: gpiomon_usrhandler
*   Purpose: Handle realtime signal from KM
*******************************************************************************/
static void gpiomon_sighdlr( int signum, siginfo_t *info, void *arg __attribute__ ((unused)) )
{
	LOG_TRACE("%s: Sig %d, data %d\n", APPNAME, signum, info->si_int );
	
	if (signum == GPIOMON_KERNEL_TO_USR_RTS) {
		portevents.status[portevents.head] = info->si_int;
		
		portevents.head = (portevents.head + 1) & (MAX_PORT_EVENTS - 1);
		/* Prevent overflow */
		if (portevents.head == portevents.tail) {
			LOG_ERR(errno, "%s: Event queue full, dropping port event\n", APPNAME);
			portevents.head = (portevents.head - 1) & (MAX_PORT_EVENTS - 1);				
		}
	}
	else if (signum == GPIOMON_ENDMONITOR_RTS) {
		portevents.endmonitor = TRUE;
	}
}

/******************************************************************************
*   Function Name: gpiomon_procsignals
*   Purpose: Process queued in signals in main thread
*******************************************************************************/
static void gpiomon_procsignals(void)
{
	int portid;
	bool_t portstate;

	while (portevents.tail != portevents.head) {
		portid = (portevents.status[portevents.tail] >> PORTID_SHIFT) & PORTID_MASK;
		portstate = (bool_t)(portevents.status[portevents.tail] & PORTSTATE_MASK);
		if (portid > 0 && portid <= 48) {
			/* Call the utility function to work on the event */
			gpiomon_processportevent(portid, portstate);
			LOG_TRACE("%s: Event %d head %d | Port %d state %s\n", APPNAME, 
							portevents.tail, portevents.head, portid, portstate?"On":"Off");
		}
		portevents.tail = (portevents.tail + 1) & (MAX_PORT_EVENTS - 1);
	}
	return;
}

/******************************************************************************
*   Function Name: gpiomon_end
*   Purpose: Unloads gpio-mon kernel module
*******************************************************************************/
static int gpiomon_end( const char *modname )
{
	int retval;
	errno = 0;
	retval = delete_module(modname, O_NONBLOCK | O_TRUNC);
	LOG_TRACE("%s: Unload module status %d\n", APPNAME, errno);
	return ( retval?FAILED:SUCCESS );
}

/******************************************************************************
*   Function Name: gpiomon_start
*   Purpose: Load and start the gpio-mon kernel module
*******************************************************************************/
static int gpiomon_start( char *modname, int sigrtnum )
{
	int retval = SUCCESS;
	
	FILE *file;
	char *module_image;
	char param_values[] = "usrpid=99999 sigid=999";
	unsigned long fileLen;
	
	errno = 0;

	file = fopen(modname, "rb");
	if (!file) {
		LOG_ERR(errno, "%s: Unable to open module file %s\n", APPNAME, modname);
		return FAILED;
	}
	
	/* Get file length */
	fseek(file, 0, SEEK_END);
	fileLen=ftell(file);
	fseek(file, 0, SEEK_SET);

	/* Allocate memory */
	module_image=(char *)malloc(fileLen+1);
	if (!module_image) {
		LOG_ERR(errno, "%s: Unable to allocate memory for module load\n", APPNAME);
        fclose(file);
		return FAILED;
	}

	/* Read file contents into module_image */
	fread(module_image, fileLen, 1, file);
	fclose(file);

	/* Start the module with pid and sigid as parameters */
	sprintf(param_values, "usrpid=%d sigid=%d", getpid(), sigrtnum);
	retval = init_module( module_image, fileLen, (const char *)param_values);
	
	LOG_TRACE("%s: Loading module %s, size %d, params %s, rc=%d\n", APPNAME, modname, fileLen, param_values, retval);
	
	return retval;
}

/******************************************************************************
*   Function Name: gpiomon_wait
*   Purpose: Handler to catch the realtime signal from KM and perform task
*******************************************************************************/
int gpiomon_wait( char *modfilename )
{
	struct sigaction action;
	sigset_t in_sigset;
	sigset_t rt_sigset;
	sigset_t proc_sigset;

	int retval = SUCCESS;
	int first = FALSE;
	unsigned int state = 0;
	
	/* Initialize status sync struct */
	memset(&portevents, 0, sizeof(portevents));
	
	/* Setup signal handler */
	sigemptyset(&proc_sigset);
	
	sigemptyset(&rt_sigset);
	sigaddset(&rt_sigset, GPIOMON_KERNEL_TO_USR_RTS);
	sigaddset(&rt_sigset, GPIOMON_ENDMONITOR_RTS);
	
	sigfillset(&in_sigset);
	sigdelset(&in_sigset, GPIOMON_KERNEL_TO_USR_RTS);
	sigdelset(&in_sigset, GPIOMON_ENDMONITOR_RTS);

	/* Setup action handler for kernel mod signals */
	memset(&action, 0, sizeof(sigaction));
	sigemptyset(&action.sa_mask);
	action.sa_flags = SA_SIGINFO;
	action.sa_sigaction = gpiomon_sighdlr;
	retval = sigaction(GPIOMON_KERNEL_TO_USR_RTS, &action, NULL);
	retval = sigaction(GPIOMON_ENDMONITOR_RTS, &action, NULL);

	if (retval == SUCCESS) {
		retval = gpiomon_start( (modfilename)?modfilename:GPIOMON_MODULE_FILENAME, 
								GPIOMON_KERNEL_TO_USR_RTS );	
		if (retval == SUCCESS) {	
			while ( !portevents.endmonitor ) {
				if (!first) {
					LOG_INFO("monitoring for port state changes\n");
					first = TRUE;
				}
				/* Wait for RT signals if the event queue is empty */
				if (portevents.tail == portevents.head) {
					errno = 0;
					sigsuspend(&in_sigset);
					if (errno != EINTR)
						break;
				}
				/* Block the RT signals while processing on queued events */
				sigprocmask(SIG_BLOCK, &rt_sigset, &proc_sigset);
				gpiomon_procsignals();
				/* Restore process signal mask */
				sigprocmask(SIG_SETMASK, &proc_sigset, NULL);
			}
			gpiomon_end(GPIOMON_MODULE_NAME);
		}
	}
	
	if (retval != SUCCESS) {
		if (!first)
			LOG_INFO("failed to setup port monitor\n");
		LOG_ERR(errno, "%s: GPIO port monitoring not active, rc=%d \n", APPNAME, retval);
	}
	
    return retval;
}


