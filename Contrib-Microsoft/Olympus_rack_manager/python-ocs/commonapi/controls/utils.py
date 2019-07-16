# Copyright (C) Microsoft Corporation. All rights reserved.

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

#!/usr/bin/python
# -*- coding: utf-8 -*-

class completion_code:
    cc_key = "Completion Code"
    success = "Success"
    failure = "Failure"
    fwdecompress = "FirmwareDecompress"
    deviceoff = "PowerOff"
    notpresent = "DeviceNotPresent"
    desc = "Status Description"
    ipmi_code = "IPMI Completion Code"
    state_desc = "Description"
    err_code = "ErrorCode"
    
'''class sensor_entity:
     Unspecified = 0                            Other = 1                     
     Unknown  = 2                               Processor = 3                        
     Disk or Disk Bay = 4                       5  Peripheral Bay                  
     6  System Management Module               7  System Board                    
     8  Memory Module                          9  Processor Module                
    10  Power Supply                          11  Add-in Card                     
    12  Front Panel Board                     13  Back Panel Board                
    14  Power System Board                    15  Drive Backplane                 
    16  System Internal Expansion Board       17  Other System Board              
    18  Processor Board                       19  Power Unit                      
    20  Power Module                          21  Power Management                
    22  Chassis Back Panel Board              23  System Chassis                  
    24  Sub-Chassis                           25  Other Chassis Board             
    26  Disk Drive Bay                        27  Peripheral Bay                  
    28  Device Bay                            29  Fan Device                      
    30  Cooling Unit                          31  Cable/Interconnect              
    32  Memory Device                         33  System Management Software      
    34  BIOS                                  35  Operating System                
    36  System Bus                            37  Group                           
    38  Remote Management Device              39  External Environment            
    40  Battery                               41  Processing Blade                
    42  Connectivity Switch                   43  Processor/Memory Module         
    44  I/O Module                            45  Processor/IO Module             
    46  Management Controller Firmware        47  IPMI Channel                    
    48  PCI Bus                               49  PCI Express Bus                 
    50  SCSI Bus (parallel)                   51  SATA/SAS Bus                    
    52  Processor/Front-Side Bus              53  Real Time Clock(RTC)            
    54  Reserved                              55  Air Inlet                       
    56  Reserved                              57  Reserved                        
    58  Reserved                              59  Reserved                        
    60  Reserved                              61  Reserved                        
    62  Reserved                              63  Reserved                        
    64  Air Inlet                             65  Processor                       
    66  Baseboard/Main System Board          160  PICMG Front Board               
   192  PICMG Rear Transition Module         193  PICMG AdvancedMC Module         
   240  PICMG Shelf Management Controller     241  PICMG Filtration Unit           
   242  PICMG Shelf FRU Information          243  PICMG Alarm Panel      '''
    
def set_failure_dict(error_msg, cc_code = completion_code.failure):
    failure = {}

    failure[completion_code.cc_key] = cc_code
    failure[completion_code.desc] = error_msg
    
    return failure 

def set_success_dict(values = {}):
    values[completion_code.cc_key] = completion_code.success
    
    return values

def check_success(values = {}):
    if completion_code.cc_key in values:
        if values[completion_code.cc_key] == completion_code.success:
            return True
    
    return False

def parse_args_retain_case(parser, args):
    """ Lowercase strings in args, parse arguments then restore case
    """
    args_lower = [string.lower() for string in args]
    
    command_args = parser.parse_args(args_lower)
    
    for string in args:
        if string.lower() in vars(command_args).values():
            i = vars(command_args).values().index(string.lower())
            key = vars(command_args).keys()[i]
            
            if key == "command":
                continue
            
            vars(command_args)[key] = string
            
    return command_args
