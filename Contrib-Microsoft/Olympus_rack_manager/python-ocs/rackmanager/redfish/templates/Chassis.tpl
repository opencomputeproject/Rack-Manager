<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.rowmanager):
        power = "RMM"
        config = "Row"
        count = 2
    elif (RackManagerConfig == rm_mode_enum.standalone_rackmanager):
        power = ""
        config = "Rack"
        count = 27
    else:
        power = "PMDU"
        config = "Rack"
        count = 52
    end
%>
{
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "@odata.context": "/redfish/v1/$metadata#Chassis",
    "@odata.id": "/redfish/v1/Chassis",
    "Name": "Chassis Collection",
    "Members@odata.count": {{count}},
    "Members": [
        %if (power):
            %if (config == "Rack"):
                {
                    "@odata.id": "/redfish/v1/Chassis/Rack"       
                },
            %end
            {
                "@odata.id": "/redfish/v1/Chassis/{{power}}"       
            },
        %end
        %if (config == "Rack"):
            {
                "@odata.id": "/redfish/v1/Chassis/MgmtSwitch"       
            },
        %end
        {
            "@odata.id": "/redfish/v1/Chassis/{{config}}Manager"       
        }
        %if (config == "Rack"):
            ,{
                "@odata.id": "/redfish/v1/Chassis/System/1"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/2"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/3"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/4"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/5"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/6"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/7"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/8"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/9"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/10"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/11"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/12"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/13"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/14"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/15"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/16"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/17"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/18"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/19"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/20"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/21"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/22"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/23"       
            },
            {
                "@odata.id": "/redfish/v1/Chassis/System/24"       
            }
            %if (count > 27):
                ,{
                    "@odata.id": "/redfish/v1/Chassis/System/25"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/26"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/27"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/28"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/29"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/30"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/31"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/32"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/33"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/34"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/35"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/36"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/37"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/38"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/39"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/40"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/41"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/42"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/43"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/44"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/45"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/46"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/47"       
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/System/48"       
                }
            %end
        %end
    ]
}
