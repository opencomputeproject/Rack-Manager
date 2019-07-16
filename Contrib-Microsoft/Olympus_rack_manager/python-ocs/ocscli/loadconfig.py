# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import ConfigParser
import constants

prompt = constants.__prompt__
#EnabledCommands = constants.__allowedCmds__

Config = ConfigParser.ConfigParser()

class loadconfig:
    def __init__(self):
        Config.read(constants.__configfile__)
        Config.sections()
        
        # Populate configuration settings
        self.loadSettings()
        
    def loadSettings(self):
        try:
            prompt = Config.get('ShellSettings', 'Prompt')
                        
        except:
            print("exception on reading configuration parameters")   