# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from time import strptime
from ipmicmd_library import * 

sdr_cachefile_path = "/tmp/sdrcache/"

#Check if sdcache directory exists if not create 
if not os.path.exists(sdr_cachefile_path):
    os.makedirs("/tmp/sdrcache")

def read_server_log_entry(serverid, entryid):
    try:
        log = read_server_log(serverid, False)
               
        if "members" in log:            
            if str(entryid) in log["members"]:
                entry = log["members"][str(entryid)]
                log["members"].clear()            
                log["members"] = entry
            else:
                print "there"
                log["members"].clear()
                    
    except Exception, e:
        return set_failure_dict(("read_server_log_entry Exception: {0}".format(e)), completion_code.failure)
        
    return log
            

def read_server_log(serverid, raw_output=True):
    try:        
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48",completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
          
        if "Failed:" in interface:
            return set_failure_dict(interface,completion_code.failure)
        
        #Verify sdr cache file exists
        filename = 'server' + str(serverid) + ".sdr"
        filepath = sdr_cachefile_path + filename
        iscache = verify_cachefile_exists(filepath, filename, interface)
    
        if iscache == True:
            #log.info("serverLog: %s cache file exists.Running commands through cache file" %fileName)
            readcmd = '-S' + ' ' + filepath + ' ' + 'sel elist'
            cmdinterface = interface + ' ' + readcmd
        else:
            #log.info("serverLog: %s cache file is not exists.Running direct commands" %fileName)
            cmdinterface = interface + ' ' + 'sel elist'
                    
        read_log = parse_server_log(cmdinterface, "readserverlog",raw_output)
        
        if read_log is None or not read_log: # Check empty or none
            return set_failure_dict("Empty data for readserverlog", completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("readserverlog Exception: ", e),completion_code.failure)

    return read_log     

def read_server_log_with_timestamp(serverid, starttime, endtime,raw_output=True):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48", completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface, completion_code.failure)
        
        #Verify sdr cache file exists
        filename = 'server' + str(serverid) + ".sdr"
        filepath = sdr_cachefile_path + filename
        iscache = verify_cachefile_exists(filepath, filename, interface)
    
        if iscache == True:
            #log.info("serverLog: %s cache file exists.Running commands through cache file" %fileName)
            readcmd = '-S' + ' '+ filepath + ' ' + 'sel elist'
            cmdinterface = interface + ' ' + readcmd
        else:
            #log.info("serverLog: %s cache file is not exists.Running direct commands" %fileName)
            cmdinterface = interface + ' ' + 'sel elist'
         
        start_time = strptime(starttime, '%m/%d/%Y-%H:%M:%S')
        end_time = strptime(endtime, '%m/%d/%Y-%H:%M:%S')
        if(end_time <= start_time):
            return set_failure_dict("Parameter out of range",completion_code.failure)
        else:
            server_log = parse_read_serverlog_with_timestamp(cmdinterface, "readserverlogwithtimestamp",start_time , end_time,raw_output)   
               
        if server_log is None or not server_log: # Check empty or none
            return set_failure_dict("Empty data for readserverlogwithtimestamp",completion_code.failure)
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

    return server_log 

def clear_server_log(serverid, raw_output = True):
    try:
        if serverid < 1 or serverid > 48:
            return set_failure_dict("Expected server-id between 1 to 48",completion_code.failure)  
        else:            
            interface = get_ipmi_interface(serverid)
        
        if "Failed:" in interface:
            return set_failure_dict(interface,completion_code.failure)
        
        #Verify sdr cache file exists
        filename = 'server' + str(serverid) + ".sdr"
        filepath = sdr_cachefile_path + filename
        iscache = verify_cachefile_exists(filepath, filename, interface)
    
        if iscache == True:
            #log.info("serverLog: %s cache file exists.Running commands through cache file" %fileName)
            clearcmd = '-S' + ' '+ filepath + ' ' + 'sel clear'
            cmdinterface = interface + ' ' + clearcmd
        else:
            #log.info("serverLog: %s cache file is not exists.Running direct commands" %fileName)
            cmdinterface = interface + ' ' + 'sel clear'
            
        read_log = parse_server_log(cmdinterface, "clearserverlog")
        
        if read_log is None or not read_log: # Check empty or none
            return set_failure_dict("Empty data for clearserverlog", completion_code.failure)
        
        if (raw_output):
            return read_log
        else:
            return set_success_dict ()
        
    except Exception, e:
        #Log_Error("Failed Exception:",e)
        return set_failure_dict(("Exception: ", e), completion_code.failure)

def parse_server_log(interface , command,raw_output=True):
    try:     
        output = call_ipmi(interface, command)
        
        if "ErrorCode" in output:
            return output
        
        read_serverlog = {}
        if(output['status_code'] == 0 ):
            if raw_output:
                return output['stdout']
            else:
                return generate_collection(output)
        else:
            error_data = output['stderr']            
            read_serverlog[completion_code.cc_key] = completion_code.failure            
            read_serverlog[completion_code.desc] = error_data.split(":")[-1]                                                  
            return read_serverlog  
             
    except Exception, e:
        #log.exception("serverLog Command: %s Exception error is: %s ", command, e)
        #print "Failed to parse serverlog results. Exception: " ,e      
        return set_failure_dict(("serverLog: Exception: ",e) , completion_code.failure)

def parse_read_serverlog_with_timestamp(interface , command, starttime, endtime,raw_output=True):
    try:     
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        read_serverlog = {}
        
        filtered_serverlog = []
        
        if(output['status_code'] == 0 ):
            read_logdata = output['stdout'].split('\n')
            read_loglist = filter(None, read_logdata) # Removes empty strings 
            
            if(len(read_loglist) > 0):
                for log in read_loglist:
                    # getting each log time and date stamp
                    datetime_part = log.split('|', 3) # Gets first 3 strings
                    logtime = datetime_part[1].strip() + datetime_part[2].strip() # combining date and time
                    
                    logtime_obj = strptime(logtime, '%m/%d/%Y%H:%M:%S')  
                    if (logtime_obj >= starttime) and (logtime_obj <= endtime):
                        filtered_serverlog.append(log) 
            else:
                if raw_output:
                    return read_logdata
                else:
                    return generate_collection(output)
            
            if(len(filtered_serverlog) > 0):
                
                if raw_output:
                    return "\n".join(filtered_serverlog)
                else:
                    return generate_collection("\n".join(filtered_serverlog))
            
            else:
                print "No logs found returning all the logs"
                return "\n".join(read_loglist)              
        else:
            error_data = output['stderr']            
            read_serverlog[completion_code.cc_key] = completion_code.failure         
            read_serverlog[completion_code.desc] = error_data.split(":")[-1]                                                  
            
            return read_serverlog  
             
    except Exception, e:
        #log.exception("serverLog Command: %s Exception error is: %s " ,command ,e)
        #print "Failed to parse serverlog results. Exception: " , e      
        return set_failure_dict(("serverLog: Exception: ",e) , completion_code.failure)

def generate_collection(output):    
    try:
        logRsp = {}
        if(output['status_code'] == 0):
                                
            sdata = output['stdout'].split('\n')
                
            logRsp["members"]={}                
            for value in sdata:
                
                if value:
                    d=''
                    t=''
                    tmp={}
                    for idx, val in enumerate(value.split("|")):
                        if idx ==0:
                            tmp["Id"] =  str(int(val.strip(), 16))
                            tmp["RecordId"] =  str(int(val.strip(), 16))
                        if idx == 1: 
                            d = val.strip()
                        if idx == 2:    
                            t= val.strip()
                        if idx == 3:
                            tmp["MessageId"] =  val.strip()
                        if idx == 4:                    
                            tmp["Message"] =  val.strip()
                        if idx == 5:
                            tmp["EntryCode"] =  val.strip()
                        if idx == 6:
                            tmp["MessageArgs"] =  val.strip()
                
                    tmp["Name"] =  "Blade SEL log entry"
                    tmp["EntryType"] =  "SEL"               
                    tmp["Created"] =  d+'T'+t
                                    
                    logRsp["members"].update({tmp["Id"]: tmp })
            
            logRsp[completion_code.cc_key] = completion_code.success
            return logRsp
        else:   
            logFailedRsp = {}
            errorData = output['stderr'].split('\n')            
            logFailedRsp[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    logFailedRsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    logFailedRsp[completion_code.ipmi_code] = data.split(":")[-1]                                        
            return logFailedRsp
          
    except Exception, e:
        return set_failure_dict(("ServerLog: Exception: ",e) , completion_code.failure) 
