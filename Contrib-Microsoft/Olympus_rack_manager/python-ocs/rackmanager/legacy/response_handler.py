# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from xml.etree import ElementTree
from controls.utils import completion_code, check_success, set_failure_dict, set_success_dict

NO_STATUS = False

def add_element (parent, tag, value, write_fail = False, nil = False):
    """
    Add a new element to the XML document.
    
    :param parent: The parent element for the element that will be created.
    :param tag: The name of the new element.
    :param value: The string value to assign to the element.
    :param write_fail: Flag to indicate if failed values should be saved as the element data.
    :param nil: Flag to indicate if a nil attribute should be added if the tag has no value.
    
    :return The new element instance.
    """
    
    element = ElementTree.SubElement (parent, tag)
    if (value and (write_fail or (value.lower () != "failure"))):
        element.text = value
    elif (nil):
        element.set ("i:nil", "true")
        
    return element

class response_category:
    """
    Response object that contains status information and other arbitrary information.
    """
    
    def __init__ (self, response_type, status = None, results = []):
        """
        Initialize the response container.
        
        :param response_type: The type of response container that is being generated.
        :param status: A request_status object representing the status for this container.
        :param results: A list of objects that contain information for this container.
        """
        
        self.root = response_type
        self.completion = status
        self.results = results
        
    def format (self, parent = None):
        """
        Format the response as an XML object representing the information contained by the object.
        
        :param parent: The parent element that contains the response data.  If this is not
        specified, a new element will be created.
        
        :return An XML element that contains the formatted response data and a flag indicating if
        the cotegory is reporting success.
        """
        
        if (parent is None):
            parent = ElementTree.Element (tag = self.root, attrib = {
                "xmlns:i" : "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns" : "http://schemas.datacontract.org/2004/07/Microsoft.GFS.WCS.Contracts"})
        else:
            parent = ElementTree.SubElement (parent, self.root)
        
        success = NO_STATUS
        
        if (self.completion):
            success = self.completion.format (parent = parent)[1]
            
        for result in self.results:
            if (result):
                success = result.format (parent = parent)[1] or success
        
        if (self.completion):
            self.completion.update_status (success)
            
        return (parent, success)
        
class request_status:
    """
    Status information for the object being requested.
    """

    code_map = {
        completion_code.success : "Success",
        completion_code.failure : "Failure",
        completion_code.deviceoff : "DevicePoweredOff",
        completion_code.fwdecompress : "FirmwareDecompressing",
        completion_code.notpresent : "Timeout"
    }

    @staticmethod
    def get_placeholder_status ():
        """
        Get a status object to act as a place holder for response objects that only have status
        based on their children.
        
        :return The status object.
        """
        
        return request_status (set_failure_dict (""))
    
    def __init__ (self, status):
        """
        Initialize status information from a function result structure.
        
        :param status: The function result information.
        """
        
        code = status.get (completion_code.cc_key, None)
        
        self.code = code if (code) else "Unknown"
        self.description = status.get (completion_code.desc, "")
        self.code_element = None
        
        self.code = request_status.code_map.get (self.code, self.code)
        
    def format (self, parent):
        """
        Format the status information in the XML document.
        
        :param parent: The parent element that will contain the status information.
        
        :return The parent element and a flag indicating if the status indicates success.
        """
        
        self.code_element = add_element (parent, "completionCode", self.code, write_fail = True)
        add_element (parent, "apiVersion", "1")
        add_element (parent, "statusDescription", self.description)
        
        return (parent, (self.code == completion_code.success))
    
    def update_status (self, success):
        """
        Update the completion code that was formatted in the response to represent the overall code.
        
        :param success: A flag indicating the success state of the request.
        """
        
        if (success and (self.code != completion_code.success) and (self.code_element is not None)):
            self.code_element.text = "Success"
        
class service_version:
    """
    Response object for the service version.
    """
    
    def __init__ (self, version):
        """
        Initialize the service version response.
        
        :param version: The result of the system query for the version information.
        """
        
        self.version = version.get ("Package", None)
            
    def format (self, parent):
        """
        Format the server version in the XML document.
        
        :param parent: The parent element that will contain the version information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "serviceVersion", self.version)
        
        return (parent, NO_STATUS)
    
class led_state:
    """
    Response object for the attention LED state.
    """
    
    def __init__ (self, state):
        """
        Initialize the attention LED state response.
        
        :param state: The result of the system query for the LED state.
        """
        
        self.state = state.get ("Manager LED Status", "NA")
        if (self.state == "Unknown"):
            self.state = "NA"
            
    def format (self, parent):
        """
        Format the attention LED state in the XML document.
        
        :param parent: The parent element that will contain the LED state.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "ledState", self.state)
        
        return (parent, NO_STATUS)
    
class blade_number:
    """
    Response object to report the blade number.
    """
    
    def __init__ (self, blade):
        """
        Initialize the blade number response.
        
        :param blade: The blade ID number to report.
        """
        
        if (blade >= 0):
            self.blade = str (blade)
        else:
            self.blade = str (-blade)
            
    def format (self, parent):
        """
        Format the blade number in the XML document.
        
        :param parent: The parent element that will contain the blade number.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeNumber", self.blade)
        
        return (parent, NO_STATUS)
    
class blade_type:
    """
    Response object to report the blade number.
    """
    
    def __init__ (self, info):
        """
        Initialize the blade type response.
        
        :param blade: The information to determine the type of blade.
        """
        
        self.blade = "Server"
            
    def format (self, parent):
        """
        Format the blade type in the XML document.
        
        :param parent: The parent element that will contain the blade type.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeType", self.blade)
        
        return (parent, NO_STATUS)
    
class blade_info:
    """
    Response object for blade information.
    """
    
    def __init__ (self, info):
        """
        Initialize the blade info response.
        
        :param info: The result of the system query for blade info.
        """
        
        server = info.get ("Server", {})
        
        if (check_success (info)):
            self.type = "Server"
        else:
            self.type = None
            
        self.serial = info.get ("SerialNumber", None)
        self.asset_tag = info.get ("AssetTag", None)
        self.fw = server.get ("BMCVersion", None)
        self.hw = server.get ("HWVersion", None)
        
    def format (self, parent):
        """
        Format the blade information in the XML document.
        
        :param parent: The parent element that will contain the blade information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeType", self.type)
        add_element (parent, "serialNumber", self.serial)
        add_element (parent, "assetTag", self.asset_tag)
        add_element (parent, "firmwareVersion", self.fw)
        add_element (parent, "hardwareVersion", self.hw)
        
        return (parent, NO_STATUS)
    
class blade_info_versions:
    """
    Response object for blade version information..
    """
    
    def __init__ (self, info):
        """
        Initialize the blade version info response.
        
        :param info: The result of the system query for blade info.
        """
        
        server = info.get ("Server", {})

        self.bios = server.get ("BiosVersion", None)
        self.cpld = server.get ("CpldVersion", None)
        
    def format (self, parent):
        """
        Format the blade version information in the XML document.
        
        :param parent: The parent element that will contain the blade version information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "biosVersion", self.bios)
        add_element (parent, "cpldVersion", self.cpld)
        
        return (parent, NO_STATUS)
        
class blade_nic_info:
    """
    Response object for NIC information on the blade.
    """
    
    @staticmethod
    def get_nic_list (mac):
        """
        Get the list of NIC information objects for the system.
        
        :param mac: The result of the system query for blade NIC information.
        
        :return A list contaning response objects for the NIC information.
        """
        
        nics = []
        if (mac):
            status = request_status (mac)
            nic1 = blade_nic_info (mac)
            nics.append (response_category ("NicInfo", status = status, results = [nic1]))
            
            if (check_success (mac)):
                status = request_status (set_failure_dict ("Not Present", "Success"))
                nic2 = blade_nic_info ()
                nics.append (response_category ("NicInfo", status = status, results = [nic2]))
                    
        return nics
                
    def __init__ (self, nic = None):
        """
        Initialize the blade NIC information.
        
        :param nic: The result of the system query for blade NIC information.
        """
        
        if (nic):
            self.id = "1" if check_success (nic) else "0"
            self.mac = nic.get ("MAC1", None)
        else:
            self.id = "2"
            self.mac = None
            
    def format (self, parent):
        """
        Format the blade NIC information in the XML document.
        
        :param parent: The parent element that will contain the NIC information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "deviceId", self.id)
        add_element (parent, "macAddress", self.mac)
        
        return (parent, NO_STATUS)
    
class blade_default_power_state:
    """
    Response object for the blade default power state.
    """
    
    def __init__ (self, state):
        """
        Initialize the blade default power state response.
        
        :param state: The result of the system query for the blade default power state.
        """
        
        self.state = state.get ("Default Power State", "NA")
            
    def format (self, parent):
        """
        Format the blade default power state in the XML document.
        
        :param parent: The parent element that will contain the default power state.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeState", self.state)
        
        return (parent, NO_STATUS)
    
class chassis_controller_info:
    """
    Response object for the chassis contorller information.
    """
    
    def __init__ (self, info):
        """
        Initialize the controller information.
        
        :param info: The result of the system query for controller information.
        """
        
        self.serial = info.get ("Board Serial", None)
        self.asset_tag = info.get ("Product Assettag", None)
        self.fw = "NA" if (check_success (info)) else None
        self.hw = info.get ("Board Version", None)
        self.sw = info.get ("Package", None)
        self.uptime = info.get ("Up Time", None)
        
    def format (self, parent):
        """
        Format the chassis controller information in the XML document.
        
        :param parent: The parent element that will contain the controller information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "serialNumber", self.serial)
        add_element (parent, "assetTag", self.asset_tag)
        add_element (parent, "firmwareVersion", self.fw)
        add_element (parent, "hardwareVersion", self.hw)
        add_element (parent, "softwareVersion", self.sw)
        add_element (parent, "systemUptime", self.uptime)
        
        return (parent, NO_STATUS)
    
class chassis_network_info:
    """
    Response object for a chassis network interface.
    """
    
    @staticmethod
    def build_network_property (nic):
        """
        Create a response object for a single chassis network interface.
        
        :param nic: The result of the system query for the NIC.
        
        :return The NIC response object.
        """
        
        status = request_status (nic)
        eth = chassis_network_info (nic)
        return response_category ("ChassisNetworkProperty", status = status, results = [eth])
    
    @staticmethod
    def build_network_property_collection (*nics):
        """
        Create a response object for a collection of network interfaces.
        
        :param nics: The results of the system queries for the NICs that should be in the
        collection.
        
        :return The network property collection response object.
        """
        
        collection = []
        for nic in nics:
            collection.append (chassis_network_info.build_network_property (nic))
            
        return response_category ("chassisNetworkPropertyCollection", results = collection)
    
    @staticmethod
    def get_network_properties (*nics):
        """
        Create a response object for the chassis network properties.
        
        :param nics: The list of results from the system queries for the NICs that will be reported.
        
        :return The network properties response object.
        """
        
        network = chassis_network_info.build_network_property_collection (*nics)
        return response_category ("networkProperties",
            status = request_status.get_placeholder_status (), results = [network])
                
    def __init__ (self, info):
        """
        Initialize the network interface information.
        
        :param info: The result of the system query for network information.
        """
        
        ip4 = info.get ("IPv4Addresses", {})
        ip6 = info.get ("IPv6Addresses", {})
        
        self.mac = info.get ("MACAddress", None)
        self.ip4 = ip4.get ("Address", None)
        self.subnet = ip4.get ("SubnetMask", None)
        self.gateway = ip4.get ("Gateway", None)
        self.ip6 = ip6.get ("Address", None)
        self.prefix = ip6.get ("PrefixLength", None)
        self.hostname = info.get ("Hostname", None)
        
        self.dhcp = ip4.get ("AddressOrigin", None)
        if (self.dhcp):
            self.dhcp = "true" if (self.dhcp == "DHCP") else "false"
            
        if (self.ip4 and self.ip6):
            self.ip = "{0}, {1}".format (self.ip4, self.ip6)
        elif (self.ip4):
            self.ip = self.ip4
        elif (self.ip6):
            self.ip = self.ip6
        else:
            self.ip = None
            
        if (self.subnet and self.prefix):
            self.mask = "{0}, {1}".format (self.subnet, self.prefix)
        elif (self.subnet):
            self.mask = self.subnet
        elif (self.prefix):
            self.mask = self.prefix
        else:
            self.mask = None
            
    def format (self, parent):
        """
        Format the chassis network interface information in the XML document.
        
        :param parent: The parent element that will contain the network interface information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "macAddress", self.mac)
        add_element (parent, "ipAddress", self.ip)
        add_element (parent, "subnetMask", self.mask)
        add_element (parent, "gatewayAddress", self.gateway)
        ElementTree.SubElement (parent, "dnsAddress")
        ElementTree.SubElement (parent, "dhcpServer", {"i:nil" : "true"})
        ElementTree.SubElement (parent, "dnsDomain", {"i:nil" : "true"})
        add_element (parent, "dnsHostName", self.hostname, nil = True)
        add_element (parent, "dhcpEnabled", self.dhcp)
        
        return (parent, NO_STATUS)
    
class chassis_psu_info:
    """
    Response object for a chassis power supply.
    """
    
    @staticmethod
    def get_psu_list (psu):
        """
        Get the list of PSU information objects for the respons.
        
        :param psu: The result of the system query for power supply information.
        
        :return The list of PSU information objects.
        """
        
        psu_list = []
        for i in range (1, 7):
            status = request_status (psu)
            info = chassis_psu_info (i, psu)
            psu_list.append (response_category ("PsuInfo", status = status, results = [info]))
            
        return psu_list
        
    def __init__ (self, psu_id, psu):
        """
        Initialize the PSU information.
        
        :param psu_id: The ID of the PSU.
        :param psu: The result of the system query for power supply information.
        """
        
        self.id = str (psu_id)
        self.serial = psu.get ("Board Serial", None)
        self.state = "ON" if (check_success (psu)) else "NA"
        self.type = None
        if (psu_id == 1):
            self.power = psu.get ("Feed1Phase1PowerInWatts", -1)
        elif (psu_id == 2):
            self.power = psu.get ("Feed1Phase2PowerInWatts", -1)
        elif (psu_id == 3):
            self.power = psu.get ("Feed1Phase3PowerInWatts", -1)
        elif (psu_id == 4):
            self.power = psu.get ("Feed2Phase1PowerInWatts", -1)
        elif (psu_id == 5):
            self.power = psu.get ("Feed2Phase2PowerInWatts", -1)
        elif (psu_id == 6):
            self.power = psu.get ("Feed2Phase3PowerInWatts", -1)
        else:
            self.power = psu.get ("PowerDrawnInWatts", -1)
        self.power = str (int (self.power))
            
    def format (self, parent):
        """
        Format the PSU information in the XML document.
        
        :param parent: The parent element that will contain the PSU information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "id", self.id)
        add_element (parent, "serialNumber", self.serial)
        add_element (parent, "state", self.state)
        add_element (parent, "powerOut", self.power)
        add_element (parent, "deviceType", self.type)
        
        return (parent, NO_STATUS)
    
class chassis_blade_info:
    """
    Response object for information about a blade in the chassis.
    """
    
    @staticmethod
    def get_blade_info (blade_id, info):
        """
        Get the complete response object for chassis blade information.
        
        :param blade_id: The slot ID for the blade.
        :param info: The result of the system query for the blade information.
        
        :return The chassis blade information response object.
        """
        
        status = request_status (info)
        blade = chassis_blade_info (blade_id, info)
        mac = response_category ("bladeMacAddress", results = blade_nic_info.get_nic_list (info))
        
        return response_category ("BladeInfo", status = status, results = [blade, mac])
    
    @staticmethod
    def get_blade_list (blades):
        """
        Get the list of chassis blade information.
        
        :param blades: The list of system query results for all blades.
        
        :return A list of blade information response objects.
        """
        
        blade_list = []
        for blade, info in enumerate (blades, 1):
            blade_list.append (chassis_blade_info.get_blade_info (blade, info))
            
        return blade_list
        
    def __init__ (self, blade_id, info):
        """
        Initialize the chassis blade information.
        
        :param blade_id: The slot ID for the blade.
        :param info: The result of the system query for the blade information.
        """
        
        self.id = info.get ("Slot Id", str (blade_id))
        self.guid = info.get ("GUID", "00000000-0000-0000-0000-000000000000")
        self.name = "BLADE{0}".format (self.id)
        self.state = info.get ("Port State", "NA").upper ()
        
    def format (self, parent):
        """
        Format the chassis blade information in the XML document.
        
        :param parent: The parent element that will contain the blade information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeNumber", self.id)
        add_element (parent, "bladeGuid", self.guid)
        add_element (parent, "bladeName", self.name)
        add_element (parent, "powerState", self.state)
        
        return (parent, NO_STATUS)
    
class chassis_battery_info:
    """
    Response object for chassis battery information.
    """
    
    @staticmethod
    def get_battery_list ():
        """
        Get the list of chassis battery information.
        
        :return A list of battery information response objects.
        """
        
        battery_list = []
        for i in range (1, 7):
            status = request_status (set_success_dict ())
            info = chassis_battery_info (i)
            battery_list.append (response_category ("BatteryInfo", status = status,
                results = [info]))
            
        return battery_list
        
    def __init__ (self, battery_id):
        """
        Initialize the chassis battery information.
        
        :param battery_id: The ID for the battery.
        """
        
        self.id = str (battery_id)
        self.presence = "0"
        self.power = "0"
        self.charge = "0"
        self.fault = "0"
        
    def format (self, parent):
        """
        Format the chassis battery information in the XML document.
        
        :param parent: The parent element that will contain the battery information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "id", self.id)
        add_element (parent, "presence", self.presence)
        add_element (parent, "batteryPowerOutput", self.power)
        add_element (parent, "batteryChargeLevel", self.power)
        add_element (parent, "faultDetected", self.power)
        
        return (parent, NO_STATUS)

class chassis_fan_info:
    """
    Response object for chassis fan information.
    """
    
    @staticmethod
    def get_fan_list ():
        """
        Get the list of chassis fan information.
        
        :return A list of fan information response objects.
        """
        
        fan_list = []
        for i in range (1, 7):
            status = request_status (set_success_dict ())
            info = chassis_fan_info (i)
            fan_list.append (response_category ("FanInfo", status = status, results = [info]))
            
        return fan_list
        
    def __init__ (self, fan_id):
        """
        Initialize the chassis fan information.
        
        :param battery_id: The ID for the fan.
        """
        
        self.id = str (fan_id)
        self.healthy = "true"
        self.speed = "0"
        self.type = None
        
    def format (self, parent):
        """
        Format the chassis fan information in the XML document.
        
        :param parent: The parent element that will contain the fan information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "fanId", self.id)
        add_element (parent, "isFanHealthy", self.healthy)
        add_element (parent, "fanSpeed", self.speed)
        add_element (parent, "fanType", self.type)
        
        return (parent, NO_STATUS)
    
class chassis_temp:
    """
    Response object for the inlet temperature.
    """
    
    def __init__ (self, temp):
        """
        Initialize the inlet temperature response.
        
        :param state: The result of the system query for the inlet temperature.
        """
        
        self.temp = temp.get ("Temperature", None)
        if (self.temp):
            self.temp = str (self.temp)
            
    def format (self, parent):
        """
        Format the inlet temperature in the XML document.
        
        :param parent: The parent element that will contain the inlet temperature.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeInletTemp", self.temp)
        
        return (parent, NO_STATUS)
    
class power_state:
    """
    Response object for the power port state.
    """
    
    def __init__ (self, state):
        """
        Initilaize the power port state response.
        
        :param state: The result of the system query for the power state.
        """
        
        self.decompress = state.get ("Decompress", "0")
        self.state = state.get ("Port State", "NA")
            
    def format (self, parent):
        """
        Format the power port state in the XML document.
        
        :param parent: The parent element that will contain the power port state.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "Decompression", self.decompress)
        add_element (parent, "powerState", self.state)
        
        return (parent, NO_STATUS)
    
class blade_state:
    """
    Response object for the blade power state.
    """
    
    def __init__ (self, state):
        """
        Initilaize the blade power state response.
        
        :param state: The result of the system query for the blade power state.
        """
        
        self.state = state.get ("State", "NA")
            
    def format (self, parent):
        """
        Format the blade power state in the XML document.
        
        :param parent: The parent element that will contain the blade power state.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "bladeState", self.state)
        
        return (parent, NO_STATUS)
    
    
class ac_port_state:
    """
    Response object to report the AC port state.
    """
    
    def __init__ (self, port, state):
        """
        Initialize the AC port state response.
        
        :param port: The port ID for the response.
        :param state: The result of the system query for the AC port state.
        """
        
        self.port = str (port)
        self.state = state.get ("Relay", "NA").upper ()
            
    def format (self, parent):
        """
        Format the AC port state in the XML document.
        
        :param parent: The parent element that will contain the AC port state.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "portNo", self.port)
        add_element (parent, "powerState", self.state)
        
        return (parent, NO_STATUS)
    
class blade_power_limit:
    """
    Response object for the blade power limit.
    """
    
    def __init__ (self, limit):
        """
        Initialize the blade power limit response.
        
        :param limit: The result of the system query for the power limit.
        """
        
        self.state = limit.get ("StaticState", "false")
        self.limit = limit.get ("StaticLimit", "-1")
        
        if (self.state.upper () == "POWER LIMIT ACTIVE"):
            self.state = "true"
        elif (self.state.upper () == "NO ACTIVE POWER LIMIT"):
            self.state = "false"
            
        self.limit = self.limit.split (" ")[0]
            
    def format (self, parent):
        """
        Format the blade power limit in the XML document.
        
        :param parent: The parent element that will contain the blade power limit.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "isPowerLimitActive", self.state)
        add_element (parent, "powerLimit", self.limit)
        
        return (parent, NO_STATUS)
    
class blade_power_reading:
    """
    Response object for the blad power reading.
    """
    
    def __init__ (self, power):
        """
        Initialize the blade power reading response.
        
        :param power: The result of the system query for the power reading.
        """
        
        self.power = power.get ("PowerReading", "-1")
        
    def format (self, parent):
        """
        Format the blad power reading in the XML document.
        
        :param parent: The parent element that will contain the blade power reading.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "powerReading", self.power)
        
        return (parent, NO_STATUS)
    
class next_boot:
    """
    Response object for blade next boot information.
    """
    
    def __init__ (self, boot):
        """
        Initialize the blade next boot response.
        
        :param boot: The result of the system query for blade next boot information.
        """
        
        self.boot = boot.get ("BootSourceOverrideTarget", "Unknown")
        self.persist = boot.get ("BootSourceOverrideEnabled", "false")
        self.uefi = boot.get ("BootSourceOverrideMode", "false")
        self.instance = "0"
        
        if ("No override" in self.boot):
            self.boot = "NoOverride"
        elif ("PXE" in self.boot):
            self.boot = "ForcePxe"
        elif ("Hard-Drive" in self.boot):
            self.boot = "ForceDefaultHdd"
        elif ("BIOS" in self.boot):
            self.boot = "ForceIntoBiosSetup"
        elif ("Floppy" in self.boot):
            self.boot = "ForceFloppyOrRemovable"
        else:
            self.boot = "Unknown"

        if (self.persist == "Persistent"):
            self.persist = "true"
        else:
            self.persist = "false"
        
        if (self.uefi == "UEFI"):
            self.uefi = "true"
        else:
            self.uefi = "false"
            
    def format (self, parent):
        """
        Format the blade next boot information in the XML document.
        
        :param parent: The parent element that will contain the next boot information.
        
        :return The parent element and a status flag for the response.
        """
        
        add_element (parent, "nextBoot", self.boot)
        add_element (parent, "persistence", self.persist)
        add_element (parent, "uefi", self.uefi)
        add_element (parent, "bootInstance", self.instance)
        
        return (parent, NO_STATUS)