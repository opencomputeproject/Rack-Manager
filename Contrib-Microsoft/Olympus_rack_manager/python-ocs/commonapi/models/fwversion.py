# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *

from controls.manage_fwversion import *

class fwversion(sys_base): 
        
    def __init__(self, id = None , info = None, works = None):
                
        if id == None:
            self.id = 0
        else:
            self.id = int(id)
        
        if info == None:
            self.info = {}
        else:
            self.info = info
            
        if works == None:
            self.works = []
        else:
            self.works = works
  
    def getFwVersion(self):
        
        fwver_rsp={}
                
        fwver_rsp= get_ocsfwversion() 
        return fwver_rsp
    
    
    def getWorks(self):        
        return self.works
       
def getocsfwversions():
    
    works =  [ ]
        
    return fwversion( works = works)
