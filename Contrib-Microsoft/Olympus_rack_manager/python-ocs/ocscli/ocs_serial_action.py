# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import pre_settings

from ocsaudit_log import *
from controls.utils import *
from models.blade_system import *
from argparse import ArgumentParser
from utils_print import print_response

def serial_start_command(command_args):
    """ Start serial session command parser
    """
    try:
        permission = False
        deviceid = 0

        parser = ArgumentParser(prog = "start serial", description = "Start serial session command")
            
        subparser = parser.add_subparsers(title = "Commands", dest = "command")
        
        serial_parser = subparser.add_parser("session", help = "Start serial session")
        serial_parser.add_argument("-i", dest = "serverid", type = int, help = "server-id (1 to 48)", required = True) 
        serial_parser.add_argument("-f", action = "store_true", help = "force start", required = False, default = False) 

        args = parse_args_retain_case(parser, command_args)
    
        if args.serverid < 1 or args.serverid > 48:
            print_response(set_failure_dict("Server ID invalid {0}, expected (1-48)".format(args.serverid), completion_code.failure)) 
            return

        config_cmd = repr(pre_settings.command_name_enum.set_blade_config)
        deviceid = args.serverid

        permission = pre_settings.pre_check_manager(config_cmd, deviceid) 

        if (permission == False):
            return
        else:
            ocsaudit_log_command("", cmd_type.type_start, cmd_interface.interface_ocscli, 
                                 "serial " + str(args.command)," ".join(command_args[1:]))
        
        system_serial_session(args.serverid, "startserialsession", args.f)

    except Exception, e:
            print_response("serial_start_command - Exception: {0}".format(e))

def serial_stop_command(command_args):
    """ Stop serial session command parser
    """
    try:
        permission = False
        deviceid = 0

        parser = ArgumentParser(prog = "stop serial", description = "Stop serial session command")
            
        subparser = parser.add_subparsers(title = "Commands", dest = "command")
        
        serial_parser = subparser.add_parser("session", help = "Start serial session")
        serial_parser.add_argument("-i", dest = "serverid", type = int, help = "Server ID (1 to 48)", required = True) 

        args = parse_args_retain_case(parser, command_args)
        
        
        if args.serverid < 1 or args.serverid > 48:
            print_response(set_failure_dict("Server ID invalid {0}, expected (1-48)".format(args.serverid), completion_code.failure)) 
            return

        config_cmd = repr(pre_settings.command_name_enum.set_blade_config)
        deviceid = args.serverid

        permission = pre_settings.pre_check_manager(config_cmd, deviceid) 

        if (permission == False):
            return
        else:
            ocsaudit_log_command("", cmd_type.type_stop, cmd_interface.interface_ocscli, 
                                 "serial " + str(args.command)," ".join(command_args[1:]))

            system_serial_session(args.serverid, "stopserialsession")
        
    except Exception, e:
            print_response("serial_stop_command - Exception: {0}".format(e))

def system_serial_session(deviceid, commandname, force = False):
    try:
        system = getsystem(deviceid) 

        action = {}
        
        action["action"] = commandname
        action["force"] = force 
            
        info = system.doWorks(action)  
        
        print_response(info)     
            
    except Exception, e:
        print_response("system_serial_session - Exception: {0}".format(e))
