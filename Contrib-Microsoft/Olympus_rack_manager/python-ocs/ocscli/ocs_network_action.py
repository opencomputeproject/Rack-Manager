# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import pre_settings

from utils_print import * 
from ocsaudit_log import *
from controls.utils import *
from argparse import ArgumentParser
from models.ethernet_interface import *


#######################################################
# Network Support functions
#######################################################
def show_service_version():
    try:
        ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                             "version", "")
                   
        info = get_ocsfwversion(raw = True)
        
        if completion_code.cc_key in info.keys():        
            print_response(info)
        else:
            print(info['stdout'])
            return
    
    except Exception,e :
        print "show_service_version - Exception: {0}".format(e)
        return

def show_network_properties(command_args):
    try:
        parser = ArgumentParser(prog = 'show network', description="Manager network information, shows network properties")
            
        subparsers = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
    
        device_displaycommand_options(subparsers)
        
        args = parse_args_retain_case(parser, command_args)

        if args.command == "interface" and not args.ifname:
            parser.print_help()
            sys.exit()
        
        get_rm_cmd =  repr(pre_settings.command_name_enum.get_rm_state)
        if pre_settings.is_get_rm_call == True:
            ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                             "network " + str(args.command)," ".join(command_args[1:]))
            
            show_properties(args)
        else:
            permission = pre_settings.pre_check_manager(get_rm_cmd, 0) 
            
            if (permission == False):
                return
            else:
                ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                             "network " + str(args.command)," ".join(command_args[1:]))
                show_properties(args)
    except Exception, e:
        print "show_network_properties - Exception: {0}".format(e) 
   
def show_properties(args):
    try:
        if args.command == "interface":
            show_interface_byname(args.ifname)           
        elif args.command == "route":
            route = get_management_network()
            print_response(route)        
            
    except Exception, e:
        print "show_properties - Exception: {0}".format(e) 
        
def set_network_interface(command_args):
    """
        Network configuration:
                                 
        Set interface to static IP address
        set network static -i {interface name} -a {IP address} -s {subnetmask} -g {gateway}
        
        Set interface to dhcp
        set network dhcp -i {interface name} -d 
        
        Enable/Disable interface
        set network enable -i {interface name} -e {"0","1"}    
        
    """
    try:
        parser = ArgumentParser(prog = 'set network', description = "Manager network information, configure an interface set to static IP address, set to dhcp, enable and disable an interface.")
            
        subparsers = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
        
        device_set_staticcommand_options(subparsers)
        device_set_dhcpcommand_options(subparsers)
        device_set_statuscommand_options(subparsers)
        set_management_route_options(subparsers)
        
        args = parse_args_retain_case(parser, command_args)
        
        #call pre-chek
        rm_config_cmd = repr(pre_settings.command_name_enum.set_rm_config)
        if pre_settings.is_rm_config_call == True:
            ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                             "network " + str(args.command)," ".join(command_args[1:]))
            set_interface(args)   
        else:  
            verify_permission = pre_settings.pre_check_manager(rm_config_cmd, 0)
            if(verify_permission == False):
                return
            else:
                ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                             "network " + str(args.command)," ".join(command_args[1:]))
                set_interface(args)
    except Exception,e:
        print("Failed to execute set network command\n",e) 
            
def set_interface(args):
    try:
        commandname = args.command
        if not commandname == "route":
            branchId = "chassis"
            branch = "chassis"
            
            eth = get_ethernetinterfaceById(branchId, branch, args.ifname)
    
            action = {}
            action["action"] = commandname
            action["ifname"] = args.ifname
            
            if commandname == "static":
                action["address"] =args.address
                action["subnetmask"] = args.subnetmask
                action["gateway"] = args.gateway
            
            info = eth.doWorks(action)
        else:
            info = set_management_network(args.gateway, args.subnet)
            
        print_response(info)
        
    except Exception, e:
        #call trace log to log exception
        print_response(set_failure_dict(("exception", e),completion_code.failure)) 

def show_all_interfaces():
    """
        Retrieve network information for system and rack manager.      
    """                  
    try:            
        branchId = "chassis"
        branch = "chassis"
                   
        eth = get_ethernetinterfaces(branchId, branch)
        info = eth.get_ethernet_interfaces_list()
      
        print_response(info)
      
    except Exception, e:
        print ("Failed to get network properties",e)        

def show_interface_byname(ifname):
    """
        Retrieve network information for system and rack manager.      
    """                  
    try:            
        branchId = "chassis"
        branch = "chassis"
                   
        eth = get_ethernetinterfaceById(branchId, branch, ifname)
        info = eth.get_cli_ethernet_info()
        
        print_response(info)
      
    except:
        print ("Failed to get network interface,\n usage :\n\t\t show/sh network interface -i {interface name}  ")     

#######################################################
# Network Action Support functions
#######################################################
def device_displaycommand_options(subparsers):   
    display_parser = subparsers.add_parser('interface', help=("Show network interface"))
    requiredNamed = display_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i',  dest='ifname', choices=['eth0','eth1'], help='Inetrface name.',required=True)
    
    subparsers.add_parser('route', help="Show management network route")

def device_set_staticcommand_options(subparsers):
    update_command_parser = subparsers.add_parser('static', help='Run set network interface to static.')   
    requiredNamed = update_command_parser.add_argument_group('required arguments')
     
    requiredNamed.add_argument('-i',  dest='ifname', choices=['eth0','eth1'], required=True, help='Interface name.')
    requiredNamed.add_argument('-a',  dest='address', required=True, help='The IP address to be assigned to this interface.')
    requiredNamed.add_argument('-s',  dest='subnetmask', required=True, help='To assign network mask to an interface')
    
    update_command_parser.add_argument('-g',  dest='gateway', default = "", help='To assign a gateway address to an interface.')
    update_command_parser.add_argument('-b', dest='broadcast', required=False, help='To assign a broadcast address to an interface.')        
       

def device_set_dhcpcommand_options(subparsers):
    update_command_parser = subparsers.add_parser('dhcp', help='Run set network interface to dhcp.')   
    requiredNamed = update_command_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i',  dest='ifname', choices=['eth0','eth1'], required=True, help='Interface name.')
    #requiredNamed.add_argument('-d', '--dhcp', dest='dhcp', required=True, help='To interface DHCP.')  
       
    update_command_parser.add_argument('-g', '--gateway', dest='gateway', required=False, help='To assign a broadcast address to an interface.')   

def device_set_statuscommand_options(subparsers):
    #enable command
    update_status_command_parser = subparsers.add_parser('enable', help='Enable network interface.')   
    requiredNamed = update_status_command_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i',  dest='ifname', choices=['eth0','eth1'], required=True, help='Interface name.')
    
    #disable command
    update_status_command_parser = subparsers.add_parser('disable', help='Disable network interface.')   
    requiredNamed = update_status_command_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i',  dest='ifname', choices=['eth0','eth1'], required=True, help='Interface name.')
    
def set_management_route_options (subparsers):
    parser = subparsers.add_parser ('route', help = "Change the management network route.")
    required = parser.add_argument_group ("required arguments")
    required.add_argument ("-g", dest = "gateway", required = True, help = "The IP address for the gateway of the management network.")
    required.add_argument ("-n", dest = "subnet", required = True, help = "The netmask of the management network as either a dotted quad or number of net bits.")
    
            
         


