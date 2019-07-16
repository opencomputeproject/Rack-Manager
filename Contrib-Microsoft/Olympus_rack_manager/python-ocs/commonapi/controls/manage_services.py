# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import subprocess
import glob

from utils import *
from subprocess import CalledProcessError


def service_enable(service, runlevels = ["defaults"]):
    """
    Enable a service to be run automatically on boot.  This does not mean the service will be
    running.
    
    Parameters:
        service -- The name of the service service script to enable.
        runlevels -- The runlevel arguments that indicate when the service should be started.
        
    Return:
        Completion information.
    """
    
    try:
        cmd = ["/usr/sbin/update-rc.d", service]
        cmd.extend(runlevels)
        
        subprocess.check_output(cmd, stderr = subprocess.STDOUT)
        return set_success_dict()
    
    except CalledProcessError as error:
        result = {}
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.err_code] = error.returncode
        result[completion_code.desc] = error.output.strip()
        return result
                
    except Exception, e:
        return set_failure_dict("service_enable - Exception: {0}".format(e), completion_code.failure)

def service_disable(service):
    """
    Disable a service from running automatically on boot.  This does not mean the service will be
    stopped.
    
    Parameters:
        service -- The name of the service script to disable.
        
    Return:
        Completion information.
    """
        
    try:
        cmd = ["/usr/sbin/update-rc.d", "-f", service, "remove"]
        subprocess.check_output (cmd, stderr = subprocess.STDOUT)
        return set_success_dict()
    
    except CalledProcessError as error:
        result = {}
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.err_code] = error.returncode
        result[completion_code.desc] = error.output.strip()
        return result
                
    except Exception, e:
        return set_failure_dict("service_disable - Exception: {0}".format(e), completion_code.failure)
        
def check_service_enabled(service):
    """
    Determine if a service is enabled to run at boot.
    
    Parameters:
        service -- The name of the service script to query.
        
    Return:
        String indicating if the service is enabled.
    """
    
    try:
        links = glob.glob("/etc/rc*.d/S*" + service)
        if (links):
            return "Enabled"
        else:
            return "Disabled"
        
    except Exception:
        return "Check failed"
 
def service_start(service, restart = False):
    """
    Start a system service.
    
    Parameters:
        service -- The name of the service script to start.
        restart -- Indicate if the service should be restarted.
        
    Return:
        Completion information.
    """
        
    try:
        cmd = ["/etc/init.d/" + service]
        
        if (restart):
            cmd.append("restart")
        else:
            cmd.append("start")
            
        subprocess.check_output (cmd, stderr = subprocess.STDOUT)
        
        return set_success_dict()
    
    except CalledProcessError as error:
        result = {}
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.err_code] = error.returncode
        result[completion_code.desc] = error.output.strip()
        return result
                
    except Exception, e:
        return set_failure_dict("service_start - Exception: {0}".format(e), completion_code.failure)
        
def service_stop(service):
    """
    Stop a system service.
    
    Parameters:
        service -- The name of the service script to stop.
        
    Return:
        Completion information.
    """
    
    try:       
        subprocess.check_output(["/etc/init.d/" + service, "stop"], stderr = subprocess.STDOUT)
        return set_success_dict()
    
    except CalledProcessError as error:
        result = {}
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.err_code] = error.returncode
        result[completion_code.desc] = error.output.strip()
        return result
                
    except Exception, e:
        return set_failure_dict("service_stop - Exception: {0}".format(e), completion_code.failure)
