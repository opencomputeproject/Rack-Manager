# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
import ConfigParser
import Constants

#Set to default value
service_name = Constants.__serviceName__
service_host = Constants.__serviceHost__
service_port = Constants.__socketPort__
thread_pool = Constants.__threadPool__
switch_ip = None
switch_uart = Constants.__switchUART__
server_config = ConfigParser.ConfigParser()

class load_config:
    def __init__(self):
        server_config.read(Constants.__configfile__)
        server_config.sections()
        
        # Populate configuration settings
        self.loadSettings()
        
    def loadSettings(self):
        try:
            service_name = server_config.get('ServiceSettings', 'serviceName')            
            service_host = server_config.get('ServiceSettings', 'serviceHost')
            service_port = server_config.get('ServiceSettings', 'socketPort') 
            thread_pool = server_config.get('ServiceSettings', 'threadPool')
            switch_ip = server_config.get('ServiceSettings', 'switchIP')
            if (not switch_ip):
                switch_ip = None
            switch_uart = server_config.get('ServiceSettings', 'switchUART')
                        
        except:
            print("exception on reading configuration parameters")   