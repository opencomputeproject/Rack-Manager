# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import ocslog
from ocsaudit_log import ocsaudit_rest_log_command
from ctypes import c_int, byref
from bottle import request
from controls.manage_user import group_id_from_usr_name
from controls.lib_utils import get_precheck_library
from pre_settings import rm_mode, rm_mode_enum, command_name_enum, pre_check, blade_check, api_authorization_check
from controls.utils import completion_code

RM_MODE = None

def get_mode ():
    """
    Get the mode the rack manager is configured to run in.
    
    :return The rack manager configuration mode.
    """
    
    return RM_MODE if (RM_MODE is not None) else get_op_mode ()

def get_op_mode ():
    """
    Get the operational mode of the rack manager.
    
    :return The rack manager mode.
    """
    
    try:
        precheck_binary = get_precheck_library ()
            
        i = c_int ()
        output = precheck_binary.get_rm_mode (byref (i))
        
        if (output == 0):
            manager_mode = rm_mode (i.value)
        else:
            manager_mode = rm_mode_enum.unknown_rm_mode
            
    except:
        ocslog.log_exception ()
        manager_mode = rm_mode_enum.unknown_rm_mode
        
    return manager_mode

def set_op_mode (mode = None):
    """
    Set the operational mode used as the default mode for the system.
    
    :param mode: Force an operation mode.  If this is not set, the system will be queried to
    determine the mode.
    """
    
    global RM_MODE
    
    if (mode is not None):
        RM_MODE = mode
    else:
        RM_MODE = get_op_mode ()

def get_max_num_systems ():
    """
    Get the maximum number of possible systems for the current configuration.
    
    :return The maximum number of systems.
    """
    
    mode = get_mode ()
    if ((mode == rm_mode_enum.standalone_rackmanager) or (mode == rm_mode_enum.rowmanager)):
        return 24
    else:
        return 48
    
def pre_check_function_call (op_category, device_id = 0):
    """
    Run pre-checks to see if the command can be run.
    
    :param op_category: The command category to check.
    :param device_id: The ID of the device the command will be executed against.
    
    :return An empty dictionary if the command can be run or a failure dictionary.
    """
    
    audit_log_request ()  
    return pre_check (get_current_role (), op_category, device_id, get_mode ())

def pre_check_authorization (op_category):
    """
    Run pre-checks to see if the user is authorized to run the command.
    
    :parame op_category: The command category to check.
    
    :return An empty dictionary if the user is authorized or a failure dictionary.
    """
    
    audit_log_request ()
    return api_authorization_check(get_current_role (), op_category)
    
def pre_check_blade_availability (device_id):
    """
    Run pre-checks to see if the blade is available.
    
    :param device_id: The ID of the blead to check.
    :param mode: The configuration mode of the rack manager.
    
    :return An empty dictionary if the blade is available or a failure dictionary.
    """
    
    return blade_check (command_name_enum.get_blade_state, device_id, get_mode ())

def get_pre_check_status_code (pre_check):
    """
    Check the pre-check result information to determine the HTTP status code result of the
    pre-check.
    
    :param pre_check: The result of the pre-check call.
    
    :return An HTTP status number for the pre-check result.  If the pre-check passed, 200 is
    returned.
    """
    
    if (pre_check):
        if (pre_check[completion_code.cc_key] != completion_code.failure):
            return 403
        else:
            return 401
    else:
        return 200

def audit_log_request ():
    """
    Log the request in the system audit log.
    """
          
    username = get_current_username ()
    ocsaudit_rest_log_command (request.method, request.url, request.url_args, username)
    
def get_current_username ():
    """
    Get the name of the user running the current request.
    
    :return The current user.
    """
    
    try:
        user = request.auth or (None, None)
        if (user is not None):
            return user[0]
        else:
            return None
    except:
        return None
    
def get_current_role ():
    """
    Get the group of the user running the current request.
    
    :return The group of the current user.
    """
    
    username = get_current_username ()
    return group_id_from_usr_name (username)