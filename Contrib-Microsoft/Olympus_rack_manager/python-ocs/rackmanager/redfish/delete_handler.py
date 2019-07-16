# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import parameters
import post_handler
import view_helper
from ocsrest import authentication, pre_check
from bottle import auth_basic
from pre_settings import command_name_enum
import controls.manage_user

############################
# Account service components
############################
@auth_basic (authentication.validate_user)
def delete_account (account):
    parameters.verify_account_name (account)
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    result = controls.manage_user.user_delete_by_name (account)
    return post_handler.check_action_result (result)
    
############################
# Manager Session components
############################    
@auth_basic (authentication.validate_user)
def delete_session (session):
    view_helper.run_pre_check (pre_check.pre_check_function_call, command_name_enum.set_rm_config)
    
    result = controls.manage_rack_manager.manager_session_kill (int(session))
    return post_handler.check_action_result (result)
