# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import os
import sys

from pre_settings import *
from utils_print import print_response
from controls.manage_user import *
from controls.manage_network import *
from controls.manage_powerport import *
from controls.manage_powermeter import *
from controls.manage_rack_manager import *
from controls.bladeinfo_lib import *
from controls.bladenextboot_lib import *
from controls.bladepowerstate_lib import *
from controls.sys_works import *

cmstatus = "Running"

def wcs_set_establishcmconnection(version):
    """ Prints chassis manager service assembly version
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:
        if version:
            result = fru_Info()
            
            if check_success(result):
                print "WCSCLI version: {0}".format(result["Firmware Version"])
            else:
                print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            print "Attemting connection to CM service..."
            print "Connection to CM succeeded."
            print ""
                                            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_establishcmconnection: Exception {0}".format(e), 
                                        completion_code.failure))
    
def wcs_set_terminatecmconnection():
    """ Spoofs a terminatecmconnection command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    print "Connection to CM terminated successfully."

def wcs_set_disablechassismanagerssl():
    """ Spoofs a disablechassismanagerssl command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    global cmstatus

    if cmstatus == "Stopped":
        print "ChassisManager service is already stopped."
    else:
        print "Stopping the ChassisManager service ..."
    
    
    print "Update EnableSslEncryption flag in ChassisManager config"
    print "Starting the ChassisManager service ..."
    print "Command Success: Successfully disabled SSL in the ChassisManager service."
    print ""
    print "You will need to establish connection to the CM again using the establishCmConnection command to run any CM service commands."
    
    cmstatus = "Running"

def wcs_set_enablechassismanagerssl():
    """ Spoofs a enablechassismanagerssl command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    global cmstatus

    if cmstatus == "Stopped":
        print "ChassisManager service is already stopped."
    else:
        print "Stopping the ChassisManager service ..."
    
    
    print "Update EnableSslEncryption flag in ChassisManager config"
    print "Starting the ChassisManager service ..."
    print "Command Success: Successfully enabled SSL in the ChassisManager service."
    print ""
    print "You will need to establish connection to the CM again using the establishCmConnection command to run any CM service commands."
    
    cmstatus = "Running"
        
def wcs_get_chassismanagerstatus():
    """ Spoofs a getchassismanagerstatus command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    print "Command Success: ChassisManager service status: {0}".format(cmstatus)

def wcs_set_stopchassismanager():
    """ Spoofs a stopchassismanager command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    global cmstatus

    if cmstatus == "Stopped":
        print "ChassisManager service is already stopped.\nCommand Failed."
        return
    
    cmstatus = "Stopped"
    print "Stopping the ChassisManager service ...\nCommand Success: ChassisManager service successfully stopped."

def wcs_set_startchassismanager():
    """ Spoofs a startchassismanager command
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    global cmstatus

    if cmstatus == "Running":
        print "ChassisManager service is already running.\nCommand Failed."
        return
    
    cmstatus = "Running"
    print "Starting the ChassisManager service ...\nCommand Success: ChassisManager service successfully started."

def wcs_set_nic(source, addr = None, subnet = None, gateway = None, pdns = None, sdns = None, nic = 0):
    """ Sets NIC properties
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        if source == "static":
            result = set_static_interface("eth" + str(nic), addr, subnet, gateway)
            
            if check_success(result):
                print_response(set_success_dict())
            else:
                print_response(set_failure_dict(result[completion_code.desc], completion_code.failure))        
        elif source == "dhcp":
            result = set_dhcp_interface("eth" + str(nic))
            
            if check_success(result):
                print "Command Success"
            else:
                print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_nic: Exception {0}".format(e), 
                                        completion_code.failure))
    
def wcs_get_serviceversion():
    """ Prints chassis manager service assembly version
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:
        result = fru_Info()
        
        if check_success(result):
            print "Command Success: Chassis Manager Service version: {0}".format(result["Firmware Version"])
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                                            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_serviceversion: Exception {0}".format(e), 
                                        completion_code.failure))

def wcs_get_nic(chassisinfo = False):
    """ Prints chassis controller network properties
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:        
        description = {"eth0": "Datacenter Network Connection", 
                       "eth1": "Management Network Connection"}       

        result = display_cli_interfaces()
                
        if check_success(result):
            for (index, interface) in result["Interfaces_list"].items():
                if interface not in description:
                    desc = "Unknown"
                    
                try:
                    if get_address_origin(interface) == "DHCP":
                        dhcp_enabled = "True"
                    else:
                        dhcp_enabled = "False"
                except RuntimeError:
                    dhcp_enabled = "False"
                    pass
                                                
                print "N/W Interface {0}:".format(index)
                print "         Index                : {0}".format(interface[-1])
                print "         Description          : {0}".format(interface)
                print "         ServiceName          :"
                print "         MAC Address          : {0}".format(get_mac_ifconfig(interface).strip())
                print "         IP Enabled           : True"
                print "         DHCP Enabled         : {0}".format(dhcp_enabled)
                print "         DHCP Server          :"
                print "         IP Address           : {0}, {1}".format(get_ip_address(interface), 
                                                                        get_IPV6(interface).strip())
                print "         Subnet Mask          : {0}".format(get_subnetmask_ifconfig(interface))
                print "         Gateway Address      : {0}".format(get_default_gateway())
                print "         DNS Servers          :"
                print "         DNS Hostname         :"
                print "         DNS Domain           :"
                print "         WNS Primary          :"
                print "         WNS Secondary        :"
                print "         Completion Code      : Success"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        
        if(not chassisinfo):
            print ""
            print "Completion Code: Success"
    
    except Exception, e:
        print_response(set_failure_dict("wcs_get_nic: Exception {0}".format(e), 
                                        completion_code.failure))
def wcs_set_userremove(username):
    """ Remove chassis controller user with specified username
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:               
        result = user_delete_by_name(username)

        if check_success(result):
            print "Command Success: Chassis Manager User Removed"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_set_userremove: Exception {0}".format(e), 
                                        completion_code.failure))

def wcs_set_userupdate(username, password, role):
    """ Update chassis controller user password or role
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:               
        if password is not None:
            result = user_update_password(username, password)
    
            if check_success(result):
                print "Command Success: Chassis Manager User Password Changed"
            else:
                print "Command Failed. Error: {0}".format(result[completion_code.desc])
        if role is not None:
            result = user_update_role(username, role)
    
            if check_success(result):
                print "Command Success: Chassis Manager User Role Changed"
            else:
                print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_set_userupdate: Exception {0}".format(e), 
                                        completion_code.failure))

def wcs_set_usercreate(username, pwd, role):
    """ Adds new chassis controller user with specified role and password
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:               
        result = user_create_new(username, pwd, role)

        if check_success(result):
            print "Command Success: Chassis Manager User Added"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_set_usercreate: Exception {0}".format(e), 
                                        completion_code.failure))

def wcs_get_chassisled():
    """ Get chassis manager attention led status
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        result = get_rack_manager_attention_led_status()

        if check_success(result):
            print "Command Success: Chassis LED: {0}".format(result["Manager LED Status"])
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_get_chassisled: Exception {0}".format(e), completion_code.failure))

def wcs_set_chassisled(state):
    """ Set chassis manager attention led on/off
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state not in (0, 1):
            print_response(set_failure_dict("Unknown state: {0}".format(state), completion_code.failure))
            return
        
        result = set_rack_manager_attention_led(state)

        if check_success(result):
            print "Command Success: Command Completed"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_set_chassisled: Exception {0}".format(e), completion_code.failure))


def wcs_set_acsocketpowerstate(port_id, state):
    """ Set state for chassic AC sockets
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state.lower() not in ("on", "off"):
            print_response(set_failure_dict("Unknown state: {0}".format(state), completion_code.failure))
            return
        
        result = powerport_set_system_reset(port_id, state.lower(), "relay")

        if check_success(result):
            print "Command Success: ACSocket {0} Power State: {1}".format(port_id, state.upper())
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_set_acsocketpowerstate: Exception {0}".format(e), completion_code.failure))

def wcs_get_acsocketpowerstate(port_id):
    """ Print status of chassis AC sockets
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        state = powerport_get_port_status(port_id, "relay", True)
                
        if check_success(state):
            print "Command Success: ACSocket {0} Power State: {1}".format(port_id, state["Relay"].upper())
        else:
            print "Command Failed. Error: {0}".format(state[completion_code.desc])
                        
    except Exception, e:
        print_response(set_failure_dict("wcs_get_acsocketpowerstate: Exception {0}".format(e), completion_code.failure))


def wcs_set_startserialsession(device_id):
    """ Start a serial session to a blade
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        result = server_start_serial_session(device_id)
                    
        if check_success(result):
            print "Serial session to blade started successfully"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_startserialsession: Exception {0}".format(e), completion_code.failure))
        
def wcs_set_stopserialsession(device_id):
    """ Terminates active serial session to a blade
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        result = server_stop_serial_session(device_id)
                    
        if check_success(result):
            print "Active serial session to blade terminated successfully"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_stopserialsession: Exception {0}".format(e), completion_code.failure))
        
def wcs_set_bladeactivepowercycle(device_id):
    """ Power cycles or soft resets the blades
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:      
            result = set_server_active_power_cycle(id)
                        
            if check_success(result):
                print "Command Success: Blade {0}: Command Completed.".format(id)
            else:
                print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladeactivepowercycle: Exception {0}".format(e), 
                                        completion_code.failure))


def wcs_get_nextboot(device_id):
    """ Gets next boot type
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        result = get_nextboot(device_id)
        
        if "BootSourceOverrideEnabled" in result and "Next boot is" in result and "BootSourceOverrideMode" in result:
            if result["BootSourceOverrideEnabled"] == "Once" and check_success(result):
                persistence = "False"
            else:
                persistence = "True" 
            
            if result["BootSourceOverrideMode"] == "Legacy":
                uefi = "False"
            else:
                uefi = "True"
                        
            print "Command Success: \nNext Boot Device: {0}. Persistence: {1}. UEFI: {2}. Boot Instance: 0x0".format(
                result["Next boot is"].strip(), persistence, uefi)
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
    except Exception, e:
        print_response(set_failure_dict("wcs_get_nextboot: Exception {0}".format(e), completion_code.failure))

def wcs_set_nextboot(device_id, boot_type, mode, persistence):
    """ Sets next boot type
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        boot_options = ['none','pxe','disk','bios','floppy']
        index = int(boot_type) - 1
        
        result = set_nextboot(device_id, boot_options[index], mode, persistence)

        if check_success(result):
            wcs_get_nextboot(device_id)
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_nextboot: Exception {0}".format(e), completion_code.failure))

def wcs_get_bladepowerreading(device_id):
    """ Prints blade power consumption
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:      
            result = get_server_power_reading(id)
            
            if check_success(result):
                print "Command Success: Blade {0}: Power Reading: {1} Watts".format(id, result["PowerReadingWatts"])
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladepowerreading: Exception {0}".format(e), completion_code.failure))
        
def wcs_get_bladepowerlimit(device_id):
    """ Prints blade static power limit
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:      
            result = get_server_power_limit(id)
            
            if check_success(result):
                if result["StaticState"] == "No Active Power Limit":
                    state = "Not active"
                elif result["StaticState"] == "Power Limit Active":
                    state = "Active"
                else:
                    state = result["StaticState"]
                
                print "Command Success: Blade {0}: Power Limit: {1}, {2}".format(id, result["StaticLimit"], state)
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladepowerlimit: Exception {0}".format(e), completion_code.failure))

def wcs_set_bladepowerlimit(device_id, powerlimit):
    """ Set blade power limit
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
            
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:       
            result = ""
            
            result = set_server_power_limit(id, powerlimit)
                
            if check_success(result):
                print "Command Success: Blade {0}: Power Limit Set".format(id)
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladepowerlimit: Exception {0}".format(e), completion_code.failure))

def wcs_set_bladepowerlimitstate(device_id, state):
    """ Set blade power limit on/off
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state.lower() not in ("on", "off"):
            print "Command Failure: Blade {0}: Completion Code: Unknown state {1}".format(device_id, state)
            return
                    
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
            
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:       
            result = ""
            
            if state.lower() == "off":
                result = set_server_power_limit_off(id)
            elif state.lower() == "on":
                result = set_server_power_limit_on(id)
                
            if check_success(result):
                print "Command Success: Blade {0}: Power Limit {1}".format(id, state.upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladepowerlimitstate: Exception {0}".format(e), completion_code.failure))

def wcs_get_bladedefaultpowerstate(device_id):
    """ Prints blade default power state
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:      
            result = get_server_default_powerstate(id)
                        
            if check_success(result):
                print "Command Success: Blade {0}: Default Power State: {1}".format(id, result["Default Power State"])
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladepowerlimit: Exception {0}".format(e), completion_code.failure))

def wcs_set_bladedefaultpowerstate(device_id, powerstate):
    """ Set blade power limit
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if powerstate == 1:
            state = "On"
        elif powerstate == 0:
            state = "Off"
        else:
            print "Command Failure: Blade {0}: Completion Code: Unknown power state {1}".format(device_id, powerstate)
            return
        
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
            
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:       
            result = ""
            
            result = set_server_default_powerstate(id, state)
                
            if check_success(result):
                print "Command Success: Blade {0}: {1}".format(id, state.upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladepowerlimit: Exception {0}".format(e), completion_code.failure))
        
def wcs_set_bladeattentionledstate(device_id, state):
    """ Set blade attention led on/off
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state not in (0, 1):
            print "Command Failure: Blade {0}: Completion Code: Unknown state {1}".format(device_id, state)
            return
                    
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
            
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:       
            result = ""
            
            result = set_server_attention_led(id, state)
                
            if state == 1:
                pstate = "ON"
            else:
                pstate = "OFF"
                
            if check_success(result):
                print "Command Success: Blade {0}: Attention LED {1}".format(id, pstate)
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladeattentionledstate: Exception {0}".format(e), completion_code.failure))

def wcs_get_bladestate(device_id):
    """ Prints whether blade chipset is receiving power
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:      
            state = get_server_state(id)
            
            if check_success(state):
                print "Command Success: Blade State {0}: {1}".format(id, state["State"].upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, state[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladestate: Exception {0}".format(e), completion_code.failure))

def wcs_set_bladestate(device_id, state):
    """ Control power to blades' chipset
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state.lower() not in ("on", "off"):
            print "Command Failure: Blade {0}: Completion Code: Unknown state {1}".format(device_id, state)
            return
                    
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
            
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:       
            result = ""
            
            if state.lower() == "off":
                result = set_server_off(id)
            elif state.lower() == "on":
                result = set_server_on(id)
                
            if check_success(result):
                print "Command Success: Blade {0}: {1}".format(id, state.upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_bladestate: Exception {0}".format(e), completion_code.failure))

def wcs_set_powerstate(device_id, state):
    """ Set power state for blades
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if state.lower() not in ("on", "off"):
            print "Command Failed. Blade {0}: Completion Code: Unknown state {1}".format(device_id, state)
            return
        
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
        
        id = port_range[0]
        
        if id == -1:
            print "Command Failed. Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
            
        while id <= port_range[1]:                           
            result = powerport_set_system_reset(id, state.lower(), "pdu")

            if check_success(result):
                print "Command Success: Blade {0}: {1}".format(id, state.upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_set_poweroff: Exception {0}".format(e), completion_code.failure))

def wcs_get_powerstate(device_id):
    """ Print blade power state information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
                    
        id = port_range[0]
        
        if id == -1:
            print "Command Failure: Blade {0}: Completion Code: Unknown mode {1}".format(id, mode)
            return
        
        while id <= port_range[1]:                           
            state = powerport_get_port_status(id, "pdu", True)
            
            if check_success(state):
                print "Blade Active Power State {0}: {1}".format(id, state[id].upper())
            else:
                print "Command Failed. Blade {0}: Completion Code: {1}".format(id, result[completion_code.desc])
            
            id = id + 1
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_powerstate: Exception {0}".format(e), completion_code.failure))

def print_blade_info(output):
    """ Print blade information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    
    try:
        print ""
        print "== Compute Node Info =="
        print "BMC Firmware Version   : {0}".format(output["FWVersion"])
        print "BIOS Version           : {0}".format(output["BIOSVersion"])
        print "CPLD Version           : {0}".format(output["CPLDVersion"])
        print "Hardware Version       : {0}".format(output["HWVersion"])
        print "Serial Number          : {0}".format(output["SerialNum"])
        print "Asset Tag              : {0}".format(output["AssetTag"])
        print ""
        print "== MAC Address =="
        print "Device Id              : {0}".format(output["DeviceID"])
        print "MAC Address            : {0}".format(output["MACAddress"])
        print ""
        
    except Exception, e:
        print_response(set_failure_dict("print_blade_info: Exception {0}".format(e), completion_code.failure))

def wcs_get_bladeinfo(device_id):
    """ Print blade information
    """
    
    try:       
        if device_id == 0:
            mode = get_mode()
            port_range = system_range(mode)
        else:
            port_range = (device_id, device_id)
        
        id = port_range[0]
        
        if id == -1:
            print_response(set_failure_dict("Unknown mode: {0}".format(mode), completion_code.failure))
            return
        
        while id <= port_range[1]:                           
            info = system_info_call(id)
                        
            if check_success(info):
                output = {}
                
                output["FWVersion"] = info["Server"]["BMCVersion"]
                output["BIOSVersion"] = info["Server"]["BiosVersion"]
                output["CPLDVersion"] = info["Server"]["CpldVersion"]
                output["HWVersion"] = info["Server"]["HWVersion"]
                output["SerialNum"] = info["SerialNumber"]
                output["AssetTag"] = info["AssetTag"]
                output["DeviceID"] = id
                output["MACAddress"] = get_server_mac(id)
                
                if output["MACAddress"] == "Failure":
                    output["MACAddress"] = "--"
                
                print_blade_info(output)
            else:
                print "Command Failed. Error: {0}".format(info[completion_code.desc])
            
            id = id + 1
                
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladeinfo: Exception {0}".format(e), completion_code.failure))

def wcs_get_bladehealth(device_id, cpu, memory, pcie, sensor, temp, fru):
    """ Print blade health information
    """
    try:
        mode = get_mode()
        result = server_info(mode, False, device_id)

        if check_success(result):
            print ""
            print "== Blade {0} Health Information ==".format(device_id)
            print "Blade ID          : {0}".format(device_id)
            print "Blade State       : {0}".format(result[device_id]["Port State"]).upper()
            print "Blade Type        : {0}".format(result[device_id]["Type"])
            print ""    
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        
        if cpu:
            show_blade_cpu_health(device_id)
        elif memory:
            show_blade_memory_health(device_id)
        elif pcie:
            show_blade_pcie_health(device_id)
        elif sensor:
            show_blade_sensor_health(device_id)
        elif temp:
            show_blade_temp_health(device_id)
        elif fru:
            show_blade_fru_health(device_id)
        else:
            show_blade_cpu_health(device_id)
            show_blade_memory_health(device_id)
            show_blade_pcie_health(device_id)
            show_blade_sensor_health(device_id)
            show_blade_temp_health(device_id)
            show_blade_fru_health(device_id)
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_bladeheatlh: Exception {0}".format(e), completion_code.failure))

def wcs_get_chassishealth(server, psu):
    """ Print chassis information
    """
    try:
        if server:
            show_server_health()
        elif psu:
            show_psu_health()
        else:
            show_server_health()
            show_psu_health()
        
        print "Completion Code : Success"
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_chassishealth: Exception {0}".format(e), completion_code.failure))

def show_server_health(id = 0):
    """ Get and display server health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try: 
        mode = get_mode()
        result = server_info(mode, True, id)
        
        print ""
        print "== Blade Health =="        
        if check_success(result):            
            for (ks, vs) in result.items():
                if "Type" in vs and "Port State" in vs and "Port Id" in vs:
                    print "Blade Id               : {0}".format(vs["Port Id"])
                    print "Blade State            : {0}".format(vs["Port State"])
                    print "Blade Type             : {0}".format(vs["Type"])
                    print "Blade Completion Code  : Success"
                    print ""
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("show_server_health: Exception {0}".format(e), completion_code.failure))

def show_psu_health():
    """ Get and display PSU health information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = get_rack_power_reading()
        print ""
        print "== PSU Health =="
        if check_success(result):
            print "Psu Id                : 1"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed1Phase1PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
            print "Psu Id                : 2"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed1Phase2PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
            print "Psu Id                : 3"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed1Phase3PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
            print "Psu Id                : 4"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed2Phase1PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
            print "Psu Id                : 5"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed2Phase2PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
            print "Psu Id                : 6"
            print "Psu Serial Number     :"
            print "Psu State             : ON"
            print "PSU Power Out         : {0}".format(result["Feed2Phase3PowerInWatts"])
            print "Psu Completion Code   : Success"
            print ""
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("show_psu_health: Exception {0}".format(e), completion_code.failure))

def wcs_get_chassisinfo(server, rm, psu, battery):
    """ Print chassis information
    """
    try:
        if server:
            show_server_information()
        elif rm:
            show_rm_information()
            wcs_get_nic(True)
        elif psu:
            show_psu_information()
        elif battery:
            show_battery_information()
        else:
            show_server_information()
            show_psu_information()
            show_battery_information()
            show_rm_information()
            wcs_get_nic(True)
        
        print "Completion Code : Success"
            
    except Exception, e:
        print_response(set_failure_dict("wcs_get_chassisinfo: Exception {0}".format(e), completion_code.failure))

def show_server_information(id = 0):
    """ Get and display server information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try: 
        mode = get_mode()
        result = server_info(mode, True, id)
                
        print ""
        print "== Compute Nodes =="
        if check_success(result):
            print "{:^2} | {:^7} | {:^36} | {:^7} | {:^70}  | {:^3}".format('#','Name','GUID','State','BMC MAC', "Completion Code")
            
            for (ks, vs) in result.items():
                if "GUID" in vs and "Port State" in vs and "MAC" in vs and "Present" in vs:
                    if vs["MAC"] == "Failure":
                        vs["MAC"] = "--"
                    if vs["Present"] == "True":
                        status = completion_code.success
                        vs["MAC"] = "DeviceID: 1 MAC Address: {0} | Device ID: 2 MAC Address: --".format(vs["MAC"])
                    else:
                        vs["GUID"] = "00000000-0000-0000-0000-000000000000"
                        status = "Timeout"
                        vs["Power State"] = "--"
                    print "{0:^2} | BLADE{0:^2} | {1:^36} |   {2:^3}   |  {3:^70} | {4:^15}".format(ks,
                                                                                                  vs["GUID"].lower(), 
                                                                                                  vs["Port State"].title(),
                                                                                                  vs["MAC"],
                                                                                                  status)
            print ""
            print "Highest Blade Inlet Temperature (C): 24"
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("show_server_information: Exception {0}".format(e), completion_code.failure))

def show_psu_information():
    """ Get and display PSU information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = get_rack_power_reading()
        print ""
        print "== Power Supplies =="
        if check_success(result):
            print "{:^1} | {:^6} | {:^6} | {:^1} | {:^6}".format('#','Serial Number','State','Pout (W)', "Completion Code")                        
            print "1 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed1Phase1PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print "2 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed1Phase2PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print "3 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed1Phase3PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print "4 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed2Phase1PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print "5 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed2Phase2PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print "6 |       --      |   On   | {0:^8} | {1:^2} ".format(int(result["Feed2Phase3PowerInWatts"]),
                                                                result[completion_code.cc_key])
            print ""
        else:
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
            
    except Exception, e:
        print_response(set_failure_dict("show_psu_information: Exception {0}".format(e), completion_code.failure))
        
def show_battery_information():
    """ Spoof battery information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        print ""
        print "== Batteries =="
        print "{:^1} | {:^6} | {:^6} | {:^1} | {:^6} | {:^6}".format('#','Present','Pout (W)','Charge (%)', 
                                                             'Fault Status', "Completion Code")                        
        print "1 |    0    |    0     |     0      |     0x0      |    Success"
        print "2 |    0    |    0     |     0      |     0x0      |    Success"
        print "3 |    0    |    0     |     0      |     0x0      |    Success"
        print "4 |    0    |    0     |     0      |     0x0      |    Success"
        print "5 |    0    |    0     |     0      |     0x0      |    Success"
        print "6 |    0    |    0     |     0      |     0x0      |    Success"
        print ""
            
    except Exception, e:
        print_response(set_failure_dict("show_battery_information: Exception {0}".format(e), completion_code.failure))

def show_rm_information():
    """ Get and display rack manager information
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = manager_info()
        uptime = get_rm_uptime()
             
        print ""            
        print "== Chassis Controller =="           
        if not check_success(uptime):
            print "Command Failed. Error: {0}".format(uptime[completion_code.desc])
        elif not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            print "Firmware Version        : {0}".format(result["FW Version"])
            print "Hardware Version        : {0}".format(result["Asset Info"]["Hardware Version"])
            print "Software Version        :"
            print "Serial Number           : {0}".format(result["Asset Info"]["SerialNumber"])
            print "Asset Tag               : {0}".format(result["Asset Info"]["AssetTag"])
            print "System Uptime           : {0}".format(uptime["Up Time"].strip())
            print ""  

    except Exception, e:
        print_response(set_failure_dict("show_rm_information: Exception {0}".format(e), completion_code.failure))

def show_blade_cpu_health(device_id):
    """ Get and display blade cpu health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = show_cpu_health(device_id)
                                        
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            result.pop(completion_code.cc_key, None)
            print ""
            print "== CPU Information =="
            for (processor, values) in result.items():
                print "Processor ID              : {0}".format(result[processor]["Processor Id"])
                print "Processor Type            : {0}".format(result[processor]["Processor Type"])
                print "Processor Frequency       : {0} MHz".format(result[processor]["Processor Frequency"])
                print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_cpu_health: Exception {0}".format(e), completion_code.failure))
            
def show_blade_fru_health(device_id):
    """ Get and display blade fru health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = get_server_fru(device_id)
                        
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            print ""
            print "== FRU Information =="
            print "Blade Serial Number     : {0}".format(result["Product Serial"])
            print "Blade Asset Tag         : {0}".format(result["AssetTag"])
            print "Blade Product Type      : {0}".format(result["Model"])
            print "Blade Hardware Version  : {0}".format(result["Board Product"])
            print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_fru_health: Exception {0}".format(e), completion_code.failure))
        
def show_blade_pcie_health(device_id):
    """ Get and display blade pcie health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = show_pcie_health(device_id)
                                
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            result.pop(completion_code.cc_key, None)
            print ""
            print "== PCIe Information =="
            for (pcie, values) in result.items():               
                result[pcie]["Vendor Id"] = format(int(result[pcie]["Vendor Id"]), "#04X")
                result[pcie]["Device Id"] = format(int(result[pcie]["Device Id"]), "#04X")
                result[pcie]["SubSystem Id"] = format(int(result[pcie]["SubSystem Id"]), "#04X")
                print "PCIe Slot Number     : {0}".format(result[pcie]["PCIe Index"])
                print "PCIe Vendor Id       : {0}".format(result[pcie]["Vendor Id"])
                print "PCIe Device Id       : {0}".format(result[pcie]["Device Id"])
                print "PCIe Subsystem Id    : {0}".format(result[pcie]["SubSystem Id"])
                print "PCIe Card State      : {0}".format(result[pcie]["PCIe Status"])
                print "PCIe Completion Code : {0}".format(completion_code.success)
                print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_pcie_health: Exception {0}".format(e), completion_code.failure))
        
def show_blade_memory_health(device_id):
    """ Get and display blade memory health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = show_memory_info(device_id)
                                
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            result.pop(completion_code.cc_key, None)
            print ""
            print "== Memory Information =="
            for (dimm, values) in result.items():
                if values["Dimm Status"] == "Present":
                    values["Dimm Status"] = "Ok"
                print "Dimm                   : {0}".format(dimm)
                print "Dimm Type              : {0}".format(values["Dimm Type"])
                print "Memory Voltage         : {0}".format(values["Dimm Voltage"])
                print "Size                   : {0}".format(values["Dimm Size"])
                print "Speed                  : {0}".format(values["Dimm Speed"])
                print "Memory Status          : {0}".format(values["Dimm Status"])
                print "Memory Completion Code : {0}".format(completion_code.success)
                print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_memory_health: Exception {0}".format(e), completion_code.failure))

def show_blade_temp_health(device_id):
    """ Get and display blade temperature health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = show_temperature_health(device_id)
                                        
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            result.pop(completion_code.cc_key, None)
            print ""
            print "== Temp Sensor Information =="
            for (sensor, values) in result.items():
                print "Sensor Number          : {0}".format(values["Sensor Number"])
                print "Sensor Type            : Temperature"                
                print "Sensor Reading         : {0}".format(values["Sensor Reading"])
                print "Sensor Description     : {0}".format(values["Sensor Description"])
                print "Sensor Entity ID       : {0}".format(values["Sensor Entity ID"])
                print "Sensor Entity Instance :"
                print "Sensor Status          : {0}".format(values["Sensor Status"])
                print "Sensor Completion Code : {0}".format(completion_code.success)
                print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_temp_health: Exception {0}".format(e), completion_code.failure))
        
def show_blade_sensor_health(device_id):
    """ Get and display blade sensor health
        IMPORTANT! - Output formatted for compatibility with WcsCli
    """
    try:
        result = show_sensor_health(device_id)
                                                
        if not check_success(result):
            print "Command Failed. Error: {0}".format(result[completion_code.desc])
        else:
            result.pop(completion_code.cc_key, None)
            print ""
            print "== Sensor Information =="
            for (sensor, values) in result.items():
                print "Sensor Number          : {0}".format(values["Sensor Number"])
                print "Sensor Type            :"
                print "Sensor Reading         : {0}".format(values["Sensor Reading"])
                print "Sensor Description     : {0}".format(values["Sensor Description"])
                print "Sensor Entity ID       : {0}".format(values["Sensor Entity ID"])
                print "Sensor Entity Instance :"
                print "Sensor Status          : {0}".format(values["Sensor Status"])
                print "Sensor Completion Code : {0}".format(completion_code.success)
                print ""    

    except Exception, e:
        print_response(set_failure_dict("show_blade_sensor_health: Exception {0}".format(e), completion_code.failure))

    