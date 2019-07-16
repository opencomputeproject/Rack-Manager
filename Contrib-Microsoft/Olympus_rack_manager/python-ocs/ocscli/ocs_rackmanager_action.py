# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import ocslog
import pre_settings

from utils_print import *
from pre_settings import *
from ocsaudit_log import *
from controls.utils import *
from controls.sys_works import *
from models.powermeter import *
from argparse import ArgumentParser
from models.rack_manager import getrackmanager

    
#######################################################
# Rack manager show/set functions
#######################################################
           
def rackmanager_parse_show_commands(command_args):
    """
    Display commands for rack manager
        ocscli show rackmanager <command> <parameters>
        
        Command options:
            "Info",
            "PortStatus",
            "LEDStatus",
            "Relay",
            "TFTPStatus",
            "TFTPList",
            "NFSStatus",
            "SessionList",
            "Log",
            "Time",
            "Type",
            "ScanDevice",
            "FWUpdate"
    """
    
    try:
        parser = ArgumentParser(prog = 'show manager', description = "Manager show commands")
        
        subparser = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
        
        rackmanager_showcommand_options(subparser)
                
        args = parse_args_retain_case(parser, command_args)
        
        get_rm_cmd = repr(pre_settings.command_name_enum.get_rm_state)
        if pre_settings.is_get_rm_call == True:
            ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                                     "manager " + str(args.command)," ".join(command_args[1:]))
            rackmanager_showcommands(args)
        else:
            permission = pre_settings.pre_check_manager(get_rm_cmd, 0) 
            if (permission == False):
                return
            else:
                ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                                     "manager " + args.command, " ".join(command_args[1:]))
                rackmanager_showcommands(args)      
        
    except Exception,e: print(e)
    
def rackmanager_parse_set_commands(command_args):
    """
    Set commands for rack manager
        ocscli set rackmanager <command> <parameters>
        
        Command options:
            "LEDOn",
            "LEDOff",
            "RelayOn",
            "RelayOff",
            "TFTPStart",
            "TFTPStop",
            "TFTPGet",
            "TFTPPut",
            "TFTPDelete",
            "NFSStart",
            "NFSStop",
            "FwUpdate",
            "ClearLog",
            "SessionKill",
            "Time"
    """
    
    try:
        parser = ArgumentParser(prog = 'set manager', description = "Manager set commands")
        
        subparser = parser.add_subparsers(title = "Commands", metavar = '', dest = 'command')
        
        rackmanager_setcommand_options(subparser)
        
        args = parse_args_retain_case(parser, command_args)
        
        set_rm_cmd = repr(pre_settings.command_name_enum.set_rm_state)
        
        if pre_settings.is_set_rm_call == True:
            ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                                 "manager " + str(args.command), " ".join(command_args[1:]))
            rackmanager_setcommands(args)
        else:
            permission = pre_settings.pre_check_manager(set_rm_cmd, 0) 
            if (permission == False):
                return
            else:
                ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                                     "manager " + str(args.command), " ".join(command_args[1:]))
                rackmanager_setcommands(args)     
        
    except Exception, e:
        ocslog.log_exception()
        print "rackmanager_parse_set_commands - Exception: {0}".format(e) 

def rackmanager_showcommand_options(subparsers):
    try:
        # ScanDevice command
        subparsers.add_parser("scandevice", help = "This command displays rack manager system information")
        
        # Type command
        type_parser = subparsers.add_parser("type", help = "This command displays manager type")
        
        # Time command
        subparsers.add_parser("time", help = "This command displays manager system time and date in UTC")
        
        # A info command
        info_parser = subparsers.add_parser('info', help = "This command shows info.")
        info_parser.add_argument ("-s", "--server", action = "store_true", help = "Returns server information")
        info_parser.add_argument ("-m", "--manager", action = "store_true", help = "Returns manager info")
        info_parser.add_argument ("-p", "--power", action = "store_true", help = "Returns manager power/PSU info")
        
        # A health command
        health_parser = subparsers.add_parser('health', help = "This command shows manager health.")
        health_parser.add_argument('-s', "--server", action = "store_true", help="Returns server health")
        health_parser.add_argument('-m', "--memory", action = "store_true", help="Returns Memory Usage")
        health_parser.add_argument('-p', "--power", action = "store_true", help="Returns power/PSU health")
        health_parser.add_argument('-r', "--sensor", action = "store_true", help="Returns Sensor reading")
        
        # A tftp server commands
        tftpstatus_parser = subparsers.add_parser('tftp', help = "This command shows TFTP server info")
        tftp_subparser = tftpstatus_parser.add_subparsers (help = "TFTP action", dest = "tftp")
        tftp_subparser.add_parser ("status", help = "This command shows TFTP server status")
        tftp_subparser.add_parser ("list", help = "This command list files under TFTP location")
        
        # A nfs server commands
        nfsstatus_parser = subparsers.add_parser('nfs', help = "This command shows NFS server info")
        nfs_subparser = nfsstatus_parser.add_subparsers (help = "NFS action", dest = "nfs")
        nfs_subparser.add_parser ("status", help = "This command shows NFS service status")
        
        # Manager session commands
        session_parser = subparsers.add_parser('session', help = "This command shows manager open ssh session")
        session_subparser = session_parser.add_subparsers (help = "session action", dest = "session")
        session_subparser.add_parser ("list", help = "This command shows active manager ssh sessions")
        
        # A attentionledstatus command
        subparsers.add_parser('led', help = "This command shows attention led status.")
        
        # Show manager version command
        subparsers.add_parser('version', help = "This command shows manager version.")
        
        # A managerInventory command
        subparsers.add_parser('inventory', help = "This command shows manger inventory details")
        
        # Log command
        log_parser = subparsers.add_parser('log', help = "This command prints chassis log contents")
        log_parser.add_argument('-b', dest = 'starttime', help = "Start time to filter by", required = False)
        log_parser.add_argument('-e', dest = 'endtime', help = "End time to filter by", required = False)
        log_parser.add_argument('-s', dest = 'startid', help = "Start message ID to filter by", required = False)
        log_parser.add_argument('-f', dest = 'endid', help = "End message ID to filter by", required = False)
        log_parser.add_argument('-l', dest = 'loglevel', help = "Log level to filter by {0-2}", required = False)
        log_parser.add_argument('-c', dest = 'component', help = "Component to filter by {0-5}", required = False)
        log_parser.add_argument('-i', dest = 'deviceid', help = "Device ID to filter by {1-48}", required = False)
        log_parser.add_argument('-p', dest = 'portid', help = "Port ID to filter by {1-48}", required = False)

        # NTP service command
        ntp_parser = subparsers.add_parser ("ntp", help = "This command shows NTP service info.")
        ntp_subparser = ntp_parser.add_subparsers (help ="NTP action", dest ="ntp")
        ntp_subparser.add_parser ("status", help = "This command shows NTP service status.")
        ntp_subparser.add_parser ("server", help = "This command show the current NTP server.")
        
        # Remote ITP service command
        itp_parser = subparsers.add_parser ("itp", help = "This command shows remote ITP service info.")
        itp_subparser = itp_parser.add_subparsers (help ="ITP action", dest ="itp")
        itp_subparser.add_parser ("status", help = "This command shows ITP service status.")
        
        # PowerMeter Display Commands
        powermeter_parser = subparsers.add_parser("powermeter", help = "This command shows powermeter info")
        powermeter_subparser = powermeter_parser.add_subparsers(help = "PowerMeter display commands", dest = "powermeter")
        powermeter_subparser.add_parser('limit', help = "This command shows power limit policy")
        powermeter_subparser.add_parser('alert', help = "This command shows power alert policy")
        powermeter_subparser.add_parser('reading', help = "This command shows power reading")
        powermeter_subparser.add_parser('version', help = "This command shows PRU version")
        
        # OcsPower Display Commands
        ocspower_parser = subparsers.add_parser("power", help = "This command shows ocspower info")
        ocspower_subparser = ocspower_parser.add_subparsers(help = "OcsPower display commands", dest = "ocspower")
        ocspower_subparser.add_parser('status', help = "This command shows power status")
        ocspower_subparser.add_parser('reading', help = "This command shows power reading")
        
        # Throttle control command
        throttle_parser = subparsers.add_parser ("throttle", help = "This command shows throttle control status.")
        throttle_subparser = throttle_parser.add_subparsers (help ="Throttle display commands", dest ="throttle")
        throttle_subparser.add_parser ("local", help = "This command shows local throttle control status.")

        # A portstatus command
        portstatus_parser = subparsers.add_parser('port', help="This command shows the power port state.")
        requiredNamed = portstatus_parser.add_argument_group('required arguments')
        requiredNamed.add_argument('-i', dest='port_id', type = int, help='portid (1-48 or 0 for all)', required=True)

		# FWUpdate command
        fwupdate_parser = subparsers.add_parser('fwupdate', help = "This command shows FWupdate related info")
        fwupdate_subparser = fwupdate_parser.add_subparsers (help = "FWUpdate info", dest = "fwupdate")
        fwupdate_subparser.add_parser ("status", help = "This command shows status of the most recent firmware update")
        fwupdate_subparser.add_parser ("list", help = "This command lists versions of available packages")
        
        if (str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.pmdu_rackmanager) or \
        	str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.tfb_dev_benchtop) or \
                     str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.standalone_rackmanager)):
    
            # A showrelay command
            relaystatus_parser = subparsers.add_parser('relay', help="This command shows manager relay status.")
            requiredNamed = relaystatus_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-p', dest='port_id', choices=['1','2','3','4'], help='portid (1-4)', required=True)
            
            # A showrowfru command
            fru_parser = subparsers.add_parser('fru', help="This command shows manager FRU details.")
            requiredNamed = fru_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-b', dest='boardname', choices=['mb','pib','acdc'], help='RM board names', default = 'mb')
            
        elif (str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.rowmanager)):
            # A showrowfru command
            fru_parser = subparsers.add_parser('fru', help="This command shows manager FRU details.")
            requiredNamed = fru_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-b', dest='boardname', choices=['mb','pib'], help='Row Manger board names', default = 'mb')
            
            # Row manager throttle status
            throttle_subparser.add_parser ("row", help = "This command shows row throttle control status.")
            
            #Show boot strap
            bootstrp_parser = subparsers.add_parser('boot', help= "This commad shows row manager boot strap status")
            strap_subparser = bootstrp_parser.add_subparsers (help ="Boot strap action", dest ="boot")
            strap_subparser.add_parser ("strap", help = "This command shows boot strap status.")
            requiredNamed = bootstrp_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-i', dest='port_id', type = int, help='portid (1-24)', required=True)
        else:
            print("unknown mode:",pre_settings.manager_mode)
            return None 
        
    except Exception, e:
            print ("rackmanager_showcommand_options() Exception {0}".format(e))
        
def rackmanager_setcommand_options(subparsers):   
    try:
        # Time command
        time_parser = subparsers.add_parser("time", help = "This command sets manager system time and date")
        time_parser.add_argument("-y", dest = "year", type = int, help = "4-digit Year")
        time_parser.add_argument("-m", dest = "month", type = int, help = "Numerical Month (1-12)")
        time_parser.add_argument("-d", dest = "day", type = int, help = "Numerical Day (1-31)")
        time_parser.add_argument("-r", dest = "hour", type = int, help = "Hour (0-23)")
        time_parser.add_argument("-n", dest = "min", type = int, help = "Minute (0-59)")
        time_parser.add_argument("-s", dest = "sec", type = int, help = "Second (0-59)")
        
        # TFTP server commands
        tftp_parser = subparsers.add_parser('tftp', help = "This command executes TFTP server actions")
        tftp_subparser = tftp_parser.add_subparsers (help = "TFTP action", dest = "tftp")
        tftp_subparser.add_parser ("start", help = "This command starts the TFTP server")
        tftp_subparser.add_parser ("stop", help = "This command stop the TFTP server")
        
        tftpdelete_subparser = tftp_subparser.add_parser('delete', help = "This command deletes a file from local TFTP server")
        tftpdelete_subparser.add_argument('-f', dest = 'file', type = str, help = 'file to delete', required = True)
        
        tftpget_subparser = tftp_subparser.add_parser('get', help = "This command gets file from TFTP server")
        tftpget_subparser.add_argument('-s', dest = 'server', type = str, help = 'TFTP server address', required = True)
        tftpget_subparser.add_argument('-f', dest = 'file', type = str, help = 'remote file name with path relative to TFTP root', required = True)
        
        tftpput_subparser = tftp_subparser.add_parser('put', help = "This command puts file to TFTP server")
        tftpput_subparser.add_argument('-s', dest = 'server', type = str, help = 'TFTP server address', required = True)
        tftpput_subparser.add_argument('-f', dest = 'file', type = str, help = 'remote file name with path relative to TFTP root', required = True)
        tftpput_subparser.add_argument('-t', dest = 'target', type = str, help = 'Manager target (auditlog or debuglog or telemetrylog)', required = True)
        
        # Manager session commands
        session_parser = subparsers.add_parser('session', help = "This command executes Manager session actions")
        session_subparser = session_parser.add_subparsers (help = "session action", dest = "session")
        sessionkill_subparser = session_subparser.add_parser ("kill", help = "This command kill the specified manager session")
        sessionkill_subparser.add_argument('-s', dest = 'sessionid', type = str, help = 'Manager SSH session id', required = True)
        
        # PowerMeter Action Commands
        powermeter_parser = subparsers.add_parser("powermeter", help = "This command executes PowerMeter actions")
        powermeter_subparser = powermeter_parser.add_subparsers(help = "PowerMeter action commands", dest = "powermeter")
        powermeter_subparser.add_parser('clearmax', help = "This command clears max power")
        powermeter_subparser.add_parser('clearfaults', help = "This command clears power faults")
        
        powermeter_limit = powermeter_subparser.add_parser('limit', help = "This command sets the power limit")
        powermeter_limit.add_argument('-p', dest = 'powerlimit', metavar = 'powerlimit', type = int, help = 'power limit in watts', required = True)
        
        powermeter_alert = powermeter_subparser.add_parser('alert', help = "This command sets the alert policy")
        powermeter_alert.add_argument('-e', dest = 'policy', metavar = 'poweralertpolicy', type = int, help = 'poweralertpolicy (0:disable, 1:enable)', required = True)
        powermeter_alert.add_argument('-d', dest = 'dcthrottlepolicy', metavar = 'dcthrottlealertpolicy', type = int, help = 'dcthrottlealertpolicy (0:disable, 1:enable)', required = True)
        powermeter_alert.add_argument('-p', dest = 'powerlimit', metavar = 'powerlimit', type = int, help = 'power limit in watts', required=  True)
        
        # OcsPower Action Commands
        ocspower_parser = subparsers.add_parser("power", help = "This command executes OcsPower actions")
        ocspower_subparser = ocspower_parser.add_subparsers(help = "OcsPower action commands", dest = "ocspower")
        ocspower_subparser.add_parser('clearfaults', help = "This command clears power faults")
        
        # NFS server commands
        nfs_parser = subparsers.add_parser('nfs', help = "This command executes NFS server actions")
        nfs_subparser = nfs_parser.add_subparsers (help = "NFS action", dest = "nfs")
        nfs_subparser.add_parser ("start", help = "This command starts the NFS server")
        nfs_subparser.add_parser ("stop", help = "This command stop the NFS server")
                
        # A attentionledon/off command
        attentionledon_parser = subparsers.add_parser('led', help = "Manager attention led commands.")
        led_subparser = attentionledon_parser.add_subparsers (help ="LED action", dest ="led")
        led_subparser.add_parser ("on", help = "This command sets attention led on.")
        led_subparser.add_parser("off", help = "This command sets attention led off.")
        
        # A Setporton / off command
        port_parser = subparsers.add_parser('port', help='Manager port command')
        set_subparser = port_parser.add_subparsers(help = "portaction", dest = "port")
        port_on_subparser = set_subparser.add_parser("on", help = "This command turns the AC outlet power ON for the server/Rack")
        requiredNamed = port_on_subparser.add_argument_group('required arguments')
        requiredNamed.add_argument('-i', dest='port_id', metavar='port-id', type =int, help='port-id (1 to 48)', required=True)
        
        # A setpoweroff command
        setportoff_parser = set_subparser.add_parser('off', help='This command turns the AC outlet power OFF for the server/Rack')
        requiredNamed = setportoff_parser.add_argument_group('required arguments')
        requiredNamed.add_argument('-i', dest='port_id', metavar='port-id', type =int, help='port-id (1 to 48)', required=True)
        
        # FWUpdate command
        fwupdate_parser = subparsers.add_parser('fwupdate', help = 'This command starts a FW update using provided patch file')
        fwupdate_parser.add_argument('-f', dest = 'file', help = 'Update file path', required = True)
        
        # Clear Log command
        log_parser = subparsers.add_parser('log', help = "This command executes log actions")
        log_subparser = log_parser.add_subparsers (help = "Log action", dest = "log")
        log_subparser.add_parser ("clear", help = "This command clears all log entries")
        
        # NTP service commands
        ntp_parser = subparsers.add_parser ("ntp", help = "This command controls the NTP service.")
        ntp_subparser = ntp_parser.add_subparsers (help ="NTP action", dest ="ntp")
        ntp_subparser.add_parser ("start", help = "This command starts the NTP service.")
        ntp_subparser.add_parser ("stop", help = "This command stops the NTP service.")
        ntp_subparser.add_parser ("restart", help = "This command restarts the NTP service.")
        ntp_subparser.add_parser ("enable", help = "This command will enable the NTP service.")
        ntp_subparser.add_parser ("disable", help = "This command will disable the NTP service.")
        server_parser = ntp_subparser.add_parser ("server", help = "This command sets the NTP server.")
        server_parser.add_argument ("-s", dest = "server", help = "NTP server address", required = True)
        
        # Remate ITP service commands
        itp_parser = subparsers.add_parser ("itp", help = "This command controls the remote ITP service.")
        itp_subparser = itp_parser.add_subparsers (help ="ITP action", dest ="itp")
        itp_subparser.add_parser ("start", help = "This command starts the ITP service.")
        itp_subparser.add_parser ("stop", help = "This command stops the ITP service.")
        itp_subparser.add_parser ("restart", help = "This command restarts the ITP service.")
        itp_subparser.add_parser ("enable", help = "This command will enable the ITP service.")
        itp_subparser.add_parser ("disable", help = "This command will disable the ITP service.")
        
        # Change the hostname
        hostname_parser = subparsers.add_parser ("hostname", help = "This command sets the hostname.")
        hostname_parser.add_argument ("-n", dest = "hostname", help = "Hostname", required = True)
        
        # Throttle control commands
        throttle_parser = subparsers.add_parser ("throttle", help = "This command controls the throttle configuration.")
        throttle_subparser = throttle_parser.add_subparsers (help = "Throttle action", dest = "throttle")
        local_parser = throttle_subparser.add_parser ("local", help = "This command controls local throttle configuration.")
        local_subparser = local_parser.add_subparsers (help = "Local throttle action", dest = "gpio")
        throttle_arg = local_subparser.add_parser ("bypass", help = "This command controls the local throttle bypass.")
        requiredNamed = throttle_arg.add_argument_group ("required arguments")
        requiredNamed.add_argument ("-e", dest = "state", choices = [0, 1], type = int, help = "Disable (0)/Enable (1)", required = True)
        throttle_arg = local_subparser.add_parser ("enable", help = "This command controls the local throttle output enable.")
        requiredNamed = throttle_arg.add_argument_group ("required arguments")
        requiredNamed.add_argument ("-e", dest = "state", choices = [0, 1], type = int, help = "Disable (0)/Enable (1)", required = True)
        
        if (str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.pmdu_rackmanager) or \
        	str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.tfb_dev_benchtop) or \
                         str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.standalone_rackmanager)):
            
            # A setrelayon/off command
            relay_parser = subparsers.add_parser('relay', help="Manager relay commands.")
            set_relay_subparser = relay_parser.add_subparsers (help ="relay action", dest ="relay")
            relayon_parser = set_relay_subparser.add_parser("on", help = "This command turns Rack Manger AC socket ON.")            
            requiredNamed = relayon_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-p', dest='port_id', choices=['1','2','3','4'], help='portid (1-4)', required=True)
            
            relayoff_parser = set_relay_subparser.add_parser('off', help="This command turns Rack Manger AC socket OFF.")
            requiredNamed = relayoff_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-p', dest='port_id', choices=['1','2','3','4'], help='portid (1-4)', required=True)
            
            # A writefru command
            writefru_parser = subparsers.add_parser('fru', help="This command is used to update the Rack Manger FRU information.")
            requiredNamed = writefru_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-b', dest='boardname', choices=['mb','pib','acdc'], help='Rack Manager board name', required=True)
            requiredNamed.add_argument('-f', dest='filename', help='fru file path', required=True)
            
        elif (str(pre_settings.manager_mode) == str(pre_settings.rm_mode_enum.rowmanager)):
            # A writefru command
            writefru_parser = subparsers.add_parser('fru', help="This command is used to update the Row Manger FRU information.")
            requiredNamed = writefru_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-b', dest='boardname', choices=['mb','pib'], help='Row Manager board name', required=True)
            requiredNamed.add_argument('-f', dest='filename', help='fru file path', required=True)
            
            # Row manager throttle control
            row_parser = throttle_subparser.add_parser ("row", help = "This command controls row throttle configuration.")
            row_subparser = row_parser.add_subparsers (help = "Row throttle action", dest = "gpio")
            throttle_arg = row_subparser.add_parser ("bypass", help = "This command controls the row throttle bypass.")
            requiredNamed = throttle_arg.add_argument_group ("required arguments")
            requiredNamed.add_argument ("-e", dest = "state", choices = [0, 1], type = int, help = "Disable (0)/Enable (1)", required = True)
            throttle_arg = row_subparser.add_parser ("enable", help = "This command controls the row throttle output enable.")
            requiredNamed = throttle_arg.add_argument_group ("required arguments")
            requiredNamed.add_argument ("-e", dest = "state", choices = [0, 1], type = int, help = "Disable (0)/Enable (1)", required = True)
            
            #set boot strap
            bootstrp_parser = subparsers.add_parser('recovery', help= "This commad turns Rack Manager ON or OFF")
            requiredNamed = bootstrp_parser.add_argument_group('required arguments')
            requiredNamed.add_argument('-i', dest='port_id', type = int, help='portid (1-24)', required=True)
            set_reset_subparser = bootstrp_parser.add_subparsers (help ="reset action", dest ="reset")
            set_reset_subparser.add_parser("on", help = "This command turns OFF Rack Manger.")
            set_reset_subparser.add_parser("off", help = "This command turns ON Rack Manger.")
        else:
            print("unknow mode:",pre_settings.manager_mode)
            return None
        
    except Exception, e:
            print ("rackmanager_setcommand_options() Exception {0}".format(e))
    
def rackmanager_showcommands(args):  

    try:        
        rackmanager = getrackmanager()

        manager_mode = get_mode()
        
        request = {}
        request["action"] = args.command
        request["mode"] = "display"
                
        if(args.command == "port" or args.command == "relay"):
            request["port_id"] = args.port_id

        elif args.command == "inventory":
            if manager_mode == None:
                print_response(set_failure_dict("Invalid manager mode",completion_code.failure))
                return
            request["rm_mode"] = manager_mode
                        
        elif(args.command == "log"):
            if args.starttime:
                request['starttime'] = args.starttime
            if args.endtime:
                request['endtime'] = args.endtime
            if args.startid:
                request['startid'] = args.startid
            if args.endid:
                request['endid'] = args.endid
            if args.component:
                request['component'] = args.component
            if args.loglevel:
                request['loglevel'] = args.loglevel
            if args.deviceid:
                request['deviceid'] = args.deviceid
            if args.portid:
                request['port_id'] = args.portid
            
        elif args.command == "info":
            if manager_mode == None:
                print_response(set_failure_dict("Invalid manager mode",completion_code.failure))
                return
            request["server"] = args.server
            request["manager"] = args.manager
            request["power"] = args.power
            request["rm_mode"] = manager_mode
            
        elif args.command == "health":
            if manager_mode == None:
                print_response(set_failure_dict("Invalid manager mode",completion_code.failure))
                return
            request["server"] = args.server
            request["memory"] = args.memory
            request["power"] = args.power
            request["sensor"] = args.sensor
            request["rm_mode"] = manager_mode
            
        elif(args.command == "fru") or (args.command == "info"):
            board_name = mode_request()
            if board_name == None:
                print_response(set_failure_dict("board_name is empty",completion_code.failure))
                return
            if args.command == "fru":
                request["boardname"] = board_name + '_' + args.boardname
            else: 
                if board_name == "rm":
                    request["boardname"] = "Rack"
                else:
                    request["boardname"] = "Row"
                    
        elif (args.command == "ntp"):
            request["action"] = args.command + args.ntp.lower()
        elif (args.command == "nfs"):
            request["action"] = args.command + args.nfs.lower()
        elif (args.command == "tftp"):
            request["action"] = args.command + args.tftp.lower()
        elif (args.command == "itp"):
            request["action"] = args.command + args.itp.lower()
        elif (args.command == "throttle"):
            request["action"] = args.command + args.throttle.lower()
        elif (args.command == "session"):
            request["action"] = args.command + args.session.lower()
        elif (args.command == "boot"):
            request["action"] = args.command + args.boot.lower()
            request["port_id"] = args.port_id
        elif (args.command == "fwupdate"):
            request["action"] = args.command + args.fwupdate.lower()
			
        if args.command == "powermeter":
            powermeter = get_powermeter()
             
            request["action"] = args.powermeter.lower()
                
            info = powermeter.doWorks(request)
        elif args.command == "power":
            request["action"] = "manager" + args.ocspower.lower()
                
            info = system_ocspower_display(-1, request)            
        else:
            info = rackmanager.doWorks(request)
        
        if (args.command == "info" and args.manager == False and args.power == False) or \
            (args.command == "info" and args.server == True and args.manager == True and args.power == True) or \
                (args.command == "health" and args.memory == False and args.power == False and args.sensor == False) or \
                    (args.command == "health" and args.server == True and args.memory == True and args.power == True and args.sensor == True):
            print_health_info(args,info)
        
        elif (args.command == "port" and args.port_id == 0):
            print_all_port_info(info) 
        
        elif args.command == "inventory":
            if (completion_code.cc_key in info.keys()) and (info[completion_code.cc_key] == completion_code.success):
                info.pop(completion_code.cc_key, None)
                print_inventory_data(info) 
                print completion_code.cc_key + ":" + completion_code.success
            else:
                print_response(info)          
        else:      
            print_response(info)
            
    except Exception, e:
        print_response(set_failure_dict(("rackmanager_showcommands() - Exception {0}".format(e)), completion_code.failure)) 

def  print_inventory_data(info):
    try:
        inventory_list = []
        for k, v in info.iteritems():
            if isinstance(v, dict): 
                inventory_list.append(v.values()) 
        
        print ("| Slot Id | Port State | Port Present | BMC SW Port |     MAC1      |     GUID    ") 
        for item in inventory_list:
            print"|",item[0]," "*(6-len(str(item[0]))),"|", \
                   item[1]," "*(9-len(item[1])),"|", \
                   item[2]," "*(11-len(item[2])),"|", \
                   item[3]," "*(10-len(str(item[3]))),"|", \
                   item[4]," "*(12-len(item[4])),"|", \
                   item[5]," "*(12-len(item[5]))
        
    except Exception, e:
        print_response(set_failure_dict(("exception ", e),completion_code.failure))   
       
def print_all_port_info(info):
    try:
        for key in info:
            info[key].pop(completion_code.cc_key, None)
            
            port_id = "Port Id: {0}".format(key) 
                
            result = "".join(str(key) + ':' + ' ' + str(value) + tab  for key,value in info[key].items())
            print port_id + "\t" + result 
        
        print completion_code.cc_key + ": {0}".format(completion_code.success)
        
    except Exception, e:
        print_response(set_failure_dict(("exception ", e),completion_code.failure))        
    
def print_health_info(args,info):
    try:
        if type(info) == str:
            print_response(set_failure_dict(info, completion_code.failure))
        
        completioncode = ""
        if (args.command == "info" and args.server == True and args.manager == False and args.power == False) or \
                 (args.command == "health" and args.server == True and args.memory == False and args.power == False and args.sensor == False):
            try:
                for key in info:
                    if key == completion_code.desc:
                        print_response(info)
                        return
                    if key == completion_code.cc_key:
                        completioncode = info[key]
                        continue
                                        
                    guid = info[key].pop('GUID', None)
                    mac = info[key].pop('MAC', None)
                    result = "".join(str(key) + ':' + ' ' + str(value) + tab  for key,value in info[key].items())
                    print result 
                    if guid != None and mac != None: 
                        print "GUID" + ':' + guid  +  tab + "MAC" + ': ' + mac
                        print'\n'            
            except Exception, e:
                print_response(set_failure_dict(("exception ", e),completion_code.failure))
                
            print completion_code.cc_key + ": {0}".format(completioncode)
            return        
        
        elif args.command == "info" or args.command == "health":
            if completion_code.cc_key in info:
                completioncode = info.pop(completion_code.cc_key,None)

            server_coll = {}
            if args.command == "info":
                server_coll = info.pop('Server Info', None)
                print_response(info)
                print tab + "Server Info:"
                
            if args.command == "health":
                server_coll = info.pop('Server State', None)                
                print_response(info)
                print tab + "Server State:"
            
            for key in server_coll:
                if key == completion_code.desc:
                    print_response(server_coll);
                else:
                    guid = server_coll[key].pop('GUID', None)
                    mac = server_coll[key].pop('MAC', None)
    
                    result = "".join(tab + str(key) + ':' + ' ' + str(value) + tab for key,value in server_coll[key].items())
                
                    print result 
                    if guid != None and mac != None: 
                        print tab + "GUID" + ':' + guid  + tab + "MAC" + ': ' + mac
                        print'\n'
            print tab + completion_code.cc_key + ": {0}".format(completioncode)
            return        
        
    except Exception,e:
        print_response(set_failure_dict(("exception to print", e), completion_code.failure))

def rackmanager_setcommands(args):    
    try:
        rackmanager = getrackmanager()
        
        request = {}
        
        request["action"] = args.command
        request["mode"] = "action"
                
        if args.command == "relay":
            request["action"] = args.command + args.relay.lower()
            request['port_id'] = args.port_id
        elif args.command == "port":
            request["action"] = args.command + args.port.lower()
            request['port_id'] = args.port_id  
        elif args.command == "fru":
            board_name = mode_request()
            if board_name == None:
                print_response(set_failure_dict("board_name is empty", completion_code.failure))
                return
            request["boardname"] = board_name + '_' + args.boardname
            request['file'] = args.filename
        elif args.command == "ntp":
            request["action"] = args.command + args.ntp.lower()
            if args.ntp == "server":
                request["server"] = args.server
        elif args.command == "hostname":
            request["hostname"] = args.hostname
        elif args.command == "led":
            request["action"] = args.command + args.led.lower()
        elif args.command == "fwupdate":
            request["file"] = args.file
        elif args.command == "nfs":
            request["action"] = args.command + args.nfs.lower()
        elif args.command == "tftp":
            request["action"] = args.command + args.tftp.lower()
        elif args.command == "session":
            request["action"] = args.command + args.session.lower()
        elif args.command == "itp":
            request["action"] = args.command + args.itp.lower()
        elif args.command == "log":
            request["action"] = args.log.lower() + args.command
        elif args.command == "throttle":
            request["action"] = args.command + args.throttle.lower() + args.gpio.lower()
            request["enable"] = True if (args.state == 1) else False
        elif args.command == "recovery":
            request["action"] = args.command + args.recovery.lower()
            request['port_id'] = args.port_id  
        elif request["action"] == "time":
            if args.year:
                request["year"] = args.year
            if args.month:
                request["month"] = args.month
            if args.day:
                request["day"] = args.day
            if args.hour:
                request["hour"] = args.hour
            if args.min:
                request["min"] = args.min
            if args.sec:
                request["sec"] = args.sec
        if request["action"] == "tftpget":
            request["server"] = args.server
            request["file"] = args.file
        elif request["action"] == "tftpput":
            request["server"] = args.server
            request["file"] = args.file
            request["target"] = args.target
        elif request["action"] == "tftpdelete":
            request["file"] = args.file
        elif request["action"] == "sessionkill":
            request["sessionid"] = args.sessionid
                            
        if args.command == "powermeter":
            powermeter = get_powermeter()
            
            request["action"] = args.powermeter.lower()
                    
            if args.powermeter == "alert":
                request["policy"] = args.policy
                request["dcthrottlepolicy"] = args.dcthrottlepolicy
                request["powerlimit"] = args.powerlimit
            elif args.powermeter == "limit":
                request["powerlimit"] = args.powerlimit
            
            info = powermeter.doWorks(request)
        elif args.command == "power":            
            request["action"] = "manager" + args.ocspower.lower()

            info = system_ocspower_action(-1, request)
        else:
            info = rackmanager.doWorks(request)
        
        print_response(info)   
          
    except Exception, e:
        print_response(set_failure_dict(("rackmanager_setcommands() - Exception {0}".format(e)), completion_code.failure)) 
