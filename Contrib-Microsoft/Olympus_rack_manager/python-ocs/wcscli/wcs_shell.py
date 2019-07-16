# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import os
import re
import sys
from distutils import command

# Import commonapi to SYSPATH
sys.path.append(os.path.abspath('/usr/lib/commonapi'))

import ocslog
import wcs_help
import wcs_parse
import pre_settings

from cmd import Cmd
from controls.utils import completion_code, set_failure_dict
from utils_print import print_response
   
    
class wcsshell(Cmd):
    """ WCS Shell Class 
    """
    
    commandlist = ["-getchassisinfo", "-getbladeinfo", "-getpowerstate", "-setpoweron", "-setpoweroff",
                   "-getbladestate", "-setbladeon", "-setbladeoff", "-getnextboot", "-setnextboot",
                   "-setbladeactivepowercycle", "-startbladeserialsession", "-stopbladeserialsession",
                   "-getacsocketpowerstate", "-setacsocketpowerstateon", "-setacsocketpowerstateoff",
                   "-adduser", "-removeuser", "-getnic", "-setnic", "-getserviceversion", "-getbladehealth",
                   "-changeuserpwd", "-changeuserrole", "-getchassisattentionledstatus", "-setchassisattentionledon",
                   "-setchassisattentionledoff", "-getbladepowerreading", "-getbladepowerlimit", "-setbladepowerlimit",
                   "-setbladepowerlimiton", "-setbladepowerlimitoff", "-setbladeattentionledon", "-setbladeattentionledoff",
                   "-setbladedefaultpowerstate", "-getbladedefaultpowerstate", "-getchassishealth", "-startchassismanager",
                   "-stopchassismanager", "-getchassismanagerstatus", "-enablechassismanagerssl", "-disablechassismanagerssl",
                   "-establishcmconnection", "-terminatecmconnection", "-clear"]
    
    def __init__(self):
        # Call superclass constructor
        Cmd.__init__(self, completekey = "tab")     
        Cmd.prompt = "wcscli# "
            
        try:
            # initialize the log 
            ocslog.initialize_log(ocslog.loglevel_t_enum.INFO_LEVEL)
            
        except Exception, e:
            print_response(set_failure_dict ("Failed to initialize log: {0}".format(e)))
                 
        
        # Get group ID
        rc = pre_settings.verify_caller_permission()
        
        if rc != 0:           
            info = set_failure_dict("Failed to verify caller permission, error code: {0}".format(rc), 
                                    completion_code.failure)
            print_response(info)
            sys.exit(rc)
        
        # Get mode type
        rc = pre_settings.get_rm_mode()
        
        if rc != 0:
            info = set_failure_dict("Failed to get rack manager mode, error code: {0}".format(rc),
                                     completion_code.failure)
            print_response(info)
            sys.exit(rc)
            
    def do_help(self, cmd):
        """ Print help 
        """
         
        try:
            if cmd == "" or cmd.lower() == "help" or cmd.lower() == "wcscli":
                wcsshell().print_topics("Supported WcsCli Commands (type wcscli help <topic>) - Type ocscli or exit to return to OcsCli shell", 
                                        self.commandlist, 15, 80)
            else:
                wcs_help.parse_wcscli_help(cmd)
                 
        except Exception, e:
            print set_failure_dict("do_help() Exception {0}".format(str(e)), completion_code.failure) 

    def do_wcscli(self, cmd):
        """ Parse wcscli commands
            IMPORTANT! - Input parsing compatible with WcsCli
        """
        try:
            args = cmd.split()
                    
            if len(args) > 0 and args[0].lower() != "help" and args[0].lower() != "-h":
                for i, command in enumerate(args):
                    if command.lower() in wcsshell.commandlist:
                        args[i] = re.sub('[-]', '', command.lower())
                
                wcs_parse.parse_wcscli_cmd(args)
            else:
                helpcmd = ""
                
                if len(args) > 1:
                    helpcmd = args[1]
                                
                wcsshell.do_help(self, helpcmd)
                    
        except:
            pass
        
    def do_exit(self, cmd):       
        """ Exit from shell
        """
        
        return True  
    
    def do_ocscli(self, cmd):       
        """ Exit from shell
        """
        
        return True      
    
    def do_EOF(self, line):
        """ Exit from shell
        """
        
        return True
    
    def do_clear(self, cmd):
        """
            Clears the screen
        """    
            
        os.system('clear')
        
    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.
        """
        
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')  
    
    def precmd(self, line):
        line = line + " "
        command, line = line.split(' ', 1)
                
        if command.lower() == "-h":
            command = "help"
            
        if command.lower() in ["wcscli", "ocscli", "exit", "help", "clear"]:
            line = command.lower()  + " " +  line
            
        return Cmd.precmd(self, line.strip())    
            
# Main function
if __name__ == '__main__':
    try:
        wcsshell().cmdloop()
        
    except KeyboardInterrupt:
        sys.exit(1)
        