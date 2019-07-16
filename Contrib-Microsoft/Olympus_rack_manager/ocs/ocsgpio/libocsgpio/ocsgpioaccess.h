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

#define DVCHANGES_MAJ_SOLIBVER		1
#define DVCHANGES_MIN_SOLIBVER		7

#define IS_NONEV_ROWMGR(rev, mode) 	( (ocs_get_mode(IDTYPE_PCBREVID, &rev) == SUCCESS) && (rev > PCBREVID_EV) && \
									  (ocs_get_mode(IDTYPE_MODEID, &mode) == SUCCESS) && (mode == RMMODE_ROWMGR) )

/* Shared lib functions */
int ocs_gpio_setup(void);
int ocs_gpio_teardown(void);
int ocs_port_control(int portid, int is_on);
int ocs_port_present(int portid, unsigned long long *portstate);
int ocs_port_state(int portid, unsigned long long *portstate);
int ocs_port_uptime(int portid, unsigned long *uptime);
int ocs_port_buffer(int is_on, unsigned int *state);
int ocs_port_throttlebypass(int is_on, unsigned int *state);
int ocs_port_thlocalbypass(int is_on, unsigned int *state);
int ocs_port_thenable(int is_on, unsigned int *state);
int ocs_port_rowthenable(int is_on, unsigned int *state);
int ocs_port_lrselect(int is_on, unsigned int *state);
int ocs_port_relay(int id, int is_on, unsigned int *state);
int ocs_port_dbgled(int id, int is_on, unsigned int *state);
int ocs_port_attentionled(int is_on, unsigned int *state);
int ocs_get_mode(unsigned int modetype, unsigned int *modeval);
int ocs_get_powergood(unsigned int *state);
int ocs_gpio_libgetversion(u_int32_t *ver);
