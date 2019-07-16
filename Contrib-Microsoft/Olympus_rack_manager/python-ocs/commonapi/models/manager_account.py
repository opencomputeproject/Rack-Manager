# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from sys_base import *

from controls.sys_works import *
from controls.manage_user import *

class manager_account(sys_base):
    def __init__(self, aid):
        self.aid = aid
    
    def getManagerAccounts(self):
        return user_list_all();    
            
    def getManagerAccount(self):
        return user_detail_by_name(self.aid)

    def getManagerAccountsbyRole(self, role):
        return user_name_from_group_name(role);
            
    def doWorks(self, parameters):        
        return user_manage_account_action(parameters)
       
def get_manageraccount(aid):
    return manager_account(aid = aid)

def get_manageraccounts():
    return manager_account(aid = 0)

