%from pre_settings import rm_mode_enum
{
    "@odata.type": "#ServiceRoot.v1_0_2.ServiceRoot",
    "@odata.context": "/redfish/v1/$metadata#ServiceRoot",
    "@odata.id": "/redfish/v1/",
    "Id": "RootService",
    "Name": "Root Service",
    "RedfishVersion": "1.1.0",
    %if (not RackManagerConfig == rm_mode_enum.rowmanager):
        "Systems": {
            "@odata.id": "/redfish/v1/Systems"
        },
    %end
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    }
}
