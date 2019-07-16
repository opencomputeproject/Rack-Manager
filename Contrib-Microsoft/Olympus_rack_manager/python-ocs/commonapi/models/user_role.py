# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *
from controls.manage_role import *

class user_role(sys_base):
    def __init__(self, roleid = None, info = None, works = None):
        self.roleid = roleid

        if info == None:
            self.info = {}
        else:
            self.info = info
            
        if works == None:
            self.works = []
        else:
            self.works = works
            
    def getRole(self):   
        return group_detail_by_name(self.roleid)

    def getRoles(self):
        return ocs_group_list()           
       
def getrole(roleid = None):
    return user_role(roleid = roleid, works = [])
