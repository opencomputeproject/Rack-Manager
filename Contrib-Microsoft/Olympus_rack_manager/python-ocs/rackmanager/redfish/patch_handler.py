# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import view_helper
import get_handler
import enums
import parameters
import re
from ocsrest import authentication, pre_check
from bottle import HTTPError, auth_basic
from pre_settings import command_name_enum
from controls.utils import set_failure_dict, completion_code
from parameters import parameter_parser
from netaddr import IPAddress
from pre_settings import rm_mode_enum
import controls.manage_rack_manager
import controls.manage_network
from controls.sys_works import ethernet_actions_results
import controls.manage_user
import controls.manage_powerport
import controls.bladenextboot_lib
import controls.bladetpmphypresence_lib
import controls.bladepowerstate_lib
import controls.bladebios_lib
import controls.manage_fpga

def execute_patch_request_actions (requested, action_map, tree = []):
    """
    Handler for all patch requests to change system parameters based on received information.
    
    :param requested: A dictionary that contains the set of system parameters to change.
    :param action_map: A mapping of the function to call for each parameter that can be set.
    Each mapping contains a tuple that has a function pointer, parameter parser, and additional
    arguments that should be passed to the function.
    :param tree: The ancestry of the current set of request properties.
    
    :return A result dictionary to be used to generate the response.
    """
    
    result = {}
    if requested is not None:
        for param, value in requested.iteritems ():
            if ("@" not in param):
                try:
                    if (hasattr (value, "keys")):
                        parents = list (tree)
                        parents.append (param)
                        
                        action_data = execute_patch_request_actions (value, action_map,
                            tree = parents)
                        view_helper.append_response_information (result, action_data)
                    elif (isinstance (value, list)):
                        for i, entry in enumerate (value):
                            parents = list (tree)
                            parents.append (param)
                            parents.append ("[{0}]".format (i))
                            
                            action_data = execute_patch_request_actions (entry, action_map,
                                tree = parents)
                            view_helper.append_response_information (result, action_data)
                            i = i + 1
                    else:
                        action = ""
                        if len (tree):
                            action = "/".join (tree) + "/"
                        action = action + param
                        
                        if (action in action_map):
                            call = action_map[action]
                            args = call[2].copy ()
                            try:
                                call[1].parse_parameter (value, args)
                            
                            except TypeError as error:
                                view_helper.append_invalid_property_type (result,
                                    action.split ("/"))
                                continue
                        
                            except Exception as error:
                                view_helper.append_invalid_property_value (result,
                                    action.split ("/"), str (error))
                                continue
                            
                            action_data = call[0] (**args)
                            view_helper.append_response_information (result, action_data)
                        else:
                            view_helper.append_read_only_property (result, action.split ("/"))
                    
                except Exception as error:
                    view_helper.append_response_information (
                        result, set_failure_dict (str (error), completion_code.failure))
                
    return result

def validate_patch_request_and_execute (action_map, name, default_params = dict ()):
    """
    Check the request for to make sure the object only contains valid properties.  If it does, then
    execute the requested actions.
    
    :param action_map: A mapping of the function to call for each parameter that can be set.
    Each mapping contains a tuple that has a function pointer, parameter parser, and additional
    arguments that should be passed to the function.
    :param name: The name of the resource to validate against.
    :param default_params: Parameters to use when generating the default set of properties.
    
    :return A result dictionary to be used to generate the response.
    """
    
    try:
        requested = view_helper.get_json_request_data ()
                
    except Exception as error:
        view_helper.raise_status_response (400,
            view_helper.create_response_with_status (description = str (error)))
                        
    valid_set = view_helper.get_json_default_resource (name, values = default_params)
    
    errors = {}
    check_for_invalid_parameters (requested, valid_set, errors)
    if errors:
        view_helper.raise_status_response (400, errors)
    
    return execute_patch_request_actions (requested, action_map)

def check_for_invalid_parameters (requested, valid_set, errors, path = "#"):
    """
    Check that all the properties contained in the request object are valid for the resource the
    request was submitted against.
    
    :param requested: The request object to validate.
    :param valid_set: The complete set of valid properties.
    :param errors: The dictionary of errors that will be updated with parameters errors"
    """
    
    for param, value in requested.items ():
        if ("@" not in param):
            param_path = "{0}/{1}".format (path, param)
            if (param not in valid_set):
                view_helper.append_unknown_parameter_error (errors, param_path)
            elif (hasattr (value, "keys")):
                check_for_invalid_parameters (value, valid_set[param], errors, path = param_path)
            elif (isinstance (value, list)):
                if (not isinstance (valid_set[param], list)):
                    view_helper.append_parameter_type_error (errors, param_path)
                else:
                    for i, entry in enumerate (value):
                        check_for_invalid_parameters (entry, valid_set[param][0], errors,
                            path = "{0}[{1}]".format (param_path, i))
                
def apply_ip_address (address = None, mask = None, gateway = None, addr_type = None,
    save_args = True, args = dict ()):
    """
    Helper function to aggregate network device parameters and apply the settings.
    
    :param address: The IP address to assign to the network interface.
    :param mask: The subnet mask.
    :param gateway: A default gateway to set for the system.
    :param addr_type: The type of IP address being assigned.
    :param save_args: A flag indicating if the specified parameters should be saved or if the
    device should be configured.  When configuring the device, any unspecified parameters will be
    extracted from the argument aggregation.
    :param args: The aggregation of previously saved network parameters.
    
    :return Result information for the configuration request.
    """
    
    result = {}
    
    if (save_args):
        if (address is not None):
            args["ip_address"] = address
        if (mask is not None):
            args["netmask"] = mask
        if (gateway is not None):
            args["gateway"] = gateway
        if (addr_type is not None):
            args["addr_type"] = addr_type
    else:
        try:
            if ("addr_type" in args):
                if (args["addr_type"] == enums.AddressOrigin.DHCP):
                    if (("ip_address" in args) or ("netmask" in args) or ("gateway" in args)):
                        result = set_failure_dict (
                            "No IP address information can be specified when using DHCP.",
                            completion_code.failure)
                    else:
                        result = ethernet_actions_results (
                            controls.manage_network.set_dhcp_interface (args["if_name"]))
                else:
                    missing = []
                    if ("ip_address" not in args):
                        missing.append ("Address")
                    if ("netmask" not in args):
                        missing.append ("SubnetMask")
                    if ("gateway" not in args):
                        args["gateway"] = ""
                        
                    if missing:
                        for param in missing:
                            view_helper.append_missing_parameter_error (result, param)
                    else:
                        del args["addr_type"]
                        result = ethernet_actions_results (
                            controls.manage_network.set_static_interface (**args))
            else:
                view_helper.append_missing_parameter_error (result, "AddressOrigin")
                
        except Exception as error:
            result = set_failure_dict (str (error))
        
    return result

def apply_management_gateway (gateway = None, mask = None, save_args = True, args = dict ()):
    """
    Helper function to aggregate management network route parameters and apply the settings.
    
    :param gateway: The IP address of the gateway for the management network.
    :param mask: The netmask for the management network.
    :param save_args: A flag indicating if the specified parameters should be saved or if the
    route should be configured.  When configuring the route, any unspecified parameters will be
    extracted from the argument aggregation.
    :param args: The aggregation of previously saved network parameters.
    
    :return Result information for the configuration request.
    """
    
    result = {}
    
    if (save_args):
        if (gateway is not None):
            args["gateway"] = gateway
        if (mask is not None):
            args["netmask"] = mask
    else:
        missing = []
        if ("gateway" not in args):
            missing.append ("MgmtGateway")
        if ("netmask" not in args):
            missing.append ("MgmtNetmask")
            
        if missing:
            for param in missing:
                view_helper.append_missing_parameter_error (result, param)
        else:
            result = controls.manage_network.set_management_network (**args)
        
    return result

def apply_power_throttle (policy = None, dcpolicy = None, force_set = False, args = dict ()):
    """
    Apply system power throttle settings.  The settings will only be applied if all arguments have
    been received, or if the force_set flag has been set.  If forcing, any missing arguments will be
    queried from the system.  If no parameters have been saved or the parameters have previously
    been applied, forcing is a noop.
    
    :param policy: The enable/disable flag for power alert throttling.
    :param dcpolicy: The enable/disable flag for datacenter alert throttling.
    :param force_set: Flag to indicate the available parameters should be applied.
    :param args: The set of previously received parameters.
    
    :return Result information for the configuration request.
    """
    
    result = {}
    
    if (policy is not None):
        args["policy"] = policy
    if (dcpolicy is not None):
        args["dcpolicy"] = dcpolicy
        
    done = args.get ("done", False)
    if ((not done) and force_set and (("policy" not in args) != ("dcpolicy" not in args))):
        current = controls.manage_powermeter.get_rack_power_throttle_status ()
        if (current[completion_code.cc_key] != completion_code.success):
            return current
            
        args["policy"] = args.get ("policy", int (enums.Boolean (current["IsAlertEnabled"],
            convert = True)))
        args["dcpolicy"] = args.get ("dcpolicy", int (enums.Boolean (
            current["IsDcThrottleEnabled"], convert = True)))
    
    if ((not done) and ("policy" in args) and ("dcpolicy" in args)):
        result = controls.manage_powermeter.set_rack_power_throttle (**args)
        args["done"] = True
    
    return result

def apply_bios_configuration (server_id, config):
    """
    Apply the chosen BIOS configuration.
    
    :param server_id: The ID of the server to configure.
    :param config: The string representation of the chosen configuartion.
    
    :return Result information for the configuration requset.
    """
    
    parts = config.split (".")
    return controls.bladebios_lib.set_server_bios_config (serverid = server_id,
        majorconfig = parts[0], minorconfig = parts[1])
    
def apply_default_power_limit (server_id, power_limit = None, ms_delay = None, auto_remove = None,
    force_set = False, args = dict ()):
    """
    Apply default power limit settings.  The settings will only be applied if all arguments have
    been received, or if the force_set flag has been set.  If forcing, any missing arguments will be
    queried from the system.  If no parameters have been saved or the parameters have previously
    been applied, forcing is a noop.
    
    :param server_id: The ID of the server to configure.
    :param power_limit: The default power limit to apply.
    :param ms_delay: The delay after asserting the throttle signal.
    :param auto_remove: The delay before the power policy is automatically deactivated.
    :param force_set: Flag to indicate the available parameters should be applied.
    :param args: The set of previously received parameters.
    
    :return Result information for the configuration request.
    """
    
    result = {}
    
    if (power_limit is not None):
        args["power_limit"] = power_limit
    if (ms_delay is not None):
        args["ms_delay"] = ms_delay
    if (auto_remove is not None):
        args["auto_remove"] = auto_remove
        
    done = args.get ("done", False)
    if ((not done) and force_set and
        (("power_limit" in args) or ("ms_delay" in args) or ("auto_remove" in args)) and
        (not (("power_limit" in args) and ("ms_delay" in args) and ("auto_remove" in args)))):
        current = controls.manage_ocspower.get_server_default_power_limit (server_id)
        if (current[completion_code.cc_key] != completion_code.success):
            return current
        
        args["power_limit"] = args.get ("power_limit",
            int (parameters.remove_non_numeric (current["PowerLimit"])))
        args["ms_delay"] = args.get ("ms_delay",
            int (parameters.remove_non_numeric (current["ThrottleDuration"])))
        args["auto_remove"] = args.get ("auto_remove",
            int (parameters.remove_non_numeric (current["LimitDelay"])))
    
    if ((not done) and ("power_limit" in args) and ("ms_delay" in args) and
        ("auto_remove" in args)):
        result = controls.manage_ocspower.set_server_default_power_limit (server_id, **args)
        args["done"] = True
    
    return result

def apply_blade_next_boot (boottype = None, mode = None, force_set = False, args = dict ()):
    """
    Apply next boot settings for a system.  The settings will only be applied if all arguments have
    been received, or if the force_set flag has been set.  If forcing, any missing arguments will be
    queried from the system.  If no parameters have been saved or the parameters have previously
    been applied, forcing is a noop.
    
    :param boottype: The device to use for the next blade boot.
    :param mode: The boot mode to use.
    :param force_set: Flag to indicate the available parameters should be applied.
    :param args: The set of previously received parameters.
    
    :return Result information for the configuration request.
    """
    
    result = {}
    
    if (boottype is not None):
        args["boottype"] = boottype
    if (mode is not None):
        args["mode"] = mode
        
    done = args.get ("done", False)
    if ((not done) and force_set and (("boottype" not in args) != ("mode" not in args))):
        current = controls.bladenextboot_lib.get_nextboot (args["serverid"])
        if (current[completion_code.cc_key] != completion_code.success):
            return current
            
        args["boottype"] = args.get ("boottype", str (enums.BootSourceOverrideTarget (
            current["BootSourceOverrideTarget"], convert = True, cmd_arg = True)))
        args["mode"] = args.get ("mode", int (enums.BootSourceOverrideMode (
            current["BootSourceOverrideMode"], convert = True)))
    
    if ((not done) and ("boottype" in args) and ("mode" in args)):
        result = controls.bladenextboot_lib.set_nextboot (**args)
        args["done"] = True
    
    return result

def validate_bios_configuration (config):
    """
    Validate that the BIOS configuration value is formatted properly.
    
    :param config: The configuration to validate.
    
    :return The validated configuration.
    """
    
    if (not re.match ("\d\.\d$", config)):
        raise ValueError ("{0} is not a valid BIOS configuration.".format (config))
    
    return config

def validate_datetime (time):
    """
    Validate that the DateTime value is formatted properly.
    
    :param time: The configuration to validate.
    
    :return The validated configuration.
    """
    
    if (not re.match('(\d{4})[-](\d{2})[-](\d{2})T(\d{2})[:](\d{2})[:](\d{2})Z$', time)):
        raise ValueError ("{0} is not a DateTime value.".format (time))
    
    return time

###################
# System components
###################
@auth_basic (authentication.validate_user)
def patch_system (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    next_boot_args = {"serverid" : system}
    actions = {
        "Boot/BootSourceOverrideTarget" : (apply_blade_next_boot,
            parameter_parser ("boottype", str, enums.BootSourceOverrideTarget, {"cmd_arg" : True}),
            {"args" : next_boot_args}),
        "Boot/BootSourceOverrideMode" : (apply_blade_next_boot,
            parameter_parser ("mode", int, enums.BootSourceOverrideMode),
            {"args" : next_boot_args}),
        "Oem/Microsoft/TPMPhysicalPresence" : (
            controls.bladetpmphypresence_lib.set_tpm_physical_presence,
            parameter_parser ("presence", int, enums.Boolean), {"serverid" : system}),
        "Oem/Microsoft/DefaultPowerState" : (
            controls.bladepowerstate_lib.set_server_default_powerstate,
            parameter_parser ("state", str, enums.PowerState), {"serverid" : system})
    }
    
    result = validate_patch_request_and_execute (actions, "system")
    next_boot = apply_blade_next_boot (force_set = True, args = next_boot_args)
    view_helper.append_response_information (result, next_boot)
    
    return get_handler.get_system (system, patch = result)
    
@auth_basic (authentication.validate_user)
def patch_system_bios_config (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    actions = {
        "ChosenConfiguration" : (apply_bios_configuration,
            parameter_parser ("config", str, validate_bios_configuration), {"server_id" : system})
    }
    
    result = validate_patch_request_and_execute (actions, "system_bios_cfg")
    return get_handler.get_system_bios_config (system, patch = result)
    
@auth_basic (authentication.validate_user)
def patch_system_fpga (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    actions = {
        "BypassMode" : (controls.manage_fpga.set_fpga_bypass,
            parameter_parser ("bypass", str, enums.BypassMode), {"serverid" : system})
    }
    
    result = validate_patch_request_and_execute (actions, "system_fpga")
    return get_handler.get_system_fpga (system, patch = result)
    
@auth_basic (authentication.validate_user)
def patch_system_chassis (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_blade_state,
        device_id = system)
    
    actions = {
        "IndicatorLED" : (controls.bladepowerstate_lib.set_server_attention_led,
            parameter_parser ("state", int, enums.IndicatorLED), {"serverid" : system})
    }
    
    result = validate_patch_request_and_execute (actions, "system_chassis")
    return get_handler.get_system_chassis (system, patch = result);
    
@auth_basic (authentication.validate_user)
def patch_system_power (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call,
        command_name_enum.set_blade_config, device_id = system)
    
    limit_args = {}
    actions = {
        "PowerControl/[0]/PowerLimit/LimitInWatts" : (
            controls.manage_ocspower.set_server_power_limit,
            parameter_parser ("powerlimitvalue", int), {"serverid" : system}),
        "PowerControl/[0]/Oem/Microsoft/DefaultLimitInWatts" : (apply_default_power_limit,
            parameter_parser ("power_limit", int), {"server_id" : system, "args" : limit_args}),
        "PowerControl/[0]/Oem/Microsoft/AutoRemoveDelayInSec" : (apply_default_power_limit,
            parameter_parser ("auto_remove", int), {"server_id" : system, "args" : limit_args}),
        "PowerControl/[0]/Oem/Microsoft/FastThrottleDurationInMs" : (apply_default_power_limit,
            parameter_parser ("ms_delay", int), {"server_id" : system, "args" : limit_args}),
        "PowerControl/[0]/Oem/Microsoft/AlertAction" : (
            controls.manage_ocspower.set_server_activate_psu_alert,
            parameter_parser ("alert_action", int, enums.AlertAction), {"serverid" : system})
    }
    
    result = validate_patch_request_and_execute (actions, "system_power")
    limit = apply_default_power_limit (server_id = system, force_set = True, args = limit_args)
    view_helper.append_response_information (result, limit)
    
    return get_handler.get_system_power (system, patch = result)
    
#########################
# Rack Manager components
#########################
@auth_basic (authentication.validate_user)
def patch_rack_manager_chassis ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    actions = {
        "IndicatorLED" : (controls.manage_rack_manager.set_rack_manager_attention_led,
            parameter_parser ("setting", int, enums.IndicatorLED), {}),
    }
    
    result = validate_patch_request_and_execute (actions, "rack_manager_chassis")
    return get_handler.get_rack_manager_chassis (patch = result)
    
@auth_basic (authentication.validate_user)
def patch_rack_manager ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
        
    actions = {
        "DateTime" : (controls.manage_rack_manager.set_rack_manager_time,
            parameter_parser ("datetime", str, validate_datetime), {}),
        "Oem/Microsoft/HostName" : (controls.manage_rack_manager.set_hostname,
            parameter_parser ("hostname", str), {}),
        "Oem/Microsoft/TFTP/ServiceStatus" : (
            controls.manage_rack_manager.set_manager_tftp_service_state,
            parameter_parser ("state", str, enums.ServiceStatus), {}),
        "Oem/Microsoft/TFTP/ServiceEnabled" : (
            controls.manage_rack_manager.set_manager_tftp_service_config,
            parameter_parser ("enable", bool, parameter_parser.validate_bool), {}),
        "Oem/Microsoft/NFS/ServiceStatus" : (
            controls.manage_rack_manager.set_manager_nfs_service_state,
            parameter_parser ("state", str, enums.ServiceStatus), {}),
        "Oem/Microsoft/NFS/ServiceEnabled" : (
            controls.manage_rack_manager.set_manager_nfs_service_config,
            parameter_parser ("enable", bool, parameter_parser.validate_bool), {}),
        "Oem/Microsoft/NTP/ServiceStatus" : (
            controls.manage_rack_manager.set_manager_ntp_service_state,
            parameter_parser ("state", str, enums.ServiceStatus), {}),
        "Oem/Microsoft/NTP/ServiceEnabled" : (
            controls.manage_rack_manager.set_manager_ntp_service_config,
            parameter_parser ("enable", bool, parameter_parser.validate_bool), {}),
        "Oem/Microsoft/NTP/TimeServer" : (controls.manage_rack_manager.set_rack_manager_ntp_server,
            parameter_parser ("server_ip", str, IPAddress), {}),
        "Oem/Microsoft/ThrottleControl/LocalBypass" : (
            controls.manage_rack_manager.set_manager_throttle_local_bypass,
            parameter_parser ("enable", bool, parameter_parser.validate_bool), {}),
        "Oem/Microsoft/ThrottleControl/LocalEnable" : (
            controls.manage_rack_manager.set_manager_throttle_output_enable,
            parameter_parser ("enable", bool, parameter_parser.validate_bool), {})
    }
    
    if (not pre_check.get_mode () == rm_mode_enum.rowmanager):
        actions.update ({
            "Oem/Microsoft/RemoteITP/ServiceStatus" : (
                controls.manage_rack_manager.set_manager_itp_service_state,
                parameter_parser ("state", str, enums.ServiceStatus), {}),
            "Oem/Microsoft/RemoteITP/ServiceEnabled" : (
                controls.manage_rack_manager.set_manager_itp_service_config,
                parameter_parser ("enable", bool, parameter_parser.validate_bool), {})
        })
    else:
        actions.update ({
            "Oem/Microsoft/ThrottleControl/RowBypass" : (
                controls.manage_rack_manager.set_row_throttle_bypass,
                parameter_parser ("enable", bool, parameter_parser.validate_bool), {}),
            "Oem/Microsoft/ThrottleControl/RowEnable" : (
                controls.manage_rack_manager.set_row_throttle_output_enable,
                parameter_parser ("enable", bool, parameter_parser.validate_bool), {})
        })
        
    result = validate_patch_request_and_execute (actions, "rack_manager")
    return get_handler.get_rack_manager (patch = result)

@auth_basic (authentication.validate_user)
def patch_rack_manager_ethernet (eth):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    requested = view_helper.get_json_request_data ()
    if ("IPv4Addresses" in requested):
        address = requested["IPv4Addresses"]
        if (len (address) > 1):
            raise HTTPError (status = 400, body = "No more than one IP address may be specified.")
    
    ip_args = {}
    mgmt_args = {}
    actions = {
        "IPv4Addresses/[0]/Address" : (apply_ip_address,
            parameter_parser ("address", str, IPAddress), {"args" : ip_args}),
        "IPv4Addresses/[0]/SubnetMask" : (apply_ip_address,
            parameter_parser ("mask", str, parameter_parser.validate_subnet_mask),
            {"args" : ip_args}),
        "IPv4Addresses/[0]/AddressOrigin" : (apply_ip_address,
            parameter_parser ("addr_type", str, enums.AddressOrigin), {"args" : ip_args})
    }
    if (eth == "eth0"):
        actions.update ({
            "IPv4Addresses/[0]/Gateway" : (apply_ip_address,
                parameter_parser ("gateway", str, IPAddress), {"args" : ip_args}),
        })
    else:
        actions.update ({
            "Oem/Microsoft/MgmtGateway" : (apply_management_gateway,
                parameter_parser ("gateway", str, IPAddress), {"args" : mgmt_args}),
            "Oem/Microsoft/MgmtNetmask" : (apply_management_gateway,
                parameter_parser ("mask", str, parameter_parser.validate_subnet_mask),
                {"args" : mgmt_args})
        })
    
    result = validate_patch_request_and_execute (actions, "rack_manager_ethernet",
        default_params = {"Intf" : eth})
    if (not result):
        if (ip_args):
            ip_args["if_name"] = eth
            set_data = apply_ip_address (save_args = False, args = ip_args)
            view_helper.append_response_information (result, set_data)
            
        if (mgmt_args):
            set_data = apply_management_gateway (save_args = False, args = mgmt_args)
            view_helper.append_response_information (result, set_data)
        
    return get_handler.get_rack_manager_ethernet (eth, patch = result)
    
#################
# PMDU components
#################
@auth_basic (authentication.validate_user)
def patch_pmdu_power_meter ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    throttle_args = {}
    actions = {
        "DatacenterThrottleEnabled" : (apply_power_throttle,
            parameter_parser ("dcpolicy", int, enums.Boolean), {"args" : throttle_args}),
        "AlertEnabled" : (apply_power_throttle,
            parameter_parser ("policy", int, enums.Boolean), {"args" : throttle_args}),
        "AlertLimitWatts" : (controls.manage_powermeter.set_rack_power_limit_policy,
            parameter_parser ("powerlimit", float), {})
    }
    
    result = validate_patch_request_and_execute (actions, "pmdu_power_meter")
    throttle = apply_power_throttle (force_set = True, args = throttle_args)
    view_helper.append_response_information (result, throttle)
    
    return get_handler.get_pmdu_power_meter (patch = result)

@auth_basic (authentication.validate_user)
def patch_pdu_control (port):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    port = int (port)
    actions = {
        "PowerState" : (controls.manage_powerport.powerport_set_system_reset,
            parameter_parser ("action_type", str, enums.PowerState, {"to_lower" : True}),
            {"port_id" : port, "port_type" : "pdu"})
    }
    
    result = validate_patch_request_and_execute (actions, "power_control_pdu")
    return get_handler.get_pdu_control (port, patch = result)

@auth_basic (authentication.validate_user)
def patch_relay_control (relay):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    relay = int (relay)
    actions = {
        "PowerState" : (controls.manage_powerport.powerport_set_system_reset,
            parameter_parser ("action_type", str, enums.PowerState, {"to_lower" : True}),
            {"port_id" : relay, "port_type" : "relay"})
    }
    
    result = validate_patch_request_and_execute (actions, "power_control_relay")
    return get_handler.get_relay_control (relay, patch = result)

@auth_basic (authentication.validate_user)
def patch_row_manager_power_control (rack):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_state)
    
    rack = int (rack)
    actions = {
        "PowerState" : (controls.manage_powerport.powerport_set_system_reset,
            parameter_parser ("action_type", str, enums.PowerState, {"to_lower" : True}),
            {"port_id" : rack, "port_type" : "pdu"}),
        "BootStrapping" : (controls.manage_powerport.powerport_set_row_boot_strapping,
            parameter_parser ("strapping", str, enums.BootStrapping), {"port_id" : rack})
    }
    
    result = validate_patch_request_and_execute (actions, "power_control_manager")
    return get_handler.get_row_manager_power_control (rack, patch = result)
    
############################
# Account service components
############################
@auth_basic (authentication.validate_user)
def patch_account (account):
    parameters.verify_account_name (account)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    actions = {
        "Password" : (controls.manage_user.user_update_password, parameter_parser ("pwd", str),
            {"username" : account}),
        "RoleId" : (controls.manage_user.user_update_role,
            parameter_parser ("role", str, enums.RoleId), {"username" : account})
    }
    
    result = validate_patch_request_and_execute (actions, "account")
    return get_handler.get_account (account, patch = result)
