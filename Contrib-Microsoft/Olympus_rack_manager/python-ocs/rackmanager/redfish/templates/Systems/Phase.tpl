{
    "@odata.type": "#Power.v1_1_0.Power",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/System/{{ID}}/Power/Phase{{Phase}}/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power/Phase{{Phase}}",
    "Id": "PowerPhase{{Phase}}",
    "Name": "System Power Phase {{Phase}}",
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power/Phase{{Phase}}#/PowerSupplies/1",
            "MemberId": "1",
            "Name": "Power Supply Phase",
            "Status": {
                "State": "Enabled"
                %if defined ("Health"):
                    ,"Health": "{{Health}}"
                %end
                %if defined ("Faults"):
                    ,"Oem": {
                        "Microsoft": {
                            "@odata.type": "#OcsPower.v1_0_0.Status",
                            "Faults": "{{Faults}}"
                        }
                    }
                %end
            },
            %if defined ("Vin"):
                "LineInputVoltage": {{Vin}},
            %end
            "PowerCapacityWatts": 300,
            "Oem": {
                "Microsoft": {
                    "@odata.type": "#OcsPower.v1_0_0.PowerSupply",
                    %if defined ("Pin"):
                        "PowerInputWatts": {{Pin}},
                    %end
                    "Actions": {
                        "#PowerSupply.ClearFaults": {
                            "target":  "/redfish/v1/Chassis/System/{{ID}}/Power/Phase{{Phase}}/Actions/PowerSupply.ClearFaults"
                        }
                    }
                }
            }
        }
    ]
}
