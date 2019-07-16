{
    "@odata.type": "#OcsPower.v1_0_0.PowerPorts",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/PMDU/PowerControl/$entity",
    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerControl",
    "Id": "PowerControl",
    "Name": "Rack Power Control"
    %if defined ("pdu_ports"):
        ,"PDU": [
            %sep = ""
            %for i, pdu in enumerate (pdu_ports):
                %port_idx = i + 1
                {{sep}}{
                    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerControl/PDU/{{port_idx}}",
                    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
                    "Id": "PowerPort{{port_idx}}",
                    "Name": "Power Port {{port_idx}}",
                    "PowerPortType": "PDU"
                    %if ("Port_Presence" in pdu):
                        ,"Presence": {{pdu["Port_Presence"]}}
                    %end
                    %if ("Port_State" in pdu):
                        ,"PowerState": "{{pdu["Port_State"]}}"
                    %end
                }
                %sep = ","
            %end
        ]
    %end
    %if defined ("relay_ports"):
        ,"Relays": [
            %sep = ""
            %for i, relay in enumerate (relay_ports):
                % port_idx = i + 1
                {{sep}}{
                    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerControl/Relay/{{port_idx}}",
                    "@odata.type": "#OcsPower.v1_0_0.PowerPort",
                    "Id": "PowerRelay{{port_idx}}",
                    "Name": "Power Relay {{port_idx}}",
                    "PowerPortType": "Relay"
                    %if ("Relay" in relay):
                        ,"PowerState": "{{relay["Relay"]}}"
                    %end
                }
                %sep = ","
            %end
        ]
    %end
}
