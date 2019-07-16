<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
    
    if defined ("TemplateDefault"):
        setdefault ("Board_Manufacturer", "")
        setdefault ("Board_Name", "")
        setdefault ("Board_Serial", "")
        setdefault ("Board_Part_Number", "")
        setdefault ("Product_Assettag", "")
        setdefault ("Manager_LED_Status", "")
        setdefault ("Board_Fru_Id", "")
        setdefault ("Board_Version", "")
        setdefault ("Board_Build", "")
        setdefault ("Board_Manufacturer_Date", "")
    end
%>
{
    "@odata.type": "#Chassis.v1_2_0.Chassis",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
    "@odata.id": "/redfish/v1/Chassis/{{config}}Manager",
    "Id": "{{config}}Manager",
    "Name": "{{config}} Manager",
    "ChassisType": "Module",
    %if defined ("Board_Manufacturer"):
        "Manufacturer": "{{Board_Manufacturer}}",
    %end
    %if defined ("Board_Name"):
        "Model": "{{Board_Name}}",
    %end
    %if defined ("Board_Serial"):
        "SerialNumber": "{{Board_Serial}}",
    %end
    %if defined ("Board_Part_Number"):
        "PartNumber": "{{Board_Part_Number}}",
    %end
    %if defined ("Product_Assettag"):
        "AssetTag": "{{Product_Assettag}}",
    %end
    "PowerState": "On",
    %if defined ("Manager_LED_Status"):
        "IndicatorLED": "{{Manager_LED_Status}}",
    %end
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.FRU"
            %if defined ("Board_Fru_Id"):
                ,"FruId": "{{Board_Fru_Id}}"
            %end
            %if defined ("Board_Version"):
                ,"Version": "{{Board_Version}}"
            %end
            %if defined ("Board_Build"):
                ,"Build": "{{Board_Build}}"
            %end
            %if defined ("Board_Manufacturer_Date"):
                ,"ManufacturerDate": "{{Board_Manufacturer_Date}}"
            %end
        }
    },
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Thermal"
    },
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Power"
    }
    %if ((config == "Rack") and (not RackManagerConfig == rm_mode_enum.standalone_rackmanager)):
        ,"Links": {
            "ContainedBy": {
                "@odata.id": "/redfish/v1/Chassis/Rack"
            }
        }
    %end
}
