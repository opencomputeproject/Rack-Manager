{
    "@odata.type": "#Manager.v1_1_0.Manager",
    "@odata.context": "/redfish/v1/$metadata#Managers/Members/$entity",
    "@odata.id": "/redfish/v1/Managers/System/{{ID}}",
    "Id": "System{{ID}}",
    "Name": "System {{ID}} Manager",
    "ManagerType": "BMC",
    %if defined ("Server_HWVersion"):
        "Model": "{{Server_HWVersion}}",
    %end
    %if defined ("Server_BMCVersion"):
        "FirmwareVersion": "{{Server_BMCVersion}}",
    %end
    "Status": {
        "State": "Enabled"
        %if defined ("Health"):
           ,"Health": "{{Health}}"
        %end
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/System/{{ID}}/EthernetInterfaces"
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Managers/System/{{ID}}/LogServices"
    },
    "Links": {
        "ManagerForServers": [
            {
                "@odata.id": "/redfish/v1/System/{{ID}}"
            }
        ],
        "ManagerForChassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/System/{{ID}}"
            }
        ],
        "ManagerInChassis": {
            "@odata.id": "/redfish/v1/Chassis/System/{{ID}}"
        }
    }
}
