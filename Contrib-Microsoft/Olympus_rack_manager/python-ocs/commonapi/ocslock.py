# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import ocslog
from ctypes import c_int
from controls.lib_utils import get_lock_library

class ocslock_t:
    """
    Enumeration definition for the available system locks.
    """
    
    map = {
        0 : "PRU_CHARDEV",
        1 : "PRU_SEQNUM",    
        2 : "TELEMETRY_DAEMON",     
        3 : "OCSGPIOACCESS",        
        4 : "I2C0_CHARDEV",
        5 : "I2C1_CHARDEV",
        6 : "PRU_PERSIST",
        7 : "OCSLOG_SHM",
        8 : "NVDIMM_DAEMON",
        9 : "USR_ACCNT",
        10 : "NET_CONFIG",
        11 : "OCSFILE_WRITE",
    }
    
    def __init__ (self, value):
        self.value = None
        for lock_id, name in ocslock_t.map.iteritems ():
            if ((lock_id == value) or (name == value)):
                self.value = value
                break

        if (self.value is None):
            raise TypeError ("Invalid lock identifier {0}.".format (value))
        
    def __str__ (self):
        return ocslock_t.map[self.value]
    
    def __repr__ (self):
        return self.str ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, int):
            return self.value == other
        if isinstance (other, basestring):
            return self.str () == other
        if isinstance (other, ocslock_t):
            return self.value == other.value
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result

class ocslock_t_enum:
    """
    Enumeration constants for the system locks.
    """
    
    PRU_CHARDEV = ocslock_t (0)
    PRU_SEQNUM = ocslock_t (1)
    TELEMETRY_DAEMON = ocslock_t (2)
    OCSGPIOACCESS = ocslock_t (3)
    I2C0_CHARDEV = ocslock_t (4)
    I2C1_CHARDEV = ocslock_t (5)
    PRU_PERSIST = ocslock_t (6)
    OCSLOG_SHM = ocslock_t (7)
    NVDIMM_DAEMON = ocslock_t (8)
    USR_ACCNT = ocslock_t (9)
    NET_CONFIG = ocslock_t (10)
    OCSFILE_WRITE = ocslock_t (11)
        
def ocs_lock (lock):
    """
    Acquire an OCS system lock.
    
    :param lock: The enumeration for the lock to acquire.
    """
    
    lock_bin = get_lock_library ()
    
    lock_id = c_int (int (lock))
    status = lock_bin.ocs_lock (lock_id)
    if (status != 0):
        raise RuntimeError ("Failed to acquire {0} lock: {1}.".format (lock, status))
    
def ocs_unlock (lock):
    """
    Release an OCS system lock.
    
    :param lock: The enumeration for the lock to release.
    """
    
    lock_bin = get_lock_library ()
    
    lock_id = c_int (int (lock))
    status = lock_bin.ocs_unlock (lock_id)
    if (status != 0):
        ocslog.log_error (status, "Failed to release {0} lock.".format (lock))
        