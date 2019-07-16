# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import pwd
import ctypes

from utils_print import print_response
from controls.lib_utils import get_audit_library
from controls.utils import set_failure_dict, completion_code


class cmd_type:
    type_get = 0
    type_patch = 1
    type_post = 2
    type_show = 3
    type_set = 4
    type_shell = 5
    type_start = 6
    type_stop = 7
    type_delete = 8
    type_unknown = 9


class cmd_interface:
    interface_ocscli = 0
    interface_wcscli = 1
    interface_rest = 2

def ocsaudit_initialize():
    try:
        audit_library = get_audit_library()
        
        output = audit_library.OcsAudit_Init()
        
        if output != 0:
            print "Failed to intialize OcsAudit", output
        
    except Exception as e:
        print "ocsaudit_initialize Exception {0}".format(e)


def ocsaudit_get_username():
    """ Return username of currently logged in user
    """
    return pwd.getpwuid(os.getuid()).pw_name


def ocsaudit_log_command(username, type, interface, command, command_args):
    """ Log command to OcsAudit
    """
        
    if username == "":
        username = ocsaudit_get_username()
    
    try:
        audit_library = get_audit_library()
                
        p_username = ctypes.c_char_p(username)
        p_command = ctypes.c_char_p(command)
        p_args = ctypes.c_char_p(command_args)
        
        output = audit_library.OcsAudit_LogCommand(p_username, type, interface, p_command, p_args)

        if output != 0:
            print "Failed to log command using audit log"

    except Exception as e:
        print "ocsaudit_log_command Exception {0}".format(e)

def ocsaudit_rest_log_command(method, url, url_args, username):
    """ Log REST command to OcsAudit
    """
    
    try:
        if method == "GET":
            type = cmd_type.type_get
        elif method == "POST":
            type = cmd_type.type_post
        elif method == "PATCH":
            type = cmd_type.type_patch
        elif method == "DELETE":
            type = cmd_type.type_delete
        else:
            type = cmd_type.type_unknown
            print "Unidentified command type {0}".format(method)
                                
        url = url.split("/v1/",1)[-1]
        args = " ".join(url_args)
        
        ocsaudit_log_command(username, type, cmd_interface.interface_rest, 
                             url, args)
    except Exception as e:
        print "ocsaudit_rest_log_command Exception {0}".format(e)
