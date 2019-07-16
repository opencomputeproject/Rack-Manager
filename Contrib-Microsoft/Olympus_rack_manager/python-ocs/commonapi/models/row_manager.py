# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.sys_works import *

class row_manager(sys_base):
    def getRowManager(self):
        #this should be same for now        
        return get_rack_manager_info()
    
    def doWorks(self, parameters):
        return system_rowmanager_action(parameters)     
       
def getrowmanager():    
    # Define device as a row manager, manages collection of rack managers
    return row_manager()