# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.manage_network import *
from controls.sys_works import *

class ethernet_interface(sys_base): 
        
    def __init__(self, parent_id,parent_name, id= None, info = None, works = None):
                
        self.parent_id = parent_id
        
        self.parent_name = parent_name
        
        if id == None:
            self.id=""
        else:
            self.id = id                      
        
        if info == None:
            self.info = {}
        else:
            self.info = info
            
        if works == None:
            self.works = []
        else:
            self.works = works
            
    def getserviceversion(self):
        if self.parent_name == "chassis":
            return get_service_version()
        else:
            return set_failure_dict('Unable to get service version', completion_code.failure)
        
    def get_ethernet_interfaces_list(self):                
        if self.parent_name=="chassis":
            return display_cli_interfaces()
        else:
            return set_failure_dict("Unable to retrieve network information", completion_code.failure)
    
    def get_cli_ethernet_info(self):
        if self.parent_name=="chassis":
            return display_interface_by_name(self.id)
        else:
            return set_failure_dict("Unable to retrieve network information", completion_code.failure)

    def doWorks(self, parameters):        
        return ethernetinterface_actions(self.id, parameters)  
        
def get_ethernetinterfaceById(parent_id,parent_name, id):        
    return ethernet_interface( parent_id=parent_id,parent_name=parent_name, id=id)
       
def get_ethernetinterfaces(parent_id, parent_name):            
    return ethernet_interface(parent_id=parent_id,parent_name=parent_name)