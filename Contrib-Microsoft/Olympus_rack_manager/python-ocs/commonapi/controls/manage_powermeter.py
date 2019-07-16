# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.


import ctypes

from ctypes import *
from utils import *
from lib_utils import get_pru_library

############################################################################################################
# Rack set functions 
############################################################################################################

def set_rack_power_limit_policy(powerlimit):
    result = {}
    output = -1
    
    try:
        if int(powerlimit) > 18000 or int(powerlimit) < 500:
            return set_failure_dict ("Power limit not in range (500 - 18000): {0}".format(powerlimit))
        
        pru_binary = get_pru_library()
            
        output = pru_binary.set_throttle_limit(c_double(powerlimit))
        
        if output != 0:
            return set_failure_dict(("Failed to set throttle limit using PRU library: {0}".format(output)), completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict("set_rack_power_limit_policy() Exception {0}".format(e), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def set_rack_power_throttle(policy, dcpolicy):
    result = {}
    output = -1
        
    if int(policy) != 0 and int(policy) != 1:
        return set_failure_dict(("Unknown policy sent to set_rack_power_throttle: {0}".format(policy)), completion_code.failure)
    if int(dcpolicy) != 0 and int(dcpolicy) != 1:
        return set_failure_dict(("Unknown DC policy sent to set_rack_power_throttle: {0}".format(dcpolicy)), completion_code.failure)
    
    try:
        pru_binary = get_pru_library()
        
        output = pru_binary.set_throttle_enable(policy, dcpolicy)
        
        if output != 0:
            return set_failure_dict(("Failed to enable/disable throttle: {0}".format(output)), completion_code.failure)
    
    except Exception as e:  
        return set_failure_dict("set_rack_power_throttle() Exception {0}".format(e), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def set_rack_power_alert_policy(policy, dcthrottlepolicy, powerlimit):
    result = {}
    output = -1
        
    if int(policy) != 0 and int(policy) != 1:
        return set_failure_dict(("Unknown policy sent to set_rack_power_alert_policy: " + str(policy)), completion_code.failure)
    
    try:
        if int(powerlimit) > 18000 or int(powerlimit) < 500:
            return set_failure_dict ("Power limit not in range (500 - 18000): {0}".format(powerlimit))
        
        pru_binary = get_pru_library()
           
        output = pru_binary.set_throttle_limit(c_double(powerlimit))
            
        if output != 0:
            return set_failure_dict(("Failed to set throttle limit using PRU library: " + str(output)), completion_code.failure)
        
        output = pru_binary.set_throttle_enable(policy, dcthrottlepolicy)
        
        if output != 0:
            return set_failure_dict(("Failed to set throttle limit using PRU library: " + str(output)), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("set_rack_power_alert_policy() Exception {0}".format(str(e)), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def set_rack_clear_max_power():
    result = {}
    output = -1
        
    try:
        pru_binary = get_pru_library()
        
        output = pru_binary.clear_max_power()
            
        if output != 0:
            return set_failure_dict(("Failed to clear max manager power using PRU library: " + str(output)), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("set_rack_clear_max_power() Exception {0}".format(str(e)), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def set_rack_clear_power_faults():
    result = {}
    output = -1
        
    try:
        pru_binary = get_pru_library ()
         
        output = pru_binary.clear_phase_status(0)
            
        if output != 0:
            return set_failure_dict(("Failed to clear feed 0 status using PRU library: " + str(output)), completion_code.failure)

        output = pru_binary.clear_phase_status(1)
            
        if output != 0:
            return set_failure_dict(("Failed to clear feed 1 status using PRU library: " + str(output)), completion_code.failure)
    
    except Exception, e:  
        return set_failure_dict("set_rack_clear_power_faults() Exception {0}".format(str(e)), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result


############################################################################################################
# Rack get functions
############################################################################################################

def get_rack_power_limit_policy():
    result = {}
    output = -1
    
    throttle_limit = c_double()
    
    try:
        pru_binary = get_pru_library ()
        
        output = pru_binary.get_throttle_limit(byref(throttle_limit))
        
        if output != 0:
            return set_failure_dict(("Failed to get throttle limit from PRU library: " + str(output)), completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict("get_rack_power_limit_policy() Exception {0}".format(str(e)),completion_code.failure) 
    
    result["AlertLimitInWatts"] = round(throttle_limit.value, 0)
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_rack_power_throttle_status():
    result = {}
    output = -1
    
    throttle_enabled = c_int()
    throttle_active = c_int()
    dcthrottle_enabled = c_int()
    dcthrottle_active = c_int()
    
    try:
        pru_binary = get_pru_library ()

        output = pru_binary.get_throttle_status(byref(throttle_enabled), byref(throttle_active), byref(dcthrottle_enabled), byref(dcthrottle_active))
        
        if output != 0:
            return set_failure_dict(("Failed to get throttle status: " + str(output)), completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict("get_rack_power_throttle_status() Exception {0}".format(str(e)),completion_code.failure) 
    
    result["IsDcThrottleEnabled"] = 'On' if dcthrottle_enabled.value == 1 else 'Off'
    result["IsDcThrottleActive"] = 'On' if dcthrottle_active.value == 1 else 'Off'
    result["IsAlertEnabled"] = 'On' if throttle_enabled.value == 1 else 'Off'
    result["IsAlertActive"] = 'On' if throttle_active.value == 1 else 'Off'
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_rack_power_alert_policy():
    result = {}
    output = -1
    
    throttle_limit = c_double()
    power = c_double()
    
    try:
        pru_binary = get_pru_library ()
        
        output = pru_binary.get_throttle_limit(byref(throttle_limit))
        
        if output != 0:
            return set_failure_dict(("Failed to get throttle limit from PRU library: " + str(output)), completion_code.failure)
              
        output = pru_binary.get_power(byref(power))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack manager power in watts from PRU library: " + str(output)), completion_code.failure)
        
        output = get_rack_power_throttle_status ()
        if (output[completion_code.cc_key] != completion_code.success):
            return output
            
    except Exception, e:  
        return set_failure_dict("get_rack_power_alert_policy() Exception {0}".format(str(e)),completion_code.failure) 
    
    result["PowerDrawnInWatts"] = round(power.value, 0)
    result["AlertLimitInWatts"] = round(throttle_limit.value, 0)
    result.update (output)
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_rack_power_reading():
    result = {}
    output = -1
    
    power = c_double()
    
    class MaxPowerStat(Structure):
        _fields_ = [('pwr', c_double),
                    ('feed1_phase1_amps', c_double),
                    ('feed1_phase2_amps', c_double),
                    ('feed1_phase3_amps', c_double),
                    ('feed2_phase1_amps', c_double),
                    ('feed2_phase2_amps', c_double),
                    ('feed2_phase3_amps', c_double),
                    ('feed1_phase1_volts', c_double),
                    ('feed1_phase2_volts', c_double),
                    ('feed1_phase3_volts', c_double),
                    ('feed2_phase1_volts', c_double),
                    ('feed2_phase2_volts', c_double),
                    ('feed2_phase3_volts', c_double)]

    class PhaseVal(Structure):
        _fields_ = [('phase1_val', c_double),
                    ('phase2_val', c_double),
                    ('phase3_val', c_double)]

    try:
        pru_binary = get_pru_library ()
        
        output = pru_binary.get_power(byref(power))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack power from PRU library: {0}".format(output)), completion_code.failure)

        powerstats = MaxPowerStat(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        output = pru_binary.get_max_power(byref(powerstats))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack max power from PRU library: {0}".format(output)), completion_code.failure)

        feed1pwr = PhaseVal(0, 0, 0)

        output = pru_binary.get_phase_power(0, byref(feed1pwr))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack feed 1 power from PRU library: {0}".format(output)), completion_code.failure)

        feed2pwr = PhaseVal(0, 0, 0)

        output = pru_binary.get_phase_power(1, byref(feed2pwr))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack feed 2 power from PRU library: {0}".format(output)), completion_code.failure)

        feed1status_str = parse_get_pru_phasestatus(0)
        feed2status_str = parse_get_pru_phasestatus(1)
            
    except Exception, e:  
        return set_failure_dict("get_rack_power_reading() Exception {0}".format(e),completion_code.failure) 
    
    result["PowerDrawnInWatts"] = round(power.value, 0)
    result["MaxPowerInWatts"] = round(powerstats.pwr, 0)
    result["Feed1Phase1PowerInWatts"] = round(feed1pwr.phase1_val, 0)
    result["Feed1Phase2PowerInWatts"] = round(feed1pwr.phase2_val, 0)
    result["Feed1Phase3PowerInWatts"] = round(feed1pwr.phase3_val, 0)
    result["Feed2Phase1PowerInWatts"] = round(feed2pwr.phase1_val, 0)
    result["Feed2Phase2PowerInWatts"] = round(feed2pwr.phase2_val, 0)
    result["Feed2Phase3PowerInWatts"] = round(feed2pwr.phase3_val, 0)
    result["Feed1PowerStatus"] = feed1status_str
    result["Feed2PowerStatus"] = feed2status_str
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_rack_pru_fw_version():
    result = {}
    output = -1
    
    maj_version = c_int()
    min_version = c_int()
    
    try:
        pru_binary = get_pru_library ()
        
        output = pru_binary.get_pru_fw_version(byref(maj_version), byref(min_version))
        
        if output != 0:
            return set_failure_dict(("Failed to get PRU fw version from PRU library: " + str(output)), completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict("get_rack_pru_fw_version() Exception {0}".format(str(e)), completion_code.failure) 
    
    result["FirmwareVersion"] = '%d.%d' % (maj_version.value, min_version.value)
    result[completion_code.cc_key] = completion_code.success
    
    return result  


############################################################################################################
# Rack parse output functions 
############################################################################################################
   
# Parse get_phase_status output
def parse_get_pru_phasestatus(phase):
    class FeedPowerStatus(LittleEndianStructure):
        _fields_ = [('power_negated', c_byte, 1),
                    ('oc_throttle_limit', c_byte, 1),
                    ('logic_error', c_byte, 1),
                    ('unknown_fault', c_byte, 1),
                    ('phase1_V_OV_fault', c_byte, 1),
                    ('phase1_V_UV_fault', c_byte, 1),
                    ('phase1_I_OC_fault', c_byte, 1),
                    ('phase2_V_OV_fault', c_byte, 1),
                    ('phase2_V_UV_fault', c_byte, 1),
                    ('phase2_I_OC_fault', c_byte, 1),
                    ('phase3_V_OV_fault', c_byte, 1),
                    ('phase3_V_UV_fault', c_byte, 1),
                    ('phase3_I_OC_fault', c_byte, 1),
                    ('oc_throttle_limit', c_byte, 1),
                    ('reserved', c_byte, 3)]

    feedstatus_str = ""
    
    try:
        pru_binary = get_pru_library ()
           
        feedstatus = FeedPowerStatus(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        output = pru_binary.get_phase_status(phase, byref(feedstatus))
        
        if output != 0:
            return set_failure_dict(("Failed to get rack feed {0} power status from PRU library: {1}".format(phase, output)),completion_code.failure)
        
        if feedstatus.power_negated == 1:
            feedstatus_str = feedstatus_str + " Power Negated"
        if feedstatus.oc_throttle_limit == 1:
            feedstatus_str = feedstatus_str + " OC Throttle Limit"
        if feedstatus.logic_error == 1:
            feedstatus_str = feedstatus_str + " Logic Error"
        if feedstatus.unknown_fault == 1:
            feedstatus_str = feedstatus_str + " Unknown Fault"
        if feedstatus.phase1_V_OV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 1 V OV Fault"
        if feedstatus.phase1_V_UV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 1 V UV Fault"
        if feedstatus.phase1_I_OC_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 1 I OC Fault"
        if feedstatus.phase2_V_OV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 2 V OV Fault"
        if feedstatus.phase2_V_UV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 2 V UV Fault"
        if feedstatus.phase2_I_OC_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 2 I OC Fault"
        if feedstatus.phase3_V_OV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 3 V OV Fault"
        if feedstatus.phase3_V_UV_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 3 V UV Fault"
        if feedstatus.phase3_I_OC_fault == 1:
            feedstatus_str = feedstatus_str + " Phase 3 I OC Fault"
            
        if feedstatus_str == "":
            feedstatus_str = "Healthy"
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_pru_phasestatus() Exception {0}".format(str(e)),completion_code.failure) 
    
    return feedstatus_str
