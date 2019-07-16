# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.sys_works import *

class powerport(sys_base): 
    def __init__(self, id):
        self.id = int(id)         
                      
    def doWorks(self, port_type, parameters):        
        return powerport_works(self.id, port_type, parameters)
 
def get_powerport(id):
    return powerport(id)    

def get_powerports():
    return powerport(0)        
