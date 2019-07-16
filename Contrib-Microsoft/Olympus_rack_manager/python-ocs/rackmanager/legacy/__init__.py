# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import sys
sys.path.append ("/usr/lib/commonapi")

import ocslog
import commands
from ocsrest import pre_check
from bottle import Bottle, request
from pre_settings import rm_mode_enum

try:
    ocslog.initialize_log (ocslog.loglevel_t_enum.INFO_LEVEL)
    
except Exception as error:
    print "Failed to initialize the ocslog", error

pre_check.set_op_mode ()
ocslog.log_info ("Running Legacy REST in configuration", pre_check.get_mode ())

app = Bottle (__name__)
app.route (path = "/<command>", method = "GET", callback = commands.process_command)
