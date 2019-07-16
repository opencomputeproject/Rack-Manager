# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
from utils import *
from lib_utils import *
from ipmicmd_library import *
from manage_powerport import *
from bladenextboot_lib import get_nextboot 
from mgmt_switch import mgmt_switch

class server_type:
    """
    Enumeration definition for the type of server in the slot.
    """
    
    map = {
        0 : "C2010",
        1 : "J2010",
        2 : "F2010",
        3 : "T2010",
        4 : "C2020",
        5 : "OEM"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        if (self.value in server_type.map):
            return server_type.map[self.value]
        else:
            return "Unknown ({0})".format (self.value)
    
    def __repr__ (self):
        return str (self)
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return str (self) == other
        elif isinstance (other, server_type):
            return self.value == other.value
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result

class server_type_enum:
    """
    Enumeration constants for the server type.
    """
    
    C2010 = server_type (0)
    J2010 = server_type (1)
    F2010 = server_type (2)
    T2010 = server_type (3)
    C2020 = server_type (4)
    OEM = server_type (5)
    
def get_server_control_interface (serverid, port = 623):
    ip = get_hostname_by_serverid (serverid)
    conn = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    
    request = bytearray ([
        0x06, 0x00, 0xff, 0x07,  # RCMP header
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x09, #IPMI session header
        0x20, 0x18, 0xc8, 0x81, 0x04, 0x38,  # IPMI header
        0x0e, 0x04, # Get Channel Authentication Capabilities command
        0x31    # Checksum
    ])
    conn.sendto (request, (ip, port))
    
    conn.settimeout (2)
    response = conn.recvfrom (256)
    
    data = bytearray (response[0])
    completion = data[20]
    if (not completion == 0):
        raise RuntimeError ("IPMI command failed with code 0x{:02X}.".format (completion))
    
    serv_type = server_type (data[24] >> 2)
    oem = data[25] + (data[26] << 8) + (data[27] << 16)
    intf = data[28]
    group = (intf & 0x38) >> 3
    slot = intf & 0x7
    ctrl = (intf & 0xc0) >> 6
    
    return (
        oem,    # OEM identfier
        (group * 6) + (slot + 1),   # Slot ID
        "IPMI" if (ctrl == 0) else "REST",   # Control interface type
        serv_type   # Server type
    )
    
def get_server_data(serverid):
    try:
        interface = get_ipmi_interface(serverid) 
        
        cmdinterface = interface + ' ocsoem redfish server'
        
        server_data = parse_server_data(cmdinterface)        
        # Check empty or none
        if server_data is None or not server_data:
            return set_failure_dict("getserverdata response empty", completion_code.failure)
            
    except Exception, e:
        return set_failure_dict("get_server_data - Exception: {0}".format(e), 
                                completion_code.failure)
            
    return server_data

def parse_server_data(interface):
    try:
        output = call_ipmi(interface, "getserverdata") 
                
        if "ErrorCode" in output:
            return output 
        
        serverdata = {}
        
        if(output['status_code'] == 0) or (output['stdout']):  
            sdata = output['stdout'].split('\n')   
            for value in sdata:
                if "Slot Id" in value:
                    serverdata["Slot Id"] = value.split(":")[-1].strip()
                elif "GUID" in value:
                    serverdata["GUID"] = value.split(":")[-1].strip()
                elif "MAC1" in value:
                    serverdata["MAC1"] = value.split(":")[-1].strip()                   
                          
            return set_success_dict (serverdata)
        
        else:            
            errorData = output['stderr'].split('\n')            
            errorData = filter(None, errorData)            
            serverdata[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    serverdata[completion_code.desc] = data.split(":")[-1].strip()
                elif completion_code.cc_key in data:
                    serverdata[completion_code.ipmi_code] = data.split(":")[-1].strip()
                else:
                    serverdata[completion_code.desc] = data.strip() 
                    break 
                
            if serverdata[completion_code.desc] == "":
                serverdata[completion_code.desc] = errorData.strip()
                
            return serverdata            
        
    except Exception,e:
        return set_failure_dict("get_server_data - Exception: {0}".format(e), 
                                completion_code.failure)        

def get_server_guid(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return "Invalid server-id {0}".format(serverid)
        else:            
            interface = get_ipmi_interface(serverid)
        
        # Construct IPMI command
        cmdinterface = interface + ' ' + "ocsoem guid" 
        output = call_ipmi(cmdinterface, "guid")  
        
        if "ErrorCode" in output:
            return "Failure" 
        
        if(output['status_code'] == 0):
            return output['stdout'].strip()
        else:
            return "Failure" 
                
    except Exception, e:
        print "get_server_guid - Exception: {0}".format(e)
        return "Exception" 
    
def get_server_mac(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return "Invalid server-id {0}.".format(serverid)
        else:            
            interface = get_ipmi_interface(serverid)
        
        # Construct IPMI command
        cmdinterface = interface + ' ' + "ocsoem nicinfo 1"
        output = call_ipmi(cmdinterface, "mac")  
        
        if "ErrorCode" in output:
            return "Failure"
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].strip()          
            return sdata[:-1]
        else:
            return "Failure"
                
    except Exception, e:
        print "get_server_mac - Exception: {0}".format(e)
        return "Exception" 

def system_info_call(bladeId):
    try:
        interface = get_ipmi_interface(bladeId) 
        
        cmdinterface = interface + ' ocsoem redfish systeminfo'
        
        # Get blade host name 
        hostvalue = interface.split(" ")[4]
        
        systeminfo = parse_system_info_call(bladeId, cmdinterface, hostvalue)    
    
        # Check empty or none
        if systeminfo is None or not systeminfo:
            return set_failure_dict("System info response empty", completion_code.failure)
            
    except Exception, e:
        return set_failure_dict("system_info_call - Exception: {0}".format(e), 
                                completion_code.failure)
            
    return systeminfo
    
def parse_system_info_call(bladeId, interface, hostname):    
    try:                
        output = call_ipmi(interface, "IpmiSystem") 
                
        if "ErrorCode" in output:
            return output           

        completionstate = True
        
        bladeRsp = {}
        bladeRsp["Server"] = {}
        bladeRsp["Server"]["ProcessorSummary"] = {}   
        bladeRsp["Server"]["MemorySummary"] = {}     
        bladeRsp["Server"]["ProcessorSummary"]["Count"] = 2
        bladeRsp["Server"]["ProcessorSummary"]["Status"] = {}
        
        processorstatus = {} 

        bladestatus = {} 
        memorystatus = {"State":"Enabled", "Health":"Ok", "HealthRollUp":"Ok"}        
        bladeRsp["Server"]["MemorySummary"]["Status"] = memorystatus              
        
        processorTypeList = []
        processorStateList = []
        
        nextboot = ""
        nextboot_colle = get_nextboot(bladeId)
        
        if (nextboot_colle[completion_code.cc_key] == completion_code.success):
            nextboot = nextboot_colle["Next boot is"]

        if(output['status_code'] == 0):
                #log.info("Completion Code: %s"%Config.completioncode[0])
                sdata = output['stdout'].split('\n')                
                bladeRsp["Id"] =  str(bladeId)
                bladeRsp["Name"]=  "Server" + str(bladeId)
                bladeRsp["HostName"]=  hostname 
                bladeRsp["ChassisId"] = "ChassisId"
                if nextboot and not nextboot.isspace() and nextboot.lower().strip() != "no override":
                    bladeRsp["Boot_BootSourceOverrideEnabled"] = "True"                    
                else:
                    bladeRsp["Boot_BootSourceOverrideEnabled"] = "False"
                    
                bladeRsp["Boot_BootSourceOverrideTarget"] = nextboot 
                
                for value in sdata:
                    # FRU details    
                    if "Fru error" in value:
                        completionstate &= False     
                        bladeRsp[completion_code.desc] += ' - ' + value.strip()    
                    elif "Chassis Type" in value:
                        bladeRsp["SystemType"] = value.split(":")[-1].strip() 
                    elif "Product Asset Tag" in value:
                        bladeRsp["AssetTag"] = value.split(":")[-1].strip()
                    elif "Product Manufacturer" in value:
                        bladeRsp["Manufacturer"] = value.split(":")[-1].strip()
                    elif "Product Name" in value:
                        bladeRsp["Model"] = value.split(":")[-1].strip()
                    elif "Chassis Part Number" in value:
                        bladeRsp["SKU"] = value.split(":")[-1].strip()
                    elif "Board Serial" in value:
                        bladeRsp["SerialNumber"] = value.split(":")[-1].strip()
                    elif "Board Part Number" in value:
                        bladeRsp["PartNumber"] = value.split(":")[-1].strip()
                    elif "FRU Device Description" in value:            
                        bladeRsp["Description"] = value.split(":")[-1].strip()
                    elif "Board Product" in value:            
                        bladeRsp["Server"]["HWVersion"] = value.split(":")[-1].strip()
                    # GUID Value
                    elif "GUID" in value:  
                        guid = value.split(":")[-1].strip()          
                        bladeRsp["UUID"] = guid
                        if guid.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get UUID'    
                    elif "MAC1" in value:
                        bladeRsp["Mac Address"] = value.split(":")[-1].strip()

                    # LED Status
                    elif "LED Status" in value:  
                        ledstate =  value.split(":")[-1].strip()        
                        bladeRsp["Server"]["IndicatorLED"] = ledstate
                        if ledstate.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get LED State'
                    # Power State                    
                    elif "Power State" in value:            
                        powerstate = value.split(':')[-1]
                        if 'on' in str(powerstate).lower():
                            bladeRsp["Server"]["PowerState"] = "On"
                            bladestatus["State"] = "On"
                        elif "off" in str(powerstate).lower():
                            bladeRsp["Server"]["PowerState"] = "Off"
                            bladestatus["State"] = "Off"
                        elif "failure" in str(powerstate).lower():
                            bladeRsp["Server"]["PowerState"] = "Failure"
                            bladestatus["State"] = "Failure"
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get Power State'
                        else:
                            bladeRsp["Server"]["PowerState"] = "Unknown"
                            bladestatus["State"] = "Unknown" 
                                            
                        bladestatus["Health"] = "Ok"
                        bladestatus["HealthRollUp"] = "Ok"
                        
                    # BIOS Version 
                    elif "BIOS Version" in value: 
                        version =  value.split(":")[-1].strip()
                        bladeRsp['Server']['BiosVersion'] = version
                        if version.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get BIOS Version'
                    
                    # CPLD Version 
                    elif "CPLD Version" in value: 
                        version =  value.split(":")[-1].strip()
                        bladeRsp['Server']['CpldVersion'] = version
                        if version.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get CPLD Version'
                    
                    # BMC Version 
                    elif "BMC Version" in value: 
                        version =  value.split(":")[-1].strip()
                        bladeRsp['Server']['BMCVersion'] = version
                        if version.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get BMC Version'
                    
                    # Processor Model 
                    elif "Processor0 Type" in value:
                        processorTypeList.append(value.split(":")[-1].strip())
                    elif "Processor1 Type " in value:
                        processorTypeList.append(value.split(":")[-1].strip())                        
                   
                    elif "Processor0 State" in value:
                        processorStateList.append(value.split(":")[-1].strip())
                    elif "Processor1 State" in value:
                        processorStateList.append(value.split(":")[-1].strip())
                        
                    elif "TotalSystemMemoryGiB" in value:
                        sysmemory = value.split(":")[-1].strip()  
                        bladeRsp["Server"]["MemorySummary"]["TotalSystemMemoryGib"] = sysmemory
                        if sysmemory.lower() == "failure":
                            completionstate &= False
                            #bladeRsp[completion_code.desc] += ' - Failed to get System Memory capacity'
                    
                
                if len(processorTypeList) == 0:
                    completionstate &= False
                    bladeRsp[completion_code.desc] += ' - Failed to get Processor Summary'
                else:       
                    model = ",".join(processorTypeList)
                    
                    model1, model2 = model.split(",")
                    
                    if model1.lower().strip() == model2.lower().strip():
                        bladeRsp["Server"]["ProcessorSummary"]["Model"] = model1
                    else:
                        bladeRsp["Server"]["ProcessorSummary"]["Model"] = "Cpu0 - " + model1 + "," + "Cpu1 - " + model2
                
                if len(processorStateList) == 0:
                    completionstate &= False
                    bladeRsp[completion_code.desc] += ' - Failed to get Processor State'
                else:
                    state = ",".join(processorStateList)
                    
                    state1, state2 = state.split(",")
                    if state1.lower().strip() == state2.lower().strip():
                        processorstatus["State"] = state2
                    else:
                        processorstatus["State"] = "Cpu0 - " + state1 + "," + "Cpu1 - " + state2
                        
                    processorstatus["Health"] = "Ok"
                    processorstatus["HealthRollUp"] = "Ok"
                        
                    bladeRsp["Server"]["ProcessorSummary"]["Status"] = processorstatus 
                    
                bladeRsp["Server"]["Status"] = bladestatus      
                
                if completionstate:
                    bladeRsp[completion_code.cc_key] = completion_code.success
                else:
                    bladeRsp[completion_code.cc_key] = completion_code.failure
                                                
                return bladeRsp
        else:               
            errorData = output['stderr'].split('\n')
            
            errorData = filter(None, errorData)
            bladeFailedRsp = {}
            bladeFailedRsp[completion_code.cc_key] = completion_code.failure
                        
            for data in errorData:
                if "Error" in data:
                    bladeFailedRsp[completion_code.desc] = data.split(":")[-1].strip()
                elif "Completion Code" in data:
                    bladeFailedRsp[completion_code.ipmi_code] = data.split(":")[-1].strip()
                else:
                    bladeFailedRsp[completion_code.desc] = data.strip() 
                    break 
                
            if bladeFailedRsp[completion_code.desc] == "":
                bladeFailedRsp[completion_code.desc] = errorData.strip()
                                       
            return bladeFailedRsp
          
    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        return set_failure_dict("parse_system_info_call - Exception: {0}".format(e), 
                                completion_code.failure)

def system_range(mode):
    """ Get port ID range based on mode
    """
    
    if mode.lower() == "pmdu":
        return (1, 48)
    elif mode.lower() == "standalone":
        return (1, 24)
    elif mode.lower() == "row":
        return (25, 48)
    else:
        return (-1, -1)
    
def server_info(mode, info = False, id = 0, inventory = False):
    try:
        server_rsp = {}
        
        switch = mgmt_switch()
        
        if id == 0:
            power_state = powerport_get_all_port_status(True)
            server_presence = powerport_get_all_port_presence(True)
            port_link_state = switch.get_all_port_link_state()
            switch.logout()
        else:
            power_state = powerport_get_port_status(id, "pdu", True)
            server_presence = powerport_get_port_presence(id, "pdu", True)
            port_link_state = switch.get_all_port_link_state()
            switch.logout()
         
        if power_state[completion_code.cc_key] == completion_code.success:
            power_state.pop(completion_code.cc_key, None)
            power_state = dict(sorted(power_state.items()))
        else:
            return set_failure_dict("Failed to get port status using GPIO Library", completion_code.failure)
        
        ''' Get the link state for all switch ports.'''
        if port_link_state[completion_code.cc_key] == completion_code.success:
            port_link_state.pop(completion_code.cc_key,None)
            port_link_state = dict(sorted(port_link_state.items()))
        else:
            return set_failure_dict("Failed to get all port link state using mgmt_switch",completion_code.failure)
        
        if server_presence[completion_code.cc_key] == completion_code.success:
            server_presence.pop(completion_code.cc_key, None)
            server_presence = dict(sorted(server_presence.items()))
        else:
            return set_failure_dict("Failed to get server presence using GPIO Library", completion_code.failure)
        
        if mode.lower() == "pmdu" or mode.lower() == "standalone":
            device_type = "Server"
        elif mode.lower() == "row":
            device_type = "Manager"
        else:
            device_type = "--"
            
        if id == 0: 
            port_range = system_range(mode)  
        else:
            port_range = (id, id)
            
        if port_range[0] == -1:
            return set_failure_dict("Invalid mode {0}".format(mode), completion_code.failure)
                      
        for (key, value) in power_state.items():
            if key < port_range[0]:
                continue
            if key > port_range[1]:
                break
                        
            server_rsp[key] = {}
            server_rsp[key]["Port Id"] = key 
            server_rsp[key]["Type"] = device_type
            server_rsp[key]["Port State"] = value
            server_rsp[key]["Present"] = server_presence[key]
                        
        if info == True and device_type != "Manager":  
            for key, value in port_link_state.items():
                if key < port_range[0]:
                    continue
                if key > port_range[1]:
                    break
                
                if server_presence[key].lower() == "true" and port_link_state[key] == "Up": 
                    server_data = get_server_data(int(key))
                    if completion_code.cc_key in server_data.keys() and server_data[completion_code.cc_key] == completion_code.failure:
                        server_rsp[key]["GUID"] = completion_code.failure
                        server_rsp[key]["MAC"] = completion_code.failure
                        if inventory == True:
                            server_rsp[key]["Slot Id"] = completion_code.failure
                    else:
                        server_rsp[key]["GUID"] = server_data["GUID"]
                        server_rsp[key]["MAC"] = server_data["MAC1"]
                        if inventory == True:
                            server_rsp[key]["Slot Id"] = server_data["Slot Id"]
                else:
                    server_rsp[key]["GUID"] = "--"
                    server_rsp[key]["MAC"] = "--" 
                    if inventory == True:
                        server_rsp[key]["Slot Id"] = "--"
    
    except Exception, e:
        #log_err("Exception to get server _info ",e)
        return set_failure_dict("server_info - Exception: {0}".format(e), completion_code.failure) 
    
    return set_success_dict(server_rsp)

def manager_inventory(mode):
    try:
        inventoryrsp = server_info(mode, True, 0, True)
                
        inventory = {}
        i = 0;
        if (completion_code.cc_key in inventoryrsp.keys()) and (inventoryrsp[completion_code.cc_key] == completion_code.success):
            inventoryrsp.pop(completion_code.cc_key, None)
            for k, v in sorted(inventoryrsp.iteritems()):            
                if isinstance(v, dict): 
                    subdict = {}
                    i = i+1
                    for  k , val in v.items():
                        if k == "Slot Id":
                            subdict['Slot Id'] = val
                        elif k == "Present":
                            subdict['Port Present'] = val
                        elif k == "Port State":
                            subdict['Port State'] = val
                        elif k == "Port Id":
                            subdict['BMC SW Port'] = val
                        elif k == "MAC":
                            subdict['MAC'] = val
                        elif k == "GUID":
                            subdict['GUID'] = val                    
                           
                    inventory.update({i:subdict})                        
                    
            inventory[completion_code.cc_key] = completion_code.success
            return inventory
        else:
            return set_failure_dict("Failed to get inventory data", completion_code.failure)
            
    except Exception, e:
        #log_err("Exception to get server _info ",e)
        return set_failure_dict("manager_inventory - Exception: {0}".format(e), completion_code.failure)

def get_system_type(serverid):
    """ Return server type using IPMITool
    """
    try:
        result = {}
        
        out = get_server_control_interface(serverid)
        
        result["OEM ID"] = out[0]
        result["Control Interface Type"] = out[2]
        result["System Type"] = out[3]
        
        return set_success_dict(result)
    
    except Exception, e:
        return set_failure_dict("get_system_type - Exception: {0}".format(e), completion_code.failure)
    
