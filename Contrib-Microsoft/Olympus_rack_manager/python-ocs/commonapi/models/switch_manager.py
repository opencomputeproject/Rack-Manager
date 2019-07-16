# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *

from controls.mgmt_switch import mgmt_switch, mgmt_switch_console
from controls.sys_works import switch_doActions
from controls.manage_network import get_ip_address


class switch_manager(sys_base): 
        
    def __init__(self, ip, uart, info = None, works = None, verbose = False):

        self.rest = mgmt_switch (ip)
        self.console = mgmt_switch_console (uart)
        self.verbose = verbose
        
        if info == None:
            self.info = {}
        else:
            self.info = info
            
        if works == None:
            self.works = []
        else:
            self.works = works
  
    def getswitch_info(self):
        
        result={}
                
        try:     
            result = self.rest.get_switch_information ()
            result.update (self.rest.get_switch_status ())
            self.rest.logout ()
            
        except Exception,ex:
            #Log 
            pass
    
        return result
    
    def getswitchport_info(self,port_id):
        
        result={}
        
        try:
            result = self.rest.get_port_status(port_id)
            self.rest.logout ()
        except Exception,ex:
            #Log 
            pass        
            
        return result
    
    def do_reset (self):
        return self.console.reboot (verbose = self.verbose)
    
    def do_configure (self, config_file):
        return self.console.configure (config_file, verbose = self.verbose)
    
    def do_upgrade (self, fw_file):
        server = get_ip_address ("eth1")
        return self.console.upgrade_fw (server, fw_file, verbose = self.verbose)
    
    def do_console (self, baud = None, pass_sigint = False):
        return self.console.shell (baud, pass_sigint)
    
    def doWorks(self,parameters):        
        return switch_doActions(self, parameters)
    
    def getWorks(self):        
        return self.works
       
def getswitch(ip, uart, verbose = False):
    
    works =  [ "switch.reset",
               "switch.configure",
               "switch.upgrade" ]
        
    return switch_manager(ip, uart, works = works, verbose = verbose)

