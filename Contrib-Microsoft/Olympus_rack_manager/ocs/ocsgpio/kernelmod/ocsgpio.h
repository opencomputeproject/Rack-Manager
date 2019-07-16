// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#define APPNAME                         "ocs-gpio"
#define OCSPORTONTIME_FILE 				"/tmp/ocsgpio_ontime_%d.log"

#define MAX_PORT_GPIOCOUNT          	48
#define MAX_RELAY_GPIOCOUNT         	4
#define MAX_DBGLED_GPIOCOUNT        	4
#define MAX_BOARDID_GPIOCOUNT       	3
#define MAX_PCBREVID_GPIOCOUNT      	3
#define MAX_ROWTHSTAT_GPIOCOUNT      	4

#define BLADE_STARTTIME_DELAY_SEC		40

#define PARAM_ALL                       0

#define PORT_ONTIME_UPDATE_ID			2

typedef enum { 
    FALSE                               = 0,
    TRUE                                = 1
} bool_t;

enum {
    IDTYPE_MODEID                       = 0,
    IDTYPE_PCBREVID                     = 1,
    IDTYPE_MAX
} BoardIDType;

enum {
    THSTATTYPE_ALL                    	= 0,
	THSTATTYPE_ROWTH                    = 1,
    THSTATTYPE_DCTH                     = 2,
    THSTATTYPE_ROWPRESENT               = 3,
    THSTATTYPE_DCPRESENT                = 4,
    THSTATTYPE_MAX
} RowThStatType;


#define RMMODE_PIB						0
#define RMMODE_ROWMGR					1
#define RMMODE_MTETFB					2

#define PCBREVID_EV                     0
#define PCBREVID_DV                     1
#define PCBREVID_PV                     2

#define P12VAGOOD						1
#define P12VBGOOD						2

#define VERSION_MAKEWORD(maj, min, rev, bld) ( ((maj & 0xFF) << 24) | \
                                                ((min & 0x0F) << 20) | \
                                                ((rev & 0x0F) << 16) | \
                                                (bld & 0xFFFF) )

#define VERSION_GET_MAJOR(ver) 			( (ver >> 24) & 0xFF )
#define VERSION_GET_MINOR(ver) 			( (ver >> 20) & 0x0F )
#define VERSION_GET_REVISION(ver) 		( (ver >> 16) & 0x0F )
#define VERSION_GET_BUILD(ver) 			( ver & 0xFFFF )

