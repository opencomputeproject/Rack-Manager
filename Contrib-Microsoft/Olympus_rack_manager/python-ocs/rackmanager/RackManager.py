# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy as cpy
from cherrypy.wsgiserver import CherryPyWSGIServer
from cherrypy.wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
from argparse import ArgumentParser

def run_rack_manager_default (app, ssl_enabled, host = '0.0.0.0', port = 8080, number_threads = 30,
    config = None, **kwargs):
    if config is not None:
        cpy.config.update (config)
    
    server = CherryPyWSGIServer ((host,port), app, numthreads = number_threads, **kwargs)
    
    if (ssl_enabled):
        server.ssl_adapter = pyOpenSSLAdapter (certificate="/usr/lib/sslcerts/certs.pem",
            private_key="/usr/lib/sslcerts/privkey.pem")
    
    try:
        server.start ()
    except KeyboardInterrupt:
        server.stop ()
    
if __name__ == "__main__":
    parser = ArgumentParser ()
    parser.add_argument ("type", nargs = "?", default = "redfish")
    args = parser.parse_args ()
    
    if (args.type == "redfish"):
        import load_config
        from redfish import app as redfish_app
        
        # Load configuration settings    
        load_config.load_config ()
        run_rack_manager_default (app = redfish_app, ssl_enabled = True,
            host = load_config.service_host, port = load_config.service_port,
            number_threads = load_config.thread_pool)
    elif (args.type == "legacy"):
        from legacy import app as legacy_app
        
        run_rack_manager_default (app = legacy_app, ssl_enabled = True, port = 8000)
    elif (args.type == "compile"):
        from redfish import app as redfish_app
        from legacy import app as legacy_app
        
        # We just want to force the python files to compile to avoid multiple processes compiling
        # the code at the same time.
        pass
    else:
        print "Unknown REST service type:", args.type
        exit (1)