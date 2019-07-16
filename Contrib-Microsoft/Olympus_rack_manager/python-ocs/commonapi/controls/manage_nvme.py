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
# NVME get functions 
############################################################################################################

def get_nvme_status(serverid):
    """ Read back NVME status 
    """
    try:
        interface = get_ipmi_interface(serverid, ["ocsoem", "nvme"])
        return parse_get_nvme_status(interface, "nvme")
    
    except Exception, e:
        return set_failure_dict("get_nvme_status() Exception {0}".format(e), completion_code.failure)
        
   
############################################################################################################
# NVME parse output functions 
############################################################################################################ 

def parse_get_nvme_status(interface, command):
    try:        
        slot = 0
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + output), completion_code.failure)
        
        get_nvme = {}
                
        if output['status_code'] == 0:
                get_nvme_data = output['stdout'].split('\n') 
                
                # Removes empty strings from the list
                get_nvme_data = filter(None, get_nvme_data)
                                
                get_nvme[completion_code.cc_key] = completion_code.success                 
                                
                for string in get_nvme_data:
                    if "Port Type" in string:
                        slot = slot + 1
                        get_nvme[slot] = {}
                        get_nvme[slot].update({"Port Type":string.split(":")[-1].strip()})
                    elif "Slot" in string:               
                        get_nvme[slot].update({"Slot":string.split(":")[-1].strip()})
                    elif "Device" in string:  
                        get_nvme[slot].update({"Device":string.split(":")[-1].strip()})             
                    elif "Vendor" in string:     
                        get_nvme[slot].update({"Vendor":string.split(":")[-1].strip()})          
                    elif "Temp" in string:  
                        get_nvme[slot].update({"Temp":string.split(":")[-1].strip()})             
                    elif "Drive Status" in string: 
                        get_nvme[slot].update({"Drive Status":string.split(":")[-1].strip()})              
                    elif "Drive Presence" in string:   
                        get_nvme[slot].update({"Drive Presence":string.split(":")[-1].strip()})            
                    elif "SMBUS Arbitration" in string:   
                        get_nvme[slot].update({"SMBUS Arbitration":string.split(":")[-1].strip()})            
                    elif "Drive Not Read" in string:     
                        get_nvme[slot].update({"Drive Not Read":string.split(":")[-1].strip()})          
                    elif "Drive Functional" in string:   
                        get_nvme[slot].update({"Drive Functional":string.split(":")[-1].strip()})            
                    elif "No Reset Required" in string:  
                        get_nvme[slot].update({"No Reset Required":string.split(":")[-1].strip()})             
                    elif "Port1 Link Active" in string:       
                        get_nvme[slot].update({"Port1 Link Active":string.split(":")[-1].strip()})        
                    elif "Port2 Link Active" in string:      
                        get_nvme[slot].update({"Port2 Link Active":string.split(":")[-1].strip()})         
                    elif "SMART Warn" in string:   
                        get_nvme[slot].update({"SMART Warn":string.split(":")[-1].strip()})            
                    elif "Serial No" in string:  
                        get_nvme[slot].update({"Serial No":string.split(":")[-1].strip()})             
                return get_nvme        
        else:
            error_data = output['stderr']
            return set_failure_dict(error_data.split(":")[-1].strip (), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_nvme_status() Exception {0}".format(e), completion_code.failure) 
    
