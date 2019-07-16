# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import ctypes
import subprocess

from ctypes import *
from utils import *
from lib_utils import get_blade_map_library

ipmi_exe_path = "/usr/bin/ipmitool -I lan -H"

def get_ipmi_interface(serverid, args = []):
    hostname = get_hostname_by_serverid(serverid)
    
    if(hostname == -1):
        raise RuntimeError ("Failed to get hostname for serverId {0}".format(serverid))
        
    interface = get_interface(hostname.strip())
        
    # Check if interface is empty
    if not interface:
        raise RuntimeError ("Empty IPMI command interface: {0}".format(interface))
    
    interface_params = []
    interface_params.append (interface)
    interface_params.extend (args)
        
    cmdinterface = ' '.join(interface_params)
        
    return cmdinterface 
    
# Get the HostIP by serverId 
def get_hostname_by_serverid(serverid):
    try:
        if (int(serverid) < 0) or (int(serverid) > 48):
            return -1

        blademap_binary = get_blade_map_library ()   
            
        hostname = create_string_buffer(48)  
        
        ret = blademap_binary.get_server_address(int(serverid), hostname) 
        
        if ret != 0: 
            return -1
        else:
            return hostname.value
        
    except Exception, e:  
        print("get_hostname_by_serverid() Exception ", e)
        
        return -1

# Gets IPMI command user access     
def get_server_access(isconsole):
    try:
        blademap_binary = get_blade_map_library ()    
        
        username = create_string_buffer(48)  
        password = create_string_buffer(48)

        if (isconsole != 1):
            ret = blademap_binary.get_server_command_access(username, password)
        else:
            ret = blademap_binary.get_server_console_access(username, password) 
        
        if ret != 0: 
            return None
        else:
            return username.value, password.value
        
    except Exception, e:  
        print("get_server_access() Exception ", e)    
        return None
            
# Constructs the common interface 
def get_interface(hostname):
    singl_args = []
    username, password = get_server_access(0)
    if username is None:
        raise RuntimeError ("Failed to get username for server")

    singl_args.append(ipmi_exe_path)
    singl_args.append(hostname)
    singl_args.append("-U")
    singl_args.append(username)
    singl_args.append("-P")
    singl_args.append(password)
    
    cmdinterface = ' '.join(singl_args) 
    
    return cmdinterface 

def call_ipmi(interface, command):
    try:    
        popencmd = subprocess.Popen(interface, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True);

        output, error = popencmd.communicate()
        
        p_status = popencmd.wait();
        
        return  {'status_code':p_status, 'stdout':output, 'stderr': error}
    except Exception:
        #log.exception("Subprocess IPMI Call error: %s Command: %s", e ,command) 
        #print "Failed: IPMI call exception, command :" + command     
        return set_failure_dict(("Subprocess IPMI call exception, Command: {0}".format(command)),completion_code.failure)

#Creates cache file if not exists
def verify_cachefile_exists(filepath, filename, cmdinterface):
    if not os.path.isfile(filepath) and not os.access(filepath, os.R_OK):
        #log.info("SdrCacheFile: %s cache file not exists.Running sdr dump to generate cache file" %fileName)
        command = 'sdr dump' + ' '+ filepath
        ipmi_interface = cmdinterface + ' ' + command 
        dump_output = call_ipmi(ipmi_interface, command) 
        if(dump_output['status_code'] == 0):
            #log.info("Successfully created sdr cache file")
            return True               
        else:
            #log.info("Failed to run sdr dump command %s:" %dumpOutput['stderr'])
            #print dumpOutput['stderr']
            return False       
    else:
        #log.info("SdrCacheFile: %s cache file exists." %fileName)
        return True