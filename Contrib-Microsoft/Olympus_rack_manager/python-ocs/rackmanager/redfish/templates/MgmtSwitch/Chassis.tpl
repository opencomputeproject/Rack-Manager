{
    "@odata.type": "#Chassis.v1_2_0.Chassis",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch",
    "Id": "MgmtSwitch",
    %if defined ("Name"):
        "Name": "{{Name}}",
    %end
    %if defined ("Description"):
        "Description": "{{Description}}",
    %end
    "ChassisType": "RackMount",
    "Manufacturer": "Microsoft",
    %if defined ("SerialNumber"):
        "SerialNumber": "{{SerialNumber}}",
    %end
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Thermal"
    },
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Power"
    },
    "Oem": {
        "Microsoft": {
            "@odata.type": "#OcsMgmtSwitch.v1_0_0.MgmtSwitch",
            %if defined ("MACAddress"):
		        "MACAddress": "{{MACAddress}}",
		    %end
		    %if defined ("HWVersion"):
		        "HardwareVersion": "{{HWVersion}}",
		    %end
		    %if defined ("FWVersion"):
		        "FirmwareVersion": "{{FWVersion}}",
		    %end
		    %if defined ("FWDate"):
		        "FirmwareDate": "{{FWDate}}",
		    %end
		    %if defined ("Uptime"):
		        "UpTime": {{Uptime}},
		    %end
		    "Ports" : [
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/1"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/2"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/3"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/4"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/5"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/6"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/7"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/8"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/9"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/10"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/11"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/12"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/13"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/14"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/15"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/16"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/17"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/18"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/19"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/20"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/21"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/22"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/23"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/24"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/25"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/26"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/27"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/28"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/29"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/30"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/31"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/32"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/33"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/34"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/35"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/36"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/37"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/38"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/39"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/40"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/41"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/42"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/43"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/44"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/45"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/46"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/47"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/MgmtSwitch/Port/48"
                }
            ]
        }
    },
    "Links": {
        "ContainedBy": {
            "@odata.id": "/redfish/v1/Chassis/Rack"
        }
    },
    "Actions": {
        "#Chassis.Reset": {
            "target": "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Reset",
            "ResetType@Redfish.AllowableValues": [
                "ForceRestart"
            ]
        },
        "Oem": {
            "OcsMgmtSwitch.v1_0_0#Chassis.Configure": {
                "target": "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.Configure"
            },
            "OcsMgmtSwitch.v1_0_0#Chassis.FirmwareUpdate": {
                "target": "/redfish/v1/Chassis/MgmtSwitch/Actions/Chassis.FirmwareUpdate"
            }
        }
    }
}
