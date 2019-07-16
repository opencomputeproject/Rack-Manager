# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.utils import *
from controls.sys_works import *

class fpga_unit(sys_base):
    
    def __init__(self, device_id):
        self.device_id = device_id
                      
    def doWorks(self, parameters):    
        try:           
            if parameters["mode"] == "action":
                return system_fpga_action(self.device_id, parameters) 
            elif parameters["mode"] == "display":
                return system_fpga_display(self.device_id, parameters)
            else:
                return set_failure_dict("Unknown mode", completion_code.failure)

        except Exception, e:
            return set_failure_dict("fpga_unit.doWorks() Exception {0}".format(e), completion_code.failure)    
       
def get_fpga(device_id):
    device_id = int(device_id)
                    
    return fpga_unit(device_id = device_id)        
