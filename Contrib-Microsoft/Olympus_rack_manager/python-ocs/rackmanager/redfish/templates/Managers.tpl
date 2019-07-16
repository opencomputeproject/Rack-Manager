<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        config = "Row"
        count = 1
    elif (RackManagerConfig == rm_mode_enum.standalone_rackmanager):
        config = "Rack"
        count = 25
    else:
        config = "Rack"
        count = 49
    end
%>
{
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "@odata.context": "/redfish/v1/$metadata#Managers",
    "@odata.id": "/redfish/v1/Managers",
    "Name": "Managers Collection",
    "Members@odata.count": {{count}},
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/{{config}}Manager"       
        }
        %if (config == "Rack"):
            ,{
                "@odata.id": "/redfish/v1/Managers/System/1"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/2"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/3"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/4"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/5"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/6"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/7"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/8"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/9"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/10"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/11"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/12"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/13"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/14"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/15"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/16"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/17"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/18"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/19"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/20"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/21"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/22"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/23"       
            },
            {
                "@odata.id": "/redfish/v1/Managers/System/24"       
            }
            %if (count > 25):
                ,{
                    "@odata.id": "/redfish/v1/Managers/System/25"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/26"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/27"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/28"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/29"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/30"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/31"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/32"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/33"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/34"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/35"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/36"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/37"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/38"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/39"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/40"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/41"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/42"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/43"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/44"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/45"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/46"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/47"       
                },
                {
                    "@odata.id": "/redfish/v1/Managers/System/48"       
                }
            %end
        %end
    ]
}
