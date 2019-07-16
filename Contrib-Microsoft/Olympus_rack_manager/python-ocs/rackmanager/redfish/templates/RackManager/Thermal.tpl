<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#Thermal.v1_1_0.Thermal",
    "@odata.context": "/redfish/v1/$metadata#Chassis/Members/{{config}}Manager/Thermal/$entity",
    "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Thermal",
    "Id": "Thermal",
    "Name": "{{config}} Manager Thermal",
    "Temperatures": [
        {
            "@odata.id": "/redfish/v1/Chassis/{{config}}Manager/Thermal#/Temperatures/1",
            "MemberId": "1"
            %if defined ("Temperature"):
                ,"ReadingCelsius": {{Temperature}}
            %end
        }
    ],
    "Oem": {
        "Microsoft": {
            "@odata.type": "#Ocs.v1_0_0.Thermal"
            %if defined ("Humidity"):
                ,"Humidity": {{Humidity}}
            %end
        }
    }
}
