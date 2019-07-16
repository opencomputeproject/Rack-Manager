{
    "@odata.type": "#LogService.v1_0_2.LogService",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/System/{{ID}}/LogServices/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/System/{{ID}}/LogServices/Log",
    "Id": "Log",
    "Name": "System{{ID}} Manager Log",
    "ServiceEnabled": true,
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Entries": {
        "@odata.id": "/redfish/v1/Managers/System/{{ID}}/LogServices/Log/Entries"
    },
    "Actions": {
        "#LogService.ClearLog": {
            "target": "/redfish/v1/Managers/System/{{ID}}/LogServices/Log/Actions/LogService.ClearLog"
        }
    }
}
