<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
    else:
        config = "Rack"
    end
%>
{
    "@odata.type": "#LogServiceCollection.LogServiceCollection",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/{{config}}Manager/LogServices/$entity",
    "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices",
    "Name": "Log Collection",
    "Description": "{{config}} Manager Logs",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/{{config}}Manager/LogServices/Log"
        }
    ]
}
