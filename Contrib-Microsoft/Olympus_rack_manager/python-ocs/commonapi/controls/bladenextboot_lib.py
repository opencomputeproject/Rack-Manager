# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import * 

class boot_type:
    none = "0x00"
    pxe = "0x04"
    disk = "0x08"
    bios = "0x18"
    floppy = "0x3C"

class persistent:
    legacy_persistent = "0xC0"
    legacy_nonpersistent = "0x80"
    efi_persistent = "0xE0"
    efi_nonpersistent = "0xA0"
                                                
def get_nextboot(serverid):
    try:
        interface = get_ipmi_interface(serverid)
        
        ipmi_cmd = 'chassis bootparam get 5'  # IPMI  command to get next boot details
            
        cmdinterface = interface + ' ' + ipmi_cmd
            
        get_next_boot = parse_get_nextboot_result(cmdinterface, "getnextboot")
        
        if get_next_boot is None or not get_next_boot: # Check empty or none
            return set_failure_dict("Empty data for getnetxtboot", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict("get_nextboot: Exception {0}".format(e), completion_code.failure)

    return get_next_boot 

def set_nextboot(serverid, boottype, mode=0, ispersist=0):
    try:
        persistent_val = ''
        if mode == 0 and ispersist == 0:
            persistent_val = persistent.legacy_nonpersistent
        elif mode == 0 and ispersist == 1:
            persistent_val = persistent.legacy_persistent
        elif mode == 1 and ispersist == 0:
            persistent_val = persistent.efi_nonpersistent
        elif mode == 1 and ispersist == 1:
            persistent_val = persistent.efi_persistent
        
        boot_value = ''        
        if boottype == "none":
            boot_value = boot_type.none
        elif boottype == "pxe":
            boot_value = boot_type.pxe
        elif boottype == "disk":
            boot_value = boot_type.disk
        elif boottype == "bios":
            boot_value = boot_type.bios
        elif boottype == "floppy":
            boot_value = boot_type.floppy
                
        interface = get_ipmi_interface(serverid, ["raw","0x00","0x08","0x05", persistent_val,boot_value , "0x00", "0x00", "0x00"])         
            
        set_next_boot = parse_set_nextboot_result(interface, "setnextboot")
        
        if set_next_boot is None or not set_next_boot: # Check empty or none
            return set_failure_dict("Empty data for setnetxtboot", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict("set_nextboot: Exception {0}".format(e), completion_code.failure)

    return set_next_boot 

# Parse setnextboot output
def parse_set_nextboot_result(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        setnextboot = {}
        
        if(output['status_code'] == 0):
                setnextboot[completion_code.cc_key] = completion_code.success 
                return setnextboot        
        else:
            error_data = output['stderr']
            return set_failure_dict (error_data.split (":")[-1].strip ())       
        
    except Exception, e:
        #log.exception("serverNextBoot Command: %s Exception error is: %s ", command, e)
        return set_failure_dict(("SetNextBoot: parse_set_nextboot_result() Exception:", e) , completion_code.failure) 

# Parse getnextboot output
def parse_get_nextboot_result(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        getnextboot = {}
        
        if(output['status_code'] == 0):                
                getnextbootopt  = output['stdout'].split('\n')  

                for bootval in getnextbootopt:
                    if "Boot Device Selector" in bootval:
                        boot = bootval.split (":")[-1]
                        getnextboot["Next boot is"] = boot 
                        getnextboot["BootSourceOverrideTarget"] = boot   
                    elif "BIOS PC Compatible (legacy) boot" in bootval:
                        getnextboot["BootSourceOverrideMode"] = "Legacy"
                    elif "BIOS EFI boot" in bootval:
                        getnextboot["BootSourceOverrideMode"] = "UEFI"                        
                    elif "Options apply to only next boot" in bootval:
                        getnextboot["BootSourceOverrideEnabled"] = "Once"
                    elif "Options apply to all future boots" in bootval:
                        getnextboot["BootSourceOverrideEnabled"] = "Persistent"
                    
                getnextboot[completion_code.cc_key] = completion_code.success     
                return getnextboot        
        else:
            error_data = output['stderr']            
            getnextboot[completion_code.cc_key] = completion_code.failure           
            getnextboot[completion_code.desc] = error_data.split(":")[-1]                                                  
            return getnextboot       
        
    except Exception, e:
        #log.exception("serverNextBoot Command: %s Exception error is: %s ", command, e) 
        #print "serverNextBoot: Failed to parse setnextboot output. Exception: " ,e          
        return set_failure_dict(("GetNextBoot: parse_get_nextboot_result() Exception ",e) , completion_code.failure) 

