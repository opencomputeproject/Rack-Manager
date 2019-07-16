# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *

from controls.bladeinfo_lib import *
from controls.sys_works import *
from controls.bladetpmphypresence_lib import *
from controls.bladenextboot_lib import *
from controls.bladepowerstate_lib import *
from controls.bladelog_lib import *
from controls.bladebios_lib import *
from controls.server_health import *
from controls.manage_nvme import *

class blade_system(sys_base): 
        
    def __init__(self, id = None):
                
        if id == None:
            self.id = 0
        else:
            self.id = int(id)
    
    def getSystem(self):
        result = system_info_call(self.id)        
        return result 
     
    def get_server_data(self):      
        return get_server_health(self.id)   
         
    def get_memory_deatils(self):      
        return show_memory_info(self.id)        
    
    def get_pcie_details(self):      
        return show_pcie_health(self.id)
    
    def get_cpu_details(self):      
        return show_cpu_health(self.id)
   
    def get_fru_details(self):      
        return get_server_fru(self.id)    
    
    def get_temperature_details(self):      
        return show_temperature_health(self.id)  
    
    def get_fan_details(self):      
        return show_fan_health(self.id)   
    
    def get_sensor_details(self): 
        return show_sensor_health(self.id)
    
    def get_server_details(self): 
        return show_server_health(self.id)
     
    def get_tpm_presence(self):
        return get_tpm_physical_presence(self.id) 
    
    def get_next_boot(self):        
        return get_nextboot(self.id)
    
    def get_nvme(self):
        return get_nvme_status(self.id)
    
    def get_default_power_state(self):        
        return get_server_default_powerstate(self.id) 
    
    def get_system_state(self):        
        return get_server_state(self.id)
    
    def get_system_power_state(self):        
        return powerport_get_port_status(self.id, 'pdu')        
    
    def get_system_port_presence(self):        
        return powerport_get_port_presence(self.id , 'pdu')        
    
    def get_system_biosconfig(self):        
        return get_server_bios_config(self.id) 
     
    def get_system_bioscode(self,version):        
        return get_bios_code(self.id, version) 
    
    def read_system_log(self):        
        return read_server_log(self.id)
    
    def read_system_log_timestamp(self, starttime, endtime):        
        return read_server_log_with_timestamp(self.id, starttime, endtime)
    
    def get_system_led_status(self):
        return get_server_attention_led_status(self.id)
    
    def doWorks(self,parameters):        
        return system_doActions(self.id,parameters)
        
    def get_datasafe_policy(self):
	    return get_nvdimm_policy(self.id)
       
def getsystem(id):
    return blade_system(id)
