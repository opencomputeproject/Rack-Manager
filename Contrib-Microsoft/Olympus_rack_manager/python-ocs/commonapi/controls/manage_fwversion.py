# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from utils import * 

def get_ocsfwversion(raw = False):
    try:
        vers = get_versions_file()
        
        if raw:
            if (vers['status_code'] == 0):
                return vers
            else:
                return set_failure_dict(vers['stderr'], completion_code.failure)
            
        return parse_versions_file(vers)
    except Exception, e:
        return set_failure_dict("get_ocsfwversion - Exception: {0}".format(e), completion_code.failure)

def get_versions_file():
    """ Read and parse rmversions.sh output 
    """
            
    command = "/etc/rmversions.sh"        

    try:
        process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        output, errorMsg = process.communicate() 
        completion_status = process.wait()   
                    
        if errorMsg:
            return {'status_code': -1, "stdout": output, "stderr": errorMsg}
        else:
            return {"status_code": completion_status, "stdout": output, "stderr": errorMsg}

    except Exception, e:              
        return {"get_versions_file - Exception: {0}".format(e), completion_code.failure}     
    
def parse_versions_file(output):    
    try:
        fwRsp = {}
                
        if output['status_code'] == 0:
            sdata = output['stdout'].split('\n')
                            
            for value in sdata:
                if "Package version" in value:
                    fwRsp["Package"] = value.split(":")[-1].strip()
                
                if "Rootfs version" in value:
                    fwRsp["Rootfs"] = value.split(":")[-1].strip()
                
                if "U-Boot version" in value:
                    fwRsp["uboot"] = value.split(":")[-1].strip()
                
                if "Kernel version" in value:
                    fwRsp["Kernel"] = value.split(":")[-1].strip()
                
                if "Devicetree version" in value:
                    fwRsp["DeviceTree"] = value.split(":")[-1].strip()
                
                if "PRU FW version" in value:
                    fwRsp["PRUFW"] = value.split(":")[-1].strip()
                       
            return set_success_dict(fwRsp)
        else:   
            fwFailedRsp = {}
            errorData = output['stderr'].split('\n')  
            errorData = filter(None, errorData)[-1]  
            
            return set_failure_dict(errorData.split(":")[-1], completion_code.failure)
          
    except Exception, e:
        return set_failure_dict("parse_versions_file - Exception: {0}".format(e), completion_code.failure) 
