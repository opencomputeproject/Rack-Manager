# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
import os

from sys_base import *
from controls.sys_works import *
from controls.manage_powermeter import *

class powermeter_unit(sys_base):
    
    def __init__(self, info = None, works = None):
        self.type = type
        
        if info == None:
            self.info = {}
        else:
            self.info = info
            
        if works == None:
            self.works = []
        else:
            self.works = works
                      
    def doWorks(self, parameters):    
        try:           
            if parameters["mode"] == "action":
                return system_powermeter_action(parameters) 
            elif parameters["mode"] == "display":
                return system_powermeter_display(parameters)
            else:
                return {'Completion Code':'Failure' , 'Error': 'Unknown Mode'}
        except Exception, e:
            return ("powermeter_unit.doWorks() Exception ", e)      
      
    def getWorks(self):        
        return self.works 
       
def get_powermeter():
    #default supported actions
    
    works =  ['powermeter.limitpolicy',
              'powermeter.alertpolicy',
              'powermeter.clearmaxpower',
              'powermeter.clearfaults']
        
    return powermeter_unit(works = works)        
