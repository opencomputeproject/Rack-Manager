# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import * 

def get_server_bios_config(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48",completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface,completion_code.failure)
        
        ipmi_cmd = 'ocsoem biosconfig'  # IPMI  command to get server bios config details
        cmdinterface = interface + ' ' + ipmi_cmd
        
        bios_config = parse_get_bios_config(cmdinterface, "getserverbiosconfig")
        
        if bios_config is None or not bios_config: # Check empty or none
            #return set_failure_dict("Empty data for biosconfig", "-1")
            return set_failure_dict("Empty data for biosconfig",completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("getbiosconfig Exception: ", e),completion_code.failure)

    return bios_config   

def set_server_bios_config(serverid, majorconfig, minorconfig):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48",completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface,completion_code.failure)
        
        ipmi_cmd = 'ocsoem setbiosconfig'  + ' ' + str(majorconfig) + ' ' + str(minorconfig) # IPMI  command to set server bios config details
        cmdinterface = interface + ' ' + ipmi_cmd
            
        bios_config = parse_set_bios_config(cmdinterface, "setserverbiosconfig")
        
        if bios_config is None or not bios_config: # Check empty or none
            return set_failure_dict("Empty data for setbiosconfig",completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("setbiosconfig Exception: ", e),completion_code.failure)

    return bios_config   

def get_bios_code(serverid, version):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48",completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)

        if "Failed:" in interface:
            return set_failure_dict(interface,completion_code.failure)
        
        ipmi_cmd = 'ocsoem bioscode' + ' ' + version # IPMI  command to get server bios code details
    
        cmdinterface = interface + ' ' + ipmi_cmd
            
        bios_code = parse_bioscode(cmdinterface, "getserverbioscode")
        
        if bios_code is None or not bios_code: # Check empty or none
            return set_failure_dict("Empty data for getserverbioscode",completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("getbioscode Exception: ", e),completion_code.failure)

    return bios_code    
    

def parse_get_bios_config(interface, command):    
    try:        
        completionstate = True
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        biosconfigrsp = {}
        biosconfigrsp["AvailableConfigurations"] = {}
        
        if(output['status_code'] == 0):
            biosdata = output['stdout'].split('\n\n')             
            #Gets current and chosen config details from output
            current_config_details = biosdata.pop(0)
            currentconfig = current_config_details.split('\n')
            
            for cfgval in currentconfig:
                if "Current BIOS Configuration" in cfgval:
                    biosconfigrsp["Current BIOS Configuration"] = cfgval.split(":")[-1]
                elif "Chosen BIOS Configuration" in cfgval:
                    biosconfigrsp["Chosen BIOS Configuration"] = cfgval.split(":")[-1]
                elif "Available Configuration Name" in cfgval:
                    biosconfigrsp["AvailableConfigName"] = cfgval.split(":")[-1]
            
            # Gets all available configuration details
            for availablecfg in biosdata:
                configdata = availablecfg.split('\n') 
                
                config_value= filter(None, configdata)
                # Skipping empty lists if any
                if  len(config_value) == 0:
                    break
                else: 
                    if config_value[0].lower().strip('-').strip() == "Available Configurations".lower():  
                        available_config_data = availablecfg.split('*')                
                        available_config_value= filter(None, available_config_data)   
                        config_info = get_config_data(available_config_value) 
                        
                        if completion_code.cc_key in config_info.keys():
                            completionstate &= False
                            biosconfigrsp["AvailableConfigurations"] = None
                        else:
                            biosconfigrsp["AvailableConfigurations"] = config_info
                              
             
            if(completionstate):
                biosconfigrsp[completion_code.cc_key] = completion_code.success
            else:
                biosconfigrsp[completion_code.cc_key] = completion_code.failure
                                 
            return biosconfigrsp
        
        else:
            error_data = output['stderr'].split('\n')            
            biosconfigrsp[completion_code.cc_key] = completion_code.failure 
            
            for data in error_data:
                if "Error" in data:
                    biosconfigrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    biosconfigrsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
            return biosconfigrsp
        
    except Exception,e:
        #log.exception("GetserverBiosConfig: Exception error:" ,e) 
        return set_failure_dict(("parse_get_bios_config() Exception: ",e),completion_code.failure)
    
def get_config_data(configdata):
    try:
        config_rsp = {}
        config_id = 1  
        
        for value in configdata:
            config_data = value.split('\n')       
            config_info = filter(None, config_data) # Removes empty strings   
            # Skipping empty lists if any 
            if  len(config_info) == 0:
                break   
            
            config_rsp[config_id] = {}                           
            for value in config_info:                   
                if "ConfigName" in value:
                    config_rsp[config_id]["Config Name"] = value.split(":")[-1].strip()
                elif "ConfigValue" in value:
                    config_rsp[config_id]["Config Value"] = value.split(":")[-1].strip()
            config_id = config_id + 1
            
    except Exception,e:
        config_rsp[completion_code.cc_key] = completion_code.failure
        config_rsp[completion_code.desc] = "Get available config data, Exception: ", e
    
    return config_rsp 
        
def parse_set_bios_config(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        setbiosconfigrsp = {}
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].split('\n') 
            completionstate = sdata.pop(0)
            if "Completion Status" in completionstate:
                setbiosconfigrsp[completion_code.cc_key] = completionstate.split(":")[-1]    
            return setbiosconfigrsp        
        
        else:
            error_data = output['stderr'].split('\n')            
            setbiosconfigrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    setbiosconfigrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    setbiosconfigrsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
            return setbiosconfigrsp       
        
    except Exception, e:
        #log.exception("Exception error is: ",e)
        return set_failure_dict(("parse_set_bios_config() Exception ",e),completion_code.failure)
    
def parse_bioscode(interface, command):    
    try:        
        output = call_ipmi(interface, command)  
        
        if "ErrorCode" in output:
            return output

        biosrsp = {}
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].split('\n') 
            biosrsp["Bios Code"] = str(sdata[0]) 
            biosrsp[completion_code.cc_key] = completion_code.success
               
            return biosrsp
        else:
            error_data = output['stderr'].split('\n')            
            biosrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    biosrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    biosrsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
            return biosrsp  
              
    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        #print "Exception: ", e
        return set_failure_dict(("ParseGetBiosCodeResult() Exception: ",e),completion_code.failure)
    
