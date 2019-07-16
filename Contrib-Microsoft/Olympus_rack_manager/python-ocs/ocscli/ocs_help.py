# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from ocsshell import *
from utils_print import ocsprint

def network_commands_list(self):
    networkcmdlist = ['interface','route' ,'static','dhcp','enable','disable']
    
    commandtype_header = "Network Commands list (type help <command>)"   
    ocsprint ("")                                   
    ocsshell().print_topics(commandtype_header, networkcmdlist,15,80)
    
def system_commands_list(self):
    showsystemcmdlist = ['info', 'health','tpmphysicalpresence', 'nextboot', 'defaultpower', 'state', 
                         'presence', 'readlog', 'readlogwithtimestamp', 'biosconfig', 'bioscode', 'fru', 
                         'datasafepolicy', 'nvme', "type"]

    setsystemcmdlist = ['tpmphysicalpresence', 'nextboot', 'defaultpower', 'on', 'off',
                         'reset', 'ledon', 'ledoff', 'clearlog', 
                        'biosconfig', 'datasafepolicy', 'rmediamount', 'rmediaunmount']

    showsystemsubcmdlist = ['power', 'fpga' , 'psu']

    setsystemsubcmdlist = ['power', 'fpga' , 'psu']
        
    show_commandtype_header = "Show System Commands list (type help <command>)"   
    show_subcommandtype_header = "Show System Subcommands list (type help <command>)" 
    set_commandtype_header = "Set System Commands list (type help <command>)"  
    set_subcommandtype_header = "Set System Subcommands list (type help <command>)" 
     
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showsystemcmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(show_subcommandtype_header, showsystemsubcmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setsystemcmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_subcommandtype_header, setsystemsubcmdlist,15,80)
    
def manager_commands_list(self):
    showmanagercmdlist = ['ledstatus', 'info', 'portstate', 'relay', 'health', 'tftp status', 'nfs status','fru', 
                          'log','inventory', 'time', 'type', 'scandevice', 'fwupdate']
    setmanagercmdlist = ['led on', 'led off', 'relay on', 'relay off', 'tftp start', 'tftp stop', 'porton','portoff',
                         'tftp get', 'nfs start', 'nfs stop', 'fwupdate', 'clearlog', 'time']

    showmanagersubcmdlist = ['power', 'powermeter', 'network']

    setmanagersubcmdlist = ['power', 'powermeter', 'network']
    
    show_commandtype_header = "Show Rack Manager Commands list (type help <command>)" 
    show_subcommandtype_header = "Show Rack Manager Subcommands list (type help <command>)"   
    set_commandtype_header = "Set Rack Manager Commands list (type help <command>)" 
    set_subcommandtype_header = "Set Rack Manager Subcommands list (type help <command>)" 
      
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showmanagercmdlist,15,80)
    ocsprint ("")                                      
    ocsshell().print_topics(show_subcommandtype_header, showmanagersubcmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setmanagercmdlist,15,80)
    ocsprint ("")                                      
    ocsshell().print_topics(set_subcommandtype_header, setmanagersubcmdlist,15,80)
    
def ocspower_commands_list(self, command):
    if command == "manager":
        showpowercmdlist = ['reading', 'status']
        setpowercmdlist = ['clearfaults']
    elif command == "system":
        showpowercmdlist = ['limit', 'reading', 'alert', 'throttle']
        setpowercmdlist = ['limit value', 'limit on', 'limit off', 'alert']
    else: 
        showpowercmdlist = []
        setpowercmdlist = []
    
    show_commandtype_header = "Show OcsPower Commands list (type sh system or manager power <command> -h)"   
    set_commandtype_header = "Set OcsPower Commands list (type set system or manager power <command> -h)" 
      
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showpowercmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setpowercmdlist,15,80)

def powermeter_commands_list(self):
    showpowercmdlist = ['limit', 'alert', 'reading', 'version']
    setpowercmdlist = ['limit', 'alert', 'clearmax', 'clearfaults']
    
    show_commandtype_header = "Show PowerMeter Commands list (type sh manager powermeter <command> -h)"   
    set_commandtype_header = "Set PowerMeter Commands list (type set manager powermeter <command> -h)" 
      
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showpowercmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setpowercmdlist,15,80)
    
def fpga_commands_list(self):
    showfpgacmdlist = ['health', 'mode', 'temp', 'i2cversion', 'assetinfo']
    setfpgacmdlist = ['bypass enable', 'bypass disable']
    
    show_commandtype_header = "Show FPGA Commands list (type sh system fpga <command> -h)"   
    set_commandtype_header = "Set FPGA Commands list (type set system fpga <command> -h)" 
      
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showfpgacmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setfpgacmdlist,15,80)
    
def psu_commands_list(self):
    showpsucmdlist = ['read', 'battery', 'update', 'version']
    setpsucmdlist = ['clear', 'battery', 'update']
    
    show_commandtype_header = "Show PSU Commands list (type sh system psu <command> -h)"   
    set_commandtype_header = "Set PSU Commands list (type set system psu <command> -h)" 
      
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showpsucmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setpsucmdlist,15,80)
    
def user_commands_list(self):
    showusercmdlist = ['info']
    setusercmdlist = ['add', 'update', 'delete']
        
    show_commandtype_header = "Show User Commands list (type help <command>)"   
    set_commandtype_header = "Set User Commands list (type help <command>)"   
    ocsprint ("")                                   
    ocsshell().print_topics(show_commandtype_header, showusercmdlist,15,80)
    ocsprint ("")                                   
    ocsshell().print_topics(set_commandtype_header, setusercmdlist,15,80)

##############################################################################
    # Network  help commands
##############################################################################
def help_network(self,commands):      
    """
    Ocscli Network "show" Commands : 
    =======================================================
    interface		 route 
    
    Ocscli Network "set" Commands: (Network configuration)
    ========================================================       
    static: Set interface to static IP address:
           
    dhcp: Set interface to DHCP:
    
    enable : Will bring interface up if it is currently down
    
    disable : Will bring interface down if it is currently up
               
    """  
        
def help_interface(self,command):        
    """
        interface: Shows interface details
        ====================================================
        Usage:            
            show/sh network interface -i {eth0, eth1}        
            
        -i -- interface name {"eth0" or "eth1"}     
        [-h] -help; display the correct syntax
         
         Syntax: show network interface -h         
    """  
def help_route(self,command):        
    """
        route: Show management network route
        ====================================================
        Usage:            
            show/sh network route            
            
			Syntax: show network route    
    """ 

def help_static(self,command):        
    """
        static:Set interface to static IP address
        ==============================================
        Usage:            
            set network static -i {interface name} -a {IP address} -s {subnetmask} -g {gateway}
            
        -i -- interface name {"eth0" or "eth1"}
        -a -- IP Address (Required for static)
        -s -- Subnetmask (Required for static)
        -g -- gateway (Optional for static IP)
        
        [-h] -help; display the correct syntax
        
        Syntax: set network static -h 
    """     
    
def help_dhcp(self,command):        
    """
        dhcp:Set interface to dhcp
        ==============================================
        Usage:
            set network dhcp -i {interface name} -d 
        
        -i -- interface name {"eth0" or "eth1"}        
        
        [-h] -help; display the correct syntax   
             
        Syntax: set network dhcp -h
    """  
    
def help_enable(self,command):        
    """
        setinterfaceenable:
        Will bring interface up if it is currently down.
        =================================================
        Usage:
            set network enable -i {interface name} 
        
        -i -- interface name {"eth0" or "eth1"}
           
        [-h] -help; display the correct syntax        
    """
def help_disable(self,command):        
    """
        setinterfacedisable:
        Will bring interface down if it is currently up.
        =================================================
        Usage:
            set network disable -i {interface name} 
        
        -i -- interface name {"eth0" or "eth1"}
           
        [-h] -help; display the correct syntax
        
    """
##############################################################################
    # System help commands
##############################################################################
def help_system(self,commands):      
    """ """

def help_serial(self,commands):      
    """  
    System "Serial" Commands: 
    ========================================================       
    startserialsession    stopserialsession
                
    """ 

def help_info(self, commands):
    """
        systeminfo : Shows system information
        =======================================================
        Usage:
            show system info -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """ 

def help_tpmphysicalpresence(self, commands):
    """
        Show: 
        
        tpmphysicalpresence: Retrieves a bit flag stored in the BMC that 
        indicates whether or not physical presence is asserted.
        =======================================================================
        Usage:
            show system tpm presence -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax   
        
        #######################################
        Set:
        
        tpmphysicalpresence: Sets a bit flag in the BMC.
        =======================================================================
        Usage:
            set system tpm presence -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
        -p -- presence, physical presence flag {0 (Not assesrted: flag is false),1 (Asserted: flag is true)} 
        
        [-h] -help; display the correct syntax      
    """

def help_nextboot(self, commands):
    """
        Show:       
        nextboot: This command gets the pending boot order to be applied 
        the next time the server boots.
        =======================================================================
        Usage:
            show system nextboot -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
        
        #######################################
        Set:
        
        nextboot: This command sets the device boot type of the start boot device 
        during the subsequent reboot for a server.
        ============================================================================
        Usage:
            set system nextboot -i {serverid} -t {boot_type}
        
        -i -- serverid, the target server number. Typically 1-48
        -t -- boot_type: 1.none:  No override
                         2.pxe:   Force PXE boot;
                         3.disk:  Force boot from default Hard-drive;
                         4.bios:  Force boot into BIOS Setup;
                         5.floppy: Force boot from Floppy/primary removable media
           
        [-h] -help; display the correct syntax 
        syntax:
            set system nextboot -i 1 -t none 
        
    """
def help_on(self, commands):
    """
        on: This command supplies the power to the server chipset,initializing the
                    boot process. This command is used to soft power the server ON. 
        =================================================================================
        Usage:
            set system on -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """    
def help_off(self, commands):
    """
        off: This command removes the power to the server chipset.                    
                    This command is used to soft power the server OFF. 
        ====================================================================
        Usage:
            set system off -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """
def help_state(self, commands):
    """
        state: This command gets the ON/OFF state of the server.
                        (whether the server chipset is receiving power). 
        ========================================================================
        Usage:
            show system state -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """ 
    
def help_defaultstate(self, commands):
    """
        defaultpowerstate: This command gets the default power state of the server ON/OFF.
        =================================================================================
        Usage:
            show system default power -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
        
        ################################################################################
        Set:
        
        defaultpowerstate: This command sets the default power state of the server ON/OFF.
        =================================================================================
        Usage:
            set system default power -i {serverid} -s {state}
        
        -i -- serverid, the target server number. Typically 1-48
        -s -- state, can be 0(default power state OFF) or 1 (default power state ON)
                
        [-h] -help; display the correct syntax
        
    """
def help_reset(self, commands):
    """
        reset: This command power cycles or soft resets the server(s).
        ==============================================================================
        Usage:
            set system reset -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """   
def help_ledon(self, commands):
    """
        ledon: This command turns the server attention LED on.
        ====================================================================
        Usage:
            set system led on -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """ 

def help_ledoff(self, commands):
    """
        ledoff: This command turns the server attention LED off.
        =====================================================================
        Usage:
            set system led off -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """ 
def help_readlog(self, commands):
    """
        readlog: This command reads the log from a  server.
        =====================================================================
        Usage:
            show system log read -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """ 
def help_clearlog(self, commands):
    """
        clearlog: This command clears the log from a  server.
        =====================================================================
        Usage:
            set system log clear -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """
def help_readlogwithtimestamp(self, commands):
    """
        readlogwithtimestamp: This command reads the log from a server based on
                              start and end date time stamp.
        ======================================================================================
        Usage:
            show system log timestamp -i {serverid} -s {starttimestamp} -e {endtimestamp} 
        
        -i -- serverid, the target server number. Typically 1-48
        -s -- start date time, start date time stamp ex: M/D/Y-HH:MM:SS
        -e -- end date time, end date time stamp ex: M/D/Y-HH:MM:SS
                
        [-h] -help; display the correct syntax 
    """ 
    
def help_bioscode(self, commands):
    """
        bioscode: This command gets the post code for the server with specified serverid.
        ==================================================================================
        Usage:
            show system bios code -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
    """   
 
def help_biosconfig(self, commands):
    """
        biosconfig: Shows currentconfig,choosenconfig and availableconfigs 
        =====================================================================
        Usage:
            show system bios config -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
                
        [-h] -help; display the correct syntax 
        
        #####################################################################
        Set:
        
        biosconfig: Sets the configuration that the user expects in the subsequent reboot of the server.
        =================================================================================================
        Usage:
            set system bios config -i {serverid} -j {major-config} -n {minor-config} 
        
        -i -- serverid, the target server number. Typically 1-48
        -j -- major-config, major configuration number 
        -n -- minor-config, minor configuration number 
              (refer to showbiosconfig for available configurations)
                
        [-h] -help; display the correct syntax 
        
    """   

def help_presence(self, commands):
    """
        showportpresence: This command gets the presence (True/False) of the server. 
        ===========================================================================
        Usage:
            show system port presence -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """ 

def help_startserialsession(self, commands):
    """
        startserialsession: Starts the server serial session.
        ============================================================
        Usage:
            start serial session -i {serverid} -f
        
        -i -- serverid, the target server number. Typically 1-48

        -f -- optional command, that will forcefully start session by killing any existing session 
           
        [-h] -help; display the correct syntax        
    """
def help_stopserialsession(self, commands):
    """
        stopserialsession: Stops the server serial session.
        ============================================================
        Usage:
            stop serial session -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """


################################################################################################################
    # RACK MANAGER Help Commands
################################################################################################################
def help_manager(self,commands):      
    """ """
    
def help_fru(self,commans):
    """
        Showmanagerfru: This command shows the manager fru data.
        ============================================================
        Usage:
            show manager fru [-b{mb,pib,acdc} 
        
        -b -- manager boardname, default set to mb
        Rack Manager board names {mb, pib,acdc}
        Row Manager board names {mb, pib}
           
        Setmanagerfru: This command setd the fru data to manager.
        ============================================================
        Usage:
            set manager fru [-b{mb,pib,acdc} -f <filename> 
        
        -b -- manager boardname, default set to mb
        -f -- filename to write fru data
        Rack Manager board names {mb, pib,acdc}
        Row Manager board names {mb, pib}
           
        [-h] -help; display the correct syntax      
    """
    
    
def help_relay(self, commands):
    """
        relay: This command shows the status of chassis AC sockets.
        ============================================================
        Usage:
            show manager -p {port_id}
        
        -p -- port_id, the target port number (Typically 1 to 4)
           
        [-h] -help; display the correct syntax        
    """
    
def help_relayon(self, commands):
    """
        relayon: This command turns the manager AC sockets ON.
        ============================================================
        Usage:
            set manager relayon -p {port_id}
        
        -p -- port_id, the target port number (Typically 1 to 4)
           
        [-h] -help; display the correct syntax        
    """
    
def help_relayoff(self, commands):
    """
        relayoff: This command turns the manager AC sockets OFF.
        ============================================================
        Usage:
            set manager relayoff -p {port_id}
        
        -p -- port_id, the target port number (Typically 1 to 4)
           
        [-h] -help; display the correct syntax        
    """

def help_managerinfo(self, commands):
    """
        info: This command returns rack manager info.
        ===========================================================
        Usage:
            show manager info

        [-h] -help; display the correct syntax
    """

def help_managerportstatus(self, commands):
    """
        portstatus: This command returns the power port status.
        ===========================================================
        Usage:
            show manager port -i {port_id}
        
        -i --port_id, the target port number {1-48, or 0 for all}

        [-h] -help; display the correct syntax
    """



def help_attentionledstatus(self, commands):
    """
        attentionledstatus: This command returns the attention led status.
        =================================================================
        Usage:
            show manager led

        [-h] -help; display the correct syntax
    """


def help_managerattentionledon(self, commands):
    """
        ledon: This command turns attention led on.
        ===========================================================
        Usage:
            set manager led on
        
        [-h] -help; display the correct syntax
    """

def help_managerattentionledoff(self, commands):
    """
        ledoff: This command turns attention led off.
        =================================================================
        Usage:
            set manager led off

        [-h] -help; display the correct syntax
    """

def help_porton(self, commands):
    """
        porton: This command turns the AC outlet power ON for the server/Port. 
        =======================================================================
        Usage:
            set manager port on -i {portid}
        
        -i -- portid, the target port id. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """ 
def help_portoff(self, commands):
    """
        portoff: This command turns the AC outlet power OFF for the server/Port. 
        =======================================================================
        Usage:
            set manager port off -i {portid}
        
        -i -- portid, the target port id. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """ 
def help_portstate(self, commands):
    """
        portstate: This command gets the AC outlet power ON/OFF state of servers/Ports
                    (whether or not the servers are receiving AC power). 
        ===========================================================================
        Usage:
            show manager port state -i {portid}
        
        -i -- portid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax 
    """ 


################################################################################################################
    # USER Help Commands
################################################################################################################
def help_user(self,commands):      
    """
    Ocscli User "show" Commands : 
    =======================================================
    info
    
    Ocscli User "set" Commands: 
    ========================================================       
    add    update    delete        
               
    """ 
    
def help_display(self, commands):
    """
        info: This command lists user properties.
        ============================================================
        Usage:
            show user info -u {username} -r {role}
        
        -u -- username, if type is users, filter by users
        -r -- role, if type is role, filter users by role 
     
        [-h] -help; display the correct syntax        
    """
    
def help_add(self, commands):
    """
        add: This command adds a new user.
        ============================================================
        Usage:
            set user add -u {username} -p {password} -r {role}
        
        -u -- username
        -p -- password
        -r -- role, {admin, operator, user}

           
        [-h] -help; display the correct syntax        
    """
    
def help_update(self, commands):
    """
        update: This command updates password or role.
        ============================================================
        Usage:
            set user update -t {type} -u {username} -p {new password} -r {new role}
        
        -t -- type, select password or role to update
        -u -- username, select user to update
        -p -- new password, if type is password, new password
        -r -- new role, if type is role, new role
           
        [-h] -help; display the correct syntax        
    """
    
def help_delete(self, commands):
    """
        delete: This command deletes a user.
        ============================================================
        Usage:
            set user delete -u {username}
        
        -u -- username, username of user to delete
           
        [-h] -help; display the correct syntax        
    """
    
################################################################################################################
    # OcsPower Help Commands
################################################################################################################

def help_systempowerlimit(self, commands):
    """
        Show:
        limit: Shows the power limit for a server
        =======================================================
        Usage:
            show system power limit -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax   
        
        ########################################################
        Set: 
        limit: Sets the power limit for a server
        =======================================================
        Usage:
            set system power limit -i {serverid} -l {powerlimit}
        
        -i -- serverid, the target server number. Typically 1-48
        -l -- Power limit per server in watts
           
        [-h] -help; display the correct syntax        
    """
             
def help_systempowerreading(self, commands):
    """
        reading: Shows the power reading for a server
        ========================================================
        Usage:
            show system power reading -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """

def help_systempowerlimiton(self, commands):
    """
        limiton: Activates the powerlimit for a server, and 
                         enables power throttling.
        ==================================================================
        Usage:
            set system power limiton -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """
def help_systempowerlimitoff(self, commands):
    """
        limitoff: Desctivates the powerlimit for a server, and disables
                          power throttling.
        =======================================================================
        Usage:
            set system power limitoff -i {serverid}
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """
def help_systempoweralertpolicy(self, commands):
    """
        Show:
        
        alertpolicy: Shows the server power alert policy
        =====================================================
        Usage:
            show system power alertpolicy -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax    
        
        ########################################################
        Set:        
        
        alertpolicy: Sets the power alert policy for a server
        ==========================================================
        Usage:
            set system power alertpolicy -i {serverid} -p {powerlimit} -e {alertaction}
                                        -r {remediationaction} -f {throttleduration}
                                        -d {removedelay}
        
        -i -- serverid, the target server number. Typically 1-48
        -p -- Power limit per server in watts
        -e -- Alert action (0:nothing, 1:throttle, 2:fastthrottle)
        -r -- Remediation action (0:nothing, 1:remove limit and rearm alert, 2:rearm alert)
        -f -- Throttle Duration, Fast throttle duration in milliseconds
        -d -- Remove Delay, Auto remove power limit delay in seconds
           
        [-h] -help; display the correct syntax  
            
    """

def help_systemthrottlingstatistics(self, commands):
    """
        throttlingstatistics: Shows the server throttling statistics
        ============================================================
        Usage:
            show system power throttlingstatistics -i {serverid} 
        
        -i -- serverid, the target server number. Typically 1-48
           
        [-h] -help; display the correct syntax        
    """
def help_managerpoweralertpolicy(self, commands):
    """
        Show:
        
        alertpolicy: This command returns the manager power alert policy.
        ======================================================================
        Usage:
            show manager power alertpolicy

        [-h] -help; display the correct syntax
        
        Set:
        
        alertpolicy: This command sets the manager power alert policy.
        ======================================================================
        Usage:
            set manager power alertpolicy -e {policy} -p {powerlimit}

        -e --policy, the power alert policy setting {0:disable, 1:enable}
        -p --powerlimit, the power limit value in watts

        [-h] -help; display the correct syntax
    """

def help_managerpowerlimitpolicy(self, commands):
    """
        Show:
        
        limitpolicy: This command returns the manager power limit policy.
        =======================================================================
        Usage:
            show manager power limitpolicy

        [-h] -help; display the correct syntax

        Set:

        limitpolicy: This command sets the manager power limit policy.
        =======================================================================
        Usage:
            set manager power limitpolicy -p {powerlimit}

        -p --powerlimit, the power limit value in watts

        [-h] -help; display the correct syntax
    """
    
def help_managerpowerreading(self, commands):
    """
        reading: This command returns manager power statistics.
        =================================================================
        Usage:
            show manager power reading

        [-h] -help; display the correct syntax
    """

def help_managerpruversion(self, commands):
    """
        pruversion: This command returns the manager pru version.
        =================================================================
        Usage:
            show manager power pruversion

        [-h] -help; display the correct syntax
    """

def help_managerclearmaxpower(self, commands):
    """
        clearmaxpower: This command clears max manager power.
        =================================================================
        Usage:
            set manager power clearmaxpower

        [-h] -help; display the correct syntax
    """

def help_managerclearpowerfaults(self, commands):
    """
        clearfaults: This command clears manager feed power faults.
        =================================================================
        Usage:
            set manager power clearfaults

        [-h] -help; display the correct syntax
    """
