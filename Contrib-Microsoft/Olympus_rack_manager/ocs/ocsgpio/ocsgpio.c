// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsgpio-common.h>
#include <ocsgpioaccess.h>
#include <ocsgpio-help.h>
#include <gpiomon-usrhdlr.h>

#define APP_VERSION_MAJOR    	1
#define APP_VERSION_MINOR    	6
#define APP_VERSION_REVISION 	0
#define APP_VERSION_BUILD    	0

const char CMD_SETUP[]          = "setupgpio";
const char CMD_TEARDOWN[]       = "cleanupgpio";
const char CMD_PORT_PRESENT[]   = "portpresent";
const char CMD_PORT_CONTROL[]   = "portcontrol";
const char CMD_PORT_STATE[]     = "portstate";
const char CMD_RELAY_CONTROL[]  = "relaycontrol";
const char CMD_LRSELECT[]       = "lrselect";
const char CMD_THBYPASS[]       = "throttlebypass";
const char CMD_THENABLE[]       = "throttlecontrol";
const char CMD_PORTBUFFER[]     = "portbuffer";
const char CMD_GET_MODE[]       = "getmode";
const char CMD_GET_PGOOD[]      = "getpowergood";
const char CMD_DEBUGLED[]     	= "debugled";
const char CMD_ATTENTIONLED[]	= "attentionled";
const char CMD_ROWTHSTAT[] 		= "rowthstatus";
const char CMD_HELP[]           = "-h";
const char CMD_ARG_ON[]         = "on";
const char CMD_ARG_OFF[]        = "off";
const char CMD_ARG_STATE[]      = "state";

const char AppName[]            = APPNAME;

/******************************************************************************
*   Function Name: show_usage
*   Purpose: Print a 1 line guide
*******************************************************************************/
void show_usage(void)
{
    LOG_INFO("Run %s -h for help\n\n", AppName);
}

/******************************************************************************
*   Function Name: show_help
*   Purpose: Print detailed help on usage
*******************************************************************************/
void show_help(void)
{
	unsigned int ver;
	ocs_gpio_libgetversion(&ver);
    LOG_INFO("\n%s v%d.%d, Lib v%d.%d. (C) 2016 Microsoft Corp\n", AppName, 
										APP_VERSION_MAJOR, APP_VERSION_MINOR,
										VERSION_GET_MAJOR(ver), VERSION_GET_MINOR(ver) );

    LOG_INFO("Usage: %s commandname <port/relay/led id> <action> \n\n"\
             "    where commandname shall be one of the following:\n"\
                            CMD_HELP_SETUP         \
                            CMD_HELP_TEARDOWN      \
                            CMD_HELP_PORTBUFFER    \
                            CMD_HELP_PORTPRESENT   \
                            CMD_HELP_PORTCONTROL   \
                            CMD_HELP_PORTSTATE     \
                            CMD_HELP_LRSELECT      \
                            CMD_HELP_THBYPASS      \
							CMD_HELP_THCONTROL     \
                            CMD_HELP_RELAY         \
                            CMD_HELP_LED           \
							CMD_HELP_ATTENTION_LED \
                            CMD_HELP_MODE		   \
							CMD_HELP_ROWTHSTAT	   \
							CMD_HELP_PGOOD,
                            AppName);
}

/******************************************************************************
*   Function Name: strlwr
*   Purpose: Helper function to convert input string to lower case and 
*            store it in place
*   In arguments: *str - Input string pointer
*   Return value: Same as input string pointer
*   Comments/Notes:
*******************************************************************************/
static char *strlwr(char *str)
{
   unsigned char *p = (unsigned char *)str;
 
   while (*p) {
      *p = tolower(*p);
      p++;
   }
 
   return str;
}

//TODO:
//LIB_VERSION_CHECK (VERSION_GET_MAJOR(ver) >= DVCHANGES_MAJ_SOLIBVER) && (VERSION_GET_MINOR(ver) >= DVCHANGES_MIN_SOLIBVER)
//LOG_INFO("[%s]:Warning - using old shared library version. Some features may fail\n", AppName);

/******************************************************************************
*   Function Name: main
*******************************************************************************/
int main(int argc, char *argv[])
{
    int retval = SUCCESS;
        
    char *paramval;
    int paramid;
    int paramcontroltype;
    bool_t paramonoff;

    unsigned long long portstate;    
    unsigned int state;
    unsigned int modeval;
	unsigned int ver;
	unsigned long uptime;
   	
    if (argc < 2)
    {
        LOG_INFO("[%s]:Insufficient argument count %d\n", AppName, argc-1);
        retval = FAILED;
        show_help();
        return retval;
    }
	
	log_init(INFO_LEVEL);
	
    paramval = argv[1];
    if (strlen(paramval) == 0) {
        LOG_INFO("[%s]:Invalid command name argument %d\n", AppName, 1);
        retval = FAILED;
        show_help();
    }
    else if (strncmp(CMD_HELP, strlwr(paramval), strlen(CMD_HELP)) == 0) {
        show_help();
    }
    else if (strncmp(CMD_SETUP, strlwr(paramval), strlen(CMD_SETUP)) == 0) {       
		if ( argc < 3 || strlen(argv[2]) == 0 ) {
            LOG_INFO("[%s]:Invalid argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        
		if (retval != FAILED) {
            retval = ocs_gpio_setup();
            if (retval != FAILED) {
                LOG_INFO("[%s]:GPIO setup done...", AppName);
				retval = gpiomon_wait(argv[2]);
			}			
        }
    }
    else if (strncmp(CMD_TEARDOWN, strlwr(paramval), strlen(CMD_TEARDOWN)) == 0) {
        if (retval != FAILED) {
            retval = ocs_gpio_teardown();
            if (retval != FAILED)
                LOG_INFO("[%s]:GPIO cleanup done\n", AppName);
        }
    }
    /* Commandline: <appname> portbuffer <action>*/
    else if (strncmp(CMD_PORTBUFFER, strlwr(paramval), strlen(CMD_PORTBUFFER)) == 0) {
        if (argc < 3) {
            LOG_INFO("[%s]:Invalid argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[2]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[2]), 2) != 0)?2:1):0;
			
            retval = ocs_port_buffer(paramonoff, &state);
			if (retval != FAILED) {
                if (paramonoff < 2)
                    state = paramonoff;
				LOG_INFO("[%s]: Port buffer state is %s\n", AppName, state?"on":"off");
			} 
        }
    }
    /* Commandline: <appname> lrselect <action>*/
    else if (strncmp(CMD_LRSELECT, strlwr(paramval), strlen(CMD_LRSELECT)) == 0) {
        if (argc < 3) {
            LOG_INFO("[%s]:Invalid argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[2]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[2]), 2) != 0)?2:1):0;
			
			retval = ocs_port_lrselect(paramonoff, &state);		
			if (retval != FAILED) {
                if (paramonoff < 2)
                    state = paramonoff;
				LOG_INFO("[%s]: LR Select state is %s\n", AppName, state?"on":"off");
			} 
        }
    }
    /* Commandline: <appname> throttlecontrol <action> <type>*/
    else if (strncmp(CMD_THENABLE, strlwr(paramval), strlen(CMD_THENABLE)) == 0) {
        if (argc < 3) {
            LOG_INFO("[%s]:Invalid argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[2]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[2]), 2) != 0)?2:1):0;

			if ( (argc == 4) && (strtol(argv[3], NULL, 10) != 0) ) {
				if (! IS_NONEV_ROWMGR(ver, modeval) )
					LOG_INFO("[%s]: operation not supported on this config %d, pcbrev %d\n", AppName, modeval, ver);
				else
					retval = ocs_port_rowthenable(paramonoff, &state);
			}
			else
				retval = ocs_port_thenable(paramonoff, &state);
			
			if (retval != FAILED) {
                if (paramonoff < 2)
                    state = paramonoff;
				LOG_INFO("[%s]: Throttle OE state is %s\n", AppName, state?"enabled":"disabled");
			} 
        }
    }
    /* Commandline: <appname> throttlebypass <action> <type>*/
    else if (strncmp(CMD_THBYPASS, strlwr(paramval), strlen(CMD_THBYPASS)) == 0) {
        if (argc < 3) {
            LOG_INFO("[%s]:Invalid argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[2]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[2]), 2) != 0)?2:1):0;
			if ( (argc == 4) && (strtol(argv[3], NULL, 10) != 0) )
				retval = ocs_port_thlocalbypass(paramonoff, &state);
			else
				retval = ocs_port_throttlebypass(paramonoff, &state);
			
			if (retval != FAILED) {
                if (paramonoff < 2)
                    state = paramonoff;
				LOG_INFO("[%s]: Throttle bypass state is %s\n", AppName, state?"on":"off");
			} 
        }
    }
    /* Commandline: <appname> rowthstatus <type>*/
    else if (strncmp(CMD_ROWTHSTAT, strlwr(paramval), strlen(CMD_ROWTHSTAT)) == 0) {
		if (! IS_NONEV_ROWMGR(ver, modeval) ) {
			retval = FAILED;
			LOG_INFO("[%s]: operation not supported on this config %d, pcbrev %d\n", AppName, modeval, ver);
		}
		else if (argc > 2) {
            paramid = strtol(argv[2], NULL, 10);
            if (paramid >= THSTATTYPE_MAX) {
                LOG_INFO("[%s]:Invalid Row manager PIB throttle status type %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {           
                /* Process the command */
                retval = ocs_port_rowthstat( paramid, &modeval );
            }
        }
        else {
            paramid = THSTATTYPE_ALL;
            retval = ocs_port_rowthstat( paramid, &modeval );
        }
		
		if (retval != FAILED) {
			if (paramid == THSTATTYPE_ALL)
				LOG_INFO("[%s]:Row manager PIB throttle status for type %d is 0x%x\n", 
									AppName, paramid, modeval);
			else
				LOG_INFO("[%s]:Row manager PIB throttle status for type %d is %s\n", 
									AppName, paramid, retval?"Present":"Absent");
		}
    }
    /* Commandline: <appname> getmode <ID type>*/
    else if (strncmp(CMD_GET_MODE, strlwr(paramval), strlen(CMD_GET_MODE)) == 0) {
        if (argc > 2) {
            paramid = strtol(argv[2], NULL, 10);
            if (paramid >= IDTYPE_MAX) {
                LOG_INFO("[%s]:Invalid ID type %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {           
                /* Process the command */
                retval = ocs_get_mode( paramid, &modeval );
            }
        }
        else {
            paramid = IDTYPE_MODEID;
            retval = ocs_get_mode( paramid, &modeval );
        }
		if (retval != FAILED)
			LOG_INFO("[%s]:ID value is %x\n", AppName, modeval);
    }
	/* Commandline: <appname> getmode <ID type>*/
    else if (strncmp(CMD_GET_PGOOD, strlwr(paramval), strlen(CMD_GET_PGOOD)) == 0) {
        retval = ocs_get_powergood( &modeval );

		if (retval != FAILED)
			LOG_INFO("[%s]: 12VA: %s, 12VB: %s\n", AppName, 
						(modeval & P12VAGOOD)?"good":"bad",
						(modeval & P12VBGOOD)?"good":"bad");
    }
    /* Commandline: <appname> debugled <LED ID> <action> */
    else if (strncmp(CMD_DEBUGLED, strlwr(paramval), strlen(CMD_DEBUGLED)) == 0) {
        if (argc < 4) {
            LOG_INFO("[%s]:Incorrect argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramid = strtol(argv[2], NULL, 10);
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[3]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[3]), 2) != 0)?2:1):0;
            
            if ( (paramid < 1) || (paramid > MAX_DBGLED_GPIOCOUNT) ) {
                LOG_INFO("[%s]:Invalid LED ID %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {
                retval = ocs_port_dbgled(paramid, paramonoff, &state);
                if (retval != FAILED) {
                    if (paramonoff < 2)
                        state = paramonoff;
                    LOG_INFO("[%s]: Debug LED %d state is %s\n", AppName, paramid, state?"on":"off");
                } 
            }
        }
    }
	/* Commandline: <appname> attentionled <action> */
	else if (strncmp(CMD_ATTENTIONLED, strlwr(paramval), strlen(CMD_ATTENTIONLED)) == 0) {
		if (argc < 3) {
			LOG_INFO("[%s]:Incorrect argument count %d\n", AppName, argc - 1);
			show_usage();
			retval = FAILED;
		}
		else {
			paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[2]), 3) != 0) ?
				((strncmp(CMD_ARG_ON, strlwr(argv[2]), 2) != 0) ? 2 : 1) : 0;

			retval = ocs_port_attentionled(paramonoff, &state);
			if (retval != FAILED) {
				if (paramonoff < 2)
					state = paramonoff;
				LOG_INFO("[%s]: Attention LED state is %s\n", AppName, state ? "on" : "off");
			}
		}
	}
    /* Commandline: <appname> relaycontrol <relay ID> <action> */
    else if (strncmp(CMD_RELAY_CONTROL, strlwr(paramval), strlen(CMD_RELAY_CONTROL)) == 0) {
        if (argc < 4) {
            LOG_INFO("[%s]:Incorrect argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramid = strtol(argv[2], NULL, 10);
            paramonoff = (strncmp(CMD_ARG_OFF, strlwr(argv[3]), 3) != 0)?
							((strncmp(CMD_ARG_ON, strlwr(argv[3]), 2) != 0)?2:1):0;
            
            if ( (paramid < 1) || (paramid > MAX_RELAY_GPIOCOUNT) ) {
                LOG_INFO("[%s]:Invalid relay ID %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {
				retval = ocs_port_relay(paramid, paramonoff, &state);
				if (retval != FAILED) {
					if (paramonoff < 2)
						state = paramonoff;
					LOG_INFO("[%s]: Relay ID %d state is %s\n", AppName, paramid, state?"on":"off");
				}
				else
					LOG_ERR(errno, "[%s]: Relay operation failed for ID %d with code %d\n", AppName, paramid, retval);
            }
        }
    }
    /* Commandline: <appname> portcontrol <blade number / range> <action> */
    else if (strncmp(CMD_PORT_CONTROL, strlwr(paramval), strlen(CMD_PORT_CONTROL)) == 0) {
        if (argc < 4) {
            LOG_INFO("[%s]:Incorrect argument count %d\n", AppName, argc-1);
            show_usage();
            retval = FAILED;
        }
        else {
            paramid = strtol(argv[2], NULL, 10);
            paramonoff = (strncmp(CMD_ARG_ON, strlwr(argv[3]), 2) == 0);
            
            if ( paramid > MAX_PORT_GPIOCOUNT ) {
                LOG_INFO("[%s]:Invalid Port ID %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {
				/* Port ID 0 will reset / recreate the on time log */
                retval = ocs_port_control(paramid, paramonoff);
            }
        }
    }
    /* Commandline: <appname> portstate <blade number / range> */
    else if (strncmp(CMD_PORT_STATE, strlwr(paramval), strlen(CMD_PORT_STATE)) == 0) {
        paramid = PARAM_ALL;
        if (argc > 2) {
            paramid = strtol(argv[2], NULL, 10);
            if ( (paramid < 1) || (paramid > MAX_PORT_GPIOCOUNT) ) {
                LOG_INFO("[%s]:Invalid Port ID %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {
                retval = ocs_port_state(paramid, &portstate);
				if ( retval != FAILED )
					LOG_INFO("[%s]: Port ID %d is %s\n", AppName, paramid, (portstate == 0)?"off":"on");
				
				retval = ocs_port_uptime(paramid, &uptime);
				if ( retval != FAILED )
					LOG_INFO("[%s]: Port ID %d was last turned on %us ago\n", AppName, paramid, uptime);
				else
					LOG_INFO("[%s]: On time for Port ID %d could not be determined\n", AppName, paramid);
            }
        }
        else {
            retval = ocs_port_state(paramid, &portstate);
			if ( retval != FAILED )
				LOG_INFO("[%s]: State for all ports is 0x%llx\n", AppName, portstate);
        }       
    }
    /* Commandline: <appname> portpresent <blade number> */
    else if (strncmp(CMD_PORT_PRESENT, strlwr(paramval), strlen(CMD_PORT_PRESENT)) == 0) {
        paramid = PARAM_ALL;
        if (argc > 2) {
            paramid = strtol(argv[2], NULL, 10);
            if ( (paramid < 1) || (paramid > MAX_PORT_GPIOCOUNT) ) {
                LOG_INFO("[%s]:Invalid Port ID %d\n", AppName, paramid);
                show_usage();
                retval = FAILED;
            }
            else {           
                retval = ocs_port_present(paramid, &portstate);
            }
        }
        else {
            retval = ocs_port_present(paramid, &portstate);
        }
        
        if ( retval != FAILED ) {
            if (paramid == PARAM_ALL)
                LOG_INFO("[%s]: Presence for all ports is 0x%llx\n", AppName, portstate);
            else
                LOG_INFO("[%s]: Port ID %d is%spresent\n", AppName, paramid, (portstate == 0)?" not ":" ");
        }
    }
    else {
        LOG_INFO("[%s]:Invalid command name argument %d\n", AppName, 1);
        show_usage();
        retval = FAILED;
    }
    
    LOG_INFO("\n");
    
    return retval;          
}                           
