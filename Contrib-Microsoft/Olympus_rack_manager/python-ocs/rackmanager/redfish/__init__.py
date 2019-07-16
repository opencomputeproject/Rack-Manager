# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import sys
sys.path.append ("/usr/lib/commonapi")

import ocslog
import bottle
import resources
import view_helper
from ocsrest import pre_check

try:
    ocslog.initialize_log (ocslog.loglevel_t_enum.INFO_LEVEL)
    
except Exception as error:
    print "Failed to initialize the ocslog", error
    
pre_check.set_op_mode ()
ocslog.log_info ("Running REST in configuration", pre_check.get_mode ())

class msocs_bottle (bottle.Bottle):
    def default_error_handler (self, res):
        bottle.response.content_type = "application/json"
        return view_helper.get_error_body (res.status_code, msg = res.body)
 
app = msocs_bottle (__name__)
resources.add_bottle_filters (app)
for name, resource in resources.REDFISH_RESOURCES.iteritems ():
    resource.register_resource (app, pre_check.get_mode (), name)
    
systems_app = msocs_bottle (__name__)
resources.add_bottle_filters (systems_app)
for name, resource in resources.REDFISH_SYSTEM_RESOURCES.iteritems ():
    resource.register_resource (systems_app, pre_check.get_mode (), name)