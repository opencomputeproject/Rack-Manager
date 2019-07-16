// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

/* runtime watch dog location /usr/bin */
/* lock file is used for record pid value to make sure only one instance running ever*/
#define LOCK_FILE	"/usr/bin/watchdog.lock"
#define WATCH_FILE  "/dev/watchdog"
#define SLEEP_TIME 30    /* write to file sleep time */
#define WATCHDOG_TIMER 60 /* watch dog time out in seconds */

