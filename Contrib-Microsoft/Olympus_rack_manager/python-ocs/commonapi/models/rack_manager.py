# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *
from controls.manage_rack_manager import *
from controls.sys_works import *

class rack_manager(sys_base):
    def getRackManager(self):
        return get_rack_manager_info()
    
    def getChassisLog(self):        
        return read_server_log(self.id)
       
    def doWorks(self, parameters):
        try:            
            op_mode = ""
                 
            if "mode" in parameters.keys():
                op_mode = parameters["mode"]
            
            if op_mode == "display":
                return system_rackmanager_display(parameters)
            elif op_mode == "action":
                return system_rackmanager_action(parameters)
            
        except Exception,e:
            return {'Completion Code':'Failure' , 'Exception': e}
    
def getrackmanager():
    return rack_manager()
     
