// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/signal.h>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <syslog.h>

#include "ocslock.h"
#include "ocslog-shm.h"


struct __attribute__((packed)) shm_queue {
	size_t read_pos;
	size_t write_pos;
	size_t wrap_pos;
} *log_queue = NULL;

char *log_start;

/* Lock file location in sharedmem */
#define OCSLOG_AREA         	 "/ocslog_area"

#define LOG_SHM_TOTAL_SIZE		(2048*1024)
#define	LOG_SHM_HEADER_SIZE		(sizeof (struct shm_queue))
#define	LOG_SHM_QUEUE_SIZE		LOG_SHM_TOTAL_SIZE - LOG_SHM_HEADER_SIZE

/* 
 * Initialize shm log 
 * Memory map the already created shared memory object to virtual memory
 * Done once per process
 */
int shm_init () {
	/* check if already initialized */
	if (log_queue != NULL) {
		syslog (LOG_NOTICE, "OCS shm_init: Already initialized\n");
		return SUCCESS;
	}
	else
		syslog (LOG_INFO, "OCS shm_init: Initializing for Pid(%d).\n", getpid ());
	    
	/* Open a shared memory object to store log info */
    int fd = shm_open (OCSLOG_AREA, O_RDWR | O_APPEND, S_IRWXU | S_IRWXG);
    if (fd < 0) {
        syslog (LOG_ERR, "OCSLOGSHM: Shm open failed\n");
        return FAILURE;
    }
        
    log_queue = mmap (NULL, LOG_SHM_TOTAL_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (log_queue == MAP_FAILED) {
        syslog (LOG_ERR, "OCSLOGSHM: Shm MMAP failed\n");
        return FAILURE;
    }
    
    log_start = (char*) log_queue + LOG_SHM_HEADER_SIZE;

	return SUCCESS;	
}

/*
 * Create shared memory object
 * Done once per system (typically during start/boot)  
 */
int shm_create () {
	/* Create/open a shared memory object to store log info */
	mode_t org_mask = umask (0);
    int fd = shm_open (OCSLOG_AREA, O_CREAT | O_RDWR | O_APPEND | O_TRUNC | O_EXCL,
    	(S_IRWXU | S_IRWXG | S_IRWXO));
    umask (org_mask);
    if (fd < 0) {
        syslog (LOG_ERR, "OCSLOGSHM: Shm open failed\n");
        return FAILURE;
    }
    
    if (ftruncate (fd, LOG_SHM_TOTAL_SIZE) != 0) {
        syslog (LOG_ERR, "OCSLOGSHM: Shm truncate failed\n");
        return FAILURE;
    }
    
    log_queue = mmap (NULL, LOG_SHM_TOTAL_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (log_queue  == MAP_FAILED) {
        syslog(LOG_ERR, "OCSLOGSHM: Shm MMAP failed\n");
        return FAILURE;
    }
	
    log_start = (char*) log_queue + LOG_SHM_HEADER_SIZE;
	log_queue->read_pos = 0;
	log_queue->write_pos = 0;
	log_queue->wrap_pos = LOG_SHM_QUEUE_SIZE;

	return SUCCESS;	
}

/* Clean up shmlog structures */
void shm_close () {
	shm_unlink (OCSLOG_AREA);
}

/* 
 * Enqueue shm entry at the head of the shared memory message queue 
 * Return success when enqueue is complete
 */
int shm_enqueue (const char *log) {
	int retval;
	int length;
	int wrap;
	size_t next_write;

	if (log_queue == NULL) {
		syslog (LOG_INFO, "Enqueue shmlog failed - init should have happened before logging\n");
		return FAILURE;
	}
	
	/* system-wide mutual exclusion lock */
	retval = ocs_lock (OCSLOG_SHM);
	if (retval != SUCCESS) {
		syslog (LOG_WARNING, "ocs_lock failed with error:%d\n", retval);
		return FAILURE;
	}

	/* If full immediately return failure */
	next_write = log_queue->write_pos + 1;
	if (next_write >= LOG_SHM_QUEUE_SIZE) {
		next_write = 0;
	}
	if (next_write == log_queue->read_pos) {
		syslog(LOG_WARNING, "Log queue in full.. ocslog-shm enqueue failed\n");
		ocs_unlock(OCSLOG_SHM);
		return FAILURE;	
	}

	length = strlen (log) + 1;
	if ((log_queue->write_pos + length) > LOG_SHM_QUEUE_SIZE) {
		next_write = 0;
		wrap = 1;
	}
	else {
		next_write = log_queue->write_pos;
		wrap = 0;
	}

	if ((next_write < log_queue->read_pos) && ((next_write + length) >= log_queue->read_pos)) {
		syslog(LOG_WARNING, "No room in queue for message.. ocslog-shm enqueue failed\n");
		ocs_unlock (OCSLOG_SHM);
		return FAILURE;
	}

	if (wrap) {
		if (log_queue->read_pos != log_queue->write_pos) {
			log_queue->wrap_pos = log_queue->write_pos;
		}
		else {
			log_queue->wrap_pos = LOG_SHM_QUEUE_SIZE;
			log_queue->read_pos = 0;
		}
		log_queue->write_pos = 0;
	}

	strcpy (log_start + log_queue->write_pos, log);

	/* Advance the write pointer and notify the read thread.*/
	log_queue->write_pos += length;
	ocs_condsignal (OCSLOG_SHM);

	ocs_unlock (OCSLOG_SHM);
	
	return SUCCESS;
}

/* 
 * Dequeue message string at the tail from shared memory
 * Return SUCCESS when log_ptr is updated with the dequeued message pointer
 */
int shm_dequeue (char **log_ptr) {
	char *next;

	if (log_queue == NULL) {
		syslog(LOG_NOTICE, "Dequeue shmlog failed  - init should happen before logging\n");
		return FAILURE;
	}
	
	/* Check for empty - Wait for the write thread */
	ocs_lock(OCSLOG_SHM);
	while (log_queue->read_pos == log_queue->write_pos) {
		ocs_condwait(OCSLOG_SHM);
	}

	next = log_start + log_queue->read_pos;
	*log_ptr = strdup (next);
	
	/* Advance the read pointer */
	log_queue->read_pos += strlen (next) + 1;
	if (log_queue->read_pos >= log_queue->wrap_pos) {
		log_queue->read_pos = 0;
		log_queue->wrap_pos = LOG_SHM_QUEUE_SIZE;
		if (log_queue->write_pos >= LOG_SHM_QUEUE_SIZE) {
			log_queue->write_pos = 0;
		}
	}

	ocs_unlock(OCSLOG_SHM);
	return (*log_ptr != NULL) ? SUCCESS : FAILURE;
}

