# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import * 

def get_server_ethernetinterface(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'lan print'
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        ethinterface = parse_get_server_ethernetinterface(cmdinterface, "getethintf")
        
        if ethinterface is None or not ethinterface:
            return set_failure_dict("Empty data for ethinterface", completion_code.failure)
        
    except Exception, e:
        return set_failure_dict(("get_server_ethernetinterface Exception: {0}".format(e)), completion_code.failure)
        
    return ethinterface 

def parse_get_server_ethernetinterface(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
                
        ethinterface = {}
        
        if(output['status_code'] == 0):                
                eth = output['stdout'].split('\n')
                
                ethinterface["MACAddress"] = eth[10].split(":", 1)[-1]
                ethinterface["Address"] = eth[8].split(":")[-1]
                ethinterface["AddressOrigin"] = eth[7].split(":")[-1]
                ethinterface["SubnetMask"] = eth[9].split(":")[-1]
                ethinterface["Gateway"] = eth[15].split(":")[-1]
                ethinterface[completion_code.cc_key] = completion_code.success

                return ethinterface        
        else:
            error_data = output['stderr']            
            ethinterface[completion_code.cc_key] = completion_code.failure           
            ethinterface[completion_code.desc] = error_data.split(":")[-1]    
                                                          
            return ethinterface       
        
    except Exception, e:
        return set_failure_dict(("parse_get_nextboot_result Exception: {0}".format(e)), completion_code.failure)
