// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

/*
 * This program is to invoke the RunTimeWatchDog & restart the machine when the watchdog fails.
 * sleeps 30 seconds after each invocation of the RunTimeWatchDog
 */

#include "runtimewatchdog.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <linux/watchdog.h>
#include <signal.h>
#include <sys/ioctl.h>
#include "ocslog.h"

void signal_handler(sig)
int sig;
{
	switch(sig) {
	case SIGHUP:
		log_info("runtimewatchdog: hangup signal catched \n");
		break;
	case SIGTERM:
		log_info("runtimewatchdog: terminate signal catched \n");
		exit(SUCCESS);
		break;
	}
}

int Daemonize()
{
		pid_t pid = 0;
	    pid_t sid = 0;

	    int lfp;
	    char str[10];

	    /* Create child process or fork a new child process */
	    pid = fork();

	    /* Indication of fork() failure */
	    if (pid < 0) {

	    	log_fnc_err(FAILURE, "runtimewatchdog: Failed to fork a new child process \n");
	        exit(FAILURE); /* Return failure in exit status */
	    }

	    /* PARENT PROCESS. Need to kill it. */
	    if (pid > 0) {
	    	log_info("pid of child process %d \n", pid);
	    	exit(SUCCESS); /* terminate the parent process succesfully */
	    }

	    /* unmask the file mode */
	    umask(0);

	    sid = setsid(); /* set new session */
	    if(sid < 0) {
	    	log_fnc_err(FAILURE, "runtimewatchdog: Failed to set new session \n");
	    	exit(FAILURE); /*  Return failure */
	    }

	    /* Change the current working directory to /usr/bin. */
	    chdir("/usr/bin");

	    /*  Close stdin. stdout and stderr */
	    close(STDIN_FILENO);
	    close(STDOUT_FILENO);
	    close(STDERR_FILENO);

	    /* File locking method to run only single process */
		lfp=open(LOCK_FILE,O_RDWR|O_CREAT,0640);
		if (lfp<0) {
			log_fnc_err(FAILURE, "runtimewatchdog: Failed to open lock file\n");
		    exit(FAILURE); /* Return failure */
		}
		/* The first instance of the server locks the file so that other instances understand that
		 *  an instance is already running. */
		if (lockf(lfp,F_TLOCK,0)<0)
			exit(0); /* can not lock */
		/* first instance continues */
		sprintf(str,"%d\n",getpid());
		write(lfp,str,strlen(str)); /* record pid to lockfile */

		signal(SIGCHLD,SIG_IGN); /* ignore child */
		signal(SIGTSTP,SIG_IGN); /* ignore tty signals */
		signal(SIGTTOU,SIG_IGN);
		signal(SIGTTIN,SIG_IGN);
		signal(SIGHUP,signal_handler); /* catch hangup signal */
		signal(SIGTERM,signal_handler);  /* catch kill signal */

		return(0);
}

int main()
{
    int fp;
    int ret_val;

    log_init (INFO_LEVEL);

    if(Daemonize() != 0) {
    	log_fnc_err(FAILURE, "runtimewatchdog: Daemonize() failed \n");
    	exit(FAILURE);
    }

    /* Open /dev/watchdog file in write mode. */
    fp = open(WATCH_FILE, O_WRONLY);
	if (fp ==-1) {
		log_fnc_err(FAILURE, "runtimewatchdog: Failed to open the file \n");
		exit(FAILURE);
	}

	int data = WATCHDOG_TIMER;

	ret_val = ioctl(fp, WDIOC_SETTIMEOUT, &data);
	if (ret_val) {
		log_fnc_err(FAILURE, "Watchdog Timer : WDIOC_SETTIMEOUT failed\n");
	}
	else {
		log_info("\nNew timeout value is : %d seconds", data);
	}

	ret_val = ioctl(fp, WDIOC_GETTIMEOUT, &data);
	if (ret_val) {
		log_fnc_err(FAILURE,"Watchdog Timer : WDIOC_GETTIMEOUT failed");
	}
	else {
		log_info("\nCurrent timeout value is : %d seconds\n", data);
	}

	while (1)
	{
		if (1 != write(fp, "\0", 1)) {
				log_info("runtimewatchdog: Write to file failed \n");
				break;
		}
		else {
				/* log_info("Write succeeded\n"); */
				sleep(SLEEP_TIME); /* sleep time 30 seconds */
		}
	}
	if (0 != close (fp))
		log_fnc_err(FAILURE, "Close failed\n");
	else
		log_info("Close succeeded\n");

    return (0);
}

