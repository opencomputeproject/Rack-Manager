// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#ifndef MGMT_SWITCH_H_
#define MGMT_SWITCH_H_

#include <termios.h>


int mgmt_switch_connect_console (const char *dev, int echo, speed_t baud);
void mgmt_switch_disconnect_console ();

int mgmt_switch_send_enter ();

int mgmt_switch_console_login ();
int mgmt_switch_console_logout ();
int mgmt_switch_goto_root_prompt ();

int mgmt_switch_reboot (int login);

int mgmt_switch_execute_config_command (const char *command, int login, char **error);
int mgmt_switch_apply_config_file (const char *path, int *line, char **error);
int mgmt_switch_clear_startup_config (int backup);
int mgmt_switch_save_startup_config (int restore);

int mgmt_switch_activate_inactive_image ();
int mgmt_switch_upload_firmware (const char *server, const char *path);

int mgmt_switch_dump_console ();
int mgmt_switch_interactive_console (int catch_sigint);


#endif /* MGMT_SWITCH_H_ */
