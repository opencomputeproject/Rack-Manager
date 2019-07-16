# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess 
import ocslog

from subprocess import *
from controls.utils import *
from ipmicmd_library import * 

def server_start_serial_session(system_id, force = False):
    try:
        if(force == True):
            server_stop_serial_session(system_id)
              
        serverhost = get_hostname_by_serverid(system_id)
                
        if(serverhost == -1):
            return set_failure_dict("Failed to get hostname for server: {0}".format(system_id))
        
        username, password = get_server_access(1)
        
        if username is None:
            return set_failure_dict("Failed to get username for server: {0}".format(system_id))                   
                                    
        sshserverParams = '%s@%s' % (username, serverhost)
        sshpassParams = '-p%s' % (password)
        
        subprocess.check_call(["sshpass", sshpassParams, "ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", 
                               "StrictHostKeyChecking=no", "-o", "LogLevel=ERROR", sshserverParams], stderr = subprocess.STDOUT)
                        
    except Exception, e: 
        ocslog.log_exception ()
        return (set_failure_dict("start_serial_session failed to connect.", completion_code.failure))
        
    return set_success_dict({"Result" : "Serial session started successfully"})  

def server_stop_serial_session(system_id):
    try:  
        serverhost = get_hostname_by_serverid(system_id)

        if(serverhost == -1):
            return set_failure_dict("Failed to get hostname for server: {0}".format(system_id))
                                    
        psstring = "ps | grep sshpass | grep %s" % serverhost
        psoutput = subprocess.check_output(psstring, shell=True)
        
        for line in psoutput.splitlines(True):
            if "grep ssh" not in line:
                strList = line.split()
                killString = "kill -9 %s" % strList[0]
                subprocess.check_call(killString, shell=True)
     
        close_active_session(system_id)
    
    except subprocess.CalledProcessError as e:
        return set_failure_dict(e.output.strip(), completion_code.failure)
    
    except Exception, e: 
        return (set_failure_dict("server_stop_serial_session - Exception: {0}".format(e), completion_code.failure))
        
    return set_success_dict({"Result" : "Serial session terminated successfully"})        
    
def get_active_session_id(serverid, interface):
    try:
        # IPMI command to get active SSH session id
        ipmi_cmd = 'ocsoem getsessions 5'  
                        
        cmdinterface = interface + ' ' + ipmi_cmd
            
        get_active_sessions = parse_get_active_sessions(cmdinterface, "getactivesessions")
        
        # Check empty or none
        if get_active_sessions is None or not get_active_sessions: 
            return set_failure_dict("Empty data for getactivesessions", completion_code.failure)
        
    except Exception, e:
        return set_failure_dict("get_active_session_id - Exception: {0}".format(e), completion_code.failure)

    return get_active_sessions 

def close_active_session(serverid):
    try:
        interface = get_ipmi_interface(serverid)
        
        get_sessionid = get_active_session_id(serverid, interface)
        sessionid = ''

        if completion_code.cc_key in get_sessionid.keys():
            if get_sessionid[completion_code.cc_key] == completion_code.failure:
                return set_failure_dict("Failed to get sessionid", completion_code.failure)
            elif get_sessionid[completion_code.cc_key] == completion_code.success and "Session Id" in get_sessionid.keys():
                sessionid = get_sessionid["Session Id"] 
            else:
                return set_failure_dict("No active sessions to stop", completion_code.success)       
        
        # getting 4 bytes of data
        first, second, third, fourth = sessionid.split('-')

        # IPMI command to close SSH session               
        ipmi_cmd = 'ocsoem closesession' + ' ' + first + ' ' + second + ' ' + third + ' ' + fourth 
            
        cmdinterface = interface + ' ' + ipmi_cmd
        
        close_active_session = parse_close_active_session(cmdinterface, "closeactivesession")
        
        # Check empty or none
        if close_active_session is None or not close_active_session:
            return set_failure_dict("Empty data for getactivesessions", completion_code.failure)
        
    except Exception, e:
        return set_failure_dict("close_active_session - Exception: {0}".format(e), completion_code.failure)

    return close_active_session 

def parse_get_active_sessions(interface, command):
    try:        
        output = call_ipmi(interface, command)          
        
        if "ErrorCode" in output:
            return output
        
        getsessions = {}
        
        if(output['status_code'] == 0):
            sessionsdata = output['stdout'].split('\n') 
            sessionsdata = filter(None, sessionsdata)
            
            for value in sessionsdata:
                if "Number of active sessions present:" in value:
                    getsessions["Sessions Count"] = value.split(":")[-1].strip() 
                elif "First record session ID:" in value:
                    session_id = value.split(":")[-1].strip() 
                    getsessions["Session Id"] = session_id[:-1]    
                elif "No active sessions present" in value:
                    getsessions["Sessions Count"] = 0   
                               
            getsessions[completion_code.cc_key] = completion_code.success
            return getsessions
        
        else:
            errorData = output['stderr'].split('\n')            
            getsessions[completion_code.cc_key] = completion_code.failure

            for data in errorData:
                if "Error" in data:
                    getsessions[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    getsessions[completion_code.ipmi_code] = data.split(":")[-1]   
                                                         
            return getsessions
        
    except Exception, e:
        return set_failure_dict("parse_get_active_sessions() - Exception: {0}".format(e), completion_code.failure)
    
def parse_close_active_session(interface, command):    
    try:        
        output = call_ipmi(interface, command)
        
        if "ErrorCode" in output:
            return output
        
        closesession = {}
        
        if(output['status_code'] == 0):
            closesession[completion_code.cc_key] = completion_code.success  
            
            return closesession
        
        else:
            errorData = output['stderr'].split('\n')            
            closesession[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    closesession[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    closesession[completion_code.ipmi_code] = data.split(":")[-1]   
                                                         
            return closesession       
        
    except Exception, e:
        return set_failure_dict("parse_close_active_session() - Exception: {0}".format(e), completion_code.failure)   
    
if __name__ == "__main__":
    print(close_active_session(1))
