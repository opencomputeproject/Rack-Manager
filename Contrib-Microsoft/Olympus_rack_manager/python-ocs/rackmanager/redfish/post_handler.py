# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import view_helper
import load_config
from ocsrest import authentication, pre_check
from bottle import HTTPError, auth_basic
from pre_settings import command_name_enum
from controls.utils import completion_code
from enums import ResetType, RoleId, RearmType, AlertAction, Operation, FWRegion, Target
from netaddr import IPAddress
from parameters import parameter_parser
import controls.manage_ocspower
import controls.bladepowerstate_lib
import controls.bladelog_lib
import controls.manage_rack_manager
import controls.manage_powermeter
import controls.manage_user
import models.switch_manager
import controls.blade_fw_update
import controls.manage_rmedia

def validate_action_parameters (validation):
    """
    Validate the parameters passed to the action.
    
    :param validation: The validation to perform on the parameters.  This is a mapping of parameter
    names to parser instances
    
    :return A dictionary containing the validated parameters.
    """
    
    data = view_helper.get_json_request_data ()
    params = {}
    errors = {}
    for param, parser in validation.items ():
        if (param in data):
            try:
                parser.parse_parameter (data[param], params)
            
            except Exception as error:
                view_helper.append_parameter_error (errors, view_helper.invalid_property_value_key,
                    str (error))
        else:
            view_helper.append_missing_parameter_error (errors, param)

    for param in data.keys ():
        if ((param not in validation) and ("@" not in param)):
            view_helper.append_unknown_parameter_error (errors, param)
    
    if errors:
        view_helper.raise_status_response (400, errors)
    
    return params

def check_action_result (result, success_code = 200, fail_code = 500):
    """
    Check the result of an action to see if it completed successfully.  If it did not, an exception
    is raised.
    
    :param result: The result of the action.
    :param success_code: The HTTP status code to return on success.
    :param fail_code: The HTTP status code to return on failure.
    
    :return A successful response message if no error occurred processing the action.
    """
    
    status = success_code if (result[completion_code.cc_key] == completion_code.success) else fail_code
    result = view_helper.create_response_with_status (code = result)
    return view_helper.return_status_response (status, result)
    
###################
# System components
###################
@auth_basic (authentication.validate_user)
def post_system_reset (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    validation = {
        "ResetType" : parameter_parser ("type", str, ResetType,
         {"valid" : [ResetType.ON, ResetType.GRACEFUL_SHUTDOWN, ResetType.GRACEFUL_RESTART]})
    }
    params = validate_action_parameters (validation)
    
    if (params["type"] == ResetType.ON):
        result = controls.bladepowerstate_lib.set_server_on (system)
    elif (params["type"] == ResetType.GRACEFUL_SHUTDOWN):
        result = controls.bladepowerstate_lib.set_server_off (system)
    else:
        result = controls.bladepowerstate_lib.set_server_active_power_cycle (system)
    
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_power_limit_rearm_trigger (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
        
    validation = {
        "RearmType" : parameter_parser ("rearm", int, RearmType)
    }
    params = validate_action_parameters (validation)
    
    current = controls.manage_ocspower.get_server_default_power_limit (system)
    if (current.get (completion_code.cc_key, completion_code.failure) != completion_code.success):
        view_helper.raise_status_response (500, view_helper.create_response_with_status (current))
        
    params["alert_action"] = int (AlertAction (current["AlertAction"], convert = True))
    
    result = controls.manage_ocspower.set_server_activate_psu_alert (system, **params)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_power_activate_limit (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    result = controls.manage_ocspower.set_server_power_limit_on (system)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_power_deactivate_limit (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    result = controls.manage_ocspower.set_server_power_limit_off (system)
    return check_action_result (result)
        
@auth_basic (authentication.validate_user)
def post_system_battery_test (system):
    system = int (system)
    check = controls.manage_ocspower.get_server_psu_battery_present (system)
    if (check.get (completion_code.cc_key, completion_code.failure) == completion_code.success):
        if (check["Battery"] == "No"):
            raise HTTPError (status = 404)
    else:
        view_helper.raise_status_response (500, view_helper.create_response_with_status(check))
    
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    result = controls.manage_ocspower.set_server_psu_battery_test (system)
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_system_power_clear_faults (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    result = controls.manage_ocspower.clear_server_psu_faults (system)
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_system_power_fw_update (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    validation = {
        "File" : parameter_parser ("fw_path", str),
        "FWRegion" : parameter_parser ("fw_type", int, FWRegion)
    }
    params = validate_action_parameters (validation)
    
    params["blade_id"] = system
    params["fw_type"] = controls.blade_fw_update.blade_fw_type (params["fw_type"])
    result = controls.blade_fw_update.start_psu_fw_update (**params)
    
    if ("FW Status" in result):
        result[completion_code.desc] = result["FW Status"]
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_power_fw_update_state (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    validation = {
        "Operation" : parameter_parser ("operation", int, Operation)
    }
    params = validate_action_parameters (validation)
    
    op = controls.blade_fw_update.blade_fw_operation (params["operation"])
    if (op == controls.blade_fw_update.blade_fw_operation_enum.ABORT):
        result = controls.blade_fw_update.abort_psu_fw_update (system)
    else:
        result = controls.blade_fw_update.query_psu_fw_update (system)
        
    if ("FW Status" in result):
        result[completion_code.desc] = result["FW Status"]
    return check_action_result (result)

@auth_basic (authentication.validate_user)    
def post_system_phase_clear_faults (system, phase):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    result = controls.manage_ocspower.clear_server_psu_faults (system, phase)
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_system_manager_clear_log (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    result = controls.bladelog_lib.clear_server_log (system, raw_output = False)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_remotemedia_mount (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)

    validation = {
        "ImageName" : parameter_parser ("imagename", str) 
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_rmedia.mount_rmedia (system, **params)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_system_remotemedia_unmount (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    result = controls.manage_rmedia.umount_rmedia (system)
    return check_action_result (result)    
    
#########################
# Rack Manager components
#########################
@auth_basic (authentication.validate_user)
def post_rack_manager_power_clear_faults ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    result = controls.manage_ocspower.set_rack_manager_clear_power_faults ()
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_rack_manager_clear_log ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    result = controls.manage_rack_manager.clear_rack_manager_telemetry_log ()
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_rack_manager_fw_update ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "File" : parameter_parser ("filename", str) 
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_rack_manager.set_rack_manager_fwupdate (**params)
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_rack_manager_tftp_get ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "Server" : parameter_parser ("server", str, IPAddress),
        "File" : parameter_parser ("file", str),
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_rack_manager.manager_tftp_client_get (**params)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_rack_manager_tftp_put ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "Server" : parameter_parser ("server", str, IPAddress),
        "File" : parameter_parser ("file", str),
        "Target" : parameter_parser ("target", str, Target)
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_rack_manager.manager_tftp_client_put (**params)
    return check_action_result (result)

@auth_basic (authentication.validate_user)
def post_rack_manager_tftp_delete ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "File" : parameter_parser ("file", str),
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_rack_manager.manager_tftp_deletefile (**params)
    return check_action_result (result)
            
#################
# PMDU components
#################
@auth_basic (authentication.validate_user)
def post_pmdu_power_meter_clear_max_power ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    result = controls.manage_powermeter.set_rack_clear_max_power ()
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_pmdu_power_meter_clear_faults ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    result = controls.manage_powermeter.set_rack_clear_power_faults ()
    return check_action_result (result)
    
##############################
# Management switch components
##############################
@auth_basic (authentication.validate_user)
def post_switch_reset ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    validation = {
        "ResetType" :parameter_parser  ("type", str, ResetType,
            {"valid" : [ResetType.FORCE_RESTART]})
    }
    validate_action_parameters (validation)
    
    switch = models.switch_manager.getswitch (load_config.switch_ip, load_config.switch_uart)
    result = switch.do_reset ()
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_switch_configure ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "File" : parameter_parser ("config_file", str)
    }
    params = validate_action_parameters (validation)
    
    switch = models.switch_manager.getswitch (load_config.switch_ip, load_config.switch_uart)
    result = switch.do_configure (**params)
    return check_action_result (result)
    
@auth_basic (authentication.validate_user)
def post_switch_fw_update ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "File" : parameter_parser ("fw_file", str)
    }
    params = validate_action_parameters (validation)
    
    switch = models.switch_manager.getswitch (load_config.switch_ip, load_config.switch_uart)
    result = switch.do_upgrade (**params)
    return check_action_result (result)

############################
# Account service components
############################
@auth_basic (authentication.validate_user)
def post_accounts ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    validation = {
        "UserName" : parameter_parser ("username", str),
        "Password" : parameter_parser ("pwd", str),
        "RoleId" : parameter_parser ("role", str, RoleId)
    }
    params = validate_action_parameters (validation)
    
    result = controls.manage_user.user_create_new (**params)
    return check_action_result (result, success_code = 201)
