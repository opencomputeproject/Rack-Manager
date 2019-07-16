# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import view_helper
import enums
import parameters
import load_config
import resources
import os
from ocsrest import authentication, pre_check
from bottle import HTTPError, auth_basic, static_file, request
from pre_settings import command_name_enum, rm_mode_enum
from controls.utils import set_failure_dict, completion_code
from ocspaths import telemetry_log_path
import controls.manage_rack_manager
import controls.manage_ocspower
import controls.manage_fwversion
import controls.manage_network
import controls.manage_user
import controls.bladeinfo_lib
import controls.bladelog_lib
import controls.bladelan_lib
import controls.bladepowerstate_lib
import controls.bladetpmphypresence_lib
import controls.bladenextboot_lib
import controls.bladebios_lib
import controls.manage_powerport
import controls.manage_powermeter
import controls.manage_fpga
import models.switch_manager
import controls.server_health

def execute_get_request_queries (query_list, init_values = dict ()):
    """
    Handler for all get requests to query the system for necessary information.
    
    :param query_list: A list of functions to be called that will provide the information required
    for the request.  Each function is a pair that contains the function to call and dictionary of
    arguments.
    :param init_values: The initial set of response information.
    
    :return A dictionary containing the information for generating the response object.
    """
    
    result = init_values.copy ()
    for query in query_list:
        try:
            query_data = query[0] (**query[1])
            view_helper.append_response_information (result, query_data)
            
        except Exception as error:
            view_helper.append_response_information (
                result, set_failure_dict (str (error), completion_code.failure))
    
    return view_helper.replace_key_spaces (result)

def get_all_power_control_status (port_type, count):
    """
    Get the status for all power control ports of a single type.
    
    :param port_type: The port type to query.
    :param count: The number of ports.
    
    :return A dictionary with the operation result.
    """
    
    status = [dict () for _ in range (0, count)]
    result = {}
    if (port_type == "relay"):
        for i in range (0, count):
            state = controls.manage_powerport.powerport_get_port_status (i + 1, port_type)
            if (state[completion_code.cc_key] == completion_code.success):
                status[i].update (state)
                if ("Relay" in status[i]):
                    status[i]["Relay"] = enums.PowerState (status[i]["Relay"], convert = True)
                else:
                    view_helper.append_response_information (result, state)
    else:
        start = 24 if (port_type == "rack") else 0
        end = 24 + count if (port_type == "rack") else count
        
        present = controls.manage_powerport.powerport_get_all_port_presence (raw = True,
            ports = range (start, end))
        if (present[completion_code.cc_key] == completion_code.success):
            for i in range (0, count):
                status[i]["Port Presence"] = enums.Boolean (present[i + 1], convert = True)
        else:
            view_helper.append_response_information (result, present)
            
        state = controls.manage_powerport.powerport_get_all_port_status (raw = True)
        if (state[completion_code.cc_key] == completion_code.success):
            for i in range (0, count):
                status[i]["Port State"] = enums.PowerState (state[i + 1], convert = True)
                
            if (port_type == "rack"):
                for i, j in enumerate (range (count + 1, (count * 2) + 1)):
                    status[i]["Boot Strap"] = enums.BootStrapping (state[j], convert = True)
        else:
            view_helper.append_response_information (result, state)
            
    result[port_type + "_ports"] = status
    return result

def parse_sensor_list (sensors, convert_reading, convert_number, sensor_type):
    """
    Parse the dictionary list of sensor data and convert it into an array used by the REST template.
    
    :param sensors: The dictionary list of sensor data to parse.  As the sensor data is parsed, the
    information will be removed from this dictionary.
    :param convert_reading: A flag indicating if the sensor reading should be converted to a numeber
    or if the raw string should be retained.
    :param convert_number: A flag indicating if the sensor number string should be converted to an
    integer or if the raw string should be retained.
    :param sensor_type: The type of sensor information being parsed.
    
    :return An array containing the parsed sensor data.
    """
    
    status_key = sensor_type + "_Status"
    number_key = sensor_type + "_Number"
    reading_key = sensor_type + "_Reading"
    
    parsed = [None] * len (sensors)
    for i, sensor in sensors.items ():
        try:
            idx = int (i) - 1
            status = sensor.pop (status_key, None)
            if (status and (status != "ns")):
                sensor["Health"] = enums.Health (status, convert = True)
            
            if (convert_number and (number_key in sensor)):
                sensor[number_key] = int (sensor[number_key][:-1], 16)
                
            if (reading_key in sensor):
                reading = sensor[reading_key]
                if (reading == "Disabled"):
                    sensor["State"] = enums.State ("Disabled")
                    del sensor[reading_key]
                else:
                    sensor["State"] = enums.State ("Enabled")
                    if ((not reading) or (reading == "No Reading")):
                        del sensor[reading_key]
                    elif (convert_reading):
                        reading = parameters.extract_number (reading)
                        if (reading):
                            sensor[reading_key] = reading
                        else:
                            del sensor[reading_key]
            
            parsed[idx] = sensor
            del sensors[i]
            
        except ValueError:
            pass
            
    return filter (None, parsed)

def auth_get (check):
    """
    Provide an authentication function decorator that will conditionally authenticate depending on
    whether the function is being called directly to handle a request or from another internal
    handler.
    """
    
    def decorator (func):
        def wrapper (*args, **kwargs):
            if (request.method == "GET"):
                auth_decorator = auth_basic (check)
                auth_wrapper = auth_decorator (func)
                return auth_wrapper (*args, **kwargs)
            else:
                return func (*args, **kwargs)
                
        return wrapper
    
    return decorator
    
#################
# Redfish schemas
#################
def get_redfish_metadata ():
    return view_helper.return_static_file_resource ("metadata")

def get_redfish_schema (schema):
    path = resources.SCHEMA_ROOT + schema
    path, file_name = os.path.split (path)
    return static_file (file_name, path)

###################
# Top-Level Redfish
###################
@auth_get (authentication.validate_user)
def get_redfish_version ():
    return view_helper.return_redfish_resource ("version")

@auth_get (authentication.validate_user)
def get_service_root ():
    return view_helper.return_redfish_resource ("service_root")

@auth_get (authentication.validate_user)
def get_systems_root ():
    return view_helper.return_redfish_resource ("systems_root")

@auth_get (authentication.validate_user)
def get_chassis_root ():
    return view_helper.return_redfish_resource ("chassis_root")

@auth_get (authentication.validate_user)
def get_managers_root ():
    return view_helper.return_redfish_resource ("managers_root")

###################
# System components
###################
@auth_get (authentication.validate_user)
def get_system (system, patch = dict ()):
    system = int (system)
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_blade_state, device_id = system)
    
    query = [
        (controls.bladeinfo_lib.system_info_call, {"bladeId" : system}),
        (controls.bladepowerstate_lib.get_server_default_powerstate, {"serverid" : system}),
        (controls.bladetpmphypresence_lib.get_tpm_physical_presence, {"serverid" : system}),
        (controls.bladenextboot_lib.get_nextboot, {"serverid" : system})
    ]
    
    result = view_helper.flatten_nested_objects (
        execute_get_request_queries (query, {"ID" : system}))
    
    for health in ["Server_Status_HealthRollUp", "Server_Status_Health",
        "Server_ProcessorSummary_Status_HealthRollUp", "Server_ProcessorSummary_Status_Health",
        "Server_MemorySummary_Status_HealthRollUp", "Server_MemorySummary_Status_Health"]:
        if (health in result):
            result[health] = enums.Health (result[health], convert = True)
            
    for state in ["Server_Status_State", "Server_ProcessorSummary_Status_State",
        "Server_MemorySummary_Status_State"]:
        if (state in result):
            result[state] = enums.State (result[state], convert = True)
            
    for state in ["Sever_PowerState", "Default_Power_State"]:
        if (state in result):
            result[state] = enums.PowerState (result[state], convert = True)
    
    if ("BootSourceOverrideTarget" in result):
        result["BootSourceOverrideTarget"] = enums.BootSourceOverrideTarget (
            result["BootSourceOverrideTarget"], convert = True)
    if ("BootSourceOverrideMode" in result):
        result["bootSourceOverrideMode"] = enums.BootSourceOverrideMode (
            result["BootSourceOverrideMode"], convert = True)
    if ("PhysicalPresence" in result):
        result["PhysicalPresence"] = enums.Boolean (result["PhysicalPresence"], convert = True)
        
    if (result.get ("BootSourceOverrideTarget", "") == enums.BootSourceOverrideTarget.NONE):
        result["BootSourceOverrideEnabled"] = enums.BootSourceOverrideEnabled (
            enums.BootSourceOverrideEnabled.DISABLED)
    else:
        if ("BootSourceOverrideEnabled" in result):
            result["BootSourceOverrideEnabled"] = enums.BootSourceOverrideEnabled (
                result["BootSourceOverrideEnabled"], convert = True)
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("system", values = result)

@auth_get (authentication.validate_user)
def get_system_bios_config (system, patch = dict ()):
    system = int (system)
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_blade_state, device_id = system)
    
    query = [
        (controls.bladebios_lib.get_server_bios_config, {"serverid" : system})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system})
    
    configs = []
    if ("AvailableConfigName" in result):
        configs.append ({"Config_Name" : result["AvailableConfigName"]})
    else:
        config_list = result.get ("AvailableConfigurations", {})
        if (config_list):
            i = 1
            while i in config_list:
                configs.append (config_list[i])
                i += 1
    result["AvailableConfigs"] = configs
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("system_bios_cfg", values = result)

@auth_get (authentication.validate_user)
def get_system_bios_code (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.bladebios_lib.get_server_bios_config, {"serverid" : system})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system})
    
    if ("Bios_Code" in result):
        if (isinstance (result["Bios_Code"], list)):
            result["Bios_Code"] = result["Bios_Code"][0]
             
    return view_helper.return_redfish_resource ("system_bios_code", values = result)

@auth_get (authentication.validate_user)
def get_system_fpga (system, patch = dict ()):
    system = int (system)
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_blade_state, device_id = system)
    
    result = controls.manage_fpga.get_fpga_i2c_version (system)
    if ((not patch) and
        (result.get (completion_code.cc_key, completion_code.failure) != completion_code.success)):
        view_helper.raise_status_response (500, view_helper.create_response_with_status (result))
        
    query = [
        (controls.manage_fpga.get_fpga_bypass_mode, {"serverid" : system}),
        (controls.manage_fpga.get_fpga_health, {"serverid" : system}),
        (controls.manage_fpga.get_fpga_assetinfo, {"serverid" : system}),
        (controls.manage_fpga.get_fpga_temp, {"serverid" : system})
    ]
    
    result["ID"] = system
    result = view_helper.remove_key_leading_number(execute_get_request_queries (query, result))
    
    for link in ["PCIe_HIP_0_Up", "PCIe_HIP_1_Up", "_40G_Link_0_Up", "_40G_Link_1_Up"]:
        if (link in result):
            result[link] = enums.LinkState (result[link], convert = True)
            
    for act in ["_40G_Link_0_Tx_Activity", "_40G_Link_1_Tx_Activity", "_40G_Link_0_Rx_Activity",
        "_40G_Link_1_Rx_Activity"]:
        if (act in result):
            result[act] = enums.Boolean (result[act], convert = True)
            
    if ("Bypass_Mode" in result):
        result["Bypass_Mode"] = enums.BypassMode (result["Bypass_Mode"], convert = True)
    if ("User_Logic_Network" in result):
        result["User_Logic_Network"] = enums.UserLogic (result["User_Logic_Network"],
            convert = True)

    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("system_fpga", values = result)

@auth_get (authentication.validate_user)
def get_system_chassis (system, patch = dict ()):
    system = int (system)
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_blade_state, device_id = system)
    
    query = [
        (controls.bladeinfo_lib.system_info_call, {"bladeId" : system})
    ]
    
    result = view_helper.flatten_nested_objects (
        execute_get_request_queries (query, {"ID" : system}))
    
    if ("Server_IndicatorLED" in result):
        result["Server_IndicatorLED"] = str (
            enums.IndicatorLED (result["Server_IndicatorLED"], convert = True))
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("system_chassis", values = result)

@auth_get (authentication.validate_user)
def get_system_power (system, patch = dict ()):
    system = int (system)
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_blade_state, device_id = system)
    
    query = [
        (controls.manage_ocspower.get_server_power_limit, {"serverid" : system}),
        (controls.manage_ocspower.get_server_power_reading, {"serverid" : system}),
        (controls.manage_ocspower.get_server_default_power_limit, {"serverid" : system}),
        (controls.manage_ocspower.get_server_psu_alert, {"serverid" : system}),
        (controls.manage_ocspower.get_server_psu_status, {"serverid" : system}),
        (controls.manage_ocspower.get_server_psu_fw_version, {"serverid" : system}),
        (controls.manage_ocspower.get_server_psu_bootloader_version, {"serverid" : system})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system})
    
    for key in ["StaticLimit", "PowerReadingWatts", "MinPowerReadingWatts", "MaxPowerReadingWatts",
        "AvgPowerReadingWatts", "SamplingPeriodSeconds", "PowerLimit", "ThrottleDuration", "LimitDelay"]:
        if (key in result):
            result[key] = parameters.remove_non_numeric (str(result[key]))
    
    for key in ["Alert_Enabled", "AutoProchot", "BladeProchot", "Balancing", "External_Power",
        "Pre_charge_Circuit", "Discharge", "Charge", "Charging", "Discharging", "Initialized"]:
        if (key in result):
            result[key] = enums.Boolean (result[key], convert = True)
            
    for key in ["Pin", "Vin", "Pout"]:
        if (key in result):
            result[key] = result[key][:-1]
    
    if ("StaticState" in result):
        result["StaticState"] = enums.State (result["StaticState"], convert = True)
    if ("SamplingPeriodSeconds" in result):
        result["SamplingPeriodSeconds"] = int (result["SamplingPeriodSeconds"]) / 60
    if ("AlertAction" in result):
        result["AlertAction"] = enums.AlertAction (result["AlertAction"], convert = True)
    if ("Faults" in result):
        if (not result["Faults"]):
            result["Health"] = "OK"
        else:
            result["Health"] = "Warning"

    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("system_power", values = result)

@auth_get (authentication.validate_user)
def get_system_power_phase (system, phase):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.manage_ocspower.get_server_psu_status, {"serverid" : system,
            "phase" : int (phase) - 1})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system, "Phase" : phase})
    
    for key in ["Pin", "Vin", "Pout"]:
        if (key in result):
            result[key] = result[key][:-1]
            
    if ("Faults" in result):
        if (not result["Faults"]):
            result["Health"] = "OK"
        else:
            result["Health"] = "Warning"
    
    return view_helper.return_redfish_resource ("system_pwr_phase", values = result)

@auth_get (authentication.validate_user)
def get_system_thermal (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query_temp = [
        (controls.server_health.show_temperature_health, {"serverid" : system})
    ]
    query_fan = [
        (controls.server_health.show_fan_health, {"serverid" : system})
    ]
    
    result_temp = execute_get_request_queries (query_temp)
    result_fan = execute_get_request_queries (query_fan)
    
    temps = parse_sensor_list (sensors = result_temp, convert_reading = True, convert_number = True,
        sensor_type = "Sensor")
    fans = parse_sensor_list (sensors = result_fan, convert_reading = True, convert_number = False,
        sensor_type = "Fan")
    
    result = {}
    view_helper.append_response_information (result, result_temp)
    view_helper.append_response_information (result, result_fan)
    
    if (temps):
        result["temps"] = temps
    if (fans):
        result["fans"] = fans
    result["ID"] = system
    
    return view_helper.return_redfish_resource ("system_thermal", values = result)

@auth_get (authentication.validate_user)
def get_system_sensors (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.server_health.show_sensor_health, {"serverid" : system})
    ]
    
    result = execute_get_request_queries (query)
    sensors = parse_sensor_list (sensors = result, convert_reading = False, convert_number = False,
        sensor_type = "Sensor")
    
    if (sensors):
        result["sensors"] = sensors
    result["ID"] = system
    
    return view_helper.return_redfish_resource ("system_sensors", values = result)

@auth_get (authentication.validate_user)
def get_system_manager (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.bladeinfo_lib.system_info_call, {"bladeId": system})
    ]
    
    result = view_helper.flatten_nested_objects (
        execute_get_request_queries (query, {"ID" : system}))
    
    if (view_helper.has_completion_errors (result)):
        result["Health"] = "Warning"
    else:
        result["Health"] = "OK"
        
    return view_helper.return_redfish_resource ("system_manager", values = result)

@auth_get (authentication.validate_user)
def get_system_ethernets (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    result = {"ID" : system}
    return view_helper.return_redfish_resource ("system_ethernets", values = result)

@auth_get (authentication.validate_user)
def get_system_ethernet (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.bladelan_lib.get_server_ethernetinterface, {"serverid": int(system)})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system})
    
    if ("AddressOrigin" in result):
        result["AddressOrigin"] = enums.AddressOrigin (result["AddressOrigin"], convert = True)
        
    return view_helper.return_redfish_resource ("system_ethernet", values = result)

@auth_get (authentication.validate_user)
def get_system_log_services (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    result = {"ID" : system}
    return view_helper.return_redfish_resource ("system_log_service", values = result)

@auth_get (authentication.validate_user)
def get_system_log (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    result = {"ID" : system}
    return view_helper.return_redfish_resource ("system_log", values = result)

@auth_get (authentication.validate_user)
def get_system_log_entries (system):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.bladelog_lib.read_server_log, {"serverid": system, "raw_output": False})
    ]
    
    result = execute_get_request_queries (query)
    result["EntryID"] = system
    
    return view_helper.return_redfish_resource ("system_log_entries", values = result)

@auth_get (authentication.validate_user)
def get_system_log_entry (system, entry):
    system = int (system)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_blade_state,
        device_id = system)
    
    query = [
        (controls.bladelog_lib.read_server_log_entry, {"serverid": system, "entryid": int(entry)})
    ]
    
    result = execute_get_request_queries (query, {"ID" : system, "EntryID" : entry})
        
    if "members" in result:
        if not result["members"]:
            raise HTTPError (status = 404)
        
    return view_helper.return_redfish_resource ("system_log_entry", values = result)

#########################
# Rack Manager components
#########################
@auth_get (authentication.validate_user)
def get_rack_manager_chassis (patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.get_rack_manager_attention_led_status, {}),
        (controls.manage_rack_manager.read_fru, {"boardtype" : "rm_mb"})
    ]
    
    result = execute_get_request_queries (query)
        
    if ("Manager_LED_Status" in result):
        result["Manager_LED_Status"] = str (enums.IndicatorLED (
            result["Manager_LED_Status"], convert = True))
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("rack_manager_chassis", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_power ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_ocspower.get_rack_manager_power_reading, {}),
        (controls.manage_ocspower.get_rack_manager_input_voltage, {}),
        (controls.manage_ocspower.get_rack_manager_hsc_status, {}),
        (controls.manage_ocspower.get_rack_manager_psu_status, {})
    ]
    result = execute_get_request_queries (query)
    
    if ("HSC_Status" in result):
        if (result["HSC_Status"] == "Healthy"):
            result["HSC_Status"] = ""
            result["Health"] = enums.Health ("OK")
        else:
            result["Health"] = enums.Health ("Warning")
    
    return view_helper.return_redfish_resource ("rack_manager_power", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_thermal ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.get_sensor_objects, {})
    ]
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("rack_manager_thermal", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager (patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.show_rack_manager_hostname, {}),
        (controls.manage_fwversion.get_ocsfwversion, {}),
        (controls.manage_rack_manager.manager_tftp_server_status, {}),
        (controls.manage_rack_manager.manager_nfs_server_status, {}),
        (controls.manage_rack_manager.get_rack_manager_ntp_status, {}),
        (controls.manage_rack_manager.get_rack_manager_itp_status, {}),
        (controls.manage_rack_manager.get_rack_manager_ntp_server, {}),
        (controls.manage_rack_manager.get_manager_throttle_local_bypass, {}),
        (controls.manage_rack_manager.get_manager_throttle_output_enable, {}),
        (controls.manage_rack_manager.show_rack_manager_time, {"edm" : True}),
        (controls.manage_rack_manager.get_rm_uptime, {})
    ]
    if (pre_check.get_mode () == rm_mode_enum.rowmanager):
        query.append ((controls.manage_rack_manager.get_row_throttle_bypass, {}))
        query.append ((controls.manage_rack_manager.get_row_throttle_output_enable, {}))
    
    result = execute_get_request_queries (query)
    
    for key in ["TFTPStatus", "NFSStatus", "NTPState", "ITPState"]:
        if (key in result):
            result[key] = enums.ServiceStatus (result[key], convert = True)
        
    for key in ["TFTPService", "NFSService", "NTPService", "ITPService", "Local_Bypass",
        "Row_Bypass", "Local_Enable", "Row_Enable"]:
        if (key in result):
            result[key] = enums.Boolean (result[key], convert = True)
            
    view_helper.update_and_replace_status_information (result, patch)
        
    return view_helper.return_redfish_resource ("rack_manager", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_ethernets ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_network.display_cli_interfaces, {})
    ]
    
    result = execute_get_request_queries (query)
        
    return view_helper.return_redfish_resource ("rack_manager_ethernets", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_ethernet (eth, patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_network.get_network_mac_address, {"if_name" : eth}),
        (controls.manage_network.get_network_ip_address, {"if_name" : eth}),
        (controls.manage_network.get_network_subnetmask, {"if_name" : eth}),
        (controls.manage_network.get_network_ip_address_origin, {"if_name" : eth}),
        (controls.manage_network.get_network_status, {"if_name" : eth})
    ]
    if (eth == "eth0"):
        query.append ((controls.manage_network.get_network_gateway, {}))
    else:
        query.append ((controls.manage_network.get_management_network, {}))
    
    result = execute_get_request_queries (query)
        
    if ("InterfaceStatus" in result):
        result["InterfaceState"] = enums.State (result["InterfaceStatus"], convert = True)
        result["InterfaceStatus"] = enums.Boolean (result["InterfaceStatus"], convert = True)
        
    if ("AddressOrigin" in result):
        result["AddressOrigin"] = enums.AddressOrigin (result["AddressOrigin"], convert = True)
        
    if ("Management_Network" in result):
        result["Management_Network"] = result["Management_Network"].netmask
        
    for key in ["IPAddress", "SubnetMask", "Gateway"]:
        if ((key in result) and (not result[key])):
            del result[key]
    
    result["Intf"] = eth
    result["Description"] = ("Datacenter" if (eth == "eth0") else "Management") + " Network Connection"
    result["InterfaceHealth"] = enums.Health ("OK")

    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("rack_manager_ethernet", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_log_services ():
    return view_helper.return_redfish_resource ("rack_manager_log_service")

@auth_get (authentication.validate_user)
def get_rack_manager_log ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.show_rack_manager_log_status, {})
    ]
    
    result = execute_get_request_queries (query)
    
    if ("TelemetryDaemonStatus" in result):
        result["TelemetryDaemonStatus"] = enums.State (result["TelemetryDaemonStatus"],
            convert = True)
            
    return view_helper.return_redfish_resource ("rack_manager_log", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_log_entries ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)

    query = [
        (controls.manage_rack_manager.get_rack_manager_log, 
            {"filename": telemetry_log_path, "raw": False})
    ]
    
    result = execute_get_request_queries (query)
    
    if (("members" in result) and (completion_code.cc_key in result)):
        for value in result["members"].itervalues ():
            value["Severity"] = enums.Health (value["Severity"], convert = True)

    return view_helper.return_redfish_resource ("rack_manager_log_entries", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_log_entry (entry):   
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.get_rack_manager_log,
            {"filename": telemetry_log_path, "raw": False, "startid": entry,
                "endid": entry})
    ]
    
    result = execute_get_request_queries (query)
    result["Entry"] = entry 
        
    if (("members" in result) and (completion_code.cc_key in result)):
        if not result["members"] and result[completion_code.cc_key] == completion_code.success:
            raise HTTPError (status = 404)
        else:
            for value in result["members"].itervalues ():
                value["Severity"] = enums.Health (value["Severity"], convert = True)
    
    return view_helper.return_redfish_resource ("rack_manager_log_entry", values = result)

@auth_get (authentication.validate_user)
def get_rack_manager_tftp ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.manager_tftp_server_listfiles, {})
    ]
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("rack_manager_tftp", values = result)

#################
# PMDU components
#################
@auth_get (authentication.validate_user)
def get_pmdu_chassis ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    if ((pre_check.get_mode () == rm_mode_enum.rowmanager) or
        (pre_check.get_mode () == rm_mode_enum.standalone_rackmanager)):
        board = "row_pib"
    else:
        board = "rm_pib"
        
    query = [
        (controls.manage_rack_manager.read_fru, {"boardtype" : board})
    ]
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("pmdu_chassis", values = result)
        
@auth_get (authentication.validate_user)
def get_pmdu_power_control ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    if (pre_check.get_mode () == rm_mode_enum.rowmanager):
        query = [
            (get_all_power_control_status, {"port_type" : "rack", "count" : 24})
        ]
    elif (pre_check.get_mode () == rm_mode_enum.standalone_rackmanager):
        query = [
            (get_all_power_control_status, {"port_type" : "pdu", "count" : 24})
        ]
    else:
        query = [
            (get_all_power_control_status, {"port_type" : "pdu", "count" : 48}),
            (get_all_power_control_status, {"port_type" : "relay", "count" : 4})
        ]
        
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("pmdu_power_control", values = result)

@auth_get (authentication.validate_user)
def get_pmdu_power_meter (patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_powermeter.get_rack_power_limit_policy, {}),
        (controls.manage_powermeter.get_rack_power_throttle_status, {}),
        (controls.manage_powermeter.get_rack_power_reading, {}),
        (controls.manage_powermeter.get_rack_pru_fw_version, {})
    ]
    result = execute_get_request_queries (query)
    
    if ("Feed1PowerStatus" in result):
        if (result["Feed1PowerStatus"] == "Healthy"):
            result["Feed1PowerStatus"] = ""
    if ("Feed2PowerStatus" in result):
        if (result["Feed2PowerStatus"] == "Healthy"):
            result["Feed2PowerStatus"] = ""
    if ("IsDcThrottleEnabled" in result):
        result["IsDcThrottleEnabled"] = enums.Boolean (result["IsDcThrottleEnabled"],
            convert = True)
    if ("IsDcThrottleActive" in result):
        result["IsDcThrottleActive"] = enums.Boolean (result["IsDcThrottleActive"], convert = True)
    if ("IsAlertEnabled" in result):
        result["IsAlertEnabled"] = enums.Boolean (result["IsAlertEnabled"], convert = True)
    if ("IsAlertActive" in result):
        result["IsAlertActive"] = enums.Boolean (result["IsAlertActive"], convert = True)
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("pmdu_power_meter", values = result)

@auth_get (authentication.validate_user)
def get_pdu_control (port, patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    port = int (port)
    query = [
        (controls.manage_powerport.powerport_get_port_presence, {"port_type" : "pdu",
            "port_id" : port}),
        (controls.manage_powerport.powerport_get_port_status, {"port_type" : "pdu",
            "port_id" : port})
    ]
    result = execute_get_request_queries (query, init_values = {"ID" : port})
    
    if ("Port_Presence" in result):
        result["Port_Presence"] = enums.Boolean (result["Port_Presence"], convert = True)
    if ("Port_State" in result):
        result["Port_State"] = enums.PowerState (result["Port_State"], convert = True)
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("power_control_pdu", values = result)

@auth_get (authentication.validate_user)
def get_relay_control (relay, patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    relay = int (relay)
    query = [
        (controls.manage_powerport.powerport_get_port_status, {"port_type" : "relay",
            "port_id" : relay})
    ]
    result = execute_get_request_queries (query, init_values = {"ID" : relay})
    
    if ("Relay" in result):
        result["Relay"] = enums.PowerState (result["Relay"], convert = True)
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("power_control_relay", values = result)

@auth_get (authentication.validate_user)
def get_row_manager_power_control (rack, patch = dict ()):
    if (not patch):
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
        
    rack = int (rack)
    query = [
        (controls.manage_powerport.powerport_get_row_port_presence, {"port_id" : rack}),
        (controls.manage_powerport.powerport_get_port_status, {"port_id" : rack,
            "port_type" : "pdu"}),
        (controls.manage_powerport.powerport_get_row_boot_strap, {"port_id" : rack})
    ]
    result = execute_get_request_queries (query, init_values = {"ID" : rack})
    
    if ("Port_Presence" in result):
        result["Port_Presence"] = enums.Boolean (result["Port_Presence"], convert = True)
    if ("Port_State" in result):
        result["Port_State"] = enums.PowerState (result["Port_State"], convert = True)
    if ("Boot_Strap" in result):
        result["Boot_Strap"] = enums.BootStrapping (result["Boot_Strap"], convert = True)
        
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("power_control_manager", values = result)

##############################
# Management switch components
##############################
@auth_get (authentication.validate_user)
def get_switch_chassis ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (models.switch_manager.getswitch (load_config.switch_ip, "").getswitch_info, {})
    ]
    
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("switch_chassis", values = result)

@auth_get (authentication.validate_user)
def get_switch_power ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (models.switch_manager.getswitch (load_config.switch_ip, "").getswitch_info, {})
    ]
    
    result = execute_get_request_queries (query)
    
    if ("MainPowerState" in result):
        result["MainPowerState"] = str (enums.Health (
            str(result["MainPowerState"]), convert = True))

    if ("RedundantPowerState" in result):    
        result["RedundantPowerState"] = str (enums.Health (
            str(result["RedundantPowerState"]), convert = True))
        
    return view_helper.return_redfish_resource ("switch_power", values = result)

@auth_get (authentication.validate_user)
def get_switch_thermal ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (models.switch_manager.getswitch (load_config.switch_ip, "").getswitch_info, {})
    ]
    
    result = execute_get_request_queries (query)
    
    if ("TemperatureSensorState" in result):
            result["TemperatureSensorState"] = str (enums.Health (
                str(result["TemperatureSensorState"]), convert = True))
            
    return view_helper.return_redfish_resource ("switch_thermal", values = result)

@auth_get (authentication.validate_user)
def get_switch_port (port):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (models.switch_manager.getswitch (load_config.switch_ip, "").getswitchport_info,
            {"port_id": port})
    ]
    
    result = execute_get_request_queries (query)
    result["ID"] = port
    
    return view_helper.return_redfish_resource ("switch_port", values = result)

#################
# Rack components
#################
@auth_get (authentication.validate_user)
def get_rack_chassis ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)

    query = [
        (controls.manage_rack_manager.read_fru, {"boardtype" : "rm_mb"})
    ]
    
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("rack_chassis", values = result)

@auth_get (authentication.validate_user)
def get_rack_inventory ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.bladeinfo_lib.manager_inventory, {"mode" : "pmdu"})
    ]
    
    result = execute_get_request_queries (query)
    
    parsed = [None] * len (result)
    if (result[completion_code.cc_key] == completion_code.success):
        for i, item in result.items ():
            try:
                idx = int (i) - 1
                if ("Port_Present" in item):
                    item["Port_Present"] = enums.Boolean (item["Port_Present"], convert = True)
                    
                if ("Port_State" in item):
                    item["Port_State"] = enums.PowerState (item["Port_State"], convert = True)
                            
                parsed[idx] = item
                del result[i]
                
            except ValueError:
                pass
            
    parsed = filter (None, parsed)
    if (parsed):
        result["list"] = parsed
        
    return view_helper.return_redfish_resource ("rack_inventory", values = result)

############################
# Account service components
############################
@auth_get (authentication.validate_user)
def get_account_service ():
    return view_helper.return_redfish_resource ("account_service")

@auth_get (authentication.validate_user)
def get_accounts ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_user.user_list_all, {})
    ]
    
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("accounts", values = result)

@auth_get (authentication.validate_user)
def get_account (account, patch = dict()):
    if (not patch):
        parameters.verify_account_name (account)
        view_helper.run_pre_check (pre_check.pre_check_function_call,
            command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_user.get_groupname_from_username, {"username": account})
    ]
    
    result = execute_get_request_queries (query, {"Account" : account})
    
    if (result.get ("groupname", "") == "unknown user"):
        raise HTTPError (status = 404)
    
    view_helper.update_and_replace_status_information (result, patch)
    return view_helper.return_redfish_resource ("account", values = result)

@auth_get (authentication.validate_user)
def get_roles ():
    return view_helper.return_redfish_resource ("roles")

@auth_get (authentication.validate_user)
def get_ocs_admin ():
    return view_helper.return_redfish_resource ("admin")

@auth_get (authentication.validate_user)
def get_ocs_operator ():
    return view_helper.return_redfish_resource ("operator")

@auth_get (authentication.validate_user)
def get_ocs_user ():
    return view_helper.return_redfish_resource ("user")

############################
# Session service components
############################
@auth_get (authentication.validate_user)
def get_session_service ():
    return view_helper.return_redfish_resource ("session_service")

@auth_get (authentication.validate_user)
def get_sessions ():
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)
    
    query = [
        (controls.manage_rack_manager.manager_session_list, {})
    ]
    
    result = execute_get_request_queries (query)
    
    return view_helper.return_redfish_resource ("sessions", values = result)

@auth_get (authentication.validate_user)
def get_session (session):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.get_rm_state)

    query = [
        (controls.manage_rack_manager.manager_session, {"sessionid": int(session)})
    ]
    
    result = execute_get_request_queries (query, {"ID" : session})

    for error in result.get (view_helper.response_status_key, []):
        if ("Invalid session id" in error.get (completion_code.desc, "")):
            raise HTTPError (status = 404)
            
    return view_helper.return_redfish_resource ("session", values = result)
