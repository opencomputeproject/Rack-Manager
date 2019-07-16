// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#define CMD_HELP_SETUP "\n\
    setupgpio - Export gpios to enable user mode access\n\
			 \tArguments: \n\
			 \t\t <kernel module> - Kernel module file name with full path\n"

#define CMD_HELP_TEARDOWN "\n\
    cleanupgpio - Un-export gpios when user mode access is no more needed\n\
              \tNote: The values of GPIOs may change to their defaults\n\
              \tcausing unexpected results\n"

#define CMD_HELP_PORTBUFFER "\n\
    portbuffer - Controls the FW_READY_BUF_EN signal to latch other signals\n\
              \tArguments: \n\
              \t\t on    - latch hw buffers\n\
              \t\t off   - un-latch hw buffers\n\
              \t\t state - read current latch state of hw buffers\n"

#define CMD_HELP_LRSELECT "\n\
    lrselect - Controls the LR Select signal\n\
              \tArguments: \n\
              \t\t on    - assert LR Select\n\
              \t\t off   - de-assert LR Select\n\
              \t\t state - read current state of LR Select\n"

#define CMD_HELP_THBYPASS "\n\
    throttlebypass - Controls the Throttle bypass signal\n\
              \tArgument 1: \n\
              \t\t on    - enable Throttle bypass\n\
              \t\t off   - disable Throttle bypass\n\
              \t\t state - read current state of Throttle bypass\n\
              \tArgument 2: \n\
              \t\t type  - 0, works on Throttle Bypass\n\
              \t\t         1, works on Local Throttle Bypass\n"

#define CMD_HELP_THCONTROL "\n\
    throttlecontrol - Controls the Throttle Output enable signal\n\
              \tArgument 1: \n\
              \t\t on    - assert Throttle OE\n\
              \t\t off   - de-assert Throttle OE\n\
              \t\t state - read current state of Throttle OE\n\
              \tArgument 2: \n\
              \t\t type  - 0, controls signal on Rack Manager\n\
              \t\t         1, controls signal on Row Manger PIB\n"
			  
#define CMD_HELP_RELAY "\n\
    relaycontrol - Controls the load power state through relay signals\n\
              \tArgument 1: \n\
              \t\t ID    - Valid relay number from 1 to 4\n\
              \tArgument 2: \n\
              \t\t on    - Turn on the load\n\
              \t\t off   - Turn off the load\n\
              \t\t state - read current power state of load\n"

#define CMD_HELP_LED "\n\
    debugled - Controls the state of debug LEDs\n\
              \tArgument 1: \n\
              \t\t ID    - Valid debug LED number from 1 to 4\n\
              \tArgument 2: \n\
              \t\t on    - Turn on the LED\n\
              \t\t off   - Turn off the LED\n\
              \t\t state - read current state of LED\n"

#define CMD_HELP_ATTENTION_LED "\n\
    attentionled - Controls the state of the attention LED\n\
              \tArgument 1: \n\
              \t\t on    - Turn on the LED\n\
              \t\t off   - Turn off the LED\n\
              \t\t state - read current state of LED\n"

#define CMD_HELP_PORTCONTROL "\n\
    portcontrol - Controls signal to the ports \n\
              \tArgument 1: \n\
              \t\t ID    - Valid Port ID from 1 to 48\n\
              \t\t       - If ID is 0, ontime log will be reset\n\
              \tArgument 2: \n\
              \t\t on    - Turn on the Port\n\
              \t\t off   - Turn off the Port\n"

#define CMD_HELP_PORTSTATE "\n\
    portstate - Reads the current state of the ports \n\
              \tArgument: \n\
              \t\t ID    - Valid Port ID from 1 to 48\n\
              \t\t       - If an ID is not given, a 64 bit value that is a \n\
              \t\t         bitmask of the state of all ports is returned \n"

#define CMD_HELP_PORTPRESENT "\n\
    portpresent - Reads the current presence state on the ports \n\
              \tArgument: \n\
              \t\t ID    - Valid Port ID from 1 to 48\n\
              \t\t       - If an ID is not given, a 64 bit value that is a \n\
              \t\t         bitmask of the presence of all ports is returned \n"

#define CMD_HELP_ROWTHSTAT "\n\
    rowthstatus - Reads the status of different throttle signals from Row manager PIB \n\
              \tArgument: \n\
              \t\t type  - Valid row throttle status types from 1 to 4\n\
              \t\t         If a type is not given, a 32 bit value that is a \n\
              \t\t         bitmask of status of all 4 throttle signals is returned \n\
              \t\t         Type 0 - Get all signals\n\
              \t\t         Type 1 - Row throttle status\n\
              \t\t         Type 2 - DC throttle status\n\
              \t\t         Type 3 - Row throttle cable status\n\
              \t\t         Type 4 - DC throttle cable status\n"
			  
#define CMD_HELP_MODE "\n\
    getmode - Reads the current mode in which Rack manager is operating\n\
              \tReturned ID value: \n\
              \t\t 0x0   - Power Interface Board config\n\
              \t\t 0x1   - Non WCS config\n\
              \t\t 0x2   - MTE\n"

#define CMD_HELP_PGOOD "\n\
    getpowergood - Reads the 12VA and 12VB status\n\n"

