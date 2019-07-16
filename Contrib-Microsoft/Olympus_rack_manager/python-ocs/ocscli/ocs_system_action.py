# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import os
import sys
import argparse
import textwrap
import pre_settings

from models.fpga import *
from controls.utils import *
from ocsaudit_log import *
from models.blade_system import *
from argparse import ArgumentParser
from controls.bladeinfo_lib import *
from utils_print import ocsprint, print_response, remove_empty_dict


#######################################################
# System Show Support functions
#######################################################

def system_show_commands(command_args):
    try:
        parser = ArgumentParser(prog = 'show system', description = "Rack manager: server management show commands")
            
        subparser = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
        
        system_showcommand_options(subparser)
        
        args = parse_args_retain_case(parser, command_args)

        if (args.serverid < 1) or (args.serverid > 48):
            error_info = set_failure_dict(("server-id invalid (%d). Expected serverid 1 to 48." % args.serverid),completion_code.failure)
            print_response(error_info) 
            sys.exit()
            
        if args.command == "port":
            get_rm_cmd =  repr(pre_settings.command_name_enum.get_rm_state)
            permission = pre_settings.pre_check_manager(get_rm_cmd, 0)
        else:
            get_server_cmd = repr(pre_settings.command_name_enum.get_blade_state)
            permission = pre_settings.pre_check_manager(get_server_cmd, args.serverid)

        if (permission == False):
            return
        else:
            ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                                     "system " + str(args.command)," ".join(command_args[1:]))
            show_system_commands(args)
            
    except Exception, e:
        #call trace log to log exception
        #OcsPrint("Failed to execute show system command\n",e)
        error_info = set_failure_dict(("show system command, Exception:",e),completion_code.failure)
        print_response(error_info) 
            
def system_set_commands(command_args):
    try:
        parser = ArgumentParser(prog = 'set system', description="Rack manager: server management set commands.")
            
        subparser = parser.add_subparsers(title="Commands", metavar='', dest='command')
                
        system_setcommand_options(subparser)
                
        args = parse_args_retain_case(parser, command_args)
                
        if (args.serverid < 1) or (args.serverid > 48):
            error_info = set_failure_dict(("server-id invalid (%d). Expected serverid 1 to 48." % args.serverid),completion_code.failure)
            print_response(error_info) 
            sys.exit()

        if args.command == "port":
            set_rm_cmd =  repr(pre_settings.command_name_enum.set_rm_state)
            permission = pre_settings.pre_check_manager(set_rm_cmd, 0)
        else:
            set_server_cmd = repr(pre_settings.command_name_enum.set_blade_state)
            permission = pre_settings.pre_check_manager(set_server_cmd, args.serverid) 
        
        if (permission == False):
            return
        else:
            ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                                 "system " + str(args.command)," ".join(command_args[1:]))
            set_system_command(args)     
            
    except Exception, e:
        #call trace log to log exception
        error_info = set_failure_dict("system_set_commands Exception: {0}".format(str(e)), completion_code.failure)
        print_response(error_info) 
        
def system_showcommand_options(subparsers):
    # Show system type command
    systemtype_parser = subparsers.add_parser("type", help = "This command shows system type")
    systemtype_parser.add_argument("-i", dest = "serverid", type = int, help = "server-id (1, 48)", required = True)
    
    # A info command
    systeminfo_parser = subparsers.add_parser('info', help=("This command shows server information"))
    requiredNamed = systeminfo_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help="server-id (1 to 48)", required=True)
    
    # A health command
    health_parser = subparsers.add_parser('health', help = "This command shows server health.")
    requiredNamed = health_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest = 'serverid', metavar = 'server-id', type = int, help = "server-id (1 to 48)", required = True)
    health_parser.add_argument('-s', "--server", action = "store_true", help = "Show server information (slotid, type, state)")
    health_parser.add_argument('-m', "--memory", action = "store_true", help = "Show server memory(Dimm) information")
    health_parser.add_argument('-c', "--cpu", action = "store_true", help = "Show server CPU information")
    health_parser.add_argument('-p', "--pcie", action = "store_true", help = "Show server PCIe information")
    health_parser.add_argument('-a', "--asset", action = "store_true", help = "Show server FRU info")
    health_parser.add_argument('-f', "--fan", action = "store_true", help = "Show server fan info")
    health_parser.add_argument('-t', "--temp", action = "store_true", help = "Show server temperature sensor info")
    health_parser.add_argument('-r', "--sensor", action = "store_true", help = "Show server sensor info")
    health_parser.add_argument('-n', "--nvme", action = "store_true", help = "Show server nvme info")
    
    # A Fru command
    systemfru_parser = subparsers.add_parser('fru', help=("This command shows server fru"))
    requiredNamed = systemfru_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help="server-id (1 to 48)", required=True)
    
    # NVMe Status command
    nvme_parser = subparsers.add_parser("nvme", help = "This command shows NVMe status")  
    nvme_parser.add_argument('-i', dest = 'serverid', metavar = 'server-id', type = int, help = 'server-id (1 to 48)', required = True)
    
    # A gettpmphysicalpresence command
    tpmphysicalpresence_parser = subparsers.add_parser('tpm', help='This command shows physical prsence of TPM')
    present_subparser = tpmphysicalpresence_parser.add_subparsers(help = "tpmaction", dest = "tpm")
    show_present_subparser = present_subparser.add_parser("presence", help = "This command shows physical prsence of TPM")
    requiredNamed = show_present_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A getnextboot command
    getnextboot_parser = subparsers.add_parser('nextboot', help=("Shows the pending boot order to be applied the next time server boots"))
    requiredNamed = getnextboot_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help="server-id (1 to 48)", required=True) 
    
    # A getdefaultpowerstate command
    default_parser = subparsers.add_parser('default', help='This command shows default server power state')
    default_state_subparser = default_parser.add_subparsers(help = "defaultaction", dest = "default")
    show_default_subparser = default_state_subparser.add_parser("power", help = "This command shows server default powerstate on/off")
    requiredNamed = show_default_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A getstate command
    get_server_state_parser = subparsers.add_parser('state', help='This command shows server state')
    requiredNamed = get_server_state_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A attentionledstatus command
    attentionledstatus_parser = subparsers.add_parser('led', help = "This command shows server attention led status.")
    requiredNamed = attentionledstatus_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A getpowerstate command
    port_parser = subparsers.add_parser('port', help='This command shows port state')
    requiredNamed = port_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A getportpresencestate command
    get_port_presence_parser = subparsers.add_parser('presence', help='Shows server port presence state (True || False)')
    requiredNamed = get_port_presence_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    # A getpowerstate command
    readserverlog_parser = subparsers.add_parser('log', help='This command reads system log entries')
    read_subparser = readserverlog_parser.add_subparsers(help = "log action", dest = "log")
    read_log_subparser = read_subparser.add_parser("read", help = "This command reads the server logs")
    requiredNamed = read_log_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)

    # A readlogwithtimestamp command
    readserverlogwithtimestamp_parser = read_subparser.add_parser('timestamp', help=("Reads the server log details based on date timestamp"))
    requiredNamed = readserverlogwithtimestamp_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help="server-id (1 to 48)", required=True)
    requiredNamed.add_argument('-s', dest='starttime', metavar='starttimestamp', help="Date time- start time stamp ex: M/D/Y-HH:MM:SS", required=True)  
    requiredNamed.add_argument('-e', dest='endtime', metavar='endtimestamp', help="Date time- end time stamp ex: M/D/Y-HH:MM:SS", required=True)
    
    # A getbiosconfig command
    getserverbiosconfig_parser = subparsers.add_parser('bios', help=("Shows the biosconfig or bioscode details"))
    config_parser = getserverbiosconfig_parser.add_subparsers(help = "config details", dest = "bios")
    bios_config_subparser = config_parser.add_parser("config", help = "This command shows current,chosen and available bios configurations")
    requiredNamed = bios_config_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i',  dest='serverid', metavar='server-id', type =int, help="server-id (1 to 48)", required=True) 
    
    # A getbioscode command
    getserverbioscode_parser = config_parser.add_parser('code', help=("This command shows bios code"))
    requiredNamed = getserverbioscode_parser.add_argument_group('required arguments')            
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    requiredNamed.add_argument('-v', dest='version', choices=['current','previous'], help='serverid version(current or previous )', default='current')
    
    # FPGA Display Commands
    fpga_parser = subparsers.add_parser("fpga", help = "This command shows FPGA info")
    
    parent_parser = argparse.ArgumentParser(add_help = False)
    parent_parser.add_argument('-i', dest = 'serverid', metavar = 'server-id', type = int, help = 'server-id (1 to 48)', required = True)

    fpga_subparser = fpga_parser.add_subparsers(help = "FPGA display commands", dest = "fpga")
    fpga_subparser.add_parser('health', help = "This command shows FPGA health", parents = [parent_parser])
    fpga_subparser.add_parser('mode', help = "This command shows bypass mode setting", parents = [parent_parser])
    fpga_subparser.add_parser('temp', help = "This command shows temperature in Celsius", parents = [parent_parser])
    fpga_subparser.add_parser('i2cversion', help = "This command shows I2C version", parents = [parent_parser])
    fpga_subparser.add_parser('assetinfo', help = "This command shows FRU contents", parents = [parent_parser])

    # OcsPower Display Commands
    ocspower_parser = subparsers.add_parser("power", help = "This command shows OcsPower info")
    
    parent_parser = argparse.ArgumentParser(add_help = False)
    parent_parser.add_argument('-i', dest = 'serverid', metavar = 'server-id', type = int, help = 'server-id (1 to 48)', required = True)

    ocspower_subparser = ocspower_parser.add_subparsers(help = "OcsPower display commands", dest = "ocspower")
    ocspower_subparser.add_parser('limit', help = "This command shows power limit", parents = [parent_parser])
    ocspower_subparser.add_parser('reading', help = "This command shows power reading", parents = [parent_parser])
    ocspower_subparser.add_parser('alert', help = "This command shows alert policy", parents = [parent_parser])
    ocspower_subparser.add_parser('throttle', help = "This command shows throttle statistics", parents = [parent_parser])
    
    # PSU Display Commands
    psu_parser = subparsers.add_parser('psu', help='This command executes PSU display commands')
    parent_parser = argparse.ArgumentParser(add_help = False)
    requiredNamed = parent_parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
    
    psu_subparser = psu_parser.add_subparsers(help = "PSU dispay", dest = "psu")
    
    read_parser = psu_subparser.add_parser("info", help = "This command reads the psu info", parents = [parent_parser])    
    read_parser.add_argument('-p', dest='phase', choices=['0','1','2'], help='psu info with phase options defult show all phase details',default = '',required = False)
    
    psu_subparser.add_parser("battery", help = "This command shows psu battery presence", parents = [parent_parser])
    psu_subparser.add_parser("update", help = "This command shows psu firmware update status", parents = [parent_parser])
        
    psu_version_subparser = psu_subparser.add_parser("version", help = "This command shows the psu version", parents = [parent_parser])
    requiredNamed = psu_version_subparser.add_argument_group('required arguments')            
    requiredNamed.add_argument('-v', dest='vertype', choices=['fw','bootloader'], help='psu versions(fw or bootloader)', default='fw')
    
    # Datasafe Display Commands
    datasafe_parser = subparsers.add_parser('datasafe', help='This command shows datasafe (NVDIMM, PCIe) settings')
    policy_subparser = datasafe_parser.add_subparsers(help = "datasafe policy", dest = "datasafe")
    show_policy_subparser = policy_subparser.add_parser("policy", help = "This command show datasafe (NVDIMM, PCIe) policy settings")
    requiredNamed = show_policy_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', dest='serverid', metavar='server-id', type =int, help='server-id (1 to 48)', required=True)
       
def system_setcommand_options(subparsers):
    # IPMITool command
    ipmitool_parser = subparsers.add_parser("cmd", help = "IPMITool passthrough")
    ipmitool_parser.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    ipmitool_parser.add_argument("-c", dest = "ipmicmd", type = str, nargs = "*", help = "IPMITool command", required = True)
     
    # A settpmphysicalpresence command
    tpmphysicalpresence_parser = subparsers.add_parser('tpm', help='TPM physical presence')
    present_subparser = tpmphysicalpresence_parser.add_subparsers(help = "tpmaction", dest = "tpm")
    set_present_subparser = present_subparser.add_parser("presence", help = "This command sets TPM physical prsence")
    requiredNamed = set_present_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-p', dest='presence', metavar='presence', type =int, choices=[1,0], help="physical presence 0 (set to false) or 1 (set to true)", required=True)
    
    # A setnextboot command
    setnextboot_parser = subparsers.add_parser('nextboot', help='This command sets server next boot type')
    requiredNamed = setnextboot_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-t',  dest='boottype', metavar='boot-type', choices = ['none','pxe','disk','bios','floppy'],
                                     help = textwrap.dedent(''' \
                                         boot-type:\t\t\t\t\n
                                            1. none: No override\t\t\t\t\n;
                                            2. pxe:Force PXE boot;
                                            3. disk: Force boot from default Hard-drive;
                                            4. bios: Force boot into BIOS Setup;
                                            5.floppy: Force boot from Floppy/primary removable media'''), required=True)
    requiredNamed.add_argument('-m', dest='bootmode', metavar='boot-mode', type=int, choices = [0,1], help="Boot mode 0- Legacy or 1- UEFI", required = True)
    requiredNamed.add_argument('-p', dest='persistent', metavar='is-persistent',type=int, choices = [0,1], help="0- Non-persistent or 1- Persistent", required = True)
    
        
    # A setdefaultpowerstate command
    default_parser = subparsers.add_parser('default', help='This command sets default power state')
    default_state_subparser = default_parser.add_subparsers(help = "defaultaction", dest = "default")
    set_default_subparser = default_state_subparser.add_parser("power", help = "This command sets server default powerstate on/off")
    requiredNamed = set_default_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-s', dest = 'state', metavar = 'power-state', choices = ["on","off"], help = "Default power state (on, off)", required = True)
    
    # A seton command
    setserveron_parser = subparsers.add_parser('on', help='This command sets server soft power ON')
    requiredNamed = setserveron_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A setoff command
    setserveroff_parser = subparsers.add_parser('off', help='This command sets server soft power OFF')
    requiredNamed = setserveroff_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A Setporton / off command
    port_parser = subparsers.add_parser('port', help='This command sets port power state')
    set_subparser = port_parser.add_subparsers(help = "portaction", dest = "port")
    port_on_subparser = set_subparser.add_parser("on", help = "This command turns the AC outlet power ON for the server")
    requiredNamed = port_on_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A setpoweroff command
    setportoff_parser = set_subparser.add_parser('off', help='This command turns the AC outlet power OFF for the server')
    requiredNamed = setportoff_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A resetserver command
    powercycle_parser = subparsers.add_parser('reset', help='This command resets server')
    requiredNamed = powercycle_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A Setledon / off command
    led_parser = subparsers.add_parser('led', help='This command sets server attention LED state')
    set_led_subparser = led_parser.add_subparsers(help = "ledaction", dest = "led")
    led_on_subparser = set_led_subparser.add_parser("on", help = "This command sets server attention led on")
    requiredNamed = led_on_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A setpoweroff command
    led_off_parser = set_led_subparser.add_parser('off', help='This command sets server attention led off')
    requiredNamed = led_off_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)

    # A clearlog command
    clearserverlog_parser = subparsers.add_parser('log', help='This command clears system logs')
    clear_subparser = clearserverlog_parser.add_subparsers(help = "log action", dest = "log")
    clear_log_subparser = clear_subparser.add_parser("clear", help = "This command clears system logs")
    requiredNamed = clear_log_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    # A setbiosconfig
    setserverbiosconfig_parser = subparsers.add_parser('bios', help=("This command executes BIOS action commands"))
    config_parser = setserverbiosconfig_parser.add_subparsers(help = "BIOS action command", dest = "bios")
    setserverbiosconfig_parser = config_parser.add_parser("config", help = "This command sets the server bios configuration")    
    requiredNamed = setserverbiosconfig_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-j',  dest='majorconfig', metavar='major-config', type =int, required=True)
    requiredNamed.add_argument('-n',  dest='minorconfig', metavar='minor-config', type =int, required=True)
    
    # FPGA Action Commands
    fpga_parser = subparsers.add_parser("fpga", help = "This command executes FPGA action commands")
        
    parent_parser = argparse.ArgumentParser(add_help = False)
    parent_parser.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)

    fpga_subparser = fpga_parser.add_subparsers(help = "FPGA action commands", dest = "fpga")
        
    bypass_parser = fpga_subparser.add_parser ("bypass", help = "This command sets bypass mode setting")
    bypass_subparser = bypass_parser.add_subparsers (help = "Bypass mode setting", dest = "bypass")
    bypass_subparser.add_parser ("enable", help = "This command enables bypass mode", parents = [parent_parser])
    bypass_subparser.add_parser ("disable", help = "This command disables bypass mode", parents = [parent_parser])
    
    # OcsPower Action Commands
    ocspower_parser = subparsers.add_parser("power", help = "This command is used to control power limit and power alerts")
    
    parent_parser = argparse.ArgumentParser(add_help = False)
    parent_parser.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)

    ocspower_subparser = ocspower_parser.add_subparsers(help = "OcsPower action commands", dest = "ocspower")
    
    limit_parser = ocspower_subparser.add_parser ("limit", help = "This command sets the static power limit")
    limit_subparser = limit_parser.add_subparsers (help = "Limit on/off", dest = "limit")
    limit_subparser.add_parser ("on", help = "This command enables power limit", parents = [parent_parser])
    limit_subparser.add_parser ("off", help = "This command disables power limit", parents = [parent_parser])
    
    limitvalue_parser = limit_subparser.add_parser("value", help = "This command sets the static power limit value", parents = [parent_parser])
    limitvalue_parser.add_argument('-l',  dest = 'powerlimit', type = int, help = 'powerlimit in watts', required = True) 
    
    ocspower_alert = ocspower_subparser.add_parser('alert', help = "This command sets the alert policy", parents = [parent_parser])
    ocspower_alert.add_argument('-p',  dest = 'powerlimit', type = int, help = 'power limit in watts', required = True)
    ocspower_alert.add_argument('-e',  dest = 'alertaction', metavar='alert-action', type =int, choices=range(0,3), help='alert action, 0:nothing, 1:throttle, 2:fast throttle', required=True)
    ocspower_alert.add_argument('-r',  dest = 'remediationaction', metavar='remediation-action', type =int, choices=range(0,3), help='remediation action, 0:nothing, 1:remove limit and re-arm alert, 2:re-arm alert', required=True)
    ocspower_alert.add_argument('-f',  dest = 'throttleduration', metavar='throttle-duration', type =int, help='fast throttle duration in milliseconds', required=False)
    ocspower_alert.add_argument('-d',  dest = 'removedelay', metavar='remove-delay', type =int, help='auto remove power limit delay in seconds', required=False)
    
    # PSU Action commands
    psu_parser = subparsers.add_parser('psu', help='This command executes PSU action commands')
    parent_parser = argparse.ArgumentParser(add_help = False)
    requiredNamed = parent_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    
    psu_subparser = psu_parser.add_subparsers(help = "PSU action commands", dest = "psu")
    psu_clear_subparser = psu_subparser.add_parser("clear", help = "This command clears psu faults", parents = [parent_parser])
    psu_clear_subparser.add_argument('-p', dest='phase', choices=['0','1','2'], help='phases (0 {phase 1}, 1 {phase 2}, 2 {phase 3}, {default all phases})', default='',required= False)
    psu_subparser.add_parser("battery", help = "PSU battery test command", parents = [parent_parser])
    
    psu_fwupdate_subparser = psu_subparser.add_parser("update", help = "The firmware update for the server PSU firmware", parents = [parent_parser])
    requiredNamed = psu_fwupdate_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument('-f', dest='file', help='update file name', required=True)
    requiredNamed.add_argument('-t', dest='type', type = int, choices = [0,1,2], help = "Type of the firmware image {0: bootloader , 1:Image_A, 2: Image_B}", required = True)

    # Datasafe set policy
    setdatasafepolicy_parser = subparsers.add_parser('datasafe', help=("sets the server datasafe (NVDIMM, PCIe) policy settings"))
    config_parser = setdatasafepolicy_parser.add_subparsers(help = "policy details", dest = "datasafe")
    setdatasafepolicy_parser = config_parser.add_parser("policy", help = "sets the server datasafe policy configuration")    
    requiredNamed = setdatasafepolicy_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-t',  dest='triggertype', metavar='trigger-type', type =int, choices=range(0,4),help='Disable (0) ADR (1) SMI (2) CPLD (3) ADR/SMI (4)', required=True)
    requiredNamed.add_argument('-n',  dest='nvdimmbackupdelay', metavar='nvdimm-backup-delay', type =int, choices=range(0,255),help='Delay in seconds (0 to 255)', required=True)
    requiredNamed.add_argument('-p',  dest='pcieresetdelay', metavar='pcie-reset-delay', type =int, choices=range(0,255),help='Delay in seconds (0 to 255)', required=True)

    # Remote media mount command
    rmedia_parser = subparsers.add_parser('rmedia', help='System remote media command')
    rmedia_parser_subparser = rmedia_parser.add_subparsers(help = "rmediaaction", dest = "rmedia")
    rmedia_mount_subparser = rmedia_parser_subparser.add_parser("mount", help = "This command mounts remote media on the server")
    requiredNamed = rmedia_mount_subparser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
    requiredNamed.add_argument('-n',  dest='rmediaimagename', metavar='rmedia-image-name', help='Remote media image name', required=True)
    
    # Remote media unmount command
    rmedia_umount_parser = rmedia_parser_subparser.add_parser('unmount', help='This command unmounts remote media from the server')
    requiredNamed = rmedia_umount_parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-i", dest = "serverid", type = int, help = "server-id (1:48)", required = True)
        
def show_system_commands(args):   
    try:
        computersystem = getsystem(args.serverid)
        commandname = args.command  
        
        info = {}
        
        if commandname == "info":       
            info = computersystem.getSystem()
        elif commandname == "health":
            if args.memory == False and args.cpu == False and args.pcie == False and args.asset == False and args.temp == False and \
                args.fan == False and args.sensor == False and args.server == False and args.nvme == False:
                info = computersystem.get_server_data()
            else:
                info = blade_health(args)
        elif commandname == "fru":
            info = computersystem.get_fru_details()
        elif commandname == "tpm":
            info = computersystem.get_tpm_presence()
        elif commandname == "nextboot":
            info = computersystem.get_next_boot()
        elif commandname == "default":
            info =  computersystem.get_default_power_state()
        elif commandname == "state":
            info = computersystem.get_system_state()
        elif commandname == "port":
            info = computersystem.get_system_power_state()
        elif commandname == "presence":
            info = computersystem.get_system_port_presence()              
        elif commandname == "bios" and args.bios.lower() == "code":
            info = computersystem.get_system_bioscode(args.version)
        elif commandname == 'led':
            info = computersystem.get_system_led_status()
        elif commandname == "nvme":
            info = computersystem.get_nvme()
        elif commandname == "type":
            info = get_system_type(args.serverid)
        elif commandname == "bios" and args.bios.lower() == "config":
            impi_code = ''
            info = computersystem.get_system_biosconfig()
            
            if completion_code.ipmi_code in info.keys():
                impi_code = info["IPMI Completion Code"]
            
            if impi_code == "FF":
                return set_failure_dict("Not Configured", completion_code.failure)
            else:
                print_biosconfig(info)
            return
        elif commandname == "log" and args.log.lower() == "read":
            info = computersystem.read_system_log()
            print (info)
            print(completion_code.cc_key + ":" + completion_code.success)
            return
        elif commandname == "log" and args.log.lower() == "timestamp":
            info = computersystem.read_system_log_timestamp(args.starttime, args.endtime)
            print (info)
            print(completion_code.cc_key + ":" + completion_code.success)
            return
        
        elif commandname == "fpga":
            fpga = get_fpga(args.serverid)
            
            request = {}
            
            request["action"] = args.fpga.lower()
            request["mode"] = "display"
                
            info = fpga.doWorks(request)
                    
        elif commandname == "power":            
            request = {}
            
            request["action"] = "system" + args.ocspower.lower()

            info = system_ocspower_display(args.serverid, request)   

        elif commandname == "psu":            
            request = {}
            
            request["action"] = commandname + args.psu.lower()
            
            if args.psu == "read":
                request["phase"] = args.phase
                        
            if args.psu == "version":
                request["version"] = args.vertype
            
            info = system_ocspower_display(args.serverid, request)   
                          
        elif commandname == "datasafe":
            info = computersystem.get_datasafe_policy()
            
        else:
            ocsprint("Command not found", commandname)
            
        print_response(info)
        
    except Exception, e:
        #call trace log to log exception
        error_info = set_failure_dict("show_system_commands({0}) - Exception: {1}".format(commandname, e), completion_code.failure)
        print_response(error_info) 
        
def blade_health(args):
    try:
        completionstate = True
        
        computersystem = getsystem(args.serverid)
        
        serverhealth = {}
        serverhealth["Server Information"] = {}
        serverhealth["CPU Information"] = {}
        serverhealth["Memory Information"] = {}   
        serverhealth["PCIE Information"] = {}     
        serverhealth["Temperature Information"] = {}
        serverhealth["FRU Information"] = {}
        serverhealth["Fan Information"] = {}
        serverhealth["Sensor Information"] = {}
        serverhealth["NVME Information"] = {}  
        
        if(args.memory):
            memory = computersystem.get_memory_deatils()
            if completion_code.cc_key in memory.keys(): 
                value = memory.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
                    
            serverhealth["Memory Information"] = memory
        
        if(args.cpu):
            cpu = computersystem.get_cpu_details()
            if completion_code.cc_key in cpu.keys(): 
                value = cpu.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["CPU Information"] = cpu
        
        if (args.pcie):
            pcie = computersystem.get_pcie_details()
            if completion_code.cc_key in pcie.keys(): 
                value = pcie.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["PCIE Information"] = pcie
            
        if (args.asset):
            asset = computersystem.get_fru_details()
            if completion_code.cc_key in asset.keys(): 
                value = asset.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["FRU Information"] = asset
        
        if (args.fan):
            fan = computersystem.get_fan_details()
            if completion_code.cc_key in fan.keys(): 
                value = fan.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["Fan Information"] = fan
        
        if (args.temp):
            temp = computersystem.get_temperature_details()
            if completion_code.cc_key in temp.keys(): 
                value = temp.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["Temperature Information"] = temp
        
        if (args.sensor):
            sensor = computersystem.get_sensor_details()
            if completion_code.cc_key in sensor.keys(): 
                value = sensor.pop(completion_code.cc_key,None)                        
                if value == completion_code.failure:
                    completionstate &= False 
            serverhealth["Sensor Information"] = sensor
        
        if (args.server):
            server = computersystem.get_server_details()
            if completion_code.cc_key in server.keys(): 
                value = server.pop(completion_code.cc_key,None)      
                if value.lower().strip() == completion_code.failure.lower().strip():
                    completionstate &= False 
            serverhealth["Server Information"] = server
            
        if (args.nvme):
            nvme = computersystem.get_nvme()
            if completion_code.cc_key in nvme.keys(): 
                value = nvme.pop(completion_code.cc_key,None)      
                if value.lower().strip() == completion_code.failure.lower().strip():
                    completionstate &= False 
            serverhealth["NVME Information"] = nvme
        
        health = remove_empty_dict(serverhealth)
            
        if completionstate:
            set_success_dict(health)
        else:
            health[completion_code.cc_key] = completion_code.failure
        
        return health
    
    except Exception, e:
        return set_failure_dict("blade_health() Exception {0}".format(e))

def set_system_command(args):
    try:       
        commandname = ""  
        computersystem = getsystem(args.serverid) 

        if args.command == "port":
            commandname = args.command + args.port.lower()
        elif args.command == "led":
            commandname = args.command + args.led.lower()
        elif args.command == "default":
            commandname = args.command + args.default.lower()
        elif args.command == "tpm":
            commandname = args.command + args.tpm.lower()
        elif args.command == "log":
            commandname = args.log + args.command.lower()
        elif args.command == "bios":
            commandname = args.command + args.bios.lower()
        elif args.command == "datasafe":
            commandname = args.command + args.datasafe.lower()
        elif args.command == "rmedia":
            commandname = args.command + args.rmedia.lower()
        else:
            commandname = args.command

        action = {}
        
        action["action"] = commandname
        
        if commandname == "tpmpresence":
            action["presence"] = args.presence
        elif commandname == "nextboot":
            action["boottype"] = args.boottype
            action["bootmode"] = args.bootmode
            action["ispersist"] = args.persistent
        elif commandname == "defaultpower":
            action["powerstate"] = 1 if args.state == "on" else 0
        elif commandname == "biosconfig":
            action["action"] = commandname
            action["major"] = args.majorconfig
            action["minor"] = args.minorconfig
        elif commandname == "power" and args.ocspower.lower() == "limit" and args.limit.lower() == "value":
            action["powerlimit"] = args.powerlimit
        elif commandname == "power" and args.ocspower.lower() == "alert":
            action["powerlimit"] = args.powerlimit
            action["alertaction"] = args.alertaction
            action["remediationaction"] = args.remediationaction
            action["throttleduration"] = args.throttleduration
            action["removedelay"] = args.removedelay
        elif commandname == "datasafepolicy":
            action["triggertype"] = args.triggertype
            action["nvdimmbackupdelay"] = args.nvdimmbackupdelay
            action["pcieresetdelay"] = args.pcieresetdelay
        elif commandname == "rmediamount":
            action["rmediaimagename"] = args.rmediaimagename
        elif commandname == "cmd":
            action["ipmicmd"] = args.ipmicmd
                
        if commandname == "fpga":
            fpga = get_fpga(args.serverid)
                        
            action["action"] = args.bypass.lower() + args.fpga.lower()
            action["mode"] = "action"
                
            info = fpga.doWorks(action)
                    
        elif commandname == "power":                        
            if args.ocspower == "limit":
                action["action"] = "system" + args.ocspower.lower() + args.limit.lower()
            else:
                action["action"] = "system" + args.ocspower.lower()
            
            info = system_ocspower_action(args.serverid, action)
            
        elif commandname == "psu":            
            action["action"] = commandname + args.psu.lower()
                        
            if args.psu == "clear":
                action["phase"] = args.phase
            if args.psu == "update":
                action["file"] = args.file
                action["type"] = args.type
            
            info = system_ocspower_action(args.serverid, action)
            
        else:
            info = computersystem.doWorks(action)   
        
        if commandname == "clearlog":
            print(info)
            print(completion_code.cc_key + ":" + completion_code.success)
            return
        '''if commandname == "biosconfig":
            print_response(info)
            return'''

        print_response(info)
        
    except Exception, e:
        #call trace log to log exception
        error_info = set_failure_dict(("Exception to set system %s:"%commandname, e), completion_code.failure)
        print_response(error_info) 

def print_biosconfig(d, indent=0):
    """
        print response from the command.    
    """
    if completion_code.cc_key in d:
        code = d.pop(completion_code.cc_key, None)  
        print_biosconfig(d) 
        output = ('\t' * (indent+1)+"{0}: {1}".format(completion_code.cc_key, code))
        print (output)
         
    else:    
        for k, v in d.iteritems():
            if isinstance(v, dict):
                output=  ('\t' * (indent+1)+"{0} : ".format(k))
                print (output)
                print_biosconfig(v, indent+1)
            else:
                output=  '\t' * (indent+1)+"{0} : {1}".format(k, v)
                print (output)    
            

