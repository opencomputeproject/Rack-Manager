# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

import re
from bottle import HTTPError
from netaddr import IPAddress
from controls.manage_user import user_list_all

class parameter_parser:
    """
    Parsing utility to validate and parse received parameters.
    """
    
    def __init__ (self, name, cast, conversion = None, conv_args = None):
        """
        Create a new parser instance to parse a single parameter.
        
        :param name: The name of the parameter.
        :param cast: The type to cast the parameter value to.
        :param coversion: A function to provide any necessary conversion on the parameter value.
        :param covn_args: A dictionary of arguments to pass to the conversion function.
        """
        
        self.name = name
        self.cast = cast
        self.conversion = conversion
        self.args = conv_args
        
    def parse_parameter (self, value, params):
        """
        Parse a parameter value to create a function argument.
        
        :param value: The parameter value to parse.
        :param params: The dictionary of parsed parameters to update with the parsed value.
        """
        
        if self.conversion:
            if self.args:
                convert = self.conversion (value, **self.args)
            else:
                convert = self.conversion (value)
        else:
            convert = value
        
        params[self.name] = self.cast (convert)
        
    @staticmethod
    def validate_bool (value):
        """
        Validate that a value is a boolean.
        
        :param value: The value to check.
        """
        
        if (not isinstance (value, bool)):
            raise TypeError ("Not a boolean value.")
        
        return value
        
    @staticmethod
    def validate_subnet_mask (value):
        """
        Validate that a value represents a valid subnet mask.
        
        :param value: The value to check.
        """
        
        if (not IPAddress (value).is_netmask ()):
            raise ValueError ("{0} is not a valid SubnetMask.".format (value))
        
        return value
    
def verify_account_name (account):
    """
    Verify that an account matches an available account on the system.  If no such account exists,
    a 404 error is raised.
    
    :param account: The account name to check.
    
    :return True
    """
    
    users = user_list_all ()
    for user in users["accounts"].itervalues ():
        if (account in user):
            return True
    
    raise HTTPError (status = 404)

def remove_non_numeric (value):
    """
    Remove non-numeric characters from value.
    
    :param value: The value to be modified.
    
    :return Numeric value.
    """
    
    return re.sub("[^0-9]", "", value)

def extract_number (value, int_only = False):
    """
    Extract the numberic value from a string.  This can be either an integer or a decimal number.
    
    :param value: The value that contains a number.
    :param int_only: A flag to only extract the integer portion of the number.
    
    :return A string representation of the numeric value.  This will be empty if no number was
    found in the value.
    """
    
    if (not int_only):
        num = re.search ("(\d+(\.\d+)?)", value)
    else:
        num = re.search ("(\d+)", value)
        
    if (num):
        return num.group (1)
    
    return ""