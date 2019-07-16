<%
    from pre_settings import rm_mode_enum
    
    if defined ("TemplateDefault"):
        setdefault ("ID", "")
        setdefault ("Manufacturer", "")
        setdefault ("Server_HWVersion", "")
        setdefault ("Description", "")
        setdefault ("SKU", "")
        setdefault ("SerialNumber", "")
        setdefault ("PartNumber", "")
        setdefault ("AssetTag", "")
        setdefault ("Server_IndicatorLED", "")
    end
%>
{
    "@odata.type": "#Chassis.v1_2_0.Chassis",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
    "@odata.id": "/redfish/v1/Chassis/System/{{ID}}",
    "Id": "{{ID}}",
    "Name": "System {{ID}}",
    "ChassisType": "Shelf",
    %if defined ("Manufacturer"):
    	"Manufacturer": "{{Manufacturer}}",
	%end
	%if defined ("Server_HWVersion"):
        "Model": "{{Server_HWVersion}}",
    %end
    %if defined ("Description"):
        "Description": "{{Description}}",
    %end
    %if defined ("SKU"):
    	"SKU": "{{SKU}}",
	%end
    %if defined ("SerialNumber"):
    	"SerialNumber": "{{SerialNumber}}",
	%end
    %if defined ("PartNumber"):
    	"PartNumber": "{{PartNumber}}",
	%end
    %if defined ("AssetTag"):
    	"AssetTag": "{{AssetTag}}",
	%end
	%if defined ("Server_IndicatorLED"):
		"IndicatorLED": "{{Server_IndicatorLED}}",
	%end
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Thermal"
    },
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Power"
    },
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.Chassis",
            "Sensors": {
                "@odata.id": "/redfish/v1/Chassis/System/{{ID}}/Sensors"
            }
        }
    },
    "Links": {
        "ComputerSystems": {
            "@odata.id": "/redfish/v1/System/{{ID}}"
        },
        "ManagedBy": {
            "@odata.id": "/redfish/v1/Managers/System/{{ID}}"
        }
        %if (not RackManagerConfig == rm_mode_enum.standalone_rackmanager):
            ,"ContainedBy": {
                "@odata.id": "/redfish/v1/Chassis/Rack"
            }
        %end
    }
}
