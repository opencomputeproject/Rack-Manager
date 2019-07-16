# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *
from controls.manage_logentry import *
from controls.sys_works import *

class event_log(sys_base):
    
    def __init__(self, entry_id = None, log_id = None, type = None, device_id = None):
        self.entry_id = entry_id
        self.log_id = log_id
        
        if type == None:
            self.type = ""
        else:
            self.type = type
        
        if device_id == None:
            self.device_id = ""
        else:
            self.device_id = device_id
            
    def get_eventlog_entry(self):
        return get_logentry(self.entry_id, self.log_id, self.type, self.device_id)
       
    def doWorks(self, parameters):
        return eventlog_actions(parameters) 

def get_eventlog(entry_id, log_id, type, device_id):
    return event_log(entry_id, log_id = log_id, type = type, device_id = device_id)


def get_eventlogs(log_id, type, device_id):
    return event_log(entry_id = 0, log_id = log_id, type = type, device_id = device_id)
     
