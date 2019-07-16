# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import ctypes

from ctypes import *
from utils import *
from lib_utils import get_authentication_library

############################################################################################################
# User actions Functions 
############################################################################################################

#Create user with given credentials
def user_create_new(username, pwd, role):
    result = {}
    output = 1

    try:
        auth_binary = get_authentication_library ()
        
        if user_id_from_name(username) is not None:
            return set_failure_dict("User already exists", completion_code.failure)
        
        if len(username) < 6:
            return set_failure_dict("Username needs to be at least 6 characters", completion_code.failure)
        
        username = c_char_p(username)
        pwd = c_char_p(pwd)
        role = c_char_p(role)
        
        output = auth_binary.add_user(username, role, pwd)

        if output is not 0:
            return set_failure_dict(("Failed to execute command using libocsauth", output),completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict(("user_create_new() Exception ", e),completion_code.failure)
    
    result[completion_code.cc_key] = completion_code.success
    
    return result        

#Update user password credentials 
def user_update_password(username, pwd):  
    result = {}
    output = 1
    
    try:
        auth_binary = get_authentication_library ()
        
        if user_id_from_name(username) is None:
            return set_failure_dict("User does not exist", completion_code.failure)
                
        username = c_char_p(username)
        pwd = c_char_p(pwd)
        
        output = auth_binary.update_password(username, pwd)

        if output is not 0:
            return set_failure_dict(("Failed to execute command using libocsauth", output),completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict(("user_update_password() Exception ", e),completion_code.failure)
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

#Update user role
def user_update_role(username, role):
        
    result = {}
    output = 1
    
    try:
        auth_binary = get_authentication_library ()
        
        if user_id_from_name(username) is None:
            return set_failure_dict("User does not exist", completion_code.failure)
        
        username = c_char_p(username)
        role = c_char_p(role)
        
        output = auth_binary.ocs_change_role(username, role)

        if output is not 0:
            return set_failure_dict(("Failed to execute command using libocsauth", output),completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict(("user_update_role() Exception ", e),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

#Update user password credentials""" 
def user_delete_by_name(username):
    result = {}
    output = 1
    
    try:
        auth_binary = get_authentication_library ()
        
        if user_id_from_name(username) is None:
            return set_failure_dict("User does not exist", completion_code.failure)
        
        if (username != 'root'):
            username = c_char_p(username)
        else:
            return set_failure_dict("Removing root user not allowed", completion_code.failure)
        
        output = auth_binary.remove_user(username)

        if output is not 0:
            return set_failure_dict(("Failed to execute command using libocsauth", output),completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict(("user_delete_by_name() Exception ", e),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

#Get user information
def user_detail_by_name(username):
    try:
        if username is None:
            return set_failure_dict("User name is required for user_detail_by_name.", completion_code.failure)
            
        uid = user_id_from_name(username)        
        gid = group_id_from_usr_name(username)
            
        if uid == None or gid == -1:
            return set_failure_dict("User does not exist: {0}".format(username), completion_code.failure)
            
        return user_detail(username, gid)
    
    except Exception, e:
        return set_failure_dict("user_detail_by_name() Exception {0}".format(e), completion_code.failure)   
    
def user_detail(username, usr_role):  
    try:
        auth_binary = get_authentication_library()
    
        role_name = create_string_buffer(20) 
    
        ret = auth_binary.get_groupname_from_id(usr_role, 20, byref(role_name))
                                
        return {"Description": "Ocs {0} account".format(role_name.value),
                "Enabled": getUserAccountStatus(username),
                "UserName": username,
                "RoleId": role_name.value,
                "Locked": "False",
                completion_code.cc_key: completion_code.success}
        
    except Exception, e:
        return set_failure_dict("user_detail() Exception {0}".format(e), completion_code.failure) 

def getUserAccountStatus (username):
    # Check to see if account is disabled or locked.
    # We need this method added to Auth library
    
    return True

def user_list_all():    
    # List all Ocs User by user role    
    # Ocs user roles are group id 
    # admin: group id 0
    # operator: group id 37
    # user: group id 100
        
    output = {}
    accounts = {}
    num_accounts = 0
    
    #list of admin
    for user_name in user_name_from_group_name('admin').split(","):
        if not 'admin' in output:
            output['admin'] = [user_name]
            if user_name != '':
                num_accounts = num_accounts + 1
        else:
            output['admin'].append(user_name)
            num_accounts = num_accounts + 1
    
    #list of operator
    for user_name in user_name_from_group_name('operator').split(","):
        if not 'operator' in output:
            output['operator'] = [user_name]
            if user_name != '':
                num_accounts = num_accounts + 1

        else:
            output['operator'].append(user_name)
            num_accounts = num_accounts + 1
        
    #list of ocs_user
    for user_name in user_name_from_group_name('user').split(","):
        if not 'user' in output:
            output['user'] = [user_name]
            if user_name != '':
                num_accounts = num_accounts + 1

        else:
            output['user'].append(user_name)
            num_accounts = num_accounts + 1
    
    accounts["accounts"] = output
    accounts["num_accounts"] = num_accounts
    accounts[completion_code.cc_key] = completion_code.success

    return accounts

def user_name_from_group_name(gp_name):
    try:
        auth_binary = get_authentication_library ()
            
        group = c_char_p(gp_name)
        members = create_string_buffer(220)
        i = c_int(220)
                        
        ret = auth_binary.ocs_group_members(group, byref(i),byref(members))  
                      
        if ret == 0:
            return members.value
        else:
            return ''
        
    except Exception, e:  
        print("user_name_from_group_name() Exception {0}".format(e))        
        return ''
    
def user_id_from_name(username):
    try:
        auth_binary = get_authentication_library ()
            
        usr = c_char_p(username)
        uid = c_uint()
                        
        ret = auth_binary.get_userid_from_name(usr, byref(uid))  
                      
        if ret == 0:
            return uid.value
        else:
            return None

    except Exception, e:  
        print("user_id_from_name() Exception {0}".format(e))
        return None
       
def group_id_from_usr_name(username):   
    try:
        auth_binary = get_authentication_library ()
            
        usr = c_char_p(username)
        gpid = c_int(-1)
         
        ret = auth_binary.get_user_group_id(usr, byref(gpid))
        if ret == 0:
            return gpid.value
        else:
            return -1
    except Exception, e: 
        print("group_id_from_usr_name() Exception {0}".format(e))
        return -1
    
def group_name_from_usr_name(username):   
    try:
        auth_binary = get_authentication_library ()
            
        usr = c_char_p(username)
        gname = create_string_buffer(20)
         
        ret = auth_binary.get_user_group_name(usr, 20, byref(gname))
        if ret == 0:
            return gname.value
        else:
            return "unknown user"
    except Exception, e:  
        print("group_name_from_usr_name() Exception {0}".format(e))
        return "failed"
    
def get_gid_from_username(username):
    result = {}
    
    try:
        result["gid"] = group_id_from_usr_name(username)
            
    except Exception, e:  
        return set_failure_dict("get_gid_from_username() Exception {0}".format(e), completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_groupname_from_username(username):
    result = {}
    
    try:
        result["groupname"] = group_name_from_usr_name(username)
            
    except Exception, e:  
        return set_failure_dict("get_groupname_from_username() Exception {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result
    
