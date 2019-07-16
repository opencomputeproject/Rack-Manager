# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-
#!/usr/bin/python

from ctypes import c_int, create_string_buffer, byref
from utils_print import print_response
from controls.lib_utils import get_authentication_library, get_precheck_library
from controls.utils import set_failure_dict, completion_code

rm_id = None
group_id = None
user_name = None
manager_mode = None

is_get_rm_call = False
is_set_rm_call = False
is_rm_config_call = False
    
class mode:
    pmdu = "PMDU"
    standalone = "STANDALONE"
    row = "ROW"
    
class rm_mode:
    """
    Enumration defination for the type of manager mode.
    """
    map = {
           0 : "PMDU_RACKMANAGER",
           1 : "STANDALONE_RACKMANAGER",
           2 : "ROWMANGER",
           3 : "UNKNOWN_RM_MODE",           
           4 : "TFB_DEV_BENCHTOP"           
    }
    
    def __init__(self,value):
        self.value = int(value)
        
    def __str__(self):
        return rm_mode.map[self.value]
    
    def __repr__(self):
        return str (self.value)
    
    def __int__(self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, rm_mode):
            return self.value == other.value
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class rm_mode_enum:
    """
    Enumertaion constants for the manager mode.
    """
    pmdu_rackmanager = rm_mode(0)
    standalone_rackmanager = rm_mode(1)
    rowmanager = rm_mode(2)
    unknown_rm_mode = rm_mode(3)
    tfb_dev_benchtop = rm_mode(4)

class command_name:
    """
    Enumration defination for the command name.
    """
    map = {
           0 : "GET_RM_STATE",
           1 : "SET_RM_STATE",
           2 : "SET_RM_CONFIG",
           
           3 : "GET_BLADE_STATE",
           4 : "SET_BLADE_STATE",
           5 : "SET_BLADE_CONFIG",
           
           #6 : "NUM_COMMANDS"           
    }
    
    def __init__(self,value):
        self.value = int(value)
        
    def __str__(self):
        return command_name.map[self.value]
    
    def __repr__(self):

        return str (self.value)
    
    def __int__(self):
        return self.value
    
class command_name_enum:
    """
    Enumertaion constants for the command name.
    """
    get_rm_state = command_name(0)
    set_rm_state = command_name(1)
    set_rm_config = command_name(2)
    get_blade_state = command_name(3)
    set_blade_state = command_name(4)
    set_blade_config = command_name(5)
    #num_commands = command_name(6)

def get_rm_mode():
    global manager_mode   
    global rm_id
    try:
        precheck_binary = get_precheck_library ()
            
        i = c_int();
            
        output = precheck_binary.get_rm_mode(byref(i))

        if output != 0:
            #log_error("Failed to get manager mode using precheck library.", output)
            #print "Failed to get manager mode using precheck library.", output
            return -1            
        else:
            manager_mode = rm_mode(i.value)
            rm_id = i.value

    except Exception:   
        #log_error("failed to get rm mode",e)
        #print "Exception to get rm mode",e
        return -1
    
    return output

def verify_caller_admin_permission():
    output = 0
    
    if group_id is None:
        output = verify_caller_permission()
    
    if output == 0 and group_id == 0:
        return True
    
    return False
    
def verify_caller_permission():
    global group_id
    global auth_binary
    
    try:
        auth_binary = get_authentication_library()
        
        caller_id = c_int()
        output = auth_binary.verify_caller_permission(byref(caller_id))
                
        if output == 0:
            group_id = caller_id.value
        else:
            return -1
            
    except Exception:
        return -1
    
    return output

def check_pre_check_output (output, dev_id = None):
    """
    Check the output from the precheck library to determine the failure reason.
    
    :param output: The status output returned by a pre-check call.
    :param dev_id: The c_int object for the device ID.
    
    :return An empty dictionary if the call succeded.  Otherwise, a dictionary that contains the
    error information.
    """
    
    if (output == 0):
        return {}
    elif (output < 0):
        precheck_binary = get_precheck_library ()
        
        errordesc = create_string_buffer (256) 
        error = precheck_binary.get_app_error (output, errordesc) 
                     
        if (error == 0):
            msg = errordesc.value.lower ().strip ()
            if (msg == "device is not present."):
                return set_failure_dict (errordesc.value, completion_code.notpresent)
            elif (msg == "device is not powered on."):
                return set_failure_dict (errordesc.value, completion_code.deviceoff)
            elif (msg == "device firmware is loading, retry again."):
                if (dev_id is not None):
                    delay = c_int ()
                    delay_output = precheck_binary.get_server_fwready_delay (dev_id, byref (delay))
                    if (delay_output == 0):
                        return set_failure_dict (
                            "Server On. Firmware Decompression Time Remaining: {0} second(s)".format (delay.value),
                            completion_code.fwdecompress)
                    else:
                        return set_failure_dict (errordesc.value + "Delay time: Failure",
                        completion_code.fwdecompress)
                else:
                    return set_failure_dict (errordesc.value, completion_code.fwdecompress)
            else:
                return set_failure_dict (errordesc.value)
        else:
            msg = "Failed to call precheck get_app_error for error code {0}: {1}".format (output, error)
            return set_failure_dict (msg)
    else:
        return set_failure_dict ("{0}".format (output))
    
def blade_check (command, device, mode):
    """
    Call the precheck library to determine if the blade is available to execute commands against.
    
    :param command: The command type being executed.
    :param device: The ID of the device the command is being executed against.
    :param mode: THe mode the rack manager is operating in.
    
    :return An empty dictionary if the blade is available.  Otherwise, a dictionary that contains
    the failure code and reason why the blade is not available.
    """
    
    precheck_binary = get_precheck_library ()
    
    cmd_id = c_int (int (command))
    dev_id = c_int (int (device))
    mode_id = c_int (int (mode))
    
    output = precheck_binary.blade_check (cmd_id, dev_id, mode_id)
    return check_pre_check_output (output, dev_id)

def api_authorization_check (group, command):
    """
    Call the precheck library to determine if the user is authorized to execute a command.
    
    :param group: The ID of the group for the user executing the command.
    :param command: The command type being executed.
    
    :return An empty dictionary if the user is authorized to execute the command.  Otherwise, a
    dictionary that contains the failure information.
    """
    
    precheck_binary = get_precheck_library ()
    
    gp_id = c_int (int (group))
    cmd_id = c_int (int (command))
    
    output = precheck_binary.api_authorization_check (gp_id, cmd_id)
    return check_pre_check_output (output)
    
def pre_check (group, command, device, mode):
    """
    Call the precheck library to determine if the command can be run in the current context.
    
    :param group: The ID of the group for the user executing the command.
    :param command: The command type being executed.
    :param device: The ID of the device the command is being executed against.
    :param mode: The mode the rack manager is operating in.
    
    :return An empty dictionary if the command can be executed.  Otherwise, a dictionary that
    contains the failure code and reason why the command can not be executed.
    """
    
    precheck_binary = get_precheck_library ()
    
    gp_id = c_int (int (group))
    cmd_id = c_int (int (command))
    dev_id = c_int (int (device))
    mode_id = c_int (int (mode))
    
    output = precheck_binary.pre_check (gp_id, cmd_id, dev_id, mode_id)
    return check_pre_check_output (output, dev_id)
    
def pre_check_manager(command_id, deviceid):
    global is_get_rm_call
    global is_set_rm_call
    global is_rm_config_call   
      
    try:
        precheck_result = pre_check (group_id, command_id, deviceid, rm_id)
        if (precheck_result):
            print_response (precheck_result)
            return False
        else:
            if command_id == repr(command_name_enum.get_rm_state):
                is_get_rm_call = True
            elif command_id == repr(command_name_enum.set_rm_config):
                is_rm_config_call = True
            elif command_id == repr(command_name_enum.set_rm_state):
                is_set_rm_call = True
                
            return True
        
    except Exception, e:
        print_response((set_failure_dict("pre_check_manager(): Exception {0}".format(e), completion_code.failure)))        
        return False

def pre_check_helper (cmd_name, cache, device_id):
    if (cache):
        return True
    else:
        return pre_check_manager (repr (cmd_name), device_id) 
    
def mode_request():
    try:
        if manager_mode == None:
            return None
        
        if manager_mode == rm_mode_enum.pmdu_rackmanager or \
           manager_mode == rm_mode_enum.tfb_dev_benchtop or \
           manager_mode == rm_mode_enum.standalone_rackmanager:    
            return "rm" 
        elif manager_mode == rm_mode_enum.rowmanager:
            return "row"
        else:
            print("Invalid manager mode")
            return None
        
    except Exception, e:
        print "mode_request Exception: {0}".format(e)
        return None
    
def get_mode():
    try:
        if manager_mode == None:
            return None
        
        if manager_mode == rm_mode_enum.pmdu_rackmanager or \
           manager_mode == rm_mode_enum.tfb_dev_benchtop:
            return mode.pmdu 
        elif manager_mode == rm_mode_enum.standalone_rackmanager: 
            return mode.standalone
        elif manager_mode == rm_mode_enum.rowmanager:
            return mode.row
        else:
            return None
        
    except Exception, e:
        print "get_mode Exception: {0}".format(e)
        return None
    