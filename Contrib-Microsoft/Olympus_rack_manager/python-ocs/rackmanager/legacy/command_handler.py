# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import response_handler
import ocslog
import re
import controls.manage_fwversion
import controls.manage_rack_manager
import controls.bladeinfo_lib
import controls.bladepowerstate_lib
import controls.manage_network
import controls.manage_powermeter
import controls.manage_powerport
import controls.manage_ocspower
import controls.bladenextboot_lib
import controls.manage_user
from controls.utils import set_failure_dict, check_success, completion_code
from pre_settings import command_name_enum
from bottle import HTTPError
from ocsrest import pre_check

def run_pre_check (command):
    """
    Execute authorization pre-checking for a command.
    
    :param func: The pre-check call to execute.
    :param args: Arguments that will be passed to the pre-check call.
    :param kwargs: Arguments that will be passed to the pre-check call.
    """
    
    try:
        output = pre_check.pre_check_authorization (command)
        code = pre_check.get_pre_check_status_code (output)
        if (code != 200):
            raise HTTPError (status = code, body = output[completion_code.desc])
            
    except HTTPError:
        raise
    
    except:
        ocslog.log_exception ()
        raise HTTPError (status = 500)
    
def process_set_result (response_type, result, extra_info = []):
    """
    Process the command result and generate a response object.
    
    :param resoponse_type: The type of response the should be generated.
    :param result: The command execution result.
    :param extra_info: Additional response objects to include with the response.
    
    :return The response object generated for the command.
    """
    
    status = response_handler.request_status (result)
    return response_handler.response_category (response_type, status = status, results = extra_info)

def process_blade_set_result (blade_id, result):
    """
    Process the blade command result and generate a response object.
    
    :param blade_id: The ID of the blade the command was exacuted against.
    :param result: The command execution result.
    
    :return The response object generated for the command.
    """
    
    num = response_handler.blade_number (blade_id)
    return process_set_result ("BladeResponse", result, extra_info = [num])
    
def parse_filter_parameters (parameters, parse):
    """
    Parse command parameters to get information filtering flags for the command.
    
    :param parameters: The list of parameters provided to the command.
    :param parse: The list of filtering parameter names to parse.
    
    :return A list with the values for the filtering flags.  The order in which they are returned
    matches the order they were defined in the parsing list.
    """
    
    parsed = []
    for flag in parse:
        val = parameters.get (flag, "false")
        if (val == "true"):
            parsed.append (True)
        else:
            parsed.append (False)
        
    if (not any (parsed)):
        parsed = [True] * len (parse)
        
    return parsed

def parse_blade_id (parameters, blade_id = "bladeid"):
    """
    Parse command parameters to get the blade ID for the command.
    
    :param parameters: The list of parameters provided to the command.
    :param blade_id: The name of the blade ID parameter.
    
    :return The blade ID to use for the command.  The blade ID provided by the request will be made
    negative if the ID is not valid.  A 0 is returned when no blade ID is provided.
    """
    
    try:
        blade = int (parameters.get (blade_id, 0))
        if (blade > pre_check.get_max_num_systems ()):
            blade = -blade
            
    except:
        # If there is an exception getting the parameter, assume no valid parameter is available.
        blade = 0
        
    return blade

def parse_port_id (parameters, port_id = "portno"):
    """
    Parse command parameters to get the socket port ID for the command.
    
    :param parameters: The list of parameters provided to the command.
    :param port_id: The name of the port ID parameter.
    
    :return The socket port ID to use for the command.  The port ID provided by the request will be
    made negative if the ID is not valid.  A 0 is returned when no port ID is provided.
    """
    
    try:
        port = int (parameters.get (port_id, 0))
        if (port > 4):
            port = -port
            
    except:
        # If there is an exception getting the parameter, assume no valid parameter is available.
        port = 0
        
    return port

def call_system_functions (calls):
    """
    Call any number of system functions and aggregate the responses.  The completion codes will be
    condensed into a single value, using the description from the first failure encountered.
    
    :param calls: A list of tuples containing functions to call and a parameter list for each call.
    
    :return An aggregated dictionary of the responses.
    """
    
    result = {}
    failures = []
    for call in calls:
        try:
            call_result = call[0] (**call[1])
            result.update (call_result)
            if (not check_success (call_result)):
                failures.append (call_result)
                
        except Exception:
            ocslog.log_exception ()
            failures.append (set_failure_dict ("Failure: Internal error"))
    
    if (len(failures) != len (calls)):
        result[completion_code.cc_key] = completion_code.success
        for failure in failures:
            if (completion_code.desc in failure):
                result[completion_code.desc] = failure[completion_code.desc]
                break
    else:
        result[completion_code.cc_key] = failures[0][completion_code.cc_key]
        result[completion_code.desc] = failures[0][completion_code.desc]
        
    return result

def call_blade_system_functions (blade_id, calls):
    """
    Call any number of systems functions for a single blade and aggregate the responses.  The blade
    will be checked for availability prior to calling the functions, and nothing will be called if
    this fails.
    
    :param blade_id: The ID of the blade to execute the calls for.
    :param calls: A list of tuples containing the functions to call, the name of the parameter that
    contains the blade ID, and a list of additional parameters to pass to the function.
    
    :return An aggregated dictionary of the responses.
    """
    
    result = pre_check.pre_check_blade_availability (blade_id)
    if (not result):
        blade_calls = []
        for call in calls:
            blade_call = (call[0], call[2])
            blade_call[1][call[1]] = blade_id
            blade_calls.append (blade_call)
            
        result = call_system_functions (blade_calls)
        
    return result

def call_blade_functions (calls):
    """
    Call a set of system functions for each blade in the rack.  The results of the calls will be
    aggregated together for each blade.
    
    :param calls: A list of tuples containing the functions to call, the name of the parameter that
    contains the blade ID, and a list of additional parameters to pass to the function.
    
    :return A list of dictionary aggregations.  Each entry are the results for one blade.
    """
                    
    blades = []
    for i in range (1, pre_check.get_max_num_systems () + 1):
        blades.append (call_blade_system_functions (i, calls))
            
    return blades

def execute_all_blades_command (cmd_object, parameters, id_name = "bladeid", row_manager = False):
    """
    Execute a command object for each blade in the rack.
    
    :param cmd_object: The type of command to execute.
    :param parameters: Additional parameters to pass to the command.
    :param id_name: The name of the blade ID parameter for the object.
    :param row_manager: Flag indicating the command should be executed as a row manager.
    
    :return A list of response objects for the commands executed against the blades.
    """
    
    blades = []
    for i in range (1, pre_check.get_max_num_systems () + 1):
        blade_param = parameters
        blade_param[id_name] = i
        blade_cmd = cmd_object (blade_param)
        
        if (not row_manager):
            blades.append (blade_cmd.get_response ())
        else:
            blades.append (blade_cmd.get_row_manager ())
        
    return blades

def set_all_blades_command (cmd_object, parameters, id_name = "bladeid", row_manager = False):
    """
    Execute a set command object for each blade in the rack.
    
    :param cmd_object: The type of set command to execute.
    :param parameters: Additional parameters to pass to the command.
    :param id_name: The name of the blade ID parameter for the object.
    :param row_manager: Flag indicating the command should be executed as a row manager.
    
    :return A response object for the command.
    """
    
    blade_list = response_handler.response_category ("bladeResponseCollection",
        results = execute_all_blades_command (cmd_object, parameters, id_name, row_manager))
        
    return response_handler.response_category ("AllBladesResponse",
        status = response_handler.request_status.get_placeholder_status (),
        results = [blade_list])
    
def convert_role_id (role):
    """
    Convert a user role parameter to the string that needs to be passed to system functions.
    
    :param role: The role parameter passed to the command.  If this is None, no conversion is
    performed.
    
    :return The string identifier for the role.  This will be empty if the role parameter is not
    valid.
    """
    
    if (role is not None):
        if ((role == "0") or (role == "wcscmuser")):
            role = "user"
        elif ((role == "1") or (role == "wcscmoperator")):
            role = "operator"
        elif ((role == "2") or (role == "wcscmadmin")):
            role = "admin"
        else:
            role = ""
        
    return role


def convert_boot_type (boot_type):
    """
    Convert a next boot type parameter to the string that needs to be passed to system functions.
    
    :param boot_type: The boot type parameter passed to the command.  If this is None, no conversion
    is performed.
    
    :return The string identifier for the boot type.  This will be empty if the boot type is not
    valid.
    """
    
    if (boot_type is not None):
        if ((boot_type == "1") or (boot_type == "nooverride")):
            boot_type = "none"
        elif ((boot_type == "2") or (boot_type == "forcepxe")):
            boot_type = "pxe"
        elif ((boot_type == "3") or (boot_type == "forcedefaulthdd")):
            boot_type = "disk"
        elif ((boot_type == "4") or (boot_type == "forceintobiossetup")):
            boot_type = "bios"
        elif ((boot_type == "5") or (boot_type == "forcefloppyorremovable")):
            boot_type = "floppy"
        else:
            boot_type = ""
            
    return boot_type

class get_service_version:
    """
    Handler for the GetServiceVersion command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        pass
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        result = call_system_functions ([
            (controls.manage_fwversion.get_ocsfwversion, {})
        ])
            
        status = response_handler.request_status (result)
        version = response_handler.service_version (result)
        
        return response_handler.response_category ("ServiceVersionResponse", status = status,
            results = [version])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class set_chassis_led_on:
    """
    Handler for the SetChassisAttentionLEDOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        pass
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        result = call_system_functions ([
            (controls.manage_rack_manager.set_rack_manager_attention_led, {"setting" : 1})
        ])
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class set_chassis_led_off:
    """
    Handler for the SetChassisAttentionLEDOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        pass
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        result = call_system_functions ([
            (controls.manage_rack_manager.set_rack_manager_attention_led, {"setting" : 0})
        ])
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class get_chassis_led_status:
    """
    Handler for the GetChassisAttentionLEDStatus command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        pass
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        result = call_system_functions ([
            (controls.manage_rack_manager.get_rack_manager_attention_led_status, {})
        ])
        
        status = response_handler.request_status (result)
        led = response_handler.led_state (result)
        
        return response_handler.response_category ("LedStatusResponse", status = status,
            results = [led])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
        
class get_blade_info:
    """
    Handler for the GetBladeInfo command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladeinfo_lib.system_info_call, "bladeId", {}),
                    (controls.bladeinfo_lib.get_server_data, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        info = response_handler.blade_info (result)
        versions = response_handler.blade_info_versions (result)
        
        result_mac = result if (check_success (result)) else {}
        mac = response_handler.response_category ("macAddress",
            results = response_handler.blade_nic_info.get_nic_list (result_mac))
        
        return response_handler.response_category ("BladeInfoResponse", status = status,
            results = [num, info, mac, versions])
        
class get_all_blades_info:
    """
    Handler for the GetAllBladesInfo command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        blade_list = response_handler.response_category ("bladeInfoResponseCollection",
            results = execute_all_blades_command (get_blade_info, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllBladesInfoResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class get_chassis_info:
    """
    Handler for the GetChassisInfo command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade, self.psu, self.controller, self.battery = parse_filter_parameters (parameters,
            ["bladeinfo", "psuinfo", "chassiscontrollerinfo", "batteryinfo"])
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        if (self.controller):
            result_ctrl_info = call_system_functions ([
                (controls.manage_rack_manager.read_fru, {"boardtype" : "rm_mb"}),
                (controls.manage_fwversion.get_ocsfwversion, {}),
                (controls.manage_rack_manager.get_rm_uptime, {})
            ])
            result_eth0 = call_system_functions ([
                (controls.manage_network.display_interface_by_name, {"if_name" : "eth0"}),
                (controls.manage_rack_manager.show_rack_manager_hostname, {})
            ])
            result_eth1 = call_system_functions ([
                (controls.manage_network.display_interface_by_name, {"if_name" : "eth1"})
            ])
            
            if (("IPv4Addresses" in result_eth1) and ("Gateway" in result_eth1["IPv4Addresses"])):
                del result_eth1["IPv4Addresses"]["Gateway"]
            
            ctrl_status = response_handler.request_status (result_ctrl_info)
            ctrl_info = response_handler.chassis_controller_info (result_ctrl_info)
            ctrl_net = response_handler.chassis_network_info.get_network_properties (result_eth0,
                result_eth1)
        else:
            ctrl_status = None
            ctrl_info = None
            ctrl_net = None
            
        if (self.psu):
            result_psu = call_system_functions ([
                (controls.manage_powermeter.get_rack_power_reading, {}),
                (controls.manage_rack_manager.read_fru, {"boardtype" : "rm_pib"})
            ])
            
            psu_list = response_handler.chassis_psu_info.get_psu_list (result_psu)
        else:
            psu_list = []
            
        if (self.blade and (not row_manager)):
            result_blades = call_blade_functions ([
                (controls.manage_powerport.powerport_get_port_status, "port_id",
                    {"port_type" : "pdu"}),
                (controls.bladeinfo_lib.get_server_data, "serverid", {})
            ])
            
            blade_list = response_handler.chassis_blade_info.get_blade_list (result_blades)
        else:
            blade_list = []
            
        if (self.battery):
            battery_list = response_handler.chassis_battery_info.get_battery_list ()
        else:
            battery_list = []
        
        results_temp = call_system_functions ([
            (controls.manage_rack_manager.get_sensor_objects, {})
        ])
        
        controller = response_handler.response_category ("chassisController", status = ctrl_status,
            results = [ctrl_info, ctrl_net])
        psu = response_handler.response_category ("psuCollections", results = psu_list)
        blade = response_handler.response_category ("bladeCollections", results = blade_list)
        battery = response_handler.response_category ("batteryCollections", results = battery_list)
        
        status = response_handler.request_status (results_temp)
        temp = response_handler.chassis_temp (results_temp)
        
        return response_handler.response_category ("ChassisInfoResponse", status = status,
            results = [controller, psu, blade, battery, temp])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class set_blade_led_on:
    """
    Handler for the SetBladeAttentionLEDOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_attention_led_on, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))

class set_all_blades_led_on:
    """
    Handler for the SetAllBladesAttentionLEDOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_led_on, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_led_on, self.args, row_manager = True)
    
class set_blade_led_off:
    """
    Handler for the SetBladeAttentionLEDOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_attention_led_off, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_led_off:
    """
    Handler for the SetAllBladesAttentionLEDOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_led_off, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_led_off, self.args, row_manager = True)
    
class set_blade_default_power_state_on:
    """
    Handler for the SetBladeDefaultPowerStateOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_default_powerstate_on, "serverid", {}) 
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_default_power_state_on:
    """
    Handler for the SetAllBladesDefaultPowerStateOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_default_power_state_on, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_default_power_state_on, self.args,
            row_manager = True)
    
class set_blade_default_power_state_off:
    """
    Handler for the SetBladeDefaultPowerStateOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_default_powerstate_off, "serverid", {}) 
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_default_power_state_off:
    """
    Handler for the SetAllBladesDefaultPowerStateOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_default_power_state_off, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_default_power_state_off, self.args,
            row_manager = True)

class get_blade_default_power_state:
    """
    Handler for the GetBladeDefaultPowerState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.get_server_default_powerstate, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        state = response_handler.blade_default_power_state (result)
        
        return response_handler.response_category ("BladeStateResponse", status = status,
            results = [num, state])
        
class get_all_blades_default_power_state:
    """
    Handler for the GetAllBladesDefaultPowerState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        blade_list = response_handler.response_category ("bladeStateResponseCollection",
            results = execute_all_blades_command (get_blade_default_power_state, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllBladesStateResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class get_power_state:
    """
    Handler for the GetPowerState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = pre_check.pre_check_blade_availability (self.port)
            if (not result):
                result[completion_code.cc_key] = completion_code.success
                result["Port State"] = "ON"
            else:
                status = result[completion_code.cc_key]
                if (status == completion_code.deviceoff):
                    result[completion_code.cc_key] = completion_code.success
                    result["Port State"] = "OFF"
                elif (status == completion_code.fwdecompress):
                    result[completion_code.cc_key] = completion_code.success
                    result["Port State"] = "OnFwDecompress"
                    
                    time = re.search ("(\d+) second", result[completion_code.desc])
                    if (time):
                        result["Decompress"] = time.group (1)
                else:
                    result = call_system_functions ([
                        (controls.manage_powerport.powerport_get_port_status,
                            {"port_id" : self.port, "port_type" : "pdu"})
                    ])
                    
                    if ("Port State" in result):
                        result["Port State"] = result["Port State"].upper ()
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
            
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.port)
        state = response_handler.power_state (result)
        
        return response_handler.response_category ("PowerStateResponse", status = status,
            results = [num, state])
        
class get_all_power_state:
    """
    Handler for the GetAllPowerState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        port_list = response_handler.response_category ("powerStateResponseCollection",
            results = execute_all_blades_command (get_power_state, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllPowerStateResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [port_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class set_power_on:
    """
    Handler for the SetPowerOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = call_system_functions ([
                (controls.manage_powerport.powerport_set_system_reset, {"port_id" : self.port,
                    "action_type" : "on", "port_type" : "pdu"})
            ])
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.port, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.port,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))

class set_all_power_on:
    """
    Handler for the SetAllPowerOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_power_on, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_power_on, self.args, row_manager = True)
    
class set_power_off:
    """
    Handler for the SetPowerOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = call_system_functions ([
                (controls.manage_powerport.powerport_set_system_reset, {"port_id" : self.port,
                    "action_type" : "off", "port_type" : "pdu"})
            ])
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.port, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.port,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_power_off:
    """
    Handler for the SetAllPowerOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_power_off, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_power_off, self.args, row_manager = True)
    
class set_blade_on:
    """
    Handler for the SetBladeOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_on, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_on:
    """
    Handler for the SetAllBladesOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_on, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_on, self.args, row_manager = True)
    
class set_blade_off:
    """
    Handler for the SetBladeOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_off, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_off:
    """
    Handler for the SetAllBladesOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_off, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_off, self.args, row_manager = True)

class get_blade_state:
    """
    Handler for the GetBladeState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.get_server_state, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        state = response_handler.blade_state (result)
        
        return response_handler.response_category ("BladeStateResponse", status = status,
            results = [num, state])
        
class get_all_blades_state:
    """
    Handler for the GetAllBladesState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        blade_list = response_handler.response_category ("bladeStateResponseCollection",
            results = execute_all_blades_command (get_blade_state, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllBladesStateResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class set_ac_socket_power_on:
    """
    Handler for the SetACSocketPowerStateOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_port_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self, port_type = "relay"):
        """
        Execute the command and get the result.
        
        :param port_type: The type of power port to turn on.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = call_system_functions ([
                (controls.manage_powerport.powerport_set_system_reset, {"port_id" : self.port,
                    "action_type" : "on", "port_type" : port_type})
            ])
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        if ((self.port < 0) and (self.port >= -24)):
            self.port = -self.port
            
        return self.get_response (port_type = "pdu")
    
class set_ac_socket_power_off:
    """
    Handler for the SetACSocketPowerStateOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_port_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_state)
        
    def get_response (self, port_type = "relay"):
        """
        Execute the command and get the result.
        
        :param port_type: The type of power port to turn off.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = call_system_functions ([
                (controls.manage_powerport.powerport_set_system_reset, {"port_id" : self.port,
                    "action_type" : "off", "port_type" : port_type})
            ])
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        if ((self.port < 0) and (self.port >= -24)):
            self.port = -self.port
            
        return self.get_response (port_type = "pdu")
    
class get_ac_socket_power_state:
    """
    Handler for the GetACSocketPowerState command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.port = parse_port_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self, port_type = "relay"):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.port > 0):
            result = call_system_functions ([
                (controls.manage_powerport.powerport_get_port_status, {"port_id" : self.port,
                    "port_type" : port_type})
            ])
            
            state = response_handler.ac_port_state (self.port, result)
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
            state = None
            
        status = response_handler.request_status (result)
        
        return response_handler.response_category ("ACSocketStateResponse", status = status,
            results = [state])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        if ((self.port < 0) and (self.port >= -24)):
            self.port = -self.port
            
        return self.get_response (port_type = "pdu")
        
class get_blade_power_limit:
    """
    Handler for the GetBladePowerLimit command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.manage_ocspower.get_server_power_limit, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        state = response_handler.blade_power_limit (result)
        
        return response_handler.response_category ("BladePowerLimitResponse", status = status,
            results = [num, state])
        
class get_all_blades_power_limit:
    """
    Handler for the GetAllBladesPowerLimit command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        blade_list = response_handler.response_category ("bladePowerLimitCollection",
            results = execute_all_blades_command (get_blade_power_limit, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllBladesPowerLimitResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class set_blade_power_limit:
    """
    Handler for the SetBladePowerLimit command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        self.limit = parameters.get ("powerlimitinwatts", None)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if ((self.blade > 0) and self.limit):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.manage_ocspower.set_server_power_limit, "serverid",
                        {"powerlimit" : self.limit})
                ]
            )
            
            if (not check_success (result)):
                if (re.search ("Given Limit .* is invalid", result.get (completion_code.desc, ""))):
                    result[completion_code.cc_key] = "ParameterOutOfRange"
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_power_limit:
    """
    Handler for the SetAllBladesPowerLimit command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit, self.args, row_manager = True)
    
class set_blade_power_limit_on:
    """
    Handler for the SetBladePowerLimitOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.manage_ocspower.set_server_power_limit_on, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_power_limit_on:
    """
    Handler for the SetAllBladesPowerLimitOn command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit_on, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit_on, self.args, row_manager = True)
    
class set_blade_power_limit_off:
    """
    Handler for the SetBladePowerLimitOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.manage_ocspower.set_server_power_limit_off, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_power_limit_off:
    """
    Handler for the SetAllBladesPowerLimitOff command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit_off, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_power_limit_off, self.args, row_manager = True)
    
class get_blade_power_reading:
    """
    Handler for the GetBladePowerReading command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.manage_ocspower.get_server_power_reading, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        power = response_handler.blade_power_reading (result)
        
        return response_handler.response_category ("BladePowerReadingResponse", status = status,
            results = [num, power])
        
class get_all_blades_power_reading:
    """
    Handler for the GetAllBladesPowerReading command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        blade_list = response_handler.response_category ("bladePowerReadingCollection",
            results = execute_all_blades_command (get_blade_power_reading, self.args,
                row_manager = row_manager))
        
        return response_handler.response_category ("GetAllBladesPowerReadingResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade_list])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
    
class get_chassis_health:
    """
    Handler for the GetChassisHealth command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade, self.psu, self.fan, self.battery = parse_filter_parameters (parameters,
            ["bladehealth", "psuhealth", "fanhealth", "batteryhealth"])
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_rm_state)
        
    def get_response (self, row_manager = False):
        """
        Execute the command and get the result.
        
        :param row_manager: Flag indicating the command should be executed as a row manager.
        
        :return The response object generated for the command.
        """
        
        if (self.blade and (not row_manager)):
            result_blades = call_blade_functions ([
                (controls.bladepowerstate_lib.get_server_state, "serverid", {})
            ])
            
            blade_list = []
            for i, blade in enumerate (result_blades):
                status = response_handler.request_status (blade)
                num = response_handler.blade_number (i)
                server = response_handler.blade_type (blade)
                state = response_handler.blade_state (blade)
                
                blade_list.append (response_handler.response_category ("BladeShellResponse",
                    status = status, results = [num, server, state]))
        else:
            blade_list = []
            
        if (self.fan):
            fan_list = response_handler.chassis_fan_info.get_fan_list ()
        else:
            fan_list = []
            
        if (self.psu):
            result_psu = call_system_functions ([
                (controls.manage_powermeter.get_rack_power_reading, {}),
                (controls.manage_rack_manager.read_fru, {"boardtype" : "rm_pib"})
            ])
            
            psu_list = response_handler.chassis_psu_info.get_psu_list (result_psu)
        else:
            psu_list = []
            
        if (self.battery):
            battery_list = response_handler.chassis_battery_info.get_battery_list ()
        else:
            battery_list = []
            
        blade = response_handler.response_category ("bladeShellCollection", results = blade_list)
        fan = response_handler.response_category ("fanInfoCollection", results = fan_list)
        psu = response_handler.response_category ("psuInfoCollection", results = psu_list)
        battery = response_handler.response_category ("batteryInfoCollection",
            results = battery_list)
        
        return response_handler.response_category ("ChassisHealthResponse",
            status = response_handler.request_status.get_placeholder_status (),
            results = [blade, fan, psu, battery])
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response (row_manager = True)
        
class get_next_boot:
    """
    Handler for the GetNextBoot command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.get_blade_state)
        
    def get_response (self, set_result = {}):
        """
        Execute the command and get the result.
        
        :param set_result: Command results passed from a call to set the next boot.
        
        :return The response object generated for the command.
        """
        
        if (set_result):
            result = set_result
        elif (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladenextboot_lib.get_nextboot, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return self.build_response (result)
        
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.build_response (set_failure_dict ("Not supported for Row Manager.",
            "CommandNotValidAtThisTime"))
    
    def build_response (self, result):
        """
        Generate the response object for the command execution result.
        
        :param result: The result of the system queries for the command.
        
        :return The response object for the result.
        """
        
        status = response_handler.request_status (result)
        num = response_handler.blade_number (self.blade)
        boot = response_handler.next_boot (result)
        
        return response_handler.response_category ("BootResponse", status = status,
            results = [num, boot])
        
class set_next_boot:
    """
    Handler for the SetNextBoot command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        self.blade = parse_blade_id (parameters)
        self.uefi = 1 if (parameters.get ("uefi", "false") == "true") else 0
        self.persist = 1 if (parameters.get ("persistent", "false") == "true") else 0
        self.boot = convert_boot_type (parameters.get ("boottype", None))
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        check = {}
        if (self.boot):
            if (self.blade > 0):
                check = pre_check.pre_check_blade_availability (self.blade)
                if (not check):
                    controls.bladenextboot_lib.set_nextboot (self.blade, self.boot, self.uefi,
                        self.persist)
        else:
            raise HTTPError (status = 400)
            
        return get_next_boot (self.args).get_response (set_result = check)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return get_next_boot (self.args).get_row_manager ()
    
class set_blade_active_power_cycle:
    """
    Handler for the SetBladeActivePowerCycle command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.blade = parse_blade_id (parameters)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.blade > 0):
            result = call_blade_system_functions (
                self.blade,
                [
                    (controls.bladepowerstate_lib.set_server_active_power_cycle, "serverid", {})
                ]
            )
        else:
            result = set_failure_dict ("ParameterOutOfRange", "ParameterOutOfRange")
        
        return process_blade_set_result (self.blade, result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return process_blade_set_result (self.blade,
            set_failure_dict ("Not supported for Row Manager.", "CommandNotValidAtThisTime"))
    
class set_all_blades_active_power_cycle:
    """
    Handler for the SetAllBladesActivePowerCycle command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.args = parameters
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_blade_state)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_active_power_cycle, self.args)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return set_all_blades_command (set_blade_active_power_cycle, self.args, row_manager = True)
    
class add_chassis_controller_user:
    """
    Handler for the AddChassisControllerUser command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.user = parameters.get ("username", None)
        self.password = parameters.get ("passwordstring", None)
        self.role = convert_role_id (parameters.get ("role", None))
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.user and self.password and (self.role is not None)):
            if (self.role):
                result = call_system_functions ([
                    (controls.manage_user.user_create_new, {"username" : self.user,
                        "pwd" : self.password, "role" : self.role})
                ])
            else:
                result = set_failure_dict ("Input security role is invalid", "ParameterOutOfRange")
        else:
            raise HTTPError (status = 400)
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class change_chassis_controller_user_password:
    """
    Handler for the ChangeChassisControllerUserPassword command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.user = parameters.get ("username", None)
        self.password = parameters.get ("newpassword", None)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.user and self.password):
            result = call_system_functions ([
                (controls.manage_user.user_update_password, {"username" : self.user,
                    "pwd" : self.password})
            ])
        else:
            raise HTTPError (status = 400)
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class change_chassis_controller_user_role:
    """
    Handler for the ChangeChassisControllerUserRole command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.user = parameters.get ("username", None)
        self.role = convert_role_id (parameters.get ("role", None))
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.user and (self.role is not None)):
            if (self.role):
                result = call_system_functions ([
                    (controls.manage_user.user_update_role, {"username" : self.user,
                        "role" : self.role})
                ])
            else:
                result = set_failure_dict ("Input security role is invalid", "ParameterOutOfRange")
        else:
            raise HTTPError (status = 400)
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()
    
class remove_chassis_controller_user:
    """
    Handler for the RemoveChassisControllerUser command.
    """
    
    def __init__ (self, parameters):
        """
        Initialize the command.
        
        :param parameters: The set of parameters passed to the command.
        """
        
        self.user = parameters.get ("username", None)
        
    def pre_check (self):
        """
        Run the pre-checks for the command.  An exception will be raised if the pre-checks fail.
        """
        
        run_pre_check (command_name_enum.set_rm_config)
        
    def get_response (self):
        """
        Execute the command and get the result.
        
        :return The response object generated for the command.
        """
        
        if (self.user):
            result = call_system_functions ([
                (controls.manage_user.user_delete_by_name, {"username" : self.user})
            ])
        else:
            raise HTTPError (status = 400)
        
        return process_set_result ("ChassisResponse", result)
    
    def get_row_manager (self):
        """
        Execute the command as a row manager and get the result.
        
        :return The response object generated for the command.
        """
        
        return self.get_response ()