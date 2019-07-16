# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.


import os
import ast
import cmd
import ocslog

from ocspaths import *
from manage_powerport import *
from manage_network import *
from manage_user import *
from manage_rack_manager import *
from manage_ocspower import *
from manage_powermeter import *
from manage_fpga import *
from manage_nvdimm import *
from manage_rmedia import *
from ipmicmd_library import *
from bladetpmphypresence_lib import * 
from bladenextboot_lib import *
from bladepowerstate_lib import *
from bladelog_lib import *
from bladebios_lib import *
from bladeinfo_lib import *
from blade_fw_update import *
from server_session import *
from utils import set_failure_dict, set_success_dict, completion_code

############################################################################################################
# Rack Manager
###########################################################################################################
def system_rackmanager_display(parameters):
    try:
        action_name = ''
        reset_type = ''
        boardname = ''
        server = ''
        manager = ''
        power = ''
        memory = ''
        sensor = ''
        rm_mode = ''
        port_id = -1
        starttime = -1
        endtime = -1
        startid = -1
        endid = -1 
        component = -1
        loglevel = -1
        deviceid = -1
        
        if 'action' in parameters.keys():
            action_name = parameters["action"]
            
        if 'starttime' in parameters.keys():
            starttime = parameters["starttime"]
        
        if 'endtime' in parameters.keys():
            endtime = parameters["endtime"]
            
        if 'startid' in parameters.keys():
            startid = parameters["startid"]
            
        if 'endid' in parameters.keys():
            endid = parameters["endid"]
            
        if 'component' in parameters.keys():
            component = parameters["component"]
            
        if 'loglevel' in parameters.keys():
            loglevel = parameters["loglevel"]
            
        if 'deviceid' in parameters.keys():
            deviceid = parameters["deviceid"]
            
        if 'port_id' in parameters.keys():
            port_id = int(parameters["port_id"])
        
        if 'boardname' in parameters.keys():
            boardname = parameters["boardname"]
        
        if 'server' in parameters.keys():
            server = parameters["server"]
        
        if 'manager' in parameters.keys():
            manager = parameters["manager"]
        
        if 'power' in parameters.keys():
            power = parameters["power"]
            
        if 'sensor' in parameters.keys():
            sensor = parameters["sensor"]
            
        if 'memory' in parameters.keys():
            memory = parameters["memory"]
            
        if 'rm_mode' in parameters.keys():
            rm_mode = parameters["rm_mode"]
            
        if action_name == 'info':
            if server == True and manager == False and power == False:
                result = server_info(rm_mode,True)
            elif server == False and manager == True and power == False:
                result = manager_info()
            elif server == False and manager == False and power == True:  
                result =   get_power_supply_objects()            
            else:
                result = get_rack_manager_info(rm_mode)
        elif action_name == 'health':
            if server == True and memory == False and power == False and sensor == False:
                result = server_info(rm_mode, False)
            elif server == False and memory == True and power == False and sensor == False:
                result = get_memory_details() 
            elif server == False and memory == False and power == True and sensor == False:  
                result =   get_power_supply_objects()
            elif server == False and memory == False and power == False and sensor == True:  
                result = get_sensor_objects_with_units()          
            else:
                result = get_rm_health(rm_mode)
        elif action_name == "relay":
            result = powerport_get_port_status(port_id, 'relay')      
        elif action_name == 'led':
            result = get_rack_manager_attention_led_status()
        elif action_name == 'version':
            result = get_ocsfwversion()
        elif action_name == "fru":
            result = read_fru(boardname)
        elif action_name == "type":
            result = show_rack_manager_type()
        elif action_name == "tftpstatus":
            result = manager_tftp_server_status()
        elif action_name == "tftplist":
            result = manager_tftp_server_listfiles()
        elif action_name == "nfsstatus":
            result = manager_nfs_server_status()
        elif action_name == "sessionlist":        
            result = manager_session_list()
        elif action_name == 'port':        
            if port_id == 0:
                result = powerport_get_all_port_status()
            else:
                result = powerport_get_port_status(port_id, 'pdu')            
        elif action_name == 'ntpstatus':
            result = get_rack_manager_ntp_status ()
        elif action_name == 'ntpserver':
            result = get_rack_manager_ntp_server ()
        elif action_name == 'itpstatus':
            result = get_rack_manager_itp_status ()
        elif action_name == 'log':
            result = get_rack_manager_log(telemetry_log_path, True, starttime, endtime, 
                                          startid, endid, loglevel, component, deviceid, port_id)
        elif action_name == 'inventory':
            result = manager_inventory(rm_mode)
        elif action_name == 'throttlelocal':
            result = get_manager_throttle_local_bypass ()
            if (result[completion_code.cc_key] == completion_code.success):
                result.update (get_manager_throttle_output_enable ())
        elif action_name == 'throttlerow':
            result = get_row_throttle_bypass ()
            if (result[completion_code.cc_key] == completion_code.success):
                result.update (get_row_throttle_output_enable ())
        elif action_name == 'bootstrap': # Row Manager bootstrap command
            result = powerport_get_row_boot_strap(port_id)
        elif action_name == "time":
            result = show_rack_manager_time()
        elif action_name == "scandevice":
            result = get_rack_manager_scandevice()
        elif action_name == "fwupdatestatus":
            result = show_rack_manager_fwupdate_status()
        elif action_name == "fwupdatelist":
            result = show_rack_manager_fwupdate_list()
        else:
            return set_failure_dict("Display command not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("system_rackmanager_display - Exception: {0}".format(e), completion_code.failure)
        
    return result

def system_rackmanager_action(parameters):
    try:
        action_name = ''
        reset_type = ''
        port_id = ''
        boardname = ''
        destpath = ''
        filename = ''
        server = ''
        target = ''
        sessionid = ''
        year = -1
        month = -1
        day = -1
        hour = -1 
        min = -1
        sec = -1
                
        if 'action' in parameters.keys():
            action_name = parameters["action"]
        if "year" in parameters.keys():
            year = parameters["year"]
        if "month" in parameters.keys():
            month = parameters["month"]
        if "day" in parameters.keys():
            day = parameters["day"]
        if "hour" in parameters.keys():
            hour = parameters["hour"]
        if "min" in parameters.keys():
            min = parameters["min"]
        if "sec" in parameters.keys():
            sec = parameters["sec"]
        if 'resettype' in parameters.keys():
            reset_type = parameters["resettype"]
        if 'port_id' in parameters.keys():
            port_id = int(parameters["port_id"])
        if 'boardname' in parameters.keys():
            boardname = parameters["boardname"]
        if "server" in parameters.keys():
            server = parameters["server"]
        if "file" in parameters.keys():
            filename = parameters["file"]
        if "destpath" in parameters.keys():
            destpath = parameters["destpath"]
        if "hostname" in parameters.keys():
            hostname = parameters["hostname"]
        if "target" in parameters.keys():
            target = parameters["target"]
        if "sessionid" in parameters.keys():
            sessionid = parameters["sessionid"]
        
        if action_name == 'ledon': 
            result = set_rack_manager_attention_led(1)
        elif action_name == 'ledoff':
            result = set_rack_manager_attention_led(0)
        elif action_name == "relayon":
            result = powerport_set_system_reset(port_id, "on", "relay")
        elif action_name == "relayoff":
            result = powerport_set_system_reset(port_id, "off", "relay")
        elif action_name == 'porton':
            result = powerport_set_system_reset(port_id, 'on', 'pdu')
        elif action_name == 'portoff':
            result = powerport_set_system_reset(port_id, 'off', 'pdu')
        elif action_name == "fru":
            result = write_fru(boardname, filename)
        elif action_name == "tftpstart":
            result = manager_tftp_server_start()
        elif action_name == "tftpstop":
            result = manager_tftp_server_stop()
        elif action_name == "tftpget":
            result = manager_tftp_client_get(server, filename)
        elif action_name == "tftpput":
            result = manager_tftp_client_put(server, filename, target)    
        elif action_name == "tftpdelete":
            result = manager_tftp_deletefile(filename)    
        elif action_name == "sessionkill":
            result = manager_session_kill(sessionid)
        elif action_name == "nfsstart":
            result = manager_nfs_server_start()
        elif action_name == "nfsstop":
            result = manager_nfs_server_stop()
        elif action_name == 'ntpstart':
            result = start_rack_manager_ntp_service ()
        elif action_name == 'ntpstop':
            result = stop_rack_manager_ntp_service ()
        elif action_name == 'ntprestart':
            result = start_rack_manager_ntp_service (restart = True)
        elif action_name == 'ntpenable':
            result = enable_rack_manager_ntp_service ()
        elif action_name == 'ntpdisable':
            result = disable_rack_manager_ntp_service ()
        elif action_name == 'ntpserver':
            result = set_rack_manager_ntp_server (server)
        elif action_name == 'itpstart':
            result = start_rack_manager_itp_service ()
        elif action_name == 'itpstop':
            result = stop_rack_manager_itp_service ()
        elif action_name == 'itprestart':
            result = start_rack_manager_itp_service (restart = True)
        elif action_name == 'itpenable':
            result = enable_rack_manager_itp_service ()
        elif action_name == 'itpdisable':
            result = disable_rack_manager_itp_service ()
        elif action_name == 'hostname':
            result = set_hostname (hostname)
        elif action_name == 'fwupdate':
            result = set_rack_manager_fwupdate(filename)
        elif action_name == 'clearlog':
            result = clear_rack_manager_telemetry_log ()
        elif action_name == 'throttlelocalbypass':
            result = set_manager_throttle_local_bypass (parameters["enable"])
        elif action_name == 'throttlelocalenable':
            result = set_manager_throttle_output_enable (parameters["enable"])
        elif action_name == 'throttlerowbypass':
            result = set_row_throttle_bypass (parameters["enable"])
        elif action_name == 'throttlerowenable':
            result = set_row_throttle_output_enable (parameters["enable"])
        elif action_name == 'recoveryon': #Row Manager bootstrap command
            result = powerport_set_row_boot_strapping(port_id, 'network')
        elif action_name == 'recoveryoff':
            result = powerport_set_row_boot_strapping(port_id, 'normal')
        elif action_name == "time":
            result = set_rack_manager_time(None, hour, min, sec, month, day, year)
        else:
            # This is to resolve integration issue with ocscli
            # ocscli passes mode as parameter, but 
            result = system_rackmanager_display(parameters)
        
    except Exception, e:
        return set_failure_dict('system_rackmanager_action - Exception: {0}'.format(e), completion_code.failure)
    
    return result
        

############################################################################################################
# Row Manager
###########################################################################################################
def system_rowmanager_action(parameters):
    
    action_name=''
    r_id=0
    
    if 'action' in parameters.keys():
        a_name = parameters['action']
        
    if 'resettype' in parameters.keys():
        r_name = parameters['resettype']
        
    if 'id' in parameters.keys():
        id = parameters['id']
    
    return {'status_code':0, 'Status ': 'action command is not implemented.'}
        
    
############################################################################################################
# SYSTEMS Blades
###########################################################################################################
def system_doResets(system_id, parameters):
    
    if 'reset' in parameters.keys():
        action_name = parameters['reset']
    
    port_type="pdu"
    
    val_commands= {'on','off','forceoff','forceon'}
       
    if action_name in val_commands:
        return powerport_set_system_reset(system_id, action_name, port_type)           
    else:
        return {'status_code':-1, 'failed: ': 'Action is not supported.'}
    

def parse_systemparameters(parameters):
    try: 
        action_name = ''
        reset_type = ''
        boottype = ''
        presence = ''
        version = ''
        starttime = ''
        endtime = ''
        triggertype = '' 
        nvdimmbackupdelay = ''
        pcieresetdelay = ''
        rmediaimagename = ''
        bootmode = ''
        persistent = ''
        ipmicmd = ''
        force = ''
        
        if 'action' in parameters.keys():
            action_name = parameters['action']
            
        if 'resettype' in parameters.keys():
            reset_type = parameters['resettype']
            
        if 'boottype' in parameters.keys():
            boottype = parameters['boottype']
        
        if 'bootmode' in parameters.keys():
            bootmode = parameters['bootmode']
        
        if 'ispersist' in parameters.keys():
            persistent = parameters['ispersist']
        
        if 'presence' in parameters.keys():
            presence = int(parameters['presence'])
            
        if 'version' in parameters.keys():
            version = parameters['version']
        
        if 'starttime' in parameters.keys():
            starttime = parameters['starttime']
        
        if 'endtime' in parameters.keys():
            endtime = parameters['endtime']
            
        if 'triggertype' in parameters.keys():
            triggertype = parameters['triggertype']
            
        if 'nvdimmbackupdelay' in parameters.keys():
            nvdimmbackupdelay = parameters['nvdimmbackupdelay']
        
        if 'pcieresetdelay' in parameters.keys():
            pcieresetdelay = parameters['pcieresetdelay']
       
        if 'rmediaimagename' in parameters.keys():
            rmediaimagename = parameters['rmediaimagename']
            
        if "ipmicmd" in parameters.keys():
            ipmicmd = parameters["ipmicmd"]
        
        if "force" in parameters.keys():
            force = parameters["force"]
        
    except Exception, e:
        print "parse_systemparameters - Exception: {0}".format(e)
        
    return  action_name, reset_type, boottype,bootmode,persistent, presence, version,starttime, endtime, \
            triggertype, nvdimmbackupdelay, pcieresetdelay, rmediaimagename, ipmicmd, force


def system_doActions(system_id, parameters):
    try:
        results = {}
        
        action_name=''
        reset_type=''
        boottype=''
        presence=''
        version=''
        starttime=''
        endtime=''
        triggertype=''
        nvdimmbackupdelay=''
        pcieresetdelay=''
        rmediaimagename=''
        bootmode = ''
        persistent = ''
        ipmicmd = ''
        force = ''

        action_name, reset_type, boottype, bootmode, persistent, presence, version,starttime, endtime, \
        triggertype, nvdimmbackupdelay, pcieresetdelay, rmediaimagename, ipmicmd, force = parse_systemparameters(parameters)
        
        if action_name =='reset':
            results = set_server_active_power_cycle(system_id)
        elif action_name == 'on':
            results = set_server_on(system_id)
        elif action_name == 'off':
            results = set_server_off(system_id)
        elif action_name == 'porton':
            results = powerport_set_system_reset(system_id, 'on', 'pdu')
        elif action_name == 'portoff':
            results = powerport_set_system_reset(system_id, 'off', 'pdu')
        elif action_name == 'startserialsession':
            return server_start_serial_session(system_id, force)
        elif action_name == 'stopserialsession':
            return close_active_session(system_id)
        elif action_name == 'tpmpresence':
            results = set_tpm_physical_presence(system_id, presence)    
        elif action_name == 'nextboot':
            results = set_nextboot(system_id, boottype, bootmode,persistent)   
        elif action_name == 'defaultpower':
            if int(parameters["powerstate"]) == 0:
                results = set_server_default_powerstate_off(system_id)
            elif int(parameters["powerstate"]) == 1:
                results = set_server_default_powerstate_on(system_id)
            else:
                return set_failure_dict('Powerstate should be 0 or 1',completion_code.failure)
        elif action_name == 'activepowercycle':
            results = set_server_active_power_cycle(system_id)
        elif action_name == 'ledon':
            results = set_server_attention_led_on(system_id)
        elif action_name == 'ledoff':
            results = set_server_attention_led_off(system_id)
        elif action_name == 'clearlog':
            results = clear_server_log(system_id)
        elif action_name == 'biosconfig':
            results = set_server_bios_config(system_id, parameters["major"], parameters["minor"])
        elif action_name == 'gettpmphysicalpresence':
            results = get_tpm_physical_presence(system_id)
        elif action_name =='getnextboot':
            results = get_nextboot(system_id) 
        elif action_name =='getdefaultpowerstate':
            results= get_server_default_powerstate(system_id)
        elif action_name =='getstate':
            results=get_server_state(system_id)    
        elif action_name == 'getbiosconfig':
            results= get_server_bios_config(system_id)        
        elif action_name == 'getbioscode':
            results = get_bios_code(system_id, version)    
        elif action_name == 'readsystemlog':
            results = read_server_log(system_id)       
        elif action_name == 'readsystemlogtimestamp':
            results = read_server_log_with_timestamp(system_id, starttime, endtime)
        elif action_name == 'datasafepolicy':
			results = set_nvdimm_policy(system_id, triggertype, nvdimmbackupdelay, pcieresetdelay)
        elif action_name == 'rmediamount':
            results = mount_rmedia(system_id, rmediaimagename)
        elif action_name == 'rmediaunmount':
            results = umount_rmedia(system_id)
        elif action_name == "type":
            results = get_system_type(system_id)
        elif action_name == "cmd":
            interface = get_ipmi_interface(system_id, ipmicmd)
            output = call_ipmi(interface, "cmd") 
                
            if "ErrorCode" in output:
                results = set_failure_dict("Failed to run IPMITool: {0}".format(output), completion_code.failure)
                                                                           
            if output["status_code"] == 0:
                results["Output"] = "\n" + output["stdout"].strip()
                results = set_success_dict(results)
            else:
                error_data = output["stderr"].strip()
                results = set_failure_dict("Failed to run command {0}".format(ipmicmd, completion_code.failure))
        else:
            return set_failure_dict("Action command not implemented: {0}".format(action_name), completion_code.failure)
    except Exception, e:
            return set_failure_dict("system_doActions - Exception: {0}".format(e), completion_code.failure)
        
    return results   

def switch_doActions(switch, parameters):
    try:
        results = {}
        
        model_name = ''
        action_name = ''
        file_path = ''
        
        if 'model' in parameters.keys(): 
            model_name = parameters['model']

        if 'action' in parameters.keys(): 
            action_name = parameters['action']
        
        if 'file' in parameters.keys(): 
            file_path = parameters['file']
        
        if model_name == 'switchport':
            results = set_failure_dict("Action command not implemented", completion_code.failure)
        elif action_name == 'reset':
            results = switch.do_reset()
        elif action_name == 'configure':
            results = switch.do_configure(file_path)
        elif action_name == 'upgrade':
            results = switch.do_upgrade(file_path)
        else:
            results = set_failure_dict("Action command not correct: {0}".format(action_name), completion_code.failure)
    except Exception, e:
            return set_failure_dict("switch_doActions - Exception: {0}".format(e), completion_code.failure)
            
    return results 


############################################################################################################
# Network interface 
###########################################################################################################
    
def ethernetinterface_actions(self, parameters):
    try:        
        a_name=''
        
        if 'action' in parameters.keys(): 
            a_name = parameters['action']
                
        if a_name == 'static':
            res = set_static_interface(parameters["ifname"],parameters["address"],parameters["subnetmask"],parameters["gateway"])       
            return ethernet_actions_results(res)
        elif a_name == 'dhcp':
            res = set_dhcp_interface(parameters["ifname"])
            return ethernet_actions_results(res)
        elif a_name == 'enable':
            res = enable_network_interface(parameters["ifname"])
            return ethernet_actions_results(res)
        elif a_name == 'disable':
            res = disable_network_interface(parameters["ifname"])
            return ethernet_actions_results(res)        
        else:
            return  set_failure_dict('Action command is not correct',completion_code.failure)
    except Exception, e:
        ocslog.log_exception ()
        return  set_failure_dict(('Exception:',e),completion_code.failure)

def ethernet_actions_results(res):
    try:
        results = {}
        
        if (res['status_code'] == 0):
                results = set_success_dict ()
        else:
            error_data = res['stderr'].split('\n')
            results = set_failure_dict (error_data)
            results['Error Code'] = res['status_code']
            
    except Exception, e:
        #Log_Error("Ethernet interface action parse results exception  :",e)
        return set_failure_dict(('Exception:',e),completion_code.failure)
    
    return results


###########################################################################################################
# Accounts and Roles
########################################################################################################### 
   
def user_manage_account_action(parameters):
    if 'action' in parameters.keys(): 
        action = parameters['action']
    
    if 'username' in parameters.keys(): 
        user = parameters['username']
    
    if 'password' in parameters.keys(): 
        pwd = parameters['password']
    
    if 'role' in parameters.keys(): 
        role = parameters['role']
        
    if action == 'user_add':
        result = user_create_new(user, pwd, role)    
    elif action == 'update_pwd':
        result = user_update_password(user, pwd)                
    elif action == 'user_delete':
        result = user_delete_by_name(user)
    elif action == 'update_role':
        result = user_update_role(user, role)       
    else:
        return set_failure_dict("Action command is not implemented", completion_code.failure)
        
    return result 
    

############################################################################################################
# POWER PORT -PDU, Relay, and System
############################################################################################################

def powerport_works(port_id, port_type, parameters):
    
    if 'action' in parameters.keys(): 
        action_name = parameters['action']
        
    if 'resettype' in parameters.keys(): 
        reset_type = parameters['resettype']
        
    if action_name == 'reset':        
        return powerport_set_system_reset(port_id, reset_type, port_type)
    else:
        return {'status_code':-1, 'failed': 'action type is not supported'}
    
############################################################################################################
# LOG: Server, Rack Manager, Row Manager
############################################################################################################
def eventlog_actions(branch_id, branch_name, parameters):
    if 'action' in parameters.keys():
        action_name = parameters['action']
       
    if action_name =='clearlog' and branch_name=='system':
        results = clear_server_log(branch_id)   
    else:
        return {'status_code':-1, 'failed': 'action type is not supported'}

############################################################################################################
# OcsPower Display and Action commands
###########################################################################################################
def system_ocspower_display(type, parameters):
    try:
        action_name = ''
        version_type = ''
        phases = ''
        
        if 'action' in parameters.keys():
            action_name = parameters["action"]
        
        if 'version' in parameters.keys():
            version_type = parameters["version"]
            
        if 'phase' in parameters.keys():
            phases = parameters["phase"]
        
        if action_name == 'systemlimit':
            result = get_server_power_limit(int(type)) 
        elif action_name == 'systemreading':
            result = get_server_power_reading(int(type)) 
        elif action_name == 'systemalert':
            result = get_server_power_alert_policy(int(type))
        elif action_name == 'systemthrottle':
            result = get_server_throttling_statistics(int(type))
        elif action_name == 'managerreading':
            result = get_rack_manager_power_reading()
        elif action_name == 'managerstatus':
            result = get_rack_manager_status()
        elif action_name == "psuinfo":
            result = get_server_psu_status(int(type), phases)
        elif action_name == "psuversion":
            if version_type == "bootloader":
                result = get_server_psu_bootloader_version(int(type))
            else:
                result = get_server_psu_fw_version(int(type))  
        elif action_name == "psubattery":
            result = get_server_psu_battery_present(int(type))  
        elif action_name == "psuupdate":           
            result = query_psu_fw_update(int(type),1)
        else:
            return set_failure_dict("Display command is not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
            return set_failure_dict(('Exception:',e),completion_code.failure)
        
    return result

def system_ocspower_action(type, parameters):
    try:
        action_name = ''
        powerlimit = ''
        alertaction = ''
        remediationaction = ''
        phases = ''
        file_name = ''
        fw_type = ''
        throttleduration = None
        removedelay = None
        
        if 'action' in parameters.keys():
            action_name = parameters["action"]
            
        if 'powerlimit' in parameters.keys():
            powerlimit = int(parameters['powerlimit'])

        if 'alertaction' in parameters.keys():
            alertaction = int(parameters['alertaction'])
            
        if 'remediationaction' in parameters.keys():
            remediationaction = int(parameters['remediationaction'])
        
        if 'throttleduration' in parameters.keys():
            if parameters['throttleduration'] is not None:
                throttleduration = int(parameters['throttleduration'])
            
        if 'removedelay' in parameters.keys():
            if parameters['removedelay'] is not None:
                removedelay = int(parameters['removedelay'])
                
        if 'phase' in parameters.keys():
            phases = parameters["phase"]
        
        if 'file' in parameters.keys():
            file_name = parameters["file"]
            
        if 'type' in parameters.keys():
            fw_type = parameters["type"]
        
        if action_name == 'systemlimitvalue':
            result = set_server_power_limit(int(type), powerlimit)
        elif action_name == 'systemlimiton': 
            result = set_server_power_limit_on(int(type))
        elif action_name == 'systemlimitoff':
            result = set_server_power_limit_off(int(type))
        elif action_name == 'systemalert':
            result = set_server_power_alert_policy(int(type), powerlimit, alertaction, remediationaction, throttleduration, removedelay)
        elif action_name == 'managerclearfaults':
            result = set_rack_manager_clear_power_faults()
        elif action_name == "psuclear":
            result = clear_server_psu_faults(int(type), phases)
        elif action_name == "psubattery":
            result = set_server_psu_battery_test(int(type))
        elif action_name == "psuupdate":
            result = start_psu_fw_update(int(type), file_name, fw_type)
            
        else:
            return set_failure_dict("Action command not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
        return set_failure_dict("system_ocspower_action - Exception: {0}".format(e), completion_code.failure)
    
    return result

############################################################################################################
# PowerMeter Display and Action commands
###########################################################################################################
def system_powermeter_display(parameters):
    try:
        action_name = ''
        
        if 'action' in parameters.keys():
            action_name = parameters["action"]
        
        if action_name == 'limit':
            result = get_rack_power_limit_policy()
        elif action_name == 'alert':
            result = get_rack_power_alert_policy()
        elif action_name == 'reading':
            result = get_rack_power_reading()
        elif action_name == 'version':
            result = get_rack_pru_fw_version()
        else:
            return set_failure_dict("Display command is not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
            return set_failure_dict(('Exception:',e),completion_code.failure)
        
    return result

def system_powermeter_action(parameters):
    try:
        action_name = ''
        powerlimit = ''
        policy = ''
        dcthrottlepolicy = ''

        if 'action' in parameters.keys():
            action_name = parameters["action"]
            
        if 'policy' in parameters.keys():
            policy = int(parameters["policy"])
            
        if 'dcthrottlepolicy' in parameters.keys():
            dcthrottlepolicy = int(parameters["dcthrottlepolicy"])
       
        if 'powerlimit' in parameters.keys():
            powerlimit = int(parameters['powerlimit'])
                    
        if action_name == 'limit':
            result = set_rack_power_limit_policy(powerlimit)
        elif action_name == 'clearmax': 
            result = set_rack_clear_max_power()
        elif action_name == 'clearfaults':
            result = set_rack_clear_power_faults()
        elif action_name == 'alert':
            result = set_rack_power_alert_policy(policy, dcthrottlepolicy, powerlimit)
        else:
            return set_failure_dict("Action command is not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
        return set_failure_dict(('system_powermeter_action() Exception:', e), completion_code.failure)
    
    return result

############################################################################################################
# FPGA Display and Action commands
###########################################################################################################
def system_fpga_display(id, parameters):
    try:
        action_name = ''
        
        if 'action' in parameters.keys():
            action_name = parameters["action"]
        
        if action_name == 'mode':
            result = get_fpga_bypass_mode(id)
        elif action_name == 'temp':
            result = get_fpga_temp(id)
        elif action_name == 'i2cversion':
            result = get_fpga_i2c_version(id)
        elif action_name == 'health':
            result = get_fpga_health(id)
        elif action_name == 'assetinfo':
            result = get_fpga_assetinfo(id)
        else:
            return set_failure_dict("Display command not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
            return set_failure_dict(('system_fpga_display() Exception:', e), completion_code.failure)
        
    return result

def system_fpga_action(id, parameters):
    try:
        action_name = ''

        if 'action' in parameters.keys():
            action_name = parameters["action"]
                    
        if action_name == 'disablebypass':
            result = set_fpga_bypass_off(id)
        elif action_name == 'enablebypass': 
            result = set_fpga_bypass_on(id)
        else:
            return set_failure_dict("Action command not implemented: {0}".format(action_name), completion_code.failure)
        
    except Exception, e:
        return set_failure_dict(('system_fpga_action() Exception:', e), completion_code.failure)
    
    return result
