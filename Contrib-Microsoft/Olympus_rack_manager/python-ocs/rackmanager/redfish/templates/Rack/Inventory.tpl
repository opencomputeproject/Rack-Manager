{
    "@odata.type": "#Ocs.v1_0_0.Inventory",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/Rack/Inventory/$entity",
    "@odata.id": "/redfish/v1/Chassis/Rack/Inventory",
    "Id": "Inventory"
    %if defined ("list"):
        ,"Contents": [
            %sepr = ""
            %for item in list:
                {{sepr}}{
                    "SlotId": "{{item.get ("Slot_Id", "--")}}",
                    %if "Port_State" in item:
                        "PortState": "{{item["Port_State"]}}",
                    %end
                    %if "Port_Present" in item:
                        "PortPresent": {{item["Port_Present"]}},
                    %end
                    "SwitchPort": {{item["BMC_SW_Port"]}},
                    "MAC1": "{{item.get ("MAC", "--")}}",
                    "GUID": "{{item.get ("GUID", "--")}}"
                }
                %sepr = ","
            %end
        ]
    %end
}