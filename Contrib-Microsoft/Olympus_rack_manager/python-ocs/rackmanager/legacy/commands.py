# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import command_handler
import ocslog
from ocsrest import authentication, pre_check
from bottle import request, response, HTTPError, HTTPResponse, auth_basic
from xml.etree import ElementTree
from pre_settings import rm_mode_enum

@auth_basic (authentication.validate_user)
def process_command (command):
    """
    Extract the command parameters and execute the command.
    
    :param command: The command being executed.
    """
    
    try:
        handler = COMMANDS.get (command.lower (), None)
        if (not handler):
            raise HTTPError (status = 404)
        
        parameters = {}
        for name, value in request.query.iteritems ():
            parameters[name.lower ()] = value.lower ()
        
        execute = handler (parameters)
        execute.pre_check ()
        
        if (pre_check.get_mode () != rm_mode_enum.rowmanager):
            result = execute.get_response ()
        else:
            result = execute.get_row_manager ()
        result = result.format ()[0]
        
        response.content_type = "application/xml"
        response.status = 200
        response.body = [ElementTree.tostring (result)]
        return response
    
    except (HTTPResponse, HTTPError):
        raise
    
    except:
        ocslog.log_exception ()
        raise HTTPError (status = 500)

##
# The list of command resources and the associated handler.
##
COMMANDS = {
    "getchassisinfo" : command_handler.get_chassis_info,
    "getbladeinfo" : command_handler.get_blade_info,
    "getallbladesinfo" : command_handler.get_all_blades_info,
    "setchassisattentionledon" : command_handler.set_chassis_led_on,
    "setchassisattentionledoff" : command_handler.set_chassis_led_off,
    "getchassisattentionledstatus" : command_handler.get_chassis_led_status,
    "setbladeattentionledon" : command_handler.set_blade_led_on,
    "setallbladesattentionledon" : command_handler.set_all_blades_led_on,
    "setbladeattentionledoff" : command_handler.set_blade_led_off,
    "setallbladesattentionledoff" : command_handler.set_all_blades_led_off,
    "setbladedefaultpowerstateon" : command_handler.set_blade_default_power_state_on,
    "setallbladesdefaultpowerstateon" : command_handler.set_all_blades_default_power_state_on,
    "setbladedefaultpowerstateoff" : command_handler.set_blade_default_power_state_off,
    "setallbladesdefaultpowerstateoff" : command_handler.set_all_blades_default_power_state_off,
    "getbladedefaultpowerstate" : command_handler.get_blade_default_power_state,
    "getallbladesdefaultpowerstate" : command_handler.get_all_blades_default_power_state,
    "getpowerstate" : command_handler.get_power_state,
    "getallpowerstate" : command_handler.get_all_power_state,
    "setpoweron" : command_handler.set_power_on,
    "setallpoweron" : command_handler.set_all_power_on,
    "setpoweroff" : command_handler.set_power_off,
    "setallpoweroff" : command_handler.set_all_power_off,
    "setbladeon" : command_handler.set_blade_on,
    "setallbladeson" : command_handler.set_all_blades_on,
    "setbladeoff" : command_handler.set_blade_off,
    "setallbladesoff" : command_handler.set_all_blades_off,
    "getbladestate" : command_handler.get_blade_state,
    "getallbladesstate" : command_handler.get_all_blades_state,
    "setbladeactivepowercycle" : command_handler.set_blade_active_power_cycle,
    "setallbladesactivepowercycle" : command_handler.set_all_blades_active_power_cycle,
    "setacsocketpowerstateon" : command_handler.set_ac_socket_power_on,
    "setacsocketpowerstateoff" : command_handler.set_ac_socket_power_off,
    "getacsocketpowerstate" : command_handler.get_ac_socket_power_state,
    "getbladepowerreading" : command_handler.get_blade_power_reading,
    "getallbladespowerreading" : command_handler.get_all_blades_power_reading,
    "getbladepowerlimit" : command_handler.get_blade_power_limit,
    "getallbladespowerlimit" : command_handler.get_all_blades_power_limit,
    "setbladepowerlimit" : command_handler.set_blade_power_limit,
    "setallbladespowerlimit" : command_handler.set_all_blades_power_limit,
    "setbladepowerlimiton" : command_handler.set_blade_power_limit_on,
    "setallbladespowerlimiton" : command_handler.set_all_blades_power_limit_on,
    "setbladepowerlimitoff" : command_handler.set_blade_power_limit_off,
    "setallbladespowerlimitoff" : command_handler.set_all_blades_power_limit_off,
    "addchassiscontrolleruser" : command_handler.add_chassis_controller_user,
    "changechassiscontrolleruserpassword" : command_handler.change_chassis_controller_user_password,
    "changechassiscontrolleruserrole" : command_handler.change_chassis_controller_user_role,
    "removechassiscontrolleruser" : command_handler.remove_chassis_controller_user,
    "getchassishealth" : command_handler.get_chassis_health,
    "getnextboot" : command_handler.get_next_boot,
    "setnextboot" : command_handler.set_next_boot,
    "getserviceversion" : command_handler.get_service_version,
}