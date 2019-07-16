{
    "@odata.type": "#OcsPower.v1_0_0.PowerPorts",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/RMM/PowerControl/$entity",
    "@odata.id": "/redfish/v1/Chassis/RMM/PowerControl",
    "Id": "PowerControl",
    "Name": "Row Power Control"
    %if defined ("rack_ports"):
        ,"RackManagers": [
            %sep = ""
            %for i, rack in enumerate (rack_ports):
                %port_idx = i + 1
                {{sep}}{
                    "@odata.id": "/redfish/v1/Chassis/RMM/PowerControl/RackManager/{{port_idx}}",
                    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
                    "Id": "PowerPort{{port_idx}}",
                    "Name": "Power Port {{port_idx}}",
                    "PowerPortType": "RackManager"
                    %if ("Port_Presence" in rack):
                        ,"Presence": {{rack["Port_Presence"]}}
                    %end
                    %if ("Port_State" in rack):
                        ,"PowerState": "{{rack["Port_State"]}}"
                    %end
                    %if ("Boot_Strap" in rack):
                        ,"BootStrapping": "{{rack["Boot_Strap"]}}"
                    %end
                }
                %sep = ","
            %end
        ]
    %end
}