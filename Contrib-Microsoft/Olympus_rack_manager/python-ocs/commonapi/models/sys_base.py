# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

class sys_base:
    def __init__(self, info = None, works = None):
        
        if info == None:
            self.info = {}
        else:
            self.info = info

        if works == None:
            self.works = []
        else:
            self.works = works

    def getServiceProvides(self):
        return self.info

    def getWorks(self):
        return self.works

    def doworks(self, works):
        result = { "status_code": 'failure', "reason": 'not supported'}