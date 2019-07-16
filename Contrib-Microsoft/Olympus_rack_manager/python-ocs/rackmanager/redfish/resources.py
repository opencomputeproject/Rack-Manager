# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import get_handler
import patch_handler
import post_handler
import delete_handler
import route_handler
from ocsrest import pre_check
from pre_settings import rm_mode_enum

TEMPLATE_ROOT = os.path.realpath ("redfish/templates") + "/"
SCHEMA_ROOT = os.path.realpath ("redfish/schemas") + "/"

class redfish_resource:
    """
    Defines a single resource accessible via the REST interface.
    """
    
    def __init__ (self, common = None, pmdu = None, row = None, stand_alone = None,
        get = None, post = None, patch = None, delete = None, default = None):
        """
        Initialize a resource to be provided by the REST interface.  The resource is initialized
        with the URI and template path for each configuration and the methods that are supported
        by the resource.
        
        :param common: A tuple of URI and template path for a resource that is common to all
        configurations.  If not specified, the specific configuration settings will be applied.
        :param pmdu: A tuple of URI and template path for the resource when configured as a rack
        manager with a PMDU.  If not specified, the resource will not be available in the PMDU rack
        manager configuration unless the information is provided as a common resource.
        :param row: A tuple of URI and template path for the resource when configured as a row
        manager.  If not specified, the resource will not be available in the row manager
        configuration unless the information is provided as a common resource.
        :param stand_alone: A tuple of URI and template path for the resource when configured as a
        stand-alone rack manager.  If not specified, the resource will not be available in the
        stand-alone rack manager configuration unless the information is provided as a common
        resource.
        :param get: The handler for GET requests for the resource.  If not specified, GET requests
        on the resource will not be supported.
        :param post: The handler for POST requests for the resource.  If not specified, POST
        requests on the resource will not be supported.
        :param patch: The handler for PATCH requests for the resource.  If not specified, PATCH
        requests on the resource will not be supported.
        :param delete: The handler for DELETE requests for the resource.  If not specified, DELETE
        requests on the resource will not be supported.
        :param default: The default handler for any request not specifically routed.  If not
        specified, requests types not explicitly specified will return a 405 error.
        """
        
        self.common = common
        self.pmdu = pmdu
        self.row = row
        self.stand_alone = stand_alone
        self.get = get
        self.post = post
        self.patch = patch
        self.delete = delete
        self.default = default
        
    def register_resource (self, app, mode, name):
        """
        Register the resource with the REST handler.  If the resource is not valid for the given
        configuration, this call does nothing.
        
        :param app: The web server instance to register the resource with.
        :param mode: The manager configuration that should be registered.
        :param name: The internal name of the resource.
        """
        
        if (self.common):
            self.rest = self.common[0]
            self.template = TEMPLATE_ROOT + self.common[1]
        elif (self.pmdu and ((mode == rm_mode_enum.pmdu_rackmanager) or
            (mode == rm_mode_enum.tfb_dev_benchtop) or (mode == rm_mode_enum.unknown_rm_mode))):
            self.rest = self.pmdu[0]
            self.template = TEMPLATE_ROOT + self.pmdu[1]
        elif (self.row and (mode == rm_mode_enum.rowmanager)):
            self.rest = self.row[0]
            self.template = TEMPLATE_ROOT + self.row[1]
        elif (self.stand_alone and (mode == rm_mode_enum.standalone_rackmanager)):
            self.rest = self.stand_alone[0]
            self.template = TEMPLATE_ROOT + self.stand_alone[1]
        else:
            self.rest = None
            
        if (not self.rest):
            return
        
        (self.path, self.file) = os.path.split (self.template)
        if (isinstance (self.rest, basestring)):
            self.rest = [self.rest]
        
        for uri in self.rest:
            if (self.get):
                app.route (path = uri, method = "GET", callback = self.get,
                    name = "get_{0}".format (name))
            if (self.post):
                app.route (path = uri, method = "POST", callback = self.post,
                    name = "post_{0}".format (name))
            if (self.patch):
                app.route (path = uri, method = "PATCH", callback = self.patch,
                    name = "patch_{0}".format (name))
            if (self.delete):
                app.route (path = uri, method = "DELETE", callback = self.delete,
                    name =  "delete_{0}".format (name))
            if (self.default):
                app.route (path = uri, method = "ANY", callback = self.default, name = name)

REGEX_1_48 = "[1-3][0-9]|4[0-8]|[1-9]"
REGEX_1_24 = "1[0-9]|2[0-4]|[1-9]"

def id_filter (config):
    """
    A bottle router filter that matches valid identifier numbers.  Based on the config, it will
    match against 24 or 48 valid IDs.
    
    :param config: The number of IDs to filter against.  This defaults to 48 if not sepeified or if
    the range isn't supported.
    """
    
    valid = config or 48
    regex = REGEX_1_24 if (int (valid) == 24) else REGEX_1_48
    
    def to_python (match):
        return match
    
    def to_url (system):
        return system
    
    return regex, to_python, to_url

def system_id_filter (config):
    """
    A Bottle router filter that matches a system identifier against valid values.
    """
    
    return id_filter (pre_check.get_max_num_systems ())

def add_bottle_filters (app):
    """
    Add custom URL filters to the Bottle instance.
    
    :param app: The web server instance to add the filters to.
    """
    
    app.router.add_filter ("id", id_filter)
    app.router.add_filter ("sysid", system_id_filter)
    
def find_resource (name):
    """
    Find a resource instance.
    
    :param name: The name of the resource to find.
    
    :return The resource instance.
    """
    
    resource = None
    for group in (REDFISH_RESOURCES, REDFISH_SYSTEM_RESOURCES):
        resource = group.get (name, None)
        if (resource):
            break;
        
    if (not resource):
        raise KeyError ("{0} is not a valid resource name.".format (name))
    
    return resource

##
# The list of accesible resources from the REST interface.
##
REDFISH_RESOURCES = {
    #################
    # Redfish schemas
    #################
    "metadata" : redfish_resource (
        common = (
            "/redfish/v1/$metadata",
            "metadata.tpl"),
        get = get_handler.get_redfish_metadata),
    "schema" : redfish_resource (
        common = (
            "/schemas/<schema:path>",
            ""),
        get = get_handler.get_redfish_schema),
                     
    ###################
    # Top-Level Redfish
    ###################
    "version" : redfish_resource (
        common = (
            "/redfish",
            "Redfish.tpl"),
        get = get_handler.get_redfish_version),
    "service_root" : redfish_resource (
        common = (
            "/redfish/v1",
            "ServiceRoot.tpl"),
        get = get_handler.get_service_root),
    "systems_root" : redfish_resource (
        pmdu  = (
            "/redfish/v1/Systems",
            "Systems.tpl"),
        stand_alone  = (
            "/redfish/v1/Systems",
            "Systems.tpl"),
        get = get_handler.get_systems_root),
    "chassis_root" : redfish_resource (
        common = (
            "/redfish/v1/Chassis",
            "Chassis.tpl"),
        get = get_handler.get_chassis_root),
    "managers_root" : redfish_resource (
        common = (
            "/redfish/v1/Managers",
            "Managers.tpl"),
        get = get_handler.get_managers_root),
    
    ###################
    # System components
    ###################
    "system_router" : redfish_resource (
        pmdu = (
            [
                "/redfish/v1/System/<system:sysid>",
                "/redfish/v1/System/<system:sysid>/<path:path>"
            ],
            ""),
        stand_alone = (
            [
                "/redfish/v1/System/<system:sysid>",
                "/redfish/v1/System/<system:sysid>/<path:path>"
            ],
            ""),
        default = route_handler.route_system_request),
    "system_chassis_router" : redfish_resource (
        pmdu = (
            [
                "/redfish/v1/Chassis/System/<system:sysid>",
                "/redfish/v1/Chassis/System/<system:sysid>/<path:path>"
            ],
            ""),
        stand_alone = (
            [
                "/redfish/v1/Chassis/System/<system:sysid>",
                "/redfish/v1/Chassis/System/<system:sysid>/<path:path>"
            ],
            ""),
        default = route_handler.route_system_request),
    "system_manager_router" : redfish_resource (
        pmdu = (
            [
                "/redfish/v1/Managers/System/<system:sysid>",
                "/redfish/v1/Managers/System/<system:sysid>/<path:path>"
            ],
            ""),
        stand_alone = (
            [
                "/redfish/v1/Managers/System/<system:sysid>",
                "/redfish/v1/Managers/System/<system:sysid>/<path:path>"
            ],
            ""),
        default = route_handler.route_system_request),
    
    #########################
    # Rack Manager components
    #########################
    "rack_manager_chassis" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/RackManager",
            "RackManager/Chassis.tpl"),
        row = (
            "/redfish/v1/Chassis/RowManager",
            "RackManager/Chassis.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/RackManager",
            "RackManager/Chassis.tpl"),
        get = get_handler.get_rack_manager_chassis,
        patch = patch_handler.patch_rack_manager_chassis),
    "rack_manager_power" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/RackManager/Power",
            "RackManager/Power.tpl"),
        row = (
            "/redfish/v1/Chassis/RowManager/Power",
            "RackManager/Power.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/RackManager/Power",
            "RackManager/Power.tpl"),
        get = get_handler.get_rack_manager_power),
    "rack_manager_power_clear_faults" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/RackManager/Power/Actions/PowerSupply.ClearFaults",
            ""),
        row = (
            "/redfish/v1/Chassis/RowManager/Power/Actions/PowerSupply.ClearFaults",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/RackManager/Power/Actions/PowerSupply.ClearFaults",
            ""),
        post = post_handler.post_rack_manager_power_clear_faults),
    "rack_manager_thermal" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/RackManager/Thermal",
            "RackManager/Thermal.tpl"),
        row = (
            "/redfish/v1/Chassis/RowManager/Thermal",
            "RackManager/Thermal.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/RackManager/Thermal",
            "RackManager/Thermal.tpl"),
        get = get_handler.get_rack_manager_thermal),
    "rack_manager" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager",
            "RackManager/Manager.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager",
            "RackManager/Manager.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager",
            "RackManager/Manager.tpl"),
        get = get_handler.get_rack_manager,
        patch = patch_handler.patch_rack_manager),
    "rack_manager_fw_update" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/Actions/Manager.FirmwareUpdate",
            ""),
        row = (
            "/redfish/v1/Managers/RowManager/Actions/Manager.FirmwareUpdate",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/Actions/Manager.FirmwareUpdate",
            ""),
        post = post_handler.post_rack_manager_fw_update),
    "rack_manager_ethernets" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/EthernetInterfaces",
            "RackManager/EthernetInterfaces.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/EthernetInterfaces",
            "RackManager/EthernetInterfaces.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/EthernetInterfaces",
            "RackManager/EthernetInterfaces.tpl"),
        get = get_handler.get_rack_manager_ethernets),
    "rack_manager_ethernet" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/EthernetInterface/<eth:re:eth[0|1]>",
            "RackManager/EthernetInterface.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/EthernetInterface/<eth:re:eth[0|1]>",
            "RackManager/EthernetInterface.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/EthernetInterface/<eth:re:eth[0|1]>",
            "RackManager/EthernetInterface.tpl"),
        get = get_handler.get_rack_manager_ethernet,
        patch = patch_handler.patch_rack_manager_ethernet),
    "rack_manager_log_service" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/LogServices",
            "RackManager/LogServices.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/LogServices",
            "RackManager/LogServices.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/LogServices",
            "RackManager/LogServices.tpl"),
        get = get_handler.get_rack_manager_log_services),
    "rack_manager_log" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/LogServices/Log",
            "RackManager/Log.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/LogServices/Log",
            "RackManager/Log.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/LogServices/Log",
            "RackManager/Log.tpl"),
        get = get_handler.get_rack_manager_log),
    "rack_manager_clear_log" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Actions/LogService.ClearLog",
            ""),
        row = (
            "/redfish/v1/Managers/RowManager/LogServices/Log/Actions/LogService.ClearLog",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Actions/LogService.ClearLog",
            ""),
        post = post_handler.post_rack_manager_clear_log),
    "rack_manager_log_entries" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Entries",
            "RackManager/LogEntries.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/LogServices/Log/Entries",
            "RackManager/LogEntries.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Entries",
            "RackManager/LogEntries.tpl"),
        get = get_handler.get_rack_manager_log_entries),
    "rack_manager_log_entry" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Entry/<entry>",
            "RackManager/LogEntry.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/LogServices/Log/Entry/<entry>",
            "RackManager/LogEntry.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/LogServices/Log/Entry/<entry>",
            "RackManager/LogEntry.tpl"),
        get = get_handler.get_rack_manager_log_entry),
    "rack_manager_tftp" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/Tftp",
            "RackManager/Tftp.tpl"),
        row = (
            "/redfish/v1/Managers/RowManager/Tftp",
            "RackManager/Tftp.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/Tftp",
            "RackManager/Tftp.tpl"),
        get = get_handler.get_rack_manager_tftp),
    "rack_manager_tftp_get" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Get",
            ""),
        row = (
            "/redfish/v1/Managers/RowManager/Tftp/Actions/Tftp.Get",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Get",
            ""),
        post = post_handler.post_rack_manager_tftp_get),
    "rack_manager_tftp_put" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Put",
            ""),
        row = (
            "/redfish/v1/Managers/RowManager/Tftp/Actions/Tftp.Put",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Put",
            ""),
        post = post_handler.post_rack_manager_tftp_put),
    "rack_manager_tftp_delete" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Delete",
            ""),
        row = (
            "/redfish/v1/Managers/RowManager/Tftp/Actions/Tftp.Delete",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/RackManager/Tftp/Actions/Tftp.Delete",
            ""),
        post = post_handler.post_rack_manager_tftp_delete),
                    
    #################
    # PMDU components
    #################
    "pmdu_chassis" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU",
            "PMDU/Chassis.tpl"),
        row = (
            "/redfish/v1/Chassis/RMM",
            "PMDU/Chassis.tpl"),
        get = get_handler.get_pmdu_chassis),
    "pmdu_power_control" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerControl",
            "PMDU/PowerControl.tpl"),
        row = (
            "/redfish/v1/Chassis/RMM/PowerControl",
            "PMDU/RowControl.tpl"),
        get = get_handler.get_pmdu_power_control),
    "power_control_pdu" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerControl/PDU/<port:id:48>",
            "PMDU/PDU.tpl"),
        get = get_handler.get_pdu_control,
        patch = patch_handler.patch_pdu_control),
    "power_control_relay" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerControl/Relay/<relay:re:[1-4]>",
            "PMDU/Relay.tpl"),
        get = get_handler.get_relay_control,
        patch = patch_handler.patch_relay_control),
    "power_control_manager" : redfish_resource (
        row = (
            "/redfish/v1/Chassis/RMM/PowerControl/RackManager/<rack:re:[1-24]>",
            "PMDU/RackManager.tpl"),
        get = get_handler.get_row_manager_power_control,
        patch = patch_handler.patch_row_manager_power_control),
    "pmdu_power_meter" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerMeter",
            "PMDU/PowerMeter.tpl"),
        get = get_handler.get_pmdu_power_meter,
        patch = patch_handler.patch_pmdu_power_meter),
    "pmdu_power_meter_clear_max" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerMeter/Actions/PowerMeter.ClearMaxPower",
            ""),
        post = post_handler.post_pmdu_power_meter_clear_max_power),
    "pmdu_power_meter_clear_faults" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/PMDU/PowerMeter/Actions/PowerMeter.ClearFaults",
            ""),
        post = post_handler.post_pmdu_power_meter_clear_faults),
    
    ##############################
    # Management Switch components
    ##############################
    "switch_chassis" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch",
            "MgmtSwitch/Chassis.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch",
            "MgmtSwitch/Chassis.tpl"),
        get = get_handler.get_switch_chassis),
    "switch_reset" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Reset",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Reset",
            ""),
        post = post_handler.post_switch_reset),
    "switch_configure" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Configure",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Configure",
            ""),
        post = post_handler.post_switch_configure),
    "switch_fw_update" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.FirmwareUpdate",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.FirmwareUpdate",
            ""),
        post = post_handler.post_switch_fw_update),
    "switch_power" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Power",
            "MgmtSwitch/Power.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Power",
            "MgmtSwitch/Power.tpl"),
        get = get_handler.get_switch_power),
    "switch_thermal" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Thermal",
            "MgmtSwitch/Thermal.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Thermal",
            "MgmtSwitch/Thermal.tpl"),
        get = get_handler.get_switch_thermal),
    "switch_port" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/MgmtSwitch/Port/<port:id:48>",
            "MgmtSwitch/Port.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/MgmtSwitch/Port/<port:id:48>",
            "MgmtSwitch/Port.tpl"),
        get = get_handler.get_switch_port),
    
    #################
    # Rack components
    #################
    "rack_chassis" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/Rack",
            "Rack/Chassis.tpl"),
        get = get_handler.get_rack_chassis),
                     
    "rack_inventory" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/Rack/Inventory",
            "Rack/Inventory.tpl"),
        get = get_handler.get_rack_inventory),
    
    ############################
    # Account service components
    ############################
    "account_service" : redfish_resource (
        common = (
            "/redfish/v1/AccountService",
            "AccountService/AccountService.tpl"),
        get = get_handler.get_account_service),
    "accounts" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/ManagerAccounts",
            "AccountService/ManagerAccounts.tpl"),
        get = get_handler.get_accounts,
        post = post_handler.post_accounts),
    "account" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/ManagerAccount/<account>",
            "AccountService/ManagerAccount.tpl"),
        get = get_handler.get_account,
        patch = patch_handler.patch_account,
        delete = delete_handler.delete_account),
    "roles" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/Roles",
            "AccountService/Roles.tpl"),
        get = get_handler.get_roles),
    "admin" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/Role/admin",
            "AccountService/ocs_admin.tpl"),
        get = get_handler.get_ocs_admin),
    "operator" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/Role/operator",
            "AccountService/ocs_operator.tpl"),
        get = get_handler.get_ocs_operator),
    "user" : redfish_resource (
        common = (
            "/redfish/v1/AccountService/Role/user",
            "AccountService/ocs_user.tpl"),
        get = get_handler.get_ocs_user),
    
    ############################
    # Session service components
    ############################
    "session_service" : redfish_resource (
        common = (
            "/redfish/v1/SessionService",
            "SessionService/SessionService.tpl"),
        get = get_handler.get_session_service),
    "sessions" : redfish_resource (
        common = (
            "/redfish/v1/SessionService/Sessions",
            "SessionService/Sessions.tpl"),
        get = get_handler.get_sessions),
    "session" : redfish_resource (
        common = (
            "/redfish/v1/SessionService/Session/<session>",
            "SessionService/Session.tpl"),
        get = get_handler.get_session,
        delete = delete_handler.delete_session)
}

##
# The list of accessible resources for IPMI compute system accessible through the interface.
##
REDFISH_SYSTEM_RESOURCES = {
    "system" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>", 
            "Systems/System.tpl"),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>", 
            "Systems/System.tpl"),
        get = get_handler.get_system,
        patch = patch_handler.patch_system),
    "system_reset" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.Reset",
            ""),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.Reset",
            ""),
        post = post_handler.post_system_reset),
    "system_remotemedia_mount" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.RemoteMediaMount",
            ""),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.RemoteMediaMount",
            ""),
        post = post_handler.post_system_remotemedia_mount),
    "system_remotemedia_unmount" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.RemoteMediaUnmount",
            ""),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/Actions/ComputerSystem.RemoteMediaUnmount",
            ""),
        post = post_handler.post_system_remotemedia_unmount),        
    "system_bios_cfg" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/BiosConfig",
            "Systems/BiosConfig.tpl"),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/BiosConfig",
            "Systems/BiosConfig.tpl"),
        get = get_handler.get_system_bios_config,
        patch = patch_handler.patch_system_bios_config),
    "system_bios_code" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/BiosCode",
            "Systems/BiosCode.tpl"),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/BiosCode",
            "Systems/BiosCode.tpl"),
        get = get_handler.get_system_bios_code),
    "system_fpga" : redfish_resource (
        pmdu = (
            "/redfish/v1/System/<system:sysid>/FPGA",
            "Systems/FPGA.tpl"),
        stand_alone = (
            "/redfish/v1/System/<system:sysid>/FPGA",
            "Systems/FPGA.tpl"),
        get = get_handler.get_system_fpga,
        patch = patch_handler.patch_system_fpga),
    "system_chassis" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>", 
            "Systems/Chassis.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>", 
            "Systems/Chassis.tpl"),
        get = get_handler.get_system_chassis,
        patch = patch_handler.patch_system_chassis),
    "system_power" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power",
            "Systems/Power.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power",
            "Systems/Power.tpl"),
        get = get_handler.get_system_power,
        patch = patch_handler.patch_system_power),
    "system_pwr_limit_rearm" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.RearmTrigger",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.RearmTrigger",
            ""),
        post = post_handler.post_system_power_limit_rearm_trigger),
    "system_pwr_limit_activate" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.Activate",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.Activate",
            ""),
        post = post_handler.post_system_power_activate_limit),
    "system_pwr_limit_deactivate" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.Deactivate",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerLimit.Deactivate",
            ""),
        post = post_handler.post_system_power_deactivate_limit),
    "system_battery_test" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.BatteryTest",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.BatteryTest",
            ""),
        post = post_handler.post_system_battery_test),
    "system_power_clear_faults" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.ClearFaults",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.ClearFaults",
            ""),
        post = post_handler.post_system_power_clear_faults),
    "system_power_fw_update" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.FirmwareUpdate",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.FirmwareUpdate",
            ""),
        post = post_handler.post_system_power_fw_update),
    "system_power_fw_state" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.FirmwareUpdateState",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Actions/PowerSupply.FirmwareUpdateState",
            ""),
        post = post_handler.post_system_power_fw_update_state),
    "system_pwr_phase" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Phase<phase:re:[1-3]>",
            "Systems/Phase.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Phase<phase:re:[1-3]>",
            "Systems/Phase.tpl"),
        get = get_handler.get_system_power_phase),
    "system_pwr_phase_clear_faults" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Phase<phase:re:[1-3]>/Actions/PowerSupply.ClearFaults",
            ""),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Power/Phase<phase:re:[1-3]>/Actions/PowerSupply.ClearFaults",
            ""),
        post = post_handler.post_system_phase_clear_faults),
    "system_thermal" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Thermal",
            "Systems/Thermal.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Thermal",
            "Systems/Thermal.tpl"),
        get = get_handler.get_system_thermal),
    "system_sensors" : redfish_resource (
        pmdu = (
            "/redfish/v1/Chassis/System/<system:sysid>/Sensors",
            "Systems/Sensors.tpl"),
        stand_alone = (
            "/redfish/v1/Chassis/System/<system:sysid>/Sensors",
            "Systems/Sensors.tpl"),
        get = get_handler.get_system_sensors),
    "system_manager" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>",
            "Systems/Manager.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>",
            "Systems/Manager.tpl"),
        get = get_handler.get_system_manager),
    "system_ethernets" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/EthernetInterfaces",
            "Systems/EthernetInterfaces.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/EthernetInterfaces",
            "Systems/EthernetInterfaces.tpl"),
        get = get_handler.get_system_ethernets),
    "system_ethernet" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/EthernetInterface",
            "Systems/EthernetInterface.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/EthernetInterface",
            "Systems/EthernetInterface.tpl"),
        get = get_handler.get_system_ethernet),
    "system_log_service" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices",
            "Systems/LogServices.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices",
            "Systems/LogServices.tpl"),
        get = get_handler.get_system_log_services),
    "system_log" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log",
            "Systems/Log.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log",
            "Systems/Log.tpl"),
        get = get_handler.get_system_log),
    "system_manager_clear_log" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Actions/LogService.ClearLog",
            ""),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Actions/LogService.ClearLog",
            ""),
        post = post_handler.post_system_manager_clear_log),
    "system_log_entries" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Entries",
            "Systems/LogEntries.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Entries",
            "Systems/LogEntries.tpl"),
        get = get_handler.get_system_log_entries),
    "system_log_entry" : redfish_resource (
        pmdu = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Entry/<entry>",
            "Systems/LogEntry.tpl"),
        stand_alone = (
            "/redfish/v1/Managers/System/<system:sysid>/LogServices/Log/Entry/<entry>",
            "Systems/LogEntry.tpl"),
        get = get_handler.get_system_log_entry),
}
