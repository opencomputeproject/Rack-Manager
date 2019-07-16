# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import re
import sys
import os
import ocslog
from xml.etree import ElementTree
from netaddr import IPNetwork, IPAddress
from subprocess import CalledProcessError
from argparse import ArgumentParser
from utils import completion_code, set_failure_dict, set_success_dict
from lib_utils import get_blade_map_library
from ctypes import create_string_buffer
from ocspaths import *

    
def get_switch_access ():
    """
    Get the login credentials for the management switch.
    
    Return:
        The user name and password needed to access the switch.
    """
    
    switchaccess_binary = get_blade_map_library ()
    
    username = create_string_buffer (48)
    password = create_string_buffer (48)
    
    if (switchaccess_binary.get_switch_access (username, password) != 0):
        raise RuntimeError ("Failed to get switch access credentials.")
    
    return username.value, password.value

def get_switch_ip_address ():
    """
    Get the IP address for the REST interface of the management switch.
    
    Return:
        The switch IP address.
    """
    
    switchaccess_binary = get_blade_map_library ()
    
    ip = create_string_buffer (20)
    
    if (switchaccess_binary.get_switch_address (ip) != 0):
        raise RuntimeError ("Failed to get the switch IP address.")
    
    return ip.value

def get_switch_port_name (port):
    """
    Get the name for the specified switch port.
    
    Parameters:
        port -- The port number to use when generating the same.
        
    Return:
        The internal name for the switch port.
    """
    
    return "gi" + str (port)

def get_switch_vlan_name (vid):
    """
    Get the name for the specified VLAN ID.
    
    Parameters:
        vid -- The VLAN ID.
        
    Return:
        The internal name for the VLAN.
    """
    
    return "VLAN" + str (vid)

def get_xml_string_value (root, tag, friendly):
    """
    Get a string value from a child to an XML element.
    
    Parameters:
        root -- The root of the XML structure to search.
        tag -- The relative path to the tag that has the desired data.
        friendly -- A friendly name for the type of data being retrieved (for exceptions).
        
    Return:
        The string value at the specified tag.
    """
    
    value = root.find ("./" + tag)
    if (value is None):
        raise mgmt_switch_error (friendly + " is not available.")
    
    return value.text

def get_xml_enum_value (root, tag, friendly, enum):
    """
    Get an enumeration value from a child to an XML element.
    
    Parameters:
        root -- The root of the XML structure to search.
        tag -- The relative path to the tag that has the desired data.
        friendly -- A friendly name for the type ef data being retrieved (for exceptions).
        enum -- The enumeration mapping.  Keys are the XML text and values are the enumeration.
        
    Return:
        The enumeration from the specified tag.
    """
    
    value = get_xml_string_value (root, tag, friendly)
    return enum[value]

def get_xml_ps_enum_value (root, ps_type):
    """
    Get the enumerated value for power supply status.
    
    Parameters:
        root -- The root of the XML structure containing the power supply status.
        ps_type -- The type of power supply (main vs. redundant)
        
    Return:
        The enumerated power supply status.
    """
    
    return get_xml_enum_value (
        root,
        ps_type + "PSStatus",
        ps_type + " power supply status",
        {"1" : "normal",
         "2" : "warning",
         "3" : "critical",
         "4" : "shutdown",
         "5" : "not present",
         "6" : "not functioning",
         "7" : "not available",
         "8" : "backing up"})
    
def get_xml_system_name (root):
    """
    Get the system name from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The system name.
    """
    
    return get_xml_string_value (root, "systemName", "system name")

def get_xml_system_description (root):
    """
    Get the system description from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The system description.
    """
    
    return get_xml_string_value (root, "systemDescription", "system description")

def get_xml_serial_number (root):
    """
    Get the serial number from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The serial number.
    """
    
    return get_xml_string_value (root, "serialNumber", "serial number")

def get_xml_base_mac_address (root):
    """
    Get the base unit MAC address from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The base MAC address.
    """
    
    return get_xml_string_value (root, "MACAddress", "base MAC address")

def get_xml_hardware_version (root):
    """
    Get the hardware version from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The hardware version.
    """
    
    return get_xml_string_value (root, "hardwareVersion", "hardware version")

def get_xml_firmware_version (root):
    """
    Get the firmware version from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The firmware version.
    """
    
    return get_xml_string_value (root, "firmwareVersion", "firmware version")

def get_xml_firmware_released_date (root):
    """
    Get the firmware released date from the system global settings XML.
    
    Parameters:
        root -- An XML element to the root of the system global settings.
        
    Return:
        The firmware released date in the form mmddyyyy hh:mm:ss.
    """
    
    return get_xml_string_value (root, "firmwareReleasedDate", "firmware released date")

def get_xml_main_power_supply_status (root):
    """
    Get the status of the main power supply from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        
    Return:
        An enumeration for the main power supply status.
    """
    
    return power_supply_status (
        get_xml_string_value (root, "mainPSStatus", "main power supply status"))

def get_xml_redundant_power_supply_status (root):
    """
    Get the status of the redundant power supply from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        
    Return:
        An enumeration for the redundant power supply status.
    """
    
    return power_supply_status (
        get_xml_string_value (root, "redundantPSStatus", "redundant power supply status"))
    
def get_xml_temperature (root):
    """
    Get the temperature from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        
    Return:
        The system temperature or -1 if the temperature redaing isn't valid.
    """
    
    if (get_xml_string_value (root, "tempSensorStatus", "temperature sensor status") == "1"):
        return int (get_xml_string_value (root, "tempSensorValue", "system temperature"))
    else:
        return -1
    
def get_xml_temperature_monitoring_status (root):
    """
    Get the temperature monitoring status from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        
    Return:
        An enumeration for the temperature monitor status.
    """
    
    return temp_monitor_status (
        get_xml_string_value (root,"temperatureStatus", "temperature status"))
    
def get_xml_fan_status (root, fan):
    """
    Get the status of a system fan from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        fan -- The ID of the fan status to get.
        
    Return:
        An enumeration for the fan status.
    """
    
    return fan_status (get_xml_string_value (
        root, 
        "fan" + str (fan) + "Status", 
        "fan " + str (fan) + " status"))

def get_xml_up_time (root):
    """
    Get the system up time from the unit diagnostics XML.
    
    Parameters:
        root -- An XML element to the root of the unit diagnostics.
        
    Return:
        The number of seconds the system has been running.
    """
    
    return float (get_xml_string_value (root, "upTime", "up time")) / 100.0

def get_xml_port_mac_address (root):
    """
    Get the MAC address from 802.3 settings XML.
    
    Parameters:
        root -- An XML element to the root of the 802.3 settings.
        
    Return:
        The port MAC address.
    """
    
    return get_xml_string_value (root, "MACAddress", "MAC address")
    
def get_xml_port_admin_state (root):
    """
    Get the configured port state from 802.3 settings XML.
    
    Parameters:
        root -- An XML element to the root of the 802.3 settings.
        
    Return:
        An enumeration for the configured port state.
    """
    
    return admin_state (get_xml_string_value (root, "adminState", "port admin state"))
    
def get_xml_port_link_state (root):
    """
    Get the port link state from 802.3 settings XML.
    
    Parameters:
        root -- An XML element to the root of the 802.3 settings.
        
    Return:
        An enumeration for the port link state.
    """
    
    return link_state (get_xml_string_value (root, "linkState", "link state"))

class power_supply_status:
    """
    Enumeration for power supply status codes.
    """
    
    map = {
        1 : "Normal",
        2 : "Warning",
        3 : "Critical",
        4 : "Shutdown",
        5 : "NotPresent",
        6 : "NotFunctioning",
        7 : "NotAvailable",
        8 : "NoPower"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return power_supply_status.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, power_supply_status):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class temp_monitor_status:
    """
    Enumeration for the temperature monitor status.
    """
    
    map = {
        1 : "Normal",
        2 : "OverThreshold",
        3 : "OverCritical"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return temp_monitor_status.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, temp_monitor_status):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class fan_status:
    """
    Enumeration for fan status codes.
    """
    
    map = {
        1 : "Normal",
        2 : "Warning",
        3 : "Critical",
        4 : "Shutdown",
        5 : "NotPresent",
        6 : "NotFunctioning"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return fan_status.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, fan_status):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class admin_state:
    """
    Enumeration for the configured port state.
    """
    
    map = {
        1 : "Up",
        2 : "Down",
        3 : "Testing"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return admin_state.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, admin_state):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class link_state:
    """
    Enumeration for the port link state.
    """
    
    map = {
        1 : "Up",
        2 : "Down",
        3 : "Testing",
        4 : "Unknown",
        5 : "Dormant",
        6 : "NotPresent",
        7 : "LowerLayerDown",
        8 : "Suspended"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return link_state.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, link_state):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class lease_state:
    """
    Enumeration for the DHCP lease state.
    """
    
    map = {
        0 : "",
        1 : "PreAllocated",
        2 : "Valid",
        3 : "Expired",
        4 : "Declined"
    }
    
    def __init__ (self, value):
        self.value = int (value)
        
    def __str__ (self):
        return lease_state.map[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, lease_state):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        elif isinstance (other, basestring):
            return self.__str__ () == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result

class mgmt_switch_error (Exception):
    """
    Exception to indicate REST request errors.
    """
    
    def __init__ (self, value):
        self.value = value
        
    def __str__ (self):
        return repr (self.value)
    
class mgmt_switch:
    """
    Interface to the REST API for the management switch.
    """
    
    def __init__ (self, address = None):
        """
        Initialize the interface the REST API.
        
        Parameters:
            address -- The IP address of the switch.
        """
        
        if (address is not None):
            self.ip = address
        else:
            self.ip = get_switch_ip_address ()
        self.session = None
        
    def get_switch_information (self):
        """
        Get the set of global information describing the physical switch device.
        
        Parameters:
            None.
            
        Return:
            A dictionary with the following keys:
                Name -- The name assigned to the switch.
                Description -- A description of the device.
                SerialNumber -- The serial number for the specific switch.
                MACAddress -- The base address assigned to the switch.
                HWVersion -- The switch hardware version.
                FWVersion -- The current firmware version.
                FWDate -- The released date of the current firmware.
        """
        
        info = {}
        try:
            xml = self.get_system_global_settings ()
            
            info[completion_code.cc_key] = completion_code.success 
            info["Name"] = get_xml_system_name (xml)
            info["Description"] = get_xml_system_description (xml)
            info["SerialNumber"] = get_xml_serial_number (xml)
            info["MACAddress"] = get_xml_base_mac_address (xml)
            info["HWVersion"] = get_xml_hardware_version (xml)
            info["FWVersion"] = get_xml_firmware_version (xml)
            info["FWDate"] = get_xml_firmware_released_date (xml)
                        
        except CalledProcessError as error:
            info[completion_code.cc_key] = completion_code.failure
            info[completion_code.err_code] = error.returncode
            info[completion_code.desc] = error.output.strip ()
                
        except Exception as error:
            info[completion_code.cc_key] = completion_code.failure
            info[completion_code.desc] = str (error)
        
        return info
    
    def get_switch_status (self):
        """
        Get the current health status of the switch.
        
        Parameters:
            None.
            
        Return:
            A dictionary with the following keys:
                MainPowerState -- The status of the main power supply.
                RedundantPowerState -- The status of the redundant power supply.
                ReadingTemp -- The temperature of the system.
                TemperatureSensorState -- The status of the temperature monitor.
                Uptime -- The total running time for the switch.
        """
        
        status = {}
        try:
            xml = self.get_unit_diagnostics ()
            
            status[completion_code.cc_key] = completion_code.success
            status["MainPowerState"] = get_xml_main_power_supply_status (xml)
            status["RedundantPowerState"] = get_xml_redundant_power_supply_status (xml)
            status["ReadingTemp"] = get_xml_temperature (xml)
            status["TemperatureSensorState"] = get_xml_temperature_monitoring_status (xml)
            status["Uptime"] = get_xml_up_time (xml);
        
#             status["FanState"] = []
#             for i in range (1, 7):
#                 status["FanState"].append (get_xml_fan_status (xml, i))

        except CalledProcessError as error:
            status[completion_code.cc_key] = completion_code.failure
            status[completion_code.err_code] = error.returncode
            status[completion_code.desc] = error.output.strip ()
                
        except Exception as error:
            status[completion_code.cc_key] = completion_code.failure
            status[completion_code.desc] = str (error)
            
        return status
    
    def get_port_status (self, port):
        """
        Get the current status of a switch port.
        
        Parameters:
            port -- The port number to query.
            
        Return:
            A dictionary with the following keys:
                MACAddress -- The MAC address for the port.
                AdminState -- The configured state of the port.
                LinkState -- The actual state of the port.
                DHCPAddress -- The DHCP address assigned to the port.
                DHCPLeaseState -- The state of the DHCP address lease.
        """
        
        status = {}
        try:
            xml = self.get_port_802_3_settings (port)
            
            status[completion_code.cc_key] = completion_code.success
            status["MACAddress"] = get_xml_port_mac_address (xml)
            status["AdminState"] = get_xml_port_admin_state (xml)
            status["LinkState"] = get_xml_port_link_state (xml)
            
            text = "port " + str (port)
            lease = self.get_dhcp_lease_for_port (port)
            if (lease is not None):
                status["DHCPAddress"] = get_xml_string_value (lease, "IPAddr", text + " DHCP lease")
                status["DHCPLeaseState"] = lease_state (
                    get_xml_string_value (lease, "state", text + " DHCP lease state"))
            else:
                status["DHCPAddress"] = ""
                status["DHCPLeaseState"] = lease_state (0)
                
        except CalledProcessError as error:
            status[completion_code.cc_key] = completion_code.failure
            status[completion_code.err_code] = error.returncode
            status[completion_code.desc] = error.output.strip ()
                
        except Exception as error:
            status[completion_code.cc_key] = completion_code.failure
            status[completion_code.desc] = str (error)
        
        return status
    
    def get_all_port_status (self):
        """
        Get the status of all switch ports.
        
        Parameters:
            None.
            
        Return:
            A list of dictionaries with each port's status.  The first entry in the list is the
            first port, and is sequencially mapped.  The contents of each entry are the same as for
            individual port status requests.
            
            The first entry contains the status code.  If there is an error, there is only one item
            in the list.
        """
        
        status = []
        try:
            xml = self.get_all_port_802_3_settings ()
            ports = xml.findall ("./Entry")
            
            status = [dict () for i in range (48)]
            status[0][completion_code.cc_key] = completion_code.success
            for i in ports:
                name = get_xml_string_value (i, "interfaceName", "port interface name")
                port = re.match ("gi(\d+)", name)
                if (not port):
                    continue
                
                port = int (port.group (1)) - 1
                status[port]["MACAddress"] = get_xml_port_mac_address (i)
                status[port]["AdminState"] = get_xml_port_admin_state (i)
                status[port]["LinkState"] = get_xml_port_link_state (i)
                status[port]["DHCPAddr"] = ""
                status[port]["DHCPLeaseState"] = lease_state (0)
                
            dhcp = self.get_dhcp_server_bindings ()
            ports = dhcp.findall ("./Entry")
            for i in ports:
                lease = self.get_ports_for_dhcp_lease (i)
                if (not lease):
                    continue
                
                port = lease[0] - 1
                status[port]["DHCPAddr"] = get_xml_string_value (i, "IPAddr", "DHCP lease")
                status[port]["DHCPLeaseState"] = lease_state (
                    get_xml_string_value (i, "state", "DHCP lease state"))
        
        except CalledProcessError as error:
            status = [dict ()]
            status[0][completion_code.cc_key] = completion_code.failure
            status[0][completion_code.err_code] = error.returncode
            status[0][completion_code.desc] = error.output.strip ()
                
        except Exception as error:
            status = [dict ()]
            status[0][completion_code.cc_key] = completion_code.failure
            status[0][completion_code.desc] = str (error)
            
        return status
    
    def get_all_port_link_state (self):
        """
        Get the link state for all switch ports.
        
        Parameters:
            None.
            
        Return:
            A dictionary containing the link state for each port.  The dictionary keys are integer
            port numbers, and the values are a link state enumeration.
        """
        
        link = {}
        try:
            xml = self.get_all_port_802_3_settings ()
            ports = xml.findall ("./Entry")
            
            for i in ports:
                name = get_xml_string_value (i, "interfaceName", "port interface name")
                port = re.match ("gi(\d+)", name)
                if (not port):
                    continue
                
                port = int (port.group (1))
                link[port] = get_xml_port_link_state (i)
                
            link = set_success_dict (link)
            
        except CalledProcessError as error:
            ocslog.log_exception ()
            link = set_failure_dict (error.output.strip ())
                
        except Exception as error:
            ocslog.log_exception ()
            link = set_failure_dict ("get_all_port_link_state() Exception: {0}".format (error))
            
        return link
    
    def send_rest_request (self, request, headers = False):
        """
        Send a request to the switch REST interface.
        
        Parameters:
            request -- The request path to send to the REST interface.
            headers -- Flag indicating if the HTTP headers should be included in the request output.
            
        Return:
            The output from the request.
        """
        
        cmd = ["curl"];
        cmd.append ("-sS");
        if (self.session is not None):
            cmd.append ("--header")
            cmd.append (self.session)
        if (headers):
            cmd.append ("-i")
        cmd.append ("http://" + self.ip + "/" + request)
        
        return subprocess.check_output (cmd, stderr = subprocess.STDOUT)
    
    def login (self):
        """
        Log in to the switch REST interface and create a session for sending requsets.
        
        Parameters:
            None.
            
        Return:
            The session ID header string to add to subsequent HTTP requests.
        """
        
        username, password = get_switch_access ()
        if (self.session is None):
            result = self.send_rest_request (
                "System.xml?action=login&user={0}&password={1}".format (username, password),
                True )

            start = result.find ("sessionID:")
            if (start == -1):
                start = result.find ("<?xml")
                xml = ElementTree.fromstring (result[start:])
                error = xml.find ("./ActionStatus/statusString")
                raise mgmt_switch_error (error.text)
            else:
                end = result.find ("\r\n", start)
                self.session = result[start:end]
                
        return self.session
    
    def logout (self):
        """
        Terminate the session with the REST interface.
        
        Parameters:
            None.
            
        Return:
            None.
        """
        
        if (self.session is not None):
            xml = ElementTree.fromstring (self.send_rest_request ("System.xml?action=logout"))
            status = xml.find ("./ActionStatus/statusString")
            if (status is not None):
                raise mgmt_switch_error (status.text)
            
            status = xml.find ("./system/action")
            if ((status is None) or (status.text != "logout does not exist")):
                raise mgmt_switch_error ("Unknown logout response.")
            
            self.session = None

    def get_section (self, section, queries = {}):
        """
        Query the switch for a section of status information from the REST interface.
        
        Parameters:
            section -- The REST section tag to request.
            
        Return:
            A parsed XML element to the root of the requested section.
        """
        
        self.login ()
        
        query = ""
        for tag, value in queries.iteritems ():
            query += "&" + tag + "=" + value
        result = self.send_rest_request ("wcd?\{" + section + query + "\}")
        
        xml = ElementTree.fromstring (result)
        status = xml.find ("./ActionStatus/statusString")
        if (status is not None):
            raise mgmt_switch_error (status.text)
        
        xml = xml.find ("./DeviceConfiguration/" + section)
        if (xml is None):
            raise mgmt_switch_error ("Requested section " + section + " not found in response.")
        
        return xml
    
    def get_system_global_settings (self):
        """
        Get the global system properties for the switch.
        
        Parameters:
            None.
            
        Return:
            A parsed XML element to the root of the system settings.
        """
        
        return self.get_section ("SystemGlobalSetting")
    
    def get_system_name (self):
        """
        Get the name assigned to the switch.
        
        Parameters:
            None.
            
        Return:
            The configured system name.
        """
        
        return get_xml_system_name (self.get_system_global_settings ())
    
    def get_system_description (self):
        """
        Get the description of the switch.
        
        Parameters:
            None.
            
        Return:
            The switch system description.
        """
        
        return get_xml_system_description (self.get_system_global_settings ())
    
    def get_serial_number (self):
        """
        Get the serial number for the switch.
        
        Parameters:
            None.
            
        Return:
            The switch serial number.
        """
        
        return get_xml_serial_number (self.get_system_global_settings ())
    
    def get_base_mac_address (self):
        """
        Get the base MAC address for the switch.
        
        Parameters:
            None.
            
        Return:
            The base MAC address.
        """
        
        return get_xml_base_mac_address (self.get_system_global_settings ())
    
    def get_hardware_version (self):
        """
        Get the hardware version of the switch.
        
        Parameters:
            None.
            
        Return:
            The switch hardware version.
        """
        
        return get_xml_hardware_version (self.get_system_global_settings ())
    
    def get_firmware_version (self):
        """
        Get the version of the currently running firmware.
        
        Parameters:
            None.
            
        Return:
            The current firmware version.
        """
        
        return get_xml_firmware_version (self.get_system_global_settings ())
    
    def get_firmware_released_date (self):
        """
        Get the released data for the current firmware.
        
        Parameters:
            None.
            
        Return:
            The firmware released data in the form of mmddyyyy hh:mm:ss
        """
        
        return get_xml_firmware_released_date (self.get_system_global_settings ())
    
    def get_all_port_802_3_settings (self):
        """
        Get the 802.3 settings for all ports.
        
        Parameters:
            None.
            
        Return:
            A parsed XML element to the root of the 802.3 settings.
        """
        
        return self.get_section ("Standard802_3List")
    
    def get_port_802_3_settings (self, port):
        """
        Get the 802.3 settings for a specific port.
        
        Parameters:
            port -- The Ethernet port number to query.
            
        Return:
            A parsed XML element to the root of the port's 802.3 settings.
        """
        
        name = get_switch_port_name (port)
        result = self.get_section ("Standard802_3List", {"interfaceName" : name})
        entry = result.find ("./Entry")
        if (entry is None):
            raise mgmt_switch_error ("No entry found for port " + name)
        
        return entry
    
    def get_port_mac_address (self, port):
        """
        Get the MAC address for a specific Ethernet port.
        
        Parameters:
            port -- The Ethernet port number to query.
            
        Return:
            The MAC address for the port.
        """
        
        return get_xml_port_mac_address (self.get_port_802_3_settings (port))
    
    def get_port_admin_state (self, port):
        """
        Get the desired state of an Ethernet port.
        
        Parameters:
            port -- The Ethernet port number to query.
            
        Return:
            The desired state of the interface.  The 'testing' state indacates that no operational
            packets can be passed.
        """
        
        return get_xml_port_admin_state (self.get_port_802_3_settings (port))
        
    def get_port_link_state (self, port):
        """
        Get the link state for a specific Ethernet port.
        
        Parameters:
            port -- The Ethernet port number to query.
            
        Return:
            The link state for the port.
        """
        
        return get_xml_port_link_state (self.get_port_802_3_settings (port))
        
    def get_unit_diagnostics (self):
        """
        Get the diagnostic information for the unit.
        
        Parameters:
            None.
            
        Return:
            The parsed XML element to the root node containing the diagnostic status.
        """
        
        result = self.get_section ("DiagnosticsUnitList")
        entry = result.find ("./Entry")
        if (entry is None):
            raise mgmt_switch_error ("No unit diagnostics entry found.")
        
        return entry
    
    def get_main_power_supply_status (self):
        """
        Get the status of the main power supply for the switch.
        
        Parameters:
            None.
            
        Return:
            The state of the main power supply.
        """
        
        return get_xml_main_power_supply_status (self.get_unit_diagnostics ())
        
    def get_redundant_power_supply_status (self):
        """
        Get the status of the redundant power supply for the switch.
        
        Parameters:
            None.
            
        Return:
            The state of the redundant power supply.
        """
        
        return get_xml_redundant_power_supply_status (self.get_unit_diagnostics ())
        
    def get_fan_status (self, fan):
        """
        Get the status of a specific fan in the switch.
        
        Parameters:
            fan -- The fan number to query.
            
        Return:
            The status of the specified fan.
        """
        
        return get_xml_fan_status (self.get_unit_diagnostics (), fan)
        
    def get_temperature (self):
        """
        Get the temperature of the switch.
        
        Parameters:
            None.
            
        Return:
            The system temperature.
        """
        
        return get_xml_temperature (self.get_unit_diagnostics ())
        
    def get_temperature_monitoring_status (self):
        """
        Get the status of chassis tempurature monitoring.
        
        Parameters:
            None.
            
        Return:
            The chassis temperature status.
        """
        
        return get_xml_temperature_monitoring_status (self.get_unit_diagnostics ())
        
    def get_up_time (self):
        """
        Get the up time for the switch.
        
        Parameters:
            None.
            
        Return:
            The up time for the switch in seconds.
        """
        
        return get_xml_up_time (self.get_unit_diagnostics ())
    
    def get_port_vlan_membership (self, port):
        """
        Get the VLAN ID the specified is a member of.
        
        Parameters:
            port -- The port number to query.
            
        Return:
            The VLAN ID for the specified port.
        """
        
        name = get_switch_port_name (port)
        xml = self.get_section ("VLANMembershipInterfaceList", {"interfaceName" : name})
        entry = xml.find ("./Entry")
        if (entry is None):
            raise mgmt_switch_error ("No VLAN entry for interface " + name)
        
        return int (get_xml_string_value (entry, "PVID", "VLAN ID"))
    
    def get_ports_on_vlan (self, vid):
        """
        Get the port numbers assigned to a specified VLAN.
        
        Parameters:
            vid -- The VLAN ID to query.
            
        Return:
            A list of port numbers for the VLAN.
        """
        
        vlan = str (vid)
        xml = self.get_section ("VLANMembershipList", {"VLANID" : vlan})
        members = xml.findall ("./VLAN/MembershipList/VLANMember")
        
        ports = []
        for member in members:
            name = get_xml_string_value (member, "interfaceName", "VLAN " + vlan + " intf name")
            port = re.match ("gi(\d+)", name)
            if (port):
                ports.append (int (port.group (1)))
                
        return ports
    
    def get_ipv4_addresses (self):
        """
        Get all IPv4 addresses assigned to switch interfaces.
        
        Parameters:
            None.
            
        Return:
            A parsed XML element to the list of IPv4 addresses.
        """
        
        return self.get_section ("IPv4InterfaceList")
    
    def get_vlan_ip_address (self, vid):
        """
        Get the IP address assigned to the switch for a particular VLAN ID.
        
        Parameters:
            vid -- The VLAN ID to query.
            
        Return:
            An IPNetwork object for the VLAN address.
        """
        
        name = get_switch_vlan_name (vid)
        text = name
        xml = self.get_ipv4_addresses ()
        vlan = xml.findall ("./ifEntry/[interfaceName='" + name + "']")
        if (not vlan):
            raise mgmt_switch_error ("No interface entry for vlan " + str (vid) + ".")
        
        addr = get_xml_string_value (vlan[0], "IPAddr", text + " IP")
        subnet = get_xml_string_value (vlan[0], "subnetMask",  text + " subnet")
        return IPNetwork (addr + "/" + subnet)
    
    def get_vlan_for_ip_address (self, ip):
        """
        Get the ID of the VLAN that contains the specified IP address.
        
        Parameters:
            ip -- The IP address to search for.
            
        Return:
            The VLAN ID or -1 if no VLAN exists for the IP address.
        """
        
        xml = self.get_ipv4_addresses ()
        vlans = xml.findall ("./ifEntry")
        if (not vlans):
            raise mgmt_switch_error ("No VLAN IP addresses found.")
        
        vid = -1
        for vlan in vlans:
            name = get_xml_string_value (vlan, "interfaceName", "IPv4 interface name")
            check = re.match ("VLAN(\d+)", name)
            if (not check):
                continue
            
            current = check.group (1)
            addr = get_xml_string_value (vlan, "IPAddr", "VLAN " + current + " IP")
            subnet = get_xml_string_value (vlan, "subnetMask", "VLAN " + current + " subnet")
            if (IPNetwork (addr + "/" + subnet) == IPNetwork (ip + "/" + subnet)):
                vid = int (current)
                break
            
        return vid
    
    def get_dhcp_server_bindings (self):
        """
        Get the list of IP addresses issued by the DHCP server.
        
        Parameters:
            None.
            
        Return:
            A parsed XML element to the root node containing the entries for each IP address.
        """
        
        return self.get_section ("DHCPSrvBindingList")
    
    def get_ports_for_dhcp_lease (self, lease):
        """
        Get the switch ports associated with a current DHCP lease.
        
        Parameters:
            lease -- A parsed XML element with DHCP lease information.
            
        Return:
            A list of port numbers that could have provided the DHCP lease.
        """
        
        client = get_xml_string_value (lease, "IPAddr", "DHCP leased IP")
        vid = self.get_vlan_for_ip_address (client)
        return self.get_ports_on_vlan (vid)
    
    def get_dhcp_lease_for_port (self, port):
        """
        Get the DHCP server lease associated with a specific port.
        
        Parameters:
            port -- The port to query.
            
        Return:
            The DHCP server lease for the port or None if no lease is available.  Only a single
            lease is returned.
        """
        
        port = int (port)
        dhcp = self.get_dhcp_server_bindings ()
        leases = dhcp.findall ("./Entry")
        
        lease = None
        for i in leases:
            ports = self.get_ports_for_dhcp_lease (i)
            if (port in ports):
                lease = i
                break;
            
        return lease
    
class mgmt_switch_console:
    """
    Interface to the serial console for the management switch.
    """
    
    def __init__ (self, dev):
        """
        Initialize the interface to the switch serial console.
        
        Parameters:
            dev -- The path to the serial device to use to connect to the switch.
        """
        
        self.dev = dev
        
    def execute_request (self, args, verbose = False):
        """
        Execute the interface program to communicate with the serial console of the management
        switch.
        
        Parameters:
            args -- A collection of arguments to pass to the program.
            verbose -- A flag indicating if the execution output should be piped to stdout.
            
        Return:
            Completion status.  In verbose mode, this will be empty.
        """
        
        cmd = ["ocsswitch", "-d", self.dev]
        cmd.extend (args)
        if (verbose):
            cmd.append ("-e")
        
        result = {}
        if (not verbose):
            try:
                subprocess.check_output (cmd, stderr = subprocess.STDOUT)
                result[completion_code.cc_key] = completion_code.success
                
            except CalledProcessError as error:
                result[completion_code.cc_key] = completion_code.failure
                result[completion_code.err_code] = error.returncode
                result[completion_code.desc] = error.output.strip ()
                
            except Exception as error:
                result[completion_code.cc_key] = completion_code.failure
                result[completion_code.desc] = str(error)
        else:
            try:
                subprocess.call (cmd)
                
            except Exception as error:
                print error
            
        return result
        
    def configure(self, file, verbose = False):
        """
        Reconfigure the switch using the specified configuration file.  The new configuration will
        persist across reboots.
        
        This will not return until the configuration has been applied, and will take some time.
        
        Parameters:
            file -- The name of the configuration file on the TFTP server.
            verbose -- A flag indicating if the console information should be sent to stdout.
            
        Return:
            Completion status.  In verbose mode, this will be empty.
        """
        
        path = srvroot_shared_path + "/" + file
    
        if (not os.path.exists(path)):
            return set_failure_dict("Configuration file does not exist: {0}".format(file), completion_code.failure)
        
        args = ["-f", path, "-c"]
        return self.execute_request(args, verbose = verbose)
        
    def upgrade_fw (self, server, path, verbose = False):
        """
        Upgrade the firmware image of the switch.
        
        Parameters:
            server -- The IP address of the TFTP server that is providing the firmware image.
            path -- The path to the image file on the TFTP server.
            verbose -- A flag indicating if the console information should be sent to stdout.
            
        Return:
            Completion status.  In verbose mode, this will be empty.
        """

        args = ["-t", server, "-f", path, "-u"]
        return self.execute_request (args, verbose = verbose)
        
    def reboot (self, verbose = False):
        """
        Reboot the switch.  This will not return until the switch has completed rebooting.
        
        Parameters:
            verbose -- A flag indicating if the console information should be sent to stdout.
            
        Return:
            Completion status.  In verbose mode, this will be empty.
        """
        
        args = ["-r"]
        return self.execute_request (args, verbose = verbose)
    
    def shell (self, baud = None, pass_sigint = False):
        """
        Start an interactive shell with the management switch.  This will not return until the
        shell session receives a signal
         
        Parameters:
            baud -- An optional parameter to specify the baud rate of the serial port.
            pass_sigint -- An optional parameter indicating if Ctrl-C and Ctrl-D should be pased
            to the remote shell or caught locally to terminate the shell session.
             
        Return:
            None.
        """
        
        cmd = ["ocsswitch", "-d", self.dev, "-s"]
        if (baud):
            cmd.extend (["-b", str (baud)])
        if (pass_sigint):
            cmd.append ("-X")
        subprocess.call (cmd)
          
        
if __name__ == "__main__":
    parser = ArgumentParser ()
    
    options = parser.add_argument_group ("REST Options")
    options.add_argument ("-a", "--address", help = "The IP address for the switch")
    options.add_argument ("-i", "--info", action = "store_true", help = "Get switch information")
    options.add_argument ("-s", "--status", action = "store_true", help = "Get switch status")
    options.add_argument ("-p", "--port", type = int, help = "Get single port status")
    options.add_argument ("-P", "--all", action = "store_true", help = "Get status for all ports")
    options.add_argument ("-l", "--link", type = int, help = "Get single port link state")
    options.add_argument ("-L", "--linkall", action = "store_true", help = "Get link state for all ports")
    
    options = parser.add_argument_group ("Console Options")
    options.add_argument ("-d", "--device", help = "The serial port device for the console")
    options.add_argument ("-A", "--server", help = "TFTP server address for FW upgrade")
    options.add_argument ("-c", "--config", help = "Apply the specified configuration file")
    options.add_argument ("-u", "--upgrade", help = "Upgrade with the specified firmware")
    options.add_argument ("-r", "--reboot", action = "store_true", help = "Reboot the switch")
    options.add_argument ("-S", "--shell", action = "store_true", help = "Start an interactive shell")
    
    args = parser.parse_args ()
    rest = None
    console = None
    if (args.info or args.status or args.port or args.all or args.link or args.linkall):
        if (not args.address):
            print "Switch IP address required for specified action."
            sys.exit (1)

        rest = mgmt_switch (args.address)
        
    if (args.config or args.upgrade or args.reboot or args.shell):
        if (not args.device):
            print "Switch serial port required for specified action."
            sys.exit (1)
        elif (args.upgrade and not args.server):
            print "TFTP server address required for firmware upgrade."
            sys.exit (1)

        console = mgmt_switch_console (args.device)
        
    if (rest is not None):
        if (args.info):
            print rest.get_switch_information ()
            
        if (args.status):
            print rest.get_switch_status ()
            
        if (args.port):
            print rest.get_port_status (args.port)
            
        if (args.all):
            port = 1
            for i in rest.get_all_port_status ():
                print "%d -> %s" % (port, repr (i))
                port = port + 1
                
        if (args.link):
            print rest.get_port_link_state (args.link)
            
        if (args.linkall):
            for i, j in sorted (rest.get_all_port_link_state ().iteritems ()):
                print "{0} -> {1}".format (i, j)
                
        rest.logout ()
        
    if (console is not None):
        if (args.config):
            print console.configure (args.config)
            
        if (args.upgrade):
            print console.upgrade_fw(args.server, args.upgrade)
            
        if (args.reboot):
            print console.reboot ()
            
        if (args.shell):
            console.shell ()
