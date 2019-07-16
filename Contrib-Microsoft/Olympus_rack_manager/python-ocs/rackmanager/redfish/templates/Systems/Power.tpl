<%
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("PowerReadingWatts", "0")
        setdefault ("SamplingPeriodSeconds", "0")
        setdefault ("MinPowerReadingWatts", "0")
        setdefault ("MaxPowerReadingWatts", "0")
        setdefault ("AvgPowerReadingWatts", "0")
        setdefault ("StaticLimit", "0")
        setdefault ("StaticState", "")
        setdefault ("PowerLimit", "0")
        setdefault ("LimitDelay", "0")
        setdefault ("ThrottleDuration", "false")
        setdefault ("AlertAction", "")
        setdefault ("Alert_Enabled", "false")
        setdefault ("AutoProchot", "false")
        setdefault ("BladeProchot", "false")
        setdefault ("Model", "")
        setdefault ("Manufacturer", "")
        setdefault ("FW_Revision", "0")
        setdefault ("Serial", "")
        setdefault ("Health", "")
        setdefault ("Faults", "")
        setdefault ("Vin", "0")
        setdefault ("Pout", "0")
        setdefault ("Pin", "0")
        setdefault ("PSU_Feed", "")
        setdefault ("Bootloader_FW_Revision", "")
        setdefault ("Battery_Status", "")
        setdefault ("Balancing", "false")
        setdefault ("External_Power", "false")
        setdefault ("Pre_charge_Circuit", "false")
        setdefault ("Discharge", "false")
        setdefault ("Charge", "false")
        setdefault ("Charging", "false")
        setdefault ("Discharging", "false")
        setdefault ("Initialized", "false")
    end
%>
{
    "@odata.type": "#Power.v1_1_0.Power",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/System/{{ID}}/Power/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power",
    "Id": "Power",
    "Name": "System Power",
    "PowerControl": [
        {
            "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power#/PowerControl/1",
            "MemberId": "1",
            "Name": "System Power Control",
            %if defined ("PowerReadingWatts"):
            	"PowerConsumedWatts": {{PowerReadingWatts}},
            %end
            "PowerCapacityWatts": 900,
            "PowerMetrics": {
                %sepr = ""
		        %if defined ("SamplingPeriodSeconds"):
		        	"IntervalInMin": {{SamplingPeriodSeconds}}
		        	%sepr = ","
		        %end
		        %if defined ("MinPowerReadingWatts"):
		        	{{sepr}}"MinConsumedWatts": {{MinPowerReadingWatts}}
		        	%sepr = ","
		        %end
		        %if defined ("MaxPowerReadingWatts"):
		        	{{sepr}}"MaxConsumedWatts": {{MaxPowerReadingWatts}}
		        	%sepr = ","
		        %end
		        %if defined ("AvgPowerReadingWatts"):
		        	{{sepr}}"AverageConsumedWatts": {{AvgPowerReadingWatts}}
		        %end
            },
            %if defined ("StaticLimit"):
                "PowerLimit": {
                    "LimitInWatts": {{StaticLimit}}
                },
            %end
            %if defined ("StaticState"):
                "Status": {
                    "State": "{{StaticState}}"
                },
            %end
            "Oem": {
                "Microsoft": {
                    "@odata.type": "#OcsPower.v1_0_0.PowerLimit",
                    %if defined ("PowerLimit"):
		            	"DefaultLimitInWatts": {{PowerLimit}},
		            %end
		            %if defined ("LimitDelay"):
		            	"AutoRemoveDelayInSec": {{LimitDelay}},
		            %end
		            %if defined ("ThrottleDuration"):
		            	"FastThrottleDurationInMs": {{ThrottleDuration}},
		            %end
		            %if defined ("AlertAction"):
		            	"AlertAction": "{{AlertAction}}",
		            %end
		            %if defined ("AutoProchot"):
                        "RackThrottleEnabled": {{AutoProchot}},
                    %end
		            %if defined ("Alert_Enabled"):
		            	"AlertActive": {{Alert_Enabled}},
		            %end
		            %if defined ("BladeProchot"):
                        "BmcForceThrottleActive": {{BladeProchot}},
                    %end
                    "Actions": {
                        "#PowerLimit.RearmTrigger": {
                            "target":  "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerLimit.RearmTrigger",
                            "RearmType@Redfish.AllowableValues": [
                                "DeactivatePowerLimit",
                                "RearmOnly"
                            ]
                        },
                        "#PowerLimit.Activate": {
                            "target": "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerLimit.Activate"
                        },
                        "#PowerLimit.Dectivate": {
                            "target": "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerLimit.Deactivate"
                        }
                    } 
                }
            }
        }
    ],
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power#/PowerSupplies/1",
            "MemberId": "1",
            "Name": "OCS Power Supply",
            %if defined ("Model"):
                "Model": "{{Model}}",
            %end
            %if defined ("Manufacturer"):
                "Manufacturer": "{{Manufacturer}}",
            %end
            %if defined ("FW_Revision"):
                "FirmwareVersion": "{{FW_Revision}}",
            %end
            %if defined ("Serial"):
                "SerialNumber": "{{Serial}}",
            %end
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
            "PowerCapacityWatts": 900,
            %if defined ("Pout"):
                "LastPowerOutputWatts": {{Pout}},
            %end
            "Oem": {
                "Microsoft": {
                    "@odata.type": "#OcsPower.v1_0_0.PowerSupply",
                    %if defined ("Pin"):
                        "PowerInputWatts": {{Pin}},
                    %end
                    %if defined ("PSU_Feed"):
                        "PsuFeed": "{{PSU_Feed}}",
                    %end
                    %if defined ("Bootloader_FW_Revision"):
                        "BootloaderVersion": "{{Bootloader_FW_Revision}}",
                    %end
                    %if defined ("Battery_Status"):
                        "Battery": {
                            %sepr = ""
                            %if defined ("Balancing"):
                                "Balancing": {{Balancing}}
                                %sepr = ","
                            %end
                            %if defined ("External_Power"):
                                {{sepr}}"ExternalPower": {{External_Power}}
                                %sepr = ","
                            %end
                            %if defined ("Pre_charge_Circuit"):
                                {{sepr}}"PreChargeActive": {{Pre_charge_Circuit}}
                                %sepr = ","
                            %end
                            %if defined ("Discharge"):
                                {{sepr}}"DischargeAllowed": {{Discharge}}
                                %sepr = ","
                            %end
                            %if defined ("Charge"):
                                {{sepr}}"ChargeAllowed": {{Charge}}
                                %sepr = ","
                            %end
                            %if defined ("Charging"):
                                {{sepr}}"Charging": {{Charging}}
                                %sepr = ","
                            %end
                            %if defined ("Discharging"):
                                {{sepr}}"Discharging": {{Discharging}}
                                %sepr = ","
                            %end
                            %if defined ("Initialized"):
                                {{sepr}}"Initialized": {{Initialized}}
                            %end
                        },
                    %end
                    "Actions": {
                        "#PowerSupply.ClearFaults": {
                            "target":  "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerSupply.ClearFaults"
                        },
                        "#PowerSupply.FirmwareUpdate": {
                            "target": "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerSupply.FirmwareUpdate",
                            "FWRegion@Redfish.AllowableValues": [
                                "A",
                                "B",
                                "Bootloader"
                            ]
                        },
                        "#PowerSupply.FirmwareUpdateState": {
                            "target": "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerSupply.FirmwareUpdateState",
                            "Operation@Redfish.AllowableValues": [
                                "Abort",
                                "Query"
                            ]
                        }
                        %if defined ("Battery_Status"):
                            ,"#PowerSupply.BatteryTest": {
                                "target": "/redfish/v1/Chassis/System/{{ID}}/Power/Actions/PowerSupply.BatteryTest"
                            }
                        %end
                    }
                }
            },
            "RelatedItem": [
                {
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power/Phase1"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power/Phase2"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power/Phase3"
                }
            ]
        }
    ]
}
