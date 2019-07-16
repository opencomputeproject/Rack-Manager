{
    "@odata.type": "#Chassis.v1_2_0.Chassis",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
    "@odata.id": "/redfish/v1/Chassis/Rack",
    "Id": "Rack",
    %if defined ("Product_Name"):
        "Name": "{{Product_Name}}",
    %end
    "ChassisType": "Rack",
    %if defined("Product_Manufacturer"):
	    "Manufacturer": "{{Product_Manufacturer}}",	
    %end
    %if defined("Product_Version"):
	    "Model": "{{Product_Version}}",	
    %end
    %if defined("Product_Serial"):
	    "SerialNumber": "{{Product_Serial}}",	
    %end
    %if defined("Product_Assettag"):
	    "AssetTag": "{{Product_Assettag}}",	
    %end
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.Chassis",
            "FRU": {
                %sepr = ""
                %if defined ("Product_Fru_Id"):
                    "FruId": "{{Product_Fru_Id}}"
                    %sepr = ","
                %end
                %if defined ("Product_Subproduct"):
                    {{sepr}}"Subproduct": "{{Product_Subproduct}}"
                    %sepr = ","
                %end
                %if defined ("Product_Build"):
                    {{sepr}}"Build": "{{Product_Build}}"
                %end
            },
            "Inventory": {
                "@odata.id": "/redfish/v1/Chassis/Rack/Inventory"
            }
        }
    },
    "Links": {
        "Contains": [
            {
                "@odata.id": "/redfish/v1/Chassis/PMDU"
            },
            {
                "@odata.id": "/redfish/v1/Chassis/RackManager"
            },
            {
                "@odata.id": "/redfish/v1/Chassis/MgmtSwitch"
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/1"
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/2"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/3"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/4"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/5"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/6"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/7"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/8"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/9"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/10"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/11"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/12"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/13"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/14"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/15"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/16"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/17"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/18"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/19"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/20"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/21"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/22"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/23"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/24"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/25"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/26"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/27"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/28"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/29"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/30"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/31"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/32"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/33"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/34"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/35"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/36"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/37"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/38"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/39"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/40"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/41"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/42"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/43"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/44"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/45"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/46"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/47"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/48"       
            }
        ],
        "PoweredBy": [
            {
                "@odata.id": "/redfish/v1/Chassis/PMDU"
            }
        ],
        "ManagedBy": [
            {
                "@odata.id": "/redfish/v1/Managers/RackManager"
            }
        ]
    }
}
