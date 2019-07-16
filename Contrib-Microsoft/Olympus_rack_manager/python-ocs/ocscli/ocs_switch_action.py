# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: utf-8 -*-

from pre_settings import *
from ocsaudit_log import *
from argparse import ArgumentParser
from models.switch_manager import getswitch
from controls.utils import parse_args_retain_case
from utils_print import ocsprint, print_response


def switch_show_commands (command_args):
    try:
        parser = ArgumentParser (prog = "show switch", description = "Management switch show commands")
        subparser = parser.add_subparsers(title="Commands", metavar='',dest='command')
        switch_show_command_options (subparser)
        args = parse_args_retain_case(parser, command_args)
        
        if (pre_check_helper (command_name_enum.get_rm_state, is_get_rm_call, 0)):
            ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                                     "switch " + str(args.command)," ".join(command_args[1:]))
            switch_show_commands_execute (args)
    
    except Exception as error:
        #call trace log to log exception
        ocsprint ("Failed to execute show switch command\n%s" % error)
    
def switch_show_command_options (subparsers):
    # The overall switch information command
    info_parser = subparsers.add_parser ("info", help = "Show switch information")
    info_parser.add_argument ("-i", dest = "ip", metavar = "IP", default = None, help = "Switch IP address")
    
    # The status for a single switch port
    port_parser = subparsers.add_parser ("port", help = "Show port status")
    port_parser.add_argument ("-i", dest = "ip", metavar = "IP", default = None, help = "Switch IP address")
    port_required = port_parser.add_argument_group ("required arguments")
    port_required.add_argument ("-p", dest = "port_id", metavar = "portID", type = int, choices = range (1, 49), help = "Port number", required = True)

def switch_show_commands_execute (args):
    try:
        switch = getswitch (args.ip, "")
        
        result = {}
        if (args.command == "info"):
            result = switch.getswitch_info ()
        elif (args.command == "port"):
            result = switch.getswitchport_info (args.port_id)
            
        print_response (result)
    
    except Exception as error:
        #call trace log to log exception
        ocsprint ("Failed to show switch %s\n%s" % (args.command, error))
        
def switch_set_commands (command_args):
    try:
        parser = ArgumentParser (prog = "set switch", description = "Management switch set commands")
        subparser = parser.add_subparsers(title="Commands", metavar='',dest='command')
        switch_set_command_options (subparser)
        args = parse_args_retain_case(parser, command_args)
        
        if (pre_check_helper (command_name_enum.set_rm_config, is_rm_config_call, 0)):
            ocsaudit_log_command("", cmd_type.type_set, cmd_interface.interface_ocscli, 
                                 "switch " + str(args.command)," ".join(command_args[1:]))
            switch_set_commands_execute (args)
    
    except Exception as error:
        #call trace log to log exception
        ocsprint ("Failed to execute set switch command\n%s" % error)
        
def switch_set_command_options (subparsers):
    # Set the switch configuration
    config_parser = subparsers.add_parser ("config", help = "Set switch configuration")
    config_parser.add_argument ("-d", dest = "uart", metavar = "device", default = "/dev/ttyO0", help = "Switch console UART")
    config_parser.add_argument ("-v", dest = "verbose", default = False, action = "store_true", help = "Enable console output during command execution")
    config_required = config_parser.add_argument_group ("required argument")
    config_required.add_argument ("-f", dest = "path", metavar = "path", help = "Path to configuration file", required = True)
    
    # Upgrade the switch firmware
    upgrade_parser = subparsers.add_parser ("upgrade", help = "Upgrade switch firmware")
    upgrade_parser.add_argument ("-d", dest = "uart", metavar = "device", default = "/dev/ttyO0", help = "Switch console UART")
    upgrade_parser.add_argument ("-v", dest = "verbose", default = False, action = "store_true", help = "Enable console output during command execution")
    upgrade_required = upgrade_parser.add_argument_group ("required arguments")
    upgrade_required.add_argument ("-f", dest = "path", metavar = "path", help = "TFTP path to fimware binary", required = True)
    
    # Reboot the switch
    reset_parser = subparsers.add_parser ("reset", help = "Reset the switch")
    reset_parser.add_argument ("-d", dest = "uart", metavar = "device", default = "/dev/ttyO0", help = "Switch console UART")
    reset_parser.add_argument ("-v", dest = "verbose", default = False, action = "store_true", help = "Enable console output during command execution")
    
def switch_set_commands_execute (args):
    try:
        switch = getswitch("", args.uart, verbose = args.verbose)
        
        result = {}
        if (args.command == "config"):
            result = switch.do_configure(args.path)
        elif (args.command == "upgrade"):
            result = switch.do_upgrade(args.path)
        elif (args.command == "reset"):
            result = switch.do_reset()
            
        print_response (result)
        if (args.verbose):
            print "\n"
    
    except Exception as error:
        #call trace log to log exception
        ocsprint ("Failed to set switch %s\n%s" % (args.command, error))
        
def switch_start_commands (command_args):
    try:
        parser = ArgumentParser(prog = "start aux", description = "Auxiliary serial port start commands")
        subparser = parser.add_subparsers(help = "Command type", dest = "command")
        switch_start_command_options(subparser)
        args = parse_args_retain_case(parser, command_args)
        
        if (pre_check_helper (command_name_enum.set_rm_state, is_set_rm_call, 0)):
            ocsaudit_log_command("", cmd_type.type_start, cmd_interface.interface_ocscli, 
                         "switch " + args.command," ".join(command_args[1:]))
            switch_start_commands_execute(args)
    
    except Exception as error:
        #call trace log to log exception
        ocsprint("Failed to execute start aux command\n%s" % error)
        
def switch_start_command_options (subparsers):
    # Connect to the serial console
    shell_parser = subparsers.add_parser ("console", help = "Access serial console")
    shell_parser.add_argument ("-d", dest = "uart", metavar = "device", default = "/dev/ttyO0", help = "Serial console UART")
    shell_parser.add_argument ("-b", dest = "baud", metavar = "baud rate", type = int, help = "The serial port baud rate")
    shell_parser.add_argument ("-x", dest = "halt", default = False, action = "store_true", help = "Pass Ctrl-C and Ctrl-D to the console and exit only on Ctrl-X")
    
def switch_start_commands_execute (args):
    try:
        switch = getswitch("", args.uart)
        baud = args.baud if args.baud else None
        
        if (args.command == "console"):
            switch.do_console (baud, args.halt)
    
        print "\n"
    except Exception as error:
        #call trace log to log exception
        ocsprint ("Failed to start switch %s\n%s" % (args.command, error))