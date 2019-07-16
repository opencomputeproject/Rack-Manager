<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#LogService.v1_0_2.LogService",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/LogServices/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log",
    "Id": "Log",
    "Name": "{{config}} Manager Log",
    "Status": {
        %if defined ("TelemetryDaemonStatus"):
             "State": "{{TelemetryDaemonStatus}}"
		%end
    },
    "Entries": {
        "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log/Entries"
    },
    "Actions": {
        "#LogService.ClearLog": {
            "target": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log/Actions/LogService.ClearLog"
        }
    }
}
