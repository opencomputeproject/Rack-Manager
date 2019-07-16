# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import redfish
import view_helper
import ocslog
from ocsrest import authentication, pre_check
from bottle import auth_basic, request, HTTPError
from pre_settings import command_name_enum
import controls.bladeinfo_lib
import controls.restcmd_library

###################
# System components
###################
@auth_basic (authentication.validate_user)
def route_system_request (system, path = ""):
    view_helper.run_pre_check (pre_check.pre_check_blade_availability, system)
    
    ctrl = ""
    try:
        ctrl = controls.bladeinfo_lib.get_server_control_interface (system)[2]
        
    except Exception as error:
        ocslog.log_exception ()
        return view_helper.return_status_response (500,
            "Failed to discover system control interface.")
        
    if (ctrl == "REST"):
        if (request.method == "GET"):
            view_helper.run_pre_check (pre_check.pre_check_function_call,
                command_name_enum.get_blade_state)
        else:
            view_helper.run_pre_check (pre_check.pre_check_function_call,
                command_name_enum.set_blade_config)
        
        try:
            return controls.restcmd_library.send_redfish_request (serverid = int (system),
                uri = request.path, method = request.method, data = request.body.read ())
            
        except controls.restcmd_library.rest_http_error as error:
            ocslog.log_exception ()
            raise HTTPError (status = error.status_code)
        
        except Exception as error:
            ocslog.log_exception ()
            return view_helper.return_status_response (500,
                "Failed to query system REST interface.")
    else:
        route = redfish.systems_app.match (request.environ)
        return route[0].call (**route[1])