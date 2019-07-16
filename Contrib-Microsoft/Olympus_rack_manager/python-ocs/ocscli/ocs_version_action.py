# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# -*- coding: UTF-8 -*-

from utils_print import * 
from ocsaudit_log import *
from controls.utils import *
from controls.manage_fwversion import *


#######################################################
# Get Version Function
#######################################################
def show_service_version():
    """ Print software versions
    """
    try:
        ocsaudit_log_command("", cmd_type.type_show, cmd_interface.interface_ocscli, 
                             "version", "")
                   
        info = get_ocsfwversion(raw = True)
        
        if completion_code.cc_key in info.keys():        
            print_response(info)
        else:
            print(info['stdout'])
            return
    
    except Exception, e:
        print "show_service_version - Exception: {0}".format(e)
        return
