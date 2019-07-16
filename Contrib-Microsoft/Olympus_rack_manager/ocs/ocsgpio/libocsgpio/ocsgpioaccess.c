// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

#include <ocsgpio-common.h>
#include <ocsgpioaccess.h>
#include <ocsgpio-rmmap.h>
#include <gpio-ops.h>
#include <led-ops.h>
#include <ocslock.h>
 
#define ATTENTION_LED_NAME "m2010:orange:attention"

/* Global variables list */
const unsigned int gpioid_portpresence[MAX_PORT_GPIOCOUNT] = {
	GPIO_PORTPRESENCE_1, GPIO_PORTPRESENCE_2, GPIO_PORTPRESENCE_3, GPIO_PORTPRESENCE_4, 
    GPIO_PORTPRESENCE_5, GPIO_PORTPRESENCE_6, GPIO_PORTPRESENCE_7, GPIO_PORTPRESENCE_8, 
    GPIO_PORTPRESENCE_9, GPIO_PORTPRESENCE_10, GPIO_PORTPRESENCE_11, GPIO_PORTPRESENCE_12, 
    GPIO_PORTPRESENCE_13, GPIO_PORTPRESENCE_14, GPIO_PORTPRESENCE_15, GPIO_PORTPRESENCE_16, 
    GPIO_PORTPRESENCE_17, GPIO_PORTPRESENCE_18, GPIO_PORTPRESENCE_19, GPIO_PORTPRESENCE_20, 
    GPIO_PORTPRESENCE_21, GPIO_PORTPRESENCE_22, GPIO_PORTPRESENCE_23, GPIO_PORTPRESENCE_24, 
    GPIO_PORTPRESENCE_25, GPIO_PORTPRESENCE_26, GPIO_PORTPRESENCE_27, GPIO_PORTPRESENCE_28, 
    GPIO_PORTPRESENCE_29, GPIO_PORTPRESENCE_30, GPIO_PORTPRESENCE_31, GPIO_PORTPRESENCE_32, 
    GPIO_PORTPRESENCE_33, GPIO_PORTPRESENCE_34, GPIO_PORTPRESENCE_35, GPIO_PORTPRESENCE_36, 
    GPIO_PORTPRESENCE_37, GPIO_PORTPRESENCE_38, GPIO_PORTPRESENCE_39, GPIO_PORTPRESENCE_40, 
    GPIO_PORTPRESENCE_41, GPIO_PORTPRESENCE_42, GPIO_PORTPRESENCE_43, GPIO_PORTPRESENCE_44, 
    GPIO_PORTPRESENCE_45, GPIO_PORTPRESENCE_46, GPIO_PORTPRESENCE_47, GPIO_PORTPRESENCE_48
};
        
const unsigned int gpioid_portcontrol[MAX_PORT_GPIOCOUNT] = {
	GPIO_PORTCONTROL_1, GPIO_PORTCONTROL_2, GPIO_PORTCONTROL_3, GPIO_PORTCONTROL_4, 
    GPIO_PORTCONTROL_5, GPIO_PORTCONTROL_6, GPIO_PORTCONTROL_7, GPIO_PORTCONTROL_8, 
    GPIO_PORTCONTROL_9, GPIO_PORTCONTROL_10, GPIO_PORTCONTROL_11, GPIO_PORTCONTROL_12, 
    GPIO_PORTCONTROL_13, GPIO_PORTCONTROL_14, GPIO_PORTCONTROL_15, GPIO_PORTCONTROL_16, 
    GPIO_PORTCONTROL_17, GPIO_PORTCONTROL_18, GPIO_PORTCONTROL_19, GPIO_PORTCONTROL_20, 
    GPIO_PORTCONTROL_21, GPIO_PORTCONTROL_22, GPIO_PORTCONTROL_23, GPIO_PORTCONTROL_24, 
    GPIO_PORTCONTROL_25, GPIO_PORTCONTROL_26, GPIO_PORTCONTROL_27, GPIO_PORTCONTROL_28, 
    GPIO_PORTCONTROL_29, GPIO_PORTCONTROL_30, GPIO_PORTCONTROL_31, GPIO_PORTCONTROL_32, 
    GPIO_PORTCONTROL_33, GPIO_PORTCONTROL_34, GPIO_PORTCONTROL_35, GPIO_PORTCONTROL_36, 
    GPIO_PORTCONTROL_37, GPIO_PORTCONTROL_38, GPIO_PORTCONTROL_39, GPIO_PORTCONTROL_40, 
    GPIO_PORTCONTROL_41, GPIO_PORTCONTROL_42, GPIO_PORTCONTROL_43, GPIO_PORTCONTROL_44, 
    GPIO_PORTCONTROL_45, GPIO_PORTCONTROL_46, GPIO_PORTCONTROL_47, GPIO_PORTCONTROL_48
};

const unsigned int gpioid_relaycontrol[MAX_RELAY_GPIOCOUNT] ={
	GPIO_RELAYCONTROL_1, GPIO_RELAYCONTROL_2, GPIO_RELAYCONTROL_3, GPIO_RELAYCONTROL_4
};
        
const unsigned int gpioid_portbuffercontrol = GPIO_PORT_PORTBUFFER;

const unsigned int gpioid_dbgled[MAX_DBGLED_GPIOCOUNT] = {
    GPIO_PORT_DEBUGLED0, GPIO_PORT_DEBUGLED1,
    GPIO_PORT_DEBUGLED2, GPIO_PORT_DEBUGLED3
};

const unsigned int gpioid_mode[MAX_BOARDID_GPIOCOUNT] = {
	GPIO_BOARDID_0, GPIO_BOARDID_1, GPIO_BOARDID_2
};

const unsigned int gpioid_boardrev[MAX_PCBREVID_GPIOCOUNT] = {
	GPIO_PCBREVID_0, GPIO_PCBREVID_1, GPIO_PCBREVID_2
};

const unsigned int gpioid_rowthstatus[MAX_ROWTHSTAT_GPIOCOUNT] = {
	GPIO_PORT_THSRCROW, GPIO_PORT_THSRCDC, GPIO_PORT_ROWTHCONNECTED, GPIO_PORT_DCTHCONNECTED
};

/* Helper macros */
#define LOG_ERROR   do {                            \
        if (errno > 0 || retval < 0)                \
            log_fnc_err(errno, " retval %d", retval);\
    } while (0);                                    \

/******************************************************************************
*   Function Name: write_portfile [private]
*   Purpose: Writes timedata to a file that is mapped to portid
*   Comments/Notes: 
*******************************************************************************/
static int write_portfile(int portid, struct timespec *tval) 
{
	int retval = SUCCESS;
	FILE *fptr;
	
	char portfilename[sizeof(OCSPORTONTIME_FILE)+1];	
	sprintf(portfilename, OCSPORTONTIME_FILE, portid);
	
	fptr = fopen(portfilename, "wb+");
	if ( !fptr ) {
		retval = FAILED;
		LOG_ERROR;	
	}
	else {
		retval = fwrite(tval, 1, sizeof(struct timespec), fptr);
		if (retval != sizeof(struct timespec))
			retval = FAILED;
		else
			LOG_TRACE("Ontime for portid %d, data written, %d bytes, %us\n", portid, retval, (unsigned int)tval.tv_sec);
		fclose(fptr);
	}
	
	return retval;
}
	
/******************************************************************************
*   Function Name: update_ontime [private]
*   Purpose: Updates on-time for the requested portid in the ontime log file
*   Comments/Notes: If portid param = 0, all time entries are initialized to 
*                   initval_s value for the tv_sec member
*******************************************************************************/
static int update_ontime( int portid, time_t initval_s )
{
	int retval;
	int i;
	struct timespec timenow = {0, 0};
	unsigned long long portpresence = 0;
	
	errno = 0;
					
	if (portid != PARAM_ALL) {
		retval = clock_gettime(CLOCK_REALTIME, &timenow);
		if ( retval == SUCCESS )
			retval = write_portfile(portid, &timenow);
		else
			LOG_ERROR;
	}
	else {
		if ( ocs_port_present( PARAM_ALL, &portpresence ) == FAILED ) {
			portpresence = 0;
			LOG_TRACE("Unable to get port presence for all ports\n");
		}
		
		/* Create file and/or Reset all time stamps */
		for (i = 0; i < MAX_PORT_GPIOCOUNT; i++) {		
			timenow.tv_sec = ((portpresence >> i) & 1)?initval_s:0;
			timenow.tv_nsec = 0;
			retval = write_portfile(portid, &timenow);
			if ( retval == FAILED )
				break;
		}
	}	return (retval != FAILED)?SUCCESS:FAILED; 
}

/******************************************************************************
*   Function Name: get_uptime (private)
*   Purpose: Reads on-time log file and computes uptime for the req portid
*   Comments/Notes:
*******************************************************************************/
static int get_uptime( int portid )
{
	int retval;
	FILE *fptr;
	struct timespec uptime = {0, 0};
	struct timespec ontime = {0, 0};
	
	char portfilename[sizeof(OCSPORTONTIME_FILE)+1];	
	sprintf(portfilename, OCSPORTONTIME_FILE, portid);
	
	errno = 0;
	
	fptr = fopen(portfilename, "rb");
	if ( !fptr ) {
		retval = FAILED;
		LOG_ERROR;
		return retval;
	}
	
	retval = fread(&ontime, 1, sizeof(struct timespec), fptr);
	LOG_TRACE("Ontime for portid %d, data read, %d bytes, %us\n", portid, retval, (unsigned int)ontime.tv_sec);
	if (retval == sizeof(struct timespec)) {
		/* If the ontime was never logged return failure */
		if (ontime.tv_sec == 0) {
			retval = FAILED;
			goto _exit_fn; 
		}

		retval = clock_gettime(CLOCK_REALTIME, &uptime);
		if ( retval != SUCCESS ) {
			retval = FAILED;
			LOG_ERROR;
			goto _exit_fn; 
		}
		
		uptime.tv_sec  -= ontime.tv_sec;
		uptime.tv_nsec -= ontime.tv_nsec;    
		if (uptime.tv_nsec > 500000000L)
			uptime.tv_sec++;
		retval = (uptime.tv_sec >= 0)?uptime.tv_sec:FAILED;
	}
	else
		retval = FAILED;

_exit_fn:
	fclose(fptr);

	return retval; 
}

/******************************************************************************
*   Function Name: setup_at_portbufferon
*   Purpose: Setup actions that need to happen after port buffer is turned on
*   Comments/Notes:
*******************************************************************************/
int setup_at_portbufferon(void)
{
    int retval = SUCCESS;
	struct timespec timenow = {0, 0};

	retval = ocs_lock(OCSGPIOACCESS);
	if (retval == SUCCESS) {
		retval = clock_gettime(CLOCK_REALTIME, &timenow);
		if (retval != SUCCESS) {
			LOG_ERROR
		}
		else {
			update_ontime( PARAM_ALL, timenow.tv_sec - BLADE_STARTTIME_DELAY_SEC );
		}
	}
	ocs_unlock(OCSGPIOACCESS);
	
	return retval;
}

/******************************************************************************
*   Function Name: ocs_gpio_setup
*   Purpose: Exports appropriate GPIOs and sets direction.
*   Comments/Notes:
*******************************************************************************/
int ocs_gpio_setup(void)
{
	unsigned int rev, mode;
    int count;
	int retval;
	
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {
        for (count=0; (retval == SUCCESS) && (count < MAX_PORT_GPIOCOUNT); count++) {		
            retval = gpio_setup( gpioid_portpresence[count], GPIO_DIR_IN,
									IS_ACTIVE_LOW(ACTIVELEVEL_PORTPRESENCE) ); 
            retval = gpio_setup( gpioid_portcontrol[count], GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_PORTCONTROL) );
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_RELAY_GPIOCOUNT); count++) {
            retval = gpio_setup( gpioid_relaycontrol[count], GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_RELAYCONTROL) ); 
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_DBGLED_GPIOCOUNT); count++) {
            retval = gpio_setup( gpioid_dbgled[count], GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_DEBUGLED) ); 
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_BOARDID_GPIOCOUNT); count++) {
            retval = gpio_setup( gpioid_mode[count], GPIO_DIR_IN,
									IS_ACTIVE_LOW(ACTIVELEVEL_MODE) ); 
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_PCBREVID_GPIOCOUNT); count++) {
            retval = gpio_setup( gpioid_boardrev[count], GPIO_DIR_IN,
									IS_ACTIVE_LOW(ACTIVELEVEL_BOARDREV) ); 
        }

        if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_PORTBUFFER, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_PORTBUFFER) ); 
        }

		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_LRSELECT, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_LRSELECT) ); 
        }
        
		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_THBYPASS, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_THROTTLEBYPASS) ); 
        }

		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_THLOCALBYPASS, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_THLOCALBYPASS) ); 
        }
		
		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_THENABLE, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_THENABLE) ); 
        }

		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_P12VAGOOD, GPIO_DIR_IN,
									IS_ACTIVE_LOW(GPIO_PORT_P12VAGOOD) ); 
        }

		if (retval == SUCCESS) {
            retval = gpio_setup( GPIO_PORT_P12VBGOOD, GPIO_DIR_IN,
									IS_ACTIVE_LOW(GPIO_PORT_P12VBGOOD) ); 
        }
		
		/* This set of gpios only valid for DV+ Row Managers */
		if ( IS_NONEV_ROWMGR(rev, mode) ) {
			for (count=0; (retval == SUCCESS) && (count < MAX_ROWTHSTAT_GPIOCOUNT); count++) {
				retval = gpio_setup( gpioid_rowthstatus[count], GPIO_DIR_IN,
										IS_ACTIVE_LOW(ACTIVELEVEL_ROWTHSTAT) ); 
			}
			
			if (retval == SUCCESS) {
				retval = gpio_setup( GPIO_PORT_ROWTHENABLE, GPIO_DIR_OUT,
									IS_ACTIVE_LOW(ACTIVELEVEL_THENABLE) ); 
			}
		}

        ocs_unlock(OCSGPIOACCESS);
    }   

    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_gpio_teardown
*   Purpose: Unexports appropriate GPIOs.
*   Comments/Notes:
*******************************************************************************/
int ocs_gpio_teardown(void)
{
    int count;
    int retval = SUCCESS;
    errno = 0;
    
    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {   
        for (count=0; (retval == SUCCESS) && (count < MAX_PORT_GPIOCOUNT); count++) {
            retval = gpio_unexport( gpioid_portpresence[count] );
            retval = gpio_unexport( gpioid_portcontrol[count] );
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_RELAY_GPIOCOUNT); count++) {
            retval = gpio_unexport( gpioid_relaycontrol[count] );
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_DBGLED_GPIOCOUNT); count++) {
            retval = gpio_unexport( gpioid_dbgled[count] );
        }

        for (count=0; (retval == SUCCESS) && (count < MAX_BOARDID_GPIOCOUNT); count++) {
            retval = gpio_unexport( gpioid_mode[count] );
        }

        if (retval == SUCCESS) {
            retval = gpio_unexport( GPIO_PORT_PORTBUFFER );
        }

        if (retval == SUCCESS) {
            retval = gpio_unexport( GPIO_PORT_LRSELECT );
        }

        if (retval == SUCCESS) {
            retval = gpio_unexport( GPIO_PORT_THBYPASS );
        }

        ocs_unlock(OCSGPIOACCESS);
    }

    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}
	
/******************************************************************************
*   Function Name: ocs_get_mode
*   Purpose: Reads appropriate GPIOs and returns the board id or pcb rev value
*   Comments/Notes:
*******************************************************************************/
int ocs_get_mode(unsigned int modetype, unsigned int *modeval)
{
    int count;
	int pincount;
    int retval = SUCCESS;
    const unsigned int *gpioid;
	unsigned int portbufferstate = 0;
    errno = 0;

    *modeval = 0;

	if (modetype == IDTYPE_PCBREVID) {
		/* PCB rev id (active high) is muxed with port presennce (active low - pin config). 
		 * So it can only be read before the buffer enable pin is asserted */
		if (ocs_port_buffer(2, &portbufferstate) == SUCCESS) {
			if (portbufferstate == GPIO_HIGH) {
				LOG_ERROR
				return(FAILED);
			}
		}
		pincount = MAX_PCBREVID_GPIOCOUNT;
		gpioid = gpioid_boardrev;
	}
	else {
		pincount = MAX_BOARDID_GPIOCOUNT;
		gpioid = gpioid_mode;
	}
	
    for (count=0; (retval >= 0) && (count < pincount); count++)
    {
		retval = gpio_read( gpioid[count], FALSE );
		
        if (retval >= 0) {
			/* PCB rev id (active high) is muxed with port presennce (active low - pin config). 
			 * So it is necessary to invert the read out value for pcb rev id */
            *modeval |= ( ((modetype == IDTYPE_PCBREVID)?(~retval & 1):retval) << count);
        }
        else {
            break;
		}
    }
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_get_powergood
*   Purpose: Read 12V feeds A and B state
*******************************************************************************/
int ocs_get_powergood(unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

	retval = gpio_read( GPIO_PORT_P12VAGOOD, FALSE);
	if (retval != FAILED) {
		*state = retval?P12VAGOOD:0;
		retval = gpio_read( GPIO_PORT_P12VBGOOD, FALSE);
		if (retval != FAILED) {
			*state += (retval?P12VBGOOD:0);
			LOG_TRACE("12V state is %d\n", *state);
		}
	}
       
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_present
*   Purpose: Reads appropriate GPIOs and prints a present / absent message
*   Comments/Notes:
*******************************************************************************/
int ocs_port_present(int portid, unsigned long long *portstate)
{
    int count;
    int retval = SUCCESS;
    errno = 0;

    *portstate = 0;
    
    if ( (portid > 0) && (portid <= MAX_PORT_GPIOCOUNT) ) {
        /* Port ID argument starts at 1. Decrement to index into the array */
        retval = gpio_read( gpioid_portpresence[portid-1], FALSE );
        if (retval >= 0) {       
            LOG_TRACE("Port [%d, %s]\n", portid, retval?"Present":"Absent");
            *portstate = (unsigned long long)(retval?GPIO_HIGH:GPIO_LOW);
        }
    }
    else {
        /* Get presence for all ports */
        for (count=0; (retval != -1) && (count < MAX_PORT_GPIOCOUNT); count++) {
            retval = gpio_read( gpioid_portpresence[count], FALSE );
            if (retval >= 0) {       
                LOG_TRACE("Port [%d, %s]\n", count+1, retval?"Present":"Absent");
				if (retval == GPIO_HIGH)
					*portstate |= ((unsigned long long)GPIO_HIGH) << count;
            }
        }
    }
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_control
*   Purpose: Writes appropriate GPIOs to turn on and off ports
*   Comments/Notes: If is_on is PORT_ONTIME_UPDATE_ID, the ontime will be updated
*                   if the port was already on. This is relevant when a blade is
*                   inserted into the port that was already on.
*******************************************************************************/
int ocs_port_control(int portid, int is_on)
{
    int retval = SUCCESS;
	int priorstate = GPIO_LOW;
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {
        if ( (portid > 0) && (portid <= MAX_PORT_GPIOCOUNT) ) {
			priorstate = gpio_read( gpioid_portcontrol[portid-1], FALSE );
			if (is_on == PORT_ONTIME_UPDATE_ID) {
				// A new blade was inserted and port is already powered, need to update on time
				if ( (priorstate >= 0) && (priorstate == GPIO_HIGH) )
					retval = update_ontime(portid, 0);
			}
			else {
				retval = gpio_write( gpioid_portcontrol[portid-1], is_on?GPIO_HIGH:GPIO_LOW );
				if (retval == SUCCESS) {
					if ( is_on && (priorstate >= 0) && (priorstate == GPIO_LOW ) )
						retval = update_ontime(portid, 0);
					/* 100ms delay to accomodate blade PSU cycle time */
					usleep(100000);
					LOG_TRACE("Port ID [%d, %s]\n", portid, is_on?"on":"off");
				}
			}
        }
		else if (portid == PARAM_ALL)
			retval = update_ontime(PARAM_ALL, 0);
        ocs_unlock(OCSGPIOACCESS);
    }
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_state
*   Purpose:  process portcontrol, relaycontrol and lrswitch 
*            commands. Writes appropriate GPIOs and prints status messages
*   Comments/Notes:
*******************************************************************************/
int ocs_port_state(int portid, unsigned long long *portstate)
{
    int count;
    int retval = SUCCESS;
    errno = 0;

	*portstate = 0;
	if ( (portid > 0) && (portid <= MAX_PORT_GPIOCOUNT) ) {
		/* Port ID argument starts at 1. Decrement to index into the array */
		retval = gpio_read( gpioid_portcontrol[portid-1], FALSE );
		if (retval >= 0) {
			LOG_TRACE("Port [%d, %s]\n", portid, retval?"on":"off");
			*portstate = (unsigned long long)(retval?GPIO_HIGH:GPIO_LOW);
		}
	}
	else {
		/* Get presence for all ports */
		for (count=0; (retval != -1) && (count < MAX_PORT_GPIOCOUNT); count++) {
			retval = gpio_read( gpioid_portcontrol[count], FALSE );
			if (retval >= 0) {       
				LOG_TRACE("Port [%d, %s]\n", count+1, retval?"on":"off");
				if (retval == GPIO_HIGH)
					*portstate |= ((unsigned long long)GPIO_HIGH) << count;
			}
		}
	}
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_buffer
*   Purpose: Control Buffer Enable signal
*******************************************************************************/
int ocs_port_buffer(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

	if (is_on == 0 || is_on == 1) {
		retval = gpio_write( GPIO_PORT_PORTBUFFER, is_on?GPIO_HIGH:GPIO_LOW );
				
		if ((retval != FAILED) && (is_on)) {
			/* A 10ms delay to allow the buffer to stabilize output */
			usleep(10000);
			retval = setup_at_portbufferon();
		}
	}
	else {
		retval = gpio_read( GPIO_PORT_PORTBUFFER, FALSE);

		if (retval != FAILED) {
			*state = retval;
			LOG_TRACE("Port buffer state is %s\n", *state?"on":"off");
		}
	}
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}


/******************************************************************************
*   Function Name: ocs_port_buffer
*   Purpose:  process portcontrol, relaycontrol and lrswitch 
*            commands. Writes appropriate GPIOs and prints status messages
*   Comments/Notes:
*******************************************************************************/
int ocs_port_uptime(int portid, unsigned long *uptime)
{
	int retval = SUCCESS;
    errno = 0;
	
	*uptime = 0;

	if (ocs_lock(OCSGPIOACCESS) == SUCCESS) {
		if ( (portid > 0) && (portid <= MAX_PORT_GPIOCOUNT) ) {
			retval = get_uptime(portid);
			if (retval != FAILED)
				*uptime = retval;
		}
		ocs_unlock(OCSGPIOACCESS);
	}

    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_lrselect
*   Purpose:  process portcontrol, relaycontrol and lrswitch 
*            commands. Writes appropriate GPIOs and prints status messages
*   Comments/Notes:
*******************************************************************************/
int ocs_port_lrselect(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {
        *state = 0;
		if (is_on == 0 || is_on == 1) {
			retval = gpio_write( GPIO_PORT_LRSELECT, is_on?GPIO_HIGH:GPIO_LOW );
		}
		else {
			retval = gpio_read( GPIO_PORT_LRSELECT, FALSE);
			if (retval != FAILED)
				*state = retval;
		}
        ocs_unlock(OCSGPIOACCESS);
    }
	
	if (retval != FAILED) {
		LOG_TRACE("LR select state is %s\n", is_on?"on":"off");
	}
	
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_thenable
*   Purpose: Control Throttle Enable signal
*******************************************************************************/
int ocs_port_thenable(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

	if (is_on == 0 || is_on == 1) {
		retval = gpio_write( GPIO_PORT_THENABLE, is_on?GPIO_HIGH:GPIO_LOW );
	}
	else {
		retval = gpio_read( GPIO_PORT_THENABLE, FALSE);

		if (retval != FAILED) {
			*state = retval;
			LOG_TRACE("Throttle output enable state is %s\n", *state?"on":"off");
		}
	}
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_rowthenable
*   Purpose: Control Throttle Enable signal
*******************************************************************************/
int ocs_port_rowthenable(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

	if (is_on == 0 || is_on == 1) {
		retval = gpio_write( GPIO_PORT_ROWTHENABLE, is_on?GPIO_HIGH:GPIO_LOW );
	}
	else {
		retval = gpio_read( GPIO_PORT_ROWTHENABLE, FALSE);

		if (retval != FAILED) {
			*state = retval;
			LOG_TRACE("Row throttle output enable state is %s\n", *state?"on":"off");
		}
	}
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_rowthstat
*   Purpose: Control Throttle Enable signal
*******************************************************************************/
int ocs_port_rowthstat(int rowthstattype, unsigned int *state)
{
    int count;
    int retval = SUCCESS;
    errno = 0;

    *state = 0;
    
    if ( (rowthstattype > 0) && (rowthstattype <= MAX_ROWTHSTAT_GPIOCOUNT) ) {
        /* Port ID argument starts at 1. Decrement to index into the array */
        retval = gpio_read( gpioid_rowthstatus[rowthstattype-1], FALSE );
        if (retval >= 0) {       
            LOG_TRACE("Row mgr throttle status type [%d, %s]\n", rowthstattype, retval?"Present":"Absent");
            *state = (unsigned long long)(retval?GPIO_HIGH:GPIO_LOW);
        }
    }
    else {
        /* Get all status */
        for (count=0; (retval != -1) && (count < MAX_ROWTHSTAT_GPIOCOUNT); count++) {
            retval = gpio_read( gpioid_rowthstatus[count], FALSE );
            if (retval >= 0) {       
                LOG_TRACE("Port [%d, %s]\n", count+1, retval?"Present":"Absent");
				if (retval == GPIO_HIGH)
					*state |= ((unsigned long long)GPIO_HIGH) << count;
            }
        }
    }
    
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_throttlebypass
*   Purpose: Control Throttle Bypass function.
*******************************************************************************/
int ocs_port_throttlebypass(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {
        *state = 0;
		if (is_on == 0 || is_on == 1) {
			retval = gpio_write( GPIO_PORT_THBYPASS, is_on?GPIO_HIGH:GPIO_LOW );
		}
		else {
			retval = gpio_read( GPIO_PORT_THBYPASS, FALSE);
			if (retval != FAILED)
				*state = retval;
		}
        ocs_unlock(OCSGPIOACCESS);
    }
	
	if (retval != FAILED) {
		LOG_TRACE("Throttle bypass state is %s\n", is_on?"on":"off");
	}
	
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_thlocalbypass
*   Purpose: Control Throttle Bypass function.
*******************************************************************************/
int ocs_port_thlocalbypass(int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if (retval == SUCCESS) {
        *state = 0;
		if (is_on == 0 || is_on == 1) {
			retval = gpio_write( GPIO_PORT_THLOCALBYPASS, is_on?GPIO_HIGH:GPIO_LOW );
		}
		else {
			retval = gpio_read( GPIO_PORT_THLOCALBYPASS, FALSE);
			if (retval != FAILED)
				*state = retval;
		}
        ocs_unlock(OCSGPIOACCESS);
    }
	
	if (retval != FAILED) {
		LOG_TRACE("Local throttle bypass state is %s\n", is_on?"on":"off");
	}
	
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_dbgled
*   Purpose: The relay is Normally closed. This function represents the control
*            of power state of the load connected to the relay
*******************************************************************************/
int ocs_port_relay(int id, int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

    retval = ocs_lock(OCSGPIOACCESS);
    if ((retval == SUCCESS) && (id > 0) && (id <= MAX_RELAY_GPIOCOUNT) ) {
		*state = 0;
		
		if (is_on == 0 || is_on == 1) {
			retval = gpio_write( gpioid_relaycontrol[id-1], is_on?GPIO_HIGH:GPIO_LOW );
		}
		else {
			retval = gpio_read( gpioid_relaycontrol[id-1], FALSE);
			if (retval != FAILED)
				*state = retval;
		}
		ocs_unlock(OCSGPIOACCESS);
    }
	
	if (retval != FAILED) {
		LOG_TRACE("Relay load %d state is %s\n", id, is_on?"on":"off");
	}
	
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_dbgled
*   Purpose:  process portcontrol, relaycontrol and lrswitch 
*            commands. Writes appropriate GPIOs and prints status messages
*   Comments/Notes:
*******************************************************************************/
int ocs_port_dbgled(int id, int is_on, unsigned int *state)
{
    int retval = SUCCESS;
    errno = 0;

	if ( (id > 0) && (id <= MAX_DBGLED_GPIOCOUNT) ) {
		if (is_on == 0 || is_on == 1) {
			retval = gpio_write( gpioid_dbgled[id-1], is_on?GPIO_HIGH:GPIO_LOW );
		}
		else {
			retval = gpio_read( gpioid_dbgled[id-1], FALSE);
			if (retval != FAILED)
				*state = retval;
		}
	}
	else
		retval = FAILED;
	
	if (retval != FAILED) {
		LOG_TRACE("LED %d state is %s\n", id, is_on?"on":"off");
	}
	
    LOG_ERROR;
    return ((retval < 0)?FAILED:SUCCESS);
}

/******************************************************************************
*   Function Name: ocs_port_attentionled
*   Purpose:   Turns on/off attention LED or returns current state
*   Comments/Notes:
*******************************************************************************/
int ocs_port_attentionled(int is_on, unsigned int *state)
{
	int retval = SUCCESS;
	errno = 0;

	if (is_on == 0 || is_on == 1) 
	{
		retval = led_set_brightness(ATTENTION_LED_NAME, is_on ? LED_ON : LED_OFF);
	}
	else 
	{
		retval = led_get_brightness(ATTENTION_LED_NAME, FALSE);

		if (retval != FAILED)
		{
			*state = retval;
		}
	}

	if (retval != FAILED) 
	{
		LOG_TRACE("Attention LED state is %s\n", is_on ? "on" : "off");
	}

	LOG_ERROR;

	return ((retval < 0) ? FAILED : SUCCESS);
}

/******************************************************************************
*   Function Name: lib_getversion
*   Purpose:  Return library version
*   Comments/Notes:
*******************************************************************************/
int ocs_gpio_libgetversion(u_int32_t *ver)
{
    *ver = VERSION_MAKEWORD(SOLIB_VERSION_MAJOR, 
                            SOLIB_VERSION_MINOR, 
                            SOLIB_VERSION_REVISION, 
                            SOLIB_VERSION_BUILD);
    
    return (SUCCESS);
}
