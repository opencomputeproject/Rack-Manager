# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import ctypes
import lib_utils
from collections import OrderedDict
from ctypes import *
from ipmicmd_library import *


############################################################################################################
# System set functions 
############################################################################################################

def set_server_power_alert_policy(serverid, powerlimit, alertaction = 0, remediationaction = 0, throttleduration = 0, removedelay = 1):   
    set_power_limit = set_server_default_power_limit (serverid, powerlimit, throttleduration, removedelay)
    if (set_power_limit[completion_code.cc_key] != completion_code.success):
        return set_power_limit
        
    return set_server_activate_psu_alert (serverid, alertaction, remediationaction)

def set_server_default_power_limit(serverid, power_limit, ms_delay, auto_remove):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "setdpc", str(power_limit),
            str(ms_delay), str(auto_remove)])
        return parse_set_server_powerlimit (interface, "setdpc")
    
    except Exception as error:
        return set_failure_dict ("set_server_default_power_limit() Exception {0}".format (error))
        
def set_server_activate_psu_alert (serverid, alert_action, rearm = 0):
    if ((alert_action < 0) or (alert_action > 2)):
        return set_failure_dict ("Alert action not in range (0 - 2)")
        
    if ((rearm < 0) or (rearm > 2)):
        return set_failure_dict ("Rearm action not in range (0 - 2)")
    
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "activatepsualert",
            str (alert_action << 2), str (rearm)])
        return parse_set_server_power_alert_policy (interface, "activatepsualert")
    
    except Exception as error:
        return set_failure_dict ("set_server_activate_psu_alert() Exception {0}".format (error))

def set_server_power_limit(serverid, powerlimit):
    try:
        # Action is set to '0' (do-nothing) and setting minimum time period to 1 
        interface = get_ipmi_interface(serverid, ["dcmi", "power", "set_limit", "action",
                                                  "no_action", "limit", str (powerlimit), 
                                                  "correction", "6000", "sample", "1"])         
        return parse_set_server_powerlimit(interface, "setserverpowerlimit")
        
    except Exception as error:  
        return set_failure_dict("set_server_power_limit() Exception {0}".format(error)) 

def set_server_power_limit_on(serverid):
    try:       
        interface = get_ipmi_interface(serverid, ["dcmi", "power", "activate"]) 
        return parse_set_server_powerlimit(interface, "setserverpowerlimiton")
        
    except Exception as error:
        return set_failure_dict("set_server_power_limit_on() Exception {0}".format(error))  

def set_server_power_limit_off(serverid):
    try:
        interface = get_ipmi_interface(serverid, ["dcmi", "power", "deactivate"]) 
        return parse_set_server_powerlimit(interface, "setserverpowerlimitoff")
    
    except Exception as error:  
        return set_failure_dict("set_server_power_limit_off() Exception {0}".format (error)) 

############################################################################################################
# System get functions 
############################################################################################################

def get_server_power_limit (serverid):
    try:       
        interface = get_ipmi_interface (serverid, ["dcmi", "power", "get_limit"])
        return parse_get_server_dcmi_powerlimit (interface, "getserverpowerlimit")
        
    except Exception as e:  
        return set_failure_dict ("get_server_power_limit() Exception {0}".format (e),
            completion_code.failure)

def get_server_power_reading (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["dcmi", "power", "reading"])
        return parse_get_server_powerreading (interface, "getserverpowerreading")
    
    except Exception as e:  
        return set_failure_dict ("get_server_power_reading() Exception {0}".format (e),
            completion_code.failure)

def get_server_default_power_limit (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "dpc"])
        return parse_get_server_powerlimit (interface, "getserverdefaultpowerlimit")
    
    except Exception as e:  
        return set_failure_dict ("get_server_default_power_limit() Exception {0}".format (e),
            completion_code.failure)
        
def get_server_psu_alert (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psualert"])
        return parse_get_server_power_alert_policy (interface, "getserverpsualert")
    
    except Exception as e:  
        return set_failure_dict ("get_server_psu_alert() Exception {0}".format (e),
            completion_code.failure)

def get_server_power_alert_policy (serverid):
    result = {}
    result["Server ID"] = serverid
    
    try:
        result.update (get_server_power_reading (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
        result.update (get_server_default_power_limit (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
        result.update (get_server_psu_alert (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
    except Exception as e:  
        return set_failure_dict ("get_server_power_alert_policy() Exception {0}".format (e),
            completion_code.failure) 
    
    Output = {}

    Output["Server ID"] = serverid
            
    if "PowerReadingWatts" in result:
        Output["PowerDrawnInWatts"] = result["PowerReadingWatts"]
    if "Alert Enabled" in result:
        Output["IsAlertLimitEnabled"] = result["Alert Enabled"]
    if "PowerLimit" in result:
        Output["AlertLimitInWatts"] = result["PowerLimit"]
    if "AlertAction" in result:
        Output["AlertAction"] = result["AlertAction"]
    if "ThrottleDuration" in result:
        Output["FastThrottleDurationInMsecs"] = result["ThrottleDuration"]
    if "LimitDelay" in result:
        Output["AutoRemoveLimitDelayInSecs"] = result["LimitDelay"]

    Output[completion_code.cc_key] = result[completion_code.cc_key]
    
    return Output 

def get_server_throttling_statistics (serverid):
    try:
        result = get_server_power_reading (serverid)
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
        result.update (get_server_power_limit (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
        result.update (get_server_default_power_limit (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
        result.update (get_server_psu_alert (serverid))
        if (result[completion_code.cc_key] != completion_code.success):
            return result
        
    except Exception as e:  
        return set_failure_dict ("get_server_throttling_statistics() Exception {0}".format (e),
            completion_code.failure) 
    
    Output = {}
    
    Output["Server ID"] = serverid
    
    if "PowerReadingWatts" in result:
        Output["PowerDrawnInWatts"] = result["PowerReadingWatts"]
    if "PowerLimit" in result:
        Output["AlertLimitInWatts"] = result["PowerLimit"]
    if "StaticState" in result:
        Output["StaticLimitStatus"] = result["StaticState"]
    if "StaticLimit" in result:
        Output["StaticLimitInWatts"] = result["StaticLimit"]
    if "AutoProchot" in result:
        Output["AutoProchotStatus"] = result["AutoProchot"]
    if "BladeProchot" in result:
        Output["BladeProchotStatus"] = result["BladeProchot"]
    
    Output[completion_code.cc_key] = result[completion_code.cc_key]
    
    return Output
   
############################################################################################################
# System parse output functions 
############################################################################################################
   
def parse_set_server_powerlimit(interface, command):
    try:        
        output = call_ipmi(interface, command) 
                
        if "ErrorCode" in output:
            return set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
                
        if output['status_code'] == 0:
            return set_success_dict()
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to set powerlimit: {0}".format(error_data.split(":")[-1].strip()), completion_code.failure)

    except Exception, e:  
        return set_failure_dict("parse_set_server_powerlimit() Exception {0}".format(e), completion_code.failure)        

def parse_set_server_power_alert_policy(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
        
        if output['status_code'] == 0:
            return set_success_dict()
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to set power alert policy: {0}".format(error_data.split(":")[-1].strip()), completion_code.failure)       
        
    except Exception, e:  
        return set_failure_dict("parse_set_server_power_alert_policy() Exception {0}".format(e), completion_code.failure) 

def parse_get_server_powerlimit(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
        
        get_powerlimit = {}
        
        if output['status_code'] == 0:
            get_powerlimit_data  = output['stdout'].split('\n')
        
            # Removes empty strings from the list
            get_powerlimit_data = filter(None, get_powerlimit_data)
    
            numerical = re.compile(r'[^\d.]+')
        
            get_powerlimit[completion_code.cc_key] = completion_code.success                 
                                                                                                                                                               
            for string in get_powerlimit_data:
                if "Default Power Limit" in string:               
                    get_powerlimit["PowerLimit"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Action" in string:               
                    get_powerlimit["AlertAction"] = string.split(":")[-1].strip()
                elif "Auto Remove" in string:               
                    get_powerlimit["LimitDelay"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Delay Time" in string:               
                    get_powerlimit["ThrottleDuration"] = numerical.sub("", string.split(":")[-1].strip())   
            
            return get_powerlimit
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to get powerlimit: {0}".format(error_data.split(":")[-1].strip()), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("parse_get_server_powerlimit() Exception {0}".format(e),completion_code.failure) 

def parse_get_server_dcmi_powerlimit(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
        
        get_powerlimit = {}
        
        if output['status_code'] == 0:
            get_powerlimit_data  = output['stdout'].split('\n')
            
            # Removes empty strings from the list
            get_powerlimit_data = filter(None, get_powerlimit_data)
            
            get_powerlimit[completion_code.cc_key] = completion_code.success                 
                                                        
            for string in get_powerlimit_data:
                if "Current Limit State" in string:               
                    get_powerlimit["StaticState"] = string.split(":")[-1].strip()
                elif "Power Limit" in string:               
                    get_powerlimit["StaticLimit"] = string.split(":")[-1].strip()
                    
            return get_powerlimit
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to get powerlimit: {0}".format(error_data.split(":")[-1].strip()),completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("parse_get_server_dcmi_powerlimit() Exception {0}".format(e),completion_code.failure)    

def parse_get_server_power_alert_policy(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
        
        get_power_alert_policy = {}
                
        if output['status_code'] == 0:
            get_power_alert_policy_data  = output['stdout'].split('\n')
            
            # Removes empty strings from the list
            get_power_alert_policy_data = filter(None, get_power_alert_policy_data)
            
            get_power_alert_policy[completion_code.cc_key] = completion_code.success                 
                                                        
            for string in get_power_alert_policy_data:
                if "Psu Alertgpi" in string:               
                    get_power_alert_policy["Alert Enabled"] = string.split(":")[-1].strip()
                elif "Auto Prochot Enabled" in string:               
                    get_power_alert_policy["AutoProchot"] = string.split(":")[-1].strip()
                elif "Bmc Prochot Enabled" in string:               
                    get_power_alert_policy["BladeProchot"] = string.split(":")[-1].strip()
                    
            return get_power_alert_policy      
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to get power alert policy: {0}".format(error_data.split(":")[-1].strip()), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("parse_get_server_power_alert_policy() Exception {0}".format(e), completion_code.failure)     

def parse_get_server_powerreading(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + str(output)), completion_code.failure)
        
        get_powerreading = {}
        
        if(output['status_code'] == 0):
            get_powerreading_data  = output['stdout'].split('\n')
        
            # Removes empty strings from the list
            get_powerreading_data = filter(None, get_powerreading_data)
    
            numerical = re.compile(r'[^\d]+')
                
            get_powerreading[completion_code.cc_key] = completion_code.success             
                                                                        
            for string in get_powerreading_data:
                if "Instantaneous power reading" in string:               
                    get_powerreading["PowerReadingWatts"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Minimum during sampling period" in string:               
                    get_powerreading["MinPowerReadingWatts"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Maximum during sampling period" in string:               
                    get_powerreading["MaxPowerReadingWatts"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Average power reading over sample period" in string:               
                    get_powerreading["AvgPowerReadingWatts"] = numerical.sub("", string.split(":")[-1].strip())
                elif "Sampling period" in string:          
                    get_powerreading["SamplingPeriodSeconds"] = int(numerical.sub("", string.split(":")[-1].strip()))   
            return get_powerreading     
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to get power reading: {0}".format (error_data.split(":")[-1].strip ()), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict(("parse_get_server_powerreading() Exception {0}".format(str(e))), completion_code.failure)
    
def get_server_psu_status (serverid, phase = ""):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuread", "all", str (phase)])
        output = call_ipmi (interface, "psuread all");
        return parse_psu_status_output (output)
        
    except Exception as error:
        return set_failure_dict ("get_server_psu_status() Exception: {0}".format (error),
            completion_code.failure)
        
def get_server_psu_fw_version (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuread", "fw"])
        output = call_ipmi (interface, "psuread fw")
        return parse_psu_status_output (output)
        
    except Exception as error:
        return set_failure_dict ("get_server_psu_fw_version() Exception: {0}".format (error),
            completion_code.failure)
        
def get_server_psu_bootloader_version (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuread", "fw", "0"])
        output = call_ipmi (interface, "psuread bootloader")
        return parse_psu_status_output (output, prefix = "Bootloader ")
    
    except Exception as error:
        return set_failure_dict (
            "get_server_psu_bootloader_version() Exception: {0}".format (error),
            completion_code.failure)
        
def get_server_psu_battery_present (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuread", "caps"])
        output = call_ipmi (interface, "psuread caps")
        return parse_psu_status_output (output)
    
    except Exception as error:
        return set_failure_dict ("get_server_psu_battery_present() Exception {0}".format (error),
            completion_code.failure)
        
def parse_psu_status_output (output, prefix = ""):
    if (output["status_code"] == 0):
        result = OrderedDict ()
        for info in output["stdout"].split ("\n"):
            if (info):
                parsed = info.split (":")
                result[prefix + parsed[0].strip ()] = parsed[1].strip ()
                    
        result[completion_code.cc_key] = completion_code.success
        return result
    else:
        return set_failure_dict (output["stderr"], completion_code.failure)
        
def clear_server_psu_faults (serverid, phase = ""):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuaction", "clear", str (phase)])
        output = call_ipmi (interface, "psuaction clear")
        
        if (output["status_code"] == 0):
            return {completion_code.cc_key : completion_code.success}
        else:
            set_failure_dict (output["stderr"], completion_code.failure)
            
    except Exception as error:
        return set_failure_dict ("clear_server_psu_faults() Exception: {0}".format (error),
            completion_code.failure)
        
def set_server_psu_battery_test (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "psuaction", "battery"])
        output = call_ipmi (interface, "psuaction battery")
        
        if (output["status_code"] == 0):
            return {completion_code.cc_key : completion_code.success}
        else:
            set_failure_dict (output["stderr"], completion_code.failure)
            
    except Exception as error:
        return set_failure_dict ("set_server_psu_battery_test() Exception: {0}".format (error),
            completion_code.failure)

############################################################################################################
# Manager get functions 
############################################################################################################

def get_rack_manager_power_reading():
    result = {}
    output = -1
        
    try:
        hsc_binary = lib_utils.get_hsc_library()
        
        power = c_double()
        output = hsc_binary.hsc_get_power(byref(power))
            
        if output != 0:
            return set_failure_dict("Failed to get power reading using HSC library: " + str(output), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("get_rack_manager_power_reading() Exception {0}".format(e), completion_code.failure)
    
    result[completion_code.cc_key] = completion_code.success
    result["PowerInWatts"] = round(power.value, 2)
    
    return result

def get_rack_manager_input_voltage():
    result = {}
    output = -1
        
    try:
        hsc_binary = lib_utils.get_hsc_library()
        
        voltage = c_double()
        output = hsc_binary.hsc_get_inputvoltage(byref (voltage))
            
        if output != 0:
            return set_failure_dict("Failed to get input voltage using HSC library: " + str(output), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("get_rack_manager_input_voltage() Exception {0}".format(e), completion_code.failure)
    
    result[completion_code.cc_key] = completion_code.success
    result["InputVoltage"] = round(voltage.value, 2)
    
    return result

def get_rack_manager_hsc_status ():
    class HscStatus(LittleEndianStructure):
            _fields_ = [('noFaults', c_byte, 1),
                        ('cml_fault', c_byte, 1),
                        ('temperature_fault', c_byte, 1),
                        ('vin_uv_fault', c_byte, 1),
                        ('iout_oc_fault', c_byte, 1),
                        ('vout_ov_fault', c_byte, 1),
                        ('unit_off', c_byte, 1),
                        ('unit_busy', c_byte, 1),
                        ('unknown_fault', c_byte, 1),
                        ('other_fault', c_byte, 1),
                        ('fan_fault', c_byte, 1),
                        ('power_good', c_byte, 1),
                        ('mfr_fault', c_byte, 1),
                        ('input_fault', c_byte, 1),
                        ('iout_pout_fault', c_byte, 1),
                        ('vout_fault', c_byte, 1)]

    hscstatus_str = ""
    output = -1
    
    try:
        hsc_binary = lib_utils.get_hsc_library()
            
        hscstatus = HscStatus(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

        output = hsc_binary.hsc_get_status(byref(hscstatus))
            
        if output != 0:
            return set_failure_dict("Failed to get power using HSC library: " + str(output), completion_code.failure)
        
        if hscstatus.cml_fault == 1:
            hscstatus_str = hscstatus_str + " CML Fault"
        if hscstatus.temperature_fault == 1:
            hscstatus_str = hscstatus_str + " Temperature Fault"
        if hscstatus.vin_uv_fault == 1:
            hscstatus_str = hscstatus_str + " Vin UV Fault"
        if hscstatus.iout_oc_fault == 1:
            hscstatus_str = hscstatus_str + " Iout OC Fault"
        if hscstatus.vout_ov_fault == 1:
            hscstatus_str = hscstatus_str + " Vout OV Fault"
        if hscstatus.unit_off == 1:
            hscstatus_str = hscstatus_str + " Unit Off Fault"
        if hscstatus.unit_busy == 1:
            hscstatus_str = hscstatus_str + " Unit Busy Fault"
        if hscstatus.unknown_fault == 1:
            hscstatus_str = hscstatus_str + " Unknown Fault"
        if hscstatus.other_fault == 1:
            hscstatus_str = hscstatus_str + " Other Fault"
        if hscstatus.fan_fault == 1:
            hscstatus_str = hscstatus_str + " Fan Fault"
        if hscstatus.mfr_fault == 1:
            hscstatus_str = hscstatus_str + " Mfr Fault"
        if hscstatus.input_fault == 1:
            hscstatus_str = hscstatus_str + " Input Fault"
        if hscstatus.iout_pout_fault == 1:
            hscstatus_str = hscstatus_str + " Iout Pout Fault"
        if hscstatus.vout_fault == 1:
            hscstatus_str = hscstatus_str + " Vout Fault"
        if hscstatus_str == "":
            hscstatus_str = "Healthy"
                                                          
    except Exception, e:  
        return set_failure_dict("get_rack_manager_power_status() Exception {0}".format(str(e)),completion_code.failure) 
    
    return {"HSC Status" : hscstatus_str, completion_code.cc_key : completion_code.success}

def get_rack_manager_psu_status():
    result = {}
    output = -1
        
    try:
        gpio_binary = lib_utils.get_gpio_library ()
        
        state = c_uint()
        output = gpio_binary.ocs_get_powergood(byref(state))
                        
        if output != 0:
            return set_failure_dict("Failed to get psu state using GPIO library: " + str(output), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("get_rack_manager_status() Exception {0}".format(str(e)), completion_code.failure)
    
    result[completion_code.cc_key] = completion_code.success
    result["PSU A Status"] = "Healthy" if ((state.value & 0x1) == 1) else "Faulty"
    result["PSU B Status"] = "Healthy" if (((state.value >> 1) & 0x1) == 1) else "Faulty"
    
    return result

def get_rack_manager_status():
    power = get_rack_manager_hsc_status()
    psu = get_rack_manager_psu_status()
    
    result = power.copy()
    result.update (psu)
    if ((result[completion_code.cc_key] == completion_code.success) and
        (power[completion_code.cc_key] == completion_code.failure)):
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.desc] = power[completion_code.desc]
        
    return result

############################################################################################################
# Manager set functions 
############################################################################################################

def set_rack_manager_clear_power_faults():
    result = {}
    output = -1
        
    try:
        hsc_binary = lib_utils.get_hsc_library()
 
        output = hsc_binary.hsc_clear_faults()
            
        if output != 0:
            return set_failure_dict("Failed to clear power faults using HSC library: {0}".format(output), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("set_rack_manager_clear_power_faults() Exception {0}".format(e), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result
