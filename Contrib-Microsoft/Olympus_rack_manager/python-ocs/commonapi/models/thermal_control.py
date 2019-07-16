# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.sys_works import *

class thermal_control(sys_base):
    def __init__(self, id = None):
        self.id = id
            
    def getThermalInfo(self):               
        cmd = "ManageThermal.py -b {0}".format(self.id)
        
        return system_executeCommand(cmd)    
        
def get_thermal(id):
    return thermal_control(id = id)