# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import os
import cmd
import sys
import json
import uuid
import base64
import getpass
import argparse
import subprocess

# Import commonapi, wcscli to SYSPATH
sys.path.append(os.path.abspath('/usr/lib/commonapi'))
sys.path.append(os.path.abspath('/usr/bin/wcscli'))

import ocslog
import ocs_help
import loadconfig
import pre_settings

from ocs_mte import *
from controls.utils import set_failure_dict, completion_code
from utils_print import *
from ocsaudit_log import *
from wcs_shell import wcsshell
from ocs_user_action import *
from ocs_switch_action import *
from ocs_system_action import *
from ocs_serial_action import *
from ocs_network_action import *
from ocs_version_action import *
from ocs_rackmanager_action import *

help_list = ["help", "-h"]
switch_list = ["switch", "sw"]
aux_list = ["auxiliary", "aux"]
system_list = ["system", "sys"]
version_list = ["version", "ver"]
network_list = ["network", "net"]
manager_list = ["manager", "man"]
serial_list = ["serial", "srl"]
    
class ocsshell(cmd.Cmd):
    """ OCS Shell Class
    """
    
    commandtypeslist = ['show', 'sh', 'set', 'start', 'stop', 'exit', 'wcscli', 'help']
    groupslist = ['version', 'user', 'network', 'system', 'manager', 'mte', 'switch', 'auxiliary'] 
    startlist = ['serial', 'mte', 'auxiliary']
    stoplist = ['serial', 'mte']   
 
    def __init__(self):
        # Call superclass constructor 
        cmd.Cmd.__init__(self, completekey='tab') 
        
        try:
            # Initialize log
            ocslog.initialize_log(ocslog.loglevel_t_enum.INFO_LEVEL)
            
        except Exception, e:
            print_response(set_failure_dict("Failed to initialize the log: {0}".format(e)))
                 
        #Get group_id
        permission_exitcode = pre_settings.verify_caller_permission() 
        
        if permission_exitcode != 0:
            print_response(set_failure_dict("Failed to verify caller permission, error code: {0}".format(permission_exitcode), 
                                            completion_code.failure))
            sys.exit(permission_exitcode)
               
        #Get mode type
        rm_mode = pre_settings.get_rm_mode()
        
        if rm_mode != 0:
            print_response(set_failure_dict("Failed to get rack manager mode, error code: {0}".format(rm_mode), 
                                            completion_code.failure))
            sys.exit(rm_mode)
            
        # Load configuration settings
        loadconfig.loadconfig()
        
        if len(sys.argv) > 1:
            mycmd = ''
           
            for arg in sys.argv[1:]:
                mycmd = mycmd + arg + " "
            
            mycmd = mycmd + "\n"
            self.cmdqueue.append(mycmd)
            self.cmdqueue.append("exit\n")
            
        # Change default prompt
        if loadconfig.prompt:
            self.changeprompt(loadconfig.prompt)    
 
    def do_show(self, commands):       
        """
        Execute ocscli show commands 
        usage:
            show group command <parameters>
            
        --------------------------------------         
         Supported groups
        --------------------------------------
         1. network
         2. manager
         3. system
         4. user
         5. switch
         6. mte
         7. version
        """ 
        
        try:
            args = commands.split()        
            command_args = args
            
            if len(command_args) == 0:
                ocsshell.do_help(self, "help")                           
            
            command = args[0].lower() 
            subcommand = ""
            
            if len(args) > 1:
                command_args = args[1:] 
                subcommand = args[1].lower()
            
            if command in help_list:
                ocsshell.do_help(self, "help") 
            elif command in version_list:
                show_service_version()     
            elif command == "user":
                user_Actions(command_args)   
            elif command in network_list:
                if subcommand == "interface" or subcommand == "route":
                    show_network_properties(command_args)
                elif len(args) == 1:
                    show_all_interfaces()
                else:
                    ocsshell.do_help(self, "network")
            elif subcommand == "power" and command in system_list and pre_settings.manager_mode == "ROWMANAGER":
                    print("System commands are not supported on Row-Manager")
                    return
            elif command in manager_list:
                if subcommand == "network":
                    if len(command_args) == 1:
                        show_all_interfaces()
                    else:
                        show_network_properties(command_args[1:])
                else:
                    rackmanager_parse_show_commands(command_args)   
            elif command == "mte":
                if verify_caller_admin_permission():
                    show_mte()            
                else:
                    print "Access denied"           
            elif command in system_list: 
                if pre_settings.manager_mode == "ROWMANAGER":
                    return set_failure_dict("System commands not supported on Row-Manager", completion_code.failure)
                system_show_commands(command_args)                
            elif command in switch_list:
                switch_show_commands(command_args)
            elif command == "-bash":
                ocsaudit_log_command("", cmd_type.type_shell, cmd_interface.interface_ocscli, 
                             "bash", command_args)
                openCommandShell("bash")
            else:
                ocsprint("Command not supported: %s\n" % command)
                ocsprint("Available categories:\n %s  "% '  \n '.join(map(str,self.groupslist)))
        except:            
            pass    

    def do_set(self,commands):       
        """
        Execute ocscli set commands 
        usage:
            set group command <parameters>
            
        ---------------------------------------
         Supported groups
        ---------------------------------------
             1. network
             2. manager
             3. system
             4. user
             5. switch                                      
        """ 
        
        try:                  
            args = commands.split()
            command_args = args
             
            if len(command_args) == 0:
                ocsshell.do_help(self, "help")
                   
            command = args[0].lower()  
            subcommand = ""
            
            if len(args) >1:
                command_args = args[1:]   
                subcommand = args[1].lower()
            
            if command in help_list:
                ocsshell.do_help(self, command)
            elif command == "user":
                user_Actions(command_args)      
            elif command in network_list:
                set_network_interface(command_args)
            elif subcommand == "power" and command in system_list and pre_settings.manager_mode == "ROWMANAGER":
                    return set_failure_dict("System commands not supported on Row-Manager", completion_code.failure)                                            
            elif command in system_list: 
                if pre_settings.manager_mode == "ROWMANAGER":
                    return set_failure_dict("System commands not supported on Row-Manager", completion_code.failure)
                system_set_commands(command_args)
            elif command in manager_list:
                if subcommand == "network":
                    set_network_interface(command_args[1:])
                else:    
                    rackmanager_parse_set_commands(command_args)
            elif command in switch_list:
                switch_set_commands(command_args)
            elif command =="-bash":
                ocsaudit_log_command("", cmd_type.type_shell, cmd_interface.interface_ocscli, 
                             "bash", command_args)
                openCommandShell("bash")
            else:
                ocsprint("Command not supported: %s\n" % command)
                ocsprint("Available categories:\n %s  "% '  \n '.join(map(str,self.groupslist)))
        except:            
            pass    
        
    def do_sh(self,commands):
        """
        sh is a short name for show.
        usage:
            sh group command <parameter>
            
        ------------------------------------
        Supported groups
        ------------------------------------
           1. network
           2. manager
           3. system
           4. user
           5. switch
           6. mte
           7. version
        """
        
        try:
            ocsshell.do_show(self,commands)
        except:            
            pass
        
    def do_start(self, commands):
        """
        Execute ocscli start commands.
        Usage:
            start command <parameters>
        -------------------------------
         Supported commands
        -------------------------------
            1. serial
            2. mte
            3. auxiliary
        """  
        
        try:                   
            args = commands.split()        
            command_args = args   
            command = args[0].lower() 
                     
            if len(command_args) == 0:
                ocsshell.do_help(self, "help")
                    
            if len(args) > 1:
                command_args = args[1:]  
                
            if command in help_list:
                ocsshell.do_help(self, command)
            elif command in serial_list:
                if pre_settings.manager_mode == "ROWMANAGER":
                    print("Server serial session not supported on Row-Manager")
                    return
                serial_start_command(command_args) 
            elif command == "mte":
                if verify_caller_admin_permission():
                    start_mte(command_args)
                else:
                    print "Access denied"
            elif command in aux_list:
                switch_start_commands(command_args)
            else:
                ocsprint("Command not supported: {0}\n".format(command))
                ocsprint("Available commands:\n %s  "% '  \n '.join(map(str,self.startlist)))
        except:
            pass   
        
    def do_stop(self,commands):
        """
        Execute ocscli stop commands.
        Usage:
            stop command <parameters>
        -------------------------------
         Supported commands
        -------------------------------
            1. serial
            2. mte
        """  
        
        try:        
                                       
            args = commands.split()
        
            command_args = args            
        
            command = args[0].lower()  
            
            if len(args) > 1:
                command_args = args[1:]  
                
            if command in help_list:
                ocsshell.do_help(self, command)
            elif command in serial_list:
                if pre_settings.manager_mode == "ROWMANAGER":
                    print "Server serial session not supported on Row-Manager"
                    return
                serial_stop_command(command_args) 
            elif command == "mte":
                if verify_caller_admin_permission():
                    stop_mte()
                else:
                    print "Access denied"
            else:
                ocsprint("Command not supported: {0}\n".format(command))
                ocsprint("Available commands:\n %s  "% '  \n '.join(map(str,self.stoplist))) 
        except:            
            pass 
        
    def do_wcscli(self, commands):
        """ Start WcsCli compatibility mode
        """
        
        wcsshell().do_wcscli(commands)
        
    def do_wcs(self, commands):
        """ Start WcsCli compatibility mode
        """
        
        wcsshell().do_wcscli(commands)
        
    def changeprompt(self, cmd):
        """ Change shell prompt. Called on load and prompt is configured from cliConfig.ini           
        """
        
        self.prompt = cmd + '# ' 
    
    def do_help(self, commands):          
        try:
            if commands == "" or commands == "help":    
                commandtype_header = "Command Types (type help <topic>)"                                      
                ocsshell().print_topics(commandtype_header, self.commandtypeslist,15,80)
                            
                groups_header = "Command Groups (type help <topic>):"            
                ocsshell().print_topics(groups_header, self.groupslist,15,80)
                
            else:         
                args = commands.lower().split()
                command = args[0]  
                subcommand = ""
                
                if len(args) > 1:
                    subcommand = args[1]     
                
                if command in self.groupslist:
                    if command in network_list:
                        ocs_help.network_commands_list(self)
                    elif subcommand == "power":
                        ocs_help.ocspower_commands_list(self, command)
                    elif subcommand == "fpga":
                        ocs_help.fpga_commands_list(self)
                    elif subcommand == "psu":
                        ocs_help.psu_commands_list(self)
                    elif subcommand == "powermeter" and command == "manager":
                        ocs_help.powermeter_commands_list(self)
                    elif command in system_list:
                        ocs_help.system_commands_list(self)
                    elif command in manager_list:
                        ocs_help.manager_commands_list(self)
                    
                    ocsshell.printusage(self, 'help_', command)
                    
                elif command in self.commandtypeslist:
                    ocsshell.printusage(self, 'do_', command)
                    
                else:
                    ocsshell.printusage(self, 'help_', command)
                    
        except Exception, e:
            print "Help - Exception: {0}".format(e)
            return
    
    def do_ipmitool(self,commands):
        """
            Ipmitool 
            Usage:
                ipmitool -I lan -H <ip address> -U admin -P admin <command>
        """  
        
        try:        
                                       
            args = commands.split()
                
            ocsaudit_log_command("", cmd_type.type_shell, cmd_interface.interface_ocscli, 
                                 "ipmitool", args)
                
            start_ipmitool(args)
            
        except Exception, e:
            print "Ipmitool - Exception: {0}".format(e)
            return 
        
    def do_scp(self,commands):  
        """
            scp 
            Usage:
                scp file.txt root@server:/usr/bin
        """      
        try:        
                                       
            args = commands.split()
           
            ocsaudit_log_command("", cmd_type.type_shell, cmd_interface.interface_ocscli, 
                                 "scp", args)
           
            secure_copy(args)
            
        except Exception,e:
            print "scp - Exception: {0}".format(e)
            return 
        
    def printusage(self, action, command):
        try:
            if action == 'help_':
                doc = getattr(ocs_help, action + command).__doc__
            else:
                doc = getattr(self, action + command).__doc__
                
            if doc:
                self.stdout.write("%s\n"%str(doc))
                return
        except AttributeError:
            pass
            
        self.stdout.write("%s\n"%str(self.nohelp % (command,)))
        
        return
              
    def do_exit(self, cmd):
        """
            Exit from shell command.
            Usage:
                exit
        """
                
        return True
    
    def do_clear(self, cmd):
        """
            Clears shell screen.
            Usage:
                clear
        """ 
               
        os.system('clear')
        
    def postloop(self):
        ocsprint("Exiting..")
        
    def do_EOF(self, line):
        return True
        
    def emptyline(self):
        """
        Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

# Main function
if __name__ == '__main__':
    try:
        ocsshell().cmdloop()
    except KeyboardInterrupt:
        sys.exit(1)
