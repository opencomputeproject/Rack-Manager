# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import * 

def set_server_default_powerstate(serverid, state):
    if (state == "On"):
        return set_server_default_powerstate_on (serverid)
    elif (state == "Off"):
        return set_server_default_powerstate_off (serverid)
    else:
        return set_failure_dict ("Invalid default power state argument {0}.".format (state),
            completion_code.failure)
        
def set_server_default_powerstate_on(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)

        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis policy always-on'  # IPMI  command to set server default power state on
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_default_powerstate_on = parse_set_server(cmdinterface, "setserverdefaultpowerstateon", 'on')
        
        if set_default_powerstate_on is None or not set_default_powerstate_on: # Check empty or none
            return set_failure_dict("Empty data for setserverdefaultpowerstateon",completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_default_powerstate_on 

def set_server_default_powerstate_off(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid) 
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis policy always-off' # IPMI  command to set server default power state off
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_default_powerstate_off = parse_set_server(cmdinterface, "setserverdefaultpowerstateoff", 'off')
        
        if set_default_powerstate_off is None or not set_default_powerstate_off: # Check empty or none
            return set_failure_dict("Empty data for setserverdefaultpowerstateoff", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_default_powerstate_off

def get_server_default_powerstate(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis status' #IPMI command to get server status
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        get_default_powerstate = parse_get_serverdefault(cmdinterface, "getserverdefaultpowerstate")
        
        if get_default_powerstate is None or not get_default_powerstate: # Check empty or none
            return set_failure_dict("Empty data for getserverdefaultpowerstate", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return get_default_powerstate

def get_server_state(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis status' #IPMI command to get server status
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        server_state = parse_get_serverdefault(cmdinterface, "getserverstate")
        
        if server_state is None or not server_state: # Check empty or none
            return set_failure_dict("Empty data for getserverdefaultpowerstate", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return server_state

def set_server_on(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid) 
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis power on' #IPMI command to set server on
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_server_on = parse_set_server(cmdinterface, "setserveron" , 'on' )
        
        if set_server_on is None or not set_server_on: # Check empty or none
            return set_failure_dict("Empty data for setserveron", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_server_on

def set_server_off(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid) 
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis power off' #IPMI command to set server off
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_server_off = parse_set_server(cmdinterface, "setserveroff" , 'off' )
        
        if set_server_off is None or not set_server_off: # Check empty or none
            return set_failure_dict("Empty data for setserveroff", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_server_off

def set_server_active_power_cycle(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)  
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'chassis power cycle ' #IPMI command to set server active powercycle interval
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_active_cycle = parse_set_server(cmdinterface, "setserveractivepowercycle" , 'cycle')
        
        if set_active_cycle is None or not set_active_cycle: # Check empty or none
            return set_failure_dict("Empty data for setserveractivepowercycle", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_active_cycle

def get_server_attention_led_status(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure) 
        
        
        ipmi_cmd = 'ocsoem getledstatus' # IPMI command to get server attantion LED status
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        get_attention_led = parse_set_server_attentionled(cmdinterface, "getserverattentionledstatus")
        
        if get_attention_led is None or not get_attention_led: # Check empty or none
            return set_failure_dict("Empty data for getserverattentionledstatus", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return get_attention_led

def set_server_attention_led (serverid, state):
    if (state == 1):
        return set_server_attention_led_on (serverid)
    elif (state == 0):
        return set_server_attention_led_off (serverid)
    else:
        return set_failure_dict ("Invalid attention LED state argument {0}.".format (state),
            completion_code.failure)
        
def set_server_attention_led_on(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'raw 0x00 0x04 0x00 0x01' # IPMI raw command to set server attantion LED on
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_attention_led = parse_set_server_attentionled(cmdinterface, "setserverattentionledon")
        
        if set_attention_led is None or not set_attention_led: # Check empty or none
            return set_failure_dict("Empty data for setserverattentionledon", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_attention_led

def set_server_attention_led_off(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'raw 0x00 0x04 0x00 0x00' # IPMI raw command to set server attantion LED off
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_attention_led = parse_set_server_attentionled(cmdinterface, "setserverattentionledoff")
        
        if set_attention_led is None or not set_attention_led: # Check empty or none
            return set_failure_dict("Empty data for setserverattentionledoff", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return set_attention_led

# Parse setserverdefaultpowerstateon setserverdefaultpowerstateoff, setserveron, setserveroff , Setserveractivepowercycle output
def parse_set_server(interface, command, state):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        set_power_state = {}
        
        if(output['status_code'] == 0):
                power_state_data  = output['stdout'].split('\n')
                powerstate =  power_state_data.pop(0)

                if 'Chassis Power Control' in powerstate:
                    power_control_state = powerstate.split(":")[-1]
                    # get server state value for SetserverOn and SetserverOff Example output : Chassis Power Control: Up/On || Chassis Power Control: Up/Off
                    if '/' in power_control_state:
                        server_powerstate = powerstate.split('/') 
                        serverstate = server_powerstate[1]                        
                        set_power_state["State"] = serverstate.upper()
                    else:
                        # get power cycle value for "Setserveractivepowercycle" Example output : Chassis Power Control: Cycle
                        #setPowerState["PowerCycle"] = powerControlState
                        serverstate = power_control_state
                        
                elif 'Set chassis power restore policy to' in powerstate:
                    power_restore = powerstate.split(":")[-1]
                    # get server state value for setserverdefaultpowerstateon and setserverdefaultpowerstateoff
                    if '-' in power_restore: # Example Powestate : Set chassis power restore policy to : always-on || Set chassis power restore policy to : always-off
                        server_power_state = powerstate.split('-')
                        serverstate = server_power_state[1]
                        set_power_state["Default Power State"] = serverstate.upper()
                     
                if(serverstate.strip().upper() == state.strip().upper()):
                    set_power_state[completion_code.cc_key] = completion_code.success
                else:
                    set_power_state[completion_code.cc_key] = completion_code.failure                     
                  
                return set_power_state        
        else:
            error_data = output['stderr']            
            set_power_state[completion_code.cc_key] = completion_code.failure            
            set_power_state[completion_code.desc] = error_data.split(":")[-1]
                                                  
            return set_power_state       
        
    except Exception, e:
        #log.exception("serverPowerState Command: %s Exception error is: %s ", command, e)
        #print "Exception: ", e      
        return set_failure_dict(("serverPowerState: Exception ",e) , completion_code.failure) 

def parse_get_serverdefault(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        get_default_powerstate = {}
        
        if(output['status_code'] == 0):
                power_state_data  = output['stdout'].split('\n') 
                 
                for powerpolicy in power_state_data:
                    if "Power Restore Policy" in powerpolicy and command == "getserverdefaultpowerstate":
                        powerpolicy = powerpolicy.split(":")[-1]
                        state = powerpolicy.split('-')[-1].strip ()
                        get_default_powerstate["Default Power State"] = state.upper()
                        break 
                    elif "System Power" in powerpolicy and command == "getserverstate":
                        powerpolicy = powerpolicy.split(":")[-1].strip ()
                        get_default_powerstate["State"] = powerpolicy.upper()
                        break
                
                get_default_powerstate[completion_code.cc_key] = completion_code.success                        
                return get_default_powerstate     
        else:
            error_data = output['stderr']            
            get_default_powerstate[completion_code.cc_key] = completion_code.failure            
            get_default_powerstate[completion_code.desc] = error_data.split(":")[-1]
                                                  
            return get_default_powerstate       
        
    except Exception, e:
        #log.exception("GetserverDefaultPowerState: %s Exception error is: %s ", command, e)
        return set_failure_dict(("Exception",e)  , completion_code.failure) 

def parse_set_server_attentionled(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        set_attention_led = {}
        
        if(output['status_code'] == 0):
                set_attention_led[completion_code.cc_key] = completion_code.success   
                if "led status" in output['stdout'].lower() and command == "getserverattentionledstatus":
                    led_status = output['stdout'].split(":")[-1].split('\n')
                    set_attention_led["LED Status"] = led_status[0]
                    
                return set_attention_led        
        else:
            error_data = output['stderr']            
            set_attention_led[completion_code.cc_key] = completion_code.failure            
            set_attention_led[completion_code.desc] = error_data.split(":")[-1]
                                                  
            return set_attention_led       
        
    except Exception, e:
        #log.exception("SetserverAttentionLED: %s Exception error is: %s ", command, e)
        #print "Exception: ", e      
        return set_failure_dict(("SetserverAttentionLED: ParseResult() Exception" ,e),completion_code.failure)         

