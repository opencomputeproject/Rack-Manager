# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import *
from ipmicmd_library import * 

############################################################################################################
# FPGA set functions 
############################################################################################################

def set_fpga_bypass(serverid, bypass):
    if bypass == "Enabled":
        return set_fpga_bypass_on(serverid)
    elif bypass == "Disabled":
        return set_fpga_bypass_off(serverid)
    else:
        return set_failure_dict("set_fpga_bypass invalid type {0}.".format(bypass), 
                                completion_code.failure)
        
def set_fpga_bypass_on(serverid):
    """ Set FPGA bypass mode on
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaaction", "setbypass"])
        return parse_set_fpga_bypass(interface, "setbypass")
    
    except Exception, e:
        return set_failure_dict("set_fpga_bypass_on() Exception {0}".format(e), completion_code.failure) 

def set_fpga_bypass_off(serverid):
    """ Set FPGA bypass mode off 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaaction", "clearbypass"])
        return parse_set_fpga_bypass(interface, "clearbypass")
    
    except Exception, e:
        return set_failure_dict("set_fpga_bypass_off() Exception {0}".format(e), completion_code.failure)

############################################################################################################
# FPGA get functions 
############################################################################################################

def get_fpga_bypass_mode(serverid):
    """ Read back FPGA bypass mode setting 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaread", "mode"])
        return parse_get_fpga_bypass_mode(interface, "mode")
    
    except Exception, e:
        return set_failure_dict("get_fpga_bypass_mode() Exception {0}".format(e), completion_code.failure)

def get_fpga_health(serverid):
    """ Read back FPGA health 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaread", "health"])
        return parse_get_fpga_health(interface, "health")
    
    except Exception, e:
        return set_failure_dict("get_fpga_health() Exception {0}".format(e), completion_code.failure)

def get_fpga_temp(serverid):
    """ Read back FPGA temperature
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaread", "temp"])
        return parse_get_fpga_temp(interface, "temp")
    
    except Exception, e:
        return set_failure_dict("get_fpga_temp() Exception {0}".format(e), completion_code.failure)

def get_fpga_i2c_version(serverid):
    """ Read back FPGA I2C version 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaread", "i2cversion"])
        return parse_get_fpga_i2cversion(interface, "i2cversion")
    
    except Exception, e:
        return set_failure_dict("get_fpga_i2c_version() Exception {0}".format(e), completion_code.failure)

def get_fpga_assetinfo(serverid):
    """ Read back product info area from FPGA FRU 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "fpgaread", "assetinfo"])
        return parse_get_fpga_assetinfo(interface, "assetinfo")
    
    except Exception, e:
        return set_failure_dict("get_fpga_assetinfo() Exception {0}".format(e), completion_code.failure)
        
   
############################################################################################################
# FPGA parse output functions 
############################################################################################################ 

def parse_set_fpga_bypass(interface, command):
    try:        
        output = call_ipmi(interface, command)
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        if output['status_code'] == 0:
            return set_success_dict()
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip(), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_set_fpga_bypass() Exception {0}".format(e), completion_code.failure) 

def parse_get_fpga_bypass_mode(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_mode = {}
        
        if output['status_code'] == 0:
                get_mode_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_mode_data = filter(None, get_mode_data)
                
                get_mode[completion_code.cc_key] = completion_code.success     
                
                for string in get_mode_data:
                    if "Bypass Mode" in string:               
                        get_mode["Bypass Mode"] = string.split(":")[-1].strip()
                    elif "User Logic Network" in string:               
                        get_mode["User Logic Network"] = string.split(":")[-1].strip()

                return get_mode    
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip(), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_fpga_bypass_mode() Exception {0}".format(e), completion_code.failure) 
    
def parse_get_fpga_temp(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_temp = {}
        
        if output['status_code'] == 0:
                get_temp_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_temp_data = filter(None, get_temp_data)
                
                get_temp[completion_code.cc_key] = completion_code.success     
                
                for string in get_temp_data:
                    if "Temperature in Celsius" in string:               
                        get_temp["Temperature in Celsius"] = string.split(":")[-1].strip()

                return get_temp
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip(), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_fpga_temp() Exception {0}".format(e), completion_code.failure) 
    
def parse_get_fpga_i2cversion(interface, command):
    try:        
        output = call_ipmi(interface, command)
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_ver = {}
        
        if output['status_code'] == 0:
                get_ver_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_ver_data = filter(None, get_ver_data)
                
                get_ver[completion_code.cc_key] = completion_code.success     
                
                for string in get_ver_data:
                    if "I2C Version" in string:               
                        get_ver["I2C Version"] = string.split(":")[-1].strip()

                return get_ver        
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip (), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_fpga_i2cversion() Exception {0}".format(e), completion_code.failure)
    
def parse_get_fpga_health(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_health = {}
        
        if output['status_code'] == 0:
                get_health_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_health_data = filter(None, get_health_data)
                
                get_health[completion_code.cc_key] = completion_code.success                 
                
                for string in get_health_data:
                    if "PCIe HIP 0 Up" in string:               
                        get_health["PCIe HIP 0 Up"] = string.split(":")[-1].strip()
                    elif "PCIe HIP 1 Up" in string:               
                        get_health["PCIe HIP 1 Up"] = string.split(":")[-1].strip()
                    elif "40G Link 0 Up" in string:               
                        get_health["40G Link 0 Up"] = string.split(":")[-1].strip()
                    elif "40G Link 0 Tx Activity" in string:               
                        get_health["40G Link 0 Tx Activity"] = string.split(":")[-1].strip()
                    elif "40G Link 0 Rx Activity" in string:               
                        get_health["40G Link 0 Rx Activity"] = string.split(":")[-1].strip()
                    elif "40G Link 1 Up" in string:               
                        get_health["40G Link 1 Up"] = string.split(":")[-1].strip()
                    elif "40G Link 1 Tx Activity" in string:               
                        get_health["40G Link 1 Tx Activity"] = string.split(":")[-1].strip()
                    elif "40G Link 1 Rx Activity" in string:               
                        get_health["40G Link 1 Rx Activity"] = string.split(":")[-1].strip()

                return get_health        
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip (), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_fpga_health() Exception {0}".format(e), completion_code.failure) 
    
def parse_get_fpga_assetinfo(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_assetinfo = {}
        
        if output['status_code'] == 0:
                get_fru_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_fru_data = filter(None, get_fru_data)
                                
                get_assetinfo[completion_code.cc_key] = completion_code.success 
                
                for string in get_fru_data:
                    if "Product Manufacturer" in string:               
                        get_assetinfo["Product Manufacturer"] = string.split(":")[-1].strip()
                    elif "Product Name" in string:               
                        get_assetinfo["Product Name"] = string.split(":")[-1].strip()
                    elif "Product Model Number" in string:               
                        get_assetinfo["Product Model Number"] = string.split(":")[-1].strip()
                    elif "Product Version" in string:               
                        get_assetinfo["Product Version"] = string.split(":")[-1].strip()
                    elif "Product Serial Number" in string:               
                        get_assetinfo["Product Serial Number"] = string.split(":")[-1].strip()
                    elif "Product FRU File ID" in string:               
                        get_assetinfo["Product FRU File ID"] = string.split(":")[-1].strip()
                    elif "Product Custom Field 1" in string:               
                        get_assetinfo["Product Custom Field 1"] = string.split(":")[-1].strip()
                    elif "Product Custom Field 2" in string:               
                        get_assetinfo["Product Custom Field 2"] = string.split(":")[-1].strip()

                return get_assetinfo        
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip (), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_fpga_assetinfo() Exception {0}".format(e), completion_code.failure) 
    

