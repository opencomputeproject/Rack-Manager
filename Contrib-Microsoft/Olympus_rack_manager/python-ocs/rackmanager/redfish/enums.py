# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

from controls.blade_fw_update import blade_fw_operation_enum, blade_fw_type_enum

bool_map = {
        "Enabled" : True,
        "Disabled" : False,
        "True" : True,
        "False" : False,
        "On" : True,
        "Off" : False,
        "1" : True,
        "0" : False,
        "Active" : True,
        "Not Active" : False,
        "Present" : True,
        "Not Present" : False,
        "Allowed" : True,
        "Not Allowed" : False,
        "Yes" : True,
        "No" : False,
        "Up" : True,
        "Down" : False
    }

def convert_to_bool (value):
    """
    Convert a value to an appropriate boolean.
    
    :param value: The value to convert to a boolean.
    
    :return True or False.
    """
    
    return bool_map[value.strip ()]

class Boolean:
    """
    Define the enumeration for Boolean JSON values.
    
    Valid values are:
        true
        false
    """
    
    values = ["true", "false"]
    
    def __init__ (self, value, convert = False):
        """
        Create a Boolean enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
            
        if ((not isinstance (value, bool)) and (value not in Boolean.values)):
            if (not convert):
                raise ValueError ("{0} is not valid for Boolean.".format (value))
            
            try:
                value = convert_to_bool (value)
            except:
                raise ValueError ("Unknown Boolean conversion for {0}.".format (value))
        
        if (isinstance (value, bool)):
            value = "true" if value else "false"
               
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return 1 if (self.value == "true") else 0
    
class IndicatorLED ():
    """
    Define the enumeration for the IndicatorLED property.
    
    Valid values are:
        On
        Off
        Unknown
    """
    
    values = {
        "Lit": 1,
        "Off": 0,
        "Unknown": -1
    }
    
    def __init__ (self, value, convert = False):
        """
        Create an IndicatorLED enumeration instance.
        
        :param value: The value to assign to the enumeration.  This can either be an integer or a
        string.  If the value is not valid, an exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value. If no conversion is possible, an
        exception will be raised.
        """
        
        if (value is int):
            self.value = None
            for val, code in IndicatorLED.values.items ():
                if (code == value):
                    self.value = val
                    break
            
            if not self.value:
                raise ValueError ("{0} is not valid for IndicatorLED.".format (value))
        else:
            if (value not in IndicatorLED.values):
                if (not convert):
                    raise ValueError ("{0} is not valid for IndicatorLED.".format (value))
                
                if ("ON" == value.upper ()):
                    value = "Lit"
                elif ("OFF" == value.upper()):
                    value = "Off"
                else:
                    value = "Unknown"
                    
            self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return IndicatorLED.values[self.value]
    
class Health ():
    """
    Define the enumeration for the Health property.
    
    Valid values are:
        OK
        Warning
        Critical
    """
    
    values = ["OK", "Warning", "Critical"]
    
    def __init__ (self, value, convert = False):
        """
        Create a Health enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        value = str (value)
        
        if (value not in Health.values):
            if (not convert):
                raise ValueError ("{0} is not valid for Health.".format (value))
            
            check = value.strip ().upper ()
            if (check in {"HEALTHY", "NORMAL", "OK", "INFO"}):
                value = "OK"
            elif (check in {"FAULTY", "OVERTHRESHOLD", "WARNING", "SHUTDOWN", "NC"}):
                value = "Warning"
            elif (check in {"OVERCRITICAL", "CRITICAL", "NOTPRESENT", "NOTFUNCTIONING",
                "NOTAVAILABLE", "NOPOWER", "UNAVAILABLE", "NA", "CR", "NR", "ERROR"}):
                value = "Critical"
            else:
                raise ValueError ("Unknown Health conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class ResetType ():
    """
    Define the enumeration for the ResetType parameter.
    
    Valid values are:
        On
        GracefulShutdown
        GracefulRestart
        ForceRestart
        ForceOff
    """
    
    ON = "On"
    GRACEFUL_SHUTDOWN = "GracefulShutdown"
    GRACEFUL_RESTART = "GracefulRestart"
    FORCE_RESTART = "ForceRestart"
    FORCE_OFF = "ForceOff"
    
    values = [ON, GRACEFUL_SHUTDOWN, GRACEFUL_RESTART, FORCE_RESTART, FORCE_OFF]
    
    def __init__ (self, value, convert = False, valid = values):
        """
        Create a ResetType enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        :param valid: Override for the set of valid values for situations when only a subset of the
        valid enumeration values are acceptable.
        """
        
        if (value not in valid):
            if (not convert):
                raise ValueError ("{0} is not valid for ResetType.".format (value))
            
            raise ValueError ("Unknown ResetType conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class RoleId ():
    """
    Define the enumeration for the RoleId parameter.
    
    Valid values are:
        admin
        operator
        user
    """
    
    values = ["admin", "operator", "user"]
    
    def __init__ (self, value, convert = False):
        """
        Create a RoleId enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.  This can be a string of either the group name or ID, or an
        integer of the group ID.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in RoleId.values):
            if (not convert):
                raise ValueError ("{0} is not valid for RoleId.".format (value))

            raise ValueError ("Unknown RoleId conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class ServiceStatus:
    """
    Define the enumeration for the ServiceStatus property for Rack Manager services.
    
    Valid values are:
        Start
        Stop
        Restart
    """
    
    values = ["Start", "Stop", "Restart"]
    
    def __init__ (self, value, convert = False):
        """
        Create a ServiceStatus enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in ServiceStatus.values):
            if (not convert):
                raise ValueError ("{0} is not valid for ServiceStatus.".format (value))

            if (value.upper () in {"ENABLED", "RUNNING"}):
                value = "Start"
            elif (value.upper () in {"DISABLED", "STOPPED"}):
                value = "Stop"
            else:
                raise ValueError ("Unknown ServiceStatus conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class State:
    """
    Define the enumeration for the State property.
    
    Valid values are:
        Enabled
        Disabled
        StandbyOffline
        StandbySpare
        InTest
        Starting
        Absent
        UnavailableOffline
    """
    
    values = ["Enabled", "Disabled", "StandbyOffline", "StandbySpare", "InTest", "Starting",
        "Absent", "UnavailableOffline"]
    
    def __init__ (self, value, convert = False):
        """
        Create a State enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in State.values):
            if (not convert):
                raise ValueError ("{0} is not valid for State.".format (value))

            if (value.upper () in {"UP", "ON", "PRESENT", "ENABLED", "OK", "POWER LIMIT ACTIVE"}):
                value = "Enabled"
            elif (value.upper () in {"DOWN", "OFF", "NO ACTIVE POWER LIMIT"}):
                value = "Disabled"
            elif (value.upper() in {"NA", "UNAVAILABLE"}):
                value = ""
            else:
                raise ValueError ("Unknown State conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class AddressOrigin:
    """
    Define the enumeration for the AddressOrgin property.
    
    Valid values are:
        DHCP,
        Static
    """
    
    DHCP = "DHCP"
    STATIC = "Static"
    
    values = [DHCP, STATIC]
    
    def __init__ (self, value, convert = False):
        """
        Create a AddressOrigin enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in AddressOrigin.values):
            if (not convert):
                raise ValueError ("{0} is not valid for AddressOrigin.".format (value))

            if ("DHCP" in value):
                value = AddressOrigin.DHCP
            else:
                raise ValueError ("Unknown AddressOrigin conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __eq__ (self, other):
        if isinstance (other, AddressOrigin):
            return self.value == other.value
        elif isinstance (other, basestring):
            return self.value == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class PowerState:
    """
    Define the enumeration for the PowerState property.
    
    Valid values are:
        On
        Off
    """
    
    values = ["On", "Off"]
    
    def __init__ (self, value, convert = False, to_lower = False):
        """
        Create a PowerState enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        :param to_lower: A flag indicating if the string representation should be in lower case
        letters.
        """
        
        if (value not in PowerState.values):
            if (not convert):
                raise ValueError ("{0} is not valid for PowerState.".format (value))

            if ("ON" == value.upper ()):
                value = "On"
            elif ("OFF" == value.upper ()):
                value = "Off"
            else:
                raise ValueError ("Unknown PowerState conversion for {0}.".format (value))
                
        self.value = value
        self.to_lower = to_lower
        
    def __str__ (self):
        if (not self.to_lower):
            return self.value
        else:
            return self.value.lower ()
    
    def __repr__ (self):
        return self.__str__ ()

class BootSourceOverrideEnabled:
    """
    Define the enumeration for the BootSourceOverrideEnabled property.
    
    Valid values are:
        Disabled
        Once
        Continuous
    """
    
    DISABLED = "Disabled"
    ONCE = "Once"
    CONTINUOUS = "Continuous"
    
    values = [DISABLED, ONCE, CONTINUOUS]
    
    def __init__ (self, value, convert = False):
        """
        Create a BootSourceOverrideEnabled enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in BootSourceOverrideEnabled.values):
            if (not convert):
                raise ValueError ("{0} is not valid for BootSourceOverrideEnabled.".format (value))

            if ("True" == value):
                value = BootSourceOverrideEnabled.ONCE
            elif ("False" == value):
                value = BootSourceOverrideEnabled.DISABLED
            elif ("Persistent" == value):
                value = BootSourceOverrideEnabled.CONTINUOUS
            else:
                raise ValueError (
                    "Unknown BootSourceOverrideEnabled conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
        
class BootSourceOverrideTarget:
    """
    Define the enumeration for the BootSourceOverrideTarget property.
    
    Valid values are:
        None
        Pxe
        Floppy
        Hdd
        BiosSetup
    """
    
    NONE = "None"
    PXE = "Pxe"
    FLOPPY = "Floppy"
    HDD = "Hdd"
    BIOS_SETUP = "BiosSetup"
    
    values = {
        NONE : "none",
        PXE : "pxe",
        FLOPPY : "floppy",
        HDD : "disk",
        BIOS_SETUP : "bios"
    }
    
    def __init__ (self, value, convert = False, cmd_arg = False):
        """
        Create a BootSourceOverrideTarget enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        :param cmd_arg: A flag indicating the command argument mapping should be returned as the
        string representation of the enumeration.
        """
        
        if (value not in BootSourceOverrideTarget.values):
            if (not convert):
                raise ValueError ("{0} is not valid for BootSourceOverrideTarget.".format (value))

            if ("PXE" in value):
                value = BootSourceOverrideTarget.PXE
            elif ("Hard-Drive" in value):
                value = BootSourceOverrideTarget.HDD
            elif ("BIOS" in value):
                value = BootSourceOverrideTarget.BIOS_SETUP
            elif ("Floppy" in value):
                value = BootSourceOverrideTarget.FLOPPY
            elif ("No override" in value):
                value = BootSourceOverrideTarget.NONE
            else:
                raise ValueError (
                    "Unknown BootSourceOverrideTarget conversion for {0}.".format (value))
                
        self.value = value
        self.cmd_arg = cmd_arg
        
    def __str__ (self):
        if (not self.cmd_arg):
            return self.value
        else:
            return BootSourceOverrideTarget.values[self.value]
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __eq__ (self, other):
        if isinstance (other, BootSourceOverrideTarget):
            return self.value == other.value
        elif isinstance (other, basestring):
            return self.value == other
        return NotImplemented
    
    def __ne__ (self, other):
        result = self.__eq__ (other)
        if result is NotImplemented:
            return result
        return not result
    
class BootSourceOverrideMode:
    """
    Define the enumeration for the BootSourceOverrideMode property.
    
    Valid values are:
        Legacy
        UEFI
    """
    
    values = {
        "Legacy" : 0,
        "UEFI" : 1
    }
    
    def __init__ (self, value, convert = False):
        """
        Create a BootSourceOverrideMode enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in BootSourceOverrideMode.values):
            if (not convert):
                raise ValueError ("{0} is not valid for BootSourceOverrideMode.".format (value))
            
            raise ValueError (
                "Unknown BootSourceOverrideMode conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return BootSourceOverrideMode.values[self.value]
    
class BypassMode:
    """
    Define the enumeration for the BypassMode property.
    
    Valid values are:
        Enabled
        Disabled
    """
    
    values = ["Enabled", "Disabled"]
    
    def __init__ (self, value, convert = False):
        """
        Create a BypassMode enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in BypassMode.values):
            if (not convert):
                raise ValueError ("{0} is not valid for BypassMode.".format (value))

            if ("On" == value):
                value = "Enabled"
            elif ("Off" == value):
                value = "Disabled"
            else:
                raise ValueError ("Unknown BypassMode conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class UserLogic:
    """
    Define the enumeration for the UserLogic property.
    
    Valid values are:
        Enabled
        Disabled
    """
    
    values = ["Enabled", "Disabled"]
    
    def __init__ (self, value, convert = False):
        """
        Create a UserLogic enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in UserLogic.values):
            if (not convert):
                raise ValueError ("{0} is not valid for UserLogic.".format (value))

            raise ValueError ("Unknown UserLogic conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class LinkState:
    """
    Define the enumeration for the LinkState property.
    
    Valid values are:
        Up
        Down
    """
    
    values = ["Up", "Down"]
    
    def __init__ (self, value, convert = False):
        """
        Create a LinkState enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in LinkState.values):
            if (not convert):
                raise ValueError ("{0} is not valid for LinkState.".format (value))

            if (value == "1"):
                value = "Up"
            elif (value == "0"):
                value = "Down"
            else:
                raise ValueError ("Unknown LinkState conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
class AlertAction:
    """
    Define the enumeration for the AlertAction property.
    
    Valid values are:
        NoAction
        ThrottleAndLimit
        PowerLimitOnly
    """
    
    values = {
        "NoAction" : 0,
        "ThrottleAndLimit" : 1,
        "PowerLimitOnly" : 2
    }
    
    def __init__ (self, value, convert = False):
        """
        Create a AlertAction enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in AlertAction.values):
            if (not convert):
                raise ValueError ("{0} is not valid for AlertAction.".format (value))

            raise ValueError ("Unknown AlertAction conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return AlertAction.values[self.value]
    
class RearmType:
    """
    Define the enumeration for the RearmType property.
    
    Valid values are:
        DeactivatePowerLimit
        RearmOnly
    """
    
    values = {
        "DeactivatePowerLimit" : 1,
        "RearmOnly" : 2
    }
    
    def __init__ (self, value, convert = False):
        """
        Create a RearmType enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in RearmType.values):
            if (not convert):
                raise ValueError ("{0} is not valid for RearmType.".format (value))

            raise ValueError ("Unknown RearmType conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return RearmType.values[self.value]

class FWRegion:
    """
    Define the enumeration for the FWRegion property.
    
    Valid values are:
        A
        B
        Bootloader
    """
    
    values = {
        "A" : blade_fw_type_enum.IMAGE_A,
        "B" : blade_fw_type_enum.IMAGE_B,
        "Bootloader" : blade_fw_type_enum.BOOTLOADER
    }
    
    def __init__ (self, value, convert = False):
        """
        Create a FWRegion enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in FWRegion.values):
            if (not convert):
                raise ValueError ("{0} is not valid for FWRegion.".format (value))

            raise ValueError ("Unknown FWRegion conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return int (FWRegion.values[self.value])
    
class Operation:
    """
    Define the enumeration for the Operation property.
    
    Valid values are:
        Abort
        Query
    """
    
    values = {
        "Abort" : blade_fw_operation_enum.ABORT,
        "Query" : blade_fw_operation_enum.QUERY
    }
    
    def __init__ (self, value, convert = False):
        """
        Create a Operation enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in Operation.values):
            if (not convert):
                raise ValueError ("{0} is not valid for Operation.".format (value))

            raise ValueError ("Unknown Operation conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
    
    def __int__ (self):
        return int (Operation.values[self.value])
    
class BootStrapping:
    """
    Define the enumeration for the BootStrapping property.
    
    Valid values are:
        Normal
        Network
    """
    
    values = ["Normal", "Network"]
    
    def __init__ (self, value, convert = False):
        """
        Create a BootStrapping enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
        
        if (value not in BootStrapping.values):
            if (not convert):
                raise ValueError ("{0} is not valid for BootStrapping.".format (value))

            if ("ON" == value.upper ()):
                value = "Network"
            elif ("OFF" == value.upper ()):
                value = "Normal"
            else:
                raise ValueError ("Unknown BootStrapping conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
        
class Target:
    """
    Define the enumeration for the TftpPut Target property.
    
    Valid values are:
        AuditLog
        DebugLog
        TelemetryLog
        RestLog
        FirmwareUpdateLog
        SystemLog
        KernelLog
    """
    
    values = ["AuditLog", "DebugLog", "TelemetryLog", "RestLog", "FirmwareUpdateLog", "SystemLog", "KernelLog"]
    
    def __init__ (self, value, convert = False):
        """
        Create a Target enumeration instance.
        
        :param value: The value to assign to the enumeration.  If the value is not valid, an
        exception will be raised.
        :param convert: A flag indicating if conversion to a valid enumeration value should be
        performed when given an invalid enumeration value.  If no conversion is possible, an
        exception will be raised.
        """
                
        if (value not in Target.values):
            if (not convert):
                raise ValueError ("{0} is not valid for Target.".format (value))

            raise ValueError ("Unknown TftpPut Targets conversion for {0}.".format (value))
                
        self.value = value
        
    def __str__ (self):
        return self.value
    
    def __repr__ (self):
        return self.__str__ ()
     
