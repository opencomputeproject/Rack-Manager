# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import os
import ctypes
from threading import Lock

hdc_lib = '/usr/lib/libocshdc.so'
hdc_lib_bin = None

hsc_lib = '/usr/lib/libocshsc.so'
hsc_lib_bin = None

gpio_lib = '/usr/lib/libocsgpio.so.1'
gpio_lib_bin = None

fwupdate_lib = '/usr/lib/libocsfwupgrade.so.1'
fwupdate_lib_bin = None

parser_lib = '/usr/lib/libocstelemetry_parse.so'
parser_lib_bin = None

auth_lib = '/usr/lib/libocsauth.so'
auth_lib_bin = None

precheck_lib = '/usr/lib/libocsprecheck.so'
precheck_lib_bin = None

pru_lib = '/usr/lib/libocspru.so'
pru_lib_bin = None

blademap_lib = "/usr/lib/libocsblademap.so"
blademap_lib_bin = None

audit_lib = "/usr/lib/libocsaudit.so"
audit_lib_bin = None

lock_lib = "/usr/lib/libocslock.so"
lock_lib_bin = None

log_lib = "/usr/lib/libocslog.so"
log_lib_bin = None

file_lib = "/usr/lib/libocsfile.so"
file_lib_bin = None

load_lock = Lock ()

def load_library (path, name, binary = None):
    if (binary is None):
        try:
            load_lock.acquire ()
            if (binary is None):
                if os.path.isfile (path) :
                    binary = ctypes.cdll.LoadLibrary (path)
                else:
                    raise RuntimeError ("Failed to load {0} library".format (name))
    
                if (binary is None):
                    raise RuntimeError ("Failed to load {0} library".format (name))
    
        finally:
            load_lock.release ()
            
    return binary
    
def get_audit_library ():
    global audit_lib_bin
    return load_library (audit_lib, "ocsaudit", audit_lib_bin)

def get_gpio_library ():
    global gpio_lib_bin
    return load_library (gpio_lib, "ocsgpio", gpio_lib_bin)

def get_hsc_library ():
    global hsc_lib_bin
    return load_library (hsc_lib, "ocshsc", hsc_lib_bin)

def get_hdc_library ():
    global hdc_lib_bin
    return load_library (hdc_lib, "oschdc", hdc_lib_bin)

def get_fwupdate_library ():
    global fwupdate_lib_bin
    return load_library (fwupdate_lib, "ocsfwupgrade", fwupdate_lib_bin)

def get_telemetry_library ():
    global parser_lib_bin
    return load_library (parser_lib, "ocstelemetry parser", parser_lib_bin)

def get_authentication_library ():
    global auth_lib_bin
    return load_library (auth_lib, "ocsauth", auth_lib_bin)

def get_precheck_library ():
    global precheck_lib_bin
    return load_library (precheck_lib, "ocsprecheck", precheck_lib_bin)

def get_pru_library ():
    global pru_lib_bin
    return load_library (pru_lib, "ocspru", pru_lib_bin)

def get_blade_map_library ():
    global blademap_lib_bin
    return load_library (blademap_lib, "ocsblademap", blademap_lib_bin)

def get_lock_library ():
    global lock_lib_bin
    return load_library (lock_lib, "ocslock", lock_lib_bin)

def get_log_library ():
    global log_lib_bin
    return load_library (log_lib, "ocslog", log_lib_bin)

def get_file_library ():
    global file_lib_bin
    return load_library (file_lib, "ocsfile", file_lib_bin)
