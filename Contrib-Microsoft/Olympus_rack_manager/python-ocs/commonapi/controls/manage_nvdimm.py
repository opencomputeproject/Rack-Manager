# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from ipmicmd_library import *

def set_nvdimm_policy(serverid, triggertype=1, nvdimmbackupdelay = 240, pcieresetdelay = 5):
    try:
        if triggertype is None:
        	triggertype = 1

        if triggertype < 0 or triggertype > 1:
            return set_failure_dict("Trigger type not in range (0 - 1)", completion_code.failure)
                    
        if nvdimmbackupdelay is None:
            nvdimmbackupdelay = 240
                
        if nvdimmbackupdelay < 0 or nvdimmbackupdelay > 255:
            return set_failure_dict("Nvdimm Backup Delay not in range (0 - 255)", completion_code.failure)
            
        if pcieresetdelay is None:
            pcieresetdelay = 1
        
        if pcieresetdelay < 0 or pcieresetdelay > 30:
            return set_failure_dict("Pcie Reset Delay not in range (0 - 30)", completion_code.failure)

        # IPMI command to set nvdimm trigger
        cmd_interface = get_ipmi_interface(serverid, ["ocsoem", "setnvdimmtrigger", str (triggertype), str (nvdimmbackupdelay), str(pcieresetdelay)])
        
        set_nvdimm_policy_response = parse_set_nvdimm_policy(cmd_interface, "setnvdimmtrigger")
        
        # Check empty or none
        if set_nvdimm_policy_response is None or not any(set_nvdimm_policy_response):
            return set_failure_dict("Empty data for setnvdimmtrigger", completion_code.failure)
        
    except Exception, e:  
        return set_failure_dict("set_nvdimm_policy() Exception {0}".format(str(e)), completion_code.failure) 
    
    return set_nvdimm_policy_response

def parse_set_nvdimm_policy(interface, command):
    try:        
        output = call_ipmi(interface, command) 
                
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + str(output)), completion_code.failure)
        
        set_nvdimmpolicy = {}
                
        if(output['status_code'] == 0):
            nvdimmpolicy_data  = output['stdout'].split('\n')
            
            # Removes empty strings from the list
            nvdimmpolicy_list =  filter(None, nvdimmpolicy_data) 
            nvdimmpolicy_setstatus = nvdimmpolicy_list[0].strip()
           
            set_nvdimmpolicy[completion_code.cc_key] = nvdimmpolicy_setstatus.split(":")[-1].strip()
            return set_nvdimmpolicy
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to set nvdimmpolicy: {0}".format (error_data.split(":")[-1].strip ()), completion_code.failure)

    except Exception, e:  
        return set_failure_dict("parse_set_server_nvdimmpolicy() Exception {0}".format(str(e)), completion_code.failure)

def get_nvdimm_policy (serverid):
    try:
        interface = get_ipmi_interface (serverid, ["ocsoem", "nvdimmtrigger"])
        return parse_get_nvdimm_policy (interface, "nvdimmtrigger")
    
    except Exception as e:  
        return set_failure_dict ("get_nvdimm_policy() Exception {0}".format (e),
            completion_code.failure)

def parse_get_nvdimm_policy(interface, command):
    try:        
        output = call_ipmi(interface, command)
        if "ErrorCode" in output:
            return set_failure_dict(("Failed to run IPMITool: " + str(output)), completion_code.failure)
        
        get_nvdimm_policy = {}
        
        if(output['status_code'] == 0):
            get_nvdimm_policy_data  = output['stdout'].split('\n') 
            get_nvdimm_policy_value = get_nvdimm_policy_data[0].split(":")[-1]
                
            get_nvdimm_policy[completion_code.cc_key] = completion_code.success 
            get_nvdimm_policy["ADR trigger"] = get_nvdimm_policy_value.split(":")[-1].strip()
            get_nvdimm_policy["ADR Complete Power Off Delay"] = get_nvdimm_policy_data[1].split(":")[-1].strip()
            get_nvdimm_policy["NVDIMM Present Power Off Delay"] = get_nvdimm_policy_data[2].split(":")[-1].strip()
            get_nvdimm_policy["ADR Complete"] = get_nvdimm_policy_data[3].split(":")[-1].strip()
            get_nvdimm_policy["ADR Complete Time Remaining"] = get_nvdimm_policy_data[4].split(":")[-1].strip()
            get_nvdimm_policy["NVDIMM Present Time Remaining"] = get_nvdimm_policy_data[5].split(":")[-1].strip()
                
        else:
            error_data = output['stderr']
            return set_failure_dict("Failed to get nvdimm policy using IPMITool: " + str(error_data.split(":")[-1]), completion_code.failure)
                                                          
    except Exception, e:  
        return set_failure_dict("parse_get_nvdimm_policy() Exception {0}".format(str(e)),completion_code.failure) 
    
    return get_nvdimm_policy  
