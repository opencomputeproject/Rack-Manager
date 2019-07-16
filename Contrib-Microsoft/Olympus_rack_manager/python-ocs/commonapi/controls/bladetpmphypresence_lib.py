# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import * 

def get_tpm_physical_presence(serverid):
    try:
        interface = get_ipmi_interface(serverid) 
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'ocsoem gettpmphypresence'  # IPMI  command to get TPM Physical presence
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        get_tpm_presence = parse_get_tpmphysical_presence(cmdinterface, "gettpmphysicalpresence")
        
        if get_tpm_presence is None or not get_tpm_presence: # Check empty or none
            return set_failure_dict("Empty data for gettpmphysicalpresence", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception ", e), completion_code.failure)

    return get_tpm_presence 

def set_tpm_physical_presence(serverid, presence=0): #default is false
    try:
        if(presence == 0):
            presence = 'false'
        elif(presence == 1):
            presence = 'true'
        else:
            return set_failure_dict("Invalid presence value", completion_code.failure)
        
        interface = get_ipmi_interface(serverid) 
    
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)         
        
        ipmi_cmd =  'ocsoem settpmphypresence {0}'.format( presence )# IPMI  command to set TPM Physical presence
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        set_tpm_presence = parse_set_tpmphysical_presence(cmdinterface, "settpmphysicalpresence")
        
        if set_tpm_presence is None or not set_tpm_presence: # Check empty or none
            return set_failure_dict("Empty data for settpmphysicalpresence", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception ", e), completion_code.failure)
    
    return set_tpm_presence 

           
def parse_get_tpmphysical_presence(interface, command):    
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        getTpmPhyPresence = {}
        
        if(output['status_code'] == 0):
            tpmPresenceData = output['stdout'].split('\n') 
            tpmpresence = tpmPresenceData.pop(0)
            
            if "Physical Presence Flag" in tpmpresence:
                getTpmPhyPresence["PhysicalPresence"] = tpmpresence.split(":")[-1] 
                               
            getTpmPhyPresence[completion_code.cc_key] = completion_code.success
            return getTpmPhyPresence
        
        else:
            errorData = output['stderr'].split('\n')            
            getTpmPhyPresence[completion_code.cc_key] = completion_code.failure

            for data in errorData:
                if "Error" in data:
                    getTpmPhyPresence[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    getTpmPhyPresence[completion_code.ipmi_code] = data.split(":")[-1]   
                                                         
            return getTpmPhyPresence
        
    except Exception, e:
        #log.exception("GetserverTpmPhysicalPresence: Exception error: %s " %e) 
        return set_failure_dict(("parse_get_tpmphysical_presence() Exception: ", e), completion_code.failure)

def parse_set_tpmphysical_presence(interface, command):    
    try:        
        output = call_ipmi(interface, command)
        
        if "ErrorCode" in output:
            return output
        
        setTpmPresenceRsp = {}
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].split('\n') 
            completionState = sdata.pop(0)
            
            if "Completion Status" in completionState:
                setTpmPresenceRsp[completion_code.cc_key] = completionState.split(":")[-1]    
            
            return setTpmPresenceRsp
        
        else:
            errorData = output['stderr'].split('\n')            
            setTpmPresenceRsp[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    setTpmPresenceRsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    setTpmPresenceRsp[completion_code.ipmi_code] = data.split(":")[-1]   
                                                         
            return setTpmPresenceRsp       
        
    except Exception, e:
        #log.exception("SetserverTpmPhyPresence: Exception error is: %s " %e)     
        return set_failure_dict(("parse_set_tpmphysical_presence() Exception: ", e) , completion_code.failure)       
