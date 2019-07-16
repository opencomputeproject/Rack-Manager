# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import struct
import array
import fcntl
import os
import re
import ctypes
import math
import subprocess
import ocslog
from utils import *
from ocslock import ocs_lock, ocs_unlock, ocslock_t_enum
from netaddr import IPNetwork, IPAddress
from subprocess import CalledProcessError
from ocsfile import ocs_file_write_complete_file
from argparse import ArgumentParser

# From linux sockios.h
SIOCGIFHWADDR  = 0x8927          # Get hardware address    
SIOCGIFADDR    = 0x8915          # get PA address 
         
SIOCGIFNETMASK = 0x891b          # get network PA mask     
SIOCGIFNAME    = 0x8910          # get interface name          
SIOCSIFLINK    = 0x8911          # set interface channel       
SIOCGIFCONF    = 0x8912          # get interface list          
SIOCGIFFLAGS   = 0x8913          # get flags               
SIOCSIFFLAGS   = 0x8914          # set flags               
SIOCGIFINDEX   = 0x8933          # name -> if_index mapping
SIOCGIFCOUNT   = 0x8938          # get number of devices
SIOCGIFBRDADDR = 0x8919    

############################################################################################################
# Network actions Functions 
###########################################################################################################
def display_interface_by_name(if_name):
    """ Display network interface information given device name
    """    
    
    try:
        result = {}
        if findInterfaceName(if_name):
            result["Id"] = if_name
            
            if interface_status(if_name):
                enabled = "Up"
            else:
                enabled = "Down"
                    
            result["State"] = enabled
            result["Health"] = "Ok"
            
            result["MACAddress"] = get_macsocket(if_name)
                        
            Address = get_ip_address(if_name)
                        
            result["IPv4Addresses"] = {
                "Address": Address,
                "SubnetMask": get_subnetmask_ifconfig(if_name),
                "AddressOrigin":get_address_origin(if_name),
                "Gateway":get_default_gateway()
            }   
            
            if get_default_interface() == if_name:
                preferred="True"
            else:
                preferred="False"
            
            ifIPV6 = get_IPV6(if_name).strip()
            
            if ifIPV6:
                ipv6= ifIPV6.split('/')[0]
                ipv6prefix=ifIPV6.split('/')[1]
            else:
                ipv6= ""
                ipv6prefix=""
                
            result["IPv6Addresses"]={
                "Address":ipv6,
                "PrefixLength":ipv6prefix,
                "AddressOrigin":"",
                "AddressState":preferred
            }
    except Exception, e:
        return set_failure_dict("display_interface_by_name - Exception: {0}".format(e), completion_code.failure) 
          
    result[completion_code.cc_key] = completion_code.success  
    return result

def display_cli_interfaces():
    try:
        """ Display all network interface information
        """    
        
        result = {}
        result["Interfaces_list"] = {}
        
        count = 0;
        ifs = list_Interfaces()
        for i in ifs:
            count = count+1
            result["Interfaces_list"].update({str(count):i})
        
        result["Interfaces_count"] = count
        
    except Exception, e:
        return set_failure_dict("display_cli_interfaces - Exception: {0}".format(e), completion_code.failure)
    
    return set_success_dict(result)

def get_command_output(command):
    result = call_network_command(command)
    return result["stderr"] if (result["stderr"]) else result["stdout"] 
    
def call_network_command(command):
    try:
        process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        output, error_msg = process.communicate()
        completion_status = process.wait()
        
        return {'status_code' : completion_status, 'stdout' : output, 'stderr': error_msg}       
    
    except Exception, e:
        ocslog.log_exception()
        return {'status_code' : -1, 'stdout' : output, 'stderr' : e}        

############################################################################################################
# Network interface support Functions 
###########################################################################################################
def validate_ip_address (address, netmask, gateway = None):
    """
    Validate that the provided IP settings are valid.
    
    :param address: The IP address that will be assigned to the interface.
    :param netmask: The subnet mask for the interface.
    :param gateway: The default gateway to use for the system.
    """
    
    ip = IPAddress (address)
    if (not ip.is_unicast () or ip.is_loopback () or ip.is_reserved ()):
        raise ValueError ("IP address is not a valid host address.")
    
    if (not IPAddress (netmask).is_netmask ()):
        raise ValueError ("Subnet mask is not valid.")
    
    subnet = IPNetwork (address, netmask)
    if gateway:
        route = IPNetwork (gateway, netmask)
        if (subnet != route):
            raise ValueError ("Gateway supplied is not on the specified subnet.")
        
def dhcp_client_running (if_name):
    """
    Check if the DHCP client is running for the interface."
    
    :param if_name: The interface to check.
    
    :return True if the client is running or False if it is not.
    """
    
    try:
        subprocess.check_output ("/usr/sbin/ifplugd -c -i {0}".format (if_name),
            stderr = subprocess.STDOUT, shell = True)
        return True
    
    except CalledProcessError:
        return False
    
def stop_dhcp_client (if_name):
    """
    Stop the DHCP client for an interface, if it is running.
    
    :param if_name: The name of the interface to stop the client on.
    """
    
    if (dhcp_client_running (if_name)):
        return call_network_command ("/usr/sbin/ifplugd -Wk -i {0}".format (if_name))
    else:
        return {"status_code" : 0, "stdout" : "", "stderr" : ""}
    
def start_dhcp_client (if_name):
    """
    Start the DHCP client for an interface, if it is not already running.
    
    :param if_name: The name of the interface to start the client on.
    """
    
    if (not dhcp_client_running (if_name)):
        return call_network_command ("/usr/sbin/ifplugd -i {0} -fI -u0 -d2".format (if_name))
    else:
        return {"status_code" : 0, "stdout" : "", "stderr" :""}
    
def network_interface_up (if_name):
    """
    Bring a network interface up.
    
    :param if_name: The name of the interface to bring up.
    """

    return call_network_command ("ifup {0}".format (if_name))

def network_interface_down (if_name):
    """
    Bring a network interface down.
    
    :param if_name: The name of the interface to bring down.
    """

    return call_network_command ("ifdown {0}".format (if_name))

def save_ip_address (if_name, new_config):
    """
    Save the IP address configuration to the interfaces file.
    
    :param if_name: The name of the network interface to configure.
    :param new_config: The set of new configuration parameters to apply to the interface.
    """
    
    interfaces = ""
    with open ("/etc/network/interfaces", "r+") as config:
        look_for = "iface {0}".format (if_name)
        keep = True
        applied = False
        for line in config:
            if ((look_for is not None) and (line.startswith (look_for))):
                if (not applied):
                    interfaces += "".join (new_config)
                    look_for = ("\tup", "\n")
                    keep = False
                    applied = True
                else:
                    interfaces += line
                    look_for = None
                    keep = True
            elif (keep):
                interfaces += line
    
    ocs_file_write_complete_file ("/etc/network/interfaces", interfaces)
        
def set_static_interface (if_name, ip_address, netmask, gateway = None):
    """ 
    Assign a static IP address to a network interface.
    
    :param if_name: The name of the network interface to configure.
    :param ip_address: The IP address to assign to the interface.
    :param netmask: The subnet mask for the interface.
    :param gateway: The default gateway for the system.
    """    
    
    # We only want to allow the gateway to be set on eth0.  The eth1 gateway gets set using
    # set_management_network.
    if (not if_name == "eth0"):
        gateway = None
        
    validate_ip_address (ip_address, netmask, gateway)
    
    ocs_lock (ocslock_t_enum.NET_CONFIG)
    result = {}
    try:
        result = stop_dhcp_client (if_name)
        if (result["status_code"] == 0):
            config = [
                "iface {0} inet static\n".format (if_name),
                "\taddress {0}\n".format (ip_address),
                "\tnetmask {0}\n".format (netmask)
            ]
            if (gateway is not None):
                config.append ("\tgateway {0}\n".format (gateway))
        
            save_ip_address (if_name, config)
            network_interface_down (if_name)
            result = network_interface_up (if_name)
        
    finally:
        ocs_unlock (ocslock_t_enum.NET_CONFIG)
        
    return result
    
def set_dhcp_interface (if_name):
    """
    Use DHCP to assign a dynamic IP address to a network interface.
    
    :param if_name: The name of the network interface to configure.
    """    
    
    ocs_lock (ocslock_t_enum.NET_CONFIG)
    result = {}
    try:
        if (not dhcp_client_running (if_name)):
            result = network_interface_down (if_name)
        else:
            result["status_code"] = 0
            
        if (result["status_code"] == 0):
            save_ip_address (if_name, ["iface {0} inet dhcp\n".format (if_name)])
            result = start_dhcp_client (if_name)
        
    finally:
        ocs_unlock (ocslock_t_enum.NET_CONFIG)
        
    return result        

def enable_network_interface (if_name):
    """
    Enable a network interface.
    
    :param if_name: The network interface to enable.
    """

    ocs_lock (ocslock_t_enum.NET_CONFIG)
    result = {}
    try:
        if (get_address_origin (if_name) == "DHCP"):
            result = start_dhcp_client (if_name)
        else:
            result = network_interface_up (if_name)
            
    finally:
        ocs_unlock (ocslock_t_enum.NET_CONFIG)
        
    return result

def disable_network_interface (if_name):
    """
    Disable a network interface.
    
    :param if_name: The network interface to disable.
    """
    
    ocs_lock (ocslock_t_enum.NET_CONFIG)
    result = {}
    try:
        if (get_address_origin (if_name) == "DHCP"):
            result = stop_dhcp_client (if_name)
        else:
            result = network_interface_down (if_name)
            
    finally:
        ocs_unlock (ocslock_t_enum.NET_CONFIG)
        
    return result
    
def get_macsocket(if_name):
    try:
        ''' Obtain the device's mac address. '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        ifreq = struct.pack('16sH14s', if_name,1, b'\x00'*14)
        
        res = fcntl.ioctl(s.fileno(), SIOCGIFHWADDR, ifreq)
        address = struct.unpack('16sH14s', res)[2]
        mac = struct.unpack('6B8x', address)
        
        result =  ":".join(['%02X' % i for i in mac])
        
        return str(result)
               
    except Exception, e:
        #Log_err(Exception ,e)
        return None 
    
def get_network_mac_address(if_name):
    result = {}
    
    try:
        result["MacAddress"] = get_macsocket(if_name)
            
    except Exception, e:  
        return set_failure_dict("get_mac_address() Exception {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result            
            
def get_network_ip_address(if_name):
    result = {}
    
    try:
        result["IPAddress"] = get_ip_address(if_name)
            
    except Exception, e:  
        return set_failure_dict("get_network_ip_address() Exception {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_network_subnetmask(if_name):
    result = {}
    
    try:
        result["SubnetMask"] = get_subnetmask_ifconfig(if_name)
            
    except Exception, e:  
        return set_failure_dict("get_network_subnetmask() Exception {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_network_ip_address_origin (if_name):
    try:
        return set_success_dict ({"AddressOrigin" : get_address_origin (if_name)})
        
    except Exception as error:
        return set_failure_dict ("get_network_ip_address_origin() Exception: {0}".format (error))

def get_network_gateway():
    result = {}
    
    try:
        result["Gateway"] = get_default_gateway()
            
    except Exception, e:  
        return set_failure_dict("get_network_gateway() Exception {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_network_status(if_name):
    result = {}
    
    try:
        result["InterfaceStatus"] = "Up" if interface_status(if_name) else "Down"
            
    except Exception, e:  
        return set_failure_dict("get_network_status() - Exception: {0}".format(str(e)),completion_code.failure) 
    
    result[completion_code.cc_key] = completion_code.success
    
    return result

def get_subnetmask_ifconfig(if_name):
    interfaceCommand = "/sbin/ifconfig %s | awk '/Mask/{print $4}' "%if_name
    
    output = get_command_output(interfaceCommand)
                
    if output:
        return output.split(':')[1].strip()
    
    return None

def get_mac_ifconfig(if_name):
    interfaceCommand = "/sbin/ifconfig %s | awk '/HWaddr/{print $5}' "%if_name
    
    return get_command_output(interfaceCommand)

def get_IPV6(if_name):
    if_command = "/sbin/ifconfig %s | awk '/inet6/{print $3}' " %if_name
    
    output = get_command_output(if_command)   
    return "%s" %output  

def get_default_gateway():
    """ Returns the default gateway """
    octet_list = []
    gw_from_route = None
    f = open ('/proc/net/route', 'r')
    for line in f:
        words = line.split()
        dest = words[1]
        try:
            if (int (dest) == 0):
                gw_from_route = words[2]
                break
        except ValueError:
            pass
    if not gw_from_route:
        return None 
    
    for i in range(8, 1, -2):
        octet = gw_from_route[i-2:i]
        octet = int(octet, 16)
        octet_list.append(str(octet)) 
    
    gw_ip = ".".join(octet_list)
    
    return gw_ip

def get_physical_interfaces():
    ''' Iterate over all the interfaces in the system. 
        Return physical interfaces (not 'lo', etc).'''
    
    SYSFS_NET_PATH = b"/sys/class/net"
    
    net_files = os.listdir(SYSFS_NET_PATH)
    interfaces = set()
    virtual = set()
    for d in net_files:
        path = os.path.join(SYSFS_NET_PATH, d)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(os.path.join(path, b"device")):
            virtual.add(d)
        interfaces.add(d)

    results = interfaces - virtual 
    return results

def get_ip_address(if_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        res = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                SIOCGIFADDR,  
                struct.pack('256s', if_name[:15]))[20:24])
    except IOError:
        return None
    
    return res

def get_netmask(if_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    ifreq = struct.pack('16sH14s',if_name, socket.AF_INET, b'\x00'*14)
    try:
        res = fcntl.ioctl(s.fileno(), SIOCGIFNETMASK, ifreq)
    except IOError:
        return 0
    netmask = socket.ntohl(struct.unpack('16sH2xI8x', res)[2])

    return 32 - int(round( math.log(ctypes.c_uint32(~netmask).value + 1, 2), 1))

def get_address_origin (if_name):
    origin = ""
    with open ("/etc/network/interfaces") as config:
        interfaces = config.read ()
        match = re.search ("iface {0} inet (\S+)".format (if_name), interfaces)
        if (not match):
            raise RuntimeError ("Could not find interface {0} configuration.".format (if_name))
        
        origin = match.group (1)
        
    if (origin == "dhcp"):
        return "DHCP"
    elif (origin == "static"):
        return "Static"
    else:
        raise RuntimeError ("Unknown address origin setting {0}".format (origin))

def get_all_interfaces():
    ''' Iterate over all the interfaces in the system. 
        Return all interfaces including virtual. ( 'lo', etc).'''
    max_possible = 128  
    
    bytes = max_possible * 32
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    names = array.array('B', '\0' * bytes)
    
    outbytes = struct.unpack('iL', 
        fcntl.ioctl( s.fileno(), SIOCGIFCONF,  struct.pack('iL', bytes, names.buffer_info()[0]))
        )[0]
    namestr = names.tostring()
    lst = []
    
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split('\0', 1)[0]
        ip   = namestr[i+20:i+24]
        lst.append((name, ip))
        
    return lst

def list_Interfaces():
    ''' Return a list of the names of the interfaces. '''
    return [br for br in get_physical_interfaces()]

def findInterfaceName(if_name):
    for br in get_physical_interfaces():
        if if_name == br:
            return br
    return None

def get_default_interface():
    """ Returns the default interface """
    default_if=''
    
    f = open ('/proc/net/route', 'r')
    for line in f:
        words = line.split()
        dest = words[1]
        try:
            if (int (dest) == 0):
                default_if = words[0]
                break
        except ValueError:
            pass
    return default_if

def interface_status(if_name):
    """ Return True if the interface is up, False otherwise
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ifreq = struct.pack('16sh', if_name, 0)
    flags = struct.unpack('16sh', fcntl.ioctl(s.fileno(), SIOCGIFFLAGS, ifreq))[1]

    # Set new flags
    if flags & 0x1:
        return True
    else:
        return False

mgmt_route_regex = "\/sbin\/ip route add (\d+\.\d+\.\d+\.\d+\/\d+) via (\d+\.\d+\.\d+\.\d+)"
    
def get_management_network ():
    """
    Get the route to get to the management network of the rack.
    
    :return Standard completion information with the subnet and gateway.
    """
    
    try:
        with open ("/etc/network/interfaces") as config:
            interfaces = config.read ()
            match = re.search (mgmt_route_regex, interfaces)
            
            if (not match):
                return set_failure_dict ("No management network gateway could be found.")
            
            return set_success_dict ({
                "Management Network" : IPNetwork (match.group (1)),
                "Management Gateway" : IPAddress (match.group (2))
            })
    
    except Exception as error:
        return set_failure_dict ("get_management_network_gateway() Exception: {0}".format (error))
            
def set_management_network (gateway, netmask):
    """
    Set the route to access the management network of the rack.
    
    :param gateway: The IP address of the gateway for the network (the management switch).
    :param netmask: The subnet mask for the complete management network.
    
    :return Standard completion information.
    """
    
    result = {}
    try:
        network = IPNetwork ("{0}/{1}".format (gateway, netmask))
        route = "/sbin/ip route add {0}/{1} via {2}".format (
            network.network, network.prefixlen, gateway)
        
        ocs_lock (ocslock_t_enum.NET_CONFIG)
        subprocess.check_output (route, shell = True, stderr = subprocess.STDOUT)
        
        interfaces = ""
        with open ("/etc/network/interfaces", "r+") as config:
            interfaces = config.read ()
            interfaces = re.sub (mgmt_route_regex, route, interfaces)
        
        ocs_file_write_complete_file ("/etc/network/interfaces", interfaces)
            
        result = set_success_dict ()
    
    except CalledProcessError as error:
        result = set_failure_dict (error.output.strip ())
        
    except Exception as error:
        result = set_failure_dict ("change_system_route() Exception: {0}".format (error))

    ocs_unlock (ocslock_t_enum.NET_CONFIG)
    return result

if __name__ == "__main__":
    parser = ArgumentParser ()
    parser.add_argument ("-u", "--up", help = "The network interface to bring up.")
    parser.add_argument ("-d", "--down", help = "The network interface to bring down.")
    
    args = parser.parse_args ()
    result = {"status_code" : 0}
    if (args.up):
        result = enable_network_interface (args.up)
    if (args.down):
        result = disable_network_interface (args.down)
        
    if (result["status_code"] != 0):
        print result
        
    exit (result["status_code"])