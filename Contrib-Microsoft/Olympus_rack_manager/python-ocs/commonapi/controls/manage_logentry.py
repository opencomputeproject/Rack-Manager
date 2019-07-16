# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils import *
from ocspaths import *
from controls.bladelog_lib import read_server_log
from controls.manage_rack_manager import get_rack_manager_log

def get_logentry(entry_id, log_id, type, device_id):
    ret = {}
    ret["members"] = {}
        
    log_id = int(log_id)

    if type == 'system' and log_id == 1:
        output = read_server_log(int(device_id), False)
        
    elif type == 'chassis' and log_id == 1:
        if device_id == "rackmanager":
        output = get_rack_manager_log(telemetry_log_path, False)
                        
        elif branch_id == "rowmanager":
            return set_failure_dict("Rowmanager log is not available", completion_code.failure)
        
        else:
            return set_failure_dict("Requested log is not available", completion_code.failure)
    else:
        return set_failure_dict("Requested log is not available", completion_code.failure)
                                            
    if entry_id == 0:
        ret["members"] = output["members"]
    elif entry_id in output["members"]:       
        ret["members"] = output["members"][entry_id]

    ret["entry_type"] = "SEL"
    ret["log_count"] = len(ret["members"])
    ret["id"] = device_id
    ret["type"] = type
    
    return ret

    
    