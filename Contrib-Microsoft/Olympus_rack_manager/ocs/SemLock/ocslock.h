// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#ifndef SEMLOCK_H_
#define SEMLOCK_H_

/* 
 * Enum with all ocslocks
 * NOTE: When adding new lock, 
 * (i) add it both the OCSLOCK_NAME enum list, 
 * (ii) increment NUM_OCSLOCKS and,
 * (iii) add to OCSLOCK_STRING
 * (iv) update python ocslock.py with new lock id
 */
typedef enum OCSLOCK_NAME
{ 
	PRU_CHARDEV = 0,
	PRU_SEQNUM = 1,	
	TELEMETRY_DAEMON = 2, 	
	OCSGPIOACCESS = 3,		
	I2C0_CHARDEV = 4,
	I2C1_CHARDEV = 5,
	PRU_PERSIST = 6,
	OCSLOG_SHM = 7,
	NVDIMM_DAEMON = 8,
	USR_ACCNT = 9,
	NET_CONFIG = 10,
	OCSFILE_WRITE = 11,
	NUM_OCSLOCKS = 12,
}ocslock_t;

static const char *OCSLOCK_STRING[NUM_OCSLOCKS] = {
    "ocsprudev", 
    "ocspruseqno", 
    "ocstelemetrydaemon", 
    "ocsgpioaccess", 
    "ocsi2c0dev", 
    "ocsi2c1dev", 
    "ocsprupersist",
    "ocslogshm",
    "ocsnvdimmdaemon",
	"ocsuseraccount",
	"ocsnetconfig",
	"ocsfilewrite",
};

/* Extern functions */
extern int ocs_lock(ocslock_t);
extern int ocs_unlock(ocslock_t);
extern int ocslock_init(ocslock_t);
extern void config_mutex_rec(ocslock_t, int(*rec_fn)());

extern int ocs_condwait(ocslock_t);
extern int ocs_condsignal(ocslock_t);


#endif // SEMLOCK_H_
