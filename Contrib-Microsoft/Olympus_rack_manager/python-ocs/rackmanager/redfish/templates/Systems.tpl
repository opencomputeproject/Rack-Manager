<%
    from pre_settings import rm_mode_enum
    if (RackManagerConfig == rm_mode_enum.standalone_rackmanager):
        count = 24
    else:
        count = 48
    end
%>
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.context": "/redfish/v1/$metadata#Systems",        
    "@odata.id": "/redfish/v1/Systems",         
    "Name": "Rack Systems Collection",
    "Members@odata.count": {{count}},
    "Members": [        
        { 
            "@odata.id": "/redfish/v1/System/1"
        },
        { 
            "@odata.id": "/redfish/v1/System/2"
        },
        { 
            "@odata.id": "/redfish/v1/System/3"
        },
        { 
            "@odata.id": "/redfish/v1/System/4"
        },
        { 
            "@odata.id": "/redfish/v1/System/5"
        },
        { 
            "@odata.id": "/redfish/v1/System/6"
        },
        { 
            "@odata.id": "/redfish/v1/System/7"
        },
        { 
            "@odata.id": "/redfish/v1/System/8"
        },
        { 
            "@odata.id": "/redfish/v1/System/9"
        },
        { 
            "@odata.id": "/redfish/v1/System/10"
        },
        { 
            "@odata.id": "/redfish/v1/System/11"
        },
        { 
            "@odata.id": "/redfish/v1/System/12"
        },
        { 
            "@odata.id": "/redfish/v1/System/13"
        },
        { 
            "@odata.id": "/redfish/v1/System/14"
        },
        { 
            "@odata.id": "/redfish/v1/System/15"
        },
        { 
            "@odata.id": "/redfish/v1/System/16"
        },
        { 
            "@odata.id": "/redfish/v1/System/17"
        },
        { 
            "@odata.id": "/redfish/v1/System/18"
        },
        { 
            "@odata.id": "/redfish/v1/System/19"
        },
        { 
            "@odata.id": "/redfish/v1/System/20"
        },
        { 
            "@odata.id": "/redfish/v1/System/21"
        },
        { 
            "@odata.id": "/redfish/v1/System/22"
        },
        { 
            "@odata.id": "/redfish/v1/System/23"
        },
        { 
            "@odata.id": "/redfish/v1/System/24"
        }
        %if (count > 24):
            ,{ 
                "@odata.id": "/redfish/v1/System/25"
            },
            { 
                "@odata.id": "/redfish/v1/System/26"
            },
            { 
                "@odata.id": "/redfish/v1/System/27"
            },
            { 
                "@odata.id": "/redfish/v1/System/28"
            },
            { 
                "@odata.id": "/redfish/v1/System/29"
            },
            { 
                "@odata.id": "/redfish/v1/System/30"
            },
            { 
                "@odata.id": "/redfish/v1/System/31"
            },
            { 
                "@odata.id": "/redfish/v1/System/32"
            },
            { 
                "@odata.id": "/redfish/v1/System/33"
            },
            { 
                "@odata.id": "/redfish/v1/System/34"
            },
            { 
                "@odata.id": "/redfish/v1/System/35"
            },
            { 
                "@odata.id": "/redfish/v1/System/36"
            },
            { 
                "@odata.id": "/redfish/v1/System/37"
            },
            { 
                "@odata.id": "/redfish/v1/System/38"
            },
            { 
                "@odata.id": "/redfish/v1/System/39"
            },
            { 
                "@odata.id": "/redfish/v1/System/40"
            },
            { 
                "@odata.id": "/redfish/v1/System/41"
            },
            { 
                "@odata.id": "/redfish/v1/System/42"
            },
            { 
                "@odata.id": "/redfish/v1/System/43"
            },
            { 
                "@odata.id": "/redfish/v1/System/44"
            },
            { 
                "@odata.id": "/redfish/v1/System/45"
            },
            { 
                "@odata.id": "/redfish/v1/System/46"
            },
            { 
                "@odata.id": "/redfish/v1/System/47"
            },
            { 
                "@odata.id": "/redfish/v1/System/48"
            }
        %end
    ]
}
