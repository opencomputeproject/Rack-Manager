// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


/* Version info - these defined will be used by build scripts as well */
#define SOLIB_VERSION_MAJOR     	1
#define SOLIB_VERSION_MINOR     	9
#define SOLIB_VERSION_REVISION  	0
#define SOLIB_VERSION_BUILD     	0

/* Shared lib functions */
int ocs_fwup_startupgrade(char *pkg_path);
int ocs_fwup_startrecovery(int recovery_type);
int ocs_fwup_getstatus(int *status);
int ocs_fwup_getlist(char *list);
int ocs_fwup_libgetversion(u_int32_t *ver);