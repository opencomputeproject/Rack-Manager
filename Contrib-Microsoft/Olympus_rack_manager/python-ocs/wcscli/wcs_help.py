# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

import wcs_shell

def parse_wcscli_help(cmd):
    """ Parse input and print corresponding information 
    """
    
    if cmd.lower() == wcs_shell.wcsshell.commandlist[0].lower():
        help_getchassisinfo()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[1].lower():
        help_getbladeinfo()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[2].lower():
        help_getpowerstate()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[3].lower():
        help_setpoweron()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[4].lower():
        help_setpoweroff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[5].lower():
        help_getbladestate()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[6].lower():
        help_setbladeon()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[7].lower():
        help_setbladeoff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[8].lower():
        help_getnextboot()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[9].lower():
        help_setnextboot()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[10].lower():
        help_setbladeactivepowercycle()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[11].lower():
        help_startbladeserialsession()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[12].lower():
        help_stopbladeserialsession()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[13].lower():
        help_getacsocketpowerstate()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[14].lower():
        help_setacsocketpowerstateon()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[15].lower():
        help_setacsocketpowerstateoff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[16].lower():
        help_adduser()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[17].lower():
        help_removeuser()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[18].lower():
        help_getnic()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[19].lower():
        help_setnic()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[20].lower():
        help_getserviceversion()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[21].lower():
        help_getbladehealth()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[22].lower():
        help_changeuserpwd()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[23].lower():
        help_changeuserrole()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[24].lower():
        help_getchassisattentionledstatus()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[25].lower():
        help_setchassisattentionledon()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[26].lower():
        help_setchassisattentionledoff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[27].lower():
        help_getbladepowerreading()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[28].lower():
        help_getbladepowerlimit()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[29].lower():
        help_setbladepowerlimit()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[30].lower():
        help_setbladepowerlimiton()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[31].lower():
        help_setbladepowerlimitoff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[32].lower():
        help_setbladeattentionledon()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[33].lower():
        help_setbladeattentionledoff()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[34].lower():
        help_setbladedefaultpowerstate()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[35].lower():
        help_getbladedefaultpowerstate()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[36].lower():
        help_getchassishealth()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[37].lower():
        help_startchassismanager()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[38].lower():
        help_stopchassismanager()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[39].lower():
        help_getchassismanagerstatus()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[40].lower():
        help_enablechassismanagerssl()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[41].lower():
        help_disablechassismanagerssl()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[42].lower():
        help_establishcmconnection()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[43].lower():
        help_terminatecmconnection()
    elif cmd.lower() == wcs_shell.wcsshell.commandlist[44].lower():
        help_clear()    
    else:
        print "Command Failed. Invalid command."

def help_getchassisinfo():   
    print("""
    Wcscli Command: (GetChassisInfo)
    ========================================================       
    This command gets status information about chassis components
    including the following:
    
    1) Blades
    2) Power Supplies
    3) Rack Manager
    
    Syntax: wcscli -getchassisinfo [-s] [-p] [-c] [-t] [-h]
    
    -s     Show information about blades
    -p     Show information about power supplies
    -c     Show rack manager information
    -t     Show battery information
    -h     Help
    
    Sample Usage:
    wcscli -getchassisinfo -s -p -c     
    """)

def help_getchassishealth():   
    print("""
    Wcscli Command: (GetChassisHealth)
    ========================================================       
    This command gets health status for blades, power supplies,
    batteries and fans:
    
    Syntax: wcscli -getchassishealth [-b] [-p] [-h]
    
    -b     Show blade health information
    -p     Show PSU health information
    -h     Help
    
    Sample Usage:
    wcscli -getchassishealth -b -p -f -t  
    """)
    
def help_getbladeinfo():   
    print("""
    Wcscli Command: (GetBladeInfo)
    ========================================================       
    This command gets status information about the blades
    
    Syntax: wcscli -getbladeinfo <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getbladeinfo -i 9     
    """)
    
def help_getpowerstate():   
    print("""
    Wcscli Command: (GetPowerState)
    ========================================================       
    This command gets AC outlet ON/OFF state of blades
    
    Syntax: wcscli -getpowerstate <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getpowerstate -i 9      
    """)
    
def help_setpoweron():   
    print("""
    Wcscli Command: (SetPowerOn)
    ========================================================       
    This command turns AC outlet ON for the blade
    
    Syntax: wcscli -setpoweron <-i ID> [-a] [-h]
    
    -a     Set for all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setpoweron -i 9     
    """)
    
def help_setpoweroff():   
    print("""
    Wcscli Command: (SetPowerOff)
    ========================================================       
    This command turns AC outlet OFF for the blade
    
    Syntax: wcscli -setpoweroff <-i ID> [-a] [-h]
    
    -a     Set for all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setpoweroff -i 9     
    """)        
    
def help_getbladestate():   
    print("""
    Wcscli Command: (GetBladeState)
    ========================================================       
    This command returns whether blades' chipset receives power
    
    Syntax: wcscli -getbladestate <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getbladestate -i 9    
    """)
    
def help_setbladeon():   
    print("""
    Wcscli Command: (SetBladeOn)
    ========================================================       
    This command supplies power to blades' chipset
    
    Syntax: wcscli -setbladeon <-i ID> [-a] [-h]
    
    -a     Set for all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladeon -i 9    
    """)
    
def help_setbladeoff():   
    print("""
    Wcscli Command: (SetBladeOff)
    ========================================================       
    This command removes power from blades' chipset
    
    Syntax: wcscli -setbladeoff <-i ID> [-a] [-h]
    
    -a     Set for all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladeoff -i 9     
    """)
    
def help_getnextboot():   
    print("""
    Wcscli Command: (GetNextBoot)
    ========================================================       
    This command gets pending boot order to be applied on next
    blade boot
    
    Syntax: wcscli -getnextboot <-i ID> [-h]
    
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getnextboot -i 9    
    """)
    
def help_setnextboot():   
    print("""
    Wcscli Command: (SetNextBoot)
    ========================================================       
    This command sets device boot type for next blade boot. A
    soft power cycle is required for this setting to take effect
    
    Syntax: wcscli -setnextboot <-i ID> <-t TYPE> [-h]
    
    -i     Blade ID [1-48]
    -t     Boot Type [1-5]
                    1. No override
                    2. Force PXE
                    3. Force default HDD
                    4. Force into BIOS setup
                    5. Force boot from Floppy/primary removable media
    -h     Help
    
    Sample Usage:
    wcscli -setnextboot -i 9 -t 3    
    """)
    
def help_setbladeactivepowercycle():   
    print("""
    Wcscli Command: (SetBladeActivePowerCycle)
    ========================================================       
    This command power cycles or soft resets the blades
    
    Syntax: wcscli -setbladeactivepowercycle <-i ID> [-a] [-h]
    
    -a     Set for all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladeactivepowercycle -i 9     
    """)
    
def help_startbladeserialsession():   
    print("""
    Wcscli Command: (StartBladeSerialSession)
    ========================================================       
    This command starts a serial session to the blade
    
    Syntax: wcscli -startbladeserialsession <-i ID> [-h]
    
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -startbladeserialsession -i 9      
    """)
    
def help_stopbladeserialsession():   
    print("""
    Wcscli Command: (StopBladeSerialSession)
    ========================================================       
    This command terminates active serial session to the blade
    
    Syntax: wcscli -stopbladeserialsession <-i ID> [-h]
    
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -stopbladeserialsession -i 9    
    """)
    
def help_getacsocketpowerstate():   
    print("""
    Wcscli Command: (GetACSocketPowerState)
    ========================================================       
    This command gets AC socket state of port
    
    Syntax: wcscli -getacsocketpowerstate <-p ID> [-h]
    
    -p     Port ID [1-4]
    -h     Help
    
    Sample Usage:
    wcscli -getacsocketpowerstate -p 1      
    """)
    
def help_setacsocketpowerstateon():   
    print("""
    Wcscli Command: (SetACSocketPowerStateOn)
    ========================================================       
    This command turns AC socket ON for the port
    
    Syntax: wcscli -setacsocketpowerstateon <-i ID> [-h]
    
    -p     Port ID [1-4]
    -h     Help
    
    Sample Usage:
    wcscli -setacsocketpowerstateon -p 1     
    """)
    
def help_setacsocketpowerstateoff():   
    print("""
    Wcscli Command: (SetACSocketPowerStateOff)
    ========================================================       
    This command turns AC socket OFF for the port
    
    Syntax: wcscli -setacsocketpowerstateoff <-i ID> [-h]
    
    -p     Port ID [1-4]
    -h     Help
    
    Sample Usage:
    wcscli -setacsocketpowerstateoff -p 1     
    """)

def help_adduser():   
    print("""
    Wcscli Command: (AddUser)
    ========================================================       
    This command creates new chassis controller user
    
    Syntax: wcscli -adduser <-u username> <-p password> [-a] [-o] [-r] [-h]
    
    -u     Username
    -p     Password
    -a     Admin Privileges
    -o     Operator Privileges
    -r     User Privileges
    -h     Help
    
    Sample Usage:
    wcscli -adduser -u myname -p pass!123 -a      
    """)

def help_removeuser():   
    print("""
    Wcscli Command: (RemoveUser)
    ========================================================       
    This command removes existing chassis controller user
    
    Syntax: wcscli -removeuser <-u username> [-h]
    
    -u     Username
    -h     Help
    
    Sample Usage:
    wcscli -removeuser -u myname
    """)

def help_changeuserpwd():   
    print("""
    Wcscli Command: (ChangeUserPwd)
    ========================================================       
    This command changes existing chassis controller user password
    
    Syntax: wcscli -changeuserpwd <-u username> <-p password> [-h]
    
    -u     Username
    -p     Password
    -h     Help
    
    Sample Usage:
    wcscli -changeuserpwd -u myname -p newpassword
    """)
    
def help_changeuserrole():   
    print("""
    Wcscli Command: (ChangeUserRole)
    ========================================================       
    This command changes existing chassis controller user role
    
    Syntax: wcscli -changeuserrole <-u username> [-a] [-o] [-r] [-h]
    
    -u     Username
    -a     Admin Privileges
    -o     Operator Privileges
    -r     User Privileges
    -h     Help
    
    Sample Usage:
    wcscli -changeuserrole -u myname -a
    """)
    
def help_getnic():   
    print("""
    Wcscli Command: (GetNIC)
    ========================================================       
    This command gets the chassis controller network properties
    
    Syntax: wcscli -getnic [-h]
    
    -h     Help
    
    Sample Usage:
    wcscli -getnic
    """)

def help_setnic():   
    print("""
    Wcscli Command: (SetNIC)
    ========================================================       
    This command sets rack manager network properties:s
    
    Syntax: wcscli -setnic <-a IP addr source> <-i IP addr>
                           <-m subnetmask> <-g gateway>
                           <-p primary DNS> <-d secondary DNS>
                           <-t network interface number> [-h]
    
    -a     IP Address Source [DHCP/STATIC]
    -i     IP Address - Required if static address source
    -m     Subnet Mask - Required if static address source
    -g     Gateway
    -p     Primary DNS server address
    -d     Secondary DNS server address - Only valid if primary is specified
    -t     Network Interface Controller Number - Default is zero
    -h     Help
    
    Sample Usage:
    wcscli -setnic -m 255.255.0.0 -i 10.160.148.220 -p 10.160.148.220 -d 127.0.0.1 -a static -t 0 
    """)

def help_getserviceversion():   
    print("""
    Wcscli Command: (GetServiceVersion)
    ========================================================       
    This command gets the chassis manager service assembly version
    
    Syntax: wcscli -getserviceversion [-h]
    
    -h     Help
    
    Sample Usage:
    wcscli -getserviceversion
    """)
    
def help_getbladehealth():   
    print("""
    Wcscli Command: (GetBladeHealth)
    ========================================================       
    This command gets health information about the blade, 
    including the following:
    
    1) CPU
    2) Memory
    3) PCIe
    4) Sensor
    5) FRU
    
    Syntax: wcscli -getbladehealth <-i ID> [-q] [-m] [-p] [-s] [-t] [-f] [-h]
    
    -i     Blade ID [1-48]
    -q     Show information about blade CPU
    -m     Show information about blade memory
    -p     Show information about blade PCIe
    -s     Show information about blade sensors
    -t     Show information about power temperature sensors
    -f     Show information about blade FRU
    -h     Help
    
    Sample Usage:
    wcscli -getbladehealth -i 9 
    """)
    
def help_getchassisattentionledstatus():   
    print("""
    Wcscli Command: (GetChassisAttentionLedStatus)
    ========================================================       
    This command gets the chassis manager attention led status
    
    Syntax: wcscli -getchassisattentionledstatus [-h]
    
    -h     Help
    
    Sample Usage:
    wcscli -getchassisattentionledstatus
    """)

def help_setchassisattentionledon():   
    print("""
    Wcscli Command: (SetChassisAttentionLedOn)
    ========================================================       
    This command sets the chassis manager attention led on
    
    Syntax: wcscli -setchassisattentionledon [-h]
    
    -h     Help
    
    Sample Usage:
    wcscli -setchassisattentionledon
    """)

def help_setchassisattentionledoff():   
    print("""
    Wcscli Command: (SetChassisAttentionLedOff)
    ========================================================       
    This command sets the chassis manager attention led off
    
    Syntax: wcscli -setchassisattentionledoff [-h]
    
    -h     Help
    
    Sample Usage:
    wcscli -setchassisattentionledoff
    """)

def help_getbladepowerreading():
    print("""
    Wcscli Command: (GetBladePowerReading)
    ========================================================
    This command returns the blade's power reading
    
    Syntax: wcscli -getbladepowerreading <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getbladepowerreading -i 9
    """)

def help_getbladedefaultpowerstate():
    print("""
    Wcscli Command: (GetBladeDefaultPowerState)
    ========================================================
    This command returns the default power on state of a blade
    
    Syntax: wcscli -getbladedefaultpowerstate <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getbladedefaultpowerstate -i 9
    """)
    
def help_setbladedefaultpowerstate():   
    print("""
    Wcscli Command: (SetBladeDefaultPowerState)
    ========================================================       
    This command sets the default power on state of a blade
    
    Syntax: wcscli -setbladedefaultpowerstate <-i ID> <-s state> [-a] [-h]
    
    -s     State [0 - stay off, 1 - power on]
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladedefaultpowerstate -s 1 -i 9
    """)

def help_getbladepowerlimit():
    print("""
    Wcscli Command: (GetBladePowerLimit)
    ========================================================
    This command returns the blade's power limit
    
    Syntax: wcscli -getbladepowerlimit <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -getbladepowerlimit -i 9
    """)
    
def help_setbladepowerlimit():   
    print("""
    Wcscli Command: (SetBladePowerLimit)
    ========================================================       
    This command sets the blade power limit
    
    Syntax: wcscli -setbladepowerlimit <-i ID> <-l limit> [-a] [-h]
    
    -l     Power limit in Watts
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladepowerlimit -l 200
    """)

def help_setbladepowerlimiton():   
    print("""
    Wcscli Command: (SetBladePowerLimitOn)
    ========================================================       
    This command sets the blade power limit on
    
    Syntax: wcscli -setbladepowerlimiton <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladepowerlimiton
    """)

def help_setbladepowerlimitoff():   
    print("""
    Wcscli Command: (SetBladePowerLimitOff)
    ========================================================       
    This command sets the blade power limit off
    
    Syntax: wcscli -setbladepowerlimitoff <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladepowerlimitoff
    """)

def help_setbladeattentionledon():   
    print("""
    Wcscli Command: (SetBladeAttentionLedOn)
    ========================================================       
    This command sets the blade attention led on
    
    Syntax: wcscli -setbladeattentionledon <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladeattentionledon
    """)

def help_setbladeattentionledoff():   
    print("""
    Wcscli Command: (SetBladeAttentionLedOff)
    ========================================================       
    This command sets the blade attention led off
    
    Syntax: wcscli -setbladeattentionledoff <-i ID> [-a] [-h]
    
    -a     Show all blades
    -i     Blade ID [1-48]
    -h     Help
    
    Sample Usage:
    wcscli -setbladeattentionledoff
    """)
    
def help_startchassismanager():   
    print("""
    Wcscli Command: (StartChassisManager)
    ========================================================       
    
    Syntax: wcscli -startchassismanager [-h]

    -h     Help
    
    Sample Usage:
    wcscli -startchassismanager
    """)
    
def help_stopchassismanager():   
    print("""
    Wcscli Command: (StopChassisManager)
    ========================================================       
    
    Syntax: wcscli -stopchassismanager [-h]

    -h     Help
    
    Sample Usage:
    wcscli -stopchassismanager
    """)

def help_getchassismanagerstatus():   
    print("""
    Wcscli Command: (GetChassisManagerStatus)
    ========================================================       
    
    Syntax: wcscli -getchassismanagerstatus [-h]

    -h     Help
    
    Sample Usage:
    wcscli -getchassismanagerstatus
    """)   

def help_enablechassismanagerssl():   
    print("""
    Wcscli Command: (EnableChassisManagerSSL)
    ========================================================       
    
    Syntax: wcscli -EnableChassisManagerSSL [-h]

    -h     Help
    
    Sample Usage:
    wcscli -enablechassismanagerssl
    """)
    
def help_disablechassismanagerssl():   
    print("""
    Wcscli Command: (DisableChassisManagerSSL)
    ========================================================       
    
    Syntax: wcscli -DisableChassisManagerSSL [-h]

    -h     Help
    
    Sample Usage:
    wcscli -disablechassismanagerssl
    """)

def help_clear():   
    print("""
    Wcscli Command: (Clear)
    ========================================================       
    This command clears user command history and clears display screen
    
    Syntax: wcscli -clear [-h]

    -h     Help
    
    Sample Usage:
    wcscli -clear
    """)

def help_terminatecmconnection():   
    print("""
    Wcscli Command: (TerminateCMConnection)
    ========================================================       
    
    Syntax: wcscli -terminatecmconnection [-h]

    -h     Help
    
    Sample Usage:
    wcscli -terminatecmconnection
    """)

def help_establishcmconnection():   
    print("""
    Wcscli Command: (EstablishCMConnection)
    ========================================================       
    
    Syntax: wcscli -establishcmconnection <-u username> <-x password> [-m host_name] [-p port] 
                                          [-s SSL_option] [-b batchfileName] [-v] [-h]

    -u     username to connect to CM service. Use domain\username if not using local domain
    -x     password to connect to CM service
    -m     host_name - Specify host name for Chassis Manager 
           (Optional. Default is localhost.
           For serial connection, localhost is assumed.)
    -p     port - Specify a valid Port to connect to for Chassis Manager
           (Option. Default is 8000)
    -s     Select Chassis Manager (CM)'s SSL Encryption mode
           (Optional. 0: disabled/ 1: (default): enabled)
           Enter 0 if CM is not configured to use SSL encryption
           (SSL disabled in CM)
           Enter 1 if CM required SSL Encryption (SSL enabled in CM)
    -b     Optional batch file option (not supported in serial mode).
    -v     Get CLI version information
    -h     Help
    
    Sample Usage:
    wcscli -establishcmconnection
    """)
