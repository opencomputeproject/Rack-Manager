# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-


import ocslog
import ocsfile
import datetime
import lib_utils
import collections
import mgmt_switch

from ctypes import *
from ocspaths import *
from bladeinfo_lib import *
from server_health import *
from manage_network import *
from manage_services import *
from manage_powerport import *
from manage_fwversion import *
from collections import OrderedDict
from mgmt_switch import *
from pre_settings import verify_caller_admin_permission, rm_mode, get_rm_mode
from ocslock import ocs_lock, ocs_unlock, ocslock_t_enum
from utils_print import ocsprint

def getlevel(level):
    if level == 0:
        return "Info"
    elif level == 1:
        return "Warning"
    elif level == 2:
        return "Error"
    else:
        return "Unknown"
    
def getcomponent(component):
    if component == 0:
        return "RackManager"
    elif component == 1:
        return "Switch"
    elif component == 2:
        return "Switch Port"
    elif component == 3:
        return "Server"
    elif component == 4:
        return "Server Power"
    elif component == 5:
        return "Server Fan"
    else:
        return "Unknown"

def show_rack_manager_type():
    result = {}
    
    result["Manager Type"] = rm_mode(get_rm_mode())
    
    return set_success_dict(result)

def show_rack_manager_hostname():
    result = {}
    
    result["Hostname"] = socket.gethostname()
    result[completion_code.cc_key] = completion_code.success

    return set_success_dict(result)

def show_rack_manager_log_status():
    result = {}

    try:
        result["TelemetryDaemonStatus"] = "Disabled"
    
        out = subprocess.check_output("ps | grep ocstelemetry_daemon | grep -v grep", shell = True)
        
        if out is not None and "ocstelemetry_daemon" in out:
            result["TelemetryDaemonStatus"] = "Enabled"
    
        return result

    except subprocess.CalledProcessError:
        return result

def clear_rack_manager_telemetry_log():
    return set_rack_manager_clear_log(telemetry_log_path)
    
def set_rack_manager_clear_log(filename):
    output = 0
    result = {}

    if filename is None or not filename:
        return set_failure_dict("No filename provided to clear log function", completion_code.failure)

    try:
        parser_bin = lib_utils.get_telemetry_library()

        files = [filename, filename + ".0",  filename + ".1"]
        
        for file in files:
            if os.path.isfile(file):
                output = parser_bin.TelemetryClearLog(file)
            else:
                continue

        if output != 0:
            return set_failure_dict(("Failed to clear log using osctelemetry_parse library: {0}".format(output)),completion_code.failure)

    except Exception, e:
        return set_failure_dict("set_rack_manager_clear_log Exception: {0}".format(str(e)),completion_code.failure)

    return set_success_dict(result)

def get_rack_manager_log(filename, raw = True, starttime = -1, endtime = -1, startid = -1, endid = -1, loglevel = -1, component = -1, bladeid = -1, portid = -1):
    output = -1
    result = {}
    empty = True 

    if raw is False:
        result['members'] = {}
    else:
        result['Entries'] = {}

    class LogEntry(Structure):
        _fields_ = [('time', c_int),
                    ('component', c_int),
                    ('level', c_int),
                    ('bladeid', c_int),
                    ('fanid', c_int),
                    ('portid', c_int),
                    ('message_id', c_int),
                    ('message', c_char * 512),
                    ('sensortype', c_char * 32)]

    if filename is None or not filename:
        return set_failure_dict("No filename provided to read log function", completion_code.failure)

    try:
        parser_bin = lib_utils.get_telemetry_library()

        files = [filename, filename + ".0",  filename + ".1"]
        
        for file in files:
            if os.path.isfile(file):
                f = open(file, 'r')
            else:
                continue
    
            if f.closed:
                return set_failure_dict("Failed to open file: {0}".format(file), completion_code.failure)
                
            for line in f:
                entry = LogEntry(0, 0, 0, 0, 0, 0, 0)
    
                output = parser_bin.TelemetryParseLine(line, byref(entry))
                    
                if output != 0:
                    return set_failure_dict(("Failed to read log using osctelemetry_parse library: {0}".format(output)),completion_code.failure)
    
                logentry = {}
                    
                if starttime != -1 and entry.time < int(starttime):
                    continue
                elif endtime != -1 and entry.time > int(endtime):
                    continue
                elif startid != -1 and entry.message_id < int(startid):
                    continue
                elif endid != -1 and entry.message_id > int(endid):
                    continue
                elif loglevel != -1 and entry.level != int(loglevel):
                    continue
                elif component != -1 and entry.component != int(component):
                    continue
                elif bladeid != -1 and entry.bladeid != int(bladeid):
                    continue
                elif portid != -1 and entry.portid != int(portid):
                    continue
                
                empty = False
    
                if raw is False:
                    result['members'][entry.message_id] = {}
                    result['members'][entry.message_id]['Oem'] = {}
                    
                    logentry['Created'] = datetime.datetime.fromtimestamp(entry.time).strftime('%Y-%m-%dT%H:%M:%SZ')
                    logentry['Severity'] = getlevel(entry.level)
                    logentry['RecordId'] = entry.message_id
                    logentry['Message'] = entry.message.strip()
    
                    if int(entry.component) is 2:
                        result['members'][entry.message_id]['Oem'] = {'PortId' : entry.portid}
                    elif int(entry.component) is 3:
                        result['members'][entry.message_id]['Oem'] = {'DeviceId' : entry.bladeid}
                    elif int(entry.component) is 4:
                        result['members'][entry.message_id]['Oem'] = {'DeviceId' : entry.bladeid}
                    elif int(entry.component) is 5:
                        result['members'][entry.message_id]['Oem'] = {'DeviceId' : entry.bladeid}
                        result['members'][entry.message_id]['Oem'] = {'FanId' : entry.bladeid}
    
                    result['members'][entry.message_id].update(logentry)
                    result['members'][entry.message_id]['Oem'].update({'Component': getcomponent(entry.component)})     
                    result['members'][entry.message_id]['Oem'].update({'SensorType': entry.sensortype.strip()})                                
                else:
                    result['Entries'].update({entry.message_id: line})
    
            f.close()
            
        if empty:
            result['Entries'] = "This log contains no entries"

        if raw and isinstance(result["Entries"], dict):
            result["Entries"] = collections.OrderedDict(sorted(result["Entries"].items()))
        elif not raw and isinstance(result["members"], dict):
            result["members"] = collections.OrderedDict(sorted(result["members"].items()))

    except Exception, e:
        return set_failure_dict("get_rack_manager_log - Exception: {0}".format(e), completion_code.failure)

    return set_success_dict(result)

def show_rack_manager_fwupdate_status():
      
    result = {}
    output = -1

    status = c_uint()
    
    try:       
        fwupdate_binary = lib_utils.get_fwupdate_library()
        
        output = fwupdate_binary.ocs_fwup_getstatus(byref(status))
           
        if output != 0:
            return set_failure_dict("Failed to get FW update status from FWUpgrade library: {0}".format(output), completion_code.failure)

        if status.value == 0:
            result["FWUpdate status"] = "Complete"
        elif status.value == 1:
            result["FWUpdate status"] = "Pending"
        elif status.value == 2:
            result["FWUpdate status"] = "Active"
        elif status.value == 3:
            result["FWUpdate status"] = "Failed"
        elif status.value == 4:
            result["FWUpdate status"] = "Too many retries"
        else:
            result["FWUpdate status"] = "Unavailable"
            
    except Exception, e:
        ocslog.log_exception ()
        return set_failure_dict("show_rack_manager_fwupdate_status() Exception {0}".format(e), completion_code.failure) 
            
    return set_success_dict(result)

def show_rack_manager_fwupdate_list():
      
    result = {}
    output = -1

    list = ctypes.create_string_buffer(64)
    
    try:       
        fwupdate_binary = lib_utils.get_fwupdate_library()
        output = fwupdate_binary.ocs_fwup_getlist(byref(list))
               
        if output != 0:
            return set_failure_dict("Failed to get FW package list from FWUpgrade library: {0}".format(output), completion_code.failure)

        pkgdata = repr(list.value)[1:-1]

        result["Rolback"] =  pkgdata.split(',')[0]
        result["Active"] =  pkgdata.split(',')[1]
        result["Upgrade"] =  pkgdata.split(',')[2]

    except Exception, e:
        ocslog.log_exception ()
        return set_failure_dict("show_rack_manager_fwupdate_status() Exception {0}".format(e), completion_code.failure) 
            
    return set_success_dict(result)

def set_rack_manager_fwupdate(filename):
    
    if filename is None or filename == "":
        return set_failure_dict("Update file not provided", completion_code.failure)
    
    result = {}
    output = -1

    filename = srvroot_shared_path + "/" + filename

    try:
        if not os.path.isfile(filename) and not os.access(filename, os.R_OK):
            return set_failure_dict("File not found: {0}".format(filename), completion_code.failure)
        
        fwupdate_binary = lib_utils.get_fwupdate_library()
        
        output = fwupdate_binary.ocs_fwup_startupgrade(filename)
        
        if output != 0:
            return set_failure_dict("Failed to start FW update using FWUpgrade library: {0}".format(output), completion_code.failure)
            
    except Exception, e:  
        return set_failure_dict("set_rack_manager_fwupdate() Exception {0}".format(e), completion_code.failure) 
            
    return set_success_dict(result)

	
def set_manager_tftp_service_state(state):
    if (state == "Start"):
        return manager_tftp_server_start()
    elif (state == "Restart"):
        return manager_tftp_server_start(restart = True)
    elif (state == "Stop"):
        return manager_tftp_server_stop()
    else:
        return set_failure_dict ("Invalid TFTP server state {0} requested".format (state),
            completion_code.failure)
        
def set_manager_tftp_service_config (enable):
    if enable:
        return service_enable("tftpd-hpa")
    else:
        return service_disable("tftpd-hpa")
        
def manager_tftp_server_start(restart = False):
    output = service_start("tftpd-hpa", restart)
    
    if output[completion_code.cc_key] != completion_code.success and \
       "Starting HPA's tftpd" in output[completion_code.desc]:
        return set_success_dict()
        
    return output

def manager_tftp_server_stop():
    output = service_stop("tftpd-hpa")
        
    if output[completion_code.cc_key] != completion_code.success and \
       "Stopping HPA's tftpd" in output[completion_code.desc]:
        return set_success_dict()
    
    return output

def manager_tftp_server_status():
    result = {}

    try:
        result["TFTPStatus"] = "Stopped"
        result["TFTPService"] = check_service_enabled("tftpd-hpa")
    
        out = subprocess.check_output("ps | grep in.tftpd-hpa | grep -v grep", shell = True)
        
        if out is not None and "in.tftpd-hpa" in out:
            result["TFTPStatus"] = "Running"
                 
        return set_success_dict(result)
                 
    except subprocess.CalledProcessError:
        return set_success_dict(result)

def manager_tftp_server_listfiles():
    result = {}
    result["TFTPFiles"] = {}
    out = subprocess.check_output("ls -1 " + srvroot_shared_path, shell = True)
    fileid = 0

    if out is not None:
        for line in out.splitlines(True):
            fileid = fileid + 1
            result["TFTPFiles"][fileid] = {}
            result["TFTPFiles"][fileid]["Name"] = line.strip('\n')

    return set_success_dict(result)

def manager_session_list():
    result = {}
    result["sessions"] = {}
    out = subprocess.check_output("netstat -tnp | grep :22 | grep ESTABLISHED", shell = True)
    index = 0

    if out is not None:
        for line in out.splitlines(True):
            index = index + 1
            result["sessions"][index] = {}
            result["sessions"][index]["ID"] = line.split()[6].split('/')[0]
            result["sessions"][index]["ClientIP"] = line.split()[4].split(':')[0]
            result["sessions"][index]["ClientPort"] = line.split()[4].split(':')[1]

    return set_success_dict(result)

def manager_session(sessionid):
    result = {}
    out = subprocess.check_output("netstat -tnp | grep :22 | grep ESTABLISHED", shell = True)
    
    found = 0
                
    if out is not None:
        for line in out.splitlines(True):
            containstr = " %s/" % (str(sessionid))
            if containstr in line:			
                result["ID"] = line.split()[6].split('/')[0]
                result["ClientIp"] = line.split()[4].split(':')[0]
                result["ClientPort"] = line.split()[4].split(':')[1]
                found = 1
                break
    
    if found == 0:
        return set_failure_dict("Invalid session id {0}".format(sessionid))
    else:
        return set_success_dict(result)

def manager_session_kill(sessionid):
    try:
        cmdstr = "ps | grep 'sshd:' | grep '^ *{0} '".format(sessionid)
        out = subprocess.check_output(cmdstr, shell = True, stderr = subprocess.STDOUT)
                
        if out is not None:
            cmdstr = "kill -9 {0}".format(sessionid)
            out = subprocess.check_output(cmdstr, shell = True, stderr = subprocess.STDOUT)
            return set_success_dict()

        return set_failure_dict("Session not active: {0}".format(sessionid), completion_code.failure)
    
    except subprocess.CalledProcessError as e:        
        if e.returncode == 1:
            return set_failure_dict("Session not active: {0}".format(sessionid), completion_code.failure)
            
        return set_failure_dict("Failed to kill session: {0}".format(sessionid), completion_code.failure)
        
    except Exception, e:  
        return set_failure_dict("manager_session_kill - Exception: {0}".format(e), completion_code.failure)  

def manager_tftp_deletefile(file):
    try:
        filepath = srvroot_shared_path + "/{0}".format(file)
        
        os.remove(filepath)

    except OSError, e:
        return set_failure_dict(e.strerror, completion_code.failure)

    except Exception, e:  
        return set_failure_dict("manager_tftp_deletefile({0}) - Exception: {1}".format(e), file, completion_code.failure)         

    return set_success_dict()

def manager_tftp_client_get(server, file):
    try:         
        cmdstr = "tftp -g -r %s -l %s/%s %s" % (file, srvroot_shared_path, file, server)
        out = subprocess.check_output(cmdstr, shell = True, stderr = subprocess.STDOUT)
        
    except subprocess.CalledProcessError as e:
        return set_failure_dict(e.output.split(":")[-1].strip(), completion_code.failure)
        
    except Exception, e:  
        return set_failure_dict("manager_tftp_client_get - Exception: {0}".format(e), completion_code.failure)         

    return set_success_dict()

def concat_files(files, output):
    with open(output, "w") as outfile:
        for file in files:
            with open(file) as infile:
                for line in infile:
                    outfile.write(line)

def manager_tftp_client_put(server, file, target):
    try:
        path = srvroot_path
        filenames = []
        
        targetfile = ""
        if target.lower() == "auditlog":
            targetfile = "ocsaudit.log"
        elif target.lower() == "debuglog":
            targetfile = "ocsevent.log"
        elif target.lower() == "telemetrylog":
            targetfile = "ocstelemetry.log"
        elif target.lower() == "restlog":
            targetfile = "ocsrest.log"
        elif target.lower() == "firmwareupdatelog":
            targetfile = "ocsfwup.log"
            path = srvroot_shared_path
        elif target.lower() == "systemlog":
            targetfile = "messages"
            path = var_log_path
        elif target.lower() == "kernellog":
            targetfile = "dmesg"
            path = var_log_path
        else:
            return set_failure_dict("Unknown target: {0}".format(target), completion_code.failure)         
            
        dirs = os.listdir(path)
            
        for filename in dirs:
            if filename.startswith(targetfile):
                filenames.append("{0}/{1}".format(path, filename))
             
        if not filenames:
            return set_failure_dict("{0} not found".format(target), completion_code.failure)
        
        filenames.sort()        
        filenames.reverse()
            
        concat_files(filenames, srvroot_shared_path + "/{0}".format(target))      
                 
        cmdstr = "tftp -p -r {0} -l {1}/{2} {3}".format(file, srvroot_shared_path, target, server)
        out = subprocess.check_output(cmdstr, shell = True, stderr = subprocess.STDOUT)
        
    except subprocess.CalledProcessError as e:
        return set_failure_dict(e.output.split(":")[-1].strip(), completion_code.failure)
        
    except Exception, e:  
        return set_failure_dict("manager_tftp_client_put - Exception: {0}".format(e), 
                                completion_code.failure)         

    return set_success_dict()
    
def set_manager_nfs_service_state (state):
    if (state == "Start"):
        return manager_nfs_server_start()
    elif (state == "Restart"):
        return manager_nfs_server_start(restart = True)
    elif (state == "Stop"):
        return manager_nfs_server_stop()
    else:
        return set_failure_dict("Invalid NFS server state {0} requested".format(state),
                                completion_code.failure)

def set_manager_nfs_service_config (enable):
    if enable:
        return service_enable("nfsserver")
    else:
        return service_disable("nfsserver")
      
def manager_nfs_server_start(restart = False):
    return service_start("nfsserver", restart)

def manager_nfs_server_stop():
    return service_stop("nfsserver")

def manager_nfs_server_status():
    result = {}

    try:
        result["NFSStatus"] = "Running"
        result["NFSService"] = check_service_enabled("nfsserver")
    
        out = subprocess.check_output(["/etc/init.d/nfsserver", "status"], stderr = subprocess.STDOUT)
        
    except CalledProcessError, e:
        if (e.returncode == 3):
            result["NFSStatus"] = "Stopped"
            return set_success_dict(result)
        else:
            return set_failure_dict(e.output.strip(), completion_code.failure)
            
    except Exception, e:
        return set_failure_dict("manager_nfs_server_status - Exception: {0}".format(e), 
                                completion_code.failure)
        
    return set_success_dict(result)
        
def set_rack_manager_ntp_server(server_ip):
    result = {}
    
    try:
        ocs_lock (ocslock_t_enum.NET_CONFIG)
        config = ""
        with open ("/etc/ntp.conf", "r+") as ntp:
            config = ntp.read ()
            config = re.sub ("server\s+\d+\.\d+\.\d+\.\d+", "server " + server_ip, config)
        
        ocsfile.ocs_file_write_complete_file ("/etc/ntp.conf", config)
        
        subprocess.check_output (["/etc/init.d/ntpd", "restart"], stderr = subprocess.STDOUT)
        result = set_success_dict ()
    
    except CalledProcessError as error:
        ocslog.log_exception ()
        result = set_failure_dict (error.output.strip ())
                
    except Exception as error:
        ocslog.log_exception ()
        result = set_failure_dict ("Failed to configure NTP server.")
        
    ocs_unlock (ocslock_t_enum.NET_CONFIG)
    return result

def get_rack_manager_ntp_server():
    result = {}

    try:
        with open ("/etc/ntp.conf", "r") as ntp:
            config = ntp.read()
            server_ip = re.search("server\s+(\d+\.\d+\.\d+\.\d+)", config)
            
            if (server_ip):
                result["NTPServer"] = server_ip.group(1)
                result = set_success_dict(result)
            else:
                result[completion_code.cc_key] = completion_code.failure
                result[completion_code.desc] = "Could not determine current NTP server."
                
                try:
                    ocsfile.ocs_file_ensure_valid ("/etc/ntp.conf")
                    
                except:
                    pass
    
    except Exception as error:
        result[completion_code.cc_key] = completion_code.failure
        result[completion_code.desc] = str (error)
        
    return result

def get_rack_manager_ntp_status():
    result = {}
    
    try:       
        subprocess.check_output (["/etc/init.d/ntpd", "status"], stderr = subprocess.STDOUT)
        
        result["NTPState"] = "Running"
        result["NTPService"] = check_service_enabled ("ntpd")
        result = set_success_dict(result)
                
    except CalledProcessError as error:
        if (error.returncode == 3):
            result["NTPState"] = "Stopped"
            result["NTPService"] = check_service_enabled ("ntpd")
            result = set_success_dict(result)
        else:
            result = set_failure_dict(str(error.output.strip()), completion_code.failure)
            
    except Exception as error:
        result = set_failure_dict(str(error), completion_code.failure)
        
    return result

def set_manager_ntp_service_state(state):
    if (state == "Start"):
        return service_start("ntpd")
    elif (state == "Restart"):
        return service_start("ntpd", restart = True)
    elif (state == "Stop"):
        return service_stop("ntpd")
    else:
        return set_failure_dict("Invalid NTP server state {0} requested".format (state),
                                 completion_code.failure)
        
def set_manager_ntp_service_config(enable):
    if enable:
        return service_enable ("ntpd")
    else:
        return service_disable ("ntpd")
    
def enable_rack_manager_ntp_service():
    return set_manager_ntp_service_config (True)

def disable_rack_manager_ntp_service():
    return set_manager_ntp_service_config (False)
        
def start_rack_manager_ntp_service(restart = False):
    return set_manager_ntp_service_state ("Restart" if restart else "Start")

def stop_rack_manager_ntp_service():
    return set_manager_ntp_service_state ("Stop")

def get_rack_manager_itp_status():
    result = {}
    
    try:       
        status = subprocess.check_output (["/etc/init.d/ocs-itp.sh", "status"],
            stderr = subprocess.STDOUT)
        
        result["ITPState"] = status.strip ()
        result["ITPService"] = check_service_enabled ("ocs-itp.sh")
        result = set_success_dict (result)
                
    except CalledProcessError as error:
        result = set_failure_dict (str (error.output.strip ()), completion_code.failure)
            
    except Exception as error:
        result = set_failure_dict (str (error), completion_code.failure)
        
    return result

def set_manager_itp_service_state(state):
    if (state == "Start"):
        return service_start("ocs-itp.sh")
    elif (state == "Restart"):
        return service_start("ocs-itp.sh", restart = True)
    elif (state == "Stop"):
        return service_stop("ocs-itp.sh")
    else:
        return set_failure_dict("Invalid ITP server state {0} requested".format (state))
        
def set_manager_itp_service_config(enable):
    if enable:
        return service_enable("ocs-itp.sh", ["defaults", "96", "4"])
    else:
        return service_disable("ocs-itp.sh")
    
def enable_rack_manager_itp_service():
    return set_manager_itp_service_config(True)

def disable_rack_manager_itp_service():
    return set_manager_itp_service_config(False)
        
def start_rack_manager_itp_service(restart = False):
    return set_manager_itp_service_state("Restart" if restart else "Start")

def stop_rack_manager_itp_service():
    return set_manager_itp_service_state("Stop")

def set_rack_manager_attention_led(setting):
    result = {}
    output = -1
        
    if setting != 0 and setting != 1:
        return set_failure_dict("Unknown attention LED setting: {0}".format(setting), completion_code.failure)

    state = c_uint()
    
    try:
        gpio_binary = get_gpio_library()
            
        output = gpio_binary.ocs_port_attentionled(setting, byref(state))
        
        if output != 0:
            return set_failure_dict("Failed to set attention led using GPIO library: {0}".format(output), completion_code.failure)
    
    except Exception, e:              
        return set_failure_dict("set_rack_manager_attention_led - Exception: {0}".format(e), completion_code.failure)
        
    return set_success_dict(result)

def get_rack_manager_attention_led_status():
    result = {}
    output = -1

    state = c_uint()

    try:
        gpio_binary = get_gpio_library()
            
        output = gpio_binary.ocs_port_attentionled(2, byref(state))
        
        if output != 0:
            return set_failure_dict("Failed to get attention led state using GPIO library: ".format(output), completion_code.failure)
        
        if(state.value == 0):
            result["Manager LED Status"] = 'OFF'
        elif (state.value == 1):
            result["Manager LED Status"] = 'ON'
        else:
            result["Manager LED Status"] = 'Unknown'
                    
        return set_success_dict(result)
        
    except Exception,e:   
        return set_failure_dict("get_rack_manager_attention_led_status - Exception:".format(e), completion_code.failure)

def get_rack_manager_port_status(port_id):  
    port_id = int(port_id)  
       
    if port_id == 0:
        result = powerport_get_all_port_status()
    else:
        result = powerport_get_port_status(port_id, "pdu")
       
    return result
        
def get_power_supply_objects():
    class HscStatus(LittleEndianStructure):
          _fields_ = [('noFaults', c_byte, 1),
                      ('cml_fault', c_byte, 1),
                      ('temperature_fault', c_byte, 1),
                      ('vin_uv_fault', c_byte, 1),
                      ('iout_oc_fault', c_byte, 1),
                      ('vout_ov_fault', c_byte, 1),
                      ('unit_off', c_byte, 1),
                      ('unit_busy', c_byte, 1),
                      ('unknown_fault', c_byte, 1),
                      ('other_fault', c_byte, 1),
                      ('fan_fault', c_byte, 1),
                      ('power_good', c_byte, 1),
                      ('mfr_fault', c_byte, 1),
                      ('input_fault', c_byte, 1),
                      ('iout_pout_fault', c_byte, 1),
                      ('vout_fault', c_byte, 1)]
    
    hscstatus_str = ""
      
    try:
        completionstate = completion_code.success
        result = {}
        
        input_voltage = c_double()
        power = c_double()
        
        hsc_binary = lib_utils.get_hsc_library ()
        
        hscstatus = HscStatus(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

        power_output = hsc_binary.hsc_get_power(byref(power))
        
        input_output = hsc_binary.hsc_get_inputvoltage(byref(input_voltage))
        
        status_output = hsc_binary.hsc_get_status(byref(hscstatus))
        
        if power_output == 0:
            result["HSC Power"] = round(power.value,2)
        else:
            completionstate = completion_code.failure
        
        if input_output == 0:
            result["HSC Input-Voltage"] = round(input_voltage.value,2)
        else:
            completionstate = completion_code.failure
        
        if status_output == 0:
            if hscstatus.power_good == 1:
                result["HSC Status"] = "OK" + '{' + str(hscstatus.power_good) + '}'
            else:
                result["HSC Status"] = "Alert" + '{' + str(hscstatus.power_good) + '}'
        else:
            completionstate = completion_code.failure
            
    except Exception,e:   
        return set_failure_dict(("Exception:", e),completion_code.failure)
    
    result[completion_code.cc_key] = completionstate
    return result

def get_sensor_objects():
    result = {}

    temperature = c_double()
    humidity = c_double()
    
    try:
        hdc_binary = lib_utils.get_hdc_library()

        temperature_output = hdc_binary.hdc_get_temperature(byref(temperature))
        humidity_output = hdc_binary.hdc_get_humidity(byref(humidity))
        
        if temperature_output == 0 and humidity_output == 0:
            result[completion_code.cc_key] = completion_code.success           
        else:
            result[completion_code.cc_key] = completion_code.failure
            
        result["Temperature"] = round(temperature.value, 2)
        result["Humidity"] = round(humidity.value,2)
            
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("get_sensor_objects - Exception: {0}".format(e), completion_code.failure)

    return result

def get_sensor_objects_with_units ():
    result = get_sensor_objects()
    
    if result[completion_code.cc_key] == completion_code.success:
        result["Temperature"] = str(result["Temperature"]) + " C"
        result["Humidity"] = str(result["Humidity"]) + " RH"
        
    return result

def get_rm_health(mode):
    completionstate = True
    try:   
        rm_health_rsp = {}
        #rm_health_rsp["Manager"] = {}
        rm_health_rsp["PSU Health"] = {}   
        rm_health_rsp["Sensor Reading"] = {}
        rm_health_rsp["Memory Usage"] = {}
        rm_health_rsp["Server State"] = {}
        
        current_time = None
        up_time = None
        
        # Blade Health
        blade_health = server_info(mode)
        if completion_code.cc_key in blade_health.keys():
            if blade_health[completion_code.cc_key] == completion_code.success:
                blade_health.pop(completion_code.cc_key,None)
                rm_health_rsp["Server State"] = blade_health
            else:
                blade_health.pop(completion_code.cc_key,None)
                completionstate &= False
                rm_health_rsp["Server State"] = blade_health
        else:
            completionstate &= False
            rm_health_rsp["Server State"] = blade_health
        
        led_status = get_rack_manager_attention_led_status()        
        if completion_code.cc_key in led_status.keys() and (led_status[completion_code.cc_key] == completion_code.success):
            rm_health_rsp["LED Status"] = led_status["Manager LED Status"]
        else:
            completionstate &= False
            rm_health_rsp["LED Status"] = ''
            
        rm_time = get_rm_uptime()
        if completion_code.cc_key in rm_time.keys():
            if rm_time[completion_code.cc_key] == completion_code.failure:
                completionstate &= False
            
            if 'Current Time' in rm_time.keys():
                current_time = rm_time["Current Time"].strip()
            
            if 'Up Time' in rm_time.keys():
                up_time = rm_time["Up Time"].strip()
                
            rm_health_rsp["Current Time"] = current_time
            rm_health_rsp["Manager Uptime"] = up_time
        else:
            completionstate &= False
            rm_health_rsp["Current Time"] = completion_code.failure
            rm_health_rsp["Manager Uptime"] = completion_code.failure
        
          
        rm_memory = get_memory_details()        
        if completion_code.cc_key in rm_memory.keys():        
            if(rm_memory[completion_code.cc_key] == completion_code.success):
                rm_memory.pop(completion_code.cc_key,None)
                rm_health_rsp["Memory Usage"] = rm_memory
            else:
                rm_memory.pop(completion_code.cc_key,None)
                completionstate &= False
                rm_health_rsp["Memory Usage"][completion_code.cc_key]= completion_code.failure
        else:
            completionstate &= False
            rm_health_rsp["Memory Usage"][completion_code.cc_key]= completion_code.failure
            
            
        psu_health = get_power_supply_objects()        
        if completion_code.cc_key in psu_health.keys():
            if(psu_health[completion_code.cc_key] == completion_code.success):
                psu_health.pop(completion_code.cc_key,None)
                rm_health_rsp["PSU Health"] = psu_health
            else:
                psu_health.pop(completion_code.cc_key,None)
                completionstate &= False
                rm_health_rsp["PSU Health"][completion_code.cc_key] = completion_code.failure
        else:
            completionstate &= False
            rm_health_rsp["PSU Health"][completion_code.cc_key] = completion_code.failure
            
        
        sensor_reading = get_sensor_objects_with_units()
        if completion_code.cc_key in sensor_reading.keys():    
            if(sensor_reading[completion_code.cc_key] == completion_code.success):
                sensor_reading.pop(completion_code.cc_key,None)           
                rm_health_rsp["Sensor Reading"] = sensor_reading
            else:
                sensor_reading.pop(completion_code.cc_key,None) 
                completionstate &= False
                rm_health_rsp["Sensor Reading"][completion_code.cc_key] = completion_code.failure
        else:
            completionstate &= False
            rm_health_rsp["Sensor Reading"][completion_code.cc_key] = completion_code.failure
    
    except Exception, e:
        #log.exception("Exception error is: %s " %e)
        rm_health_rsp[completion_code.cc_key] = completion_code.failure
        rm_health_rsp[completion_code.desc] = "Get manager health Exception: ", e
        return rm_health_rsp
    
    
    if completionstate:
        rm_health_rsp[completion_code.cc_key] = completion_code.success
    else:
        rm_health_rsp[completion_code.cc_key] = completion_code.failure
    
    return rm_health_rsp
    
def get_memory_details():
    try:
        rm_memory = {}
        memory_output  = call_fru_util("free")
        
        if(memory_output['status_code'] == 0):
            sdata = memory_output['stdout'].split('\n')
            data = sdata[1].split(' ')
            memory = filter(None, data) # Removes empty strings
            rm_memory["Total Memory"] = memory[1] + ' KB'
            rm_memory["Used Memory"] = memory[2] + ' KB' 
            rm_memory["Free Memory"] = memory[3] + ' KB'
            rm_memory["Shared"] = memory[4] + ' KB'
            rm_memory["Buffers"] = memory[5] + ' KB'
        else:
            rm_memory[completion_code.cc_key] = completion_code.failure
            
    except Exception, e:
        return set_failure_dict(e, '-1')
    
    rm_memory[completion_code.cc_key] = completion_code.success
    return rm_memory

def get_rm_uptime():
    completionstate = completion_code.success
    try:
        rm_time = {}
        # Command to get Manager uptime and current time
        current_time = "uptime | awk '{print $1'}"
        up_time = "uptime | grep -ohe 'up .*' | awk '{$1=\"\"; print $0}' | sed 's/, load.*$//' | awk '{print $0}'"
        
        time_output = call_fru_util(current_time)
        
        if(time_output['status_code'] == 0):
            rm_time["Current Time"] = time_output['stdout'].strip ()
        else: 
            completionstate = completion_code.failure
            #Log _Erro("Current time error")
        
        up_output = call_fru_util(up_time)
        
        if(up_output['status_code'] == 0):
            rm_time["Up Time"] = up_output['stdout'].strip ()
        else: 
            completionstate = completion_code.failure
            #rm_time["Completion Code"] = "Failure"            
            #Log _Erro("Up time error")
            
    except Exception, e:
        return set_failure_dict(e, completion_code.failure)
    
    rm_time[completion_code.cc_key] = completionstate 
    return rm_time

def read_fru(boardtype):
    fru_util_exe_cmd = None

    try:
        if boardtype == "rm_mb" or boardtype == "row_mb":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 0 -s 50 -r"
        elif boardtype == "rm_pib":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 51 -r"
        elif boardtype == "rm_acdc":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 50 -r"
        elif boardtype == "row_pib":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 52 -r"  
        
        if fru_util_exe_cmd:
            fru_response = parse_read_fru(fru_util_exe_cmd)
            
            if fru_response is None or not fru_response: # Check empty or none
                #log.error(": failed to read fru data: %s" %boardtype)
                fru_response[completion_code.cc_key] = completion_code.failure
                fru_response[completion_code.desc] = "Fru response is empty"
        else:
            return set_failure_dict ("Unknown board type {0}".format (boardtype),
                completion_code.failure)
        
    except Exception,e:
            return set_failure_dict(e, completion_code.failure)    
    
    return fru_response 

def write_fru(boardtype, filename):
    fru_util_exe_cmd = None
    
    try:
        filepath = srvroot_shared_path + "/" + filename
    
        if not os.path.isfile(filepath) and not os.access(filepath, os.R_OK):
            return set_failure_dict("File not found: {0}".format(filename), completion_code.failure)
        
        if boardtype == "rm_mb" or boardtype == "row_mb":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 0 -s 50 -w" + ' ' + filepath
        elif boardtype == "rm_pib":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 51 -w" + ' ' + filepath
        elif boardtype == "rm_acdc":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 50 -w" + ' ' + filepath
        elif boardtype == "row_pib":
            fru_util_exe_cmd = "/usr/bin/ocs-fru -c 1 -s 52 -w" + ' ' + filepath 
        
        if fru_util_exe_cmd:
            fru_response = parse_write_fru(fru_util_exe_cmd)
            
            if fru_response is None or not fru_response:
                fru_response[completion_code.cc_key] = completion_code.failure
                fru_response[completion_code.desc] = "Empty FRU response"
        else:
            return set_failure_dict ("Unknown board type {0}".format (boardtype),
                completion_code.failure)
        
    except Exception, e:
            ocslog.log_exception()
            return set_failure_dict("write_fru - Exception: {0}", completion_code.failure)    
    
    return fru_response

def get_rack_manager_info(rmmode): 
    completioncode = completion_code.success
    try:  
        manager_rsp = {}
        manager_rsp["Server Info"] = {}  
        manager_rsp["RM Controller"] = {}   
        manager_rsp["PSU Info"] = {}

        rm_time = get_rm_uptime()
        if rm_time[completion_code.cc_key] == completion_code.failure:
            completioncode = completion_code.failure            
        
        if 'Current Time' in rm_time.keys():
            current_time = rm_time["Current Time"].strip()
        
        if 'Up Time' in rm_time.keys():
            up_time = rm_time["Up Time"].strip()
            
        manager_rsp["Current Time"] = current_time
        manager_rsp["Manager Uptime"] = up_time
        
        manager_controller = manager_info()
        # Rack Manager Controller
        if(manager_controller[completion_code.cc_key] == completion_code.success):
            manager_controller.pop(completion_code.cc_key,None)
            manager_rsp["RM Controller"] = manager_controller            
        else:
            manager_controller.pop(completion_code.cc_key,None)
            completioncode = completion_code.failure
            manager_rsp["RM Controller"] = manager_controller
            
        # Server Information
        blade_info = server_info(rmmode, True)
        if blade_info[completion_code.cc_key] == completion_code.success:
            blade_info.pop(completion_code.cc_key,None)
            manager_rsp["Server Info"] = blade_info
        else:
            blade_info.pop(completion_code.cc_key,None)
            completioncode = completion_code.failure
            manager_rsp["Server Info"] = blade_info
            
        #PSU Information
        psu_info = get_power_supply_objects()
        if psu_info[completion_code.cc_key] == completion_code.success:
            psu_info.pop(completion_code.cc_key,None)
            manager_rsp["PSU Info"] = psu_info
        else:
            psu_info.pop(completion_code.cc_key,None)
            completioncode = completion_code.failure
            manager_rsp["PSU Info"] = psu_info
         
    except Exception,e:
            return set_failure_dict(("Exception",e), completion_code.failure)    
    
    manager_rsp[completion_code.cc_key] = completioncode 
    return manager_rsp

def call_fru_util(command):
    try:    
        popencmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True);

        output, error = popencmd.communicate()
        
        p_status = popencmd.wait();
        
        return  {'status_code':p_status, 'stdout':output, 'stderr': error}
    except Exception:
        return set_failure_dict("Subprocess ocs-fru call exception, Command: " + command, "-1")

def manager_info():
    completionstate = True
    current_time = ""
    up_time = ""
    
    try:
        rm_controller = {}
        
        rm_controller["Type"] = rm_mode(get_rm_mode())
        rm_controller["Host Name"] = socket.gethostname()
        rm_controller["Asset Info"] = {}
        rm_controller["Network"] = {}
        rm_controller["Status"] = {}
        rm_controller["Temperature"] = {}
        
        led_rsp = get_rack_manager_attention_led_status()
        led_status = ''
                
        if(led_rsp[completion_code.cc_key] == completion_code.success):
            led_status = led_rsp["Manager LED Status"]
        else:
            led_status = completion_code.failure
            completionstate &= False
            
        rm_controller["Status"]["LED Status"] =  led_status              
        rm_controller["Status"]["Power"] = "ON"
        rm_controller["Status"]["Health"] = "OK"
        
        fw_version = get_ocsfwversion()
        
        if completion_code.cc_key in fw_version.keys():
            if (fw_version[completion_code.cc_key] == completion_code.success):
                rm_controller["FW Version"] = fw_version['Package']
            else:
                rm_controller["FW Version"] = completion_code.failure
                completionstate &= False
        
        ip_address = get_ip_address("eth0")
        macaddress = get_macsocket("eth0")
        
        if ip_address is None or not ip_address:
            completionstate &= False
            rm_controller["Network"]["IP Address"] = completion_code.failure
        else:                
            rm_controller["Network"]["IP Address"] = ip_address
            
        if macaddress is None or not macaddress:
            completionstate &= False
            rm_controller["Network"]["Mac Address"] = completion_code.failure
        else:
            rm_controller["Network"]["Mac Address"] = macaddress
            
        sensor_reading = get_sensor_objects_with_units()
        
        if(sensor_reading[completion_code.cc_key] == completion_code.success):
            sensor_reading.pop(completion_code.cc_key,None)           
            rm_controller["Temperature"]["Temperature"] = sensor_reading["Temperature"]
            rm_controller["Temperature"]["Humidity"] = sensor_reading["Humidity"]            
        else:
            completionstate &= False
            rm_controller["Temperature"]["Temperature"] = completion_code.failure
            rm_controller["Temperature"]["Humidity"] = completion_code.failure
            
        fru = fru_Info()

        if fru is None or not fru:
            completionstate &= False
            rm_controller["Asset Info"] = "Fru response is empty"
        else:
            if(fru[completion_code.cc_key] == completion_code.success):
                fru.pop(completion_code.cc_key,None)
                rm_controller["Asset Info"] = fru
            else:
                completionstate &= False
                        
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("manager_info - Exception: {0}".format(e), completion_code.failure)
    
    if completionstate:
        rm_controller[completion_code.cc_key] = completion_code.success
    else:
        rm_controller[completion_code.cc_key] = completion_code.failure
                    
    return rm_controller

def fru_Info():    
    try:    
        interface = "/usr/bin/ocs-fru -c 0 -s 50 -r"
        
        output = call_fru_util(interface)  

        rack_rsp = {}
        
        if(output['status_code'] == 0):      
                #log.info("Completion Code: %s"%Config.completioncode[0])
                sdata = output['stdout'].split('\n')                                
                    
                for value in sdata:                    
                # FRU details
                    if "product productname" in value:
                        rack_rsp["Name"]=  value.split(":")[-1].strip()
                                                
                    elif "product manufacture" in value:
                        rack_rsp["Manufacturer"]=  value.split(":")[-1].strip()
                                            
                    elif "product productversion" in value:
                        rack_rsp["Firmware Version"]=  value.split(":")[-1].strip()
                        
                    elif "board version" in value:
                        rack_rsp["Hardware Version"] = value.split(":")[-1].strip()
                    
                    elif "product serial" in value:
                        rack_rsp["SerialNumber"] = value.split(":")[-1].strip()
                        
                    elif "product fruid" in value:
                        rack_rsp["FruId"] = value.split(":")[-1].strip()              
                
                    elif "product assettag: " in value:
                        rack_rsp["AssetTag"] = value.split(":")[-1].strip()
                        
                    elif "product build" in value:
                        rack_rsp["Build"] = value.split(":")[-1].strip()  
                
                rack_rsp[completion_code.cc_key] = completion_code.success
        else:   
            errorData = output['stderr'].split('\n')            
            rack_rsp[completion_code.cc_key] = completion_code.failure
            
            for data in errorData:
                if "Error" in data:
                    rack_rsp[completion_code.desc] = data.split(":")[-1]
                elif "Completion Code" in data:
                    rack_rsp["Error Code"] = data.split(":")[-1]         
         
                              
    except Exception, e:         
        return set_failure_dict(("Manager info parse results() Exception: ",e), completion_code.failure)    
    
    return rack_rsp  

def get_nic(serverid):
    try:
        nic_rsp = {}
        
        nic_rsp["Nic Info"] = {}

        get_nic_info = get_server_nicinfo(serverid)
                                
        if get_nic_info[completion_code.cc_key] == completion_code.success:
            get_nic_info.pop(completion_code.cc_key, None)
            nic_rsp["Nic Info"] = get_nic_info
        else:
            nic_rsp["Nic Info"] = get_nic_info
            
    except Exception, e:
        #log_err("Exception to get server _info ",e)
        return set_failure_dict(("Exception: get nic info ",e), completion_code.failure)
    
    return nic_rsp
        
def parse_read_fru(frucommand):
    try:        
        output = call_fru_util(frucommand)   
        
        fru_rsp = {}

        if(output['status_code'] == 0):
                fru_rsp[completion_code.cc_key] = completion_code.success
                #log.info("Completion Code: %s"%Config.completioncode[0])
                sdata = output['stdout'].split('\n')                                
                
                for value in sdata:           
                    #Board Info Area       
                    if "board mfgdatetime" in value:
                        fru_rsp["Board Manufacturer Date"]= value.split(":")[-1].strip()                         
                    elif "board manufacturer" in value:
                        fru_rsp["Board Manufacturer"]=  value.split(":")[-1].strip()                                              
                    elif "board name" in value:
                        fru_rsp["Board Name"]=  value.split(":")[-1].strip()                           
                    elif "board serial" in value:
                        fru_rsp["Board Serial"] = value.split(":")[-1].strip() 
                    elif "board part" in value:
                        fru_rsp["Board Part Number"] = value.split(":")[-1].strip()  
                    elif "board fruId" in value:
                        fru_rsp["Board Fru Id"] = value.split(":")[-1].strip()  
                    elif "board address1" in value:
                        fru_rsp["Board Address1"] = value.split(":")[-1].strip() 
                    elif "board address2" in value:
                        fru_rsp["Board Address2"] = value.split(":")[-1].strip()            
                    elif "board version" in value:
                        fru_rsp["Board Version"] = value.split(":")[-1].strip()  
                    elif "board build" in value:
                        fru_rsp["Board Build"] = value.split(":")[-1].strip()  
                    #Product Info area   
                    elif "product manufacture" in value:
                        fru_rsp["Product Manufacturer"]=  value.split(":")[-1].strip()                                              
                    elif "product productname" in value:
                        fru_rsp["Product Name"]=  value.split(":")[-1].strip()    
                    elif "product productversion" in value:
                        fru_rsp["Product Version"] = value.split(":")[-1].strip()
                    elif "product assettag" in value:
                        fru_rsp["Product Assettag"] = value.split(":")[-1].strip()                       
                    elif "product serial" in value:
                        fru_rsp["Product Serial"] = value.split(":")[-1].strip() 
                    elif "product fruid" in value:
                        fru_rsp["Product Fru Id"] = value.split(":")[-1].strip()  
                    elif "product subproduct" in value:
                        fru_rsp["Product Subproduct"] = value.split(":")[-1].strip()  
                    elif "product build" in value:
                        fru_rsp["Product Build"] = value.split(":")[-1].strip()                                          
        else:   
            error_data = output['stderr'].split('\n')    
            error_data = filter(None, error_data)     
            #log_error("Failed to read fru %s ",error_data )   
            fru_rsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "ERROR" in data:
                    fru_rsp[completion_code.cc_key] = data
                elif "eeprom read completion code" in data:
                    fru_rsp["Utility Completion Code"] = data.split(":")[-1]  
                elif "not found" in data:                           
                    fru_rsp["stderr"] = error_data 
                    break          
          
    except Exception, e:         
        return set_failure_dict(("parse_read_fru exception:",e) ,completion_code.failure)  
    
    return fru_rsp

def parse_write_fru(frucommand):
    try:        
        output = call_fru_util(frucommand)  
        
        fru_rsp = {}
            
        if(output['status_code'] == 0):
                #log.info("Completion Code: %s"%Config.completioncode[0])
                fru_rsp[completion_code.cc_key] = completion_code.success                              
                
        else:   
            error_data = output['stderr'].split('\n')    
            error_data = filter(None, error_data)     
            #log_error("Failed to read fru %s ",error_data )   
            fru_rsp[completion_code.cc_key] = completion_code.failure
            
            for data in error_data:
                if "ERROR" in data:
                    fru_rsp[completion_code.desc] = data
                elif "write completion code" in data:
                    fru_rsp["Utility Completion Code"] = data.split(":")[-1]  
                elif "not found" in data:                           
                    fru_rsp["stderr"] = error_data 
                    break                                        
          
    except Exception, e:         
        return set_failure_dict(("parse_write_fru exception:",e) , completion_code.failure)  
    
    return fru_rsp

def set_hostname(hostname):
    result = {}
    
    try:
        ocs_lock (ocslock_t_enum.NET_CONFIG)
        ocsfile.ocs_file_write_complete_file ("/etc/hostname", hostname + "\n")
            
        subprocess.check_output (["hostname", hostname], stderr = subprocess.STDOUT)
        result = set_success_dict ()
        
    except CalledProcessError as error:
        ocslog.log_exception ()
        result = set_failure_dict (error.output.strip ())
        
    except Exception as error:
        ocslog.log_exception ()
        result = set_failure_dict ("Failed to set the hostname for the system.")
        
    ocs_unlock (ocslock_t_enum.NET_CONFIG)
    return result
    
def get_manager_throttle_local_bypass():
    try:
        gpio_binary = get_gpio_library()
        
        is_on = c_int (2)
        state = c_int (0)
        status = gpio_binary.ocs_port_thlocalbypass (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict ("Failed to get throttle local bypass: {0}".format (status))
        
        return set_success_dict ({"Local Bypass" : True if (state.value) else False})
    
    except Exception as error:
        return set_failure_dict (
            "get_manager_throttle_local_bypass() Exception: {0}".format (error))
    
def set_manager_throttle_local_bypass(enable):
    try:
        gpio_binary = get_gpio_library()
        
        is_on = c_int(1 if enable else 0)
        state = c_int(0)
        status = gpio_binary.ocs_port_thlocalbypass (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict("Failed to set throttle local bypass: {0}".format (status))
        
        return set_success_dict()
    
    except Exception as error:
        return set_failure_dict (
            "set_manager_throttle_local_bypass - Exception: {0}".format (error))

def get_manager_throttle_output_enable ():
    try:
        gpio_binary = get_gpio_library ()
        
        is_on = c_int (2)
        state = c_int (0)
        status = gpio_binary.ocs_port_thenable (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict ("Failed to get throttle output enable: {0}".format (status))
        
        return set_success_dict ({"Local Enable" : True if (state.value) else False})
    
    except Exception as error:
        return set_failure_dict (
            "get_manager_throttle_output_enable() Exception: {0}".format (error))
        
def set_manager_throttle_output_enable (enable):
    try:
        gpio_binary = get_gpio_library ()
        
        is_on = c_int (1 if enable else 0)
        state = c_int (0)
        status = gpio_binary.ocs_port_thenable (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict ("Failed to set throttle output enable: {0}".format (status))
        
        return set_success_dict ()
    
    except Exception as error:
        return set_failure_dict (
            "set_manager_throttle_output_enable() Exception: {0}".format (error))
        
def get_row_throttle_bypass ():
    try:
        gpio_binary = get_gpio_library ()
        
        is_on = c_int (2)
        state = c_int (0)
        status = gpio_binary.ocs_port_throttlebypass (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict ("Failed to get throttle bypass: {0}".format (status))
        
        return set_success_dict ({"Row Bypass" : True if (state.value) else False})
    
    except Exception as error:
        return set_failure_dict ("get_row_throttle_bypass() Exception: {0}".format (error))
                                 
def set_row_throttle_bypass (enable):
    try:
        gpio_binary = get_gpio_library ()
        
        is_on = c_int (1 if enable else 0)
        state = c_int (0)
        status = gpio_binary.ocs_port_throttlebypass (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict ("Failed to set throttle bypass: {0}".format (status))
        
        return set_success_dict ()
    
    except Exception as error:
        return set_failure_dict ("set_manager_throttle_bypass() Exception: {0}".format (error))
    
def get_row_throttle_output_enable ():
    try:
        gpio_binary = get_gpio_library ()
        
        is_on = c_int (2)
        state = c_int (0)
        status = gpio_binary.ocs_port_rowthenable (is_on, byref (state))
        
        if (status != 0):
            return set_failure_dict (
                "Failed to get row throttle output enable: {0}".format (status))
        
        return set_success_dict ({"Row Enable" : True if (state.value) else False})
    
    except Exception as error:
        return set_failure_dict (
            "get_row_throttle_output_enable() Exception: {0}".format (error))
        
def set_row_throttle_output_enable (enable):
    try:
        gpio_binary = get_gpio_library()
        
        is_on = c_int(1 if enable else 0)
        state = c_int(0)
        status = gpio_binary.ocs_port_rowthenable(is_on, byref(state))
        
        if (status != 0):
            return set_failure_dict (
                "Failed to set row throttle output enable: {0}".format(status))
        
        return set_success_dict()
    
    except Exception as error:
        return set_failure_dict("set_row_throttle_output_enable() Exception: {0}".format(error))
    
def get_rack_manager_time():
    """ Returns current date and time in UTC
    """
    try:
        result = {}
        
        now = str(datetime.datetime.utcnow())
        
        result["Year"] = now[0:4]
        result["Month"] = now[5:7]
        result["Day"] = now[8:10]
        result["Hour"] = now[11:13]
        result["Min"] = now[14:16]
        result["Sec"] = now[17:19]
        
        return set_success_dict(result)
        
    except Exception, e:
        return set_failure_dict("get_rack_manager_time() Exception: {0}".format(e))

def show_rack_manager_time(edm = False):
    """ Returns formatted date and time in UTC
    """
    try:
        result = {}
        
        now = get_rack_manager_time()
                
        if edm:   
            result["DateTime"] = "{0}-{1}-{2}T{3}:{4}:{5}Z".format(now["Year"], now["Month"], now["Day"], 
                                                                   now["Hour"], now["Min"], now["Sec"])
        else:
            result["DateTime"] = "{0}-{1}-{2} {3}:{4}:{5}".format(now["Year"], now["Month"], now["Day"], 
                                                                  now["Hour"], now["Min"], now["Sec"])
        
        return set_success_dict(result)
    
    except Exception, e:
        return set_failure_dict("show_rack_manager_time() Exception: {0}".format(e))

def set_rack_manager_time(datetime = None, hour = -1, min = -1, sec = -1, month = -1, day = -1, year = -1):
    """ Sets system date and time
    """
    try:
        if datetime is not None:
            year, month, day, hour, min, sec = re.findall("\\d+", datetime)
        else:
            now = get_rack_manager_time()
            
            if hour == -1:
                hour = now["Hour"]
            elif hour > 23 or hour < 0:
                return set_failure_dict("Hour value out of range (0-23): {0}".format(hour), completion_code.failure)
            if min == -1:
                min = now["Min"]
            elif min > 59 or min < 0:
                return set_failure_dict("Minute value out of range (0-59): {0}".format(min), completion_code.failure)
            if sec == -1:
                sec = now["Sec"]
            elif sec > 59 or sec < 0:
                return set_failure_dict("Second value out of range (0-59): {0}".format(sec), completion_code.failure)
            if month == -1:
                month = now["Month"]
            elif month > 12 or month < 1:
                return set_failure_dict("Month value out of range (1-12): {0}".format(month), completion_code.failure)
            if day == -1:
                day = now["Day"]
            elif day > 31 or day < 1:
                return set_failure_dict("Day value out of range (1-31): {0}".format(day), completion_code.failure)
            if year == -1:
                year = now["Year"]
                
        newdate = "{0}-{1}-{2} {3}:{4}:{5}".format(year, month, day, hour, min, sec)
                        
        pipe = subprocess.check_output(["date", "-s", newdate], stderr = subprocess.STDOUT)

        return set_success_dict()
        
    except subprocess.CalledProcessError as e:
            return set_failure_dict("Failed to set system time: {0}".format(e.output.strip()), completion_code.failure)
                            
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("set_rack_manager_time - Exception: {0}".format(e))
    
def get_rack_manager_scandevice():
    """ Scan rack manager system information and print to user
    """
    
    try:
        # Check if admin user
        if not verify_caller_admin_permission():
            return set_failure_dict("Access Denied", completion_code.failure)
        
        try:
            # Call ScanDevices shell script
            pipe = subprocess.check_call("/usr/lib/commonapi/controls/scandevice.sh")
        
        except subprocess.CalledProcessError, e:
            print "Failed to run ScanDevice script: {0}".format(e)
            pass
        
        # Switch Link State
        print "\nRack Manager Switch Link State"
                
        switch = mgmt_switch()
        port = 1
        
        for state in switch.get_all_port_status():
            if state[completion_code.cc_key] != completion_code.success:
                print "\tExit Code: {0}, Error: {1}\n".format(state["ErrorCode"], 
                                                            state[completion_code.desc]) 
                break
                
            print "%d -> %s" % (port, repr(state))
            port = port + 1 
        
        try:
            switch.logout()
        except:
            pass
        
        return set_success_dict()
    
    except Exception, e:
        ocslog.log_exception()
        return set_failure_dict("get_rack_manager_scandevice - Exception: {0}".format(e))    
