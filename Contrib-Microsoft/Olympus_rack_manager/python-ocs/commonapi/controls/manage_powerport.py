# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import ocslog

from utils import *
from lib_utils import get_gpio_library
from ctypes import *


############################################################################################################
# Port Status Functions 
############################################################################################################
def powerport_get_port_status(port_id, port_type, raw = False):
    """ Get port status
    """
    
    try:
        gpio_binary = get_gpio_library ()
        
        output = {}
        
        i = c_long()
        j = c_int()
        
        if (port_id < 1) or (port_id > 48):
            return set_failure_dict("Invalid port-id {0}. Expected {1, 48}".format(port_id),
                                     completion_code.failure)   
                
        if port_type == "pdu":
            output = gpio_binary.ocs_port_state(port_id, byref(i))
            
            if (output == 0):
                if (i.value == 1):
                    if raw:
                        return set_success_dict({port_id: "On"})
                    else:
                        return set_success_dict({"Port State": "On"})
                else:
                    if raw:
                        return set_success_dict({port_id: "Off"})
                    else:
                        return set_success_dict({"Port State": "Off"})
            else:
                return set_failure_dict(("Failed to get port status from GPIO Library: {0}".format(output)), 
                                        completion_code.failure)
            
        elif port_type == "relay":
            output = gpio_binary.ocs_port_relay(port_id, 2, byref(j))
            
            if (output == 0):
                if (j.value == 1):
                    return set_success_dict({"Relay": "On"})
                else:
                    return set_success_dict({"Relay": "Off"})
            else:
                return set_failure_dict(("Failed to get relay status from GPIO Library: {0}".format(output)), 
                                        completion_code.failure)
        
    except Exception,e:      
        return set_failure_dict("powerport_get_port_status - Exception: {0}".format(e), completion_code.failure)

def powerport_get_row_boot_strap (port_id, raw = False):
    """ Get boot strapping setting
    """
    
    result = powerport_get_port_status (port_id + 24, "pdu", raw)
    state = result.pop ("Port State", None)
    
    if (state):
        result["Boot Strap"] = "Normal" if (state == "Off") else "Network"
        
    return result

def powerport_get_all_port_status(raw = False, ports = range (0, 48)):
    """ Get all 48 blades' statuses
    """ 
    
    try:    
        output = {}
            
        gpio_binary = get_gpio_library()
            
        presence = c_longlong()
        port_id = c_int(int(0))
            
        rc = gpio_binary.ocs_port_state(port_id, byref(presence))
            
        if rc == 0:
            for i, j in enumerate (ports):
                if (((presence.value >> j) & 1) == 1):
                    result = "ON"
                else:
                    result = "OFF"
                                        
                if raw:
                    output.update({(i + 1): result})
                else:        
                    result = set_success_dict({"Port State" :result})
                    result = ({(i + 1): result})
                    output.update(result) 
            
        if raw:
            return set_success_dict(output)
        else:
            return output
            
    except Exception,e:      
        return set_failure_dict("powerport_get_all_port_status - Exception: {0}".format(e), completion_code.failure) 

############################################################################################################
# Port Presence Functions 
############################################################################################################
def powerport_get_port_presence(port_id, port_type, raw = False):
    """ Get port presence
    """
        
    try:
        if port_type == "relay":
            return set_success_dict({"Port Presence": "True"})
        
        gpio_binary = get_gpio_library()
        
        output = {}
        
        i = c_long()
        
        if (port_id < 1) or (port_id > 48):
            return set_failure_dict("Invalid port-id {0}. Expected {1, 48}".format(port_id), 
                                    completion_code.failure)

        output = gpio_binary.ocs_port_present(port_id, byref(i))
        
        if output == 0:
            if (i.value == 1):
                if raw:
                    return set_success_dict({port_id: "True"})
                else:
                    return set_success_dict({"Port Presence": "True"})
            else:
                if raw:
                    return set_success_dict({port_id: "False"})
                else:
                    return set_success_dict({"Port Presence": "False"})
        else:
            #Log_Info(Failed to get port presence)            
            return set_failure_dict(("Failed to get port presence from GPIO Library: {0}".format(output)), 
                                        completion_code.failure)
        
    except Exception, e:
        #log_error ("Exception :",e)      
        return set_failure_dict("powerport_get_port_presence - Exception: {0}".format(e), completion_code.failure)         

def powerport_get_row_port_presence (port_id, raw = False):
    """ Get row port presence.
    """
    
    return powerport_get_port_presence (port_id + 24, "pdu", raw)

def powerport_get_all_port_presence(raw = False, ports = range (0, 48)):
    """ Get all 48 blades' presence
    """ 
    
    try:    
        output = {}
            
        gpio_binary = get_gpio_library()
            
        presence = c_longlong()
        port_id = c_int(int(0))
            
        rc = gpio_binary.ocs_port_present(port_id, byref(presence))
            
        if rc == 0:
            for i, j in enumerate (ports):
                if (((presence.value >> j) & 1) == 1):
                    result = "True"
                else:
                    result = "False"
                                        
                if raw:
                    output.update({(i + 1): result})
                else:        
                    result = set_success_dict({"Port Presence" :result})
                    result = ({(i + 1): result})
                    output.update(result) 
            
        if raw:
            return set_success_dict(output)
        else:
            return output
            
    except Exception,e:      
        return set_failure_dict("powerport_get_all_port_presence - Exception: {0}".format(e), completion_code.failure)               
    
############################################################################################################
# Reset actions Functions 
###########################################################################################################
def powerport_set_system_reset(port_id, action_type, port_type):
    """ Turn power port on/off through GPIO shared library
    """
    
    try:
        gpio_binary = get_gpio_library ()
         
        action = 1
        output = ''
        j = c_int()
        
        if (port_id < 1) or (port_id > 48):
            return set_failure_dict("Invalid port-id {0}. Expected {1, 48}".format(port_id), 
                                    completion_code.failure) 
        
        if action_type.lower() == 'on': 
            action = 1  
        else:    
            action = 0
        
        if port_type.lower() == "pdu":
            output = gpio_binary.ocs_port_control(port_id, action)  
            
        elif port_type.lower() == "relay":            
            output = gpio_binary.ocs_port_relay(port_id, action, byref(j)) 
            
        if (output == 0):
            return set_success_dict()
        else:
            #log_err
            return set_failure_dict(("Failed to reset system using GPIO Library: {0}".format(output)), 
                                    completion_code.failure)      
        
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("powerport_set_system_reset - Exception: {0}".format(e), 
                                completion_code.failure)

def powerport_set_row_boot_strapping (port_id, strapping):
    """ Change the boot strapping for a row manager port.
    """
    
    if (strapping.lower () == "network"):
        action = "on"
    elif (strapping.lower () == "normal"):
        action = "off"
    else:
        return set_failure_dict ("Invalid boot strapping option: {0}".format (strapping))
    
    return powerport_set_system_reset (port_id + 24, action, "pdu")