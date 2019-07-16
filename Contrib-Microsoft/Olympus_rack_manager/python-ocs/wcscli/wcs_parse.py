# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import os
import sys
import pre_settings

from wcs_help import *
from wcs_action import *
from ocsaudit_log import *
from argparse import ArgumentParser
from utils_print import print_response
from controls.utils import set_failure_dict, completion_code, parse_args_retain_case

# List of commands categorized by presettings group
get_rm_cmds = ["getchassisinfo", "getacsocketpowerstate", "getnic", "getserviceversion",
               "getpowerstate", "getchassisattentionledstatus", "getchassishealth",
               "getchassismanagerstatus"]
set_rm_cmds = ["setpoweron", "setpoweroff", "setacsocketpowerstateoff", "setacsocketpowerstateon", 
               "adduser", "removeuser", "setnic", "changeuserpwd", "changeuserrole", 
               "setchassisattentionledon", "setchassisattentionledoff", "startchassismanager",
               "stopchassismanager", "enablechassismanagerssl", "disablechassismanagerssl",
               "establishcmconnection", "terminatecmconnection"]
get_svr_cmds = ["getbladeinfo", "getbladestate", "getnextboot", "getbladehealth", "getbladepowerreading",
                "getbladepowerlimit", "getbladedefaultpowerstate"]
set_svr_cmds = ["setbladeon", "setbladeoff", "setnextboot", "setbladeactivepowercycle", 
                "startbladeserialsession", "stopbladeserialsession", "setbladepowerlimit", 
                "setbladepowerlimiton", "setbladepowerlimitoff", "setbladeattentionledon", 
                "setbladeattentionledoff", "setbladedefaultpowerstate"]

def parse_wcscli_cmd(args):
    """ Call parser then execute command
    """
    try:
        # Parse command arguments       
        parser = ArgumentParser(description = "WcsCli Command Parser", prog = "wcscli")
        subparser = parser.add_subparsers(help = 'Command', dest = 'command')
        wcs_command_options(subparser)   
                
        cmd_args = parse_args_retain_case(parser, args)     
                
        ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_wcscli, 
                             str(cmd_args.command), " ".join(args[1:]))
        
        wcs_execute_cmd(cmd_args)
            
    except Exception, e:
        print_response(set_failure_dict("parse_wcscli_cmd(): Exception {0}".format(e), completion_code.failure)) 


def wcs_command_options(subparser):
    """ Parse incoming command arguments
        IMPORTANT! Parsing compatible with WcsCli
    """
    
    try:
        # SetNextBoot
        setnextboot = subparser.add_parser('setnextboot', help = "This command sets device boot type for subsequent blade reboot")
        setnextboot.add_argument("-i", dest = "device_id", metavar = "blade_index" , type = int, 
                                 help = "the target blade number. Typically 1-48", required = True)
        setnextboot.add_argument("-t", dest = "boot_type", type = int, choices = range(1, 6), 
                                 help = "1. NoOverride, 2. Force Pxe, 3. ForceDefaultHdd, 4. ForceIntoBiosSetup, 5. ForceFloppyOrRemovable",
                                 required = True)
        setnextboot.add_argument("-m", dest = "mode", type = int, choices = range(0, 2), 
                                 help = "0 - legacy, 1 - UEFI", required = True)
        setnextboot.add_argument("-p", dest = "persistence", type = int, choices = range(0, 2), 
                                 help = "0: one-time boot override. 1: request BIOS update to this boot option after the soft power cycle.\
                                 This boot option must be enabled in the BIOS boot order for the persistence to work", required = True)
        
        # SetBladeActivePowerCycle
        setactivepowercycle = subparser.add_parser('setbladeactivepowercycle', help = "This command resets blades")
        setactivepowercycle.add_argument("-a", action = "store_true", help = "all connected blades")
        setactivepowercycle.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetPowerOn
        setpoweron = subparser.add_parser('setpoweron', help = "This command sets AC outlet power on for the blades")
        setpoweron.add_argument("-a", action = "store_true", help = "all connected blades")
        setpoweron.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                help = "the target blade number. Typically 1-48")
        
        # SetPowerOff
        setpoweroff = subparser.add_parser('setpoweroff', help = "This command sets AC outlet power off for the blades")
        setpoweroff.add_argument("-a", action = "store_true", help = "all connected blades")
        setpoweroff.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # GetBladeDefaultPowerState
        getbladedefaultpowerstate = subparser.add_parser('getbladedefaultpowerstate', help = "This command gets blade default power state")
        getbladedefaultpowerstate.add_argument("-a", action = "store_true", help = "all connected blades")
        getbladedefaultpowerstate.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladeDefaultPowerState
        setbladedefaultpowerstate = subparser.add_parser('setbladedefaultpowerstate', help = "This command sets blade default power state")
        setbladedefaultpowerstate.add_argument("-s", dest = "powerstate", metavar = "state", help = "can be 0 (stay off) or 1 (power on)",
                                               type = int, required = True)
        setbladedefaultpowerstate.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladedefaultpowerstate.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladePowerLimit
        setbladepowerlimit = subparser.add_parser('setbladepowerlimit', help = "This command sets blade static power limit")
        setbladepowerlimit.add_argument("-l", dest = "powerlimit", help = "power limit per blade in Watts", required = True)
        setbladepowerlimit.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladepowerlimit.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladePowerLimitOn
        setbladepowerlimiton = subparser.add_parser('setbladepowerlimiton', help = "This command sets blade static power limit on")
        setbladepowerlimiton.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladepowerlimiton.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladePowerLimitOff
        setbladepowerlimitoff = subparser.add_parser('setbladepowerlimitoff', help = "This command sets blade static power limit off")
        setbladepowerlimitoff.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladepowerlimitoff.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladeAttentionLedOn
        setbladeattentionledon = subparser.add_parser('setbladeattentionledon', help = "This command sets blade attention led on")
        setbladeattentionledon.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladeattentionledon.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladeAttentionLedOff
        setbladeattentionledoff = subparser.add_parser('setbladeattentionledoff', help = "This command sets blade attention led off")
        setbladeattentionledoff.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladeattentionledoff.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetACSocketPowerStateOn
        setpoweron = subparser.add_parser('setacsocketpowerstateon', help = "This command turns AC socket on for the port")
        setpoweron.add_argument("-p", dest = "port_id", type = int, choices = range(1, 5), help = "Port index {1:4}",
                                required = True)
        
        # SetACSocketPowerStateOff
        setacsocketoff = subparser.add_parser('setacsocketpowerstateoff', help = "This command turns AC socket off for the port")
        setacsocketoff.add_argument("-p", dest = "port_id", metavar = "port_number", type = int, choices = range(1, 5), 
                                    help = "port number user wants to turn on i.e. 1, 2 or 3", required = True)
        
        # SetBladeOn
        setbladeon = subparser.add_parser('setbladeon', help = "This command turns on power on for the blades' chipset")
        setbladeon.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladeon.add_argument("-i", dest = "device_id", metavar = "blade_index" , type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # SetBladeOff
        setbladeoff = subparser.add_parser('setbladeoff', help = "This command turns off power to the blades' chipset")
        setbladeoff.add_argument("-a", action = "store_true", help = "all connected blades")
        setbladeoff.add_argument("-i", dest = "device_id", metavar = "blade_index" , type = int, 
                                 help = "the target blade number. Typically 1-48")
        
        # GetChassisInfo
        getchassisinfo = subparser.add_parser('getchassisinfo', help = "This command gets status info on chassis components")
        getchassisinfo.add_argument("-s", action = "store_true", help = "show blade information")
        getchassisinfo.add_argument("-c", action = "store_true", help = "show chassis information")
        getchassisinfo.add_argument("-p", action = "store_true", help = "show power information")
        getchassisinfo.add_argument("-t", action = "store_true", help = "show battery information")
        
        # GetChassisHealth
        getchassishealth = subparser.add_parser('getchassishealth', help = "This command gets health info on chassis components")
        getchassishealth.add_argument("-b", action = "store_true", help = "show blade health")
        getchassishealth.add_argument("-p", action = "store_true", help = "show Psu health")
        
        # GetBladeInfo
        getbladeinfo = subparser.add_parser('getbladeinfo', help = "This command gets status information about the blades")
        getbladeinfo.add_argument("-a", action = "store_true", help = "all connected blades")
        getbladeinfo.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                  help = "the target blade number. Typically 1-48")
        
        # GetBladeHealth
        getbladehealth = subparser.add_parser('getbladehealth', help = "This command gets blade health information")
        getbladehealth.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                    help = "the target blade number. Typically 1-48", required = True)
        getbladehealth.add_argument("-q", action = "store_true", help = "Blade CPU Information")
        getbladehealth.add_argument("-m", action = "store_true", help = "Blade Memory Information")
        getbladehealth.add_argument("-p", action = "store_true", help = "Blade PCIE Information")
        getbladehealth.add_argument("-s", action = "store_true", help = "Blade Sensor Information")
        getbladehealth.add_argument("-t", action = "store_true", help = "Temperature Sensor Information")
        getbladehealth.add_argument("-f", action = "store_true", help = "Blade Fru Information")
        
        # GetPowerState
        getpowerstate = subparser.add_parser('getpowerstate', help = "This command gets AC outlet power information of the blades")
        getpowerstate.add_argument("-a", action = "store_true", help = "Get info for all blades")
        getpowerstate.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                                   help = "the target blade number. Typically 1-48")
        
        # GetBladePowerReading
        getbladepowerreading = subparser.add_parser('getbladepowerreading', help = "This command gets power consumption of blade")
        getbladepowerreading.add_argument("-a", action = "store_true", help = "Get info for all blades")
        getbladepowerreading.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                             help = "the target blade number. Typically 1-48")
        
        # GetBladePowerLimit
        getbladepowerlimit = subparser.add_parser('getbladepowerlimit', help = "This command gets static power limit of blade")
        getbladepowerlimit.add_argument("-a", action = "store_true", help = "Get info for all blades")
        getbladepowerlimit.add_argument("-i", dest = "device_id", metavar = "blade_index", type = int, 
                             help = "the target blade number. Typically 1-48")
        
        # GetACSocketPowerState
        getsocketstate = subparser.add_parser('getacsocketpowerstate', help = "This command gets AC socket state of the port")
        getsocketstate.add_argument("-p", dest = "port_id", metavar = "port_number", type = int, choices = range(1, 5), 
                                    help = "port number user wants to get i.e. 1, 2 or 3", required = True)
        
        # GetBladeState
        getbladestate = subparser.add_parser('getbladestate', help = "This command gets power state of blades' chipset")
        getbladestate.add_argument("-a", action = "store_true", help = "Get info for all blades")
        getbladestate.add_argument("-i", dest = "device_id", type = int, help = "Blade index {1:48}")
        
        # GetNextBoot
        getnextboot = subparser.add_parser('getnextboot', help = "This command gets pending boot order of next blade boot")
        getnextboot.add_argument("-i", dest = "device_id", metavar = "blade_index" , type = int, 
                                 help = "the target blade number. Typically 1-48", required = True)
        
        # StartBladeSerialSession
        startserial = subparser.add_parser('startbladeserialsession', help = "This command starts a serial session to blade")
        startserial.add_argument("-i", dest = "device_id", type = int, help = "Blade index {1:48}", 
                                 required = True)
    
        # StopBladeSerialSession
        stopserial = subparser.add_parser('stopbladeserialsession', help = "This command terminates active serial session to blade")
        stopserial.add_argument("-i", dest = "device_id", type = int, help = "Blade index {1:48}", 
                                 required = True)
        
        # AddUser
        adduser = subparser.add_parser('adduser', help = "This command adds provided user to chassis controller")
        adduser.add_argument("-u", dest = "username", metavar = "username", help = "the username for the new user", required = True)
        adduser.add_argument("-p", dest = "pwd", metavar = "password", help = "the password for the new user", required = True)
        adduser.add_argument("-a", dest = "role", const = "admin", action = "store_const", help = "Admin Role")
        adduser.add_argument("-o", dest = "role", const = "operator", action = "store_const", help = "Operator Role")
        adduser.add_argument("-r", dest = "role", const = "user", action = "store_const", help = "User Role")
        
        # ChangeUserPwd
        changepwd = subparser.add_parser('changeuserpwd', help = "This command updates user's password")
        changepwd.add_argument("-u", dest = "username", help = "Username", required = True)
        changepwd.add_argument("-p", dest = "pwd", metavar = "new password", help = "New password", required = True)
        
        # ChangeUserRole
        changerole = subparser.add_parser('changeuserrole', help = "This command updates user's role")
        changerole.add_argument("-u", dest = "username", help = "Username", required = True)
        changerole.add_argument("-a", dest = "role", const = "admin", action = "store_const", help = "Admin Role")
        changerole.add_argument("-o", dest = "role", const = "operator", action = "store_const", help = "Operator Role")
        changerole.add_argument("-r", dest = "role", const = "user", action = "store_const", help = "User Role")
        
        # RemoveUser
        removeuser = subparser.add_parser('removeuser', help = "This command removes existing user from chassis controller")
        removeuser.add_argument("-u", dest = "username", help = "Username to delete", required = True)
        
        # GetNIC
        getnic = subparser.add_parser('getnic', help = "This command gets chassis controller network properties")
        
        # GetChassisAttentionLedStatus
        getcmattentionled = subparser.add_parser('getchassisattentionledstatus', help = "This command gets chassis manager attention led status")
        
        # SetChassisAttentionLedOn
        setcmattentionledon = subparser.add_parser('setchassisattentionledon', help = "This command sets chassis manager attention led on")
        
        # SetChassisAttentionLedOff
        setcmattentionledoff = subparser.add_parser('setchassisattentionledoff', help = "This command sets chassis manager attention led off")
        
        # GetServiceVersion
        getserviceversion = subparser.add_parser('getserviceversion', help = "This command gets chassis manager service assembly version")
        
        # SetNIC
        setnic = subparser.add_parser('setnic', help = "This command sets chassis controller network properties")
        setnic.add_argument("-a", dest = "source", choices = ("dhcp", "static"), help = "IP address source", 
                                    required = True)
        setnic.add_argument("-i", dest = "addr", help = "IP Address")
        setnic.add_argument("-m", dest = "subnet", help = "Subnet Mask")
        setnic.add_argument("-g", dest = "gateway", help = "Gateway")
        setnic.add_argument("-p", dest = "pdns", help = "Primary DNS server address")
        setnic.add_argument("-d", dest = "sdns", help = "Secondary DNS server address")
        setnic.add_argument("-t", dest = "nic", type = int, help = "NIC Number")

        subparser.add_parser('clear')
        
        # DummyCommands
        subparser.add_parser('startchassismanager')
        subparser.add_parser('stopchassismanager')
        subparser.add_parser('getchassismanagerstatus')
        subparser.add_parser('enablechassismanagerssl')
        subparser.add_parser('disablechassismanagerssl')
        subparser.add_parser('terminatecmconnection')
        
        establishcnxn = subparser.add_parser('establishcmconnection')
        establishcnxn.add_argument("-u", dest = "username", help = "username to connect to CM service. Use domain\username if not using local domain")
        establishcnxn.add_argument("-x", dest = "password", help = "password to connect to CM service")
        establishcnxn.add_argument("-m", dest = "host_name", help = "Specify host name for Chassis Manager (Optional. Default is localhost. For serial"+
                                                                    " connection, localhost is assumed.")
        establishcnxn.add_argument("-p", dest = "port", help = "Specify a valid Port to connect to for Chassis Manager (Optional. Default is 8000)")
        establishcnxn.add_argument("-s", dest = "ssl", help = "Select Chassis Manager (CM)'s SSL Encryption mode (Optional. 0: disabled /"+
                                                                    "1 (default): enabled) Enter 0 if CM is not configured to use SSL encryption"+
                                                                    " (SSL disabled in CM) Enter 1 if CM requires SSL Encryption (SSL enabled in CM)")
        establishcnxn.add_argument("-b", dest = "batch", help = "Optional batch file option (not supported in serial mode).")
        establishcnxn.add_argument("-v", dest = "version", action = "store_true", help = "Get CLI version information")
        
    except Exception, e:
        print_response(set_failure_dict("wcs_command_options: Exception {0}".format(e), completion_code.failure))
        
        
def wcs_execute_cmd(args):
    """ Attempt to execute incoming command
    """
    try:
        # Check PreSettings to see if command permitted
        device_id = 0
                
        if args.command in set(get_rm_cmds):
            cmd_type = repr(pre_settings.command_name_enum.get_rm_state)
        elif args.command in set(set_rm_cmds):
            cmd_type = repr(pre_settings.command_name_enum.set_rm_state)
        elif args.command in set(get_svr_cmds):
            cmd_type = repr(pre_settings.command_name_enum.get_blade_state)
        elif args.command in set(set_svr_cmds):
            cmd_type = repr(pre_settings.command_name_enum.set_blade_state)
        elif args.command == "clear":
            os.system('clear')
            return
        else:
            print "Command Failed. Error: Invalid Command."
            return
            
        if "device_id" in vars(args) and args.device_id != None:
            device_id = args.device_id
            
            if device_id > 48 or device_id < 1:
                print "Command Failed. Blade {0}: Completion Code: ParameterOutOfRange".format(device_id)
                return 
                        
        permission = pre_settings.pre_check_manager(cmd_type, device_id)
            
        if permission:
            # Execute commands
            if args.command == "establishcmconnection":
                if not args.version and (args.username is None or args.password is None):
                    print "Command Failed. Required arguments missing."
                    help_establishcmconnection()
                else:
                    wcs_set_establishcmconnection(args.version)
            elif args.command == "terminatecmconnection":
                wcs_set_terminatecmconnection()
            elif args.command == "disablechassismanagerssl":
                wcs_set_disablechassismanagerssl()
            elif args.command == "enablechassismanagerssl":
                wcs_set_enablechassismanagerssl()
            elif args.command == "getchassismanagerstatus":
                wcs_get_chassismanagerstatus()
            elif args.command == "startchassismanager":
                wcs_set_startchassismanager()
            elif args.command == "stopchassismanager":
                wcs_set_stopchassismanager()
            elif args.command == "getchassisinfo":
                wcs_get_chassisinfo(args.s, args.c, args.p, args.t)
            elif args.command == "getchassishealth":
                wcs_get_chassishealth(args.b, args.p)
            elif args.command == "getbladehealth":
                if args.device_id is not None:
                    wcs_get_bladehealth(args.device_id, args.q, args.m, args.p, args.s, args.t, args.f)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladehealth()
            elif args.command == "getbladeinfo":
                if args.a:
                    wcs_get_bladeinfo(0)
                elif args.device_id is not None:
                    wcs_get_bladeinfo(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladeinfo()
            elif args.command == "getpowerstate":
                if args.a:
                    wcs_get_powerstate(0)
                elif args.device_id is not None:
                    wcs_get_powerstate(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getpowerstate()
            elif args.command == "setpoweron":
                if args.a:
                    wcs_set_powerstate(0, "on")
                elif args.device_id is not None:
                    wcs_set_powerstate(args.device_id, "on")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setpoweron()
            elif args.command == "setpoweroff":
                if args.a:
                    wcs_set_powerstate(0, "off")
                elif args.device_id is not None:
                    wcs_set_powerstate(args.device_id, "off")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setpoweroff()
            elif args.command == "getbladepowerreading":
                if args.a:
                    wcs_get_bladepowerreading(0)
                elif args.device_id is not None:
                    wcs_get_bladepowerreading(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladepowerreading()
            elif args.command == "getbladedefaultpowerstate":
                if args.a:
                    wcs_get_bladedefaultpowerstate(0)
                elif args.device_id is not None:
                    wcs_get_bladedefaultpowerstate(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladedefaultpowerstate()
            elif args.command == "setbladedefaultpowerstate":
                if args.a and args.powerstate is not None:
                    wcs_set_bladedefaultpowerstate(0, args.powerstate)
                elif args.device_id is not None and args.powerstate is not None:
                    wcs_set_bladedefaultpowerstate(args.device_id, args.powerstate)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladedefaultpowerstate()
            elif args.command == "getbladepowerlimit":
                if args.a:
                    wcs_get_bladepowerlimit(0)
                elif args.device_id is not None:
                    wcs_get_bladepowerlimit(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladepowerlimit()
            elif args.command == "setbladepowerlimit":
                if args.a and args.powerlimit is not None:
                    wcs_set_bladepowerlimit(0, args.powerlimit)
                elif args.device_id is not None and args.powerlimit is not None:
                    wcs_set_bladepowerlimit(args.device_id, args.powerlimit)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladepowerlimit()
            elif args.command == "setbladepowerlimiton":
                if args.a:
                    wcs_set_bladepowerlimitstate(0, "on")
                elif args.device_id is not None:
                    wcs_set_bladepowerlimitstate(args.device_id, "on")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladepowerlimiton()
            elif args.command == "setbladepowerlimitoff":
                if args.a:
                    wcs_set_bladepowerlimitstate(0, "off")
                elif args.device_id is not None:
                    wcs_set_bladepowerlimitstate(args.device_id, "off")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladepowerlimitoff()
            elif args.command == "setbladeattentionledon":
                if args.a:
                    wcs_set_bladeattentionledstate(0, 1)
                elif args.device_id is not None:
                    wcs_set_bladeattentionledstate(args.device_id, 1)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladeattentionledon()
            elif args.command == "setbladeattentionledoff":
                if args.a:
                    wcs_set_bladeattentionledstate(0, 0)
                elif args.device_id is not None:
                    wcs_set_bladeattentionledstate(args.device_id, 0)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladeattentionledoff()
            elif args.command == "getbladestate":
                if args.a:
                    wcs_get_bladestate(0)
                elif args.device_id is not None:
                    wcs_get_bladestate(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getbladestate()
            elif args.command == "setbladeon":
                if args.a:
                    wcs_set_bladestate(0, "on")
                elif args.device_id is not None:
                    wcs_set_bladestate(args.device_id, "on")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladeon()
            elif args.command == "setbladeoff":
                if args.a:
                    wcs_set_bladestate(0, "off")
                elif args.device_id is not None:
                    wcs_set_bladestate(args.device_id, "off")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladeoff()
            elif args.command == "getnextboot":
                if args.device_id is not None:
                    wcs_get_nextboot(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getnextboot()
            elif args.command == "setnextboot":
                if args.device_id is not None and args.boot_type is not None \
                   and args.mode is not None and args.persistence is not None:
                    wcs_set_nextboot(args.device_id, args.boot_type, args.mode, args.persistence)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setnextboot()
            elif args.command == "setbladeactivepowercycle":
                if args.a:
                    wcs_set_bladeactivepowercycle(0)
                elif args.device_id is not None:
                    wcs_set_bladeactivepowercycle(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_setbladeactivepowercycle()
            elif args.command == "startbladeserialsession":
                if args.device_id is not None:
                    wcs_set_startserialsession(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_startbladeserialsession()
            elif args.command == "stopbladeserialsession":
                if args.device_id is not None:
                    wcs_set_stopserialsession(args.device_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_stopbladeserialsession()
            elif args.command == "getacsocketpowerstate":
                if args.port_id is not None:
                    wcs_get_acsocketpowerstate(args.port_id)
                else:
                    print "Command Failed. Required arguments missing."
                    help_getacsocketpowerstate()
            elif args.command == "setacsocketpowerstateon":
                if args.port_id is not None:
                    wcs_set_acsocketpowerstate(args.port_id, "on")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setacsocketpowerstateon()
            elif args.command == "setacsocketpowerstateoff":
                if args.port_id is not None:
                    wcs_set_acsocketpowerstate(args.port_id, "off")
                else:
                    print "Command Failed. Required arguments missing."
                    help_setacsocketpowerstateoff()
            elif args.command == "adduser":
                if args.username is not None and args.pwd is not None and args.role is not None:
                    wcs_set_usercreate(args.username, args.pwd, args.role)
                else:
                    print "Command Failed. Required arguments missing."
                    help_adduser()
            elif args.command == "changeuserpwd":
                if args.username is not None and args.pwd is not None:
                    wcs_set_userupdate(args.username, password = args.pwd, role = None)
                else:
                    print "Command Failed. Required arguments missing."
                    help_changeuserpwd()
            elif args.command == "changeuserrole":
                if args.username is not None and args.role is not None:
                    wcs_set_userupdate(args.username, password = None, role = args.role)
                else:
                    print "Command Failed. Required arguments missing."
                    help_changeuserrole()
            elif args.command == "removeuser":
                if args.username is not None:
                    wcs_set_userremove(args.username)
                else:
                    print "Command Failed. Required arguments missing."
                    help_removeuser()
            elif args.command == "getnic":
                wcs_get_nic()
            elif args.command == "getserviceversion":
                wcs_get_serviceversion()
            elif args.command == "setchassisattentionledon":
                wcs_set_chassisled(1)
            elif args.command == "setchassisattentionledoff":
                wcs_set_chassisled(0)
            elif args.command == "getchassisattentionledstatus":
                wcs_get_chassisled()
            elif args.command == "setnic":
                if args.source == "static" and not (args.addr or args.subnet):
                    print "Command Failed. Required arguments missing."
                    help_setnic()
                else:
                    if args.nic:
                        nic = args.nic
                    else:
                        nic = 0
                        
                    wcs_set_nic(args.source, args.addr, args.subnet, args.gateway, args.pdns, args.sdns, nic)
                    
            else:
                print "Command Failed. Invalid Command."
        else:
            return    
            
    except Exception, e:
        print_response(set_failure_dict("wcs_execute_cmd(): Exception {0}".format(e), completion_code.failure)) 
