// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

/* Signals used by the KM and usr handler */
#define GPIOMON_KERNEL_TO_USR_RTS		(SIGRTMIN+1)
#define GPIOMON_ENDMONITOR_RTS			(SIGRTMIN+2)

#define GPIOMON_SDRCACHE_FILE			"/tmp/sdrcache/Blade%d"
#define GPIOMON_MODULE_FILENAME			"gpio-mon.ko"
#define GPIOMON_MODULE_NAME				"gpio-mon"

#define PORTID_SHIFT					0
#define PORTID_MASK						0xFF
#define PORTSTATE_SHIFT					8
#define PORTSTATE_MASK					0x100

/* Externed functions */
int gpiomon_wait( char *modfilename );
