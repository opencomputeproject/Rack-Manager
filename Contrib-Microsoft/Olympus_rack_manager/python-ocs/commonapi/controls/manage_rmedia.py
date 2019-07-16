# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import fcntl
import socket
import struct

from ocspaths import *
from manage_network import *
from ipmicmd_library import *

def mount_rmedia(serverid, imagename):
    try:
        # Rmedia server IP is the management NIC (eth1) in the RM
        imageserverip = get_ip_address('eth1')
                        
        if imageserverip is None:
            return set_failure_dict("Rmedia Image server IP address not provided", completion_code.failure)
                    
        if imagename is None:
            return set_failure_dict("Rmedia Image name not provided", completion_code.failure)
            
        # IPMI command interface
        cmd_interface = get_ipmi_interface(serverid, ["ocsoem", "mount", str(imageserverip), str(imagename), nfs_path])             
        output = call_ipmi(cmd_interface, "mount")   
         
        if(output['status_code'] == 0):
            return {completion_code.cc_key : completion_code.success}
        else:
            return set_failure_dict (output["stderr"].strip(), completion_code.failure)
        
    except Exception, e:  
        return set_failure_dict("mount_rmedia - Exception: {0}".format(e), completion_code.failure) 

def umount_rmedia(serverid):
    try:
        # IPMI command interface
        cmd_interface = get_ipmi_interface(serverid, ["ocsoem", "unmount"]) 
        output = call_ipmi(cmd_interface, "unmount") 
        
        if(output['status_code'] == 0):
            return {completion_code.cc_key : completion_code.success}
        else:
            return set_failure_dict (output["stderr"].strip(), completion_code.failure)
                
    except Exception, e:  
        return set_failure_dict("umount_rmedia - Exception: {0}".format(e), completion_code.failure)
