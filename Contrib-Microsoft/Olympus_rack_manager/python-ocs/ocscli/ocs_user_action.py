# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import pre_settings

from utils_print import * 
from ocsaudit_log import *
from controls.utils import *
from argparse import ArgumentParser
from models.manager_account import *


#######################################################
# User Actions Support functions
#######################################################
def user_Actions(command_args):
    """
        Entry point to user management.
            List all users:
                ocscli show user info
                
            List user information by user name.
                ocscli show user info -t {user} -u {username}
            
            List user information by user name.
                ocscli show user info -t {role} -r {rolename}                        
                
            Add new User:
                ocscli set user add -u {username} -p '{password}' -r {role name}
            
            Update password: 
                ocscli set user update -t "password" -u {username} -p {new password}
            
            Update role:
                ocscli set user update -t "role" -u {username} -r {new role} 
            
            Delete User:
                ocscli set user delete -u {username}        
    """
    
    parser = ArgumentParser(description = "Display, create, or delete user accounts, or update role/password")

    subparsers = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
    
    user_addCommand_options(subparsers)
    user_infoCommand_options(subparsers)
    user_updateCommand_options(subparsers)
    user_deleteCommand_options(subparsers)
       
    args = parse_args_retain_case(parser, command_args) 
    
    if args.command == "info":                       
        ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                             "user " + str(args.command)," ".join(command_args[1:]))
                
        get_rm_cmd = repr(pre_settings.command_name_enum.get_rm_state)
        permission = pre_settings.pre_check_manager(get_rm_cmd, 0) 
            
        if (permission == False):
            return
        else:
            if args.username and args.role:
                user_displayByNameRole(args.username, args.role)            
            elif args.username:
                user_displayByName(args.username)
            elif args.role:
                user_displayByRole(args.role)
            else:
                user_displayAll()
    else:
        protected_args = command_args[1:]

        # Mask password when logged in OcsAudit
        if "-p" in protected_args:
            index = protected_args.index("-p") + 1
            protected_args[index] = "*****"
            
        ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                             "user " + str(args.command)," ".join(protected_args))
        
        set_rm_cmd = repr(pre_settings.command_name_enum.set_rm_state)
        permission = pre_settings.pre_check_manager(set_rm_cmd, 0) 
            
        if (permission == False):
            return
        else:
            if args.command == "add":
                if not args.username:
                    print_response(set_failure_dict("Must provide username", completion_code.failure))
                elif not args.password:
                    print_response(set_failure_dict("Must provide password", completion_code.failure))
                elif not args.role:
                    print_response(set_failure_dict("Must provide role", completion_code.failure))
                else:
                    user_add(args.username, args.password, args.role)     
                           
            elif args.command == "update":
                if args.oType.lower() == "password":
                    if args.password:
                        user_updatePwd(args.username, args.password)
                    else:
                        print_response(set_failure_dict("Must provide password", completion_code.failure))
                elif args.oType.lower() == "role":
                    if args.role:
                        user_updateRole(args.username, args.role)
                    else:
                        print_response(set_failure_dict("Must provide role", completion_code.failure))
                        
            elif args.command == "delete":
                user_delete(args.username)

#######################################################
# User Actions Support functions
#######################################################

def user_infoCommand_options(subparsers):   
    info_parser = subparsers.add_parser('info', help = 'Display user accounts information')    
    info_parser.add_argument('-u',  dest = 'username', required = False, help = 'Username')
    info_parser.add_argument('-r',  dest = 'role', required = False, choices = ['admin', 'operator', 'user'], help = 'User roles: supported admin, operator, and user')
      
def user_addCommand_options(subparsers):     
    add_parser = subparsers.add_parser('add', help = 'Add user account')
    add_parser.add_argument('-u',  dest = 'username', required = True, help = 'Username')
    add_parser.add_argument('-p',  dest = 'password', required = False, help = 'Password for user')
    add_parser.add_argument('-r',  dest = 'role', required = False, choices = ['admin', 'operator', 'user'], help = 'User roles: supported admin, operator, and user')

def user_updateCommand_options(subparsers):         
    update_parser = subparsers.add_parser('update', help='Update user account password or role')
    update_parser.add_argument('-t', dest = 'oType', choices = ['password', 'role'], required = True, help = 'Provide update type user or role.')
    update_parser.add_argument('-u',  dest = 'username', required = True, help = 'Username')
    update_parser.add_argument('-p',  dest = 'password', required = False, help = 'Password for user')
    update_parser.add_argument('-r',  dest = 'role', required = False, choices=['admin', 'operator', 'user'], help = 'User roles: supported admin, operator, and user')

def user_deleteCommand_options(subparsers):      
    delete_parser = subparsers.add_parser('delete', help = 'Delete user account')
    delete_parser.add_argument('-u',  dest = 'username', required = True, help = 'Username')

def user_displayByRole(role):
    output = {}
    
    usr = get_manageraccounts()
    info = usr.getManagerAccountsbyRole(role)
    
    for user_name in info.split(","):
        if not role in output:
            output[role] = [user_name]
        else:
            output[role].append(user_name)
    
    output[completion_code.cc_key] = completion_code.success
    
    print_response(output)
    
def user_displayAll():
    usr = get_manageraccounts()
    info = usr.getManagerAccounts()
    
    print_response(info)

def user_displayByName(username):
    usr = get_manageraccount(username)
    info = usr.getManagerAccount()
        
    print_response(info)
    
def user_displayByNameRole(username, role):
    usr = get_manageraccount(username)
    info = usr.getManagerAccount()
    
    if info["RoleId"] == role:
        print_response(info)

def user_add(username, password, role):
    try:   
        usr = get_manageraccount(username)
        action = {}
        
        action["action"] = "user_add"
        action["username"] = username
        action["password"] = password
        action["role"] = role
        
        info = usr.doWorks(action)
        print_response(info)
        
    except Exception, e:  
        return ("user_add() Exception ", e)

def user_delete(username):
    try:
        usr = get_manageraccount(username)
        action = {}
        
        action["action"] = "user_delete"
        action["username"] = username
        
        info = usr.doWorks(action)
        print_response(info)
        
    except Exception, e:  
        return ("user_delete() Exception ", e) 
        
def user_updatePwd(username, password):
    try: 
        usr = get_manageraccount(username)
        action = {}
        
        action["action"] = "update_pwd"
        action["username"] = username
        action["password"] = password
        
        info = usr.doWorks(action)
        print_response(info)
        
    except Exception, e:  
        return ("user_updatePwd() Exception ", e) 

def user_updateRole(username, role):
    try:
        usr = get_manageraccount(username)
        action = {}
        
        action["action"] = "update_role"
        action["username"] = username        
        action["role"] = role
        
        info = usr.doWorks(action)
        print_response(info)
        
    except Exception, e:  
        return ("user_updateRole() Exception ", e) 
