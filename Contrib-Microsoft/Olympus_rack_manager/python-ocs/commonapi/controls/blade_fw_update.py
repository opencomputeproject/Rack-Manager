# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/env python

import sys
import time
import os.path
import paramiko

from ocspaths import *
from argparse import ArgumentParser
from ctypes import create_string_buffer
from lib_utils import get_blade_map_library
from utils import set_failure_dict, set_success_dict, completion_code
from ipmicmd_library import get_ipmi_interface, get_hostname_by_serverid, call_ipmi

class blade_fw_type:
    """
    Enumeration definition for the type of firmware image being updated.
    """
    
    map = {
        0 : "bootloader",
        1 : "image A",
        2 : "image B"
    }
    
    def __init__ (self, value):
        value = int (value)
        if (value not in blade_fw_type.map):
            raise TypeError ("Invalid firmware image type {0}.".format (value))
        
        self.value = value
        
    def __str__ (self):
        return blade_fw_type.map[self.value]
    
    def __repr__ (self):
        return str (self.value)
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, blade_fw_type):
            return self.value == other.value
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result

class blade_fw_type_enum:
    """
    Enumeration constants for the blade FW type.
    """
    
    BOOTLOADER = blade_fw_type (0)
    IMAGE_A = blade_fw_type (1)
    IMAGE_B = blade_fw_type (2)
    
class blade_fw_operation:
    """
    Enumeration definition for the operation to perform for the firmware image request.
    """
    
    map = {
        1 : "start",
        2 : "abort",
        3 : "query"
    }
    
    def __init__ (self, value):
        value = int (value)
        if (value not in blade_fw_operation.map):
            raise TypeError ("Invalid firmware operation {0}.".format (value))
        
        self.value = value
        
    def __str__ (self):
        return blade_fw_operation.map[self.value]
    
    def __repr__ (self):
        return str (self.value)
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, blade_fw_operation):
            return self.value == other.value
        elif isinstance (other, int):
            return self.value == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class blade_fw_operation_enum:
    """
    Enumeration constants for the blade FW operation.
    """
    
    START = blade_fw_operation (1)
    ABORT = blade_fw_operation (2)
    QUERY = blade_fw_operation (3)

# Globally configure the paramiko logging.
import logging
logging.getLogger ("paramiko").setLevel (logging.CRITICAL)

def get_sftp_access ():
    """
    Get the login credentials for SFTP access to the server.
    
    :return The username and password to use for SFTP access.
    """
    
    blade_lib = get_blade_map_library ()
    
    user = create_string_buffer (48)
    passwd = create_string_buffer (48)
    status = blade_lib.get_server_console_access (user, passwd)
    
    if (status != 0):
        raise RuntimeError("Failed to get SFTP login credentials.")
    
    return user.value, passwd.value

def get_fw_image_type (fw_path):
    """
    Determine the type of firmware image being updated based on the file name.
    
    :param fw_path: The path to the image being used for the update.
    
    :return The type of the firmware image file.
    """
    
    if ("RegionA" in fw_path):
        return blade_fw_type_enum.IMAGE_A
    elif ("RegionB" in fw_path):
        return blade_fw_type_enum.IMAGE_B
    else:
        raise RuntimeError("Could not determine the firmware type from file {0}".format (fw_path))
    
def upload_fw_image(blade_id, fw_file, dest):
    """
    Upload a firmware file to a blade.
    
    :param blade_id: The ID of the blade that should receive the file.
    :param fw_file: The name of firmware file to upload.
    :param dest: The destination directory where the file should be placed.
    
    :return The remote path of the uploaded file.
    """
    
    fw_path = srvroot_shared_path + "/" + fw_file
    
    if (not os.path.exists(fw_path)):
        raise IOError("FW image file does not exist: " + fw_file)
    
    fw_dest = dest + "/" + "PSU_FW.hex"
    
    blade_host = get_hostname_by_serverid (blade_id)
        
    if (blade_host == -1):
        raise LookupError("Failed to determine host for blade {0}".format(blade_id))
    
    user, passwd = get_sftp_access()
    try:
        # Connect to the blade.
        transport = paramiko.Transport((blade_host, 22))
        transport.connect(username = user, password = passwd)
    
        # Send the file.
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(fw_path, fw_dest)
        
    finally:
        try:
            # Disconnect from the blade.
            sftp.close()
            transport.close()
        except:
            pass
        
    return fw_dest
        
def send_psu_fw_ipmi_request (blade_id, fw_type, operation, fw_name = None):
    """
    Send an IMPI PSU firmware command to the blade.
    
    :param blade_id: The ID of the blade to send the requset to.
    :param fw_type: The type of firmware for the request.
    :param operation: The command operation to perform.
    :param fw_name: The name of the firmware file.  Required for START requests.
        
    :return The IPMI command result.
    """
    
    cmd_args = ["ocsoem", "psufwupdate", "1", repr (fw_type), repr (operation)]
    if ((fw_name is not None) and (blade_fw_operation_enum.START == operation)):
        cmd_args.append (fw_name)
    interface = get_ipmi_interface (blade_id, cmd_args)
        
    result = call_ipmi (interface, "psufwupdate")
    if (completion_code.cc_key in result):
        return result
    
    fw_resp = {}
    if (result["status_code"] == 0):
        fw_resp["FW Status"] = result["stdout"].split (":")[1].strip ()
        fw_resp = set_success_dict (fw_resp)
    else:
        error_data = result["stderr"].split ("\n")
        fw_resp[completion_code.cc_key] = completion_code.failure
        
        for data in error_data:
            if ("Error sending" in data):
                ipmi_error = data.split (":")
                fw_resp[completion_code.desc] = ipmi_error[0].strip ()
                if (len (ipmi_error) > 1):
                    fw_resp[completion_code.ipmi_code] = ipmi_error[1].strip ()
            elif ("Error:" in data):
                fw_resp[completion_code.desc] = data.split (":")[-1].strip ()
            elif ("Failed" in data) or ("PSU firmware" in data):
                fw_resp[completion_code.desc] = data.strip ()
                
    return fw_resp;
    
def start_psu_fw_update(blade_id, fw_file, fw_type):
    """
    Start the firmware update for the blade PSU firmware.
    
    :param blade_id: The ID of the blade to update.
    :param fw_file: The name of the PSU firmware file to use for the update.
    :param fw_type: An enumeration instance for the type of firmware image being updated.
        
    :return Completion information.
    """
    
    if ((blade_id < 1) or (blade_id > 48)):
        return set_failure_dict("Expected blade ID between 1 and 48.")  
    
    try:
        remote_path = upload_fw_image(blade_id, fw_file, "/var/wcs/home")
        status = send_psu_fw_ipmi_request (blade_id, fw_type, blade_fw_operation_enum.START,
            os.path.basename (remote_path))
        
        if ("in progress" not in status["FW Status"]):
            return set_failure_dict(status["FW Status"])
        
        return status
        
    except IOError, e:
        return set_failure_dict("FW image file does not exist: {0}".format(fw_file), completion_code.failure)
        
    except Exception, e:
        return set_failure_dict("start_psu_fw_update - Exception: {0}".format(e))
    
def abort_psu_fw_update (blade_id, fw_type = blade_fw_type_enum.IMAGE_A):
    """
    Abort the active firmware update for the blade PSU firmware.
    
    :param blade_id: The ID of the blade PSU to abort.
    :param fw_type: An enumeration instance for the type of firmware image being updated.
    
    :return Completion information.
    """
    
    if ((blade_id < 1) or (blade_id > 48)):
        return set_failure_dict ("Expected blade ID between 1 and 48.")
    
    try:
        return send_psu_fw_ipmi_request (blade_id, fw_type, blade_fw_operation_enum.ABORT)
    
    except Exception as error:
        return set_failure_dict ("abort_psu_fw_update () Exception: {0}".format (error))
    
def query_psu_fw_update (blade_id, fw_type = blade_fw_type_enum.IMAGE_A):
    """
    Query the blade for the status of PSU firmware update.
    
    :param blade_id: The ID of the blade to query.
    :param fw_type: An enumeration instance for the type of firmware being queried.
        
    :return Completion information.
    """
    
    if ((blade_id < 1) or (blade_id > 48)):
        return set_failure_dict ("Expected blade ID between 1 and 48")  
    
    try:
        return send_psu_fw_ipmi_request (blade_id, fw_type, blade_fw_operation_enum.QUERY)
        
    except Exception as error:
        return set_failure_dict ("query_psu_fw_update () Exception: {0}".format (error))
    
if __name__ == "__main__":
    parser = ArgumentParser ()
    
    parser.add_argument ("-s", "--server", type = int, required = True,
        help = "The ID of the server to update")
    parser.add_argument ("-S", "--start", action = "store_true", help = "Start the firmware update")
    parser.add_argument ("-Q", "--query", action = "store_true",
        help = "Query the firmware progress")
    parser.add_argument ("-A", "--abort", action = "store_true",
        help = "Abort the current firmware update.")
    parser.add_argument ("-F", "--full", action = "store_true",
        help = "Start the upgrade and monitor until finished or an error is encountered.")
    parser.add_argument ("-U", "--upload", action = "store_true",
        help = "Only upload the firmware file to the server.")
    parser.add_argument ("-I", "--ipmi", help = "Only send a FW IPMI command for an operation.")
    parser.add_argument ("-p", "--path", help = "The path to the firmware update file")
    parser.add_argument ("-r", "--region", help = "The firmware region being updated")
    
    args = parser.parse_args ()
    if ((not args.start) and (not args.query) and (not args.full) and (not args.upload)
        and (not args.ipmi)):
        print "No firmware update action specified."
        sys.exit (1)
    if ((args.start or args.full or args.upload) and (not args.path)):
        print "Firmware path is required for the specified action."
        sys.exit (1)
    if (args.query and (not args.region)):
        print "Firmware reqion is required for the specified action."
        sys.exit (1)
    if (args.ipmi):
        operation = blade_fw_operation (args.ipmi)
        if ((operation == blade_fw_operation_enum.START) and (not args.path)):
            print "Firmware path is required for the specified action."
            sys.exit (1)            
    
    if (args.region):
        region = blade_fw_type (args.region)
    elif ((not args.upload) and (not args.query) and (not args.abort)):
        if (args.path):
            region = get_fw_image_type (args.path)
        else:
            print "FW region or file name must be specified."
            sys.exit (1)
    else:
        region = blade_fw_type_enum.IMAGE_A
    
    if (args.upload):
        upload_fw_image (args.server, args.path, "/var/wcs/home")
        print "File {0} uploaded.".format (args.path)
        sys.exit (0)
        
    if (args.ipmi):
        result = send_psu_fw_ipmi_request (args.server, region, operation, args.path)
        print "IPMI:", result
        sys.exit (0)
        
    if (args.start or args.full):
        result = start_psu_fw_update (args.server, args.path, region)
        print "Start:", result
        while (args.full):
            status = query_psu_fw_update (args.server, region)
            print "Status:", status
            
            if ((status[completion_code.cc_key] != completion_code.success) or
                ("in progress" not in status["FW Status"])):
                args.full = False
                
            if (args.full):
                time.sleep (1)
        
    if (args.query):
        result = query_psu_fw_update (args.server, region)
        print "Query:", result
        
    if (args.abort):
        result = abort_psu_fw_update (args.server, region)
        print "Abort:", result
        