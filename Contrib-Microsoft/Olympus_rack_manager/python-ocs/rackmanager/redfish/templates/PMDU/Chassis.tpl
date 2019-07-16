<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        id = "RMM"
        name = "RMM"
        type = "RackMount"
        config = "Row"
    else:
        id = "PMDU"
        name = "PMDU"
        type = "Sidecar"
        config = "Rack"
    end
%>
{
    "@odata.type": "#Chassis.v1_2_0.Chassis",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/$entity",
    "@odata.id": "/redfish/v1/Chassis/{{id}}",
    "Id": "{{id}}",
    "Name": "{{name}}",
    "ChassisType": "{{type}}",
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
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.Chassis",
            "FRU": {
                %sepr = ""
                %if defined ("Board_Fru_Id"):
                    {{sepr}}"FruId": "{{Board_Fru_Id}}"
                    %sepr = ","
                %end
                %if defined ("Board_Version"):
                    {{sepr}}"Version": "{{Board_Version}}"
                    %sper = ","
                %end
                %if defined ("Board_Build"):
                    {{sepr}}"Build": "{{Board_Build}}"
                    %sepr = ","
                %end
                %if defined ("Board_Manufacturer_Date"):
                    {{sepr}}"ManufacturerDate": "{{Board_Manufacturer_Date}}"
                %end
            },
            "PowerControl": {
                "@odata.id": "/redfish/v1/Chassis/{{id}}/PowerControl"
            }
            %if (id == "PMDU"):
                ,"PowerMeter": {
                    "@odata.id": "/redfish/v1/Chassis/PMDU/PowerMeter"
                }
            %end
        }
    },
    "Links": {
        "ManagedBy": {
            "@odata.id": "/redfish/v1/Managers/{{config}}Manager"
        }
        %if (id == "PMDU"):
            ,"ContainedBy": {
                "@odata.id": "/redfish/v1/Chassis/Rack"
            }
        %end
    }
}
