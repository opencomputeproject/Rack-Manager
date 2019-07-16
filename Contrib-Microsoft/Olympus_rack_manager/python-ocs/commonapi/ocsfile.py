# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from ctypes import c_char_p, c_ulong
from controls.lib_utils import get_file_library

def ocs_file_write_complete_file (path, data):
    """
    Write data to a system-critital file, completely replacing the existing file.
    
    :param path: The path of the file to write.
    :param data: The data to write to the file.
    """
    
    file_bin = get_file_library ()
    
    path_str = c_char_p (path)
    data_str = c_char_p (data)
    length = c_ulong (len (data))
    
    status = file_bin.ocs_file_write_complete_file (path_str, data_str, length)
    if (status != 0):
        raise RuntimeError ("Failed to write file {0} ({1}).".format (path, status))
    
def ocs_file_ensure_valid (path):
    """
    Check a file to ensure that is is currently valid and restore it to a valid state if it is not.
    
    :param path: The path of the file to validate.
    """
    
    file_bin = get_file_library ()
    
    path_str = c_char_p (path)
    status = file_bin.ocs_file_ensure_valid (path_str)
    if (status != 0):
        raise RuntimeError ("Failed to validate file {0} ({1}).".format (path, status))