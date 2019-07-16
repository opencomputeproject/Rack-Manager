// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <syslog.h>
#include <errno.h>
#include <string.h>
#include "ocslog-shm.h"
#include "ocslock.h"
#include "ocsfile.h"

int main()
{
	int ocslock_id, ret;
	int fail = 0;

	for(ocslock_id=0; ocslock_id<NUM_OCSLOCKS; ocslock_id++) {
		ret = ocslock_init(ocslock_id);
		if(ret!=0) {
			syslog(LOG_ERR, "Ocs-Init for ocslockid %d failed with error code %d\n", ocslock_id, ret);
			fail = 1;
		}
	}

	ret = shm_create ();
	if(ret!=0) {
		syslog(LOG_ERR, "Ocs-Init failed to create log shared memory: %d\n", ret);
		fail = 1;
	}

	ret = ocs_file_validate_all ();
	if (ret != 0) {
		syslog (LOG_ERR, "Ocs-Init failed to verify all system files: %d\n", ret);
		fail = 1;
	}

	ret = daemon (0, 0);
	if (ret == 0) {
		/* Daemon loop to re-validate files on-demand after they have been written. */
		while (1) {
			int retry = 0;

			ocs_lock (OCSFILE_WRITE);
			if (ocs_condwait (OCSFILE_WRITE) == 0) {
				ocs_unlock (OCSFILE_WRITE);
			}

			while ((ocs_file_validate_all () != 0) && (retry < 6)) {
				syslog (LOG_ERR, "Ocs-Init validation failed, retry (%d).\n", retry);
				sleep (10);
				retry++;
			}
		}
	}
	else {
		syslog (LOG_ERR, "Ocs-Init failed to start file integrity daemon: %s\n", strerror (errno));
		fail = 1;
	}

	return fail;
}
