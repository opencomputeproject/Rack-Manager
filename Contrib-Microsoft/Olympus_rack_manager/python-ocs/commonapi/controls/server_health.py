# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipmicmd_library import *
from bladeinfo_lib import *
from bladethermal_lib import fan_sub_parser

def get_server_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
             
        ipmi_cmd = 'ocsoem redfish health'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "Server health")            
                
        healthrsp = {}
        
        if completion_code.cc_key in output:
            healthrsp[completion_code.cc_key] = completion_code.failure
            healthrsp[completion_code.desc] = "get server health ipmi call error "
            return healthrsp 
        
        if(output['status_code'] == 0) or (output['stdout']):  
            healthrsp =  parse_health_response(output['stdout'])    
            return healthrsp
        
        else:            
            errorData = output['stderr'].split('\n')            
            errorData = filter(None, errorData)            
            healthrsp[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    healthrsp[completion_code.desc] = data.split(":")[-1].strip()
                elif completion_code.cc_key in data:
                    healthrsp[completion_code.ipmi_code] = data.split(":")[-1].strip()
                else:
                    healthrsp[completion_code.desc] = data.strip() 
                    break 
                
            if healthrsp[completion_code.desc] == "":
                healthrsp[completion_code.desc] = errorData.strip()
                
            return healthrsp
                                       
    except Exception,e:
        #log.exception("Exception error is: %s " %e)
        healthrsp[completion_code.cc_key] = completion_code.failure
        healthrsp[completion_code.desc] = "Get server health, Exception: ", e
        return healthrsp  
    
def parse_health_response(output):
    try: 
        completionstate = True
        healthrsp = {}
        healthrsp[" Server Information"] = {}
        healthrsp["CPU Information"] = {}
        healthrsp["Memory Information"] = {}   
        healthrsp["PCIE Information"] = {}     
        healthrsp["Temperature Information"] = {}
        healthrsp["FRU Information"] = {}
        healthrsp["Fan Information"] = {}
        healthrsp["Sensor Information"] = {}          
        
        #populating temperatures data
        health = output.split('$')

        healthdata = filter(None, health) #Remove empty data
        
        if len(healthdata) == 0:
            healthrsp[completion_code.cc_key] = completion_code.failure
            healthrsp[completion_code.desc] = "health data is empty"
            return healthrsp 
        else:
            for value in healthdata:
                object_data = value.split('\n')
                object_value= filter(None, object_data)
                # Skipping empty lists if any
                if  len(object_value) == 0:
                    break
                else:
                    if object_value[0].lower().strip('-').strip() == "fru information":                        
                        fru_info = get_fru_info(object_value)   
                        if completion_code.cc_key in fru_info.keys():
                            value = fru_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                            
                        healthrsp["FRU Information"] = fru_info
                        
                    elif object_value[0].lower().strip('-').strip() == "cpu information":                        
                        cpu_info = get_cpu_info(object_value)                        
                        if completion_code.cc_key in cpu_info.keys():
                            value = cpu_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                        healthrsp["CPU Information"] = cpu_info
                        
                    elif object_value[0].lower().strip('-').strip() == "server information":                        
                        server_info = get_server_info(object_value)   
                                             
                        if completion_code.cc_key in server_info.keys():
                            value = server_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                                
                        healthrsp[" Server Information"] = server_info
                                
                    elif object_value[0].lower().strip('-').strip() == "memory information":                        
                        memory_data = value.split('*')                
                        memory_value= filter(None, memory_data)  
                        mem_info = get_memory_health(memory_value)   
                        
                        if completion_code.cc_key in mem_info.keys():
                            value = mem_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                                
                        healthrsp["Memory Information"] = mem_info 
                        
                    elif object_value[0].lower().strip('-').strip() == "pcie information":                        
                        pcie_data = value.split('*')                
                        pcie_value= filter(None, pcie_data)  
                        pcie_info = get_pcie_info(pcie_value)   
                        
                        if completion_code.cc_key in pcie_info.keys():
                            value = pcie_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                            
                        healthrsp["PCIE Information"] = pcie_info 
                        
                    elif object_value[0].lower().strip('-').strip() == "fan information":   
                        del object_value[0] # deleting first record which is "-----Fan Information-------" string                     
                        fan_info = get_sensor_info(object_value, 'fan')   
                        
                        if completion_code.cc_key in fan_info.keys():
                            value = fan_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                            
                        healthrsp["Fan Information"] = fan_info
                        
                    elif object_value[0].lower().strip('-').strip() == "temperature information":   
                        del object_value[0] # deleting first record which is "-----Temperature Information-------" string            
                        temp_info = get_sensor_info(object_value)    
                                         
                        if completion_code.cc_key in temp_info.keys():
                            value = temp_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                                
                        healthrsp["Temperature Information"] = temp_info
                        
                    elif object_value[0].lower().strip('-').strip() == "sensor information":   
                        del object_value[0] # deleting first record which is "-----Sensor Information-------" string            
                        sensor_info = get_sensor_info(object_value)    
                                         
                        if completion_code.cc_key in sensor_info.keys():
                            value = sensor_info.pop(completion_code.cc_key,None)                        
                            if value == completion_code.failure:
                                completionstate &= False
                                
                        healthrsp["Sensor Information"] = sensor_info
                    
    except Exception,e:
        #log.exception("Exception error is: %s " %e)
        healthrsp[completion_code.cc_key] = completion_code.failure
        healthrsp[completion_code.desc] = "Get server health, Exception: ", e
        return healthrsp 
    
    if completionstate:
        healthrsp[completion_code.cc_key] = completion_code.success
    else:
        healthrsp[completion_code.cc_key] = completion_code.failure
    return healthrsp

def get_memory_health(memory):
    try:
        completionstate = True
        mem_rsp = {}
        dimm_id = 1  
        
        for value in memory:
            dimm_data = value.split('\n')       
            dimm_data = filter(None, dimm_data) # Removes empty strings   
            # Skipping empty lists if any 
            if  len(dimm_data) == 0:
                break   
            if len(dimm_data) == 2:
                continue
            
            mem_rsp[dimm_id] = {}                           
            for value in dimm_data:                   
                if "Completion Code:" in value:
                    completionstate &= False
                elif "DimmId" in value:
                    mem_rsp[dimm_id]["Dimm Id"] = value.split(":")[-1].strip() 
                elif "Dimm Type" in value:
                    mem_rsp[dimm_id]["Dimm Type"] = value.split(":")[-1].strip()
                elif "Dimm speed" in value:
                    mem_rsp[dimm_id]["Dimm Speed"] = value.split(":")[-1].strip()  
                elif "Dimm size" in value:
                    mem_rsp[dimm_id]["Dimm Size"] = value.split(":")[-1].strip()  
                elif "Dimm Status" in value:
                    mem_rsp[dimm_id]["Dimm Status"] = value.split(":")[-1].strip()
                elif "Voltage" in value:
                    mem_rsp[dimm_id]["Dimm Voltage"] = value.split(":")[-1].strip()
                elif "Running Speed" in value:
                    mem_rsp[dimm_id]["Running Speed"] = value.split(":")[-1].strip()
            dimm_id = dimm_id + 1
            
    except Exception,e:
        mem_rsp[completion_code.cc_key] = completion_code.failure
        mem_rsp[completion_code.desc] = "Get memory health, Exception: ", e
        return mem_rsp 
    
    if completionstate:
        mem_rsp[completion_code.cc_key] = completion_code.success
    else:
        mem_rsp[completion_code.cc_key] = completion_code.failure
    
    return mem_rsp  

def get_pcie_info(pcie):
    try:
        completionstate = True
        pcie_rsp = {}
        pcie_id = 1  

        for value in pcie:
            pcie_data = value.split('\n')  
            
            pcie_data = filter(None, pcie_data) # Removes empty list   
            # Skipping empty lists if any 
            if  len(pcie_data) == 0:
                break  
            if  len(pcie_data) == 2:
                continue
             
            pcie_rsp[pcie_id] = {}                           
            for value in pcie_data:   
                if "Completion Code:" in value:
                    completionstate &= False
                elif "PCIe Id" in value:
                    pcie_rsp[pcie_id]["PCIe Index"] = value.split(":")[-1].strip() 
                elif "PCIe Status" in value:
                    pcie_rsp[pcie_id]["PCIe Status"] = value.split(":")[-1].strip() 
                elif "PCIe Device" in value:
                    pcie_rsp[pcie_id]["State"] = value.split(":")[-1].strip()
                elif "Device Id" in value:
                    pcie_rsp[pcie_id]["Device Id"] = value.split(":")[-1].strip()  
                elif "Vendor Id" in value:
                    pcie_rsp[pcie_id]["Vendor Id"] = value.split(":")[-1].strip()  
                elif "SubSystem Id" in value:
                    pcie_rsp[pcie_id]["SubSystem Id"] = value.split(":")[-1].strip()
                elif "SubSystem vendor Id" in value:
                    pcie_rsp[pcie_id]["SubSystem vendor Id"] = value.split(":")[-1].strip()
                
            pcie_id = pcie_id + 1
            
    except Exception,e:
        pcie_rsp[completion_code.cc_key] = completion_code.failure
        pcie_rsp[completion_code.desc] = "Get PCIe health, Exception: ", e
        return pcie_rsp 
    
    if completionstate:
        pcie_rsp[completion_code.cc_key] = completion_code.success
    else:
        pcie_rsp[completion_code.cc_key] = completion_code.failure
    
    return pcie_rsp  
    
def get_server_info(server):
    try:
        completionstate = True        
        server_rsp = {}
                                     
        for value in server:   
            if "Completion Code:" in value:
                completionstate &= False
            elif "Server communication type" in value:
                server_type = value.split(":")[-1].strip()
                if server_type == "IPMI":
                    server_rsp["Server Type"] = "C2010"
                elif server_type == "REST":
                    server_rsp["Server Type"] = "J2010"
                else:
                    server_rsp["Server Type"] = "Unknown"
                    completionstate &= False                    
            elif "Slot Id" in value:
                server_rsp["Server Slot ID"] = value.split(":")[-1].strip()
            elif "System Power State" in value:
                server_rsp["Server State"] = value.split(":")[-1].strip()
        
    except Exception,e:
        server_rsp[completion_code.cc_key] = completion_code.failure
        server_rsp[completion_code.desc] = "Get Server Information, Exception: ", e
        return server_rsp 
    
    if completionstate:
        server_rsp[completion_code.cc_key] = completion_code.success
    else:
        server_rsp[completion_code.cc_key] = completion_code.failure
    
    return server_rsp    

def get_cpu_info(cpu):
    try:
        completionstate = True
        
        cpursp = {}
        cpursp["Processor-1"] = {}
        cpursp["Processor-2"] = {}    
        
        for value in cpu:   
            if "Completion Code:" in value:
                completionstate &= False
            elif "Processor0 Type" in value:
                cpursp["Processor-1"]["Processor Id"] = 0
                cpursp["Processor-1"]["Processor Type"] = value.split(":")[-1].strip() 
            elif "Processor0 Frequency" in value:
                cpursp["Processor-1"]["Processor Frequency"] = value.split(":")[-1].strip()
            elif "Processor0 State" in value:
                cpursp["Processor-1"]["ProcessorState"] = value.split(":")[-1].strip()
            elif "Processor1 Type" in value:
                cpursp["Processor-2"]["Processor Id"] = 1
                cpursp["Processor-2"]["Processor Type"] = value.split(":")[-1].strip() 
            elif "Processor1 Frequency" in value:
                cpursp["Processor-2"]["Processor Frequency"] = value.split(":")[-1].strip()
            elif "Processor1 State" in value:
                cpursp["Processor-2"]["ProcessorState"] = value.split(":")[-1].strip()        
        
    except Exception,e:
        cpursp[completion_code.cc_key] = completion_code.failure
        cpursp[completion_code.desc] = "Get CPU health, Exception: ", e
        return cpursp 
    
    if completionstate:
        cpursp[completion_code.cc_key] = completion_code.success
    else:
        cpursp[completion_code.cc_key] = completion_code.failure
    
    return cpursp

def get_sensor_info(temp, sensortype = ''):
    try:
        completionstate = True        
        temp_rsp = {}
        record_id = 1           
        for value in temp:   
            if "Completion Code:" in value:
                completionstate &= False
            
            # Skipping empty lists if any 
            if  len(value) == 0:
                break             
            
            val = value.split ("|")
            sensor = {}
            if sensortype == "fan":
                if "pwm" in val[0].lower().strip():
                    continue
                else:
                    sensor["Fan Name"] = val[0].strip ()
                    sensor["Fan Number"] = val[1].strip ()
                    sensor["Fan Status"] = val[2].strip ()
                    sensor["Fan MemberId"] = val[3].strip ()
                    sensor["Fan Reading"] = val[4].strip ()
            else:
                sensor["Sensor Description"] = val[0].strip ()
                sensor["Sensor Number"] = val[1].strip ()
                sensor["Sensor Status"] = val[2].strip ()
                sensor["Sensor Entity ID"] = val[3].strip ()
                sensor["Sensor Reading"] = val[4].strip ()
                
            
            temp_rsp[record_id] = sensor                   
                          
            record_id = record_id + 1
        
    except Exception,e:
        temp_rsp[completion_code.cc_key] = completion_code.failure
        temp_rsp[completion_code.desc] = "Get Sensor Information, Exception: ", e
        return temp_rsp 
    
    if completionstate:
        temp_rsp[completion_code.cc_key] = completion_code.success
    else:
        temp_rsp[completion_code.cc_key] = completion_code.failure
    
    return temp_rsp   

def show_memory_info(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        ipmi_cmd = 'ocsoem dimminfo'        
        cmdinterface = interface + ' ' + ipmi_cmd
    
        get_memory = parse_memory(cmdinterface ,"memory")  
            
        if get_memory is None or not get_memory: # Check empty or none
            return set_failure_dict("Empty memory info", completion_code.failure)                
        
        return get_memory  
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("get memory info Exception: ", e), completion_code.failure)
    
def show_pcie_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        ipmi_cmd = 'ocsoem getpcie'        
        cmdinterface = interface + ' ' + ipmi_cmd
         
        get_pcie = parse_pcie(cmdinterface ,"pcie")     
            
        if get_pcie is None or not get_pcie: # Check empty or none
            return set_failure_dict("Empty PCIe information", completion_code.failure)
            
        return get_pcie
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("get Pcie info Exception: ", e), completion_code.failure)
    
def show_cpu_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'ocsoem redfish cpu'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "cpu")          
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        cpursp = {}
        
        if(output['status_code'] == 0):
            cpu_data = output['stdout'].split('\n')
            
            cpursp = get_cpu_info(cpu_data)
        else:
            error_data = output['stderr'].split('\n')            
            cpursp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    cpursp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    cpursp[completion_code.ipmi_code] = data.split(":")[-1]  
    
        if cpursp is None or not cpursp: # Check empty or none
            return set_failure_dict("Empty cpu information", completion_code.failure)
            
        return cpursp
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("show cpu info Exception: ", e), completion_code.failure)

def show_temperature_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'sdr type temperature'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "Temperature")          
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        temprsp = {}
        
        if(output['status_code'] == 0):
            temp_data = output['stdout'].split('\n')            
            temprsp = get_sensor_info(temp_data)
        else:
            error_data = output['stderr'].split('\n')            
            temprsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    temprsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    temprsp[completion_code.ipmi_code] = data.split(":")[-1]  
    
        if temprsp is None or not temprsp: # Check empty or none
            return set_failure_dict("Empty temperature information", completion_code.failure)
            
        return temprsp
    
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("show temperature info Exception: ", e), completion_code.failure)

def show_fan_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'sdr type fan'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "Fan")          
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        fanrsp = {}
        
        if(output['status_code'] == 0):
            fan_data = output['stdout'].split('\n')            
            fanrsp = get_sensor_info(fan_data,'fan')            
        else:
            error_data = output['stderr'].split('\n')            
            fanrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    fanrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    fanrsp[completion_code.ipmi_code] = data.split(":")[-1]  
    
        if fanrsp is None or not fanrsp: # Check empty or none
            return set_failure_dict("Empty fan information", completion_code.failure)
            
        return fanrsp
    
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("show fan info Exception: ", e), completion_code.failure)

# This method is using to get the show manager inventory or sh system health -s (server info)
def show_server_health(serverid, inventory = False):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'ocsoem redfish server'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "server")        
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        serverrsp = {}
        
        if(output['status_code'] == 0) or output['stdout']:
            server_data = output['stdout'].split('\n')            
            serverrsp = parse_server_details(server_data, inventory)            
        else:
            error_data = output['stderr'].split('\n')            
            serverrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    serverrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    serverrsp[completion_code.ipmi_code] = data.split(":")[-1]  
    
        if serverrsp is None or not serverrsp: # Check empty or none
            return set_failure_dict("Empty server information", completion_code.failure)
            
        return serverrsp
    
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("show server info Exception: ", e), completion_code.failure)

def parse_server_details(server, inventory):
    try:
        completionstate = True        
        server_rsp = {}
                                     
        for value in server:   
            if "Completion Code" in value:
                completionstate &= False
            elif "Server communication type" in value:
                server_type = value.split(":")[-1].strip()
                if server_type == "IPMI":
                    server_rsp["Server Type"] = "C2010"
                elif server_type == "REST":
                    server_rsp["Server Type"] = "J2010"
                else:
                    server_rsp["Server Type"] = "Unknown"
                    completionstate &= False                    
            elif "Slot Id" in value:
                server_rsp["Server Slot ID"] = value.split(":")[-1].strip()
            elif "System Power State" in value:
                server_rsp["Server State"] = value.split(":")[-1].strip()
            elif inventory == True and "GUID" in value:
                guid = value.split(":")[-1].strip()
                if guid.lower().strip() == "failure":
                    completionstate &= False                    
                server_rsp["UUID"] = guid
            elif inventory == True and "MAC1" in value:
                mac1 = value.split(":")[-1].strip()
                if mac1.lower().strip() == "failure":
                    completionstate &= False
                server_rsp["MAC1"] = mac1
        
    except Exception,e:
        server_rsp[completion_code.cc_key] = completion_code.failure
        server_rsp[completion_code.desc] = "Get Server Information, Exception: ", e
        return server_rsp 
    
    if completionstate:
        server_rsp[completion_code.cc_key] = completion_code.success
    else:
        server_rsp[completion_code.cc_key] = completion_code.failure
    
    return server_rsp   
    
def show_sensor_health(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        ipmi_cmd = 'sdr elist'        
        cmdinterface = interface + ' ' + ipmi_cmd
        
        output = call_ipmi(cmdinterface, "sensor")          
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        sensorrsp = {}
        
        if(output['status_code'] == 0):
            sensor_data = output['stdout'].split('\n')            
            sensorrsp = get_sensor_info(sensor_data)
        else:
            error_data = output['stderr'].split('\n')            
            sensorrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    sensorrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    sensorrsp[completion_code.ipmi_code] = data.split(":")[-1]  
    
        if sensorrsp is None or not sensorrsp: # Check empty or none
            return set_failure_dict("Empty sensor information", completion_code.failure)
            
        return sensorrsp
    
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("show sensor info Exception: ", e), completion_code.failure)

def get_server_fru(serverid):
    
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        # IPMI  command to get FRU  details
        cmdinterface = interface + ' ' + "fru print" 
        
        fru_collection = parse_fru_data(cmdinterface, "fru")
        
        if fru_collection is None or not fru_collection: # Check empty or none
                return set_failure_dict("Empty Fru data", completion_code.failure)
                
    except Exception, e:
        return set_failure_dict(("Server fru Exception",e), completion_code.failure)
    
    return fru_collection
    
def get_server_nicinfo(serverid):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        nic_collection = {}
        
        for i in range(1,3):            
            ipmi_cmd = 'ocsoem nicinfo' + ' ' + str(i)  # IPMI  command to get server pcie details
            cmdinterface = interface + ' ' + ipmi_cmd      
            get_nic = parse_nic(cmdinterface , "nic", str(i))     
            
            if get_nic is None or not get_nic: # Check empty or none
                nic_collection[completion_code.cc_key] = completion_code.failure
            
            nic_collection.update({i: get_nic})
        
    except Exception, e:
        return set_failure_dict(("Server fru Exception",e), completion_code.failure)
    
    nic_collection[completion_code.cc_key] = completion_code.success
    return nic_collection
    
def parse_fru_data(interface,command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        fru_rsp = {}
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].split('\n') 
            fru_rsp = get_fru_info(sdata)            
        else:
            error_data = output['stderr'].split('\n')            
            fru_rsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    fru_rsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    fru_rsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
        
    except Exception, e:
        #log.exception("Exception error is: ",e)
        return set_failure_dict(("parse_fru() Exception ",e), completion_code.failure) 
    
    return fru_rsp

def get_fru_info(output):    
    try:
        completionstate = True
        fru_rsp = {}
                
        for value in output:
            if "Completion Code:" in value:
                completionstate &= False
            elif "Board Mfg Date" in value:
                date = value.split(":")
                date.pop(0)
                fru_rsp["Board Mfg Date"] = ":".join(date)
            elif "Board Mfg" in value:
                fru_rsp["Board Mfg"] = value.split(":")[-1].strip()
            elif "Board Product" in value:
                fru_rsp["Board Product"] = value.split(":")[-1].strip()
            elif "Board Serial" in value:
                fru_rsp["Board Serial Number"] = value.split(":")[-1].strip()
            elif "Board Part Number" in value:
                fru_rsp["Board Part Number"] = value.split(":")[-1].strip()
            elif "Product Asset Tag" in value:
                fru_rsp["AssetTag"] = value.split(":")[-1].strip()
            elif "Product Manufacturer" in value:
                fru_rsp["Manufacturer"] = value.split(":")[-1].strip()
            elif "Product Name" in value:
                fru_rsp["Model"] = value.split(":")[-1].strip()
            elif "Product Part Number" in value:
                fru_rsp["Product Part Number"] = value.split(":")[-1].strip()               
            elif "Product Version" in value:
                fru_rsp["Product Version"] = value.split(":")[-1].strip()
            elif "Product Serial" in value:            
                fru_rsp["Product Serial"] = value.split(":")[-1].strip()
        
        if completionstate:
            fru_rsp[completion_code.cc_key] = completion_code.success
        else:            
            fru_rsp[completion_code.cc_key] = completion_code.failure
            
        return fru_rsp
    except Exception,e:
        #log.exception("Exception error is: %s " %e)
        fru_rsp[completion_code.cc_key] = completion_code.failure
        fru_rsp[completion_code.desc] = "Get fru info, Exception: ", e
        return fru_rsp 
    
def parse_memory(interface ,command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return set_failure_dict("IPMI call error {0}".format(output), completion_code.failure)
        
        memoryrsp = {}
        
        if(output['status_code'] == 0):
            memory_data = output['stdout'].split('*')                
            memory_value= filter(None, memory_data)  
            memoryrsp = get_memory_health(memory_value)  
            return memoryrsp
        else:
            error_data = output['stderr'].split('\n')            
            memoryrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    memoryrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    memoryrsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
        
    except Exception, e:
        #log.exception("Exception error is: ",e)
        return set_failure_dict(("parse_memopry() Exception ",e), completion_code.failure) 
    
def parse_pcie(interface ,command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        pciersp = {}
                
        if(output['status_code'] == 0):
            pcie_data = output['stdout'].split('*')                
            pcie_value= filter(None, pcie_data)  
            pciersp = get_pcie_info(pcie_value)  
            return pciersp
        else:
            error_data = output['stderr'].split('\n')            
            pciersp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    pciersp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    pciersp[completion_code.ipmi_code] = data.split(":")[-1]                                        
        
    except Exception, e:
        #log.exception("Exception error is: ",e)
        return set_failure_dict(("parse_pcie Exception ",e), completion_code.failure) 

def parse_nic(interface, command, nicid):
    try:        
        output = call_ipmi(interface, command+nicid)          
        
        if "ErrorCode" in output:
            return output
        
        nicrsp = {}
        
        if(output['status_code'] == 0):
            sdata = output['stdout'].strip()          
            nicrsp["Device Id"] =  nicid
            nicrsp["Mac Address"] =  sdata[:-1]
        else:
            error_data = output['stderr'].split('\n')      
            nicrsp["Device Id"] =  nicid      
            nicrsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "Error" in data:
                    nicrsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    nicrsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
        
    except Exception, e:
        #log.exception("Exception error is: ",e)
        return set_failure_dict(("parse_pcie Exception ",e), completion_code.failure) 
    
    return nicrsp
