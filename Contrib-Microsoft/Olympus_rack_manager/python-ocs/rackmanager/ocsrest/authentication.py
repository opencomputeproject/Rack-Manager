# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import ocslog
from ctypes import c_char_p
from controls.lib_utils import  get_authentication_library

def validate_user (username, password):
    """
    Authenticate the user login credentials.
    
    :param username: The user name.
    :parem password: The password for the user.
    
    :return True if the user credentials have been authenticated.
    """
    
    try:
        auth_binary = get_authentication_library ()
            
        usr = c_char_p (username)
        psw = c_char_p (password)            
        auth = auth_binary.verify_authentication (usr, psw)  
    
        if auth == 0:
            return True
        else:
            return False
    except:
        ocslog.log_exception ()
        return False