<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#Power.v1_1_0.Power",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/{{config}}Manager/Power/$entity",
    "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Power",
    "Id": "Power",
    "Name": "{{config}} Manager Power",
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Power#/PowerSupplies/1",
            "MemberId": "1",
            "Name": "HSC",
            %if defined ("InputVoltage"):
                "LineInputVoltage": {{InputVoltage}},
            %end
            %if defined ("PowerInWatts"):
                "LastPowerOutputWatts": {{PowerInWatts}},
            %end
            "Status": {
                "State": "Enabled",
                %if defined ("Health"):
                    "Health": "{{Health}}",
                %end
                "Oem": {
                    "Microsoft": {
                        "@odata.type": "#OcsPower.v1_0_0.Status"
                        %if defined ("PSU_A_Status"):
                            ,"PsuA": "{{PSU_A_Status}}"
                        %end
                        %if defined ("PSU_B_Status"):
                            ,"PsuB": "{{PSU_B_Status}}"
                        %end
                        %if defined ("HSC_Status"):
                            ,"Faults": "{{HSC_Status}}"
                        %end
                    }
                }
            }
        }
    ],
    "Oem": {
        "Microsoft": {
            "@odata.type": "OcsPower.v1_0_0.PowerSupply",
            "Actions": {
                "#PowerSupply.ClearFaults": {
                    "target":  "/redfish/v1/Chassis/{{config}}Manager/Power/Actions/PowerSupply.ClearFaults"
                }
            }
        }
    }
}
