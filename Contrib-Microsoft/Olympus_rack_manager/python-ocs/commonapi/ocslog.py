# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import traceback
from controls.lib_utils import get_log_library
from ctypes import c_char_p, c_int

class loglevel_t:
    """
    Enumeration definition for the system logging levels.
    """
    
    map = {
        0 : "SILENT_LEVEL",
        1 : "ERROR_LEVEL",    
        2 : "INFO_LEVEL"
    }
    
    def __init__ (self, value):
        self.value = None
        for lock_id, name in loglevel_t.map.iteritems ():
            if ((lock_id == value) or (name == value)):
                self.value = value
                break

        if (self.value is None):
            raise TypeError ("Invalid log level identifier {0}.".format (value))
        
    def __str__ (self):
        return loglevel_t.map[self.value]
    
    def __repr__ (self):
        return self.str ()
    
    def __int__ (self):
        return self.value
    
    def __eq__ (self, other):
        if isinstance (other, int):
            return self.value == other
        if isinstance (other, basestring):
            return self.str () == other
        if isinstance (other, loglevel_t):
            return self.value == other.value
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result

class loglevel_t_enum:
    """
    Enumeration constants for the log levels.
    """
    
    SILENT_LEVEL = loglevel_t (0)
    ERROR_LEVEL = loglevel_t (1)
    INFO_LEVEL = loglevel_t (2)
   
def initialize_log (level):
    """
    Initialize the log instance.
    
    :param level: The logging level for the log instance.
    """
    
    log_binary = get_log_library ()
    
    lev = c_int (int (level))
    log_binary.log_init (lev)
    
def log_out (*args):
    """
    Log a message to stdout.
    
    :param args: The list of items to concatenate together for the message.
    """
     
    out = " ".join (map (str, args))
    try:
        log_binary = get_log_library ()
        
        msg = c_char_p (out)
        log_binary.log_out (msg)
        
    except:
        print out
    
def log_info (*args):
    """
    Log a message to the log at info level.
    
    :param args: The list of items to concatenate together for the message.
    """
    
    try:
        log_binary = get_log_library ()
        
        msg = c_char_p (" ".join (map (str, args)))
        log_binary.log_info (msg)
        
    except:
        pass
        
def log_error (error, *args):
    """
    Log a message to the log at error level.
    
    :param error: The error code for the message.
    :param args: The list of items to concatenate together for the message.
    """
    
    try:
        log_binary = get_log_library ()
        
        err = c_int (error)
        msg = c_char_p (" ".join (map (str, args)))
        log_binary.log_err (err, msg)
        
    except:
        pass
    
def log_exception (limit = None):
    """
    Log information about the last received exception.
    
    :param trace: Flag indicating if traceback information should be logged.
    """
    
    try:
        log_binary = get_log_library ()
        
        err = c_char_p (traceback.format_exc (limit = limit))
        log_binary.log_exception (err)
        
    except:
        pass