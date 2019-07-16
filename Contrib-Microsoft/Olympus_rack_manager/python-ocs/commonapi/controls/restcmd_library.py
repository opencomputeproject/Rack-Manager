# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import subprocess
import json
from ipmicmd_library import get_hostname_by_serverid
from lib_utils import get_blade_map_library
from ctypes import create_string_buffer, byref

class rest_http_error (Exception):
    """
    Exception to indicate REST HTTP request errors.
    """
    
    def __init__ (self, code, body = ""):
        self.status_code = code
        self.body = body
        
    def __str__ (self):
        if (self.body):
            return self.body
        else:
            return str (self.status_code)
    
def send_redfish_request (serverid, uri, service_port = 0, method = "GET", data = None,
    encrypted = True, connect_timeout = 2):
    """
    Send a Redfish request to the REST service on a system.
    
    :param serverid: The ID for the server to send the request to.
    :param uri: The resource to access.
    :param service_port: The port the REST service is listening on.
    :param method: The HTTP request type to execute.
    :param data: The data to send with the request.
    :param encrypted: Flag indicating if HTTPS should be used for the requested instead of plain
        HTTP.
    :param connect_timeout: The number of seconds to wait for a connection before timing out the
    request.
        
    :return The data returned from the Redfish request.
    """
    
    access = get_blade_map_library ()
    
    user = create_string_buffer (48)
    passwd = create_string_buffer (48)
    status = access.get_server_rest_access (byref (user), byref (passwd))
    if (status != 0):
        raise RuntimeError ("Failed to get server access credentials: {0}".format (status))
    
    try:
        ip = get_hostname_by_serverid (serverid)
        cmd = ["curl", "-sS", "-k", "-i", "-u", "{0}:{1}".format (user.value, passwd.value),
            "-X", method, "--connect-timeout", "{0}".format (connect_timeout)]
        if (data):
            cmd.extend (["-d", "{0}".format (data), "-H", "Content-Type: application/json"])
        cmd.append ("{0}://{1}{2}{3}".format ("https" if (encrypted) else "http", ip,
            "" if (not service_port) else ":{0}".format (service_port), uri))

        response = subprocess.check_output (cmd, stderr = subprocess.STDOUT)
        status, body = parse_http_response (response)
        if (status >= 300):
            raise rest_http_error (status, body)
        
        return body
    
    except subprocess.CalledProcessError as error:
        raise RuntimeError (error.output.strip ())
    
def parse_http_response (response):
    """
    Parse the response from a REST request to determine the request status code and get the response
    data.
    
    :param response: The response received from the request.
    
    :return A tuple containing the response status code and body.
    """
    
    line_start = 0
    while (True):
        line_end = response.index ("\r\n", line_start)
        status_line = response[:line_end].split ()
        status_code = int (status_line[1])
        if (status_code >= 200):
            break;
        
        line_start = response.index ("\r\n\r\n", line_start) + 4
        
    body = response.index ("\r\n\r\n", line_start) + 4
    return (status_code, response[body:])

def parse_redfish_response (response, remove_annotations = True, dict_type = dict):
    """
    Parse a Redfish response message to generate a dictionary with the received information.
    
    :param response: The response string received from the Redfish service.
    :param remove_annotations: A flag indicating if annotations in the Redfish response should be
    removed from the parsed dictionary.
    :parm dict_type: The type of dictionary object to generate.
    
    :return A dictionary with the parsed information.  Regardless of the value of the
    'remove_annotations' flag, the completion code information will remain in the
    '@Message.ExtendendInfo' property.
    """
    
    parsed = json.loads (response, object_pairs_hook = dict_type)
    
    if (remove_annotations):
        remove_redfish_annotations (parsed)
        
    return parsed
                
def remove_redfish_annotations (data):
    """
    Remove the annotation properties from a Redfish response.  The "@Message.ExtendedInfo" property
    will remain.
    
    :param data: The Redfish JSON data to remove annotations from.
    """
    
    for prop, value in data.items ():
        if (hasattr (value, "keys")):
            remove_redfish_annotations (value)
        elif (isinstance (value, list)):
            for obj in value:
                if (hasattr (obj, "keys")):
                    remove_redfish_annotations (obj)
            
            data[prop] = filter (None, value)
        
        if (not prop == "@Message.ExtendedInfo"):
            if ("@" in prop):
                del data[prop]
            elif ((hasattr (value, "keys") or isinstance (value, list)) and (not data[prop])):
                del data[prop]